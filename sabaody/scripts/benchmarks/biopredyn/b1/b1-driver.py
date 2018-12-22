# Driver code for B1 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.biopredyn.benchsetup import BiopredynConfiguration
from params import getDefaultParamValues, getUpperBound, getLowerBound
from b4problem import B1_UDP

from os.path import join, dirname, abspath, realpath

def get_udp(validation_mode,n):
    if not validation_mode:
        return B1_UDP(getLowerBound(),getUpperBound())
    else:
        raise RuntimeError('No validation')

sbmlfile = abspath(join('..','..','..','..','..','sbml','b1-fixed.xml'))
script_dir = dirname(realpath(__file__))
spark_files = ','.join(join(script_dir,p) for p in [
    sbmlfile,
    ])
py_files = ','.join(join(script_dir,p) for p in [
    'data.py',
    'b1problem.py',
    'params.py',
    '../benchsetup.py',
    ])
config = BiopredynConfiguration.from_cmdline_args('b1-driver', get_udp, getDefaultParamValues, sbmlfile=sbmlfile, spark_files=spark_files, py_files=py_files)

config.run_command(config.command)
