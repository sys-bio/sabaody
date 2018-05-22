from __future__ import print_function, division, absolute_import

from params import getDefaultParamValues

from sabaody import getQualifiedName

from pymemcache.client.base import Client

from uuid import uuid4
from time import time

# some refs:
#https://developerzen.com/best-practices-writing-production-grade-pyspark-jobs-cb688ac4d20f
#https://medium.com/@mrpowers/creating-a-pyspark-project-with-pytest-pyenv-and-egg-files-d2709eb1604c

class B2Run:
    '''
    Abstracts some of the logic of setting up a parameter fitting problem.
    Provides information via MC for monitoring.
    '''
    def __init__(self, mc_host, mc_port):
        self.mc_host = mc_host
        self.mc_port = mc_port
        self.client = Client((mc_host,mc_port))

        self.setupMonitoringVariables()
        self.calculateInitialScore()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_val, trace):
        self.client.set('com.how2cell.sabaody.B2.run.status', 'finished', 604800)
        self.client.set('com.how2cell.sabaody.B2.run.endTime', str(time()), 604800)

    def setupMonitoringVariables(self):
        self.run = int(self.client.get('com.how2cell.sabaody.B2.run') or 0)
        self.run += 1
        self.client.set('com.how2cell.sabaody.B2.run', self.run, 604800)

        self.run_id = str(uuid4())
        self.client.set('com.how2cell.sabaody.B2.runId', self.run_id, 604800)
        self.client.set('com.how2cell.sabaody.B2.run.startTime', str(time()), 604800)
        self.client.set('com.how2cell.sabaody.B2.run.status', 'active', 604800)

        print('Starting run {} of B2 problem with id {}...'.format(self.run, self.run_id))

    def calculateInitialScore(self):
        with open('../../../sbml/b2.xml') as f:
            sbml = f.read()

        # show initial score
        from b2problem import B2Problem
        p = B2Problem(sbml)
        self.initial_score = p.evaluate(getDefaultParamValues())
        print('Initial score: {}'.format(self.initial_score))

    def getNameQualifier(self):
        from toolz import partial
        return partial(getQualifiedName, 'B2', str(self.run_id))