# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from airflow.operators.python_operator import PythonOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator

def topology_generator(n_islands, island_size, migrant_pool_size, generations):
            from sabaody import TopologyGenerator
            import MySQLdb
            mariadb_connection = MySQLdb.connect('luna','sabaody','w00t','sabaody')
            cursor = mariadb_connection.cursor()

            generator = TopologyGenerator(island_size=island_size, migrant_pool_size=migrant_pool_size, generations=generations)
            major,minor,patch = generator.get_version()
            cursor.execute('SELECT COUNT(*) FROM topology_sets WHERE '+\
                '(VersionMajor, VersionMinor, VersionPatch, NumIslands, IslandSize, MigrantPoolSize, Generations) = '+\
                '({major}, {minor}, {patch}, {n_islands}, {island_size}, {migrant_pool_size},{generations});'.format(
                major=major,
                minor=minor,
                patch=patch,
                n_islands=n_islands,
                island_size=island_size,
                migrant_pool_size=migrant_pool_size,
                generations=generations,
            ))
            x = cursor.fetchone()
            n_matches = int(x[0])
            # print('n_matches', n_matches)

            # if this version is already stored, do nothing
            if n_matches == 0:
                serialized_topologies = generator.serialize(n_islands)
                # store in database
                cursor.execute('\n'.join([
                    'INSERT INTO topology_sets (TopologySetID, VersionMajor, VersionMinor, VersionPatch, NumIslands, IslandSize, MigrantPoolSize, Generations, Content)',
                    'VALUES ({id},{major},{minor},{patch},{n_islands},{island_size},{migrant_pool_size},{generations},{content});'.format(
                        id="'topology_set({})'".format(generator.get_version_string()),
                        major=major,
                        minor=minor,
                        patch=patch,
                        n_islands=n_islands,
                        island_size=island_size,
                        migrant_pool_size=migrant_pool_size,
                        generations=generations,
                        content="0x{}".format(serialized_topologies.hex()),
                        )]))
                mariadb_connection.commit()


def legalize_name(name):
    '''
    Convert a string into a task id for airflow.
    '''
    result = ''
    from re import compile
    r = compile('[\w]')
    for c in name:
        if r.match(c) is not None:
            result += c
        else:
            result += '_'
    return result


class TaskFactory():
    def create(self, dag):
        n_islands = 10
        island_size = 10
        migrant_pool_size = 2
        generations = 10 # ideally same as island_size

        # first, make sure the SQL tables exist
        self.setup_tables = MySqlOperator(
            task_id='setup_tables',
            database='sabaody',
            sql='''
                CREATE TABLE IF NOT EXISTS topology_sets (
                  PrimaryKey INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                  TopologySetID VARCHAR(255) NOT NULL,
                  VersionMajor INT NOT NULL,
                  VersionMinor INT NOT NULL,
                  VersionPatch INT NOT NULL,
                  NumIslands INT NOT NULL,
                  IslandSize INT NOT NULL,
                  MigrantPoolSize INT NOT NULL,
                  Generations INT NOT NULL,
                  Content BLOB NOT NULL);
                CREATE TABLE IF NOT EXISTS benchmark_runs (
                  PrimaryKey INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                  Benchmark VARCHAR(255) NOT NULL,
                  SuiteRunID INT NOT NULL,
                  Description TEXT NOT NULL,
                  TopologyID VARCHAR(255) NOT NULL,
                  ChampionScores BLOB NOT NULL,
                  MinScore DOUBLE NOT NULL,
                  AverageScore DOUBLE NOT NULL,
                  TimeStart DATETIME NOT NULL,
                  TimeEnd DATETIME NOT NULL);''',
          dag=dag)

        # store the topologies in the table
        self.generate_topologies = PythonOperator(
            task_id='generate_topologies',
            python_callable=topology_generator,
            op_kwargs={
                'n_islands': n_islands,
                'island_size': island_size,
                'migrant_pool_size': migrant_pool_size,
                'generations': generations},
            dag=dag)

        self.setup_tables >> self.generate_topologies

        # for each topology, create a benchmark task
        self.benchmarks = []
        from sabaody import TopologyGenerator
        generator = TopologyGenerator(island_size=island_size, migrant_pool_size=migrant_pool_size)
        topologies = generator.generate_all(n_islands)

        for topology in topologies:
            # https://stackoverflow.com/questions/49957464/apache-airflow-automation-how-to-run-spark-submit-job-with-param
            self.benchmarks.append(SparkSubmitOperator(
                task_id=legalize_name(topology['description']),
                conf={
                    'spark.cores.max': 5,
                    'spark.executor.cores': 1,
                },
                application_args=[
                    '--topology sql:sabaody@luna,pw=w00t,db=sabaody,version={version}(n_islands={n_islands},island_size={island_size},migrant_pool_size={migrant_pool_size},generations={generations}):"{desc}"'.format(
                        version=TopologyGenerator.get_version_string(),
                        n_islands=n_islands,
                        island_size=island_size,
                        migrant_pool_size=migrant_pool_size,
                        generations=generations,
                        desc=topology['description'],
                    ),
                    '--migration central',
                    '--migration-policy uniform',
                    '--rounds 100',
                    '--description "{}"'.format(topology['description']),
                ],
                dag=dag,
                **{
                    'deploy-mode' : 'client'
                },
            ))
            self.generate_topologies >> self.benchmarks[-1]