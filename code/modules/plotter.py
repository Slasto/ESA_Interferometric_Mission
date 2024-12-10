import numpy as np
import plotly.graph_objects as go
from IPython.display import display, Markdown
from modules.golomb_simple import orbital_golomb_array

def print_result(udp : orbital_golomb_array, x_solution, N_obs : int = 300) -> None:
    """ Prints the result details and visualizes the given solution.

    Args:
        udp (`orbital_golomb_array`): An instance of the orbital golomb array class, used to evaluate the fitness and plot the solution.
        x_solution (`list` of length N): The solution to be evaluated and plotted.
        N_obs (`int`, optional): Number of observations for simulating reconstruction.
        image_path (`str`, optional): Path to the image used in simulated reconstruction.
    Returns: None
    """
    fit = udp.fitness(x_solution)[0]
    display(Markdown("---"))
    print("Solution: ", x_solution)
    print("Fitness: {:.5f}".format(fit))
    udp.plot(x_solution, figsize=(25,7))
    display(Markdown("---"))
    udp.plot_simulated_reconstruction(x_solution, N_obs, image_path="../data/star.jpg")
    display(Markdown("---"))
    udp.plot_simulated_reconstruction(x_solution, N_obs, image_path="../data/nebula.jpg")

def plot_in_3D_space(UDP: orbital_golomb_array, x_encoded : list[(float,float,float)], meas : int = 2) -> None:
    """
    Plots the satellites in 3D space based on the encoded positions and measurement index.

    Args:
        UDP (`orbital_golomb_array`): An instance of the orbital golomb array class.
        x_encoded (`list[(float,float,float)]`): Encoded positions of the satellites.
        meas (`int`, optional): Measurement index. Defaults to 2.

    Returns:
        None
    """
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
                                                              )]
        )

        
        rel_pos = []
        for stm in UDP.stms:
            d_ic = dx0 * UDP.scaling_factor
            fc = (stm @ d_ic.T).T[:, :3]
            #fc = propagate_formation(d_ic, stm)
            rel_pos.append(fc / UDP.scaling_factor)

        points_3D = np.array(rel_pos)[meas]
        if meas != 0:
                points_3D = points_3D / (UDP.inflation_factor)
                
        points_3D = points_3D[np.max(points_3D, axis=1) < 1 ]
        points_3D = points_3D[np.min(points_3D, axis=1) > -1]

        pos3D = (points_3D * UDP.grid_size / 2)
        pos3D = pos3D + int(UDP.grid_size / 2)
        return pos3D.astype(int)
    
    points = x_encoded_into_grid_on_t_meas(UDP, x_encoded, meas)
    x_data, y_data, z_data = zip(*points)

    # Creazione della figura
    fig = go.Figure()

    # Aggiunta dei frame per l'animazione
    for i in range(len(x_data)):
        fig.add_trace(go.Scatter3d(
            x=[x_data[i]],
            y=[y_data[i]],
            z=[z_data[i]],
            mode='markers',
            marker=dict(size=20, color='green'),
            name=f'Satellite {i+1}'
    ))

    # Configura la grigpointslia quadrata (una linea ogni 1 unità)
    tick_plot = np.arange(0, UDP.grid_size, 1)
    range_plot = [0, UDP.grid_size]

    fig.update_layout(
        scene=dict(
            xaxis=dict(
                range=range_plot,
                tickvals=tick_plot,
                showgrid=True,
                gridcolor="lightgray",
            ),
            yaxis=dict(
                range=range_plot,
                tickvals=tick_plot,
                showgrid=True,
                gridcolor="lightgray",
            ),
            zaxis=dict(
                range=range_plot,
                tickvals=tick_plot,
                showgrid=True,
                gridcolor="lightgray",
            ),
            aspectmode="cube"
        ),
        title="Arrangement of satellites in space",
        margin=dict(r=10, l=10, b=10, t=30)
    )
    fig.show()