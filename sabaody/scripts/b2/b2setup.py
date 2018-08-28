from __future__ import print_function, division, absolute_import

from params import getDefaultParamValues

from sabaody.problem_setup import ProblemSetup

from sabaody import Archipelago

# some refs:
#https://developerzen.com/best-practices-writing-production-grade-pyspark-jobs-cb688ac4d20f
#https://medium.com/@mrpowers/creating-a-pyspark-project-with-pytest-pyenv-and-egg-files-d2709eb1604c

class B2Run(ProblemSetup):
    '''
    Abstracts some of the logic of setting up a parameter fitting problem.
    Provides information via MC for monitoring.
    '''
    def getName(self):
        return 'B2'

    def getDomain(self):
        return 'com.how2cell.sabaody.B2'

    def calculateInitialScore(self):
        with open('../../../sbml/b2.xml') as f:
            sbml = f.read()

        # show initial score
        from b2problem import B2Problem
        p = B2Problem(sbml)
        self.initial_score = p.evaluate(getDefaultParamValues())
        print('Initial score: {}'.format(self.initial_score))

def run_b2_islands(spark_context, topology_name, migrator_name, island_size, n_islands, migrant_pool_size, selection_policy, replacement_policy):
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
        champion_scores = a.run(spark_context, migrator, 10)
        print('chamption scores {}'.format(champion_scores))
        min_score = min(champion_scores)
        average_score = float(sum(champion_scores))/len(champion_scores)
        print('min champion score {}'.format(min_score))
        print('mean champion score {}'.format(average_score))

        time_end = arrow.utcnow()
        print('Total run time: {}'.format(time_start.humanize(time_end,only_distance=True)))