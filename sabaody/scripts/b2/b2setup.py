from __future__ import print_function, division, absolute_import

from params import getDefaultParamValues

from sabaody.problem_setup import ProblemSetup
from sabaody import Archipelago

from pyspark import SparkContext, SparkConf

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

class B2Configuration:
    '''
    A class to handle initialization of the configuration of the problem run
    and algorithmic parameters, including the island topology, migration settings,
    and Spark configs.
    This class takes a topology name and generates a corresponding topology.
    '''
    def _initialize(self, app_name='b2-driver'):
        '''
        Sets up the Spark config to bundle all Python scripts and SBML files
        necessary to run the problem.
        '''
        from os.path import join, abspath, dirname, realpath
        self.spark_conf = SparkConf().setAppName(app_name)
        self.spark_conf.setMaster('spark://{}:{}'.format(self.hostname,self.port))
        self.spark_conf.set('spark.driver.memory', '1g')
        #self.spark_conf.set('spark.executor.memory', '2g')
        #self.spark_conf.set('spark.executor.cores', '4')
        #self.spark_conf.set('spark.cores.max', '40')

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

        self.spark_conf.set('spark.files', ','.join([spark_files,py_files]))
        # set py files
        self.spark_conf.set('spark.submit.pyFiles', py_files)
        self.spark_conf.set('spark.logConf', True)

        # after setting up the Spark config, we can instantiate the Spark context
        self.spark_context = SparkContext(conf=self.spark_conf)


    @classmethod
    def from_cmdline_args(cls):
        '''
        Initializes the run configuration from command line arguments.
        '''
        config = cls()
        import argparse
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
        from re import match
        if not match(r'[^: ](:[\d]+)?', args.host):
            raise RuntimeError('Expected host name to be either a name or name:port')
        if not ':' in args.host:
            config.hostname = args.host
            config.port = 7077
        else:
            config.hostname,config.port = args.host.split(':')
        config.topology_name = args.topology
        config.migrator_name = args.migration
        config.n_islands = args.num_islands

        config._initialize()

        return config

def make_algorithm():
    #pass
    import pygmo as pg
    return pg.de(gen=10)

def run_b2_islands(config):
    with B2Run('luna', 11211) as run:
        spark_context = config.spark_context
        topology_name = config.topology_name
        migrator_name = config.migrator_name
        island_size = config.island_size
        n_islands = config.n_islands
        migrant_pool_size = config.migrant_pool_size
        selection_policy = config.selection_policy
        replacement_policy = config.replacement_policy

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
        if topology_name == 'ring' or topology_name == 'bidir-ring':
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
            migrator = CentralMigrator(selection_policy, replacement_policy, 'http://luna:10100') # FIXME: hardcoded
            migrator.defineMigrantPools(a.topology, 133)
        elif migrator_name == 'kafka' or migrator_name == 'kafka-migrator':
            from sabaody.kafka_migration_service import KafkaMigrator, KafkaBuilder
            # Kafka must be running
            migrator = KafkaMigrator(selection_policy, replacement_policy, KafkaBuilder('luna', 9092)) # FIXME: hardcoded
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