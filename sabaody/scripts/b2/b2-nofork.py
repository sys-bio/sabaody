# B2 non-forking version
from __future__ import print_function, division, absolute_import

from pymemcache.client.base import Client
from pyspark import SparkContext, SparkConf
mc_host = 'luna'
mc_port = 11211
client = Client((mc_host,mc_port))
conf = SparkConf().setAppName("b2-single")
sc = SparkContext(conf=conf)

from sabaody import Archipelago
from obj import B2Model
from params import getDefaultParamValues, getLowerBound, getUpperBound

# some refs:
#https://developerzen.com/best-practices-writing-production-grade-pyspark-jobs-cb688ac4d20f
#https://medium.com/@mrpowers/creating-a-pyspark-project-with-pytest-pyenv-and-egg-files-d2709eb1604c

def worker_function():
    archi = Archipelago

run = int(client.get('com.how2cell.sabaody.B2.run'))
if run is None:
    run = 1
else:
    run += 1
client.set('com.how2cell.sabaody.B2.run', run, 604800)

print('Starting run {} of B2 problem...'.format(run))

# show initial score
e = B2Model()
print('Initial score: {}'.format(e.evaluate(getDefaultParamValues())))