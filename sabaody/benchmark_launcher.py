# Sabaody
# Copyright 2018-2019 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody import getQualifiedName, Archipelago
from sabaody.topology import TopologyFactory

from pymemcache.client.base import Client
from sabaody.metrics import InfluxDBMetric

from pyspark import SparkContext, SparkConf
from numpy import array, mean

from itertools import chain
from uuid import uuid4
from time import time

class MemcachedMonitor:
    '''
    Abstracts some of the logic of setting up a parameter fitting problem.
    Provides information via MC for monitoring.
    '''
    def __init__(self, name, mc_host, mc_port, run=None, run_id=None):
        self.name = name
        self.run = run
        self.run_id = run_id
        self.mc_host = mc_host
        self.mc_port = mc_port
        self.mc_client = Client((self.mc_host,self.mc_port))

    def getName(self):
        return self.name


    def __enter__(self):
        from sabaody.diagnostics import test_memcached
        test_memcached(self.mc_host, self.mc_port)
        self.setupMonitoringVariables()
        return self


    def domainAppend(self,s):
        return '.'.join((self.getDomain(),s))


    def __exit__(self, exception_type, exception_val, trace):
        self.update('finished', self.run, 'status')
        self.update(str(time()), self.run, 'endTime')


    def setupMonitoringVariables(self):
        if self.run is None:
            # self.run = int(self.mc_client.get(self.domainAppend('run')) or 0)
            # self.run += 1
            self.run = 0
        self.update(self.run, 'run')

        if self.run_id is None:
            self.run_id = str(uuid4())
        self.update(self.run_id, 'runId')

        print('monitor at {}'.format(self.getNameQualifier()()))

        self.update(str(time()), 'startTime')
        self.update('active', 'status')

        # print('Starting run {} of {} with id {}...'.format(self.run, self.getName(), self.run_id))

    def getNameQualifier(self):
        from toolz import partial
        return partial(getQualifiedName, self.getName(), str(self.run_id))


    def __getstate__(self):
        return {
          'name': self.name,
          'run': self.run,
          'run_id': self.run_id,
          'mc_host': self.mc_host,
          'mc_port': self.mc_port}


    def __setstate__(self, state):
        self.name = state['name']
        self.run = state['run']
        self.run_id = state['run_id']
        self.mc_host = state['mc_host']
        self.mc_port = state['mc_port']
        self.mc_client = Client((self.mc_host,self.mc_port))


    def update(self, value, *key):
        # print('update {}'.format(self.getNameQualifier()(*list(str(k) for k in key))))
        self.mc_client.set(self.getNameQualifier()(*list(str(k) for k in key)), str(value), 604800)


    def best_score_candidate(self, best_f, best_x):
        from json import dumps, loads
        current_best_f = self.mc_client.get(self.getNameQualifier()('global', 'best_f'))
        if current_best_f is not None:
            current_best_f = array(loads(current_best_f))
        if current_best_f is None or mean(best_f) < mean(current_best_f):
            self.update(dumps(best_f.tolist()), 'global', 'best_f')
            self.update(dumps(best_x.tolist()), 'global', 'best_x')


    def get_best_x(self):
        best_x = self.mc_client.get(self.getNameQualifier()('global', 'best_x'))
        if best_x is not None:
            from json import loads
            best_x = array(loads(best_x))
        return best_x


    def get_best_f(self):
        best_f = self.mc_client.get(self.getNameQualifier()('global', 'best_f'))
        if best_f is not None:
            from json import loads
            best_f = array(loads(best_f))
        return best_f


