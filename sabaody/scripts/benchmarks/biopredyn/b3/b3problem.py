# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.timecourse.timecourse_sim_base import StalledSimulation
from sabaody.timecourse.timecourse_sim_biopredyn import TimecourseSimBiopredyn
from sabaody.scripts.benchmarks.biopredyn.launcher import BioPreDynUDP

from numpy import array, mean, sqrt, maximum, minimum, vstack

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner

from typing import SupportsFloat

class B3Problem(TimecourseSimBiopredyn):
    ''' Class that performs a timecourse simulation
    and evaluates the objective function for b1.'''

    def __init__(self, sbml):
        self.sbml = sbml
        self.r = RoadRunner(sbml)
        from data import measured_quantity_ids, exp_data
        self.measured_quantity_ids = measured_quantity_ids
        self.reference_values = exp_data
        self.reference_value_means_squared = mean(self.reference_values, axis=0)**2
        from params import new_param_ids as param_ids
        self.param_list = param_ids

        self.penalty_scale = 1.


    def evaluate(self, x):
        # type: (array) -> SupportsFloat
        """
        Evaluate and return the objective function.
        """
        from interruptingcow import timeout
        # from data import time_end, n_points
        from data import t1, t2, time_end, n1, n2, n3
        self.reset()
        self.setParameterVector(x)
        self.r.reset()
        def worker():
            # sim = array(self.r.simulate(0., time_end, n_points, self.measured_quantity_ids))

            s1 = self.r.simulate(0., t1, n1, self.measured_quantity_ids)
            self.r.simulate(t1, t1+t1/n1/50, 10, self.measured_quantity_ids)
            s2 = self.r.simulate(t1, t2, n2, self.measured_quantity_ids)
            self.r.simulate(t2, t2+(t2-t1)/n2/50, 10, self.measured_quantity_ids)
            s3 = self.r.simulate(t2, time_end, n3, self.measured_quantity_ids)
            sim = vstack((
                s1,
                s2,
                s3,
                ))
            residuals = sim-self.reference_values
            from pprint import pprint
            print('residuals:')
            normalized_mse_per_quantity = mean(residuals**2,axis=0)/self.reference_value_means_squared
            pprint({id: value for id,value in zip(self.measured_quantity_ids, normalized_mse_per_quantity)})
            return sqrt(mean(normalized_mse_per_quantity))
        try:
            with timeout(10, StalledSimulation):
                return worker()
        except (RuntimeError, StalledSimulation):
            # if convergence fails, use a penalty score
            return 1e9*self.penalty_scale


    def plotQuantity(self, quantity_id, param_values):
        ''' Plot a simulated quantity vs its data points using Tellurium.'''
        from data import measured_quantity_ids, measured_quantity_id_to_name_map
        from data import t1, t2, time_end, n1, n2, n3
        quantity_name = measured_quantity_id_to_name_map.get(quantity_id,quantity_id)
        iq = measured_quantity_ids.index(quantity_id)
        reference_data = array(self.reference_values[:,iq])

        r = RoadRunner(self.sbml)
        r.reset()
        r.resetAll()
        r.resetToOrigin()
        self._setParameterVector(param_values, self.param_list, r)
        # r.oneStep(0., 10)
        # print('plotQuantity OAA\' = {}'.format(r["OAA'"]))
        s1 = r.simulate(0., t1, n1, ['time', quantity_id])
        r.simulate(t1, t1+t1/n1/50, 10, ['time', quantity_id])
        s2 = r.simulate(t1, t2, n2, ['time', quantity_id])
        r.simulate(t2, t2+(t2-t1)/n2/50, 10, ['time', quantity_id])
        s3 = r.simulate(t2, time_end, n3, ['time', quantity_id])
        sim = vstack((
            s1,
            s2,
            s3,
            ))
        assert sim.shape[0] == reference_data.shape[0]
        residuals = sim[:,1] - reference_data

        r.reset()
        r.resetAll()
        r.resetToOrigin()
        self._setParameterVector(param_values, self.param_list, r)
        # self._setParameterVector(param_values, self.param_list, r)
        s = r.simulate(0,time_end,1000,['time',quantity_id])

        import tellurium as te
        te.plot(sim[:,0], reference_data, scatter=True,
            name=quantity_name+' data', show=False,
            title=quantity_name,
            error_y_pos=maximum(residuals,0),
            error_y_neg=-minimum(residuals,0))
        te.plot(s[:,0], s[:,1], name=quantity_name+' sim')
        print('deviation for {}: {}'.format(quantity_id, mean(residuals**2)/self.reference_value_means_squared[iq]))


    def getParameterValue(self,param_index):
        from params import param_index_to_name_map
        try:
            return self.r[param_index_to_name_map[param_index]]
        except KeyError:
            raise KeyError('No such parameter for index {}, must be 0-1758 inclusive'.format(param_index))


class B3_UDP(BioPreDynUDP):
    def __init__(self, lb, ub, sbml_file='b3.xml'):
        super().__init__(lb=lb, ub=ub, sbml_file=sbml_file)

    def fitness(self, x):
        if self.evaluator is None:
            from b3problem import B3Problem
            self.evaluator = B3Problem(self.sbml_file)
        return (self.evaluator.evaluate(x),)
