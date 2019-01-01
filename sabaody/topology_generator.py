# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody import Archipelago

from pygmo import de, de1220, sade, ihs, pso, simulated_annealing, bee_colony, cmaes, nsga2
from pygmo import nlopt

from uuid import uuid4

class TopologyGenerator:
    '''
    Generates a set of topologies used for benchmarks.
    '''

    def __init__(self, n_islands, island_size=20, migrant_pool_size=5, generations=10):
        self.topologies = []
        from sabaody.topology import TopologyFactory
        self.factory =  TopologyFactory(island_size=island_size,
                                        migrant_pool_size=migrant_pool_size)
        self.n_islands = n_islands
        self.island_size = island_size
        self.migrant_pool_size = migrant_pool_size
        self.generations = generations
        self._generate_all(n_islands)


    def new_topology(self, desc, archipelago, category=None, algorithms=None):
        t = {
            'description': desc,
            'archipelago': archipelago,
            'id': uuid4(),
            'generations': self.generations,
            }
        if category is not None:
            t['category'] = category
        if algorithms is not None:
            t['algorithms'] = algorithms
        self.topologies.append(t)
        return t


    def get_checksum(self):
        # from pickle import dumps
        # return hash(dumps(self.topologies)) % 16777216
        return hash(self.get_version()) % 16777216


    @classmethod
    def get_version(cls):
        # semantic version
        return (0,1,0)


    @classmethod
    def get_version_string(cls):
        return '{}.{}.{}'.format(*cls.get_version())


    def make_nelder_mead(self):
        nm = nlopt('neldermead')
        nm.selection = 'best'
        nm.replacement = 'random'
        nm.maxtime = 1
        nm.maxeval = 10
        return nm


    def make_praxis(self):
        praxis = nlopt('praxis')
        praxis.selection = 'best'
        praxis.replacement = 'random'
        praxis.maxtime = 1
        praxis.maxeval = 10
        return praxis


    @classmethod
    def find(cls,desc,topologies):
        for t in topologies:
            if t['description'] == desc:
                return t
        raise RuntimeError('No such topology "{}"'.format(desc))


    def find_in_database(self, desc, user, host, pw, db):
        import MySQLdb
        mariadb_connection = MySQLdb.connect(host=host,user=user,passwd=pw,db=db)
        cursor = mariadb_connection.cursor()
        query_string = 'SELECT PrimaryKey,Content FROM topology_sets WHERE '+\
            '(Checksum, NumIslands, IslandSize, MigrantPoolSize, Generations) = '+\
            '({checksum}, {n_islands}, {island_size}, {migrant_pool_size},{generations});'.format(
            checksum=self.get_checksum(),
            n_islands=self.n_islands,
            island_size=self.island_size,
            migrant_pool_size=self.migrant_pool_size,
            generations=self.generations,
            )
        cursor.execute(query_string)
        from pickle import loads
        t = cursor.fetchone()
        if t is None:
            raise RuntimeError('Entry not found for query {}'.format(query_string))
        key = int(t[0])
        topologies = loads(t[1])
        return (self.find(desc,topologies),key)


    def _generate_all(self, n):
        '''
        Generate a set of benchmark topologies.

        :param n: Number of islands.
        '''
        g = self.generations

        def assign_every_other_algo(archipelago, algo):
            for island in archipelago.topology.endpoints:
                island.algorithm = algo
            return archipelago

        def assign_endpoints(archipelago, algo):
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
          desc='One-way ring, sade',
          category='rings',
          algorithms=['sade'],
          archipelago=Archipelago(self.factory.createOneWayRing(sade(gen=g),n)))
        self.new_topology(
          desc='One-way ring, ihs',
          category='rings',
          algorithms=['ihs'],
          archipelago=Archipelago(self.factory.createOneWayRing(ihs(gen=g),n)))
        self.new_topology(
          desc='One-way ring, pso',
          category='rings',
          algorithms=['pso'],
          archipelago=Archipelago(self.factory.createOneWayRing(pso(gen=g),n)))
        self.new_topology(
          desc='One-way ring, pso_gen',
          category='rings',
          algorithms=['pso_gen'],
          archipelago=Archipelago(self.factory.createOneWayRing(pso_gen(gen=g),n)))
        # self.new_topology(
        #   desc='One-way ring, simulated_annealing',
        #   category='rings',
        #   algorithms=['simulated_annealing'],
        #   archipelago=Archipelago(self.factory.createOneWayRing(simulated_annealing(Ts=1.,Tf=.01),n)))
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
        self.new_topology(
          desc='One-way ring, xnes',
          category='rings',
          algorithms=['xnes'],
          archipelago=Archipelago(self.factory.createOneWayRing(xnes(gen=g),n)))
        # de + nelder mead combo
        self.de_nm_oring = self.new_topology(
          desc='One-way ring, de+nelder mead',
          category='rings',
          algorithms=['de','neldermead'],
          archipelago=assign_every_other_algo(Archipelago(self.factory.createOneWayRing(de(gen=g),n)), self.make_nelder_mead()))
        # de + praxis combo
        self.new_topology(
          desc='One-way ring, de+praxis',
          category='rings',
          algorithms=['de','praxis'],
          archipelago=assign_every_other_algo(Archipelago(self.factory.createOneWayRing(de(gen=g),n)), self.make_praxis()))
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
          desc='Bidirectional ring, sade',
          category='rings',
          algorithms=['sade'],
          archipelago=Archipelago(self.factory.createBidirRing(sade(gen=g),n)))
        self.new_topology(
          desc='Bidirectional ring, ihs',
          category='rings',
          algorithms=['ihs'],
          archipelago=Archipelago(self.factory.createBidirRing(ihs(gen=g),n)))
        self.new_topology(
          desc='Bidirectional ring, pso',
          category='rings',
          algorithms=['pso'],
          archipelago=Archipelago(self.factory.createBidirRing(pso(gen=g),n)))
        self.new_topology(
          desc='Bidirectional ring, pso_gen',
          category='rings',
          algorithms=['pso'],
          archipelago=Archipelago(self.factory.createBidirRing(pso_gen(gen=g),n)))
        # self.new_topology(
        #   desc='Bidirectional ring, simulated_annealing',
        #   category='rings',
        #   algorithms=['simulated_annealing'],
        #   archipelago=Archipelago(self.factory.createBidirRing(simulated_annealing(),n)))
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
        self.new_topology(
          desc='Bidirectional ring, xnes',
          category='rings',
          algorithms=['xnes'],
          archipelago=Archipelago(self.factory.createBidirRing(xnes(gen=g),n)))
        # de + nelder mead combo
        self.de_nm_bring = self.new_topology(
          desc='Bidirectional ring, de+nelder mead',
          category='rings',
          algorithms=['de','neldermead'],
          archipelago=assign_every_other_algo(Archipelago(self.factory.createBidirRing(de(gen=g),n)), self.make_nelder_mead()))
        # de + praxis combo
        self.new_topology(
          desc='Bidirectional ring, de+praxis',
          category='rings',
          algorithms=['de','praxis'],
          archipelago=assign_every_other_algo(Archipelago(self.factory.createBidirRing(de(gen=g),n)), self.make_praxis()))
        # de + nsga2 combo
        self.new_topology(
          desc='Bidirectional ring, de+nsga2',
          category='rings',
          algorithms=['de','nsga2'],
          archipelago=assign_every_other_algo(Archipelago(self.factory.createBidirRing(de(gen=g),n)), nsga2(gen=g)))

        # bidirectional chains
        self.new_topology(
          desc='Bidirectional chain, de',
          category='chains',
          algorithms=['de'],
          archipelago=Archipelago(self.factory.createBidirChain(de(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, de1220',
          category='chains',
          algorithms=['de1220'],
          archipelago=Archipelago(self.factory.createBidirChain(de1220(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, sade',
          category='chains',
          algorithms=['sade'],
          archipelago=Archipelago(self.factory.createBidirChain(sade(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, ihs',
          category='chains',
          algorithms=['ihs'],
          archipelago=Archipelago(self.factory.createBidirChain(ihs(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, pso',
          category='chains',
          algorithms=['pso'],
          archipelago=Archipelago(self.factory.createBidirChain(pso(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, pso_gen',
          category='chains',
          algorithms=['pso_gen'],
          archipelago=Archipelago(self.factory.createBidirChain(pso_gen(gen=g),n)))
        # self.new_topology(
        #   desc='Bidirectional chain, simulated_annealing',
        #   category='chains',
        #   algorithms=['simulated_annealing'],
        #   archipelago=Archipelago(self.factory.createBidirChain(simulated_annealing(),n)))
        self.new_topology(
          desc='Bidirectional chain, bee_colony',
          category='chains',
          algorithms=['bee_colony'],
          archipelago=Archipelago(self.factory.createBidirChain(bee_colony(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, cmaes',
          category='chains',
          algorithms=['cmaes'],
          archipelago=Archipelago(self.factory.createBidirChain(cmaes(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, nsga2',
          category='chains',
          algorithms=['nsga2'],
          archipelago=Archipelago(self.factory.createBidirChain(nsga2(gen=g),n)))
        self.new_topology(
          desc='Bidirectional chain, xnes',
          category='chains',
          algorithms=['xnes'],
          archipelago=Archipelago(self.factory.createBidirChain(nsga2(gen=g),n)))
        # de + nelder mead combo
        self.new_topology(
          desc='Bidirectional chain, de+nelder mead',
          category='chains',
          algorithms=['de','neldermead'],
          archipelago=assign_endpoints(Archipelago(self.factory.createBidirChain(de(gen=g),n)), self.make_nelder_mead()))
        # de + praxis combo
        self.new_topology(
          desc='Bidirectional chain, de+praxis',
          category='chains',
          algorithms=['de','praxis'],
          archipelago=assign_endpoints(Archipelago(self.factory.createBidirChain(de(gen=g),n)), self.make_praxis()))
        # de + nsga2 combo
        self.new_topology(
          desc='Bidirectional chain, de+nsga2',
          category='chains',
          algorithms=['de','nsga2'],
          archipelago=assign_endpoints(Archipelago(self.factory.createBidirChain(de(gen=g),n)), nsga2(gen=g)))

        return self.topologies


    def serialize(self):
        from pickle import dumps
        return dumps(self.topologies)
