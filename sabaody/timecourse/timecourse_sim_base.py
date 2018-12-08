from __future__ import print_function, division, absolute_import

from collections import OrderedDict
from numpy import array, hstack, argwhere, unique, maximum, minimum
from typing import SupportsFloat
from builtins import super
import os

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner
from sabaody.utils import expect

from sabaody.pygmo_interf import Evaluator

#raise RuntimeError('improt tc')

class StalledSimulation(RuntimeError):
    pass

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

class TimecourseSimBase(Evaluator):
    ''' Base class for timecourse simulations.'''

    def plotQuantity(self, identifier, bars=True):
        ''' Plot a simulated quantity vs its data points using Tellurium.
        The residuals should already be calculated.'''
        data = self.measurement_map[identifier]
        # data contains one column of time and one column of values
        import tellurium as te
        te.plot(data[:,0], data[:,1], scatter=True, name=identifier+' data', show=False, error_y_pos=maximum(array(self.quantity_residuals[identifier]),0), error_y_neg=-minimum(array(self.quantity_residuals[identifier]),0))
        # simulate and plot the model
        r = RoadRunner(self.sbml)
        s = r.simulate(0,self.timepoints[-1],1000,['time',identifier])
        te.plot(s[:,0], s[:,1], name=identifier+' sim')


    def RMSE_quantity(self, identifier):
        ''' Calc the RMSE of a quantity.'''
        from math import sqrt
        return sqrt(float((array(self.quantity_residuals[identifier])**2).mean()))


    def MSE(self):
        ''' Calc the MSE for all residuals.
        Call this after calculating all residuals.'''
        r = array(self.residuals)
        return (r**2).mean()


    def RMSE(self):
        ''' Calc the RMSE for all residuals.
        Call this after calculating all residuals.'''
        from math import sqrt
        r = sqrt(float(array(self.residuals)))
        return (r**2).mean()


    def reset(self):
        self.r.resetAll()


    def _setParameterVector(self, x, param_list, exponential=True):
        # type: (array, List) -> None
        expect(len(x) == len(param_list), 'Wrong length for parameter vector - expected {} but got {}'.format(len(param_list), len(x)))
        if exponential:
            from math import exp
            for i,v in enumerate(x):
                self.r[param_list[i]] = exp(v)
        else:
            for i,v in enumerate(x):
                self.r[param_list[i]] = v


    def _getParametersDict(self, param_list, use_log=True):
        # type: (List, bool) -> Dict
        '''
        Returns the current values of the parameters as a dictionary.
        '''
        expect(len(x) == len(param_list), 'Wrong length for parameter vector - expected {} but got {}'.format(len(param_list), len(x)))
        result = {}
        if use_log:
            from math import log
            for p in param_list:
                result[p] = log(self.r[p])
        else:
            for p in param_list:
                result[p] = self.r[p]


    def divergent(self):
        '''
        Check whether the simulation has diverged (+-infinity).
        '''
        from sabaody.utils import divergent
        reaction_rates = self.r.getReactionRates()
        if divergent(reaction_rates):
            return true


    def setParameterVector(self, x):
        '''
        Set the entire parameter vector (x can be a 1d array).
        '''
        # type: (ndarray) -> None
        self._setParameterVector(x, self.param_list)


    def getParametersDict(self):
        '''
        Get the parameter names and current values as a dictionary.
        '''
        # type: () -> Dict
        return self._getParametersDict(x, self.param_list, use_log=True)


    def getParameterNames(self):
        '''
        Get the parameter names (SBML ids).
        '''
        return self.param_list
