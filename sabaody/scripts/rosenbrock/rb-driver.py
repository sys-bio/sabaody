# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("rb-driver")
sc = SparkContext(conf=conf)

from sabaody import Archipelago

from rbsetup import RBRun

with RBRun('luna', 11211) as run:
    from rbsetup import make_problem
    a = Archipelago(4, make_problem, run.initial_score, None, run.getNameQualifier(), run.mc_host, run.mc_port)
    a.run(sc)

