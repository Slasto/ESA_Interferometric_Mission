# This Source Code is based on European Space Agency: SpOC 3 Interferometric Mission

from itertools import combinations
from collections import Counter

import heyoka as hy
import numpy as np
import scipy
import time
import PIL
import SSIM_PIL

from matplotlib import pyplot as plt
import matplotlib.cm as cm

def propagate_formation(dx0, stm):
    """From some initial (relative) position and velocities returns new (relative) positions at
    some future time (defined by the stm).
    Args:
        dx0 (`np.array` (N, 6)): initial relative positions and velocities.
        stm (`np.array` (6,6)): the state transition matrix at some future time.
    Returns:
        np.array (N,3): propagated positions
    """
    dxT = stm @ dx0.T
    # We return only the positions
    return dxT.T[:, :3]

def stm_factory(ic, T, mu, M, verbose=True):
    """Constructs all the STMS and reference trajectory in a CR3BP dynamics
    Args:
        ic (`np.array` (N, 6)): initial conditions (absolute).
        T (`float`): propagation time
        mu (`float`): gravity parameter
        M (`int`): number of grid points (observations)
        verbose (boolean): print time it took to build Taylor integrator and STMs
    Returns:
        (ref_state (M, 6), stms (M,6,6)): the propagated state and stms
    """
    # ----- We assemble the CR3BP equation of motion --------
    # The state
    x, y, z, vx, vy, vz = hy.make_vars("x", "y", "z", "vx", "vy", "vz")
    xarr = np.array([x, y, z, vx, vy, vz])
    # The dynamics
    r_1 = hy.sqrt((x + hy.par[0]) ** 2 + y**2 + z**2)
    r_2 = hy.sqrt((x - (1 - hy.par[0])) ** 2 + y**2 + z**2)
    dxdt = vx
    dydt = vy
    dzdt = vz
    dvxdt = (
        2 * vy
        + x
        - (1 - hy.par[0]) * (x + hy.par[0]) / (r_1**3)
        - hy.par[0] * (x + hy.par[0] - 1) / (r_2**3)
    )
    dvydt = -2 * vx + y - (1 - hy.par[0]) * y / (r_1**3) - hy.par[0] * y / (r_2**3)
    dvzdt = -(1 - hy.par[0]) / (r_1**3) * z - hy.par[0] / (r_2**3) * z
    # This array contains the expressions (r.h.s.) of our dynamics
    farr = np.array([dxdt, dydt, dzdt, dvxdt, dvydt, dvzdt])

    # We now compute the variational equations
    # 1 - Define the symbols
    symbols_phi = []
    for i in range(6):
        for j in range(6):
            # Here we define the symbol for the variations
            symbols_phi.append("phi_" + str(i) + str(j))
    phi = np.array(hy.make_vars(*symbols_phi)).reshape((6, 6))

    # 2 - Compute the gradient
    dfdx = []
    for i in range(6):
        for j in range(6):
            dfdx.append(hy.diff(farr[i], xarr[j]))
    dfdx = np.array(dfdx).reshape((6, 6))

    # 3 - Assemble the expressions for the r.h.s. of the variational equations
    dphidt = dfdx @ phi

    dyn = []
    for state, rhs in zip(xarr, farr):
        dyn.append((state, rhs))
    for state, rhs in zip(phi.reshape((36,)), dphidt.reshape((36,))):
        dyn.append((state, rhs))

    # These are the initial conditions on the variational equations (the identity matrix)
    ic_var = np.eye(6).reshape((36,)).tolist()

    start_time = time.time()
    ta = hy.taylor_adaptive(
        # The ODEs.
        dyn,
        # The initial conditions (do not matter, they will change)
        [0.1] * 6 + ic_var,
        # Operate below machine precision
        # and in high-accuracy mode.
        tol=1e-16,
    )
    if verbose:
        print(
            "--- %s seconds --- to build the Taylor integrator -- (do this only once)"
            % (time.time() - start_time)
        )
    # We set the Taylor integration param
    ta.pars[:] = [mu]
    # We set the ic
    ta.state[:6] = ic
    ta.state[6:] = ic_var
    ta.time = 0.0
    # The time grid
    t_grid = np.linspace(0, T, M)
    # We integrate
    start_time = time.time()
    sol = ta.propagate_grid(t_grid)
    if verbose:
        print("--- %s seconds --- to construct all stms" % (time.time() - start_time))

    ref_state = sol[4][:, :6]
    stms = sol[4][:, 6:].reshape(M, 6, 6)
    return (ref_state, stms)

