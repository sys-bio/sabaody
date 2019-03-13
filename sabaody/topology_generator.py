# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody import Archipelago
from sabaody.topology import FullyConnectedTopology

from pygmo import de, de1220, sade, ihs, pso, pso_gen, simulated_annealing, bee_colony, cmaes, nsga2, xnes
from pygmo import nlopt
from toolz import partial
from itertools import islice, cycle

from uuid import uuid4

class TopologyGenerator:
    '''
    Generates a set of topologies used for benchmarks.
    '''

    def __init__(self, n_islands, island_size=20, migrant_pool_size=5, generations=10, seed=1):
        self.topologies = []
        from sabaody.topology import TopologyFactory
        self.factory =  TopologyFactory(island_size=island_size,
                                        migrant_pool_size=migrant_pool_size,
                                        seed=seed)
        self.name = 'pagmo'
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


    def find_by_desc(self, desc):
        for t in self.topologies:
            if t['description'] == desc:
                return t['archipelago']


    def get_checksum(self):
        # from pickle import dumps
        from hashlib import md5
        # return hash(dumps(self.topologies)) % 16777216
        # print('hash version {} = {}'.format(self.get_version(), hash(self.get_version())))
        # print('hash name {} = {}'.format(self.name, int(md5(self.name.encode('utf8')).hexdigest(),16)))
        return (hash(self.get_version()) + int(md5(self.name.encode('utf8')).hexdigest(),16)) % 16777216


    @classmethod
    def get_version(cls):
        # semantic version
        return (0,2,5,)


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
        mariadb_connection.close()
        if t is None:
            raise RuntimeError('Entry not found for query {}'.format(query_string))
        key = int(t[0])
        topologies = loads(t[1])
        return (self.find(desc,topologies),key)

    def create_variants(self, n, desc, category, constructor):
        def assign_2nd_alg(archipelago, algo):
            if category == 'rings':
                for island in archipelago.topology.every_other_island():
                    island.algorithm = algo
            elif hasattr(archipelago.topology, 'endpoints'):
                for island in archipelago.topology.endpoints:
                    island.algorithm = algo
            elif isinstance(archipelago.topology, FullyConnectedTopology):
                for island in islice(archipelago.topology.islands, None, None, 2):
                    island.algorithm = algo
            return archipelago

        def assign_algs(archipelago, algos):
            '''
            Evenly partitions and assigns algorithms to islands.
            '''
            for island,algo in zip(archipelago.topology.islands, cycle(algos)):
                island.algorithm = algo

        g = self.generations

        self.new_topology(
          desc='{}, de'.format(desc),
          category=category,
          algorithms=['de'],
          archipelago=Archipelago(constructor(de(gen=g),n)))
        self.new_topology(
          desc='{}, de1220'.format(desc),
          category=category,
          algorithms=['de1220'],
          archipelago=Archipelago(constructor(de1220(gen=g),n)))
        self.new_topology(
          desc='{}, sade'.format(desc),
          category=category,
          algorithms=['sade'],
          archipelago=Archipelago(constructor(sade(gen=g),n)))
        self.new_topology(
          desc='{}, ihs'.format(desc),
          category=category,
          algorithms=['ihs'],
          archipelago=Archipelago(constructor(ihs(gen=g),n)))
        self.new_topology(
          desc='{}, pso'.format(desc),
          category=category,
          algorithms=['pso'],
          archipelago=Archipelago(constructor(pso(gen=g),n)))
        self.new_topology(
          desc='{}, pso_gen'.format(desc),
          category=category,
          algorithms=['pso_gen'],
          archipelago=Archipelago(constructor(pso_gen(gen=g),n)))
        # self.new_topology(
        #   desc='{}, simulated_annealing'.format(desc),
        #   category=category,
        #   algorithms=['simulated_annealing'],
        #   archipelago=Archipelago(constructor(simulated_annealing(),n)))
        self.new_topology(
          desc='{}, bee_colony'.format(desc),
          category=category,
          algorithms=['bee_colony'],
          archipelago=Archipelago(constructor(bee_colony(gen=g),n)))
        self.new_topology(
          desc='{}, cmaes'.format(desc),
          category=category,
          algorithms=['cmaes'],
          archipelago=Archipelago(constructor(cmaes(gen=g),n)))
        self.new_topology(
          desc='{}, nsga2'.format(desc),
          category=category,
          algorithms=['nsga2'],
          archipelago=Archipelago(constructor(nsga2(gen=g),n)))
        self.new_topology(
          desc='{}, xnes'.format(desc),
          category=category,
          algorithms=['xnes'],
          archipelago=Archipelago(constructor(xnes(gen=g),n)))
        # de + nelder mead combo
        self.new_topology(
          desc='{}, de+nelder mead'.format(desc),
          category=category,
          algorithms=['de','neldermead'],
          archipelago=assign_2nd_alg(Archipelago(constructor(de(gen=g),n)), self.make_nelder_mead()))
        # de + praxis combo
        self.new_topology(
          desc='{}, de+praxis'.format(desc),
          category=category,
          algorithms=['de','praxis'],
          archipelago=assign_2nd_alg(Archipelago(constructor(de(gen=g),n)), self.make_praxis()))
        # de + nsga2 combo
        self.new_topology(
          desc='{}, de+nsga2'.format(desc),
          category=category,
          algorithms=['de','nsga2'],
          archipelago=assign_2nd_alg(Archipelago(constructor(de(gen=g),n)), nsga2(gen=g)))
        # de + de1220 combo
        self.new_topology(
          desc='{}, de+de1220'.format(desc),
          category=category,
          algorithms=['de','de1220'],
          archipelago=assign_2nd_alg(Archipelago(constructor(de(gen=g),n)), de1220(gen=g)))
        # de + sade combo
        self.new_topology(
          desc='{}, de+sade'.format(desc),
          category=category,
          algorithms=['de','sade'],
          archipelago=assign_2nd_alg(Archipelago(constructor(de(gen=g),n)), sade(gen=g)))
        # de + pso combo
        self.new_topology(
          desc='{}, de+pso'.format(desc),
          category=category,
          algorithms=['de','pso'],
          archipelago=assign_2nd_alg(Archipelago(constructor(de(gen=g),n)), pso(gen=g)))


      # extra configurations for fully connected topology
        if constructor is self.factory.createFullyConnected:
            self.new_topology(
                desc='{}, de+pso+praxis'.format(desc),
                category=category,
                algorithms=['de','pso','praxis'],
                archipelago=assign_algs(Archipelago(constructor(de(gen=g),n)), (de(gen=g), pso(gen=g), self.make_praxis())))
            self.new_topology(
                desc='{}, de+pso+praxis+nsga2'.format(desc),
                category=category,
                algorithms=['de','pso','praxis','nsga2'],
                archipelago=assign_algs(Archipelago(constructor(de(gen=g),n)), (de(gen=g), pso(gen=g), self.make_praxis(), nsga2(gen=g))))
            self.new_topology(
                desc='{}, de+pso+praxis+cmaes'.format(desc),
                category=category,
                algorithms=['de','pso','praxis','cmaes'],
                archipelago=assign_algs(Archipelago(constructor(de(gen=g),n)), (de(gen=g), pso(gen=g), self.make_praxis(), cmaes(gen=g))))
            self.new_topology(
                desc='{}, de+pso+praxis+xnes'.format(desc),
                category=category,
                algorithms=['de','pso','praxis','xnes'],
                archipelago=assign_algs(Archipelago(constructor(de(gen=g),n)), (de(gen=g), pso(gen=g), self.make_praxis(), xnes(gen=g))))


    def _generate_all(self, n):
        '''
        Generate a set of benchmark topologies.

        :param n: Number of islands.
        '''
        from math import log

        self.create_variants(n, 'One-way ring', 'rings', self.factory.createOneWayRing)
        self.create_variants(n, 'Bidirectional ring', 'rings', self.factory.createBidirRing)
        self.create_variants(n, 'Bidirectional chain', 'chain', self.factory.createBidirChain)
        if n == 1:
            # remaining topologies are degenerate
            return self.topologies
        self.create_variants(n, 'Rim', 'rings', self.factory.createRim)
        self.create_variants(n, '1-2 Ring', 'rings', self.factory.create_12_Ring)
        self.create_variants(n, '1-2-3 Ring', 'rings', self.factory.create_123_Ring)
        self.create_variants(n, 'Fully Connected', 'clustered', self.factory.createFullyConnected)
        self.create_variants(n, 'Broadcast', 'clustered', self.factory.createBroadcast)
        self.create_variants(round(log(n,2)), 'Hypercube', 'clustered', self.factory.createHypercube) # FIXME: hard-coded
        if n <= 4:
            # remaining topologies need at least 4 islands
            return self.topologies
        self.create_variants(n, 'Watts-Strogatz', 'clustered', partial(self.factory.createWattsStrogatz, k=int(n/4)))
        self.create_variants(n, 'Erdos-Renyi', 'clustered', self.factory.createErdosRenyi)
        self.create_variants(n, 'Barabasi-Albert', 'clustered', partial(self.factory.createBarabasiAlbert, m=int(n/4)))
        self.create_variants(n, 'Extended Barabasi-Albert', 'clustered', partial(self.factory.createExtendedBarabasiAlbert, m=int(n/4)))
        self.create_variants(n, 'Ageing Extended Barabasi-Albert', 'clustered', partial(self.factory.createAgeingExtendedBarabasiAlbert, m=int(n/4)))

        return self.topologies


    def serialize(self):
        from pickle import dumps
        return dumps(self.topologies)


