# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.pagmo.launcher import PagmobenchLauncher

from os.path import join, dirname, abspath, realpath

script_dir = dirname(realpath(__file__))
py_files = ','.join(join(script_dir,p) for p in [
    '../launcher.py',
])
config = PagmobenchLauncher.from_cmdline_args(app_name='rb-driver', problem=pg.problem(pg.rosenbrock(dim)), spark_files=[], py_files=py_files)

config.run_command(config.command)
