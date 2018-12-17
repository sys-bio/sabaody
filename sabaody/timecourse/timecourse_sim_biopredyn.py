# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from numpy import array, maximum, minimum, mean, sqrt, abs, zeros
from typing import SupportsFloat
from builtins import super
import os

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner
from sabaody.utils import expect

from .timecourse_sim_base import TimecourseSimBase, StalledSimulation

class TimecourseSimBiopredyn(TimecourseSimBase):
    ''' Evaluates objective function for aligned timecourses. '''

    def __init__(self, sbml, time_values, measured_quantities, param_ids, scaled_data, scaled_error):
        '''
        Constructor.

        :param measured_quantities: A list of the measured quantities.
        :param scaled_data: The scaled reference data.
        :param scaled_error: The scaled reference error.
        '''
        self.sbml = sbml
        self.r = RoadRunner(sbml)
        self.r.selections = ['time'] + measured_quantities
        self.time_values = time_values
        assert self.time_values[0] == 0.
        self.measured_quantities = measured_quantities
        self.param_list = param_ids
        self.scaled_data = scaled_data
        self.scaled_error = scaled_error

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
            t_now = 0.
            scaled_residuals = zeros((len(self.time_values), len(self.measured_quantities)))
            for it_next in range(1, len(self.time_values)):
                t_now = self.r.simulate(t_now, self.time_values[it_next], 100)
                t_now = self.time_values[it_next]
                if self.divergent():
                    return 1e9*self.penalty_scale
                for iq,q in enumerate(self.measured_quantities):
                    scaled_residuals[it_next-1,iq] = (self.r[q]-self.scaled_data[it_next-1,iq])/self.scaled_error[it_next-1,iq]
            return sqrt(mean(scaled_residuals**2.))
        try:
            with timeout(10, StalledSimulation):
                return worker()
        except (RuntimeError, StalledSimulation):
            # if convergence fails, use a penalty score
            return 1e9*self.penalty_scale
