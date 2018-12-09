from __future__ import print_function, division, absolute_import

# run this in a notebook to plot

from b2problem_validator import B2ProblemValidator

from params import getDefaultParamValues, getBestKnownValues

n=100
with open('../../../../../sbml/b2.xml') as f:
    sbml = f.read()
m = B2ProblemValidator(sbml, n)
q = 'cpep'
m.plotQuantity(identifier=q, param_values=getBestKnownValues(), n=n)
print('MSE for {}: {:.3}'.format(q,m.RMSE_quantity(q)))
