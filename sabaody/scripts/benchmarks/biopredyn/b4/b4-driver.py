# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.biopredyn.benchsetup import BiopredynConfiguration
from params import getDefaultParamValues, getUpperBound, getLowerBound
from b4problem import B4_UDP

from os.path import join, dirname, realpath

def get_udp(validation_mode,n):
    if not validation_mode:
        return B4_UDP(getLowerBound(),getUpperBound())
    else:
        raise RuntimeError('No validation')

script_dir = dirname(realpath(__file__))
py_files = ','.join(join(script_dir,p) for p in [
    'data.py',
    'b4problem.py',
    'params.py',
    ])
config = BiopredynConfiguration.from_cmdline_args('b4-driver', '../../../../../sbml/b4.xml', script_dir, get_udp, getDefaultParamValues, py_files)

config.run_command(config.command)
