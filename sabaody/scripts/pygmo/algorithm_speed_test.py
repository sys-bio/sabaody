# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from pygmo import island as pg_island, problem, rosenbrock, simulated_annealing, de
from math import sqrt

def benchmark_simulated_annealing():
    island = pg_island(
        algo=simulated_annealing(Ts=1.,Tf=.01),
        prob=problem(rosenbrock(5)),
        size=10)

    N = 10
    print('Simulated Annealing (pop. size {})'.format(island.get_population().get_f().size))
    for k in range(N):
        island.evolve()
        island.wait()
        d = sqrt(float(((island.get_population().champion_x-rosenbrock(5).best_known())**2).mean()))
        print('SA {:2}/{}: best fitness {:9.2f}, deviation {:9.2f}, fevals {}'.format(
            k,N,float(island.get_population().champion_f[0]),
            d,island.get_population().problem.get_fevals()))

def benchmark_differential_evolution():
    island = pg_island(
        algo=de(gen=10),
        prob=problem(rosenbrock(5)),
        size=10)

    N = 10
    print('Differential Evolution (pop. size {})'.format(island.get_population().get_f().size))
    for k in range(N):
        island.evolve()
        island.wait()
        d = sqrt(float(((island.get_population().champion_x-rosenbrock(5).best_known())**2).mean()))
        print('DE {:2}/{}: best fitness {:9.2f}, deviation {:9.2f}, fevals {}'.format(
            k,N,float(island.get_population().champion_f[0]),
            d,island.get_population().problem.get_fevals()))

benchmark_simulated_annealing()
benchmark_differential_evolution()
