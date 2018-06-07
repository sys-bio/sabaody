from __future__ import print_function, division, absolute_import

from sabaody import getQualifiedName

from numpy import array
from toolz import partial
from time import sleep

from itertools import islice

class NoProblem:
    pass

def count_nodes_with_degree(topology, degree):
    '''
    Counts the number of nodes with a given degree.
    '''
    total = 0
    for n in topology:
        if topology.degree[n] == degree:
            total += 1
    return total

def test_one_way_ring_topology():
    '''
    Test the one way ring topology.
    '''
    from sabaody.topology import TopologyFactory
    domain_qual = partial(getQualifiedName, 'com.how2cell.sabaody.test_one_way_ring_topology')
    topology_factory = TopologyFactory(NoProblem, domain_qual, 'localhost', 11211)

    t = topology_factory.createOneWayRing(None,4)
    assert len(t.island_ids) == 4
    assert len(t.islands) == 4
    for island,id in zip(t.islands,t.island_ids):
        assert island.id == id
    for id in t.island_ids:
        # should be two neighbors, but one-way migration
        assert len(t.neighbor_islands(id)) == len(t.neighbor_ids(id)) == 2
        assert len(t.outgoing_islands(id)) == len(t.outgoing_ids(id)) == 1
        # outgoing node should be in neighbors
        assert frozenset(t.outgoing_ids(id)) < frozenset(t.neighbor_ids(id))
        assert frozenset(t.outgoing_islands(id)) < frozenset(t.neighbor_islands(id))

def test_rim_topology():
    '''
    Test the rim topology.
    '''
    from sabaody.topology import TopologyFactory
    domain_qual = partial(getQualifiedName, 'com.how2cell.sabaody.test_rim_topology')
    topology_factory = TopologyFactory(NoProblem, domain_qual, 'localhost', 11211)

    t = topology_factory.createRim(None,5)
    assert len(t.island_ids) == 5
    assert len(t.islands) == 5
    # hub
    assert count_nodes_with_degree(t,4) == 1
    # adjacent to hub
    assert count_nodes_with_degree(t,2) == 2
    # not adjacent to hub
    assert count_nodes_with_degree(t,3) == 2

def count_hits(islands):
    '''
    Counts the number of islands which have hit the
    global minimum.
    '''
    return sum(1 for i in islands if i.get_population().champion_f[0] == 0.)

def hits_contiguous(islands,topology):
    '''
    Returns true if the hits are contiguous. See :ref:`count_hits`.
    '''
    sg_nodes = tuple(id for id in topology.nodes if islands[id].get_population().champion_f[0] == 0.)

def seed_island(i):
    '''
    Seed an island (i.e. set the value of one decision vector)
    with the global minimum of the Rosenbrock function.
    '''
    p = i.get_population()
    n = p.get_x().shape[1]
    p.set_x(0,array([1.]*n))
    i.set_population(p)

def seed_first(islands,topology):
    '''
    If the topology has defined endpoints, use the first one.
    Otherwise, use an arbitrary point (works for rings).
    '''
    if hasattr(topology,'endpoints'):
        seed_island(islands[topology.endpoints[0]])
    else:
        # arbitrary, works for e.g. ring
        seed_island(tuple(islands.values())[0])

def seed_last(islands,topology):
    '''
    Seed the last endpoint.
    '''
    seed_island(islands[topology.endpoints[-1]])

def seed_predecessor(islands,topology):
    seed_island(islands[tuple(topology.predecessors(tuple(islands.keys())[0]))[0]])

def test_one_way_ring_migration():
    '''
    Tests the migration on a one way ring.
    '''
    from sabaody.topology import TopologyFactory

    def make_problem():
        import pygmo as pg
        return pg.problem(pg.rosenbrock(3))

    def make_algorithm():
        return pg.de(gen=10)

    domain_qual = partial(getQualifiedName, 'com.how2cell.sabaody.test_one_way_ring_migration')
    topology_factory = TopologyFactory(make_problem, domain_qual, 'localhost', 11211)
    topology = topology_factory.createOneWayRing(make_algorithm,5)
    assert len(topology.island_ids) == 5

    from sabaody.migration_central import CentralMigrator, start_migration_service
    from sabaody.migration import BestSPolicy, FairRPolicy, sort_by_fitness
    import pygmo as pg
    try:
        process = start_migration_service()
        sleep(2)
        migrator = CentralMigrator('http://localhost:10100', BestSPolicy(migration_rate=1), FairRPolicy())

        from collections import OrderedDict
        islands = OrderedDict((i.id, pg.island(algo=i.algorithm_constructor(),
                                     prob=i.problem_constructor(),
                                     size=i.size)) for i in topology.islands)
        for island_id in islands.keys():
            migrator.defineMigrantPool(island_id, 3)
        # seed solution in one island
        seed_first(islands,topology)
        assert count_hits(islands.values()) == 1

        for n in range(1,5+1):
            assert count_hits(islands.values()) == n
            # perform migration
            for island_id,i in islands.items():
                migrator.sendMigrants(island_id, i, topology)
            for island_id,i in islands.items():
                deltas,src_ids = migrator.receiveMigrants(island_id, i, topology)
        assert n==5

        # reset & differentiate from chain
        islands = OrderedDict((i.id, pg.island(algo=i.algorithm_constructor(),
                                     prob=i.problem_constructor(),
                                     size=i.size)) for i in topology.islands)
        seed_predecessor(islands,topology)
        # perform migration
        for island_id,i in islands.items():
            migrator.sendMigrants(island_id, i, topology)
        for island_id,i in islands.items():
            deltas,src_ids = migrator.receiveMigrants(island_id, i, topology)
        assert tuple(islands.values())[0].get_population().champion_f[0] == 0.
        assert count_hits(islands.values()) == 2
    finally:
        process.terminate()

def test_bidir_chain():
    '''
    Tests the migration on a one way chain.
    '''
    from sabaody.topology import TopologyFactory

    def make_problem():
        import pygmo as pg
        return pg.problem(pg.rosenbrock(3))

    def make_algorithm():
        return pg.de(gen=10)

    domain_qual = partial(getQualifiedName, 'com.how2cell.sabaody.test_bidir_chain_migration')
    topology_factory = TopologyFactory(make_problem, domain_qual, 'localhost', 11211)
    topology = topology_factory.createBidirChain(make_algorithm,5)
    assert len(topology.island_ids) == 5
    assert len(topology.endpoints) == 2

    from sabaody.migration_central import CentralMigrator, start_migration_service
    from sabaody.migration import BestSPolicy, FairRPolicy, sort_by_fitness
    import pygmo as pg
    try:
        process = start_migration_service()
        sleep(2)
        migrator = CentralMigrator('http://localhost:10100', BestSPolicy(migration_rate=1), FairRPolicy())

        from collections import OrderedDict
        for k in (1,2):
            islands = OrderedDict((i.id, pg.island(algo=i.algorithm_constructor(),
                                        prob=i.problem_constructor(),
                                        size=i.size)) for i in topology.islands)
            for island_id in islands.keys():
                migrator.defineMigrantPool(island_id, 3)
            if k == 1:
                # test forward migration
                seed_first(islands,topology)
            else:
                # test reverse migration
                seed_last(islands,topology)

            for n in range(1,5+1):
                assert count_hits(islands.values()) == n
                # perform migration
                for island_id,i in islands.items():
                    migrator.sendMigrants(island_id, i, topology)
                for island_id,i in islands.items():
                    deltas,src_ids = migrator.receiveMigrants(island_id, i, topology)
            migrator.purgeAll()
    finally:
        process.terminate()