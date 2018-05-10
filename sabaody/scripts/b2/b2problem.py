from __future__ import print_function, division, absolute_import

from sabaody import TimecourseModel, Problem

from params import param_list, getUpperBound, getLowerBound
from data import *

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

def b2_constructor():
    import pygmo as pg
    return pg.problem(Problem(B2Problem('b2.xml'), getLowerBound(), getUpperBound()))

def problem_constructor2(n):
    import pygmo as pg
    return pg.rosenbrock(n)