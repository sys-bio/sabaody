# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

# run this in a notebook to plot

from b3problem import B3Problem
from params import getDefaultParamValues, getBestKnownValues
from data import measured_quantity_ids

v = getBestKnownValues()
# v[0] = 3.
# v[10] = 3.
# v[20] = 3.
# for k in range(len(v)):
#     v[k] = 3.
# print(getDefaultParamValues())

with open('../../../../../sbml/b3.xml', encoding='utf-8') as f:
    sbml = f.read()
m = B3Problem(sbml)
print(m.evaluate(v))
for q in measured_quantity_ids:
    m.plotQuantity(quantity_id=q, param_values=v)