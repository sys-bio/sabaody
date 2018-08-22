from __future__ import print_function, division, absolute_import

from numpy import array, array_equal

from uuid import uuid4
from time import sleep

def test_migration_replacement_policy_integration():
    '''
    Test migration replacement policy.
    '''
    from sabaody.migration_central import CentralMigrator, start_migration_service
    from sabaody.migration import BestSPolicy, FairRPolicy, sort_by_fitness
    from sabaody.utils import arrays_equal
    from pygmo import population, rosenbrock
    try:
        process = start_migration_service()
        sleep(2)
        m = CentralMigrator(None, FairRPolicy(), None, 'http://localhost:10100')

        island1 = uuid4()
        island2 = uuid4()

        m.defineMigrantPool(island1, 3)
        m.defineMigrantPool(island2, 3)

        # migrants to island 1
        m.migrate(island1, array([1.,1.,1.]), 1., 'manual1')
        m.migrate(island1, array([2.,2.,2.]), 2., 'manual1')
        # population for island 1
        p1 = population(prob=rosenbrock(3), size=0, seed=0)
        p1.push_back(array([9.,0.,1.]), array([3.]))
        p1.push_back(array([9.,0.,2.]), array([4.]))

        # migrants to island 2
        m.migrate(island2, array([3.,3.,3.]), 3.5, 'manual2')
        m.migrate(island2, array([4.,4.,4.]), 4.5, 'manual2')
        # population for island 2
        p2 = population(prob=rosenbrock(3), size=0, seed=0)
        p2.push_back(array([9.,9.,1.]), array([3.]))
        p2.push_back(array([9.,9.,2.]), array([4.]))

        migrants,fitness,src_island_id = m.welcome(island1)
        assert array_equal(migrants, array([
          [2.,2.,2.],
          [1.,1.,1.],
          ]))
        assert array_equal(fitness, array([
          [2.],
          [1.]]))
        assert src_island_id == ['manual1', 'manual1']
        # some parts of the code use loops like this
        # (zip-type looping with 2d arrays), so make sure it works
        for candidate,f in zip(migrants,fitness):
            assert float(f) in (1.,2.)
            assert array_equal(candidate, array([2.,2.,2.])) or array_equal(candidate, array([1.,1.,1.]))

        # re-push the migrants
        m.migrate(island1, array([1.,1.,1.]), 1.)
        m.migrate(island1, array([2.,2.,2.]), 2.)

        deltas,src_ids = m.replace(island1, p1)
        assert array_equal(sort_by_fitness(p1)[0], array([
                           [1.,1.,1.],
                           [2.,2.,2.]]))
        assert deltas == [-3.,-1.]

        # test island 2
        deltas,src_ids = m.replace(island2, p2)
        assert array_equal(sort_by_fitness(p2)[0], array([
                           [9.,9.,1.],
                           [3.,3.,3.]]))

    finally:
        process.terminate()