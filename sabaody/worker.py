def run_island(i):
    class Problem:
        def __init__(self, evaluator, lb, ub):
            from .utils import expect, check_vector
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

    import pygmo as pg
    from multiprocessing import cpu_count
    from b2problem import B2Problem
    from params import getDefaultParamValues, getLowerBound, getUpperBound
    from pymemcache.client.base import Client
    mc_client = Client((i.mc_host,i.mc_port))
    #udp = i.problem_factory()

    algorithm = pg.algorithm(pg.de())
    problem = pg.problem(Problem(B2Problem(i.problem_factory), getLowerBound(), getUpperBound()))
    # TODO: configure pop size
    #a = pg.archipelago(n=cpu_count,algo=algorithm, prob=problem, pop_size=100)

    mc_client.set(i.domain_qualifier('island', str(i.id), 'status'), 'Running', 10000)
    mc_client.set(i.domain_qualifier('island', str(i.id), 'n_cores'), str(cpu_count()), 10000)
    print('Starting island {} with {} cpus'.format(str(i.id), str(cpu_count())))

    #a.evolve(100)

    return 0