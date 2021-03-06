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
    g = TopologyGenerator(n_islands = 10, island_size = 10, migrant_pool_size=5)

    from pygmo import de, nlopt

    # should have 5 islands with de and 5 with nelder mead
    assert sum(type(i.algorithm) is de for i in roundtrip(g.find_by_desc('Bidirectional ring, de+nelder mead')).topology.islands) == 5
    assert sum(type(i.algorithm) is nlopt for i in roundtrip(g.find_by_desc('Bidirectional ring, de+nelder mead')).topology.islands) == 5
