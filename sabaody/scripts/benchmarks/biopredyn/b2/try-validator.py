# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

import sabaody

from sabaody.timecourse.timecourse_sim_validate import TimecourseSimValidate
from params import param_list, getBestKnownValues

from numpy import array
from os.path import abspath

sim = TimecourseSimValidate(
    sbml = abspath('../../../../../sbml/b2.xml'),
    measured_quantities = ['cpep', 'cg6p', 'cpyr', 'cf6p', 'cglcex', 'cg1p', 'cpg', 'cfdp', 'cgap'],
    param_list = param_list,
    reference_param_values = getBestKnownValues(),
    time_start = 0.,
    time_end = 300.,
    n=100)

print('value at reference: {}'.format(sim.evaluate(getBestKnownValues())))
# tweak values
new_values = array(getBestKnownValues())
new_values[0] -= 1.
new_values[5] += 1.
print('value at perturbation: {}'.format(sim.evaluate(new_values)))
