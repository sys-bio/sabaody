# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

import argparse

parser = argparse.ArgumentParser(description='Run the B2 problem.')
parser.add_argument('host', metavar='hostname',
                    help='The hostname of the master node of the spark cluster')
parser.add_argument('--topology', required=True,
                    choices = ['ring', 'bidir-ring', 'one-way-ring'],
                    help='The topology to use')
parser.add_argument('--migration', required=True,
                    choices = ['none', 'null',
                      'central', 'central-migrator',
                      'kafka', 'kafka-migrator',
                     ],
                    help='The migration scheme to use')
parser.add_argument('--num-islands', type=int, required=True,
                    help='The migration scheme to use')
args = parser.parse_args()
hostname = args.host
topology_name = args.topology
migrator_name = args.migration
n_islands = args.num_islands
print('Connecting to spark master {}:7077'.format(hostname))

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("b2-driver")
conf.setMaster('spark://{}:7077'.format(hostname))
conf.set('spark.driver.memory', '1g')
#conf.set('spark.executor.memory', '2g')
#conf.set('spark.executor.cores', '4')
#conf.set('spark.cores.max', '40')

import os
from os.path import join, abspath
script_dir = os.path.dirname(os.path.realpath(__file__))
# set files to be copied to the cwd of each executor
spark_files = ','.join(join(script_dir,p) for p in [
    abspath(join('..','..','..','sbml','b2.xml')),
    ])
py_files = ','.join(join(script_dir,p) for p in [
    'data.py',
    'b2problem.py',
    'params.py',
    'b2setup.py',
    ])

print('using spark files {}'.format(spark_files))
conf.set('spark.files', ','.join([spark_files,py_files]))
# set py files
print('using py files {}'.format(py_files))
conf.set('spark.submit.pyFiles', py_files)
conf.set('spark.logConf', True)
sc = SparkContext(conf=conf)

from b2setup import run_b2_islands

island_size = 10
migrant_pool_size = 5
from sabaody.migration import BestSPolicy, FairRPolicy
selection_policy = BestSPolicy(migration_rate=migrant_pool_size)
replacement_policy = FairRPolicy()

run_b2_islands(
    spark_context=sc,
    topology_name=topology_name,
    migrator_name=migrator_name,
    island_size=island_size,
    n_islands=n_islands,
    migrant_pool_size=migrant_pool_size,
    selection_policy=selection_policy,
    replacement_policy=replacement_policy,
    )