class orbital_golomb_array:
    def __init__(
        self,
        n_sat: int,
        ic: list,
        T: float,
        n_meas=3,
        mu=0.01215058560962404,
        scaling_factor=1e-4,
        inflation_factor=1.5,
        grid_size=20,
        verbose = True
    ):
        """Constructs a UDP (User Defined Problem) compatible with pagmo/pygmo and representing the design
        of a ballistic formation flight around a nominal CR3BP trajectory, able to perform a good interferometric
        reconstruction of the image contained in *img_path*.
        Args:
            n_sat (`int`): Number of satellites in the formation.
            ic (`list`): Initial conditions of the reference CR3BP solution.
            T (`float`): Time of flight for the measurments
            mu (`float`): parameter of the CR3BP
            n_meas (`int`): Number of interferometric measurments performed along the trajectory
                           (assumed at equally spaced time intervals).
            scaling_factor (`float`, optional): The initial positions and velocities will be scaled down by this factor.
                             Defaults to 1e-4.
            inflation_factor (`float`, optional): The allowed formation inflation. (outside this radius satellites are no longer considered)
            grid_size (int, optional): Size of the Golomb grid.
            verbose (boolean): print time it took to build Taylor integrator and STMs
        """
        # Init data members
        self.n_sat = n_sat
        self.ic = ic
        self.T = T
        self.n_meas = n_meas
        self.scaling_factor = scaling_factor
        self.grid_size = grid_size
        self.mu = mu
        self.inflation_factor = inflation_factor
        self.verbose = verbose
        self.distance_limit_weight = 1/n_sat

        # We construct the various STMs and reference trajectory
        self.ref_state, self.stms = stm_factory(ic, T, mu, n_meas, self.verbose)

    # Mandatory method in the UDP pygmo interface
    # (returns the lower and upper bound of each component in the chromosome)
    def get_bounds(self):
        # return ([-1.0] * self.n_sat * 3 + [-10.0] * self.n_sat * 3 , [1.0] * self.n_sat * 3 + [10.0] * self.n_sat * 3 )
        return ([-1.0] * self.n_sat * 3 + [-1.0] * self.n_sat * 3 , [1.0] * self.n_sat * 3 + [1.0] * self.n_sat * 3 )

    def get_nix(self):
        """
        Get number of integer variables in the chromosome/decision vector.

        Returns:
            int: number of integer variables.
        """
        # the chromosome exists solely of float variables.
        return 0

    # Mandatory method in the UDP pygmo interface
    # (returns the fitness of the chromosome [obj1, obj2 ..., ec1, ec2, ...,iec1, iec2...]
    def fitness(self, x):
        return self.fitness_impl(x)

    # Plots the representation of the chromosome in several graphs
    def plot(self, x, figsize=(25,7)):
        return self.fitness_impl(x, plotting=True, figsize=figsize)

    def plot_simulated_reconstruction(
        self, x, M=100, grid_size=256, image_path="../data/nebula.jpg", plot_image=True
    ):
        """_summary_

        Args:
            x (`list` of length N): Chromosome contains initial relative positions and velocities of each satellite:
            Example: x = [ dx0_N1, dx0_N2, ..., dx0_NN, dy0_N1, dy0_N2, ..., dy0_NN , ...... , dvz0_N1, dvz0_N2, ..., dvz0_NN]
            M (`int`): Number of interferometric measurements performed along the trajectory
                           (assumed at equally spaced time intervals).
            grid_size (int, optional): _description_. Defaults to 256.
            image_path (str, optional): _description_. Defaults to "data/nebula.jpg".
        """        

        #  Time of flight for the measurements
        T = self.T

        _, stms = stm_factory(self.ic, T, self.mu, M, self.verbose)

        # 1) Decode the chromosomes into (x, y, z, vx, vy, vz) of the satellites.
        N = self.n_sat

        dx0 = np.array(
            [(i, j, k, p, m, n) for (i, j, k, p, m, n) in zip(x[      : N], 
                                                              x[N     : 2 * N], 
                                                              x[2 * N : 3 * N],
                                                              x[3 * N : 4 * N],
                                                              x[4 * N : 5 * N],
                                                              x[5 * N : ],
                                                              )]
        )


        # We now propagate all these relative positions to the measurment points. We do this accounting for the formation size
        rel_pos = []
        for stm in stms:
            # We scale the initial positions and velocities
            d_ic = dx0 * self.scaling_factor
            fc = propagate_formation(d_ic, stm)
            # We store the relative positions in the original 'units'
            rel_pos.append(fc / self.scaling_factor)
        rel_pos = np.array(rel_pos)

        # For each observation point we construct the corresponding Golomb Array
        gs_xy = []  # This will contain all the Golomb Arrays at each observation point
        g_xy = np.zeros(
            (grid_size, grid_size)
        )  # This will contain all the positions cumulatively (for plotting)

        # For each observation point we construct the corresponding Golomb Array
        gs_xz = []  # This will contain all the Golomb Arrays at each observation point
        g_xz = np.zeros(
            (grid_size, grid_size)
        )  # This will contain all the positions cumulatively (for plotting)

        # For each observation point we construct the corresponding Golomb Array
        gs_yz = []  # This will contain all the Golomb Arrays at each observation point
        g_yz = np.zeros(
            (grid_size, grid_size)
        )  # This will contain all the positions cumulatively (for plotting)

        for k in range(M):

            gs_xy.append(np.zeros((grid_size, grid_size)))
            gs_xz.append(np.zeros((grid_size, grid_size)))
            gs_yz.append(np.zeros((grid_size, grid_size)))

            points_3D = rel_pos[k]                
            # Account for an added factor allowing the formation to spread.
            points_3D = points_3D / (self.inflation_factor) 

            # and removing the points outside [-1,1] (cropping wavelengths here)
            points_3D = points_3D[np.max(points_3D, axis=1) < 1 ]
            points_3D = points_3D[np.min(points_3D, axis=1) > -1]

            # Interpret now the 3D positions [-1,1] as points on a grid.
            pos3D = (points_3D * grid_size / 2).astype(int)
            pos3D = pos3D + int(grid_size / 2)
            

            for i, j, k_ in pos3D:
                gs_xy[k][i, j] = 1
                g_xy[i, j] = 1

                gs_xz[k][i, k_] = 1
                g_xz[i, k_] = 1

                gs_yz[k][j, k_] = 1
                g_yz[j, k_] = 1

        def plot_recon(gs, g, plot=True):
            # We Simulate the interferometric measurement
            otf = np.zeros((grid_size * 2 - 1, grid_size * 2 - 1))
            for one_g in gs:
                tmp = scipy.signal.correlate(one_g, one_g, mode="full")
                otf = otf + tmp
            otf[abs(otf) < 0.1] = 0
            otf[abs(otf) > 1] = 1
            otf = np.fft.fftshift(otf)

            I_o = PIL.Image.open(image_path)
            I_o = np.asarray(I_o.resize((511, 511)))
            imo_fft = np.fft.fft2(I_o)
            imr_fft = imo_fft * otf  # Hadamard product here
            I_r = abs(np.fft.ifft2(imr_fft))
            if plot is False:
                return I_r
            # We plot
            fig = plt.figure(figsize=(15, 3))
            ax = fig.subplots(1, 4)
            ax[0].imshow(I_o, cmap="gray")
            ax[0].axis("off")
            ax[0].set_title("Image")
            ax[1].imshow(I_r, cmap="gray")
            ax[1].axis("off")
            ax[1].set_title("Reconstruction")
            ax[2].imshow(g, cmap="gray")
            ax[2].axis("off")
            ax[2].set_title("Golomb Array Traj")
            ax[3].imshow(otf, cmap="gray")
            ax[3].axis("off")
            ax[3].set_title("Optical Transfer Function")
            plt.show()

        if plot_image is False :
            return (
                plot_recon(gs_xy, None, plot=plot_image), 
                plot_recon(gs_xz, None, plot=plot_image), 
                plot_recon(gs_yz, None, plot=plot_image)
            )

        I_r_images = [
            plot_recon(gs_xy, None, plot=False),
            plot_recon(gs_xz, None, plot=False),
            plot_recon(gs_yz, None, plot=False)
        ]
        # Now we open up the main image and resize it to match the first reconstructed image dimensions
        I_o = PIL.Image.open(image_path).resize(I_r_images[0].shape[::-1])
        # We gonna convert those reconstructed images to grayscale, feel me?
        rec_images_bw = [PIL.Image.fromarray(img.astype('uint8'), mode='L') for img in I_r_images]
        # Compare dem similarity values between the images, ya dig?
        values = [SSIM_PIL.compare_ssim(I_o, rec_img, GPU=False) for rec_img in rec_images_bw]
        # Now let's spit out those values for ya
        print('XY\t''SSIM = %.4f%%' %(values[0]*100))
        plot_recon(gs_xy, g_xy)
        print('XZ\t''SSIM = %.4f%%' %(values[1]*100))
        plot_recon(gs_xz, g_xz)
        print('YZ\t''SSIM = %.4f%%' %(values[2]*100))
        plot_recon(gs_yz, g_yz)


    # Here is where the action takes place
    def fitness_impl(
        self,
        x,
        plotting=False,
        figsize=(15, 10),
        return_all_n_meas_fillfactor: bool = False,
        reduce_fill_if_not_optimal: bool = False,
        limit_distance: int = None,
    ):
        """Fitness function

        Args:
            x (`list` of length N): Chromosome contains initial relative positions and velocities of each satellite:
            Example: x = [ dx0_N1, dx0_N2, ..., dx0_NN, dy0_N1, dy0_N2, ..., dy0_NN , ...... , dvz0_N1, dvz0_N2, ..., dvz0_NN]
            plotting (bool, optional): Plot satellites on grid at each measurement and corresponding auto-correlation function and fill factors. Defaults to False.
            figsize (tuple, optional): Figure size. Defaults to (15, 10).
        Returns:
            float: fitness of corresponding chromosome x.
        """        
        # 1) Decode the chromosomes into (x, y, z, vx, vy, vz) of the satellites.
        N = self.n_sat

        dx0 = np.array(
            [(i, j, k, r, m, n) for (i, j, k, r, m, n) in zip(x[      : N], 
                                                              x[N     : 2 * N], 
                                                              x[2 * N : 3 * N],
                                                              x[3 * N : 4 * N],
                                                              x[4 * N : 5 * N],
                                                              x[5 * N : ],
                                                              )]
        )

        # 2) We now propagate all these relative positions to the measurment points. We do this accounting for the formation size
        rel_pos = []
        for stm in self.stms:
            # We scale the initial positions and velocities
            d_ic = dx0 * self.scaling_factor
            fc = propagate_formation(d_ic, stm)
            # We store the relative positions in the original 'units'
            rel_pos.append(fc / self.scaling_factor)
        rel_pos = np.array(rel_pos)

        # 3) At each observation epoch we compute the fill factor
        # See:
        # Memarsadeghi, Nargess, Ryan D. Joseph, John C. Kaufmann, and Byung Suk Lee.
        # "Golomb Patterns, Astrophysics, and Citizen Science Games." IEEE Access 10 (2022): 76125-76135.

        fill_factor = []

        if plotting:
            fig = plt.figure(figsize=figsize)
            gs = fig.add_gridspec(2, self.n_meas * 3, hspace=0.02, wspace=0.02)
            fig.suptitle('Placement of satellites (red squares) with respect to mothership (M)\nAutocorrelation matrix and corresponding fill factors.', fontsize=16, fontweight='bold', y=1.05)
            plt.axis("off")
            axs = gs.subplots(sharex=False, sharey=False)
            axs = axs.ravel()

        for k in range(self.n_meas):

            points_3D = rel_pos[k]   
            # Account for an added factor allowing the formation to spread. (Except for first observation, k == 0)
            if k != 0:
                points_3D = points_3D / (self.inflation_factor) 

            # and removing the points outside [-1,1] (cropping wavelengths here)
            points_3D = points_3D[np.max(points_3D, axis=1) < 1 ]
            points_3D = points_3D[np.min(points_3D, axis=1) > -1]

            # Interpret now the 3D positions [-1,1] as points on a grid.
            pos3D = (points_3D * self.grid_size / 2)
            pos3D = pos3D + int(self.grid_size / 2)
            pos3D = pos3D.astype(int)

            # Compute uv plane fill factor
            # Here we use the (https://stackoverflow.com/questions/62026550/why-does-scipy-signal-correlate2d-use-such-an-inefficient-algorithm)
            # correlate and ot correlate2d. We must then consider a threshold to define zero as the frequency domain inversion has numerical roundoffs

            EYE = np.zeros((self.grid_size, self.grid_size, self.grid_size))
            for i, j, k_ in pos3D:
                EYE[i, j, k_] = 1
            xy = np.max(EYE, axis = (2,))
            xz = np.max(EYE, axis = (1,))
            yz = np.max(EYE, axis = (0,))

            xyC = scipy.signal.correlate(xy, xy, mode="full")
            xzC = scipy.signal.correlate(xz, xz, mode="full")
            yzC = scipy.signal.correlate(yz, yz, mode="full")
            xyC[abs(xyC < 1e-8)] = 0
            xzC[abs(xzC < 1e-8)] = 0
            yzC[abs(yzC < 1e-8)] = 0

            f1 = np.count_nonzero(xyC) / xyC.shape[0] / xyC.shape[1]
            f2 = np.count_nonzero(xzC) / xzC.shape[0] / xzC.shape[1]
            f3 = np.count_nonzero(yzC) / yzC.shape[0] / yzC.shape[1]

            limit_distance_value = 0
            if limit_distance is not None:
                center = int(self.grid_size / 2)
                for i,j,k in pos3D :
                    if (
                            abs(center - i) <= limit_distance
                        and abs(center - j) <= limit_distance
                        and abs(center - k) <= limit_distance
                    ) is False :
                        limit_distance_value+=1

            if reduce_fill_if_not_optimal and len(pos3D)>1:
                alpha_f1, alpha_f2, alpha_f3 = compute_n_unique_dist_on_xy_xz_yz(pos3D)
                #size = sum(1 for _ in combinations(pos3D, 2))
                size = len(pos3D) * (len(pos3D)-1) //2
                f1 = f1 * (alpha_f1/size)
                f2 = f2 * (alpha_f2/size)
                f3 = f3 * (alpha_f3/size)

            fill_factor.append(
                (f1 + f2 + f3) - (limit_distance_value * self.distance_limit_weight)
            )  # Save sum of three fill factors at this observation
            
            if plotting:
                # XY
                # On the first row we plot the Golomb Grids
                axs[k * self.n_meas].imshow(xy, cmap=cm.jet, interpolation="nearest", origin='lower')
                axs[k * self.n_meas].add_patch(plt.Rectangle((int(self.grid_size / 2)-0.5, int(self.grid_size / 2)-0.5), 1, 1, color='black', alpha=0.5))
                axs[k * self.n_meas].text( int(self.grid_size / 2), int(self.grid_size / 2), 'M', color='white', fontsize=12, ha='center', va='center')
                axs[k * self.n_meas].grid(False)
                axs[k * self.n_meas].set_xlim(-0.5, self.grid_size - 0.5)
                axs[k * self.n_meas].set_ylim(-0.5, self.grid_size - 0.5)
                axs[k * self.n_meas].axis("off")
                if k == 0:
                    axs[k * self.n_meas].set_title(f"1st measurement\nt = 0\nXY plane\n{int(np.sum(xy))} satellites remaining !", color="black")
                elif k == 1:
                    axs[k * self.n_meas].set_title(f"2nd measurement\nt = 1 period\nXY plane\n{int(np.sum(xy))} satellites remaining !", color="black")
                else:
                    axs[k * self.n_meas].set_title(
                        f"3rd measurement\nt = 2 periods\nXY plane\n{int(np.sum(xy))} satellites remaining !",
                        color="black",
                    )

                # On the second row we plot the autocorrelated Golomb Grids
                axs[k * self.n_meas + 3 * self.n_meas].imshow(xyC, cmap=cm.jet, interpolation="nearest", origin='lower')
                axs[k * self.n_meas + 3 * self.n_meas].grid(False)
                axs[k * self.n_meas + 3 * self.n_meas].axis("off")
                if k == 0:
                    axs[k * self.n_meas + 3 * self.n_meas].set_title(f"fill factor = {f1:1.6f}", color="red")
                elif k == 1:
                    axs[k * self.n_meas + 3 * self.n_meas].set_title(f"fill factor = {f1:1.6f}", color="red")
                else:
                    axs[k * self.n_meas + 3 * self.n_meas].set_title(f"fill factor = {f1:1.6f}", color="red")

                # XZ
                # On the first row we plot the Golomb Grids
                axs[k * self.n_meas + 1].imshow(xz, cmap=cm.jet, interpolation="nearest", origin='lower')
                axs[k * self.n_meas + 1].add_patch(plt.Rectangle((int(self.grid_size / 2)-0.5, int(self.grid_size / 2)-0.5), 1, 1, color='black', alpha=0.5))
                axs[k * self.n_meas + 1].text( int(self.grid_size / 2), int(self.grid_size / 2), 'M', color='white', fontsize=12, ha='center', va='center')
                axs[k * self.n_meas + 1].grid(False)
                axs[k * self.n_meas + 1].set_xlim(-0.5, self.grid_size - 0.5)
                axs[k * self.n_meas + 1].set_ylim(-0.5, self.grid_size - 0.5)
                axs[k * self.n_meas + 1].axis("off")
                if k == 0:
                    axs[k * self.n_meas + 1].set_title(f"1st measurement\nt = 0\nXZ plane\n{int(np.sum(xz))} satellites remaining !", color="black")
                elif k == 1:
                    axs[k * self.n_meas + 1].set_title(f"2nd measurement\nt = 1 period\nXZ plane\n{int(np.sum(xz))} satellites remaining !", color="black")
                else:
                    axs[k * self.n_meas + 1].set_title(f"3rd measurement\nt = 2 periods\nXZ plane\n{int(np.sum(xz))} satellites remaining !", color="black")

                # On the secnd raw we plot the autocorrelated Golomb Grids
                axs[k * self.n_meas + 1 + 3 * self.n_meas].imshow(xzC, cmap=cm.jet, interpolation="nearest", origin='lower')
                axs[k * self.n_meas + 1 + 3 * self.n_meas].grid(False)
                axs[k * self.n_meas + 1 + 3 * self.n_meas].axis("off")
                if k == 0:
                    axs[k * self.n_meas + 1 + 3 * self.n_meas].set_title(
                        f"fill factor = {f2:1.6f}", color="red"
                    )
                elif k == 1:
                    axs[k * self.n_meas + 1 + 3 * self.n_meas].set_title(
                        f"fill factor = {f2:1.6f}", color="red"
                    )
                else:
                    axs[k * self.n_meas + 1 + 3 * self.n_meas].set_title(
                        f"fill factor = {f2:1.6f}", color="red"
                    )

                # XZ
                # On the first raw we plot the Golomb Grids
                axs[k * self.n_meas + 2].imshow(
                    yz, cmap=cm.jet, interpolation="nearest", origin="lower"
                )
                axs[k * self.n_meas + 2].add_patch(
                    plt.Rectangle(
                        (int(self.grid_size / 2) - 0.5, int(self.grid_size / 2) - 0.5),
                        1,
                        1,
                        color="black",
                        alpha=0.5,
                    )
                )
                axs[k * self.n_meas + 2].text(
                    int(self.grid_size / 2),
                    int(self.grid_size / 2),
                    "M",
                    color="white",
                    fontsize=12,
                    ha="center",
                    va="center",
                )
                axs[k * self.n_meas + 2].grid(False)
                axs[k * self.n_meas + 2].set_xlim(-0.5, self.grid_size - 0.5)
                axs[k * self.n_meas + 2].set_ylim(-0.5, self.grid_size - 0.5)
                axs[k * self.n_meas + 2].axis("off")

                if k == 0:
                    axs[k * self.n_meas + 2].set_title(
                        f"1st measurement\nt = 0\nYZ plane\n{int(np.sum(yz))} satellites remaining !",
                        color="black",
                    )
                elif k == 1:
                    axs[k * self.n_meas + 2].set_title(
                        f"2nd measurement\nt = 1 period\nYZ plane\n{int(np.sum(yz))} satellites remaining !",
                        color="black",
                    )
                else:
                    axs[k * self.n_meas + 2].set_title(
                        f"3rd measurement\nt = 2 periods\nYZ plane\n{int(np.sum(yz))} satellites remaining !",
                        color="black",
                    )

                # On the secnd raw we plot the autocorrelated Golomb Grids
                axs[k * self.n_meas + 2 + 3 * self.n_meas].imshow(
                    yzC, cmap=cm.jet, interpolation="nearest", origin="lower"
                )
                axs[k * self.n_meas + 2 + 3 * self.n_meas].grid(False)
                axs[k * self.n_meas + 2 + 3 * self.n_meas].axis("off")
                if k == 0:
                    axs[k * self.n_meas + 2 + 3 * self.n_meas].set_title(
                        f"fill factor = {f3:1.6f}", color="red"
                    )
                elif k == 1:
                    axs[k * self.n_meas + 2 + 3 * self.n_meas].set_title(
                        f"fill factor = {f3:1.6f}", color="red"
                    )
                else:
                    axs[k * self.n_meas + 2 + 3 * self.n_meas].set_title(
                        f"fill factor = {f3:1.6f}", color="red"
                    )
        if plotting:
            plt.show()

        if return_all_n_meas_fillfactor:
            return [
                -fill for fill in fill_factor
            ]  # Return worst of all three observations
        else:  # Default
            return [-min(fill_factor)]  # Return worst of all three observations

    def fitness_distance(
        self,
        x,
    ) :
        N = self.n_sat

        dx0 = np.array(
            [
                (i, j, k, r, m, n)
                for (i, j, k, r, m, n) in zip(
                    x[:N],
                    x[N : 2 * N],
                    x[2 * N : 3 * N],
                    x[3 * N : 4 * N],
                    x[4 * N : 5 * N],
                    x[5 * N :],
                )
            ]
        )

        rel_pos = []
        for stm in self.stms:
            # We scale the initial positions and velocities
            d_ic = dx0 * self.scaling_factor
            fc = propagate_formation(d_ic, stm)
            # We store the relative positions in the original 'units'
            rel_pos.append(fc / self.scaling_factor)
        rel_pos = np.array(rel_pos)

        distances_values = []

        for k in range(self.n_meas):
            points_3D = rel_pos[k]
            # Account for an added factor allowing the formation to spread. (Except for first observation, k == 0)
            if k != 0:
                points_3D = points_3D / (self.inflation_factor)

            # and removing the points outside [-1,1] (cropping wavelengths here)
            points_3D = points_3D[np.max(points_3D, axis=1) < 1]
            points_3D = points_3D[np.min(points_3D, axis=1) > -1]

            # Interpret now the 3D positions [-1,1] as points on a grid.
            pos3D = points_3D * self.grid_size / 2
            pos3D = pos3D + int(self.grid_size / 2)
            pos3D = pos3D.astype(int)
            
            if len(pos3D) > 1 : 
                xy, xz, yz = compute_n_unique_dist_on_xy_xz_yz(pos3D)
                distances_values.append(-(xy+xz+yz)/sum(1 for _ in combinations(pos3D, 2)))

        return distances_values

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

