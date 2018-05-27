from __future__ import print_function, division, absolute_import

from toolz import partial
from numpy import array, array_equal
import arrow
from pytest import fixture

from uuid import uuid4
from time import sleep
import sys

# Tornado fixtures

@fixture
def app():
    from sabaody.migration_central import create_central_migration_service
    return create_central_migration_service()

# Unit tests

def test_migration_client(mocker):
    '''
    Test the client methods, including define_migrant_pool and push_migrant.
    requests.post is patched so post requests are never actually sent.
    '''
    mocker.patch('requests.post')
    from sabaody.migration_central import CentralMigrator
    # url doesn't matter, requests never sent
    m = CentralMigrator('http://www.schneierfacts.com:10100')

    island_id = uuid4()
    m.define_migrant_pool(island_id, 4)
    from requests import post
    if sys.version_info >= (3,6):
        post.assert_called_once()
    post.reset_mock()
    m.push_migrant(island_id, array([1., 2., 3., 4.]), 1.)
    if sys.version_info >= (3,6):
        post.assert_called_once()
    post.reset_mock()

def test_migration_buffer():
    '''
    Test the logic for the migration buffers: verify the length
    of migrant vectors.
    '''
    from sabaody.migration_central import FIFOMigrationBuffer
    b = FIFOMigrationBuffer(buffer_size=3, param_vector_size=3)
    b.push(array([1., 2., 3.]))
    b.push(array([4., 5., 6.]))
    b.push(array([7., 8., 9.]))
    migrants = b.pop(3)
    assert len(migrants) == 3
    assert array_equal(migrants[0], array([7., 8., 9.]))

def test_migration_host():
    '''
    Test the logic for the migration host server, including garbage collection.
    '''
    from sabaody.migration_central import MigrationServiceHost
    m = MigrationServiceHost(param_vector_size=3)
    m.defineMigrantPool(str(uuid4()), 3, 'FIFO', arrow.utcnow().shift(microseconds=+1))
    assert len(m._migrant_pools) == 1
    sleep(1) # make sure island expires
    m.garbageCollect()
    assert len(m._migrant_pools) == 0


def test_migration_replacement_policy_integration(base_url):
    '''
    Test migration replacement policy.
    '''
    from sabaody.migration_central import CentralMigrator
    m = CentralMigrator(base_url)