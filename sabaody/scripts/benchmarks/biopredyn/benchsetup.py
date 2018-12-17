from __future__ import print_function, division, absolute_import

from sabaody.timecourse.timecourse_launcher import MemcachedMonitor, TimecourseSimLauncher

import json

# some refs:
#https://developerzen.com/best-practices-writing-production-grade-pyspark-jobs-cb688ac4d20f
#https://medium.com/@mrpowers/creating-a-pyspark-project-with-pytest-pyenv-and-egg-files-d2709eb1604c

class BiopredynMCMonitor(MemcachedMonitor):
    '''
    Abstracts some of the logic of setting up a parameter fitting problem.
    Provides information via MC for monitoring.
    '''

    def getDomain(self):
        return 'com.how2cell.sabaody.biopredyn.{}'.format(self.getName())


    def getNameQualifier(self):
        from toolz import partial
        from sabaody import getQualifiedName
        return partial(getQualifiedName, 'biopredyn', self.getName(), str(self.run))

class BiopredynConfiguration(TimecourseSimLauncher):
    @classmethod
    def from_cmdline_args(cls, app_name, sbmlfile, script_dir, udp_constructor, getDefaultParamValues):
        from os.path import join, abspath

        # set files to be copied to the cwd of each executor
        spark_files = ','.join(join(script_dir,p) for p in [
            abspath(join('..','..','..','..','..','sbml','b2.xml')),
            ])
        py_files = ','.join(join(script_dir,p) for p in [
            'data.py',
            'b2problem.py',
            'b2problem_validator.py',
            'params.py',
            ])
        py_files += ','+join(script_dir,'..','benchsetup.py')

        result = super(BiopredynConfiguration,cls).from_cmdline_args(app_name, spark_files, py_files)
        result.app_name = app_name
        result.sbmlfile = sbmlfile
        result.udp_constructor = udp_constructor
        result.getDefaultParamValues = getDefaultParamValues
        return result


    def monitor(self, name, host, port, run=None):
        return BiopredynMCMonitor(name, host, port, run=None)


    def serialize_results(self, filename, champion_scores, min_score, average_score, time_start, time_end):
        results = {
                  'champion_scores': champion_scores,
                  'min_champion_score': min_score,
                  'mean_champion_score': average_score,
                  'total_run_time': (time_start-time_end)
                  }
        with open(filename,'w') as f:
            json.dump(results)


    def deserialize_results(self, filename):
        with open(filename,'w') as f:
            return json.load(f)


    def commit_results_to_database(self, host, user, database, password, rounds, generations, champions, min_score, average_score, validation_mode, validation_points, time_start, time_end, metric_id):
        import MySQLdb
        mariadb_connection = MySQLdb.connect(host,user,password,database)
        cursor = mariadb_connection.cursor()
        from pickle import dumps
        # cursor.execute(
        #     "DELETE FROM benchmark_runs WHERE (Benchmark, RunID, Description)=('{benchmark}',{suite_run_id},'{description}');".format(
        #         benchmark=self.app_name,
        #         suite_run_id=self.suite_run_id,
        #         description=self.description,
        #     ))
        # mariadb_connection.commit()
        query = '\n'.join([
            'INSERT INTO benchmark_runs (Benchmark, RunID, MetricID, Description, TopologyID, Rounds, Generations, Champions, MinScore, ValidationMode, ValidationPoints, AverageScore, TimeStart, TimeEnd)',
            "VALUES ('{benchmark}','{run_id}','{metric_id}','{description}','{topologyid}',{rounds},{generations},{champions},{min_score},{average_score},{validation_mode},{validation_points},'{time_start}','{time_end}');".format(
                benchmark=self.app_name,
                run_id=self.run_id,
                metric_id=metric_id,
                description=self.description,
                topologyid=self.topology_id,
                rounds=rounds,
                generations=generations,
                champions='0x{}'.format(dumps(champions).hex()),
                min_score=min_score,
                average_score=average_score,
                validation_mode=validation_mode,
                validation_points=validation_points,
                time_start=time_start.format('YYYY-MM-DD HH:mm:ss'),
                time_end=time_end.format('YYYY-MM-DD HH:mm:ss'),
                )])
        print(query)
        cursor.execute(query)
        mariadb_connection.commit()


    def run_islands(self):
        with self.monitor(self.app_name, 'luna', 11211, self.suite_run_id) as monitor:
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
                    migrator.defineMigrantPools(a.topology, 116)

                a.set_mc_server(monitor.mc_host, monitor.mc_port, monitor.getNameQualifier())
                a.monitor = monitor
                a.metric = metric
                results = a.run(self.spark_context, migrator, self.udp, self.rounds)
                champions = sorted([(f[0],x) for f,x in results], key=lambda t: t[0])
                champion_scores = [f for f,x in champions]

                best_score,best_candidate = champions[0]
                average_score = float(sum(champion_scores))/len(champion_scores)
                time_end = arrow.utcnow()

                # self.serialize_results(output, champion_scores, best_score, average_score, time_start, time_end)
                self.commit_results_to_database(
                    host='luna',
                    user='sabaody',
                    database='sabaody',
                    password='w00t',
                    rounds=self.rounds,
                    generations=self.generations,
                    champions=champions,
                    min_score=best_score,
                    average_score=average_score,
                    validation_mode=self.validation_mode,
                    validation_points=self.validation_points,
                    time_start=time_start,
                    time_end=time_end,
                    metric_id = metric.database)

                print('min champion score {}'.format(best_score))
                print('mean champion score {}'.format(average_score))
                print('Total run time: {}'.format(time_start.humanize()))



class BioPreDynUDP:
    def __init__(self, lb, ub, sbml_file):
        # type: (Evaluator, array, array) -> None
        '''
        Inits the problem with an objective evaluator
        (implementing the method evaluate), the parameter
        vector lower bound (a numpy array) and upper bound.
        Both bounds must have the same dimension.
        '''
        from sabaody.utils import check_vector, expect
        check_vector(lb)
        check_vector(ub)
        expect(len(lb) == len(ub), 'Bounds mismatch')
        self.lb = lb
        self.ub = ub
        # delay loading until we're on the worker node
        self.evaluator = None
        self.sbml_file = sbml_file


    # derived classes need method 'fitness'


    def get_bounds(self):
        return (self.lb,self.ub)


    def get_name(self):
        return 'Sabaody udp'


    def get_extra_info(self):
        return 'Sabaody extra info'


    def __getstate__(self):
        return {
          'lb': self.lb,
          'ub': self.ub,
          'sbml_file': self.sbml_file}


    def __setstate__(self, state):
        self.lb = state['lb']
        self.ub = state['ub']
        self.sbml_file = state['sbml_file']
        # lazy init
        self.evaluator = None
