from modules.golomb_problem import (
    orbital_golomb_array,
    x_encoded_into_grid_on_t_meas,
    compute_n_unique_dist_on_xy_xz_yz,
)
from IPython.display import display, Markdown, clear_output
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
    udp: orbital_golomb_array, n_sats_range: range, optimizer : callable, print_table : bool = False, file_name: str = None
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
        if print_table:
            clear_output()
            show_table_of_solutions(result)
            display(Markdown("---"))
        golomb_fitness, solution = optimizer(udp, n_sats)

        # Additional score --- --- --- ---  --- --- ---  --- --- ---
        n_distances = 3 * n_sats * (n_sats - 1) // 2
        distances_score = 0
        sats_in_grid_score = 0
        for i in range(udp.n_meas):
            x_grid = x_encoded_into_grid_on_t_meas(udp, solution, i)
            xy_score, zy_score, yz_score = compute_n_unique_dist_on_xy_xz_yz(x_grid)
            distances_score += xy_score + zy_score + yz_score

            sats_in_grid_score += len(x_grid)

        distances_score /= n_distances * udp.n_meas
        sats_in_grid_score /= n_sats * udp.n_meas
        #  --- --- ---  --- --- ---  --- --- ---  --- --- ---  --- --- ---

        result[n_sats] = {
            "fitness": golomb_fitness,
            "diverse_distances_metric": distances_score,
            "satellites_in_grid": sats_in_grid_score,
            "x_encoded": solution,
        }
    if print_table :  
        show_table_of_solutions(result)

    if file_name is not None:
        os.makedirs("logs", exist_ok=True)
        with open(f"logs/{file_name}.log", "w") as file:
            file.write(str(result))
        print(f"Log has been saved in 'logs/{file_name}.log'")

    return result