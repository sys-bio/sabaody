# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.pagmo.benchsetup import PagmobenchLauncher
from params import getDefaultParamValues, getUpperBound, getLowerBound
from b4problem import B4_UDP

from os.path import join, dirname, abspath, realpath

def get_udp(validation_mode,n):
    if not validation_mode:
        return B4_UDP(getLowerBound(),getUpperBound())
    else:
        raise RuntimeError('No validation')

sbmlfile = abspath(join('..','..','..','..','..','sbml','b4.xml'))
script_dir = dirname(realpath(__file__))
config = PagmobenchLauncher.from_cmdline_args('rb-driver', pg.problem(pg.rosenbrock(dim)), getDefaultParamValues, sbmlfile=sbmlfile, spark_files=[], py_files=[])

config.run_command(config.command)
