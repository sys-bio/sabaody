from __future__ import print_function, division, absolute_import

from sabaody.benchmark_launcher import MemcachedMonitor, BenchmarkLauncherBase

import json

class PagmobenchMCMonitor(MemcachedMonitor):

    def getDomain(self):
        return 'com.how2cell.sabaody.pagmobench.{}'.format(self.getName())


    def getNameQualifier(self):
        from toolz import partial
        from sabaody import getQualifiedName
        return partial(getQualifiedName, 'pagmobench', self.getName(), str(self.run))

class PagmobenchLauncher(BenchmarkLauncherBase):
    @classmethod
    def from_cmdline_args(cls, app_name, problem, spark_files, py_files):
        from os.path import join
        result = super(PagmobenchLauncher,cls).from_cmdline_args(app_name, spark_files, py_files)
        result.app_name = app_name
        result.problem = problem
        result.udp = None
        return result


    def monitor(self, name, host, port, run=None):
        return PagmobenchMCMonitor(name, host, port, run=None)
