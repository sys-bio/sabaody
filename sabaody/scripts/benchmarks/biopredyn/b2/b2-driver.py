# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.biopredyn.launcher import BiopredynConfiguration
from params import getDefaultParamValues, getUpperBound, getLowerBound
from sabaody.terminator import TerminatorBase
from b2problem import B2_UDP
from b2problem_validator import B2Validator_UDP

from os.path import join, dirname, realpath

def get_udp(validation_mode,n):
    if not validation_mode:
        return B2_UDP(getLowerBound(),getUpperBound())
    else:
        return B2Validator_UDP(getLowerBound(),getUpperBound(),n=n)

class B2Terminator(TerminatorBase):
    def should_stop(self, pg_island, monitor):
        from numpy import mean
        best_f = monitor.get_best_f()
        if best_f is None:
            return False
        else:
            return mean(best_f) < 1.1*(0.2530801448126069+0.24730614493051514+0.24460544824403804)/3.

sbmlfile = join('..','..','..','..','..','sbml','b2.xml')
script_dir = dirname(realpath(__file__))
spark_files = ','.join(join(script_dir,p) for p in [
    sbmlfile,
    ])
py_files = ','.join(join(script_dir,p) for p in [
    'data.py',
    'b2problem.py',
    'b2problem_validator.py',
    'params.py',
    '../launcher.py',
    ])
config = BiopredynConfiguration.from_cmdline_args('b2-driver', get_udp, getDefaultParamValues, sbmlfile=sbmlfile, spark_files=spark_files, py_files=py_files, terminator=B2Terminator())

config.run_command(config.command)
