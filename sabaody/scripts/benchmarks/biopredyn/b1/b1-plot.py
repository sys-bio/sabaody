# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

# run this in a notebook to plot

from b1problem import B1Problem
from params import getDefaultParamValues
from data import measured_quantity_ids
import arrow

# print(getDefaultParamValues())

load_start = arrow.utcnow()
with open('../../../../../sbml/b1-copasi.xml') as f:
    sbml = f.read()
m = B1Problem(sbml)
load_stop = arrow.utcnow()
print('load duration:',(load_stop-load_start).seconds)

# print(m.evaluate(getDefaultParamValues()))
sim_start = arrow.utcnow()
for k in range(10):
    v = m.evaluate(getDefaultParamValues())
sim_stop = arrow.utcnow()
print('sim duration:',(sim_stop-sim_start).seconds)
print('obj value:',v)

for q in measured_quantity_ids:
# for q in ['s_1543','r_1166']:
    m.plotQuantity(quantity_id=q, param_values=getDefaultParamValues())
