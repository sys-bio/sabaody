from __future__ import print_function, division, absolute_import

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("dumbeddown")
sc = SparkContext(conf=conf)

from uuid import uuid4
from sabaody import Island, run_island, problem_constructor, getQualifiedName
from toolz import partial

run_id = str(uuid4())
num_islands = 4

island_ids = [str(uuid4()) for x in range(num_islands)]
islands = [Island(u, problem_constructor, partial(getQualifiedName, 'B2', str(run_id)), 'luna', 11211) for u in island_ids]
print(sc.parallelize(islands).map(run_island).collect())