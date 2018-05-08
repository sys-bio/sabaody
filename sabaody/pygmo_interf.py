from __future__ import print_function, division, absolute_import

from .utils import expect, check_vector

from pymemcache.client.base import Client

from abc import ABC, abstractmethod
from numpy import array
from typing import SupportsFloat
from uuid import uuid4
from json import dumps, loads


class Evaluator(ABC):
    '''
    Evaluates an objective function.
    Required to implement at least the functino evaluate,
    which returns a double precision float.
    '''
    @abstractmethod
    def evaluate(self):
        # type: () -> SupportsFloat
        '''Evaluates the objective function.'''
        pass


class Problem:
    def __init__(self, evaluator, lb, ub):
        # type: (Evaluator, array, array) -> None
        '''
        Inits the problem with an objective evaluator
        (implementing the method evaluate), the parameter
        vector lower bound (a numpy array) and upper bound.
        Both bounds must have the same dimension.
        '''
        check_vector(lb)
        check_vector(ub)
        expect(len(lb) == len(ub), 'Bounds mismatch')
        self.evaluator = evaluator
        self.lb = lb
        self.ub = ub

    def fitness(self, x):
        return evaluator.evaluate(x)

    def get_bounds(self):
        return (lb,ub)

    def get_name(self):
        return 'Sabaody udp'

    def get_extra_info(self):
        return 'Sabaody extra info'

class Island:
    def __init__(self, id, problem_factory, domain_qualifier, mc_host, mc_port=11211):
        self.id = id
        self.mc_host = mc_host
        self.mc_port = mc_port
        self.problem_factory = problem_factory

    def run(self):
        import pygmo as pg
        from multiprocessing import cpu_count
        mc_client = Client((mc_host,mc_port))
        udp = self.problem_factory()

        algorithm = pg.algorithm(pg.diff_evo())
        problem = pg.problem(udp)
        # TODO: configure pop size
        a = pg.archipelago(n=cpu_count,algo=algorithm, prob=problem, pop_size=100)

        mc_client.set(self.domain_qualifier('island', str(self.id), 'status'), 'Running', 10000)
        mc_client.set(self.domain_qualifier('island', str(self.id), 'n_cores'), str(cpu_count()), 10000)
        print('Starting island {} with {} cpus'.format(str(self.id), str(cpu_count())))

        a.evolve(1)

class Archipelago:
    def __init__(self, num_islands, problem_factory, initial_score, topology, domain_qualifier, mc_host, mc_port=11211):
        self.num_islands = num_islands
        self.problem_factory = problem_factory
        self.initial_score = initial_score
        self.topology = topology
        self.domain_qualifier = domain_qualifier
        self.mc_host = mc_host
        self.mc_port = mc_port
        mc_client = Client((self.mc_host,self.mc_port))
        # construct islands
        self.island_ids = [str(uuid4()) for x in range(self.num_islands)]
        mc_client.set(self.domain_qualifier('islandIds'), dumps(self.island_ids), 10000)

    def run(self, sc, initial_score):
        islands = sc.parallelize(self.island_ids).map(lambda u: Island(u, self.problem_factory, self.domain_qualifier, self.mc_host, self.mc_port))
        print(islands.map(lambda i: i.id).collect())
        return



