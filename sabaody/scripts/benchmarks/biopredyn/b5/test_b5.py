# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

# run this in a notebook to plot

from b5problem import B5Problem
from parameters import getDefaultParamValues
from observables import observables

from os.path import join, dirname, realpath

with open(join(dirname(realpath(__file__)), '../../../../../sbml/b5.xml')) as f:
    sbml = f.read()
m = B5Problem(sbml)
m.setExperimentNumber(0)
m.r.reset()
m.r.resetAll()
# m.setParameterVector(getDefaultParamValues(), exponential=False)
print(getDefaultParamValues())
print(m.r.getReactionRates())
