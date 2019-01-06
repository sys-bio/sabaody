# Sabaody
# Copyright 2018-2019 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.pagmo.launcher import PagmobenchLauncher
from sabaody.terminator import TerminatorBase
from pygmo import problem, griewank

from os.path import join, dirname, abspath, realpath

class GriewankTerminator(TerminatorBase):
    def __init__(self, dim, cutoff):
        self.dim = dim
        self.cutoff = cutoff

    def should_stop(self, pg_island, monitor):
        from numpy import mean, sqrt
        return sqrt(mean((monitor.get_best_x()-griewank(dim).best_known())**2.)) < self.cutoff

script_dir = dirname(realpath(__file__))
py_files = ','.join(join(script_dir,p) for p in [
    '../launcher.py',
    ])
config = PagmobenchLauncher.from_cmdline_args(app_name='gr-driver', problem=problem(griewank(dim)), spark_files='', py_files=py_files, terminator=GriewankTerminator)

config.run_command(config.command)
