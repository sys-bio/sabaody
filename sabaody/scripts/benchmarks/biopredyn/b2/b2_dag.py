# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from airflow import DAG
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 11, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}

dag = DAG(
  'b2_benchmark',
  default_args=default_args,
  concurrency=1,
  schedule_interval=timedelta(10))

from sabaody.scripts.benchmarks.bench_dag import TaskFactory

tasks = TaskFactory().create(dag)