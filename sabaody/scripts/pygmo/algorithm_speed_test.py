# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from pygmo import island as pg_island, problem as pg_problem, rosenbrock, simulated_annealing

def benchmark_simulated_annealing():
    problem = pg_problem(rosenbrock(5))
    island = pg_island(
        algo=simulated_annealing(Ts=1.,Tf=.01),
        prob=problem,
        size=10)

    N = 100
    for k in range(N):
        island.evolve()
        from math import sqrt
        d = sqrt(float(((island.get_population().champion_x-rosenbrock(5).best_known())**2).mean()))
        print('Round {}/{}: best fitness {:9.2f}, deviation {:9.2f}, num. fun. evals {}'.format(
            k,N,float(island.get_population().champion_f[0]),
            d,island.get_population().problem.get_fevals()))

benchmark_simulated_annealing()
