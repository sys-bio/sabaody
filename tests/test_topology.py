from __future__ import print_function, division, absolute_import

from sabaody import getQualifiedName

from toolz import partial
from time import sleep

class NoProblem:
    pass

def test_one_way_ring():
    '''
    Test the one way ring topology.
    '''
    from sabaody.topology import TopologyFactory
    domain_qual = partial(getQualifiedName, 'com.how2cell.sabaody.test_one_way_ring')
    topology_factory = TopologyFactory(NoProblem, domain_qual, 'localhost', 11211)

    t = topology_factory.createOneWayRing(4)
    assert len(t.island_ids) == 4
    for id in t.island_ids:
        # should be two neighbors, but one-way migration
        assert len(t.neighbor_islands(id)) == len(t.neighbor_ids(id)) == 2
        assert len(t.outgoing_islands(id)) == len(t.outgoing_ids(id)) == 1
        # outgoing node should be in neighbors
        assert frozenset(t.outgoing_ids(id)) < frozenset(t.neighbor_ids(id))
        assert frozenset(t.outgoing_islands(id)) < frozenset(t.neighbor_islands(id))

def test_one_way_ring_migration():
    '''
    Tests the migration on a one way ring.
    '''
    from sabaody.topology import TopologyFactory

    def make_problem():
        import pygmo as pg
        return pg.problem(pg.rosenbrock(5))

    domain_qual = partial(getQualifiedName, 'com.how2cell.sabaody.test_one_way_ring_migration')
    topology_factory = TopologyFactory(make_problem, domain_qual, 'localhost', 11211)
    t = topology_factory.createOneWayRing(5)
    assert len(t.island_ids) == 5

    from sabaody.migration_central import CentralMigrator, start_migration_service
    from sabaody.migration import BestSPolicy, FairRPolicy, sort_by_fitness
    try:
        process = start_migration_service()
        sleep(1)
        m = CentralMigrator('http://localhost:10100', BestSPolicy(migration_rate=10), FairRPolicy())
    finally:
        process.terminate()