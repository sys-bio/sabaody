from __future__ import print_function, division, absolute_import

from sabaody.migration_central import FIFOMigrationBuffer, MigrationServiceHost

from numpy import array, array_equal
import arrow

from uuid import uuid4
from time import sleep

def test_migration_buffer():
    b = FIFOMigrationBuffer(buffer_size=3, param_vector_size=3)
    b.push(array([1., 2., 3.]))
    b.push(array([4., 5., 6.]))
    b.push(array([7., 8., 9.]))
    migrants = b.pop(3)
    assert len(migrants) == 3
    assert array_equal(migrants[0], array([7., 8., 9.]))

def test_migration_host():
    m = MigrationServiceHost(param_vector_size=3)
    m.defineMigrantPool(str(uuid4()), 3, 'FIFO', arrow.utcnow().shift(microseconds=+1))
    assert len(m._migrant_pools) == 1
    sleep(1) # make sure island expires
    m.garbageCollect()
    assert len(m._migrant_pools) == 0