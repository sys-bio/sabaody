# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from b2setup import B2Configuration

config = B2Configuration.from_cmdline_args()

config.island_size = 10
config.migrant_pool_size = 5
from sabaody.migration import BestSPolicy, FairRPolicy
config.selection_policy = BestSPolicy(migration_rate=config.migrant_pool_size)
config.replacement_policy = FairRPolicy()

config.run_command(config.command)
