# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("rb-driver")
sc = SparkContext(conf=conf)

from sabaody import Archipelago

from rbsetup import RBRun

from numpy import array, save, savez, mean, std, nan_to_num, vstack
import arrow

from tempfile import gettempdir
from os.path import join
import json

start = arrow.utcnow()

champions = []
stage_deltas = []
N = 2
for i in range(N):
    with RBRun('luna', 11211) as run:
        print('Started run {} of {}'.format(i+1,N))
        from rbsetup import make_problem
        a = Archipelago(4, make_problem, run.initial_score, None, run.getNameQualifier(), run.mc_host, run.mc_port)
        result = a.run(sc)
        import pprint
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(result)
        with open(join(gettempdir(),'deltas.json'),'w') as f:
            json.dump(result,f)

        with open(join(gettempdir(),'deltas.json')) as f:
            ip,host,island_id,raw_deltas = json.load(f)[0][:4]
            champions.append(array([c for c,d,ids in raw_deltas]))
            stage_deltas.append(array([float(nan_to_num(mean(d))) for c,d,ids in raw_deltas]))

end = arrow.utcnow()
print('Total time:  {}'.format((end-start)))

champions_stack = vstack(champions)
champions_mean = mean(champions_stack, axis=0)
champions_std = std(champions_stack, axis=0)
savez('/tmp/rb-spark-champions.npz', champions_mean=champions_mean, champions_std=champions_std)

stage_deltas_stack = vstack(stage_deltas)
stage_deltas_mean = mean(stage_deltas_stack, axis=0)
stage_deltas_std = std(stage_deltas_stack, axis=0)
savez('/tmp/rb-spark-stage_deltas.npz', stage_deltas_mean=stage_deltas_mean, stage_deltas_std=stage_deltas_std)