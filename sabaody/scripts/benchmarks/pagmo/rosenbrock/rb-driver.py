# Sabaody
# Copyright 2018-2019 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.pagmo.launcher import PagmobenchLauncher
from sabaody.terminator import TerminatorBase
from pygmo import problem, rosenbrock

from os.path import join, dirname, abspath, realpath

class RosenbrockTerminator(TerminatorBase):
    def __init__(self, dim, cutoff):
        self.dim = dim
        self.cutoff = cutoff

    def should_stop(self, pg_island, monitor):
        from numpy import mean, sqrt
        best_x = monitor.get_best_x()
        if best_x is None:
            return False
        else:
            return sqrt(mean((best_x-rosenbrock(self.dim).best_known())**2.)) < self.cutoff

script_dir = dirname(realpath(__file__))
py_files = ','.join(join(script_dir,p) for p in [
    '../launcher.py',
    ])
config = PagmobenchLauncher.from_cmdline_args(app_name='rb-driver', problem=lambda dim: problem(rosenbrock(dim)), spark_files='', py_files=py_files, terminator=RosenbrockTerminator)

config.run_command(config.command)
