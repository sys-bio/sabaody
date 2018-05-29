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
        sleep(1)
        m = CentralMigrator('http://localhost:10100')

        island1 = uuid4()
        island2 = uuid4()

        m.define_migrant_pool(island1, 3)
        m.define_migrant_pool(island2, 3)

        # migrants to island 1
        m.push_migrant(island1, array([1.,1.,1.]), 1.)
        m.push_migrant(island1, array([2.,2.,2.]), 2.)
        # population for island 1
        p1 = population(prob=rosenbrock(3), size=0, seed=0)
        p1.push_back(array([9.,0.,1.]), array([3.]))
        p1.push_back(array([9.,0.,2.]), array([4.]))

        # migrants to island 2
        m.push_migrant(island2, array([3.,3.,3.]), 3.)
        m.push_migrant(island2, array([4.,4.,4.]), 4.)
        # population for island 2
        p2 = population(prob=rosenbrock(3), size=0, seed=0)
        p2.push_back(array([9.,9.,1.]), array([3.5]))
        p2.push_back(array([9.,9.,2.]), array([4.5]))

        migrants,fitness = m.pull_migrants(island1)
        assert array_equal(migrants, array([
          [2.,2.,2.],
          [1.,1.,1.],
          ]))
        assert array_equal(fitness, array([
          [2.],
          [1.]]))

        # re-push the migrants
        m.push_migrant(island1, array([1.,1.,1.]), 1.)
        m.push_migrant(island1, array([2.,2.,2.]), 2.)

        m.replace(island1, p1, FairRPolicy())
        assert array_equal(sort_by_fitness(p1)[0], array([
                           [1.,1.,1.],
                           [2.,2.,2.]]))

    finally:
        process.terminate()