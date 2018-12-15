# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from numpy import array, maximum, minimum, mean, sqrt, abs
from typing import SupportsFloat
from builtins import super
import os

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner
from sabaody.utils import expect

from .timecourse_sim_base import TimecourseSimAligned, StalledSimulation

class TimecourseSimValidate(TimecourseSimAligned):
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
        self.measured_quantities = measured_quantities
        self.param_list = param_list
        self.setParameterVector(reference_param_values)

        sim = self.r.simulate(time_start, time_end, n)
        self.reference_time = array(sim[:,0])
        self.reference_quantities = array(sim[:,1:])
        self.reference_quantity_means_squared = mean(self.reference_quantities, axis=0)**2
        # print(self.reference_quantity_means_squared)

        self.penalty_scale = 1.


    def plotQuantity(self, identifier, param_values, n, bars=True):
        ''' Plot a simulated quantity vs its data points using Tellurium.'''
        i = self.measured_quantities.index(identifier)
        reference_quantity = self.reference_quantities[:,i]

        r = RoadRunner(self.sbml)
        if param_values is not None:
            self._setParameterVector(param_values, self.param_list, r)
        s = r.simulate(0,float(self.reference_time[-1]),n,['time',identifier])
        simulated_quantity = s[:,1]
        residuals = simulated_quantity - reference_quantity
        # relative residuals
        # print('avg relative deviation for ', identifier, ': {:.1f}'.format(mean(abs(residuals/reference_quantity))*100.), '%')
        # residuals normalized to overall mean
        print('avg relative deviation for ', identifier, ': {:.1f}'.format(mean(abs(residuals))/mean(abs(reference_quantity))*100.), '%')
        r.reset()
        s = r.simulate(0,float(self.reference_time[-1]),1000,['time',identifier])

        import tellurium as te
        te.plot(self.reference_time, reference_quantity, scatter=True,
            name=identifier+' data', show=False,
            error_y_pos=maximum(residuals,0),
            error_y_neg=-minimum(residuals,0))
        te.plot(s[:,0], s[:,1], name=identifier+' sim')
