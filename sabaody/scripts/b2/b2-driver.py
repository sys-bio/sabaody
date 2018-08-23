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
args = parser.parse_args()
hostname = args.host
topology_name = args.topology
migrator_name = args.migration
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
#spark_files = ','.join(join(script_dir,p) for p in [
    #abspath(join('..','..','..','sbml','b2.xml')),
    #])
#print('using spark files {}'.format(spark_files))
#conf.set('spark.files', spark_files)
## set py files
#py_files = ','.join(join(script_dir,p) for p in [
    #'data.py',
    #'b2problem.py',
    #'params.py',
    #'b2setup.py',
    #])
#print('using py files {}'.format(py_files))
#conf.set('spark.submit.pyFiles', py_files)
conf.set('spark.logConf', True)
sc = SparkContext(conf=conf)

from sabaody import Archipelago

from b2setup import B2Run

n_islands = 100
island_size = 100
migrant_pool_size = 5
from sabaody.migration import BestSPolicy, FairRPolicy
selection_policy = BestSPolicy(migration_rate=migrant_pool_size)
replacement_policy = FairRPolicy()

with B2Run('luna', 11211) as run:
    from b2problem import make_problem

    import arrow
    time_start = arrow.utcnow()

    # set up topology parameters
    from sabaody.topology import TopologyFactory
    topology_factory = TopologyFactory(problem_constructor=make_problem,
                                       island_size=island_size,
                                       migrant_pool_size=migrant_pool_size,
                                       domain_qualifier=run.getNameQualifier(),
                                       mc_host=run.mc_host,
                                       mc_port=run.mc_port)

    # instantiate algorithm and topology
    def make_algorithm():
        pass
        #import pygmo as pg
        #return pg.de(gen=10)
    if topology_name == 'ring' or topology_name == 'bidir-ring':
        a = Archipelago(topology_factory.createBidirRing(None,n_islands))
    elif topology_name == 'one-way-ring':
        a = Archipelago(topology_factory.createOneWayRing(None,n_islands))
    else:
        raise RuntimeError('Unrecognized topology')

    # select migrator
    # assumes the migrator process / service has already been started
    if migrator_name == 'central' or migrator_name == 'central-migrator':
        from sabaody.migration_central import CentralMigrator
        # central migrator process must be running
        migrator = CentralMigrator(selection_policy, replacement_policy, 'http://luna:10100')
        migrator.defineMigrantPools(a.topology, 133)
    elif migrator_name == 'kafka' or migrator_name == 'kafka-migrator':
        from sabaody.kafka_migration_service import KafkaMigrator, KafkaBuilder
        # Kafka must be running
        migrator = KafkaMigrator(selection_policy, replacement_policy, KafkaBuilder('luna', 9092))
    else:
        raise RuntimeError('Migration scheme undefined')
    a.set_mc_server(run.mc_host, run.mc_port, run.getNameQualifier())
    a.run(sc, migrator)

    time_end = arrow.utcnow()
    print('Total run time: {}'.format(time_start.humanize(time_end,only_distance=True)))
