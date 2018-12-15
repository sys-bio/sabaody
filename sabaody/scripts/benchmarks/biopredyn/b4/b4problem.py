# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.timecourse.timecourse_sim_biopredyn import TimecourseSimBiopredyn
from sabaody.scripts.benchmarks.biopredyn.benchsetup import BioPreDynUDP

from params import getUpperBound, getLowerBound, param_ids
from data import time_values, conc_ids, scaled_data, scaled_error

from numpy import array, zeros, maximum, minimum

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner

class B4Problem(TimecourseSimBiopredyn):
    ''' Class that performs a timecourse simulation
    and calculates the residuals for b4.'''

    def __init__(self, sbml):
        super().__init__(sbml, time_values=time_values, measured_quantities=conc_ids, param_ids=param_ids, scaled_data=scaled_data, scaled_error=scaled_error)


    def plotQuantity(self, quantity, param_values):
        ''' Plot a simulated quantity vs its data points using Tellurium.'''
        from data import name_to_id_map, conc_indices
        quantity_id = name_to_id_map[quantity]
        iq = conc_ids.index(quantity_id)
        reference_data = array(self.scaled_data[:,iq])

        r = RoadRunner(self.sbml)
        self._setParameterVector(param_values, self.param_list, r)
        # r.selections = ['time', quantity_id]
        t_now = 0.
        simulated_quantity = zeros((len(self.time_values),))
        residuals = zeros((len(self.time_values),))
        for it_next in range(1, len(self.time_values)):
            r.simulate(t_now, self.time_values[it_next], 10)
            t_now = self.time_values[it_next]
            simulated_quantity[it_next-1] = r[quantity_id]
            residuals[it_next-1] = r[quantity_id]-reference_data[it_next-1]
        r.reset()
        self._setParameterVector(param_values, self.param_list, r)
        s = r.simulate(0,float(self.time_values[-1]),1000,['time',quantity_id])

        import tellurium as te
        te.plot(self.time_values, reference_data, scatter=True,
            name=quantity+' data', show=False,
            error_y_pos=maximum(residuals,0),
            error_y_neg=-minimum(residuals,0))
        te.plot(s[:,0], s[:,1], name=quantity+' sim')


class B2_UDP(BioPreDynUDP):
    def __init__(self, lb, ub, sbml_file='b4.xml'):
        super().__init__(lb=lb, ub=ub, sbml_file=sbml_file)

    def fitness(self, x):
        if self.evaluator is None:
            from b4problem import B4Problem
            self.evaluator = B4Problem(self.sbml_file)
        return (self.evaluator.evaluate(x),)
