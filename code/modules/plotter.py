from modules.golomb_simple import orbital_golomb_array


def print_resoult(udp : orbital_golomb_array, x_solution, N_obs : int = 300, image_path : str = "../data/star.jpg") :
    fit_0 = udp.fitness(x_solution)[0]
    fit_1 = fit_0 + 1
    print("solution: ", x_solution)
    print("wrost Fill factor: {:.5f}".format(fit_0), " ,\t wrost Empty factor(?) : {:.5f}".format(fit_1))
    udp.plot(x_solution, figsize=(25,7))
    udp.plot_simulated_reconstruction(x_solution, N_obs, image_path=image_path)
    return