def init_simple_problem() -> orbital_golomb_array :
    '''SIMPLE problem configuration with 5 satellites and grid 11*11'''

    # DRO
    ic = [0.896508460944940632764, 0., 0., 0.000000000000013951082, 0.474817948848534454598, 0.]
    period = 2.6905181697222775
    # Number of satellites
    N = 5

    # Grid size
    grid_size = 11

    ############### Constants
    # Number of observations
    M = 3
    T = period*(M-1) # This makes it so that each observation is made after each period

    mu = 0.01215058560962404  # M_L/(M_T + M_L)

    scaling_factor = 1e-4

    inflation_factor = 1.23
    ###############

    # Instantiate UDP
    return orbital_golomb_array(n_sat=N, ic = ic, T = T, grid_size=grid_size, scaling_factor = scaling_factor, n_meas=M, inflation_factor = inflation_factor, mu=mu, verbose=False)

def init_medium_problem() -> orbital_golomb_array:
    '''MEDIUM problem configuration with 40 satellites and grid 21*21'''

    # DRO
    ic = [0.896508460944940632764, 0., 0., 0.000000000000013951082, 0.474817948848534454598, 0.]
    period = 2.6905181697222775

    # Number of satellites
    N = 40

    # Grid size
    grid_size = 21

    ############### Constants
    # Number of observations
    M = 3
    T = period*(M-1) # This makes it so that each observation is made after each period

    mu = 0.01215058560962404  # M_L/(M_T + M_L)

    scaling_factor = 1e-4

    inflation_factor = 1.23
    ###############

    # Instantiate UDP
    return orbital_golomb_array(n_sat=N, ic = ic, T = T, grid_size=grid_size, scaling_factor = scaling_factor, n_meas=M, inflation_factor = inflation_factor, mu=mu, verbose=False)

