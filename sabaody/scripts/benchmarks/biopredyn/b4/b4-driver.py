# Driver code for B4 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.biopredyn.launcher import BiopredynConfiguration
from params import getDefaultParamValues, getUpperBound, getLowerBound
from sabaody.terminator import TerminatorBase
from b4problem import B4_UDP

from os.path import join, dirname, realpath

def get_udp(validation_mode,n):
    if not validation_mode:
        return B4_UDP(getLowerBound(),getUpperBound())
    else:
        raise RuntimeError('No validation')

class B4Terminator(TerminatorBase):
    def should_stop(self, pg_island, monitor):
        from numpy import mean
        best_f = monitor.get_best_f()
        if best_f is None:
            return False
        else:
            return mean(best_f) < 0.065

sbmlfile = join('..','..','..','..','..','sbml','b4.xml')
script_dir = dirname(realpath(__file__))
spark_files = ','.join(join(script_dir,p) for p in [
    sbmlfile,
    ])
py_files = ','.join(join(script_dir,p) for p in [
    'data.py',
    'b4problem.py',
    'params.py',
    '../launcher.py',
    ])
config = BiopredynConfiguration.from_cmdline_args('b4-driver', get_udp, getDefaultParamValues, sbmlfile=sbmlfile, spark_files=spark_files, py_files=py_files, terminator=B4Terminator())

config.run_command(config.command)
