# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.timecourse.timecourse_sim_validate import TimecourseSimValidate
from sabaody.scripts.benchmarks.biopredyn.benchsetup import BioPreDynUDP

from params import param_list, getBestKnownValues

class B2ProblemValidator(TimecourseSimValidate):
    ''' Class that performs a timecourse simulation
    and calculates the residuals for b4.'''

    def __init__(self, sbml, n):
        self.param_list = param_list
        super().__init__(
            sbml,
            measured_quantities = ['cpep', 'cg6p', 'cpyr', 'cf6p', 'cglcex', 'cg1p', 'cpg', 'cfdp', 'cgap'],
            param_list = param_list,
            reference_param_values = getBestKnownValues(),
            time_start = 0.,
            time_end = 300.,
            n = n,
        )

class B2Validator_UDP(BioPreDynUDP):
    def __init__(self, lb, ub, sbml_file='b2.xml', n=100):
        super().__init__(lb=lb, ub=ub, sbml_file=sbml_file)
        self.n = n


    def __getstate__(self):
        s = super().__getstate__()
        s.update({'n': self.n})
        return s


    def __setstate__(self, state):
        super().__setstate__(state)
        self.n = state['n']

    def fitness(self, x):
        if self.evaluator is None:
            from b2problem_validator import B2ProblemValidator
            self.evaluator = B2ProblemValidator(self.sbml_file, self.n)
        return (self.evaluator.evaluate(x),)
