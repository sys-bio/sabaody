# B2 monitor
from __future__ import print_function, division, absolute_import

from sabaody import getQualifiedName

from toolz import partial
from pymemcache.client.base import Client
mc_host = 'luna'
mc_port = 11211
client = Client((mc_host,mc_port))

from time import sleep
from json import dumps, loads

while True:
    run = int(client.get('com.how2cell.sabaody.B2.run'))
    run_id = client.get('com.how2cell.sabaody.B2.runId')
    if run_id:
        domain_qualifier = partial(getQualifiedName, 'B2', str(run_id))
        def get(*args):
            return client.get(domain_qualifier(*args))
        island_ids = loads(get('islandIds') or '[]')
        print('Run {}'.format(run))
        print('  id: {}'.format(str(run_id)))
        print('  island ids: {}'.format(island_ids))
    else:
        print('No run id')
    sleep(1)