# rosenbrock monitor
from __future__ import print_function, division, absolute_import

from sabaody import getQualifiedName
from sabaody.benchmark_launcher import print_out_status

from asciimatics.screen import Screen
from toolz import partial
from pymemcache.client.base import Client
mc_host = 'luna'
mc_port = 11211
client = Client((mc_host,mc_port))

import argparse
parser = argparse.ArgumentParser(description='Run monitor.')
parser.add_argument('domain', nargs='+',
                    help='The domain and app to monitor, e.g. biopredyn b2-driver.')
args = parser.parse_args()
domain = args.domain

def domainJoin(s,*args):
    return '.'.join(['.'.join(('com.how2cell.sabaody',*domain)),str(s),*list(str(a) for a in args)])

domain_qualifier = partial(getQualifiedName, *domain)

Screen.wrapper(partial(print_out_status, client, domainJoin, domain_qualifier))