def init_hard_problem() -> orbital_golomb_array:
    '''HARD problem configuration with different ic and period compared to medium'''
    # Halo
    ic= [ 1.0829551779304256e+00,-6.9232801936027592e-27,-2.0231744561698364e-01,9.7888791827480806e-15,-2.0102644884016105e-01,2.4744866465838825e-14] 
    period=2.383491010514447 

    # Number of satellites
    N = 40

    # Grid size
    grid_size = 21

    ############### Constants
    # Number of observations
    M = 3
    T = period*(M-1) # This makes it so that each observation is made after each period

    mu = 0.01215058560962404  # M_L/(M_T + M_L)

    scaling_factor = 1e-4

    inflation_factor = 1.23
    ###############

    # Instantiate UDP
    return orbital_golomb_array(n_sat=N, ic = ic, T = T, grid_size=grid_size, scaling_factor = scaling_factor, n_meas=M, inflation_factor = inflation_factor, mu=mu, verbose=False)

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

def x_encoded_into_grid_on_t_meas(UDP: orbital_golomb_array, x_encoded : list[(float,float,float)], meas : int) -> np.ndarray:
    """
    Converts encoded positions into grid coordinates for a specific measurement.

    Args:
        UDP (`orbital_golomb_array`): An instance of the orbital golomb array class.
        x_encoded (`list[(float,float,float)]`): Encoded positions of the satellites.
        meas (`int`): Measurement index.

    Returns:
        `np.ndarray`: Grid coordinates of the satellites for the given measurement.

    Raises:
        ValueError: If the measurement index exceeds the number of measurements in UDP.
    """ 
    if meas > UDP.n_meas  :
        raise ValueError("Measurement index exceeds the number of measurements in UDP")
        
    N = UDP.n_sat
    dx0 = np.array(
            [(i, j, k, r, m, n) for (i, j, k, r, m, n) in zip(x_encoded[      : N], 
                                                              x_encoded[N     : 2 * N], 
                                                              x_encoded[2 * N : 3 * N],
                                                              x_encoded[3 * N : 4 * N],
                                                              x_encoded[4 * N : 5 * N],
                                                              x_encoded[5 * N : ],
                                                            )
            ]
        )

    d_ic = dx0 * UDP.scaling_factor 
    fc = (UDP.stms[meas] @ d_ic.T).T[:, :3] 
    points_3D = np.array(fc / UDP.scaling_factor)
    
    if meas != 0:
        points_3D = points_3D / (UDP.inflation_factor)
            
    points_3D = points_3D[np.max(points_3D, axis=1) < 1 ]
    points_3D = points_3D[np.min(points_3D, axis=1) > -1]
    pos3D = (points_3D * UDP.grid_size / 2)
    pos3D = pos3D + int(UDP.grid_size / 2)
    return pos3D.astype(int)

