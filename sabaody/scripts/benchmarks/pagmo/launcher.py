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
    def _create_arg_parser(cls):
        parser = super(PagmobenchLauncher,cls)._create_arg_parser()
        parser.add_argument('--dimension', type=int,
                            help='Dimension of the test problem.')
        parser.add_argument('--cutoff', type=float,
                            help='The RMSD cutoff between the fitted and known values at which to stop the fitting procedure.')
        return parser

    @classmethod
    def from_cmdline_args(cls, app_name, problem, spark_files, py_files, terminator):
        from os.path import join
        result = super(PagmobenchLauncher,cls).from_cmdline_args(app_name, spark_files, py_files)
        result.dimension = self.args.dimension
        result.cutoff = self.args.cutoff
        result.app_name = app_name
        result.problem = problem
        result.udp = None
        result.terminator=terminator(self.dimension, self.cutoff)
        return result


    def monitor(self, name, host, port, run=None):
        return PagmobenchMCMonitor(name, host, port, run=None)
