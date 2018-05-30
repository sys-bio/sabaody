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
    def __init__(self, id, problem_factory, migrator, island_ids, domain_qualifier, mc_host, mc_port=11211):
        self.id = id
        self.mc_host = mc_host
        self.mc_port = mc_port
        self.problem_factory = problem_factory
        self.domain_qualifier = domain_qualifier
        self.migrator = migrator
        self.island_ids = island_ids

def run_island(island):
    import pygmo as pg
    from multiprocessing import cpu_count
    from pymemcache.client.base import Client
    from sabaody.migration import BestSPolicy, FairRPolicy
    from sabaody.migration_central import CentralMigrator
    mc_client = Client((island.mc_host,island.mc_port))
    migrator = CentralMigrator('http://luna:10100')

    #udp = island.problem_factory()

    algorithm = pg.algorithm(pg.de())
    #problem = pg.problem(udp)
    problem = island.problem_factory()
    # TODO: configure pop size
    i = pg.island(algo=algorithm, prob=problem, size=20)

    mc_client.set(island.domain_qualifier('island', str(island.id), 'status'), 'Running', 10000)
    mc_client.set(island.domain_qualifier('island', str(island.id), 'n_cores'), str(cpu_count()), 10000)
    #print('Starting island {} with {} cpus'.format(str(i.id), str(cpu_count())))

    evolve_steps = 10
    rounds = 10
    migration_log = []
    for x in range(rounds):
        i.evolve(evolve_steps)
        i.wait()

        # perform migration
        # send migrants
        selection_policy = BestSPolicy(migration_rate=10)
        pop = i.get_population()
        candidates,candidate_f = selection_policy.select(pop)
        for connected_island in island.island_ids:
            if connected_island != island.id:
                for candidate,f in zip(candidates,candidate_f):
                    migrator.push_migrant(connected_island, candidate, f, src_island_id=island.id)
        # receive migrants
        deltas,src_ids = migrator.replace(island.id, pop, FairRPolicy())
        i.set_population(pop)
        migration_log.append((float(pop.champion_f[0]),deltas,src_ids))

    import socket
    hostname = socket.gethostname()
    ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    return (ip, hostname, island.id, migration_log, i.get_population().problem.get_fevals())

class Archipelago:
    def __init__(self, num_islands, problem_factory, initial_score, topology, domain_qualifier, mc_host, mc_port=11211):
        from pymemcache.client.base import Client
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

    def run(self, sc):
        from sabaody.migration_central import CentralMigrator
        migrator = CentralMigrator('http://luna:10100')
        for island_id in self.island_ids:
            migrator.define_migrant_pool(island_id, 5) # FIXME: hardcoded
        #islands = sc.parallelize(self.island_ids).map(lambda u: Island(u, self.problem_factory, self.domain_qualifier, self.mc_host, self.mc_port))
        islands = [Island(u, problem_factory=self.problem_factory, migrator=None, island_ids=self.island_ids, domain_qualifier=self.domain_qualifier, mc_host=self.mc_host, mc_port=self.mc_port) for u in self.island_ids]
        #print(islands.map(lambda i: i.id).collect())
        #print(islands.map(lambda i: i.run()).collect())
        #from .worker import run_island
        return sc.parallelize(islands).map(run_island).collect()



