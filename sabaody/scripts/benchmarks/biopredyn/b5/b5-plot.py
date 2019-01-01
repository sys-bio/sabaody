# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

# run this in a notebook to plot

from b5problem import B5Problem
from parameters import getDefaultParamValues
from observables import observables

# print(getDefaultParamValues())

with open('../../../../../sbml/b5.xml') as f:
    sbml = f.read()
m = B5Problem(sbml)
print(m.evaluate(getDefaultParamValues()))
for q in observables:
    m.plotQuantity(quantity_id=q, param_values=getDefaultParamValues())
