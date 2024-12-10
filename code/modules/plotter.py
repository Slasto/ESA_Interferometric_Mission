from modules.golomb_simple import orbital_golomb_array
from IPython.display import display, Markdown


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