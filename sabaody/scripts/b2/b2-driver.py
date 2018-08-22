# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("b2-driver")
conf.setMaster('spark://10.21.208.21:7077')
conf.set('spark.driver.memory', '1g')
#conf.set('spark.executor.memory', '2g')
#conf.set('spark.executor.cores', '4')
#conf.set('spark.cores.max', '40')
import os
from os.path import join
script_dir = os.path.dirname(os.path.realpath(__file__))
# set files to be copied to the cwd of each executor
conf.set('spark.files', ','.join(join(script_dir,p) for p in [
    join(['..','..','..','sbml','b2.xml']),
    ]))
# set py files
conf.set('spark.submit.pyFiles', ','.join(join(script_dir,p) for p in [
    'data.py',
    'b2problem.py',
    'params.py',
    'b2setup.py',
    ]))
conf.set('spark.logConf', True)
sc = SparkContext(conf=conf)

from sabaody import Archipelago

from b2setup import B2Run

topology = 'one-way-ring'
n_islands = 100
island_size = 100
migrant_pool_size = 5
selection_policy = BestSPolicy(migration_rate=migrant_pool_size)
replacement_policy = FairRPolicy()

with B2Run('luna', 11211) as run:
    from b2problem import make_problem

    # set up topology parameters
    from sabaody.topology import TopologyFactory
    topology_factory = TopologyFactory(problem_constructor=make_problem,
                                       island_size=island_size,
                                       migrant_pool_size=migrant_pool_size,
                                       domain_qualifier=run.getNameQualifier(),
                                       mc_host=run.mc_host,
                                       mc_port=run.mc_port)

    # instantiate algorithm and topology
    import pygmo as pg
    def make_algorithm():
        return pg.de(gen=10)
    if topology_name == 'ring' or topology == 'bidir-ring':
        a = Archipelago(topology_factory.createBidirRing(make_algorithm,n_islands))
    elif topology_name == 'one-way-ring':
        a = Archipelago(topology_factory.createOneWayRing(make_algorithm,n_islands))
    else:
        raise RuntimeError('Unrecognized topology')

    # select migrator
    # assumes the migrator process / service has already been started
    if migrator_name == 'central' or migrator_name == 'central-migrator':
        from sabaody.migration_central import CentralMigrator
        # central migrator process must be running
        migrator = CentralMigrator(selection_policy, replacement_policy, topology, 'http://luna:10100')
    elif migrator_name == 'kafka' or migrator_name == 'kafka-migrator':
        from sabaody.kafka_migration_service import KafkaMigrator, KafkaBuilder
        # Kafka must be running
        migrator = KafkaMigrator(selection_policy, replacement_policy, KafkaBuilder('luna', 9092)
    a.set_mc_server(run.mc_host, run.mc_port, run.getNameQualifier())
    a.run(sc, migrator)

