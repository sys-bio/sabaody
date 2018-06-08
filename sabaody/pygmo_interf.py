# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from .utils import check_vector, expect

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


class Island:
    def __init__(self, id, problem_constructor, algorithm_constructor, size, domain_qualifier, mc_host, mc_port=11211):
        self.id = id
        self.mc_host = mc_host
        self.mc_port = mc_port
        self.problem_constructor = problem_constructor
        self.algorithm_constructor = algorithm_constructor
        self.size = size
        self.domain_qualifier = domain_qualifier

def run_island(island, topology):
    import pygmo as pg
    from multiprocessing import cpu_count
    from pymemcache.client.base import Client
    from sabaody.migration import BestSPolicy, FairRPolicy
    from sabaody.migration_central import CentralMigrator
    mc_client = Client((island.mc_host,island.mc_port))
    migrator = CentralMigrator('http://luna:10100')

    algorithm = pg.de(gen=10)
    problem = island.problem_constructor()
    # TODO: configure pop size
    i = pg.island(algo=algorithm, prob=problem, size=20)

    mc_client.set(island.domain_qualifier('island', str(island.id), 'status'), 'Running', 10000)
    mc_client.set(island.domain_qualifier('island', str(island.id), 'n_cores'), str(cpu_count()), 10000)

    rounds = 10
    migration_log = []
    for x in range(rounds):
        i.evolve()
        i.wait()

        # perform migration
        migrator.sendMigrants(island.id, i, topology)
        deltas,src_ids = migrator.receiveMigrants(island.id, i, topology)
        migration_log.append((float(pop.champion_f[0]),deltas,src_ids))

    import socket
    hostname = socket.gethostname()
    ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    return (ip, hostname, island.id, migration_log, i.get_population().problem.get_fevals())

class Archipelago:
    def __init__(self, islands, topology, initial_score=None):
        from pymemcache.client.base import Client
        if initial_score is None:
            self.initial_score = ...
        else:
            self.initial_score = initial_score
        self.topology = topology
        self.mc_host = mc_host
        self.mc_port = mc_port
        mc_client = Client((self.mc_host,self.mc_port))
        mc_client.set(self.domain_qualifier('islandIds'), dumps(topology.island_ids), 10000)

    def run(self, sc):
        from sabaody.migration_central import CentralMigrator
        migrator = CentralMigrator('http://luna:10100')
        for island_id in self.island_ids:
            migrator.defineMigrantPool(island_id, 5) # FIXME: hardcoded
        #islands = sc.parallelize(self.island_ids).map(lambda u: Island(u, self.problem_factory, self.domain_qualifier, self.mc_host, self.mc_port))
        islands = [Island(u, problem_factory=self.problem_factory, domain_qualifier=self.domain_qualifier, mc_host=self.mc_host, mc_port=self.mc_port) for u in self.island_ids]
        #print(islands.map(lambda i: i.id).collect())
        #print(islands.map(lambda i: i.run()).collect())
        #from .worker import run_island
        return sc.parallelize(topology.islands).map(run_island).collect()



