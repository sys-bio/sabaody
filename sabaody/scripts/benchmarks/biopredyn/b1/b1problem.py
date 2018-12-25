# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.timecourse.timecourse_sim_base import StalledSimulation
from sabaody.timecourse.timecourse_sim_biopredyn import TimecourseSimBiopredyn
from sabaody.scripts.benchmarks.biopredyn.benchsetup import BioPreDynUDP

from numpy import array, mean, sqrt

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner

from typing import SupportsFloat

class B1Problem(TimecourseSimBiopredyn):
    ''' Class that performs a timecourse simulation
    and evaluates the objective function for b1.'''

    def __init__(self, sbml):
        self.sbml = sbml
        self.r = RoadRunner(sbml)
        from data import measured_quantity_ids, exp_data
        self.measured_quantity_ids = measured_quantity_ids
        self.reference_values = exp_data
        from params import param_ids
        self.param_list = param_ids

        self.penalty_scale = 1.


    def evaluate(self, x):
        # type: (array) -> SupportsFloat
        """
        Evaluate and return the objective function.
        """
        from interruptingcow import timeout
        self.reset()
        self.setParameterVector(x)
        self.r.reset()
        def worker():
            # skip the first timepoint
            self.r.simulate(0., 1., 10, self.measured_quantity_ids)
            sim = self.r.simulate(1., 120., 120, self.measured_quantity_ids)
            return sqrt(mean((sim-self.reference_values)**2.))
        try:
            with timeout(10, StalledSimulation):
                return worker()
        except (RuntimeError, StalledSimulation):
            # if convergence fails, use a penalty score
            return 1e9*self.penalty_scale


    def getParameterValue(self,param_index):
        from params import param_index_to_name_map
        try:
            return self.r[param_index_to_name_map[param_index]]
        except KeyError:
            raise KeyError('No such parameter for index {}, must be 0-1758 inclusive'.format(param_index))

    def getCurrentValues_matlab(self):
        # identical to matlab version
        return array([
            self.r.s_0075,
            self.r.s_0180,
            self.r.s_0188,
            self.r.s_0259,
            self.r.s_0260,
            self.r.s_0359,
            self.r.s_0362,
            self.r.s_0394,
            self.r.s_0409,
            self.r.s_0423,
            self.r.s_0434,
            self.r.s_0555,
            self.r.s_0557,
            self.r.s_0563,
            self.r.s_0567,
            self.r.s_0568,
            self.r.s_0586,
            self.r.s_0629,
            self.r.s_0680,
            self.r.s_0765,
            self.r.s_0764,
            self.r.s_0767,
            self.r.s_0785,
            self.r.s_0849,
            self.r.s_0955,
            self.r.s_0991,
            self.r.s_1003,
            self.r.s_1039,
            self.r.s_1045,
            self.r.s_1198,
            self.r.s_1203,
            self.r.s_1360,
            self.r.s_1399,
            self.r.s_1520,
            self.r.s_1538,
            self.r.s_1543,
            self.r.s_1559,
            self.r.s_1565,
            self.getParameterValue(1613) * (self.r.s_0565 - self.r.s_0563) / self.getParameterValue(1614) / (1 + self.r.s_0565 / self.getParameterValue(1614) + 1 + self.r.s_0563 / self.getParameterValue(1615) - 1),
            self.getParameterValue(1628) * self.r.s_0456 / self.getParameterValue(1629) / (1 + self.r.s_0456 / self.getParameterValue(1629)),
            self.getParameterValue(1642) * self.r.s_0680 / self.getParameterValue(1643) / (1 + self.r.s_0680 / self.getParameterValue(1643)),
            self.getParameterValue(1608) * self.r.s_0362 / self.getParameterValue(1609) / (1 + self.r.s_0362 / self.getParameterValue(1609)),
            self.getParameterValue(1616) * self.r.s_0765 / self.getParameterValue(1617) / (1 + self.r.s_0765 / self.getParameterValue(1617)),
            self.getParameterValue(1657) * self.r.s_1520 / self.getParameterValue(1658) / (1 + self.r.s_1520 / self.getParameterValue(1658)),
            ])

    def getCurrentValues(self):
        return array([
            self.r.s_0075,
            self.r.s_0180,
            self.r.s_0188,
            self.r.s_0259,
            self.r.s_0260,
            self.r.s_0359,
            self.r.s_0362,
            self.r.s_0394,
            self.r.s_0409,
            self.r.s_0423,
            self.r.s_0434,
            self.r.s_0555,
            self.r.s_0557,
            self.r.s_0563,
            self.r.s_0567,
            self.r.s_0568,
            self.r.s_0586,
            self.r.s_0629,
            self.r.s_0680,
            self.r.s_0765,
            self.r.s_0764,
            self.r.s_0767,
            self.r.s_0785,
            self.r.s_0849,
            self.r.s_0955,
            self.r.s_0991,
            self.r.s_1003,
            self.r.s_1039,
            self.r.s_1045,
            self.r.s_1198,
            self.r.s_1203,
            self.r.s_1360,
            self.r.s_1399,
            self.r.s_1520,
            self.r.s_1538,
            self.r.s_1543,
            self.r.s_1559,
            self.r.s_1565,
            # reactions
            self.r.r_1166,
            self.r.r_1697,
            self.r.r_1762,
            self.r.r_1106,
            self.r.r_1172,
            self.r.r_2079,
            ])


class B4_UDP(BioPreDynUDP):
    def __init__(self, lb, ub, sbml_file='b4.xml'):
        super().__init__(lb=lb, ub=ub, sbml_file=sbml_file)

    def fitness(self, x):
        if self.evaluator is None:
            from b1problem import B1Problem
            self.evaluator = B1Problem(self.sbml_file)
        return (self.evaluator.evaluate(x),)
