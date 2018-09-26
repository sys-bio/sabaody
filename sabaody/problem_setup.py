# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody import getQualifiedName, Archipelago

from pymemcache.client.base import Client
from .metrics import InfluxDBMetric

from pyspark import SparkContext, SparkConf

from uuid import uuid4
from time import time

class MemcachedMonitor:
    '''
    Abstracts some of the logic of setting up a parameter fitting problem.
    Provides information via MC for monitoring.
    '''
    def __init__(self, mc_host, mc_port):
        self.mc_host = mc_host
        self.mc_port = mc_port
        self.mc_client = Client((self.mc_host,self.mc_port))

        self.setupMonitoringVariables()

    def __enter__(self):
        from .diagnostics import test_memcached
        test_memcached(self.mc_host, self.mc_port)
        return self

    def domainAppend(self,s):
        return '.'.join((self.getDomain(),s))

    def __exit__(self, exception_type, exception_val, trace):
        self.mc_client.set(self.domainAppend('run.status'), 'finished', 604800)
        self.mc_client.set(self.domainAppend('run.endTime'), str(time()), 604800)

    def setupMonitoringVariables(self):
        self.run = int(self.mc_client.get(self.domainAppend('run')) or 0)
        self.run += 1
        self.mc_client.set(self.domainAppend('run'), self.run, 604800)

        self.run_id = str(uuid4())
        self.mc_client.set(self.domainAppend('runId'), self.run_id, 604800)
        self.mc_client.set(self.domainAppend('run.startTime'), str(time()), 604800)
        self.mc_client.set(self.domainAppend('run.status'), 'active', 604800)

        print('Starting run {} of {} problem with id {}...'.format(self.run, self.getName(), self.run_id))

    def getNameQualifier(self):
        from toolz import partial
        return partial(getQualifiedName, self.getName(), str(self.run_id))

class TimecourseRunConfiguration:
    '''
    A class to handle initialization of the configuration of the problem run
    and algorithmic parameters, including the island topology, migration settings,
    and Spark configs.
    This class takes a topology name and generates a corresponding topology.
    '''
    def _initialize_spark(self, app_name, spark_files, py_files):
        '''
        Sets up the Spark config to bundle all Python scripts and SBML files
        necessary to run the problem.
        '''
        from os.path import join
        self.spark_conf = SparkConf().setAppName(app_name)
        self.spark_conf.setMaster('spark://{}:{}'.format(self.hostname,self.port))
        self.spark_conf.set('spark.driver.memory', '1g')
        #self.spark_conf.set('spark.executor.memory', '2g')
        #self.spark_conf.set('spark.executor.cores', '4')
        #self.spark_conf.set('spark.cores.max', '40')

        self.spark_conf.set('spark.files', ','.join([spark_files,py_files]))
        # set py files
        self.spark_conf.set('spark.submit.pyFiles', py_files)
        self.spark_conf.set('spark.logConf', True)

        # after setting up the Spark config, we can instantiate the Spark context
        self.spark_context = SparkContext(conf=self.spark_conf)


    @classmethod
    def _create_arg_parser(cls):
        import argparse
        parser = argparse.ArgumentParser(description='Run the B2 problem.')
        parser.add_argument('command',
                            help='The command. Can be "run" or "count-params".')
        parser.add_argument('--host', metavar='hostname', required=True,
                            help='The hostname of the master node of the spark cluster with optional port, e.g. localhost:7077')
        parser.add_argument('--topology', required=True,
                            help='The topology to use')
        parser.add_argument('--migration', required=True,
                            choices = ['none', 'null',
                              'central', 'central-migrator',
                              'kafka', 'kafka-migrator',
                            ],
                            help='The migration scheme to use')
        parser.add_argument('--migration-policy', required=True,
                            choices = ['none', 'null',
                              'each', 'each-to-all',
                              'uniform',
                            ],
                            help='The migration policy to use')
        parser.add_argument('--num-islands', type=int, required=True,
                            help='The migration scheme to use')
        return parser


    @classmethod
    def from_cmdline_args(cls, app_name, spark_files, py_files):
        '''
        Initializes the run configuration from command line arguments.
        '''
        config = cls()
        parser = cls._create_arg_parser()
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
        config.migration_policy_name = args.migration_policy
        config.n_islands = args.num_islands
        config.command = args.command

        config._initialize_spark(app_name, spark_files, py_files)

        return config


    def make_algorithm(self):
        import pygmo as pg
        return pg.de(gen=10) # FIXME: hard-coded algo


    def generate_archipelago(self, topology_name, topology_factory, metric):
        from os.path import isfile
        if isfile(topology_name):
            import pickle
            with open(topology_name) as f:
                return Archipelago(pickle.load(f), metric)
        elif topology_name == 'ring' or topology_name == 'bidir-ring':
            return Archipelago(topology_factory.createBidirRing(self.make_algorithm(),self.n_islands), metric)
        elif topology_name == 'one-way-ring':
            return Archipelago(topology_factory.createOneWayRing(self.make_algorithm(),self.n_islands), metric)
        else:
            raise RuntimeError('Unrecognized topology')

    def select_migration_policy(self, migration_policy_name):
        from sabaody.migration import MigrationPolicyEachToAll, MigrationPolicyUniform
        if migration_policy_name == 'each' or migration_policy_name == 'each-to-all':
            return MigrationPolicyEachToAll()
        elif migration_policy_name == 'uniform':
            return MigrationPolicyUniform()
        else:
            raise RuntimeError('Unknown migration policy')


    def select_migrator(self, migrator_name, migration_policy, selection_policy, replacement_policy):
        if migrator_name == 'central' or migrator_name == 'central-migrator':
            from sabaody.migration_central import CentralMigrator
            # central migrator process must be running
            return CentralMigrator(migration_policy, selection_policy, replacement_policy, 'http://luna:10100') # FIXME: hardcoded
        elif migrator_name == 'kafka' or migrator_name == 'kafka-migrator':
            from sabaody.kafka_migration_service import KafkaMigrator, KafkaBuilder
            # Kafka must be running
            return KafkaMigrator(selection_policy, replacement_policy, KafkaBuilder('luna', 9092)) # FIXME: hardcoded
        else:
            raise RuntimeError('Migration scheme undefined')

    def create_metric(self, prefix):
        return InfluxDBMetric(host='luna', database_prefix=prefix) # FIXME: hardcoded


    def run_command(self, command):
        if command == 'run' or command == 'run-islands':
            return self.run_islands()
        else:
            raise RuntimeError('Unrecognized command: {}'.format(command))