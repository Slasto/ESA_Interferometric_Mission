import numpy as np
import plotly.graph_objects as go
from IPython.display import display, Markdown
from modules.golomb_problem import orbital_golomb_array, x_encoded_into_grid_on_t_meas

def plot_simulated_reconstruction(udp : orbital_golomb_array, x_solution, N_obs : int = 300) -> None:
    """
    Plots simulated reconstructions using given solutions and number of observations.

    Args:
        udp (`orbital_golomb_array`): The orbital golomb array instance to perform plot operations.
        x_solution: The solution data used for reconstruction.
        N_obs (`int`, optional): Number of observations for simulation. Defaults to 300.
    """
    display(Markdown("---"))
    udp.plot_simulated_reconstruction(x_solution, N_obs, image_path="../data/star.jpg")
    display(Markdown("---"))
    udp.plot_simulated_reconstruction(x_solution, N_obs, image_path="../data/nebula.jpg")

def print_result(udp : orbital_golomb_array, x_solution, N_obs : int = 300, show_simulated_reconstruction : bool = False) -> None:
    """ Prints the result details and visualizes the given solution.

    Args:
        udp (`orbital_golomb_array`): An instance of the orbital golomb array class, used to evaluate the fitness and plot the solution.
        x_solution (`list` of length N): The solution to be evaluated and plotted.
        plot_simulated_reconstruction (`int`, optional): Show image recostruction of star.jpeg and nebula.jpeg
        N_obs (`int`, optional): Number of observations for simulating reconstruction.
    """
    
    print("Solution: ", x_solution)
    print("Fitness: ", udp.fitness(x_solution))
    udp.plot(x_solution, figsize=(25,7))

    if show_simulated_reconstruction:
        plot_simulated_reconstruction(udp, x_solution, N_obs)  

def plot_in_3D_space(UDP: orbital_golomb_array, x_encoded : list[(float,float,float)], meas : int = 2) -> None:
    """
    Plots the satellites in 3D space based on the encoded positions and measurement index.

    Args:
        UDP (`orbital_golomb_array`): An instance of the orbital golomb array class.
        x_encoded (`list[(float,float,float)]`): Encoded positions of the satellites.
        meas (`int`, optional): Measurement index. Defaults to 2.
    """
    
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