# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from biopredyn import BiopredynConfiguration
from params import getDefaultParamValues
from b2problem import B2Problem

config = BiopredynConfiguration.from_cmdline_args('b2-driver', '../../../sbml/b2.xml', B2Problem, getDefaultParamValues)

config.island_size = 10
config.migrant_pool_size = 5
from sabaody.migration import BestSPolicy, FairRPolicy
config.selection_policy = BestSPolicy(migration_rate=config.migrant_pool_size)
config.replacement_policy = FairRPolicy()

config.run_command(config.command)
