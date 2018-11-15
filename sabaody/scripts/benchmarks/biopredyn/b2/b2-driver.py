# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from sabaody.scripts.benchmarks.biopredyn.benchsetup import BiopredynConfiguration
from params import getDefaultParamValues, getUpperBound, getLowerBound
from b2problem import B2_UDP

from os.path import dirname, realpath

config = BiopredynConfiguration.from_cmdline_args('b2-driver', '../../../../../sbml/b2.xml', dirname(realpath(__file__)), B2_UDP(getLowerBound(),getUpperBound()), getDefaultParamValues)

config.island_size = 10
config.migrant_pool_size = 5
from sabaody.migration import BestSPolicy, FairRPolicy
config.selection_policy = BestSPolicy(migration_rate=config.migrant_pool_size)
config.replacement_policy = FairRPolicy()

config.run_command(config.command)
