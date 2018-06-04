from __future__ import print_function, division, absolute_import

from sabaody import getQualifiedName

from numpy import array
from toolz import partial
from time import sleep

from itertools import islice

class NoProblem:
    pass

def test_one_way_ring():
    '''
    Test the one way ring topology.
    '''
    from sabaody.topology import TopologyFactory
    domain_qual = partial(getQualifiedName, 'com.how2cell.sabaody.test_one_way_ring')
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

def count_hits(islands):
    '''
    Counts the number of islands which have hit the
    global minimum.
    '''
    return sum(1 for i in islands if i.get_population().champion_f[0] == 0.)

def seed_at(islands,index,n):
    i = tuple(islands.values())[index]
    p = i.get_population()
    p.set_x(0,array([1.]*n))
    i.set_population(p)

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
        sleep(1)
        migrator = CentralMigrator('http://localhost:10100', BestSPolicy(migration_rate=1), FairRPolicy())

        from collections import OrderedDict
        islands = OrderedDict((i.id, pg.island(algo=i.algorithm_constructor(),
                                     prob=i.problem_constructor(),
                                     size=i.size)) for i in topology.islands)
        for island_id in islands.keys():
            migrator.defineMigrantPool(island_id, 3)
        # seed solution in one island
        seed_at(islands,0,3)
        assert count_hits(islands.values()) == 1

        n=1
        for i1,i2 in zip(islands.values(),islice(islands.values(),1,None)):
            assert i1.get_population().champion_f[0] < 0.1*i2.get_population().champion_f[0]
            assert count_hits(islands.values()) == n
            n+=1
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
        seed_at(islands,-1,3)
        # perform migration
        for island_id,i in islands.items():
            migrator.sendMigrants(island_id, i, topology)
        for island_id,i in islands.items():
            deltas,src_ids = migrator.receiveMigrants(island_id, i, topology)
        assert tuple(islands.values())[0].get_population().champion_f[0] == 0.
        assert count_hits(islands.values()) == 2
    finally:
        process.terminate()

#def test_bidir_chain():
    #'''
    #Tests the migration on a one way chain.
    #'''
    #from sabaody.topology import TopologyFactory

    #def make_problem():
        #import pygmo as pg
        #return pg.problem(pg.rosenbrock(3))

    #def make_algorithm():
        #return pg.de(gen=10)

    #domain_qual = partial(getQualifiedName, 'com.how2cell.sabaody.test_bidir_chain')
    #topology_factory = TopologyFactory(make_problem, domain_qual, 'localhost', 11211)
    #topology = topology_factory.createBidirChain(make_algorithm,5)
    #assert len(topology.island_ids) == 5

    #from sabaody.migration_central import CentralMigrator, start_migration_service
    #from sabaody.migration import BestSPolicy, FairRPolicy, sort_by_fitness
    #import pygmo as pg
    #try:
        #process = start_migration_service()
        #sleep(1)
        #migrator = CentralMigrator('http://localhost:10100', BestSPolicy(migration_rate=1), FairRPolicy())

        #from collections import OrderedDict
        #islands = OrderedDict((i.id, pg.island(algo=i.algorithm_constructor(),
                                     #prob=i.problem_constructor(),
                                     #size=i.size)) for i in topology.islands)
        #for island_id in islands.keys():
            #migrator.defineMigrantPool(island_id, 3)
        ## forward migration
        #seed_at(islands,0,3)

        #n=1
        #for i1,i2 in zip(islands.values(),islice(islands.values(),1,None)):
            #assert i1.get_population().champion_f[0] < 0.1*i2.get_population().champion_f[0]
            #assert count_hits(islands.values()) == n
            #n+=1
            ## perform migration
            #for island_id,i in islands.items():
                #migrator.sendMigrants(island_id, i, topology)
            #for island_id,i in islands.items():
                #deltas,src_ids = migrator.receiveMigrants(island_id, i, topology)
        #assert n==5
    #finally:
        #process.terminate()