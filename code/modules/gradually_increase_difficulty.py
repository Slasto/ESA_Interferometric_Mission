from modules.golomb_problem import (
    orbital_golomb_array,
    compute_unique_distances_and_sats_in_grid,
    similarity_chk
)
from IPython.display import display, Markdown, clear_output
import matplotlib.pyplot as plt
from tqdm import tqdm
import os

def increase_difficulty(
    udp: orbital_golomb_array, n_sats_range: range, optimizer : callable, verbose : bool = True, file_name: str = None
) -> list[tuple[float, list[float]]]:
    """
    Increase the difficulty of finding optimal solutions by iterating over a range of satellite numbers.

    Args:
        udp (`orbital_golomb_array`): The orbital Golomb problem data structure.
        n_sats_range (`range`): The range of satellite counts to optimize over.
        optimizer (`callable`): A function that takes udp and n_sats as arguments and returns a tuple
                              of golomb_fitness and a solution (list of floats).
        print_table (bool, optional): Whether to display the solutions table after each iteration. Defaults to False.
        file_name (`str`, optional): If provided, the results will be saved to 'logs/{file_name}.log'. Defaults to None.

    Returns:
        `list[tuple[float, list[float]]]`: A list of tuples with each tuple containing the fitness score and the
                                          corresponding solution for each satellite count.
    """
    result = dict()

    for n_sats in tqdm(n_sats_range, "Optimization on"):
        udp.n_sat = n_sats
        
        if verbose:
            show_table_of_solutions(result)
            display(Markdown("---"))
            
        golomb_fitness, solution = optimizer(udp)

        distances_score, sats_in_grid_score = compute_unique_distances_and_sats_in_grid(udp,solution)
        ssim_score = similarity_chk(udp, solution, n_orb=300)
        result[udp.n_sat] = {
            "fitness": golomb_fitness,
            "diverse_distances_metric": distances_score,
            "satellites_in_grid": sats_in_grid_score,
            "x_encoded": solution,
            "ssim": ssim_score
        }
        if verbose :
            clear_output()

    if file_name is not None: 
        os.makedirs("logs", exist_ok=True)

    if verbose :
        clear_output()
        plot_results(result, file_name)
        show_table_of_solutions(result)

    if file_name is not None:
        with open(f"logs/{file_name}.log", "w") as file:
            file.write(str(result))
        print("Log and plot have been saved in the 'logs' folder")

    return result

def show_table_of_solutions(result: dict) -> None:
    """
    Display a Markdown table of solutions yielded by the `increase_difficulty()` function's dictionary-like result.

    Args:
        result (`dict`): A dictionary where each key is the number of satellites (N_sats)
                       and its value is another dictionary containing:
                       - "fitness": A float value of the fitness metric.
                       - "diverse_distances_metric": A float value representing the diverse distance metric.
                       - "satellites_in_grid": A float value indicating the percentage of satellites in the grid.
    """
    table_header = "| N_sats | Original fitness | Unique distances [%] | Satellites in grid [%] | SSIM (xy,xz,yz) [%] | \n|---|---|---|---| --- |\n"
    for n_sats, values in result.items():
        fitness = values["fitness"]
        diverse_distances_metric = values["diverse_distances_metric"] * 100
        satellites_in_grid = values["satellites_in_grid"] *100
        ssim_score = [round(i*100,2) for i in values["ssim"]]
        
        table_header += f"| {n_sats} | {(fitness):.4f} | {diverse_distances_metric:.2f} | {satellites_in_grid:.2f} | {ssim_score} |\n"
    display(Markdown(table_header))

def plot_results(result: dict, file_name : str = None):
    n_sats = list(result.keys())
    fitness = [result[n]["fitness"] for n in n_sats]
    diverse_distances = [result[n]["diverse_distances_metric"] for n in n_sats]
    satellites_in_grid = [result[n]["satellites_in_grid"] for n in n_sats]

    fig, axs = plt.subplots(1, 3, figsize=(14, 4))

    axs[0].plot(n_sats, fitness, marker='o', linestyle='-')
    axs[0].set_title('Golomb Fitness')
    axs[0].set_xlabel('Number of Satellites')
    axs[0].set_ylabel('Fitness')
    axs[0].grid(True)

    axs[1].plot(n_sats, diverse_distances, marker='o', linestyle='-', color='orange')
    axs[1].set_title('Diverse Distances Metric')
    axs[1].set_xlabel('Number of Satellites')
    axs[1].set_ylabel('Diverse Distances [%]')
    axs[1].grid(True)

    axs[2].plot(n_sats, satellites_in_grid, marker='o', linestyle='-', color='green')
    axs[2].set_title('Satellites in Grid')
    axs[2].set_xlabel('Number of Satellites')
    axs[2].set_ylabel('Satellites in Grid [%]')
    axs[2].grid(True)
    
    plt.tight_layout()

    if file_name is not None:
        plt.savefig(f'logs/{file_name}_score.svg', format='svg')

    plt.show()
    plt.close(fig)
    plot_ssim(result, file_name)

def plot_ssim(result: dict, file_name : str = None):
    n_sats = list(result.keys())
    ssim = [result[n]["ssim"] for n in n_sats]

    ssim_xy = [score[0] for score in ssim]
    ssim_xz = [score[1] for score in ssim]
    ssim_yz = [score[2] for score in ssim]

    fig, ax = plt.subplots(figsize=(14, 4))

    ax.plot(n_sats, ssim_xy, marker='o', linestyle='-', label='SSIM XY')
    ax.plot(n_sats, ssim_xz, marker='o', linestyle='-', label='SSIM XZ')
    ax.plot(n_sats, ssim_yz, marker='o', linestyle='-', label='SSIM YZ')

    ax.set_title('SSIM Components per Number of Satellites')
    ax.set_xlabel('Number of Satellites')
    ax.set_ylabel('SSIM')
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    if file_name is not None :
        plt.savefig(f'logs/{file_name}_ssim.svg', format='svg')

    plt.show()
    plt.close(fig)

    