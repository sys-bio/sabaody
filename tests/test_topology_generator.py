from __future__ import print_function, division, absolute_import

from sabaody import getQualifiedName

from numpy import array
from toolz import partial
from time import sleep

from itertools import islice

def roundtrip(archipelago):
    '''
    Roundtrip an archipelago through Python pickle serializer.
    '''
    from pickle import dumps, loads
    return loads(dumps(archipelago))

def test_topology_generator():
    '''
    Tests the generated topologies.
    Test serialization of archipelago.
    Make sure that combo topologies contain both algorithms.
    '''
    from sabaody.topology_generator import TopologyGenerator
    g = TopologyGenerator(island_size = 10, migrant_pool_size=5)
    g.generate_all(10) # 10 islands

    from pygmo import de, nlopt

    # should have 5 islands with de and 5 with nelder mead
    assert sum(type(i.algorithm) is de for i in roundtrip(g.de_nm_bring['archipelago']).topology.islands) == 5