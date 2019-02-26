# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from os.path import join, abspath, realpath, dirname
from datetime import datetime, timedelta

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

biopredyn_root_path = abspath(join(dirname(realpath(__file__)),'biopredyn'))

from sabaody import TopologyGenerator, BiopredynTopologyGenerator

pagmo_n_islands_values = (10,)
biopredyn_n_islands_values = (1,2,4,8,16)
island_size = 500
migrant_pool_size = 4
generations = 1000

def topology_generator(name, n_islands, island_size, migrant_pool_size, generations):
    import MySQLdb
    if name == 'pagmo':
        generator = TopologyGenerator(n_islands=n_islands,  island_size=island_size, migrant_pool_size=migrant_pool_size, generations=generations)
    elif name == 'biopredyn':
        generator = BiopredynTopologyGenerator(n_islands=n_islands,  island_size=island_size, migrant_pool_size=migrant_pool_size, generations=generations)
    else:
        raise RuntimeError('Unrecognized generator "{}"'.format(name))

    mariadb_connection = MySQLdb.connect('luna','sabaody','w00t','sabaody')
    cursor = mariadb_connection.cursor()

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
            'INSERT INTO topology_sets (Name, TopologySetID, Checksum, NumIslands, IslandSize, MigrantPoolSize, Generations, Content)',
            'VALUES ({name},{id},{checksum},{n_islands},{island_size},{migrant_pool_size},{generations},{content});'.format(
                name="'{}'".format(name),
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
    def __init__(self, dag, rounds, n_islands_values, topology_set_name):
        self.dag = dag
        self.rounds = rounds
        self.n_islands_values = n_islands_values
        self.topology_set_name = topology_set_name
        # first, make sure the SQL tables exist
        self.setup_topology_sets_table = MySqlOperator(
            task_id='.'.join((self.dag.dag_id, 'setup_topology_sets_table')),
            database='sabaody',
            sql='''
                CREATE TABLE IF NOT EXISTS topology_sets (
                    PrimaryKey INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                    Name VARCHAR(255) NOT NULL,
                    TopologySetID VARCHAR(255) NOT NULL,
                    Checksum INT NOT NULL,
                    NumIslands INT NOT NULL,
                    IslandSize INT NOT NULL,
                    MigrantPoolSize INT NOT NULL,
                    Generations INT NOT NULL,
                    Content LONGBLOB NOT NULL);''',
            dag=self.dag)

        # first, make sure the SQL tables exist
        self.setup_benchmark_results_table = MySqlOperator(
            task_id='.'.join((self.dag.dag_id, 'setup_benchmark_results_table')),
            database='sabaody',
            sql='''
                CREATE TABLE IF NOT EXISTS benchmark_runs (
                    PrimaryKey INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                    Benchmark VARCHAR(255) NOT NULL,
                    RunID VARCHAR(255) NOT NULL,
                    MetricID VARCHAR(255) NOT NULL,
                    Description TEXT NOT NULL,
                    TopologyID VARCHAR(255) NOT NULL,
                    MaxRounds INT,
                    Generations INT,
                    Champions BLOB NOT NULL,
                    MinScore DOUBLE NOT NULL,
                    AverageScore DOUBLE NOT NULL,
                    ActualRounds TEXT NOT NULL,
                    ActualAvgRounds DOUBLE NOT NULL,
                    ValidationMode INT NOT NULL,
                    ValidationPoints INT NOT NULL,
                    TimeStart DATETIME NOT NULL,
                    TimeEnd DATETIME NOT NULL);''',
            dag=self.dag)

        # store the topologies in the table
        for n_islands in self.n_islands_values:
            self.generate_topologies = PythonOperator(
                task_id='.'.join((self.dag.dag_id, self.topology_set_name, 'n_islands_{}'.format(n_islands), 'generate_topologies')),
                python_callable=topology_generator,
                op_kwargs={
                    'name': self.topology_set_name,
                    'n_islands': n_islands,
                    'island_size': island_size,
                    'migrant_pool_size': migrant_pool_size,
                    'generations': generations},
                dag=self.dag)

        self.setup_topology_sets_table >> self.generate_topologies
        self.setup_benchmark_results_table >> self.generate_topologies

    def get_application_args(self, topology, n_islands):
        return [ # FIXME: hardcoded
            '--topology',  'sql:sabaody@luna,pw=w00t,db=sabaody(name={name},n_islands={n_islands},island_size={island_size},migrant_pool_size={migrant_pool_size},generations={generations}):{desc}'.format(
                name=self.topology_set_name,
                n_islands=n_islands,
                island_size=island_size,
                migrant_pool_size=migrant_pool_size,
                generations=generations,
                desc=topology['description'],
            ),
            '--migration', 'central',
            '--migration-policy', 'uniform',
            '--rounds', str(self.rounds),
            '--description', '{}'.format(topology['description']),
            '--host', 'ragnarok',
            '--metric-host', 'luna',
            '--selection-policy', 'best',
            '--selection-rate', '4',
            '--replacement-policy', 'fair',
            '--suite-run-id', '1',
            'run',
            # '--deploy-mode', 'client',
            ]

    def make_topology_generator(self, n_islands):
        if self.topology_set_name == 'pagmo':
            return TopologyGenerator(n_islands=n_islands,  island_size=island_size, migrant_pool_size=migrant_pool_size, generations=generations)
        elif self.topology_set_name == 'biopredyn':
            return BiopredynTopologyGenerator(n_islands=n_islands,  island_size=island_size, migrant_pool_size=migrant_pool_size, generations=generations)
        else:
            raise RuntimeError('Unrecognized generator "{}"'.format(self.topology_set_name))

    def generate(self, benchmark, application):
        # for each topology, create a benchmark task
        self.benchmarks = []

        for n_islands in self.n_islands_values:
            for topology in self.make_topology_generator(n_islands=n_islands).topologies:
                # https://stackoverflow.com/questions/49957464/apache-airflow-automation-how-to-run-spark-submit-job-with-param
                self.benchmarks.append(SparkSubmitOperator(
                    task_id='.'.join((self.dag.dag_id, benchmark, 'n_islands_{}'.format(n_islands), legalize_name(topology['description']))),
                    conf={
                        'spark.cores.max': 10,
                        'spark.executor.cores': 1,
                    },
                    application=application,
                    application_args=self.get_application_args(topology, n_islands),
                    dag=self.dag,
                ))
                self.generate_topologies >> self.benchmarks[-1]


biopredyn_rounds = 4000

def make_biopredyn_task_generator(dag):
    return TaskGenerator(dag, rounds=biopredyn_rounds, n_islands_values=biopredyn_n_islands_values, topology_set_name='biopredyn')

all_bench_generator = make_biopredyn_task_generator(all_benchmarks_dag)

b1_dag = DAG(
  'b1_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
make_biopredyn_task_generator(b1_dag).generate('b1', join(biopredyn_root_path,'b1','b1-driver.py'))
all_bench_generator.generate('b1', join(biopredyn_root_path,'b1','b1-driver.py'))

b2_dag = DAG(
  'b2_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
make_biopredyn_task_generator(b2_dag).generate('b2', join(biopredyn_root_path,'b2','b2-driver.py'))
all_bench_generator.generate('b2', join(biopredyn_root_path,'b2','b2-driver.py'))

b3_dag = DAG(
  'b3_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
make_biopredyn_task_generator(b3_dag).generate('b3', join(biopredyn_root_path,'b3','b3-driver.py'))
all_bench_generator.generate('b3', join(biopredyn_root_path,'b3','b3-driver.py'))

b4_dag = DAG(
  'b4_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
make_biopredyn_task_generator(b4_dag).generate('b4', join(biopredyn_root_path,'b4','b4-driver.py'))
all_bench_generator.generate('b4', join(biopredyn_root_path,'b4','b4-driver.py'))

b5_dag = DAG(
  'b5_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
make_biopredyn_task_generator(b5_dag).generate('b5', join(biopredyn_root_path,'b5','b5-driver.py'))
all_bench_generator.generate('b5', join(biopredyn_root_path,'b5','b5-driver.py'))



# pagmo test problems

class PagmoTaskGenerator(TaskGenerator):
    def get_application_args(self, topology, n_islands, dimension, cutoff):
        return super().get_application_args(topology=topology, n_islands=n_islands)+[
            '--dimension', str(dimension),
            '--cutoff', str(cutoff),
            ]
    def generate(self, benchmark, application, dimension, cutoff):
        self.benchmarks = []
        for n_islands in self.n_islands_values:
            for topology in self.make_topology_generator(n_islands=n_islands).topologies:
                self.benchmarks.append(SparkSubmitOperator(
                    task_id='.'.join((self.dag.dag_id, benchmark, legalize_name(topology['description']))),
                    conf={
                        'spark.cores.max': 10,
                        'spark.executor.cores': 1,
                    },
                    application=application,
                    application_args=self.get_application_args(topology, n_islands, dimension, cutoff),
                    dag=self.dag,
                ))
                self.generate_topologies >> self.benchmarks[-1]

pagmo_benchmarks_dag = DAG(
  'pagmo_benchmarks',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))

pagmo_root_path = abspath(join(dirname(realpath(__file__)),'pagmo'))
pagmo_rounds = 2000
pagmo_dimension = 16
pagmo_cutoff = 0.01

def make_pagmo_task_generator(dag):
    return PagmoTaskGenerator(dag, rounds=pagmo_rounds, n_islands_values=pagmo_n_islands_values, topology_set_name='pagmo')

pagmo_bench_generator = make_pagmo_task_generator(pagmo_benchmarks_dag)

ackley_dag = DAG(
  'ackley_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
make_pagmo_task_generator(ackley_dag).generate(
    'ackley', join(pagmo_root_path,'ackley','ak-driver.py'), dimension=pagmo_dimension, cutoff=pagmo_cutoff)
pagmo_bench_generator.generate('ackley', join(pagmo_root_path,'ackley','ak-driver.py'), dimension=pagmo_dimension, cutoff=pagmo_cutoff)

griewank_dag = DAG(
  'griewank_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
make_pagmo_task_generator(griewank_dag).generate(
    'griewank', join(pagmo_root_path,'griewank','gr-driver.py'), dimension=pagmo_dimension, cutoff=pagmo_cutoff)
pagmo_bench_generator.generate('griewank', join(pagmo_root_path,'griewank','gr-driver.py'), dimension=pagmo_dimension, cutoff=pagmo_cutoff)

rastrigin_dag = DAG(
  'rastrigin_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
make_pagmo_task_generator(rastrigin_dag).generate(
    'rastrigin', join(pagmo_root_path,'rastrigin','ra-driver.py'), dimension=pagmo_dimension, cutoff=pagmo_cutoff)
pagmo_bench_generator.generate('rastrigin', join(pagmo_root_path,'rastrigin','ra-driver.py'), dimension=pagmo_dimension, cutoff=pagmo_cutoff)

rosenbrock_dag = DAG(
  'rosenbrock_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
make_pagmo_task_generator(rosenbrock_dag).generate(
    'rosenbrock', join(pagmo_root_path,'rosenbrock','rb-driver.py'), dimension=pagmo_dimension, cutoff=pagmo_cutoff)
pagmo_bench_generator.generate('rosenbrock', join(pagmo_root_path,'rosenbrock','rb-driver.py'), dimension=pagmo_dimension, cutoff=pagmo_cutoff)

schwefel_dag = DAG(
  'schwefel_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10000))
make_pagmo_task_generator(schwefel_dag).generate(
    'schwefel', join(pagmo_root_path,'schwefel','sw-driver.py'), dimension=pagmo_dimension, cutoff=pagmo_cutoff)
pagmo_bench_generator.generate('schwefel', join(pagmo_root_path,'schwefel','sw-driver.py'), dimension=pagmo_dimension, cutoff=pagmo_cutoff)
