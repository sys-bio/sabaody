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
          'cgap': GAP,
        })

    def setParameterVector(self, x):
        # type: (ndarray) -> None
        super().setParameterVector(x, param_list)

    def getParameterNames(self):
        return param_list

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
        # delay loading until we're on the worker node
        self.evaluator = None

    def fitness(self, x):
        if self.evaluator is None:
            from b2problem import B2Problem
            self.evaluator = B2Problem('b2.xml')
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
        self.evaluator = None