def print_out_status(client, domainJoin, screen):
    from asciimatics.screen import Screen
    from toolz import partial

    from time import sleep
    from json import dumps, loads
    from pprint import PrettyPrinter
    from time import time
    while True:
        run = client.get(domainJoin('run')).decode('utf8')
        # run_id = client.get(domainJoin('runId')).decode('utf8')
        status = client.get(domainJoin('status')).decode('utf8').lower()
        started = float((client.get(domainJoin('startTime')) or b'0').decode('utf8'))
        stopped = float((client.get(domainJoin('endTime')) or b'0').decode('utf8'))
        active = bool(status == 'active')
        if active:
            runtime = time()-started
        else:
            runtime = stopped-started
        if run:
            def get(*args):
                return client.get(domainJoin(*args))
            island_ids = [i for i in loads(get('islandIds') or '[]')]

            pp = PrettyPrinter(indent=2)

            v = int(screen.height/2)-10
            screen.print_at('Run {}    '.format(run),
                            int(screen.width/2)-65, v,
                            Screen.COLOUR_WHITE)
            v += 1
            screen.print_at('Status: {}    '.format(status.upper()),
                            int(screen.width/2)-65, v,
                            Screen.COLOUR_GREEN if status == 'active' else Screen.COLOUR_WHITE if status == 'finished' else Screen.COLOUR_RED)
            v += 1
            screen.print_at('Run time: {:.0f} s    '.format(runtime),
                            int(screen.width/2)-65, v,
                            Screen.COLOUR_GREEN if status == 'active' else Screen.COLOUR_WHITE if status == 'finished' else Screen.COLOUR_RED)
            v += 1
            screen.print_at('Islands ({}):'.format(len(island_ids)),
                            int(screen.width/2)-65, v,
                            Screen.COLOUR_WHITE)
            v += 1
            for i in island_ids:
                screen.print_at(i, int(screen.width/2)-55, v, Screen.COLOUR_WHITE)
                round = (client.get(domainJoin('island',i,'round')) or b'?').decode('utf8')
                screen.print_at('    ', int(screen.width/2)+15, v, Screen.COLOUR_WHITE)
                screen.print_at(round, int(screen.width/2)+15, v, Screen.COLOUR_WHITE)\
                # best score
                best_f = (client.get(domainJoin('island',i,'best_f')) or b'?').decode('utf8')
                screen.print_at(' '*6, int(screen.width/2)+21, v, Screen.COLOUR_WHITE)
                screen.print_at(best_f, int(screen.width/2)+21, v, Screen.COLOUR_WHITE)
                v+=1
        else:
            screen.print_at('No run id'.format(run),
                            0, 0,
                            colour=Screen.COLOUR_WHITE)
        ev = screen.get_key()
        if ev in (ord('Q'), ord('q')):
            return
        screen.refresh()
        sleep(1)