class BiopredynTopologyGenerator(TopologyGenerator):
    '''
    Generates fewer topologies per problem.
    '''
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.name = 'biopredyn'

    def create_variants(self, n, desc, category, constructor):
        def assign_2nd_alg(archipelago, algo):
            if category == 'rings':
                for island in archipelago.topology.every_other_island():
                    island.algorithm = algo
            elif hasattr(archipelago.topology, 'endpoints'):
                for island in archipelago.topology.endpoints:
                    island.algorithm = algo
            elif isinstance(archipelago.topology, FullyConnectedTopology):
                for island in islice(archipelago.topology.islands, None, None, 2):
                    island.algorithm = algo
            return archipelago

        def assign_algs(archipelago, algos):
            '''
            Evenly partitions and assigns algorithms to islands.
            '''
            for island,algo in zip(archipelago.topology.islands, cycle(algos)):
                island.algorithm = algo

        g = self.generations

        self.new_topology(
          desc='{}, de'.format(desc),
          category=category,
          algorithms=['de'],
          archipelago=Archipelago(constructor(de(gen=g),n)))
        self.new_topology(
          desc='{}, de1220'.format(desc),
          category=category,
          algorithms=['de1220'],
          archipelago=Archipelago(constructor(de1220(gen=g),n)))
        self.new_topology(
          desc='{}, sade'.format(desc),
          category=category,
          algorithms=['sade'],
          archipelago=Archipelago(constructor(sade(gen=g),n)))
        self.new_topology(
          desc='{}, bee_colony'.format(desc),
          category=category,
          algorithms=['bee_colony'],
          archipelago=Archipelago(constructor(bee_colony(gen=g),n)))
        # de + nelder mead combo
        self.new_topology(
          desc='{}, de+nelder mead'.format(desc),
          category=category,
          algorithms=['de','neldermead'],
          archipelago=assign_2nd_alg(Archipelago(constructor(de(gen=g),n)), self.make_nelder_mead()))
        # de + praxis combo
        self.new_topology(
          desc='{}, de+praxis'.format(desc),
          category=category,
          algorithms=['de','praxis'],
          archipelago=assign_2nd_alg(Archipelago(constructor(de(gen=g),n)), self.make_praxis()))
        # de + sade combo
        self.new_topology(
          desc='{}, de+sade'.format(desc),
          category=category,
          algorithms=['de','sade'],
          archipelago=assign_2nd_alg(Archipelago(constructor(de(gen=g),n)), sade(gen=g)))


    def _generate_all(self, n):
        '''
        Generate a set of benchmark topologies for biopredyn.

        :param n: Number of islands.
        '''
        from math import log

        if n == 1:
            self.create_variants(n, 'Bidirectional chain', 'chain', self.factory.createBidirChain)
        else:
            self.create_variants(n, 'Rim', 'rings', self.factory.createRim)
            # self.create_variants(round(log(n,2)), 'Hypercube', 'clustered', self.factory.createHypercube)

        return self.topologies
