from __future__ import print_function, division, absolute_import

from sabaody import TimecourseModel

from params import param_list
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