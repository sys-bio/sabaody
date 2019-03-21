# Driver code for B1 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.biopredyn.launcher import BiopredynConfiguration
from params import getDefaultParamValues, getUpperBound, getLowerBound
from sabaody.terminator import TerminatorBase
from b1problem import B1_UDP

from os.path import join, dirname, realpath

def get_udp(validation_mode,n):
    if not validation_mode:
        return B1_UDP(getLowerBound(),getUpperBound())
    else:
        raise RuntimeError('No validation')

class B1Terminator(TerminatorBase):
    def should_stop(self, pg_island, monitor):
        from numpy import mean
        best_f = monitor.get_best_f()
        if best_f is None:
            return False
        else:
            return False # put criterion here

sbmlfile = join('..','..','..','..','..','sbml','b1-copasi.xml')
script_dir = dirname(realpath(__file__))
spark_files = ','.join(join(script_dir,p) for p in [
    sbmlfile,
    ])
py_files = ','.join(join(script_dir,p) for p in [
    'data.py',
    'b1problem.py',
    'params.py',
    '../launcher.py',
    ])
config = BiopredynConfiguration.from_cmdline_args('b1-driver', get_udp, getDefaultParamValues, sbmlfile=sbmlfile, spark_files=spark_files, py_files=py_files, terminator=B1Terminator())

config.run_command(config.command)
