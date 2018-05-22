# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("b2-nofork")
sc = SparkContext(conf=conf)

from sabaody import Archipelago

from b2setup import B2Run

with B2Run('luna', 11211) as run:
    from b2problem import make_problem
    a = Archipelago(4, make_problem, run.initial_score, None, run.getNameQualifier(), run.mc_host, run.mc_port)
    a.run(sc)

