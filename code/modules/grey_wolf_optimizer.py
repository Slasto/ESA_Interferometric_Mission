# src: https://www.geeksforgeeks.org/implementation-of-grey-wolf-optimization-gwo-algorithm/ 
import random
import copy    # array-copying convenience

class __wolf: 
  def __init__(self, fitness, dim, minx, maxx, seed): 
    self.rnd = random.Random(seed) 
    self.position = [0.0 for i in range(dim)] 
  
    for i in range(dim): 
      self.position[i] = ((maxx - minx) * self.rnd.random() + minx) 
  
    self.fitness = fitness(self.position) # curr fitness 
  
  
  
# grey wolf optimization (GWO) 
def gwo(fitness, max_iter, num_particles, dim, minx, maxx, verbose=True): 
    """
    Performs Grey Wolf Optimization (GWO) to find the best solution for a given fitness function.

    Args:
        fitness (`func`): A fitness function that evaluates the quality of a solution.
        max_iter (`int`): The maximum number of iterations to perform.
        num_particles (`int`): The number of wolves in the population.
        dim (`int`): The dimensionality of the search space.
        minx (`int`): The minimum boundary of the search space.
        maxx (`int`): The maximum boundary of the search space.
        verbose (`bool` optional) : Print settings and result of gwo 
    Returns:
        y(`list` of length N): Chromosome contains position of the best solution found.
    """
    if verbose:
      print("\nBegin grey wolf optimization\n") 
      print("Setting num_particles = " + str(num_particles)) 
      print("Setting max_iter    = " + str(max_iter)) 
      print("\nStarting GWO algorithm\n") 

    rnd = random.Random() 
  
    # create n random wolves  
    population = [ __wolf(fitness, dim, minx, maxx, i) for i in range(num_particles)] 
  
    # On the basis of fitness values of wolves  
    # sort the population in asc order 
    population = sorted(population, key = lambda temp: temp.fitness) 
  
    # best 3 solutions will be called as  
    # alpha, beta and gaama 
    alpha_wolf, beta_wolf, gamma_wolf = copy.copy(population[: 3]) 
    vet_fitness_alpha = []
  
  
    # main loop of gwo 
    Iter = 0
    while Iter < max_iter: 
  
        # after every 10 iterations  
        # print iteration number and best fitness value so far 
        if Iter % 10 == 0 and Iter > 1 and verbose: 
            print("Iter = " + str(Iter) + " best fitness = %.4f" % alpha_wolf.fitness) 
  
        # linearly decreased from 2 to 0 
        a = 2*(1 - Iter/max_iter) 
  
        # updating each population member with the help of best three members  
        for i in range(num_particles): 
            A1, A2, A3 = a * (2 * rnd.random() - 1), a * ( 
              2 * rnd.random() - 1), a * (2 * rnd.random() - 1) 
            C1, C2, C3 = 2 * rnd.random(), 2*rnd.random(), 2*rnd.random() 
  
            X1 = [0.0 for i in range(dim)] 
            X2 = [0.0 for i in range(dim)] 
            X3 = [0.0 for i in range(dim)] 
            Xnew = [0.0 for i in range(dim)] 
            for j in range(dim): 
                X1[j] = alpha_wolf.position[j] - A1 * abs( 
                  C1 * alpha_wolf.position[j] - population[i].position[j]) 
                X2[j] = beta_wolf.position[j] - A2 * abs( 
                  C2 *  beta_wolf.position[j] - population[i].position[j]) 
                X3[j] = gamma_wolf.position[j] - A3 * abs( 
                  C3 * gamma_wolf.position[j] - population[i].position[j]) 
                Xnew[j]+= X1[j] + X2[j] + X3[j] 
              
            for j in range(dim): 
                Xnew[j]/=3.0
              
            # fitness calculation of new solution 
            fnew = fitness(Xnew) 
  
            # greedy selection 
            if fnew < population[i].fitness: 
                population[i].position = Xnew 
                population[i].fitness = fnew 
                  
        # On the basis of fitness values of wolves  
        # sort the population in asc order 
        population = sorted(population, key = lambda temp: temp.fitness) 
  
        # best 3 solutions will be called as  
        # alpha, beta and gaama 
        alpha_wolf, beta_wolf, gamma_wolf = copy.copy(population[: 3]) 
        vet_fitness_alpha.append(fitness(alpha_wolf.position))

          
        Iter+= 1
    # end-while 
    if verbose:
      print("\nGWO completed\n") 
      print("\nBest solution found:") 
      print(["%.6f"%alpha_wolf.position[k] for k in range(dim)]) 
      fitness_minimum_gwo = fitness(alpha_wolf.position)  
      print("fitness of best solution = %.6f" % fitness_minimum_gwo) 
      print("\nEnd GWO\n") 
    # returning the best solution 
    return alpha_wolf.position, vet_fitness_alpha 