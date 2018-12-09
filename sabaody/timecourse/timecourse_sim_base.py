# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

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

class StalledSimulation(RuntimeError):
    pass

class TimecourseSimBase(Evaluator):
    ''' Base class for timecourse simulations.'''


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


    def _setParameterVector(self, x, param_list, rr_instance, exponential=True):
        # type: (array, List) -> None
        expect(len(x) == len(param_list), 'Wrong length for parameter vector - expected {} but got {}'.format(len(param_list), len(x)))
        if exponential:
            from math import exp
            for i,v in enumerate(x):
                rr_instance[param_list[i]] = exp(v)
        else:
            for i,v in enumerate(x):
                rr_instance[param_list[i]] = v


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
        self._setParameterVector(x, self.param_list, self.r)


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
