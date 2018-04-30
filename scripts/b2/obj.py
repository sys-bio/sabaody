from __future__ import print_function, division, absolute_import

from numpy import array
from typing import SupportsFloat
from sabaody.utils import expect

import tellurium as te
from roadrunner import RoadRunner
from sabaody import Evaluator

from data import *

class MissingValue(Exception):
    pass

def valueAtTime(a,t):
    ''' Find a value in a matching the measurement time t. '''
    try:
        return float(a[np.argwhere(a[:,0] == t)[0],1])
    except IndexError:
        raise MissingValue
    except TypeError:
        print(np.argwhere(a[:,0] == t))
        raise MissingValue

class B2Model(Evaluator):
    ''' Class that performs a timecourse simulation
    and calculates the residuals for b4.'''

    def __init__(self):
        self.r = RoadRunner('./b2.xml')
        self.residuals = []
        print(self.r.getFloatingSpeciesIds())

        self.timepoints = np.unique(np.hstack(a[:,0] for a in data_quantities))
        self.reset()

        self.measurement_map = {
          'PEP': PEP,
          'G6P': G6P,
          'PYR': PYR,
          'F6P': F6P,
          'GLCex': GLCex,
          'G1P': G1P,
          '6PG': x6PG,
          'FDP': FDP,
        }

        # keep track of the number of times a measurement is used
        # (check correct number of residuals)
        self.measurement_count = dict((quantity,0) for quantity in self.measurement_map)

    def calcResiduals(self,t):
        ''' Try to calculate residuals at the current time t
        and add them to self.residuals.
        If they do not exist for certain datasets at time t,
        just pass over the dataset.'''
        self.usage_map = dict((q,False) for q in self.measurement_map)
        self.tryAddResidual(t, self.r.cpep, 'PEP')
        self.tryAddResidual(t, self.r.cg6p, 'G6P')
        self.tryAddResidual(t, self.r.cpyr, 'PYR')
        self.tryAddResidual(t, self.r.cf6p, 'F6P')
        self.tryAddResidual(t, self.r.cglcex, 'GLCex')
        self.tryAddResidual(t, self.r.cg1p, 'G1P')
        self.tryAddResidual(t, self.r.cpg, '6PG')
        self.tryAddResidual(t, self.r.cfdp, 'FDP')

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

#b2 = B2Model()
#print(b2.timepoints)
#print(b2.timepoints.shape[0])
#b2.buildResidualList()
#b2.printDatapointUsage()