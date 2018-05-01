from __future__ import print_function, division, absolute_import

from collections import OrderedDict
from numpy import array, hstack, argwhere, unique
from typing import SupportsFloat
from builtins import super

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner
from sabaody.utils import expect

from .pygmo_interf import Evaluator

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

class TimecourseModel(Evaluator):
    ''' Class that performs a timecourse simulation
    and calculates the residuals for b4.'''

    def __init__(self, model_path, data_quantities, measurement_map):
        '''
        Constructor.

        :param measurement_map: A dictionary that maps the names of quantities to measurements to their respective (numpy) arrays.
        '''
        self.r = RoadRunner(model_path)
        self.residuals = []
        #print(self.r.getFloatingSpeciesIds())

        self.timepoints = unique(hstack(a[:,0] for a in data_quantities))
        self.reset()

        self.measurement_map = measurement_map

        # keep track of the number of times a measurement is used
        # (check correct number of residuals)
        self.measurement_count = OrderedDict((quantity,0) for quantity in self.measurement_map)

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
            self.residuals.append(predicted_value - valueAtTime(a,t))
            # increment the residual use count (check all measurements are used exactly once)
            self.measurement_count[identifier] += 1
            self.usage_map[identifier] = True
        except MissingValue:
            # no measurement at this timepoint, do nothing
            return

    def MSE(self):
        ''' Calc the MSE for all residuals.
        Call this after calculating all residuals.'''
        r = array(self.residuals)
        return (r**2).mean()

    def simulateToNextTime(self):
        t_begin = self.t
        t_end = self.timepoints[self.next_ti]
        delta = t_end-t_begin
        stepsize = 0.05
        steps = int(max(100,delta/stepsize))
        self.r.simulate(0,delta,steps)
        return t_end

    def reset(self):
        self.r.resetAll()
        self.t = self.timepoints[0]
        # next time index
        self.next_ti = 0

    def buildResidualList(self):
        while self.next_ti < self.timepoints.shape[0]:
            self.t = self.simulateToNextTime()
            self.calcResiduals(self.t)
            self.next_ti += 1

    def setParameterVector(self, x):
        # type: (array) -> None
        from params import param_list
        expect(len(x) == len(param_list), 'Wrong length for parameter vector - expected {} but got {}'.format(len(param_list), len(x)))
        for i,v in enumerate(x):
            self.r[param_list[i]] = v

    def evaluate(self, x):
        # type: (array) -> SupportsFloat
        """
        Evaluate and return the objective function.
        """
        self.reset()
        self.setParameterVector(x)
        self.buildResidualList()
        return self.MSE()

    def printDatapointUsage(self):
        ''' For debugging. Make sure every data point is
        used.'''
        total = 0
        total_used = 0
        for q in self.measurement_count:
            a = self.measurement_map[q]
            used = self.measurement_count[q]
            n = a.shape[0]
            print('Usage for {}: {}/{}'.format(q,used,n))
            total+=n
            total_used+=used
        print('*** Total usage: {}/{} ({:.1f}%)'.format(total_used,total,100.*total_used/total))