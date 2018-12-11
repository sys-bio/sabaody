# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from pyspark import SparkContext, SparkConf

from sabaody import Archipelago, MigrationPolicyUniform, BestSPolicy, FairRPolicy
from sabaody.migration_central import CentralMigrator

from rbsetup import RBRunMCMonitor
import pygmo as pg

from numpy import array, save, savez, mean, std, nan_to_num, vstack
import arrow

from tempfile import gettempdir
from os.path import join
import json
from os.path import dirname, realpath

from sabaody import TopologyGenerator

n_islands         = 10
island_size       = 10
migrant_pool_size = 2
generations       = 10
rounds = 500
dim = 5
spark_hostname = 'ragnarok'
spark_port = 7077

script_dir = dirname(realpath(__file__))
spark_files = ''
py_files = ','.join(join(script_dir,p) for p in [
    'rbsetup.py',
    ])
print('pyfiles', py_files)

spark_conf = SparkConf().setAppName("rb-driver")
spark_conf.setMaster('spark://{}:{}'.format(spark_hostname,spark_port))
spark_conf.set('spark.driver.memory', '1g')
spark_context = SparkContext(conf=spark_conf)
# spark_conf.set('spark.files', ','.join([spark_files,py_files]))
spark_conf.set('spark.files', py_files)
spark_conf.set('spark.submit.pyFiles', py_files)

generator = TopologyGenerator(
    n_islands = n_islands,
    island_size = island_size,
    migrant_pool_size = migrant_pool_size,
    generations = generations)
topology,id = generator.find_in_database(
    desc = 'One-way ring, de',
    user = 'sabaody',
    host = 'luna',
    pw   = 'w00t',
    db   = 'sabaody')
a = topology['archipelago']
migration_policy = MigrationPolicyUniform()
selection_policy = BestSPolicy(migration_rate=1)
replacement_policy = FairRPolicy()
migrator = CentralMigrator(migration_policy, selection_policy, replacement_policy, 'http://luna:10100')
if isinstance(migrator, CentralMigrator):
    migrator.defineMigrantPools(a.topology, dim)

time_start = arrow.utcnow()

champions = []
stage_deltas = []
N = 1
for i in range(N):
    with RBRunMCMonitor('rb-driver', 'luna', 11211, run=1) as monitor:
        print('Started run {} of {}'.format(i+1,N))
        a.monitor = monitor
        results = a.run(spark_context, migrator, pg.problem(pg.rosenbrock(dim)), rounds)
        a.monitor = None

        champions = sorted([(f[0],x) for f,x in results], key=lambda t: t[0])
        champion_scores = [f for f,x in champions]

        best_score,best_candidate = champions[0]
        average_score = float(sum(champion_scores))/len(champion_scores)

        print('min champion score {}'.format(best_score))
        print('mean champion score {}'.format(average_score))
        print('candidiate:', best_candidate)
        print('Diff with best known:')
        print(best_candidate - pg.rosenbrock(dim).best_known())
        print('Total run time: {}'.format(time_start.humanize()))
        # import pprint
        # pp = pprint.PrettyPrinter(indent=2)
        # pp.pprint(result)
        # with open(join(gettempdir(),'deltas.json'),'w') as f:
        #     json.dump(result,f)

        # with open(join(gettempdir(),'deltas.json')) as f:
        #     ip,host,island_id,raw_deltas = json.load(f)[0][:4]
        #     champions.append(array([c for c,d,ids in raw_deltas]))
        #     stage_deltas.append(array([float(nan_to_num(mean(d))) for c,d,ids in raw_deltas]))

time_end = arrow.utcnow()
print('Total time:  {}'.format((time_end-time_start)))

# champions_stack = vstack(champions)
# champions_mean = mean(champions_stack, axis=0)
# champions_std = std(champions_stack, axis=0)
# savez('/tmp/rb-spark-champions.npz', champions_mean=champions_mean, champions_std=champions_std)

# stage_deltas_stack = vstack(stage_deltas)
# stage_deltas_mean = mean(stage_deltas_stack, axis=0)
# stage_deltas_std = std(stage_deltas_stack, axis=0)
# savez('/tmp/rb-spark-stage_deltas.npz', stage_deltas_mean=stage_deltas_mean, stage_deltas_std=stage_deltas_std)
