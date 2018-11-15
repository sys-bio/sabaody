from __future__ import print_function, division, absolute_import

from sabaody.problem_setup import MemcachedMonitor, TimecourseRunConfiguration

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

class BiopredynConfiguration(TimecourseRunConfiguration):
    @classmethod
    def from_cmdline_args(cls, app_name, sbmlfile, script_dir, udp, getDefaultParamValues):
        from os.path import join, abspath

        # set files to be copied to the cwd of each executor
        spark_files = ','.join(join(script_dir,p) for p in [
            abspath(join('..','..','..','..','..','sbml','b2.xml')),
            ])
        py_files = ','.join(join(script_dir,p) for p in [
            'data.py',
            'b2problem.py',
            'params.py',
            ])
        py_files += ','+join(script_dir,'..','benchsetup.py')

        result = super(BiopredynConfiguration,cls).from_cmdline_args(app_name, spark_files, py_files)
        result.app_name = app_name
        result.sbmlfile = sbmlfile
        result.udp = udp
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


    def commit_results_to_database(self, host, user, database, password, champion_scores, min_score, average_score, time_start, time_end):
        import MySQLdb
        mariadb_connection = MySQLdb.connect(host,user,password,database)
        cursor = mariadb_connection.cursor()
        from pickle import dumps
        cursor.execute(
            "DELETE FROM benchmark_runs WHERE (Benchmark, SuiteRunID, Description)=('{benchmark}',{suite_run_id},'{description}');".format(
                benchmark=self.app_name,
                suite_run_id=self.suite_run_id,
                description=self.description,
            ))
        mariadb_connection.commit()
        cursor.execute('\n'.join([
            'INSERT INTO benchmark_runs (Benchmark, SuiteRunID, Description, TopologyID, ChampionScores, MinScore, AverageScore, TimeStart, TimeEnd)',
            "VALUES ('{benchmark}',{suite_run_id},'{description}','{topologyid}',{champion_scores},{min_score},{average_score},'{time_start}','{time_end}');".format(
                benchmark=self.app_name,
                suite_run_id=self.suite_run_id,
                description=self.description,
                topologyid=self.topology_id,
                champion_scores='0x{}'.format(dumps(champion_scores).hex()),
                min_score=min_score,
                average_score=average_score,
                time_start=time_start.format('YYYY-MM-DD HH:mm:ss'),
                time_end=time_end.format('YYYY-MM-DD HH:mm:ss'),
                )]))
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
                champion_scores = a.run(self.spark_context, migrator, self.udp, self.rounds)

                min_score = min(champion_scores)
                average_score = float(sum(champion_scores))/len(champion_scores)
                time_end = arrow.utcnow()

                # self.serialize_results(output, champion_scores, min_score, average_score, time_start, time_end)
                self.commit_results_to_database(
                    host='luna',
                    user='sabaody',
                    database='sabaody',
                    password='w00t',
                    champion_scores=champion_scores,
                    min_score=min_score,
                    average_score=average_score,
                    time_start=time_start,
                    time_end=time_end)

                print('chamption scores {}'.format(champion_scores))
                print('min champion score {}'.format(min_score))
                print('mean champion score {}'.format(average_score))
                print('Total run time: {}'.format(time_start.humanize()))


    def calculateInitialScore(self):
        with open(self.sbmlfile) as f:
            sbml = f.read()

        # show initial score
        self.initial_score = self.udp.evaluate(self.getDefaultParamValues())
        print('Initial score: {}'.format(self.initial_score))


    def run_command(self, command):
        if command == 'count-params':
            with open(self.sbmlfile) as f:
                sbml = f.read()
                from b2problem import B2Problem
                print('Number of parameters: {}'.format(len(
        p = self.udp.getParameterNames())))
        else:
            return super().run_command(command)
