from __future__ import print_function, division, absolute_import

from sabaody.timecourse_model import TimecourseModel

try:
    from params import param_list, getUpperBound, getLowerBound
    from data import *
except ImportError:
    from .params import param_list, getUpperBound, getLowerBound
    from .data import *

class B2Problem(TimecourseModel):
    ''' Class that performs a timecourse simulation
    and calculates the residuals for b4.'''

    def __init__(self, sbml):
        super().__init__(sbml, data_quantities, {
          'cpep': PEP,
          'cg6p': G6P,
          'cpyr': PYR,
          'cf6p': F6P,
          'cglcex': GLCex,
          'cg1p': G1P,
          'cpg': x6PG,
          'cfdp': FDP,
        })

    def setParameterVector(self, x):
        # type: (array) -> None
        super().setParameterVector(x, param_list)

class b2_ctor_class():
    def __init__(self, prob_class, model_class, lb, ub):
        self.prob_class = prob_class
        self.model_class = model_class
        self.lb = lb
        self.ub = ub

    def __call__(self):
        import pygmo as pg
        return pg.problem(self.prob_class(self.model_class, self.lb, self.ub))

#def b2_constructor():
    #import pygmo as pg
    #return pg.problem(Problem(B2Problem('b2.xml'), getLowerBound(), getUpperBound()))

def problem_constructor2(n):
    import pygmo as pg
    return pg.rosenbrock(n)

def make_problem():
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
    return pg.problem(B2_UDP(getLowerBound(),getUpperBound()))