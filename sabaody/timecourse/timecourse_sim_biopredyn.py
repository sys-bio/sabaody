# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from numpy import array, maximum, minimum, mean, sqrt, abs
from typing import SupportsFloat
from builtins import super
import os

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner
from sabaody.utils import expect

from .timecourse_sim_aligned import TimecourseSimAligned, StalledSimulation

class TimecourseSimBiopredyn(TimecourseSimAligned):
    ''' Evaluates objective function for aligned timecourses. '''

    def __init__(self, sbml, measured_quantities, scaled_data, scaled_error):
        '''
        Constructor.

        :param measured_quantities: A list of the measured quantities.
        :param scaled_data: The scaled reference data.
        :param scaled_error: The scaled reference error.
        '''
        self.sbml = sbml
        self.r = RoadRunner(sbml)
        self.r.selections = ['time'] + measured_quantities
        self.measured_quantities = measured_quantities
        self.param_list = param_list
        self.setParameterVector(reference_param_values)

        sim = self.r.simulate(time_start, time_end, n)
        self.reference_time = array(sim[:,0])
        self.reference_quantities = array(sim[:,1:])
        self.reference_quantity_means_squared = mean(self.reference_quantities, axis=0)**2
        # print(self.reference_quantity_means_squared)

        self.penalty_scale = 1.


    def evaluate(self, x):
        # type: (array) -> SupportsFloat
        """
        Evaluate and return the objective function.
        """
        from interruptingcow import timeout
        self.reset()
        self.setParameterVector(x)
        def worker():
            values = self.r.simulate(self.time_start, self.time_end, self.n)
            residuals = array(values[:,1:] - self.reference_quantities)
            # residuals *= 100.
            # print('residuals:')
            # print(residuals)
            # print(array(residuals**2))
            quantity_mse = mean(residuals**2,axis=0)/self.reference_quantity_means_squared
            # print('quantity_mse')
            # print(quantity_mse)
            return sqrt(mean(quantity_mse))
        if self.divergent():
            return 1e9*self.penalty_scale
        try:
            with timeout(10, StalledSimulation):
                return worker()
        except (RuntimeError, StalledSimulation):
            # if convergence fails, use a penalty score
            return 1e9*self.penalty_scale
