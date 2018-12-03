# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from roadrunner import Logger
Logger.disableConsoleLogging()
Logger.setLevel(Logger.LOG_FATAL)

from sabaody.utils import create_solo_benchmark_table, commit_solo_benchmark_run
from params import getDefaultParamValues, getUpperBound, getLowerBound
from b2problem import B2_UDP

import arrow
from scipy.optimize import differential_evolution
from pprint import pprint

# make sure the database and table are ready before we do anything
table = 'scipy_de_solo_runs'
create_solo_benchmark_table(
    host='luna',
    user='sabaody',
    database='sabaody',
    password='w00t',
    table=table)

problem = B2_UDP(getLowerBound(),getUpperBound(),'../../../../../sbml/b2.xml')

print('initial score: {}'.format(problem.fitness(getDefaultParamValues())[0]))

time_start = arrow.utcnow()

N = 1000
r = differential_evolution(
    func=lambda x: float(problem.fitness(x)[0]),
    bounds=[(lb,ub) for lb,ub in zip(getLowerBound(),getUpperBound())],
    maxiter=N)

time_end = arrow.utcnow()

print('final score: {}'.format(problem.fitness(r.x)[0]))
print('max iterations: {}'.format(N))
print('duration: {}'.format(time_end-time_start))

values = r.x
parameters_dict = {}
for p,v in zip(problem.evaluator.param_list,values):
    parameters_dict[p] = v

pprint(parameters_dict)

commit_solo_benchmark_run(
    host='luna',
    user='sabaody',
    database='sabaody',
    password='w00t',
    table=table,
    description='scipy de b2',
    final_score=r.fun,
    final_params=parameters_dict,
    time_start=time_start,
    time_end=time_end)
