from __future__ import print_function, division, absolute_import

from uuid import uuid4

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("b2-nofork2")
sc = SparkContext(conf=conf)

run_id = str(uuid4())
num_islands = 4

def get_fitness(x):
    from b2problem import B2Problem
    return (B2Problem('b2.xml').evaluate(x),)

def run_island(id):
    class B2_UDP:
        def __init__(self, lb, ub):
            # type: (Evaluator, array, array) -> None
            '''
            Inits the problem with an objective evaluator
            (implementing the method evaluate), the parameter
            vector lower bound (a numpy array) and upper bound.
            Both bounds must have the same dimension.
            '''
            from sabaody.utils import check_vector, expect
            check_vector(lb)
            check_vector(ub)
            expect(len(lb) == len(ub), 'Bounds mismatch')
            self.lb = lb
            self.ub = ub
            from b2problem import B2Problem
            self.evaluator = B2Problem('b2.xml')

        def fitness(self, x):
            return (self.evaluator.evaluate(x),)

        def get_bounds(self):
            return (self.lb,self.ub)

        def get_name(self):
            return 'Sabaody udp'

        def get_extra_info(self):
            return 'Sabaody extra info'

        def __getstate__(self):
            return {
              'lb': self.lb,
              'ub': self.ub}

        def __setstate__(self, state):
            self.lb = state['lb']
            self.ub = state['ub']
            from b2problem import B2Problem
            self.evaluator = B2Problem('b2.xml')

    import pygmo as pg
    from pymemcache.client.base import Client
    mc_client = Client(('luna',11211))

    algorithm = pg.algorithm(pg.de(gen=1000))
    from params import getLowerBound, getUpperBound
    problem = pg.problem(B2_UDP(getLowerBound(),getUpperBound()))
    i = pg.island(algo=algorithm, prob=problem, size=20)

    #mc_client.set(id.domain_qualifier('island', str(id), 'status'), 'Running', 10000)

    i.evolve()
    i.wait()

    import socket
    hostname = socket.gethostname()
    ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    return (ip, hostname)

island_ids = [str(uuid4()) for x in range(num_islands)]
print(sc.parallelize(island_ids, numSlices=4).map(run_island).collect())