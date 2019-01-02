# Driver code for B5 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.biopredyn.launcher import BiopredynConfiguration
from params import getDefaultParamValues, getUpperBound, getLowerBound
from b5problem import B5_UDP

from os.path import join, dirname, abspath, realpath

def get_udp(validation_mode,n):
    if not validation_mode:
        return B4_UDP(getLowerBound(),getUpperBound())
    else:
        raise RuntimeError('No validation')

sbmlfile = join('..','..','..','..','..','sbml','b5.xml')
script_dir = dirname(realpath(__file__))
spark_files = ','.join(join(script_dir,p) for p in [
    sbmlfile,
    'exp_data.json',
    'exp_y0.json',
    'params.json',
    'stimuli.json',
    ])
py_files = ','.join(join(script_dir,p) for p in [
    'b5problem.py',
    'observables.py',
    'parameters.py',
    '../launcher.py',
    ])
config = BiopredynConfiguration.from_cmdline_args('b5-driver', get_udp, getDefaultParamValues, sbmlfile=sbmlfile, spark_files=spark_files, py_files=py_files)

config.run_command(config.command)
