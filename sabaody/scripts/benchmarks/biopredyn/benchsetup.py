from __future__ import print_function, division, absolute_import

from sabaody.benchmark_launcher import MemcachedMonitor, BenchmarkLauncherBase

import json

# some refs:
#https://developerzen.com/best-practices-writing-production-grade-pyspark-jobs-cb688ac4d20f
#https://medium.com/@mrpowers/creating-a-pyspark-project-with-pytest-pyenv-and-egg-files-d2709eb1604c

class BiopredynMCMonitor(MemcachedMonitor):
    '''
    Abstracts some of the logic of setting up a parameter fitting problem.
    Provides information via MC for monitoring.
    '''

    def getDomain(self):
        return 'com.how2cell.sabaody.biopredyn.{}'.format(self.getName())


    def getNameQualifier(self):
        from toolz import partial
        from sabaody import getQualifiedName
        return partial(getQualifiedName, 'biopredyn', self.getName(), str(self.run))

class BiopredynConfiguration(BenchmarkLauncherBase):
    @classmethod
    def from_cmdline_args(cls, app_name, udp_constructor, getDefaultParamValues, sbmlfile, spark_files, py_files):
        from os.path import join
        result = super(BiopredynConfiguration,cls).from_cmdline_args(app_name, spark_files, py_files)
        result.app_name = app_name
        result.sbmlfile = sbmlfile
        result.udp_constructor = udp_constructor
        result.getDefaultParamValues = getDefaultParamValues
        return result


    def monitor(self, name, host, port, run=None):
        return BiopredynMCMonitor(name, host, port, run=None)



class BioPreDynUDP:
    def __init__(self, lb, ub, sbml_file):
        # type: (Evaluator, array, array) -> None
        '''
        Inits the problem with an objective evaluator
        (implementing the method evaluate), the parameter
        vector lower bound (a numpy array) and upper bound.
        Both bounds must have the same dimension.
        '''
        from sabaody.utils import check_vector, expect
        check_vector(lb)
        check_vector(ub)
        expect(len(lb) == len(ub), 'Bounds mismatch')
        self.lb = lb
        self.ub = ub
        # delay loading until we're on the worker node
        self.evaluator = None
        self.sbml_file = sbml_file


    # derived classes need method 'fitness'


    def get_bounds(self):
        return (self.lb,self.ub)


    def get_name(self):
        return 'Sabaody udp'


    def get_extra_info(self):
        return 'Sabaody extra info'


    def __getstate__(self):
        return {
          'lb': self.lb,
          'ub': self.ub,
          'sbml_file': self.sbml_file}


    def __setstate__(self, state):
        self.lb = state['lb']
        self.ub = state['ub']
        self.sbml_file = state['sbml_file']
        # lazy init
        self.evaluator = None
