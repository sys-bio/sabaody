# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("b2-driver")
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
    algorithm = pg.de(gen=10)
    if topology_name == 'ring' or topology == 'bidir-ring':
        a = Archipelago(topology_factory.createBidirRing(algorithm,n_islands))
    elif topology_name == 'one-way-ring':
        a = Archipelago(topology_factory.createOneWayRing(algorithm,n_islands))
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

