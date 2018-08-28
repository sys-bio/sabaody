# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

import argparse
from os.path import join, abspath, dirname, realpath
from re import match
from pyspark import SparkContext, SparkConf

parser = argparse.ArgumentParser(description='Run the B2 problem.')
parser.add_argument('host', metavar='hostname',
                    help='The hostname of the master node of the spark cluster with optional port, e.g. localhost:7077')
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
if not match(r'[^: ](:[\d]+)?', args.host):
    raise RuntimeError('Expected host name to be either a name or name:port')
if not ':' in args.host:
    hostname = args.host
    port = 7077
else:
    hostname,port = args.host.split(':')
topology_name = args.topology
migrator_name = args.migration
n_islands = args.num_islands
print('Connecting to spark master {}:{}'.format(hostname,port))

conf = SparkConf().setAppName("b2-driver")
conf.setMaster('spark://{}:{}'.format(hostname,port))
conf.set('spark.driver.memory', '1g')
#conf.set('spark.executor.memory', '2g')
#conf.set('spark.executor.cores', '4')
#conf.set('spark.cores.max', '40')

script_dir = dirname(realpath(__file__))

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

conf.set('spark.files', ','.join([spark_files,py_files]))
# set py files
conf.set('spark.submit.pyFiles', py_files)
conf.set('spark.logConf', True)

sc = SparkContext(conf=conf)

island_size = 10
migrant_pool_size = 5
from sabaody.migration import BestSPolicy, FairRPolicy
selection_policy = BestSPolicy(migration_rate=migrant_pool_size)
replacement_policy = FairRPolicy()

from b2setup import run_b2_islands
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
