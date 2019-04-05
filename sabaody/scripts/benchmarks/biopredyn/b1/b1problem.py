# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.timecourse.timecourse_sim_base import StalledSimulation
from sabaody.timecourse.timecourse_sim_biopredyn import TimecourseSimBiopredyn
from sabaody.scripts.benchmarks.biopredyn.launcher import BioPreDynUDP

from numpy import array, mean, sqrt, maximum, minimum

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner

from typing import SupportsFloat

class B1Problem(TimecourseSimBiopredyn):
    ''' Class that performs a timecourse simulation
    and evaluates the objective function for b1.'''

    def __init__(self, sbml):
        self.sbml = sbml
        self.r = RoadRunner(sbml)
        # self.r.integrator = 'rk4'
        # print(self.r.integrator)
        # self.r.integrator.absolute_tolerance = 1e-10
        # self.r.integrator.relative_tolerance = 1e-4
        from data import measured_quantity_ids, exp_data, norm_data
        self.measured_quantity_ids = measured_quantity_ids
        self.reference_values = exp_data
        # self.reference_value_means_squared = mean(self.reference_values, axis=0)**2
        self.reference_norms = maximum(norm_data, 0.0005)
        # self.reference_norms_squared = maximum(norm_data, 0.0005)**2
        self.quantity_norms = array(
            [0.0466906, 0.1666200, 0.1325631, 0.0757189, 0.1266561, 0.11634345,
             0.1143341, 0.1104889, 0.2808254, 0.1275417, 0.1163108, 0.26822369,
             0.1866278, 0.1555892, 0.4453806, 0.1598696, 0.1222940, 0.14366202,
             0.1259413, 0.1473395, 0.1407897, 0.1246730, 0.1153060, 0.12375571,
             0.1814630, 0.2199502, 0.1608888, 0.1903940, 0.1242392, 0.11704526,
             0.1287076, 0.1319431, 0.1324937, 0.0690382, 0.1316586, 2.15109423,
             0.1215476, 0.1414125, 0.1112873, 0.1297432, 0.1288462, 0.1155096,
             0.1203922, 0.18807463])**2
        # UDP-D-glucose excluded because it has buggy errors
        self.overall_norm = float(mean(array(
            [0.0466906, 0.1666200, 0.1325631, 0.0757189, 0.1266561, 0.11634345,
             0.1143341, 0.1104889, 0.2808254, 0.1275417, 0.1163108, 0.26822369,
             0.1866278, 0.1555892, 0.4453806, 0.1598696, 0.1222940, 0.14366202,
             0.1259413, 0.1473395, 0.1407897, 0.1246730, 0.1153060, 0.12375571,
             0.1814630, 0.2199502, 0.1608888, 0.1903940, 0.1242392, 0.11704526,
             0.1287076, 0.1319431, 0.1324937, 0.0690382, 0.1316586,
             0.1215476, 0.1414125, 0.1112873, 0.1297432, 0.1288462, 0.1155096,
             0.1203922, 0.18807463])))
        from params import param_ids
        self.param_list = param_ids

        self.penalty_scale = 1.


    def evaluate(self, x):
        # type: (array) -> SupportsFloat
        """
        Evaluate and return the objective function.
        """
        from interruptingcow import timeout
        self.reset()
        self.setParameterVector(x)
        self.r.reset()
        def worker():
            # skip the first timepoint
            # self.r.simulate(0., 1., 10, self.measured_quantity_ids)
            sim = self.r.simulate(0., 119., 120, self.measured_quantity_ids)
            # sim = array(sim[0:-1:10,:])
            residuals = (sim-self.reference_values)/self.reference_norms
            normalized_mse_per_quantity = mean(residuals**2,axis=0)
            # print('sqrt(normalized_mse_per_quantity) = ', sqrt(normalized_mse_per_quantity))
            # print('normed residuals', normalized_mse_per_quantity/self.quantity_norms)
            return float(sqrt(mean(normalized_mse_per_quantity/self.quantity_norms)))*self.overall_norm
        try:
            with timeout(10, StalledSimulation):
                return worker()
        except (RuntimeError, StalledSimulation):
            # if convergence fails, use a penalty score
            return 1e9*self.penalty_scale


    def plotQuantity(self, quantity_id, param_values):
        ''' Plot a simulated quantity vs its data points using Tellurium.'''
        from data import time_values, measured_quantity_ids, measured_quantity_id_to_name_map
        quantity_name = measured_quantity_id_to_name_map[quantity_id]
        iq = measured_quantity_ids.index(quantity_id)
        reference_data = array(self.reference_values[:,iq])

        r = RoadRunner(self.sbml)
        self._setParameterVector(param_values, self.param_list, r)
        r.reset()
        # r.resetAll()
        # r.resetToOrigin()
        # r.integrator = 'euler'
        # r.integrator = 'rk4'
        # r.integrator.subdivision_steps = 1000
        # r.integrator.absolute_tolerance = 1e-10
        # r.integrator.relative_tolerance = 1e-4
        # r.integrator.initial_time_step = 0.001
        # r.integrator.minimum_time_step = 0.0001
        # r.integrator.maximum_time_step = 0.1
        # print(r.integrator)
        sim = r.simulate(0., 119., 120, ['time', quantity_id])
        assert sim.shape[0] == reference_data.shape[0]
        residuals = sim[:,1] - reference_data

        r.reset()
        # r.resetAll()
        # r.resetToOrigin()
        s = r.simulate(0,float(time_values[-1]),121,['time',quantity_id])

        # print('mse for {}: '.format(quantity_name), sqrt(mean((residuals**2)/(self.reference_norms[:,iq]**2))))

        import tellurium as te
        te.plot(time_values, reference_data, scatter=True,
            name=quantity_name+' data', show=False,
            title=quantity_name,
            error_y_pos=maximum(residuals,0),
            error_y_neg=-minimum(residuals,0))
        te.plot(s[:,0], s[:,1], name=quantity_name+' sim')


    def getParameterValue(self,param_index):
        from params import param_index_to_name_map
        try:
            return self.r[param_index_to_name_map[param_index]]
        except KeyError:
            raise KeyError('No such parameter for index {}, must be 0-1758 inclusive'.format(param_index))

    def getCurrentValues_matlab(self):
        # identical to matlab version
        return array([
            self.r.s_0075,
            self.r.s_0180,
            self.r.s_0188,
            self.r.s_0259,
            self.r.s_0260,
            self.r.s_0359,
            self.r.s_0362,
            self.r.s_0394,
            self.r.s_0409,
            self.r.s_0423,
            self.r.s_0434,
            self.r.s_0555,
            self.r.s_0557,
            self.r.s_0563,
            self.r.s_0567,
            self.r.s_0568,
            self.r.s_0586,
            self.r.s_0629,
            self.r.s_0680,
            self.r.s_0765,
            self.r.s_0764,
            self.r.s_0767,
            self.r.s_0785,
            self.r.s_0849,
            self.r.s_0955,
            self.r.s_0991,
            self.r.s_1003,
            self.r.s_1039,
            self.r.s_1045,
            self.r.s_1198,
            self.r.s_1203,
            self.r.s_1360,
            self.r.s_1399,
            self.r.s_1520,
            self.r.s_1538,
            self.r.s_1543,
            self.r.s_1559,
            self.r.s_1565,
            self.getParameterValue(1613) * (self.r.s_0565 - self.r.s_0563) / self.getParameterValue(1614) / (1 + self.r.s_0565 / self.getParameterValue(1614) + 1 + self.r.s_0563 / self.getParameterValue(1615) - 1),
            self.getParameterValue(1628) * self.r.s_0456 / self.getParameterValue(1629) / (1 + self.r.s_0456 / self.getParameterValue(1629)),
            self.getParameterValue(1642) * self.r.s_0680 / self.getParameterValue(1643) / (1 + self.r.s_0680 / self.getParameterValue(1643)),
            self.getParameterValue(1608) * self.r.s_0362 / self.getParameterValue(1609) / (1 + self.r.s_0362 / self.getParameterValue(1609)),
            self.getParameterValue(1616) * self.r.s_0765 / self.getParameterValue(1617) / (1 + self.r.s_0765 / self.getParameterValue(1617)),
            self.getParameterValue(1657) * self.r.s_1520 / self.getParameterValue(1658) / (1 + self.r.s_1520 / self.getParameterValue(1658)),
            ])

    def getCurrentValues(self):
        return array([
            self.r.s_0075,
            self.r.s_0180,
            self.r.s_0188,
            self.r.s_0259,
            self.r.s_0260,
            self.r.s_0359,
            self.r.s_0362,
            self.r.s_0394,
            self.r.s_0409,
            self.r.s_0423,
            self.r.s_0434,
            self.r.s_0555,
            self.r.s_0557,
            self.r.s_0563,
            self.r.s_0567,
            self.r.s_0568,
            self.r.s_0586,
            self.r.s_0629,
            self.r.s_0680,
            self.r.s_0765,
            self.r.s_0764,
            self.r.s_0767,
            self.r.s_0785,
            self.r.s_0849,
            self.r.s_0955,
            self.r.s_0991,
            self.r.s_1003,
            self.r.s_1039,
            self.r.s_1045,
            self.r.s_1198,
            self.r.s_1203,
            self.r.s_1360,
            self.r.s_1399,
            self.r.s_1520,
            self.r.s_1538,
            self.r.s_1543,
            self.r.s_1559,
            self.r.s_1565,
            # reactions
            self.r.r_1166,
            self.r.r_1697,
            self.r.r_1762,
            self.r.r_1106,
            self.r.r_1172,
            self.r.r_2079,
            ])


class B1_UDP(BioPreDynUDP):
    def __init__(self, lb, ub, sbml_file='b1-copasi.xml'):
        super().__init__(lb=lb, ub=ub, sbml_file=sbml_file)

    def fitness(self, x):
        if self.evaluator is None:
            from b1problem import B1Problem
            self.evaluator = B1Problem(self.sbml_file)
        return (self.evaluator.evaluate(x),)
