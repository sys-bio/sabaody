# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from airflow.operators.python_operator import PythonOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from os.path import join

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 11, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}

all_benchmarks_dag = DAG(
  'all_benchmarks',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))

root_path = '/opt/nfs/src/sabaody/sabaody/scripts/benchmarks/biopredyn'

b1_dag = DAG(
  'b1_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
TaskFactory().generate(b1_dag, join(root_path,'b1','b1-driver.py'))
TaskFactory().generate(all_benchmarks_dag, join(root_path,'b1','b1-driver.py'))

b2_dag = DAG(
  'b2_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
TaskFactory().generate(b2_dag, join(root_path,'b2','b2-driver.py'))
TaskFactory().generate(all_benchmarks_dag, join(root_path,'b2','b2-driver.py'))

b3_dag = DAG(
  'b3_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
TaskFactory().generate(b2_dag, join(root_path,'b3','b3-driver.py'))
TaskFactory().generate(all_benchmarks_dag, join(root_path,'b3','b3-driver.py'))

b4_dag = DAG(
  'b4_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
TaskFactory().generate(b4_dag, join(root_path,'b4','b4-driver.py'))
TaskFactory().generate(all_benchmarks_dag, join(root_path,'b4','b4-driver.py'))


def topology_generator(n_islands, island_size, migrant_pool_size, generations):
            from sabaody import TopologyGenerator
            import MySQLdb
            mariadb_connection = MySQLdb.connect('luna','sabaody','w00t','sabaody')
            cursor = mariadb_connection.cursor()

            generator = TopologyGenerator(n_islands=n_islands, island_size=island_size, migrant_pool_size=migrant_pool_size, generations=generations)
            checksum = generator.get_checksum()
            cursor.execute('SELECT COUNT(*) FROM topology_sets WHERE '+\
                '(Checksum, NumIslands, IslandSize, MigrantPoolSize, Generations) = '+\
                "({checksum}, {n_islands}, {island_size}, {migrant_pool_size},{generations});".format(
                checksum=checksum,
                n_islands=n_islands,
                island_size=island_size,
                migrant_pool_size=migrant_pool_size,
                generations=generations,
            ))
            x = cursor.fetchone()
            n_matches = int(x[0])

            # if this version is already stored, do nothing
            if n_matches == 0:
                serialized_topologies = generator.serialize()
                # store in database
                cursor.execute('\n'.join([
                    'INSERT INTO topology_sets (TopologySetID, Checksum, NumIslands, IslandSize, MigrantPoolSize, Generations, Content)',
                    'VALUES ({id},{checksum},{n_islands},{island_size},{migrant_pool_size},{generations},{content});'.format(
                        id="'topology_set({})'".format(generator.get_version_string()),
                        checksum=checksum,
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


class TaskGenerator():
    def __init__(self):
        # first, make sure the SQL tables exist
        self.setup_topology_sets_table = MySqlOperator(
            task_id='setup_topology_sets_table',
            database='sabaody',
            sql='''
                CREATE TABLE IF NOT EXISTS topology_sets (
                    PrimaryKey INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                    TopologySetID VARCHAR(255) NOT NULL,
                    Checksum INT NOT NULL,
                    NumIslands INT NOT NULL,
                    IslandSize INT NOT NULL,
                    MigrantPoolSize INT NOT NULL,
                    Generations INT NOT NULL,
                    Content MEDIUMBLOB NOT NULL);''',
            dag=dag)

        # first, make sure the SQL tables exist
        self.setup_benchmark_results_table = MySqlOperator(
            task_id='setup_benchmark_results_table',
            database='sabaody',
            sql='''
                CREATE TABLE IF NOT EXISTS benchmark_runs (
                    PrimaryKey INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                    Benchmark VARCHAR(255) NOT NULL,
                    RunID VARCHAR(255) NOT NULL,
                    MetricID VARCHAR(255) NOT NULL,
                    Description TEXT NOT NULL,
                    TopologyID VARCHAR(255) NOT NULL,
                    Rounds INT,
                    Generations INT,
                    Champions BLOB NOT NULL,
                    MinScore DOUBLE NOT NULL,
                    AverageScore DOUBLE NOT NULL,
                    ValidationMode INT NOT NULL,
                    ValidationPoints INT NOT NULL,
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

        self.setup_topology_sets_table >> self.generate_topologies
        self.setup_benchmark_results_table >> self.generate_topologies

    def generate(self, dag, application):
        n_islands = 10
        island_size = 500
        migrant_pool_size = 4
        generations = 1000

        # for each topology, create a benchmark task
        self.benchmarks = []
        from sabaody import TopologyGenerator
        generator = TopologyGenerator(n_islands=n_islands,  island_size=island_size, migrant_pool_size=migrant_pool_size)

        for topology in generator.topologies:
            # https://stackoverflow.com/questions/49957464/apache-airflow-automation-how-to-run-spark-submit-job-with-param
            self.benchmarks.append(SparkSubmitOperator(
                task_id=legalize_name(topology['description']),
                conf={
                    'spark.cores.max': 10,
                    'spark.executor.cores': 1,
                },
                application=application,
                application_args=[
                    '--topology',  'sql:sabaody@luna,pw=w00t,db=sabaody(n_islands={n_islands},island_size={island_size},migrant_pool_size={migrant_pool_size},generations={generations}):{desc}'.format(
                        n_islands=n_islands,
                        island_size=island_size,
                        migrant_pool_size=migrant_pool_size,
                        generations=generations,
                        desc=topology['description'],
                    ),
                    '--migration', 'central',
                    '--migration-policy', 'uniform',
                    '--rounds', '50',
                    '--description', '{}'.format(topology['description']),
                    '--host', 'luna',
                    '--selection-policy', 'best',
                    '--selection-rate', '4',
                    '--replacement-policy', 'fair',
                    '--suite-run-id', '1',
                    'run',
                    # '--deploy-mode', 'client',
                ],
                dag=dag,
            ))
            self.generate_topologies >> self.benchmarks[-1]
