from __future__ import print_function, division, absolute_import

from uuid import uuid4

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("dumbeddown")
sc = SparkContext(conf=conf)

run_id = str(uuid4())
num_islands = 4

def get_fitness(x):
    from b2problem import B2Problem
    return (B2Problem('b2.xml').evaluate(x),)

def run_island(i):
    class Problem:
        def __init__(self, evaluator, lb, ub):
            # type: (Evaluator, array, array) -> None
            '''
            Inits the problem with an objective evaluator
            (implementing the method evaluate), the parameter
            vector lower bound (a numpy array) and upper bound.
            Both bounds must have the same dimension.
            '''
            #check_vector(lb)
            #check_vector(ub)
            #expect(len(lb) == len(ub), 'Bounds mismatch')
            #self.evaluator = B2Problem('b2.xml')
            self.lb = lb
            self.ub = ub

        def fitness(self, x):
            return get_fitness(x)

        def get_bounds(self):
            return (self.lb,self.ub)

        def get_name(self):
            return 'Sabaody udp'

        def get_extra_info(self):
            return 'Sabaody extra info'
    import pygmo as pg
    from multiprocessing import cpu_count
    from pymemcache.client.base import Client
    mc_client = Client(('luna',11211))

    algorithm = pg.algorithm(pg.de())
    from params import getLowerBound, getUpperBound
    problem = pg.problem(Problem(None,getLowerBound(),getUpperBound()))
    a = pg.archipelago(n=cpu_count(),algo=algorithm, prob=problem, pop_size=100)

    mc_client.set(i.domain_qualifier('island', str(i), 'status'), 'Running', 10000)
    mc_client.set(i.domain_qualifier('island', str(i), 'n_cores'), str(cpu_count()), 10000)

    #a.evolve(100)

    #from roadrunner import RoadRunner

    #r = RoadRunner()

    return 0

island_ids = [str(uuid4()) for x in range(num_islands)]
print(sc.parallelize(island_ids).map(run_island).collect())