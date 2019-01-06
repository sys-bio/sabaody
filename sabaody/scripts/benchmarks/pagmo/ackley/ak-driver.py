# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.pagmo.launcher import PagmobenchLauncher
from sabaody.terminator import TerminatorBase
from pygmo import problem, ackley

from os.path import join, dirname, abspath, realpath

class AckleyTerminator(TerminatorBase):
    def __init__(self, dim, cutoff):
        self.dim = dim
        self.cutoff = cutoff

    def should_stop(self, pg_island, monitor):
        from numpy import mean, sqrt
        return sqrt(mean((monitor.get_best_x()-ackley(dim).best_known())**2.)) < self.cutoff

dim = 10
cutoff = 0.01
script_dir = dirname(realpath(__file__))
py_files = ','.join(join(script_dir,p) for p in [
    '../launcher.py',
    ])
config = PagmobenchLauncher.from_cmdline_args(app_name='ak-driver', problem=problem(ackley(dim)), spark_files='', py_files=py_files, terminator=AckleyTerminator(dim,cutoff))

config.run_command(config.command)