def compute_n_unique_dist_on_xy_xz_yz(pos3D) -> tuple[int,int,int]:
    """
    Compute the number of unique distances across three coordinate planes (xy, xz, yz) 
    by evaluating the Manhattan distance between each pair of points.

    Args:
        pos3D (`list[tuple[float, float, float]]`): A list of tuples where each tuple
        represents the (x, y, z) coordinates of a point in 3D space.

    Returns:
        `Tuple[int,int,int]` : (duplicate_distance_xy, duplicate_distance_xz, duplicate_distance_yz)
    """

    def unique_of_distance(distances: list[float]) -> int:
        """Helper function to check if there are duplicate distances in a given list of distances."""
        return sum(1 for distance, n_repetitions in Counter(distances).items() if n_repetitions < 2 or distance == (0,0))

    def compute_plane_distances(points: list[tuple[float, float]]) -> list[float]:
        """Compute the Manhattan distance between pairs of points in the same plane."""
        return [(abs(u_1 - u_2), abs(v_1 - v_2)) for (u_1, v_1), (u_2, v_2) in combinations(set(points), 2)]

    xy_points = [(x, y) for x, y, _ in pos3D]
    xz_points = [(x, z) for x, _, z in pos3D]
    yz_points = [(y, z) for _, y, z in pos3D]

    return (
        unique_of_distance(compute_plane_distances(xy_points)),
        unique_of_distance(compute_plane_distances(xz_points)),
        unique_of_distance(compute_plane_distances(yz_points))
    )

