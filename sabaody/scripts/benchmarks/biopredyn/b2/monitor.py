# rosenbrock monitor
from __future__ import print_function, division, absolute_import

from sabaody import getQualifiedName
from sabaody.timecourse.timecourse_launcher import print_out_status

from asciimatics.screen import Screen
from toolz import partial
from pymemcache.client.base import Client
mc_host = 'luna'
mc_port = 11211
client = Client((mc_host,mc_port))

import argparse
parser = argparse.ArgumentParser(description='Run monitor.')
parser.add_argument('app',
                    help='The app to monitor, e.g. b2-driver.')
args = parser.parse_args()
app = args.app

def domainJoin(s,*args):
    return '.'.join(['com.how2cell.sabaody.biopredyn.'+app,str(s),*list(str(a) for a in args)])

domain_qualifier = partial(getQualifiedName, 'biopredyn', app)

Screen.wrapper(partial(print_out_status, client, domainJoin, domain_qualifier))
