# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

# run this in a notebook to plot

from b4problem import B4Problem
from params import getDefaultParamValues
from data import quantity_names

# print(getDefaultParamValues())

with open('../../../../../sbml/b4.xml') as f:
    sbml = f.read()
m = B4Problem(sbml)
print(m.evaluate(getDefaultParamValues()))
for q in quantity_names:
    m.plotQuantity(quantity=q, param_values=getDefaultParamValues())
