# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.timecourse.timecourse_sim_base import StalledSimulation
from sabaody.timecourse.timecourse_sim_biopredyn import TimecourseSimBiopredyn
from sabaody.scripts.benchmarks.biopredyn.launcher import BioPreDynUDP

from numpy import array, zeros, maximum, minimum, mean, sqrt

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner

class B4Problem(TimecourseSimBiopredyn):
    ''' Class that performs a timecourse simulation
    and calculates the residuals for b4.'''

    def __init__(self, sbml):
        '''
        Constructor.

        :param measured_quantities: A list of the measured quantities.
        :param scaled_data: The scaled reference data.
        :param scaled_error: The scaled reference error.
        '''
        from params import param_ids
        from data import time_values, conc_ids, scaled_data, scaled_error
        self.sbml = sbml
        self.r = RoadRunner(sbml)
        self.r.selections = ['time'] + conc_ids
        self.time_values = time_values
        assert self.time_values[0] == 0.
        self.measured_quantities = conc_ids
        self.param_list = param_ids
        self.reference_values = scaled_data
        self.reference_value_means = mean(self.reference_values, axis=0)
        self.scaled_data = scaled_data
        self.scaled_error = scaled_error

        self.penalty_scale = 1.


    def evaluate_original(self, x):
        # type: (array) -> SupportsFloat
        """
        Evaluate the objective function and return the result. Identical to original
        biopredynbench evaluation, i.e. divides by scaled error. Difficult to compare
        across models.
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


    def evaluate(self, x):
        # type: (array) -> SupportsFloat
        """
        Evaluate the objective function and return the result.
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
                    scaled_residuals[it_next-1,iq] = (self.r[q]-self.scaled_data[it_next-1,iq])/self.reference_value_means[iq]
            return sqrt(mean(scaled_residuals**2.))
        try:
            with timeout(10, StalledSimulation):
                return worker()
        except (RuntimeError, StalledSimulation):
            # if convergence fails, use a penalty score
            return 1e9*self.penalty_scale


    def plotQuantity(self, quantity, param_values):
        ''' Plot a simulated quantity vs its data points using Tellurium.'''
        from data import name_to_id_map, conc_indices
        quantity_id = name_to_id_map[quantity]
        iq = self.measured_quantities.index(quantity_id)
        reference_data = array(self.scaled_data[:,iq])

        r = RoadRunner(self.sbml)
        self._setParameterVector(param_values, self.param_list, r)
        r.reset()
        # r.selections = ['time', quantity_id]
        t_now = 0.
        simulated_quantity = zeros((len(self.time_values),))
        residuals = zeros((len(self.time_values),))
        for it_next in range(1, len(self.time_values)):
            self._setParameterVector(param_values, self.param_list, r)
            r.simulate(t_now, self.time_values[it_next], 100)
            t_now = self.time_values[it_next]
            simulated_quantity[it_next-1] = r[quantity_id]
            residuals[it_next-1] = r[quantity_id]-reference_data[it_next-1]
        r.reset()
        # self._setParameterVector(param_values, self.param_list, r)
        s = r.simulate(0,float(self.time_values[-1]),1000,['time',quantity_id])

        import tellurium as te
        te.plot(self.time_values, reference_data, scatter=True,
            name=quantity+' data', show=False,
            error_y_pos=maximum(residuals,0),
            error_y_neg=-minimum(residuals,0))
        te.plot(s[:,0], s[:,1], name=quantity+' sim')


class B4_UDP(BioPreDynUDP):
    def __init__(self, lb, ub, sbml_file='b4.xml'):
        super().__init__(lb=lb, ub=ub, sbml_file=sbml_file)

    def fitness(self, x):
        if self.evaluator is None:
            from b4problem import B4Problem
            self.evaluator = B4Problem(self.sbml_file)
        return (self.evaluator.evaluate(x),)
