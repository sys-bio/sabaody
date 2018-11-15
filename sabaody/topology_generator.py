# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody import Archipelago

from pygmo import de, de1220, pso, simulated_annealing, bee_colony, cmaes, nsga2
from pygmo import nlopt

class TopologyGenerator:
    '''
    Generates a set of topologies used for benchmarks.
    '''

    def __init__(self, island_size=20, migrant_pool_size=5, generations=10):
        self.topologies = []
        from sabaody.topology import TopologyFactory
        self.factory =  TopologyFactory(island_size=island_size,
                                        migrant_pool_size=migrant_pool_size)
        self.generations = generations


    def new_topology(self, desc, archipelago, category=None, algorithms=None):
        t = {
            'description': desc,
            'archipelago': archipelago,
            }
        if category is not None:
            t['category'] = category
        if algorithms is not None:
            t['algorithms'] = algorithms
        self.topologies.append(t)
        return t


    @classmethod
    def get_version(cls):
        # semantic version
        return (0,0,1)


    @classmethod
    def get_version_string(cls):
        return '{}.{}.{}'.format(*cls.get_version())


    def make_nelder_mead(self):
        nm = nlopt('neldermead')
        nm.selection = 'random'
        nm.replacement = 'random'
        return nm


    @classmethod
    def find(cls,desc,topologies):
        for t in topologies:
            if t['description'] == desc:
                return t['archipelago']
        raise RuntimeError('No such topology "{}"'.format(desc))


    @classmethod
    def find_in_database(cls, desc, user, host, pw, db, version, n_islands, island_size, migrant_pool_size, generations):
        major,minor,patch = version
        import MySQLdb
        mariadb_connection = MySQLdb.connect(host=host,user=user,passwd=pw,db=db)
        cursor = mariadb_connection.cursor()
        cursor.execute('SELECT Content FROM topology_sets WHERE '+\
            '(VersionMajor, VersionMinor, VersionPatch, NumIslands, IslandSize, MigrantPoolSize, Generations) = '+\
            '({major}, {minor}, {patch}, {n_islands}, {island_size}, {migrant_pool_size},{generations});'.format(
            major=major,
            minor=minor,
            patch=patch,
            n_islands=n_islands,
            island_size=island_size,
            migrant_pool_size=migrant_pool_size,
            generations=generations,
        ))
        from pickle import loads
        topologies = loads(cursor.fetchone()[0])
        return cls.find(desc,topologies)


    def generate_all(self, n):
        '''
        Generate a set of benchmark topologies.

        :param n: Number of islands.
        '''
        g = self.generations

        def assign_every_other_algo(archipelago, algo):
            for island in archipelago.topology.every_other_island():
                island.algorithm = algo
            return archipelago

        # one-way rings
        self.new_topology(
          desc='One-way ring, de',
          category='rings',
          algorithms=['de'],
          archipelago=Archipelago(self.factory.createOneWayRing(de(gen=g),n)))
        self.new_topology(
          desc='One-way ring, de1220',
          category='rings',
          algorithms=['de1220'],
          archipelago=Archipelago(self.factory.createOneWayRing(de1220(gen=g),n)))
        self.new_topology(
          desc='One-way ring, pso',
          category='rings',
          algorithms=['pso'],
          archipelago=Archipelago(self.factory.createOneWayRing(pso(gen=g),n)))
        self.new_topology(
          desc='One-way ring, simulated_annealing',
          category='rings',
          algorithms=['simulated_annealing'],
          archipelago=Archipelago(self.factory.createOneWayRing(simulated_annealing(),n)))
        self.new_topology(
          desc='One-way ring, bee_colony',
          category='rings',
          algorithms=['bee_colony'],
          archipelago=Archipelago(self.factory.createOneWayRing(bee_colony(gen=g),n)))
        self.new_topology(
          desc='One-way ring, cmaes',
          category='rings',
          algorithms=['cmaes'],
          archipelago=Archipelago(self.factory.createOneWayRing(cmaes(gen=g),n)))
        self.new_topology(
          desc='One-way ring, nsga2',
          category='rings',
          algorithms=['nsga2'],
          archipelago=Archipelago(self.factory.createOneWayRing(nsga2(gen=g),n)))
        # de + nelder mead combo
        self.de_nm_oring = self.new_topology(
          desc='One-way ring, de+nelder mead',
          category='rings',
          algorithms=['de','neldermead'],
          archipelago=assign_every_other_algo(Archipelago(self.factory.createOneWayRing(de(gen=g),n)), self.make_nelder_mead()))
        # de + nsga2 combo
        self.new_topology(
          desc='One-way ring, de+nsga2',
          category='rings',
          algorithms=['de','nsga2'],
          archipelago=assign_every_other_algo(Archipelago(self.factory.createOneWayRing(de(gen=g),n)), nsga2(gen=g)))

        # bidirectional rings
        self.new_topology(
          desc='Bidirectional ring, de',
          category='rings',
          algorithms=['de'],
          archipelago=Archipelago(self.factory.createBidirRing(de(gen=g),n)))
        self.new_topology(
          desc='Bidirectional ring, de1220',
          category='rings',
          algorithms=['de1220'],
          archipelago=Archipelago(self.factory.createBidirRing(de1220(gen=g),n)))
        self.new_topology(
          desc='Bidirectional ring, pso',
          category='rings',
          algorithms=['pso'],
          archipelago=Archipelago(self.factory.createBidirRing(pso(gen=g),n)))
        self.new_topology(
          desc='Bidirectional ring, simulated_annealing',
          category='rings',
          algorithms=['simulated_annealing'],
          archipelago=Archipelago(self.factory.createBidirRing(simulated_annealing(),n)))
        self.new_topology(
          desc='Bidirectional ring, bee_colony',
          category='rings',
          algorithms=['bee_colony'],
          archipelago=Archipelago(self.factory.createBidirRing(bee_colony(gen=g),n)))
        self.new_topology(
          desc='Bidirectional ring, cmaes',
          category='rings',
          algorithms=['cmaes'],
          archipelago=Archipelago(self.factory.createBidirRing(cmaes(gen=g),n)))
        self.new_topology(
          desc='Bidirectional ring, nsga2',
          category='rings',
          algorithms=['nsga2'],
          archipelago=Archipelago(self.factory.createBidirRing(nsga2(gen=g),n)))
        # de + nelder mead combo
        self.de_nm_bring = self.new_topology(
          desc='Bidirectional ring, de+nelder mead',
          category='rings',
          algorithms=['de','neldermead'],
          archipelago=assign_every_other_algo(Archipelago(self.factory.createBidirRing(de(gen=g),n)), self.make_nelder_mead()))
        # de + nsga2 combo
        self.new_topology(
          desc='Bidirectional ring, de+nsga2',
          category='rings',
          algorithms=['de','nsga2'],
          archipelago=assign_every_other_algo(Archipelago(self.factory.createBidirRing(de(gen=g),n)), nsga2(gen=g)))

        # bidirectional chains
        self.new_topology(
          desc='Bidirectional chain, de',
          category='rings',
          algorithms=['de'],
          archipelago=Archipelago(self.factory.createBidirChain(de(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, de1220',
          category='rings',
          algorithms=['de1220'],
          archipelago=Archipelago(self.factory.createBidirChain(de1220(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, pso',
          category='rings',
          algorithms=['pso'],
          archipelago=Archipelago(self.factory.createBidirChain(de1220(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, simulated_annealing',
          category='rings',
          algorithms=['simulated_annealing'],
          archipelago=Archipelago(self.factory.createBidirChain(simulated_annealing(),n)))
        self.new_topology(
          desc='Bidirectional chain, bee_colony',
          category='rings',
          algorithms=['bee_colony'],
          archipelago=Archipelago(self.factory.createBidirChain(bee_colony(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, cmaes',
          category='rings',
          algorithms=['cmaes'],
          archipelago=Archipelago(self.factory.createBidirChain(cmaes(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, nsga2',
          category='rings',
          algorithms=['nsga2'],
          archipelago=Archipelago(self.factory.createBidirChain(nsga2(gen=g),n)))

        return self.topologies


    def serialize(self, n):
        from pickle import dumps
        return dumps(self.generate_all(n))
