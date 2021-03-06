# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.timecourse.timecourse_sim_irreg import TimecourseSimIrreg
from sabaody.scripts.benchmarks.biopredyn.launcher import BioPreDynUDP

from params import param_list, getUpperBound, getLowerBound
from data import *

class B2Problem(TimecourseSimIrreg):
    ''' Class that performs a timecourse simulation
    and calculates the residuals for b2.'''

    def __init__(self, sbml):
        self.param_list = param_list
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

class B2_UDP(BioPreDynUDP):
    def __init__(self, lb, ub, sbml_file='b2.xml'):
        super().__init__(lb=lb, ub=ub, sbml_file=sbml_file)

    def fitness(self, x):
        if self.evaluator is None:
            from b2problem import B2Problem
            self.evaluator = B2Problem(self.sbml_file)
        return (self.evaluator.evaluate(x),)
