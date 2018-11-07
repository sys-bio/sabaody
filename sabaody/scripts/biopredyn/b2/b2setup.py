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
    def __init__(self, name, host, port):
        super().__init__(host, port)
        self.name = name

    def getName(self):
        return self.name

    def getDomain(self):
        return 'com.how2cell.sabaody.biopredyn.{}'.format(self.getName())

class BiopredynConfiguration(TimecourseRunConfiguration):
    @classmethod
    def from_cmdline_args(cls, name, sbmlfile, problem_class, getDefaultParamValues):
        from os.path import join, abspath, dirname, realpath
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

        result = super(BiopredynConfiguration,cls).from_cmdline_args('b2-driver', spark_files, py_files)
        result.sbmlfile = sbmlfile
        result.problem_class = problem_class
        result.getDefaultParamValues = getDefaultParamValues
        return result


    def monitor(self, host, port):
        return BiopredynMCMonitor(name, host, port)


    def make_problem(self):
        from b2problem import B2_UDP, getLowerBound, getUpperBound
        import pygmo as pg
        return pg.problem(B2_UDP(getLowerBound(),getUpperBound()))


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


    def run_islands(self, output):
        with self.monitor('luna', 11211) as monitor:
            with self.create_metric(monitor.getDomain()+'.') as metric:
                import arrow
                time_start = arrow.utcnow()

                # set up topology parameters
                from sabaody.topology import TopologyFactory
                topology_factory = TopologyFactory(problem=self.make_problem(),
                                                  island_size=self.island_size,
                                                  migrant_pool_size=self.migrant_pool_size,
                                                  domain_qualifier=monitor.getNameQualifier(),
                                                  mc_host=monitor.mc_host,
                                                  mc_port=monitor.mc_port)

                # instantiate algorithm and topology
                a = self.generate_archipelago(self.topology_name, topology_factory, metric)

                # select migration policy
                migration_policy = self.select_migration_policy(self.migration_policy_name)
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
                champion_scores = a.run(self.spark_context, migrator, 10)

                min_score = min(champion_scores)
                average_score = float(sum(champion_scores))/len(champion_scores)
                time_end = arrow.utcnow()

                self.serialize_results(output, champion_scores, min_score, average_score, time_start, time_end)

                print('chamption scores {}'.format(champion_scores))
                print('min champion score {}'.format(min_score))
                print('mean champion score {}'.format(average_score))
                print('Total run time: {}'.format(time_start.humanize()))


    def calculateInitialScore(self):
        with open(self.sbmlfile) as f:
            sbml = f.read()

        # show initial score
        p = self.problem_class(sbml)
        self.initial_score = p.evaluate(self.getDefaultParamValues())
        print('Initial score: {}'.format(self.initial_score))


    def run_command(self, command):
        if command == 'count-params':
            with open(self.sbmlfile) as f:
                sbml = f.read()
                from b2problem import B2Problem
                print('Number of parameters: {}'.format(len(
        p = self.problem_class(sbml).getParameterNames())))
        else:
            return super().run_command(command)