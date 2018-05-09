# B2 non-forking version
from __future__ import print_function, division, absolute_import

from pymemcache.client.base import Client
from pyspark import SparkContext, SparkConf
mc_host = 'luna'
mc_port = 11211
client = Client((mc_host,mc_port))
conf = SparkConf().setAppName("b2-single")
sc = SparkContext(conf=conf)

from sabaody import Archipelago, Problem, getQualifiedName
#from b2problem import B2Problem
#from params import getDefaultParamValues, getLowerBound, getUpperBound

from uuid import uuid4
from time import time

# some refs:
#https://developerzen.com/best-practices-writing-production-grade-pyspark-jobs-cb688ac4d20f
#https://medium.com/@mrpowers/creating-a-pyspark-project-with-pytest-pyenv-and-egg-files-d2709eb1604c

run = int(client.get('com.how2cell.sabaody.B2.run'))
if run is None:
    run = 1
else:
    run += 1
client.set('com.how2cell.sabaody.B2.run', run, 604800)

run_id = str(uuid4())
client.set('com.how2cell.sabaody.B2.runId', run_id, 604800)
client.set('com.how2cell.sabaody.B2.run.startTime', str(time()), 604800)
client.set('com.how2cell.sabaody.B2.run.status', 'active', 604800)

print('Starting run {} of B2 problem with id {}...'.format(run, run_id))

with open('../../../sbml/b2.xml') as f:
    sbml = f.read()

# show initial score
#p = B2Problem(sbml)
#initial_score = p.evaluate(getDefaultParamValues())
initial_score = 0.
#print('Initial score: {}'.format(initial_score))

from toolz import partial

#a = Archipelago(4, lambda: Problem(B2Problem(sbml), getLowerBound(), getUpperBound()), initial_score, None, partial(getQualifiedName, 'B2', str(run_id)), mc_host, mc_port)
a = Archipelago(4, sbml, initial_score, None, partial(getQualifiedName, 'B2', str(run_id)), mc_host, mc_port)
a.run(sc, initial_score)

client.set('com.how2cell.sabaody.B2.run.status', 'finished', 604800)
client.set('com.how2cell.sabaody.B2.run.endTime', str(time()), 604800)