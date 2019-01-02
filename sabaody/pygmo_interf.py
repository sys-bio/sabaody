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
    Required to implement at least the function evaluate,
    which returns a double precision float.
    '''
    @abstractmethod
    def evaluate(self):
        # type: () -> SupportsFloat
        '''Evaluates the objective function.'''
        pass

class Island:
    def __init__(self, id, algorithm, size, domain_qualifier=None, mc_host=None, mc_port=None):
        self.id = id
        self.mc_host = mc_host
        self.mc_port = mc_port
        self.algorithm = algorithm
        self.size = size
        self.domain_qualifier = domain_qualifier

def run_island(island, topology, migrator, udp, rounds, metric=None, monitor=None, problem=None):
    # TODO: pass pygmo problem not udp
    import pygmo as pg
    from multiprocessing import cpu_count
    from pymemcache.client.base import Client
    from sabaody.migration import BestSPolicy, FairRPolicy
    from sabaody.migration_central import CentralMigrator

    # TODO: configure pop size
    print('algorithm ', island.algorithm)
    print(dir(island.algorithm))
    if hasattr(island.algorithm, 'maxeval'):
        # print('maxeval ', island.algorithm.maxeval)
        island.algorithm.maxeval = 1000
    if hasattr(island.algorithm, 'maxtime'):
        # print('maxtime ', island.algorithm.maxt.ime)
        island.algorithm.maxtime = 1
    if problem is not None:
        i = pg.island(algo=island.algorithm, prob=problem, size=island.size, udi=pg.mp_island(use_pool=False))
    else:
        i = pg.island(algo=island.algorithm, prob=pg.problem(udp), size=island.size, udi=pg.mp_island(use_pool=False))

    if monitor is not None:
        monitor.update('Running', 'island', island.id, 'status')
        monitor.update(cpu_count(), 'island', island.id, 'n_cores')

    migration_log = []
    best_f = None
    best_x = None
    for round in range(rounds):
        if monitor is not None:
            monitor.update(round, 'island', island.id, 'round')

        from interruptingcow import timeout
        from .timecourse.timecourse_sim_irreg import StalledSimulation
        # with timeout(10, StalledSimulation):
        # print('island {} begin evolve'.format(island.id))
        i.evolve()
        i.wait()
        # print('island {} evolve finished'.format(island.id))

        # perform migration
        migrator.sendMigrants(island.id, i, topology)
        deltas,src_ids = migrator.receiveMigrants(island.id, i, topology)

        f,x = i.get_population().champion_f,i.get_population().champion_x
        if best_f is None or f[0] < best_f[0]:
            best_f = f
            best_x = x
        if monitor is not None:
            monitor.update('{:6.4}'.format(float(best_f[0])), 'island', island.id, 'best_f')

        # TODO: send objective function evaluations to metric
        if metric is not None:
            metric.process_champion(island.id, best_f, best_x, round)
            metric.process_deltas(deltas,src_ids, round)
        migration_log.append((float(i.get_population().champion_f[0]),deltas,src_ids))

    #import socket
    #hostname = socket.gethostname()
    #ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    #return (ip, hostname, island.id, migration_log, i.get_population().problem.get_fevals())
    return best_f, best_x

class Archipelago:
    def __init__(self, topology, metric=None, monitor=None):
        self.topology = topology
        # self.metric = metric
        self.monitor=monitor

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

    def run(self, sc, migrator, udp, rounds, problem=None):
        assert self.metric is not None
        def worker(island):
            return run_island(island,self.topology,
                migrator=migrator,
                udp=udp,
                rounds=rounds,
                metric=self.metric,
                monitor=self.monitor,
                problem=problem)
        return sc.parallelize(self.topology.islands, numSlices=len(self.topology.islands)).map(worker).collect()
