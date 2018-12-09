# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from numpy import array
from typing import SupportsFloat
from builtins import super
import os

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner
from sabaody.utils import expect

from .timecourse_sim_base import TimecourseSimBase, StalledSimulation

class TimecourseSimValidate(TimecourseSimBase):
    ''' Validates convergence to a given set of parameters.
    Generates datapoints on a grid for measured_quantities.'''

    def __init__(self, sbml, measured_quantities, param_list, reference_param_values, time_start, time_end, n):
        '''
        Constructor.

        :param measured_quantities: A list of the measured quantities.
        :param reference_param_values: The vector of parameter values in the reference state.
        :param time_start: Start time of the simulation.
        :param time_end: End time of the simulation.
        :param n: Number of intervals/points in simulation.
        '''
        self.sbml = sbml
        self.r = RoadRunner(sbml)
        self.time_start = time_start
        self.time_end = time_end
        self.n = n
        self.r.selections = ['time'] + measured_quantities
        self.param_list = param_list
        self.setParameterVector(reference_param_values)
        self.reference_quantities = array(self.r.simulate(time_start, time_end, n)[:,1:])


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
            residuals = values[:,1:] - self.reference_quantities
            return (residuals**2).mean()
        if self.divergent():
            return 1e9*self.penalty_scale
        try:
            with timeout(10, StalledSimulation):
                return worker()
        except (RuntimeError, StalledSimulation):
            # if convergence fails, use a penalty score
            return 1e9*self.penalty_scale
