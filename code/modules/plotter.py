from matplotlib import pyplot as plt
from IPython.display import display, Markdown
from modules.golomb_problem import orbital_golomb_array, x_encoded_into_grid_on_t_meas, compute_unique_distances_and_sats_in_grid

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
    distance, sat = compute_unique_distances_and_sats_in_grid(udp,x_solution)
    print("N sat: ", udp.n_sat,"\tGrid size: ", udp.grid_size) 
    print("Solution: ", x_solution)
    distance *=  100
    sat *= 100
    print(f"Default Fitness: {udp.fitness(x_solution)[0]}\tDiverse Distances [%]: {distance:.4f}\tSatellites in Grid [%]: {sat:.4f}")
    udp.plot(x_solution, figsize=(25,7))

    if show_simulated_reconstruction:
        plot_simulated_reconstruction(udp, x_solution, N_obs)
    plt.close('all')

def plot_fitness_improvement(evolution):
    """
    Plots the fitness improvement over generations or iterations.

    Args:
        evolution (`object` or `list`): An object or a list representing the evolution data. 
        The object should either have a method `get_log()` or an attribute `history`, 
        containing the fitness information. If a list is provided, it is treated as the fitness values directly.

    Raises:
        ValueError: If the `evolution` object does not have the expected attributes or is not a list.
    """
    if hasattr(evolution, 'get_log'):
        generations = range(1, (len(evolution.get_log())*2)+1)
        fitness_values = [log[2] for log in evolution.get_log() for _ in (0, 1)]
    elif hasattr(evolution, 'history'):
        generations = range(len(evolution.history))
        fitness_values = [log['fitness'] for log in evolution.history]
    elif isinstance(evolution, list):
        generations = range(len(evolution))
        fitness_values = evolution  # Use list values as fitness values
    else:
        raise ValueError("Unsupported evolution object")

    plt.figure(figsize=(15,7))
    plt.margins(0.01)
    plt.grid(True)
    plt.plot(generations, fitness_values, label='Fitness Over Generations')
    # min_fitness_index = fitness_values.index(min(fitness_values))
    # plt.axvline(x=min_fitness_index, color='r', linestyle='--', label=f'First Minimum Fitness:{min_fitness_index}')
    plt.xticks(ticks=range(1, len(generations)+2, max(1, len(generations) // 25))) # one tick every len(generations)/25
    plt.xlabel('Generations|Iterations')
    plt.xlim(left=1)
    plt.ylabel('Fitness')
    plt.title('Fitness Improvement Over Generations|Iterations')
    plt.legend()
    plt.show()

def plot_in_3D_space(UDP: orbital_golomb_array, x_encoded : list[(float,float,float)], meas : int = 2) -> None:
    """
    Plots the satellites in 3D space based on the encoded positions and measurement index.

    Args:
        UDP (`orbital_golomb_array`): An instance of the orbital golomb array class.
        x_encoded (`list[(float,float,float)]`): Encoded positions of the satellites.
        meas (`int`, optional): Measurement index. Defaults to 2.
    """
    import plotly.graph_objects as go
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
    tick_plot = [i for i in range(0, UDP.grid_size, 1)]
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