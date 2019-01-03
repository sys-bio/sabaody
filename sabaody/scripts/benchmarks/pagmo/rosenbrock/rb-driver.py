# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.pagmo.launcher import PagmobenchLauncher
from pygmo import problem, rosenbrock

from os.path import join, dirname, abspath, realpath

dim = 10
script_dir = dirname(realpath(__file__))
py_files = ','.join(join(script_dir,p) for p in [
    '../launcher.py',
    ])
config = PagmobenchLauncher.from_cmdline_args(app_name='rb-driver', problem=problem(rosenbrock(dim)), spark_files='', py_files=py_files)

config.run_command(config.command)
