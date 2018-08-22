from __future__ import print_function, division, absolute_import

from sabaody import getQualifiedName

from pymemcache.client.base import Client

from uuid import uuid4
from time import time

class ProblemSetup:
    '''
    Abstracts some of the logic of setting up a parameter fitting problem.
    Provides information via MC for monitoring.
    '''
    def __init__(self, mc_host, mc_port):
        self.mc_host = mc_host
        self.mc_port = mc_port
        self.mc_client = Client((self.mc_host,self.mc_port))

        self.setupMonitoringVariables()
        self.calculateInitialScore()

    def __enter__(self):
        from .diagnostics import test_memcached
        test_memcached(self.mc_host, self.mc_port)
        return self

    def domainAppend(self,s):
        return '.'.join((self.getDomain(),s))

    def __exit__(self, exception_type, exception_val, trace):
        self.mc_client.set(self.domainAppend('run.status'), 'finished', 604800)
        self.mc_client.set(self.domainAppend('run.endTime'), str(time()), 604800)

    def setupMonitoringVariables(self):
        self.run = int(self.mc_client.get(self.domainAppend('run')) or 0)
        self.run += 1
        self.mc_client.set(self.domainAppend('run'), self.run, 604800)

        self.run_id = str(uuid4())
        self.mc_client.set(self.domainAppend('runId'), self.run_id, 604800)
        self.mc_client.set(self.domainAppend('run.startTime'), str(time()), 604800)
        self.mc_client.set(self.domainAppend('run.status'), 'active', 604800)

        print('Starting run {} of {} problem with id {}...'.format(self.run, self.getName(), self.run_id))

    def getNameQualifier(self):
        from toolz import partial
        return partial(getQualifiedName, self.getName(), str(self.run_id))