def compute_unique_distances_and_sats_in_grid(udp: orbital_golomb_array, solution: list[float]) -> tuple[float, float]:
    """
    Compute the normalized count of unique distances and the average number of satellites
    in the grid for a given set of solutions in an orbital golomb array.

    Args:
        udp (orbital_golomb_array): An instance representing the configuration of the satellites.
        solution (list[float]): A list representing the proposed positions and velocities of the satellites.

    Returns:
        tuple[float, float]: A tuple containing the normalized count of unique distances and the average
        number of satellites present in the grid across all measurement times.
    """
    n_distances = 3 * udp.n_sat * (udp.n_sat - 1) // 2
    distances_score = 0
    sats_in_grid_score = 0
    for i in range(udp.n_meas):
        x_grid = x_encoded_into_grid_on_t_meas(udp, solution, i)
        # sats_in_grid --- --- 
        EYE = np.zeros((udp.grid_size, udp.grid_size, udp.grid_size))
        for i, j, k_ in x_grid:
                EYE[i, j, k_] = 1
        sats_in_grid_score += np.sum(np.max(EYE, axis = (2,))) + np.sum(np.max(EYE, axis = (1,))) + np.sum(np.max(EYE, axis = (0,)))
        # --- --- ---
        distances_score += sum(compute_n_unique_dist_on_xy_xz_yz(x_grid))
        
    distances_score /= (n_distances * udp.n_meas)
    sats_in_grid_score /= (udp.n_sat * udp.n_meas * 3)
    return distances_score, sats_in_grid_score

#  --- --- ---  --- --- ---  --- --- ---  --- --- ---  --- --- ---
def similarity_chk(udp: orbital_golomb_array, x_encoded: list[(float,float,float)], n_orb: int = 300, image_path: str ="../data/nebula.jpg"):
    # Aight, here we gettin' some reconstructed images based on the encoded data and measurables
    I_r_images = udp.plot_simulated_reconstruction(x_encoded, n_orb, image_path=image_path, plot_image=False)
    # Now we open up the main image and resize it to match the first reconstructed image dimensions
    I_o = PIL.Image.open(image_path).resize(I_r_images[0].shape[::-1])
    # We gonna convert those reconstructed images to grayscale, feel me?
    rec_images_bw = [PIL.Image.fromarray(img.astype('uint8'), mode='L') for img in I_r_images]
    # Compare dem similarity values between the images, ya dig?
    values = [SSIM_PIL.compare_ssim(I_o, rec_img, GPU=False) for rec_img in rec_images_bw]
    # Now let's spit out those values for ya
    return values