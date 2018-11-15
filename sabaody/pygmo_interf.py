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

#def serialize_pg_algorithm(algorithm):
    #import pygmo as pg
    #if isinstance(algorithm, pg.core.bee_colony):
        #return {'type': 'bee_colony',
                #'gen': algorithm.gen,
                #'limit': algorithm.limit,
                #'seed': algorithm.seed}
    #elif isinstance(algorithm, pg.core.de):
        #return {'type': 'de',
                #'gen': algorithm.gen,
                #'F': algorithm.F,
                #'CR': algorithm.CR,
                #'variant': algorithm.variant,
                #'ftol': algorithm.ftol,
                #'xtol': algorithm.xtol,
                #'seed': algorithm.seed}
    ## TODO: rest
    #else:
        ## if not a pygmo2 alg, just return as-is
        #return algorithm

#def deserialize_pg_algorithm(algorithm):
    #import pygmo as pg
    #if not isinstance(algorithm, dict) or not 'type' in algorithm:
        #return algorithm
    #t = algorithm['type']
    #kwargs = {k:v for k,v in algorithm.items() if k != 'type'}
    #if t == 'bee_colony':
        #return pg.bee_colony(**kwargs)
    #elif t == 'de':
        #return pg.de(**kwargs)

class Island:
    def __init__(self, id, algorithm, size, domain_qualifier=None, mc_host=None, mc_port=None):
        self.id = id
        self.mc_host = mc_host
        self.mc_port = mc_port
        #self.problem = problem
        self.algorithm = algorithm
        self.size = size
        self.domain_qualifier = domain_qualifier

    #def __getstate__(self):
        #return {**self.__dict__.copy(), 'algorithm': serialize_pg_algorithm}

def run_island(island, topology, migrator, udp, rounds, metric=None):
    # TODO: pass pygmo problem not udp
    import pygmo as pg
    from multiprocessing import cpu_count
    from pymemcache.client.base import Client
    from sabaody.migration import BestSPolicy, FairRPolicy
    from sabaody.migration_central import CentralMigrator
    if island.mc_host:
        mc_client = Client((island.mc_host,island.mc_port))
    else:
        mc_client = None

    # TODO: configure pop size
    i = pg.island(algo=island.algorithm, prob=pg.problem(udp), size=island.size)

    if mc_client is not None:
        mc_client.set(island.domain_qualifier('island', str(island.id), 'status'), 'Running', 10000)
        mc_client.set(island.domain_qualifier('island', str(island.id), 'n_cores'), str(cpu_count()), 10000)

    migration_log = []
    for x in range(rounds):
        if mc_client is not None:
            mc_client.set(island.domain_qualifier('island', str(island.id), 'round'), str(x), 10000)

        i.evolve()
        i.wait()

        # perform migration
        migrator.sendMigrants(island.id, i, topology)
        deltas,src_ids = migrator.receiveMigrants(island.id, i, topology)
        if metric is not None:
            metric.process_deltas(deltas,src_ids,float(i.get_population().champion_f[0]))
        migration_log.append((float(i.get_population().champion_f[0]),deltas,src_ids))

    #import socket
    #hostname = socket.gethostname()
    #ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    #return (ip, hostname, island.id, migration_log, i.get_population().problem.get_fevals())
    return i.get_population().champion_f[0]

class Archipelago:
    def __init__(self, topology, metric=None):
        self.topology = topology
        self.metric = metric

        self.mc_host = None
        self.mc_port = None
        self.domain_qualifier = None

    def set_mc_server(self, mc_host, mc_port, domain_qualifier):
        from pymemcache.client.base import Client
        self.mc_host = mc_host
        self.mc_port = mc_port
        self.domain_qualifier = domain_qualifier
        if self.mc_host:
            mc_client = Client((self.mc_host,self.mc_port))
            mc_client.set(self.domain_qualifier('islandIds'), dumps(self.topology.island_ids), 10000)

    def run(self, sc, migrator, udp, rounds):
        def worker(island):
            return run_island(island,self.topology,migrator,udp,rounds,self.metric)
        return sc.parallelize(self.topology.islands, numSlices=len(self.topology.islands)).map(worker).collect()
