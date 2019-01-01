# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.timecourse.timecourse_sim_base import StalledSimulation
from sabaody.timecourse.timecourse_sim_biopredyn import TimecourseSimBiopredyn
from sabaody.scripts.benchmarks.biopredyn.benchsetup import BioPreDynUDP

from numpy import array, mean, sqrt, maximum, minimum, vstack

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner

from os.path import join, dirname, realpath
from typing import SupportsFloat

class B5Problem(TimecourseSimBiopredyn):
    ''' Class that performs a timecourse simulation
    and evaluates the objective function for b1.'''

    def __init__(self, sbml):
        self.sbml = sbml
        self.r = RoadRunner(sbml)
        from observables import observables
        self.measured_quantity_ids = observables
        from json import load
        with open(join(dirname(realpath(__file__)), 'exp_data.json')) as f:
            self.reference_value_collection = [array(a) for a in load(f)]
            self.reference_value_means_squared_collection = []
            for a in self.reference_value_collection:
                self.reference_value_means_squared_collection.append(mean(a, axis=0)**2)
        with open(join(dirname(realpath(__file__)), 'exp_y0.json')) as f:
            self.exp_y0_collection = [array(a) for a in load(f)]
        with open(join(dirname(realpath(__file__)), 'stimuli.json')) as f:
            self.stimuli_collection = [d for d in load(f)]
        from parameters import param_ids
        self.param_list = param_ids

        self.penalty_scale = 1.


    def setExperimentNumber(self, n):
        '''
        Villaverde et al. use a set of 10 different experiments with respective
        different stimuli combinations and expected results.
        This method initialized appropriate variables for the given experiment.
        '''
        self.reference_values = self.reference_value_collection[n]
        self.reference_value_means_squared = self.reference_value_means_squared_collection[n]
        self.exp_y0 = self.exp_y0_collection[n]
        from species import species
        for k,s in enumerate(species):
            self.r.setValue('init({})'.format(s), float(self.exp_y0[k]))
        self.stimuli = self.stimuli_collection[n]
        print(self.stimuli)
        for s,b in self.stimuli.items():
            self.r[s] = b*1.


    def evaluate(self, x):
        # type: (array) -> SupportsFloat
        """
        Evaluate and return the objective function.
        """
        from interruptingcow import timeout
        for n in range(10):
            self.setExperimentNumber(n)
            self.reset()
            self.setParameterVector(x)
            self.r.reset()
            def worker():
                sim = self.r.simulate(0., 30., 16, self.measured_quantity_ids)
                residuals = sim-self.reference_values
                normalized_mse_per_quantity = mean(residuals**2,axis=0)/self.reference_value_means_squared
                return sqrt(mean(normalized_mse_per_quantity))
            try:
                with timeout(10, StalledSimulation):
                    return worker()
            except (RuntimeError, StalledSimulation):
                # if convergence fails, use a penalty score
                return 1e9*self.penalty_scale


    def plotQuantity(self, quantity_id, param_values, exp_number):
        ''' Plot a simulated quantity vs its data points using Tellurium.'''
        self.setExperimentNumber(exp_number)
        iq = self.measured_quantity_ids.index(quantity_id)
        reference_data = array(self.reference_values[:,iq])

        r = RoadRunner(self.sbml)
        r.reset()
        r.resetAll()
        r.resetToOrigin()
        self._setParameterVector(param_values, self.param_list, r)
        sim = r.simulate(0., 30., 16, ['time', quantity_id])
        assert sim.shape[0] == reference_data.shape[0]
        residuals = sim[:,1] - reference_data

        r.reset()
        r.resetAll()
        r.resetToOrigin()
        self._setParameterVector(param_values, self.param_list, r)
        # self._setParameterVector(param_values, self.param_list, r)
        s = r.simulate(0,30.,1000,['time',quantity_id])

        import tellurium as te
        te.plot(sim[:,0], reference_data, scatter=True,
            name=quantity_id+' data', show=False,
            title=quantity_id,
            error_y_pos=maximum(residuals,0),
            error_y_neg=-minimum(residuals,0))
        te.plot(s[:,0], s[:,1], name=quantity_id+' sim')


    def getParameterValue(self,param_index):
        from params import param_index_to_name_map
        try:
            return self.r[param_index_to_name_map[param_index]]
        except KeyError:
            raise KeyError('No such parameter for index {}, must be 0-1758 inclusive'.format(param_index))


class B4_UDP(BioPreDynUDP):
    def __init__(self, lb, ub, sbml_file='b4.xml'):
        super().__init__(lb=lb, ub=ub, sbml_file=sbml_file)

    def fitness(self, x):
        if self.evaluator is None:
            from b1problem import B1Problem
            self.evaluator = B1Problem(self.sbml_file)
        return (self.evaluator.evaluate(x),)
