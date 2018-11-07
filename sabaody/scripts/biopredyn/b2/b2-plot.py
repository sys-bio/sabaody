from __future__ import print_function, division, absolute_import

# run this in a notebook to plot

from b2problem import B2Problem
from params import getDefaultParamValues

with open('../../../sbml/b2.xml') as f:
    sbml = f.read()
m = B2Problem(sbml)
m.evaluate(getDefaultParamValues())
q = 'cpep'
m.plotQuantity(q)
print('MSE for {}: {:.3}'.format(q,m.RMSE_quantity(q)))