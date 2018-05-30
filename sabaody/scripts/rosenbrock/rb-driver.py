# Driver code for B2 parameter fitting problem.
from __future__ import print_function, division, absolute_import

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("rb-driver")
sc = SparkContext(conf=conf)

from sabaody import Archipelago
from sabaody.problem_setup import ProblemSetup

from b2setup import B2Run

class RBRun(ProblemSetup):
    '''
    Abstracts some of the logic of setting up a parameter fitting problem.
    Provides information via MC for monitoring.
    '''
    def getName(self):
        return 'RB'

    def getDomain(self):
        return 'com.how2cell.sabaody.RB'

    def calculateInitialScore(self):
        self.initial_score = 0

def make_problem():
    import pygmo as pg
    return pg.problem(pg.rosenbrock(5))

with RBRun('luna', 11211) as run:
    a = Archipelago(4, make_problem, run.initial_score, None, run.getNameQualifier(), run.mc_host, run.mc_port)
    a.run(sc)

