# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from roadrunner import RoadRunner, Logger
Logger.disableConsoleLogging()
Logger.setLevel(Logger.LOG_FATAL)

from params import getDefaultParamValues, getUpperBound, getLowerBound
from b2problem import B2_UDP

from pygmo import island as pg_island, problem, rosenbrock, simulated_annealing, de, mp_island
from math import sqrt


def benchmark_loading_time():
    import arrow
    time_start = arrow.utcnow()
    r = RoadRunner('../../../../../sbml/b2.xml')
    delta_t = arrow.utcnow() - time_start
    print('Loading time:', delta_t)

def benchmark_simulated_annealing():
    island = pg_island(
        algo=simulated_annealing(Ts=1.,Tf=.01),
        prob=problem(B2_UDP(getLowerBound(),getUpperBound(),'../../../../../sbml/b2.xml')),
        size=10)

    N = 10
    import arrow
    time_start = arrow.utcnow()
    print('Simulated Annealing (pop. size {})'.format(island.get_population().get_f().size))
    for k in range(N):
        island.evolve()
        island.wait()
        delta_t = arrow.utcnow() - time_start
        print('SA {:2}/{}: best fitness {:9.2f}, fevals {}, duration {}'.format(
            k,N,float(island.get_population().champion_f[0]),
            island.get_population().problem.get_fevals(),
            delta_t))


def benchmark_differential_evolution(generations):
    island = pg_island(
        algo=de(gen=generations),
        prob=B2_UDP(getLowerBound(),getUpperBound(),'../../../../../sbml/b2.xml'),
        size=10)

    N = 50
    import arrow
    time_start = arrow.utcnow()
    print('Differential Evolution (pop. size {})'.format(island.get_population().get_f().size))
    for k in range(N):
        island.evolve()
        island.wait()
        delta_t = arrow.utcnow() - time_start
        print('DE {:2}/{}: best fitness {:9.2f}, fevals {}, duration {}'.format(
            k,N,float(island.get_population().champion_f[0]),
            island.get_population().problem.get_fevals(),
            delta_t))


def benchmark_differential_evolution_no_pool(generations):
    island = pg_island(
        algo=de(gen=generations),
        prob=B2_UDP(getLowerBound(),getUpperBound(),'../../../../../sbml/b2.xml'),
        size=10,
        udi=mp_island(use_pool=False))

    N = 50
    import arrow
    time_start = arrow.utcnow()
    print('Differential Evolution (no pool, pop. size {})'.format(island.get_population().get_f().size))
    for k in range(N):
        island.evolve()
        island.wait()
        delta_t = arrow.utcnow() - time_start
        print('DE {:2}/{}: best fitness {:9.2f}, fevals {}, duration {}'.format(
            k,N,float(island.get_population().champion_f[0]),
            island.get_population().problem.get_fevals(),
            delta_t))


if __name__ == "__main__":
    benchmark_loading_time()
    benchmark_differential_evolution(10)
    benchmark_differential_evolution_no_pool(10)
    # benchmark_simulated_annealing()
