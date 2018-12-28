# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

# run this in a notebook to plot

from b3problem import B3Problem
from params import getDefaultParamValues
from data import measured_quantity_ids

# print(getDefaultParamValues())

with open('../../../../../sbml/b3.xml') as f:
    sbml = f.read()
m = B3Problem(sbml)
print(m.evaluate(getDefaultParamValues()))
for q in measured_quantity_ids:
    m.plotQuantity(quantity_id=q, param_values=getDefaultParamValues())
