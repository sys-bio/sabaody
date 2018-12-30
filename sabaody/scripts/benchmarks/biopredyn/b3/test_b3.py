from b3problem import B3Problem
from os.path import join, dirname, abspath, realpath
from numpy import allclose, isclose

# problem = B3Problem(abspath(join(dirname(realpath(__file__)), '..','..','..','..','..','sbml','b3.xml')))

from roadrunner import RoadRunner
orig = RoadRunner(abspath(join(dirname(realpath(__file__)), '..','..','..','..','..','sbml','b3-original.xml')))
# print('Original OAA\' = {}'.format(orig["OAA'"]))
new = RoadRunner(abspath(join(dirname(realpath(__file__)), '..','..','..','..','..','sbml','b3.xml')))

for rxn_id in new.model.getReactionIds():
    if orig[rxn_id] != new[rxn_id]:
        print('discrepancy: {} = {} vs {}'.format(rxn_id, orig[rxn_id], new[rxn_id]))

quantities = ['[Emp]','e_Emp_kcat_f','FBP','e_Emp_Kfbp','e_Emp_kcat_r','PG3','e_Emp_Kpg3']
print('** Emp: **')
print('Cell = {} vs {}'.format(orig['Cell'],new['Cell']))
for q in quantities:
    if orig[q] != new[q]:
        print('discrepancy: {} = {} vs {}'.format(q, orig[q], new[q]))

quantities = ['PfkA','e_PfkA_kcat','G6P','e_PfkA_Kg6p','e_PfkA_n','e_PfkA_L','PEP','e_PfkA_Kpep']
print('** e_PfkA **')
for q in quantities:
    if orig[q] != new[q]:
        print('discrepancy: {} = {} vs {}'.format(q, orig[q], new[q]))
