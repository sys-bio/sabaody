# dumbed down archipelago
from __future__ import print_function, division, absolute_import

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("dumbeddown")
sc = SparkContext(conf=conf)

from uuid import uuid4
from sabaody import Island, Archipelago, run_island, problem_constructor, getQualifiedName
from toolz import partial

run_id = str(uuid4())
num_islands = 4

a = Archipelago(4, problem_constructor, 0., None, partial(getQualifiedName, 'B2', str(run_id)), 'luna', 11211)
a.run(sc, 0.)