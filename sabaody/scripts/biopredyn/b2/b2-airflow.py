"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from itertools import product

from airflowTestScript import deploy_mode

num_islands = list(range(4 , 6))
topology = ["bidir-ring"]
migration = ["central"]
migration_policy = ["uniform"]
host = ["luna"]
command = ["run"]
deploy_mode = ["client"]
script = ["b2-driver.py"]

spark_configs = ["spark.cores.max=5","spark.executor.cores=1"]

def compose_spark_command(script, deploy_mode,confs, topology, migration, migration_policy, num_islands, host, command):
    """spark-submit
    --deploy-mode client
    --conf "spark.cores.max=5"
    --conf "spark.executor.cores=1"
    b2-driver.py
    --topology ring
    --migration central
    --migration-policy uniform
    --num-islands 4
    --host luna
    run"""

    spark_command = """spark-submit
    --deploy-mode {deploy_mode} 
    {configs}
    {script}
    --topology {topology} 
    --migration {migration} 
    --migration-policy {migration_policy} 
    --num-islands {num_islands} 
    --host {host} 
    {command}
    """

    if type(confs) != list:
        confs = []

    config_structure = """ --conf "{conf}" """

    spark_benchmark_configs = []
    for items in confs:
        spark_benchmark_configs.append(config_structure.format(conf = items))



    spark_command = spark_command.format(
        deploy_mode = deploy_mode,
        configs = " ".join(spark_benchmark_configs),
        script = script,
        topology = topology,
        migration = migration,
        migration_policy = migration_policy,
        num_islands = num_islands ,
        host = host,
        command = command
    )

    return spark_command.replace("\n"," ")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.now(),
    'email': ['s.asifullah7@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG(
    'B2Benchmark', default_args=default_args, schedule_interval=timedelta(10))


def compose():
    global num_islands, topology, migration_policy, migration, deploy_mode, spark_configs
    tasks = []
    combinations = list(product(script,deploy_mode, topology, migration, migration_policy,num_islands, host, command))

    for arrangement in combinations:
        tasks.append(
            compose_spark_command(
                script=arrangement[0],
                deploy_mode=arrangement[1],
                confs=spark_configs,
                topology=arrangement[2],
                migration = arrangement[3],
                migration_policy = arrangement[4],
                num_islands = arrangement[5],
                host = arrangement[6],
                command=arrangement[7]

            )
        )

    airflow_benchmark_tasks = []
    for task_id,each_item in enumerate(tasks):

        airflow_benchmark_tasks.append(
            BashOperator(
                task_id =task_id,
                bash_command = "{0}".format(each_item),
                dag = dag
            )
        )

    return airflow_benchmark_tasks

def build_topology(airflow_tasks):
    for task_id in range(1, len(airflow_tasks)):
        airflow_tasks[task_id].set_upstream(airflow_tasks[task_id-1])

def run():
    airflow_tasks = compose()
    build_topology(airflow_tasks)

run()


compose()