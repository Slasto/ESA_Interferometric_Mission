from modules.golomb_problem import (
    orbital_golomb_array,
    compute_unique_distances_and_sats_in_grid
)
from IPython.display import display, Markdown, clear_output
import matplotlib.pyplot as plt
from tqdm import tqdm
import os


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
    table_header = "| N_sats | Fitness | Diverse Distances [%] | Satellites in Grid [%] | \n|---|---|---|---|\n"
    for n_sats, values in result.items():
        fitness = values["fitness"]
        diverse_distances_metric = values["diverse_distances_metric"]
        satellites_in_grid = values["satellites_in_grid"]
        table_header += f"| {n_sats} | {fitness:.4f} | {diverse_distances_metric:.4f} | {satellites_in_grid:.4f} |\n"
    display(Markdown(table_header))


def increase_difficulty(
    udp: orbital_golomb_array, n_sats_range: range, optimizer : callable, verbose : bool = False, file_name: str = None
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
        if verbose:
            clear_output()
            show_table_of_solutions(result)
            display(Markdown("---"))
        golomb_fitness, solution = optimizer(udp, n_sats, verbose)

        distances_score, sats_in_grid_score = compute_unique_distances_and_sats_in_grid(udp,solution)

        result[n_sats] = {
            "fitness": golomb_fitness,
            "diverse_distances_metric": distances_score,
            "satellites_in_grid": sats_in_grid_score,
            "x_encoded": solution,
        }
    if verbose :
        clear_output()
        plot_results(result)
        show_table_of_solutions(result)

    if file_name is not None:
        os.makedirs("logs", exist_ok=True)
        with open(f"logs/{file_name}.log", "w") as file:
            file.write(str(result))
        print(f"Log has been saved in 'logs/{file_name}.log'")

    return result

def plot_results(result: dict):
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
    plt.show()