from __future__ import print_function, division, absolute_import

# run this in a notebook to plot

from b2problem import B2Problem
from params import getDefaultParamValues, getBestKnownValues

with open('../../../../../sbml/b2.xml') as f:
    sbml = f.read()
m = B2Problem(sbml)
print('obj value', m.evaluate(getBestKnownValues()))
for q in ['cpep', 'cg6p', 'cpyr', 'cf6p', 'cglcex', 'cg1p', 'cpg', 'cfdp', 'cgap']:
    m.plotQuantity(q, param_values=getBestKnownValues())
    print('MSE for {}: {:.3}'.format(q,m.RMSE_quantity(q)))
