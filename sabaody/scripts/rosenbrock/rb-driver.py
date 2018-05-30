# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("rb-driver")
sc = SparkContext(conf=conf)

from sabaody import Archipelago

from rbsetup import RBRun

from tempfile import gettempdir
from os.path import join
import json

for i in range(10):
    with RBRun('luna', 11211) as run:
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
            if champions is None:
                champions = array([c for c,d,ids in raw_deltas])
            else:
                champions += array([c for c,d,ids in raw_deltas])
            delta_means = [float(nan_to_num(mean(d))) for c,d,ids in raw_deltas]

