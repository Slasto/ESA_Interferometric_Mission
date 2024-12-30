import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

def is_not_convex(f: callable, num_variables: int, bounds=None, n_points : int=1000, num_jobs : int=4):
    """
    Check if the function `f` is not convex using parallel processing and more efficient sampling.
    
    Parameters:
        f: callable, a function taking (n, x) where n is the number of samples, and returns a scalar.
        num_variables: int, number of input variables in x.
        bounds: optional (2, num_variables) array of bounds for the input variables.
        max_time: maximum time to run the test in seconds.
        min_points: number of points to sample.
        num_jobs: number of parallel jobs to run (default is 4).
    
    Returns:
        bool: True if the function is not convex.
    
    Raises:
        TimeoutError: if the convexity check times out after `max_time` seconds.
    """

    # Generate points (use uniform sampling for better coverage of the space)
    def sample_points():
        if bounds is None:
            pts = np.random.randn(2, n_points, num_variables)
        else:
            pts = np.random.uniform(bounds[0], bounds[1], (2, n_points, num_variables))
        return pts

    def check_convexity(pts):
        mean_pt = np.mean(pts, axis=0)
        f_pts = (f(pts[0]) + f(pts[1])) / 2
        return np.any(f_pts < f(mean_pt))

    with ThreadPoolExecutor(max_workers=num_jobs) as executor:
        futures = [executor.submit(check_convexity, sample_points()) for _ in range(n_points)]

        for future in as_completed(futures):
            if future.result():
                return True

    raise TimeoutError(f"Could not find any counterexamples after {n_points} iterations, function may be convex.")

def is_not_concave(f: callable, num_variables: int, bounds=None, n_points : int=1000, num_jobs : int=4):
    """
    Check if the function `f` is not concave using parallel processing and more efficient sampling.
    
    Parameters:
        f: callable, a function taking (n, x) where n is the number of samples, and returns a scalar.
        num_variables: int, number of input variables in x.
        bounds: optional (2, num_variables) array of bounds for the input variables.
        max_time: maximum time to run the test in seconds.
        min_points: number of points to sample.
        num_jobs: number of parallel jobs to run (default is 4).
    
    Returns:
        bool: True if the function is not concave.
    
    Raises:
        TimeoutError: if the concavity check times out after `max_time` seconds.
    """

    # Convert f to a concave check by negating it
    f_neg = lambda x: -f(x)

    # Generate points
    def sample_points():
        if bounds is None:
            pts = np.random.randn(2, n_points, num_variables)
        else:
            pts = np.random.uniform(bounds[0], bounds[1], (2, n_points, num_variables))
        return pts

    def check_concavity(pts):
        mean_pt = np.mean(pts, axis=0)
        f_pts = (f_neg(pts[0]) + f_neg(pts[1])) / 2
        return np.any(f_pts < f_neg(mean_pt))

    with ThreadPoolExecutor(max_workers=num_jobs) as executor:
        futures = [executor.submit(check_concavity, sample_points()) for _ in range(n_points)]

        for future in as_completed(futures):
            if future.result():
                return True

    raise TimeoutError(f"Could not find any counterexamples after {n_points} iterations, function may be concave.")