class BenchmarkLauncherBase:
    '''
    The base class for all timecourse benchmarks which handles initialization of Spark
    configs and algorithmic parameters, including the island topology, migration settings,
    and selection / replacement policies.
    '''
    def __init__(self):
        self.run_id = str(uuid4())
        self.problem = None
        self.udp_constructor = None

    def _initialize_spark(self, app_name, spark_files, py_files):
        '''
        Sets up the Spark config to bundle all Python scripts and SBML files
        necessary to run the problem.
        '''
        from os.path import join
        self.spark_conf = SparkConf().setAppName(app_name)
        self.spark_conf.setMaster('spark://{}:{}'.format(self.hostname,self.port))
        self.spark_conf.set('spark.driver.memory', '1g')
        # examples of other inportant config variables
        #self.spark_conf.set('spark.executor.memory', '2g')
        #self.spark_conf.set('spark.executor.cores', '4')
        #self.spark_conf.set('spark.cores.max', '40')

        self.spark_conf.set('spark.files', ','.join((spark_files,py_files)))
        # set py files
        self.spark_conf.set('spark.submit.pyFiles', py_files)
        self.spark_conf.set('spark.logConf', True)

        # after setting up the Spark config, instantiate the Spark context
        self.spark_context = SparkContext(conf=self.spark_conf)


    @classmethod
    def _create_arg_parser(cls):
        import argparse
        parser = argparse.ArgumentParser(description='Run the B2 problem.')
        parser.add_argument('command',
                            help='The command. Can be "run" or "count-params".')
        parser.add_argument('--host', metavar='hostname', required=True,
                            help='The hostname of the master node of the spark cluster with optional port, e.g. localhost:7077')
        parser.add_argument('--metric-host', required=True,
                            help='The host of the metric processor (InfluxDB) with optional port, e.g. localhost:8086')
        parser.add_argument('--topology',
                            help='The topology to use.')
        parser.add_argument('--num-islands', type=int, # not used if reading from a database / file
                            help='The number of islands in the topology (if not reading from a file or database).')
        parser.add_argument('--migration', required=True,
                            choices = [
                              'none', 'null',
                              'central', 'central-migrator',
                              'kafka', 'kafka-migrator',
                            ],
                            help='The migration scheme to use.')
        parser.add_argument('--migration-host', required=True,
                            help='The migration host.')
        parser.add_argument('--migration-policy', required=True,
                            choices = [
                              'none', 'null',
                              'each', 'each-to-all',
                              'uniform',
                            ],
                            help='The migration policy to use.')
        parser.add_argument('--selection-policy', required=True,
                            choices = [
                              'best-s-policy', 'best',
                            ],
                            help='The selection policy to use')
        parser.add_argument('--selection-rate', type=int,
                            help='The migration rate used in the selection policy (exclusive with --selection-fraction).')
        parser.add_argument('--selection-fraction', type=float,
                            help='The population used in the selection policy (exclusive with --selection-rate).')
        parser.add_argument('--replacement-policy', required=True,
                            choices = [
                              'fair-r-policy', 'fair',
                            ],
                            help='The replacement policy to use.')
        parser.add_argument('--suite-run-id', required=True,
                            help='The id of this run, used for indexing. Shared with rest of suite.')
        parser.add_argument('--rounds', type=int, default=10,
                            help='The number of rounds of migrations to perform.')
        parser.add_argument('--description', required=True,
                            help='A description of the topology used.')
        parser.add_argument('--validation-mode', type=bool, default=False,
                            help='If true, run in validation mode.')
        parser.add_argument('--validation-points', type=int, default=0,
                            help='If in validation mode, the number of points for the reference simulation.')
        parser.add_argument('--use-pool', type=bool, default=False,
                            help='Use a pool of processes or a thread pool (better performance for compatible problems).')
        return parser


    @classmethod
    def from_cmdline_args(cls, app_name, spark_files, py_files):
        '''
        Initializes the run configuration from command line arguments.
        '''
        config = cls()
        parser = cls._create_arg_parser()
        args = parser.parse_args()
        config.args = args
        from re import match
        if not match(r'[^: ](:[\d]+)?', args.host):
            raise RuntimeError('Expected host name to be either a name or name:port')
        if not ':' in args.host:
            config.hostname = args.host
            config.port = 7077
        else:
            config.hostname,config.port = args.host.split(':')
        if not ':' in args.metric_host:
            config.metric_host = args.metric_host
            config.metric_port = 8086
        else:
            config.metric_host,config.metric_port = args.metric_port.split(':')
        config.topology_name = args.topology
        config.migrator_name = args.migration
        config.migration_host = args.migration_host
        config.migration_policy = cls.select_migration_policy(args.migration_policy)
        if args.selection_rate is not None and args.selection_fraction is not None:
            raise RuntimeError('Specify either --selection-rate or --selection-fraction, not both')
        if args.selection_rate is not None:
            config.selection_policy = cls.select_selection_policy(args.selection_policy, migration_rate=args.selection_rate)
        elif args.selection_fraction is not None:
            config.selection_policy = cls.select_selection_policy(args.selection_policy, pop_fraction=args.selection_fraction)
        else:
            raise RuntimeError('Specify either --selection-rate or --selection-fraction')
        config.replacement_policy = cls.select_replacement_policy(args.replacement_policy)
        config.suite_run_id = args.suite_run_id
        config.rounds = args.rounds
        config.description = args.description
        config.generations = None
        config.validation_mode = args.validation_mode
        config.validation_points = args.validation_points
        config.use_pool = args.use_pool
        config.command = args.command

        config._initialize_spark(app_name, spark_files, py_files)

        return config


    def generate_archipelago(self, topology_name, metric, monitor):
        from os.path import isfile
        from re import compile
        db_regex = compile(r'sql:(\w+)@([\w:]+),pw=([^,]+),db=([\w]+)\(name=(\w+),n_islands=(\d+),island_size=(\d+),migrant_pool_size=(\d+),generations=(\d+)\):(.*)')
        if isfile(topology_name):
            import pickle
            with open(topology_name) as f:
                return pickle.load(f)['archipelago']
        elif db_regex.match(topology_name) is not None:
            m = db_regex.match(topology_name)
            from sabaody import TopologyGenerator, BiopredynTopologyGenerator
            name = m.group(5)
            if name == 'pagmo':
                generator_class = TopologyGenerator
            elif name == 'biopredyn':
                generator_class = BiopredynTopologyGenerator
            generator = generator_class(
                n_islands = int(m.group(6)),
                island_size = int(m.group(7)),
                migrant_pool_size = int(m.group(8)),
                generations = int(m.group(9)))
            topology,id = generator.find_in_database(
                desc = m.group(10),
                user = m.group(1),
                host = m.group(2),
                pw   = m.group(3),
                db   = m.group(4))
            self.topology_set_id = id
            self.topology_id = topology['id']
            self.generations = topology['generations']
            return Archipelago(TopologyFactory.prefixIds(topology['archipelago'].topology, prefix=self.run_id+'-'))
        else:
            # generate the topology from available presets via command line arguments
            topology_factory = TopologyFactory(problem=self.make_problem(),
                                              island_size=self.island_size,
                                              migrant_pool_size=self.migrant_pool_size,
                                              domain_qualifier=monitor.getNameQualifier(),
                                              mc_host=monitor.mc_host,
                                              mc_port=monitor.mc_port)
            if topology_name == 'ring' or topology_name == 'bidir-ring':
                return Archipelago(topology_factory.createBidirRing(self.make_algorithm(),self.n_islands), metric)
            elif topology_name == 'one-way-ring':
                return Archipelago(topology_factory.createOneWayRing(self.make_algorithm(),self.n_islands), metric)
            else:
                raise RuntimeError('Unrecognized topology')


    @classmethod
    def select_migration_policy(cls, policy_name):
        from sabaody.migration import MigrationPolicyEachToAll, MigrationPolicyUniform
        if policy_name == 'each' or policy_name == 'each-to-all':
            return MigrationPolicyEachToAll()
        elif policy_name == 'uniform':
            return MigrationPolicyUniform()
        else:
            raise RuntimeError('Unknown migration policy')


    @classmethod
    def select_selection_policy(cls, policy_name, migration_rate=None, pop_fraction=None):
        from sabaody.migration import BestSPolicy
        if policy_name == 'best-s-policy' or policy_name == 'best':
            if migration_rate is not None and pop_fraction is not None:
                raise RuntimeError('Specify either migration rate or fraction, not both')
            if migration_rate is not None:
                return BestSPolicy(migration_rate=migration_rate)
            elif pop_fraction is not None:
                return BestSPolicy(pop_fraction=pop_fraction)
            else:
                raise RuntimeError('Neither migration rate nor fraction specified')
        else:
            raise RuntimeError('Unknown selection policy')


    @classmethod
    def select_replacement_policy(cls, policy_name):
        from sabaody.migration import FairRPolicy
        if policy_name == 'fair-r-policy' or policy_name == 'fair':
            return FairRPolicy()
        else:
            raise RuntimeError('Unknown replacement policy')


    def select_migrator(self, migrator_name, migration_policy, selection_policy, replacement_policy):
        if migrator_name == 'central' or migrator_name == 'central-migrator':
            from sabaody.migration_central import CentralMigrator
            # central migrator process must be running
            print('using central migrator at {}'.format(self.migration_host))
            return CentralMigrator(migration_policy, selection_policy, replacement_policy, self.migration_host)
        elif migrator_name == 'kafka' or migrator_name == 'kafka-migrator':
            from sabaody.kafka_migration_service import KafkaMigrator, KafkaBuilder
            # Kafka must be running
            return KafkaMigrator(selection_policy, replacement_policy, KafkaBuilder('luna', 9092)) # FIXME: hardcoded
        else:
            raise RuntimeError('Migration scheme undefined')


    def create_metric(self, prefix):
        metric = InfluxDBMetric(host=self.metric_host, port=self.metric_port, database=prefix+self.run_id)
        print ('using influxdb database {}'.format(metric.database))
        return metric


    def calculateInitialScore(self):
        with open(self.sbmlfile) as f:
            sbml = f.read()

            # show initial score
            self.initial_score = self.udp.evaluate(self.getDefaultParamValues())
            print('Initial score: {}'.format(self.initial_score))


    def run_command(self, command):
        if command == 'count-params':
            print('Number of parameters: {}'.format(len(p = self.udp.getParameterNames())))
        else:
            return super().run_command(command)


    def run_command(self, command):
        if command == 'run' or command == 'run-islands':
            if self.udp_constructor is not None:
                self.udp = self.udp_constructor(self.validation_mode, self.validation_points)
            return self.run_islands()
        else:
            raise RuntimeError('Unrecognized command: {}'.format(command))


    def run_islands(self):
        with self.monitor(
            name=self.app_name,
            host='luna',
            port=11211,
            run=self.suite_run_id,
            ) as monitor: # FIXME: hard-coded
            with self.create_metric(monitor.getDomain()+'.') as metric:
                import arrow
                time_start = arrow.utcnow()

                # set up topology parameters
                from sabaody.topology import TopologyFactory

                # instantiate algorithm and topology
                a = self.generate_archipelago(self.topology_name, metric, monitor)

                # select migrator
                # assumes the migrator process / service has already been started
                migrator = self.select_migrator(self.migrator_name,
                                                self.migration_policy,
                                                self.selection_policy,
                                                self.replacement_policy)
                from sabaody.migration_central import CentralMigrator
                if isinstance(migrator, CentralMigrator):
                    if self.udp is not None:
                        l = len(self.udp.get_bounds()[0])
                    elif self.problem is not None:
                        l = len(self.problem.get_bounds()[0])
                    migrator.defineMigrantPools(a.topology, l)

                a.monitor = monitor
                a.metric = metric
                a.monitor_island_ids()
                results = a.run(sc=self.spark_context, migrator=migrator, udp=self.udp, rounds=self.rounds, use_pool=self.use_pool, problem=self.problem, terminator=self.terminator)
                champions = sorted([(f[0],x) for f,x,r in results], key=lambda t: t[0])
                champion_scores = [f for f,x in champions]
                rounds = [r for f,x,r in results]

                best_score,best_candidate = champions[0]
                average_score = float(sum(champion_scores))/len(champion_scores)
                time_end = arrow.utcnow()

                self.commit_results_to_database(
                    host='luna',
                    user='sabaody',
                    database='sabaody',
                    password='w00t',
                    max_rounds=self.rounds,
                    generations=self.generations,
                    n_islands=len(a.topology.islands),
                    island_size=a.topology.islands[0].size,
                    champions=champions,
                    min_score=best_score,
                    average_score=average_score,
                    actual_rounds=rounds,
                    validation_mode=self.validation_mode,
                    validation_points=self.validation_points,
                    time_start=time_start,
                    time_end=time_end,
                    metric_id = metric.database)

                print('min champion score {}'.format(best_score))
                print('mean champion score {}'.format(average_score))
                print('Total run time: {}'.format(time_start.humanize()))
                print('Rounds: {}'.format(rounds))


    def commit_results_to_database(self, host, user, database, password, max_rounds, generations, n_islands, island_size, champions, min_score, average_score, actual_rounds, validation_mode, validation_points, time_start, time_end, metric_id):
        import MySQLdb
        mariadb_connection = MySQLdb.connect(host,user,password,database)
        cursor = mariadb_connection.cursor()
        from pickle import dumps
        import json
        # cursor.execute(
        #     "DELETE FROM benchmark_runs WHERE (Benchmark, RunID, Description)=('{benchmark}',{suite_run_id},'{description}');".format(
        #         benchmark=self.app_name,
        #         suite_run_id=self.suite_run_id,
        #         description=self.description,
        #     ))
        # mariadb_connection.commit()
        query = '\n'.join([
            'INSERT INTO benchmark_runs (Benchmark, RunID, MetricID, Description, TopologyID, MaxRounds, Generations, NumIslands, IslandSize, Champions, MinScore, AverageScore, ActualRounds, ActualAvgRounds, ValidationMode, ValidationPoints, TimeStart, TimeEnd)',
            "VALUES ('{benchmark}','{run_id}','{metric_id}','{description}','{topologyid}',{max_rounds},{generations},{n_islands},{island_size},{champions},{min_score},{average_score},'{actual_rounds}',{actual_avg_rounds},{validation_mode},{validation_points},'{time_start}','{time_end}');".format(
                benchmark=self.app_name,
                run_id=self.run_id,
                metric_id=metric_id,
                description=self.description,
                topologyid=self.topology_id,
                max_rounds=max_rounds,
                generations=generations,
                n_islands=n_islands,
                island_size=island_size,
                champions='0x{}'.format(dumps(champions).hex()),
                min_score=min_score,
                average_score=average_score,
                actual_rounds=json.dumps(actual_rounds),
                actual_avg_rounds=float(mean(array(actual_rounds))),
                validation_mode=validation_mode*1,
                validation_points=validation_points,
                time_start=time_start.format('YYYY-MM-DD HH:mm:ss'),
                time_end=time_end.format('YYYY-MM-DD HH:mm:ss'),
                )])
        # print(query)
        cursor.execute(query)
        mariadb_connection.commit()
