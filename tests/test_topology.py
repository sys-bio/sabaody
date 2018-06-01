from __future__ import print_function, division, absolute_import

from sabaody import getQualifiedName

from toolz import partial

class Problem:
    pass

domain_qual = partial(getQualifiedName, 'com.how2cell.sabaody.test')

def test_one_way_ring():
    '''
    Test the one way ring topology.
    '''
    from sabaody.topology import TopologyFactory
    topology_factory = TopologyFactory(Problem, domain_qual, 'localhost', 11211)

    t = topology_factory.createOneWayRing(4)
    assert len(t.island_ids) == 4
    for id in t.island_ids:
        # should be two neighbors, but one-way migration
        assert len(t.neighbor_islands(id)) == len(t.neighbor_ids(id)) == 2
        assert len(t.outgoing_islands(id)) == len(t.outgoing_ids(id)) == 1
        # outgoing node should be in neighbors
        assert frozenset(t.outgoing_ids(id)) < frozenset(t.neighbor_ids(id))
        assert frozenset(t.outgoing_islands(id)) < frozenset(t.neighbor_islands(id))