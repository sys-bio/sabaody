# Sabaody
# Copyright 2018-2019 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.pagmo.launcher import PagmobenchLauncher
from sabaody.terminator import TerminatorBase
from pygmo import problem, rastrigin

from os.path import join, dirname, abspath, realpath

class RastriginTerminator(TerminatorBase):
    def __init__(self, dim, cutoff):
        self.dim = dim
        self.cutoff = cutoff

    def should_stop(self, pg_island, monitor):
        from numpy import mean, sqrt
        best_x = monitor.get_best_x()
        if best_x is None:
            return False
        else:
            return sqrt(mean((best_x-rastrigin(self.dim).best_known())**2.)) < self.cutoff

script_dir = dirname(realpath(__file__))
py_files = ','.join(join(script_dir,p) for p in [
    '../launcher.py',
    ])
config = PagmobenchLauncher.from_cmdline_args(app_name='ra-driver', problem=lambda dim: problem(rastrigin(dim)), spark_files='', py_files=py_files, terminator=RastriginTerminator)

config.run_command(config.command)
