from __future__ import print_function, division, absolute_import

from numpy import array, array_equal

def test_migration_policies():
    '''
    Test the client methods, including define_migrant_pool and push_migrant.
    '''
    from sabaody.migration import TopCandidateSelectionPolicy
    from pygmo import population, rosenbrock
    p = population(prob=rosenbrock(3), size=0, seed=0)
    p.push_back(array([10.,11., 12.]), array([4.]))
    p.push_back(array([1.,  2.,  3.]), array([1.]))
    p.push_back(array([7.,  8.,  9.]), array([3.]))
    p.push_back(array([4.,  5.,  6.]), array([2.]))

    policy = TopCandidateSelectionPolicy(0.5)
    assert array_equal(policy.select(p), array([
      [1., 2., 3.],
      [4., 5., 6.]]))