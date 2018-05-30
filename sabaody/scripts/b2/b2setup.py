from __future__ import print_function, division, absolute_import

from params import getDefaultParamValues

from sabaody import getQualifiedName
from sabaody.problem_setup import ProblemSetup

from pymemcache.client.base import Client

from uuid import uuid4
from time import time

# some refs:
#https://developerzen.com/best-practices-writing-production-grade-pyspark-jobs-cb688ac4d20f
#https://medium.com/@mrpowers/creating-a-pyspark-project-with-pytest-pyenv-and-egg-files-d2709eb1604c

class B2Run(ProblemSetup):
    '''
    Abstracts some of the logic of setting up a parameter fitting problem.
    Provides information via MC for monitoring.
    '''
    def getName(self):
        return 'B2'

    def getDomain(self):
        return 'com.how2cell.sabaody.B2'

    def calculateInitialScore(self):
        with open('../../../sbml/b2.xml') as f:
            sbml = f.read()

        # show initial score
        from b2problem import B2Problem
        p = B2Problem(sbml)
        self.initial_score = p.evaluate(getDefaultParamValues())
        print('Initial score: {}'.format(self.initial_score))