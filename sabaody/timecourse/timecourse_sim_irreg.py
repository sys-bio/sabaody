# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from collections import OrderedDict
from numpy import array, hstack, argwhere, unique, maximum, minimum, mean, sqrt
from typing import SupportsFloat
from builtins import super
import os

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner
from sabaody.utils import expect

from .timecourse_sim_base import TimecourseSimBase, StalledSimulation

class MissingValue(Exception):
    pass

def valueAtTime(a,t):
    ''' Find a value in a matching the measurement time t. '''
    try:
        return float(a[argwhere(a[:,0] == t)[0],1])
    except IndexError:
        raise MissingValue
    except TypeError:
        print(argwhere(a[:,0] == t))
        raise MissingValue

class TimecourseSimIrreg(TimecourseSimBase):
    ''' Performs a timecourse simulation on an irregular grid.'''

    def __init__(self, sbml, data_quantities, measurement_map):
        '''
        Constructor.

        :param measurement_map: A dictionary that maps the names of quantities to measurements to their respective (numpy) arrays.
        '''
        self.sbml = sbml
        self.r = RoadRunner(sbml)
        # self.r.integrator.stiff = False
        # self.r.integrator.minimum_time_step = 0.0001
        # self.r.integrator.maximum_time_step = 1.
        # self.residuals = []
        #print(self.r.getFloatingSpeciesIds())

        self.timepoints = unique(hstack(a[:,0] for a in data_quantities))
        self.reset()

        self.measurement_map = measurement_map
        # map a quantity to its mean measured value
        self.mean_measurement_map = {quantity: mean(values[:,1]) for quantity,values in self.measurement_map.items()}

        # keep track of the number of times a measurement is used
        # (check correct number of residuals)
        self.measurement_count = OrderedDict((quantity,0) for quantity in self.measurement_map)
        self.penalty_scale = 1.


    def plotQuantity(self, identifier, param_values, bars=True):
        ''' Plot a simulated quantity vs its data points using Tellurium.
        The residuals should already be calculated.'''
        data = self.measurement_map[identifier]
        # data contains one column of time and one column of values
        import tellurium as te
        te.plot(data[:,0], data[:,1], scatter=True, name=identifier+' data', show=False, error_y_pos=maximum(array(self.quantity_residuals[identifier]),0), error_y_neg=-minimum(array(self.quantity_residuals[identifier]),0))
        # simulate and plot the model
        r = RoadRunner(self.sbml)
        if param_values is not None:
            self._setParameterVector(param_values, self.param_list, r)
        s = r.simulate(0,self.timepoints[-1],1000,['time',identifier])
        te.plot(s[:,0], s[:,1], name=identifier+' sim')


    def calcResiduals(self,t):
        ''' Try to calculate residuals at the current time t
        and add them to self.residuals.
        If they do not exist for certain datasets at time t,
        just pass over the dataset.'''
        self.usage_map = dict((q,False) for q in self.measurement_map)
        for quantity in self.measurement_map.keys():
            self.tryAddResidual(t, self.r[quantity], quantity)

    def tryAddResidual(self,t,predicted_value,identifier):
        ''' Append a residual to the list of residuals.
            Call with a single value from a simulation and pass
            array of measurements for that quantity.
            If there is no measurement at this time point (t), do nothing.'''
        a = self.measurement_map[identifier]
        try:
            # if there is a measurement a this timepoint, append to list
            r = predicted_value - valueAtTime(a,t)
            # self.residuals.append(r)
            self.quantity_residuals[identifier].append(r)
            # increment the residual use count (check all measurements are used exactly once)
            self.measurement_count[identifier] += 1
            self.usage_map[identifier] = True
        except MissingValue:
            # no measurement at this timepoint, do nothing
            return

    def simulateToNextTime(self):
        t_begin = self.t
        t_end = self.timepoints[self.next_ti]
        delta = t_end-t_begin
        stepsize = 0.1
        steps = int(max(100,delta/stepsize))
        self.r.simulate(t_begin,t_end,steps)
        return t_end

    def reset(self):
        self.r.resetAll()
        self.t = self.timepoints[0]
        # next time index
        self.next_ti = 0


    def buildResidualList(self):
        # simulate to the first timepoint (not necessarily zero)
        delta = self.timepoints[0]
        stepsize = 0.1
        steps = int(max(100,delta/stepsize))
        self.r.simulate(0,delta,steps)
        if self.divergent():
            raise RuntimeError('Diverged at first time step')
        self.next_ti = 1
        if len(self.timepoints) < 2:
            raise RuntimeError('Expected at least two timepoints')
        # calculate the residuals
        self.calcResiduals(self.t)
        # simulate to the rest of the timepoints
        while self.next_ti < self.timepoints.shape[0]:
            self.t = self.simulateToNextTime()
            if self.divergent():
                raise RuntimeError('Diverged at time step {}'.format(self.next_ti))
            self.calcResiduals(self.t)
            self.next_ti += 1


    def evaluate(self, x):
        # type: (array) -> SupportsFloat
        """
        Evaluate and return the objective function.
        """
        from interruptingcow import timeout
        self.reset()
        self.setParameterVector(x)
        self.quantity_residuals = dict((quantity,list()) for quantity in self.measurement_map)
        def worker():
            self.buildResidualList()
        if self.divergent():
            return 1e9*self.penalty_scale
        try:
            with timeout(10, StalledSimulation):
                worker()
        except (RuntimeError, StalledSimulation):
            # if convergence fails, use a penalty score
            return 1e9*self.penalty_scale
        print('evaluate')
        # for quantity,residuals in self.quantity_residuals.items():
            # print(quantity,mean(array(residuals)**2.),self.mean_measurement_map[quantity])
        return sqrt(mean(array([
            mean(array(residuals)**2.)/self.mean_measurement_map[quantity]**2. \
            for quantity,residuals in self.quantity_residuals.items() \
            ])))


    def getUsageByQuantity(self):
        '''
        Calculates the number of times a given quantity is used.
        Should be equal to the number of datap oints for that quantity
        if all goes well.
        '''
        total = 0
        total_used = 0
        usage_for_quantity = OrderedDict()

        for q in self.measurement_count:
            a = self.measurement_map[q]
            used = self.measurement_count[q]
            usage_for_quantity[q] = used
            n = a.shape[0]
            total+=n
            total_used+=used

        return (total,total_used,usage_for_quantity)


    def printDatapointUsage(self):
        ''' For debugging. Make sure every data point is
        used.'''
        total,total_used,usage_for_quantity = self.getUsageByQuantity()
        for q,used in usage_for_quantity.keys():
            a = self.measurement_map[q]
            n = a.shape[0]
            print('Usage for {}: {}/{}'.format(q,used,n))
        print('*** Total usage: {}/{} ({:.1f}%)'.format(total_used,total,100.*total_used/total))


    def RMSE_quantity(self, identifier):
        ''' Calc the RMSE of a quantity.'''
        from math import sqrt
        return sqrt(float((array(self.quantity_residuals[identifier])**2).mean()))/self.mean_measurement_map[identifier]
