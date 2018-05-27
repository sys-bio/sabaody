from __future__ import print_function, division, absolute_import

from numpy import array, array_equal, sort

def test_migration_policies():
    '''
    Test the client methods, including define_migrant_pool and push_migrant.
    '''
    from sabaody.migration import BestSPolicy, FairRPolicy, sort_by_fitness
    from pygmo import population, rosenbrock
    p = population(prob=rosenbrock(3), size=0, seed=0)
    p.push_back(array([10.,11., 12.]), array([4.]))
    p.push_back(array([1.,  2.,  3.]), array([1.]))
    p.push_back(array([7.,  8.,  9.]), array([3.]))
    p.push_back(array([4.,  5.,  6.]), array([2.]))

    # test selection
    s = BestSPolicy(0.5)
    candidates,candidate_f = s.select(p)
    assert array_equal(candidates, array([
      [1., 2., 3.],
      [4., 5., 6.]]))

    # test replacement
    p2 = population(prob=rosenbrock(3), size=0, seed=0)
    p2.push_back(array([9.,9.,9.]), array([5.]))
    p2.push_back(array([8.,9.,9.]), array([6.]))
    p2.push_back(array([7.,9.,9.]), array([7.]))
    p2.push_back(array([6.,9.,9.]), array([8.]))

    r = FairRPolicy()
    print('candidates')
    print(candidates)
    print('candidate_f')
    print(candidate_f)
    # should replace worst two
    r.replace(p2,candidates,candidate_f)
    assert array_equal(sort_by_fitness(p2)[0], array([
        [1.,2.,3.],
        [4.,5.,6.],
        [9.,9.,9.],
        [8.,9.,9.]]))