from __future__ import print_function, division, absolute_import

from numpy import array, array_equal, sort

def test_selection_replacement_policies():
    '''
    Test the replacement and selection policies.
    '''
    from sabaody.migration import BestSPolicy, FairRPolicy, sort_by_fitness
    from pygmo import population, rosenbrock
    # rosenbrock with dim 3 is just to suppress errors from pagmo, never evaluated
    p = population(prob=rosenbrock(3), size=0, seed=0)
    # create a fake population
    p.push_back(array([10.,11., 12.]), array([4.]))
    p.push_back(array([1.,  2.,  3.]), array([1.]))
    p.push_back(array([7.,  8.,  9.]), array([3.]))
    p.push_back(array([4.,  5.,  6.]), array([2.]))

    # test selection
    s = BestSPolicy(2)
    candidates,candidate_f = s.select(p)
    # test that selected candidates are top two
    assert array_equal(candidates, array([
      [1., 2., 3.],
      [4., 5., 6.]]))
    assert array_equal(candidate_f, array([
      [1.],
      [2.]]))
    # test rate vs fraction
    s2 = BestSPolicy(pop_fraction=0.5)
    # shoud be same number of candidates either way
    assert s2.select(p)[0].shape[0] == candidates.shape[0] == 2

    # test replacement
    p2 = population(prob=rosenbrock(3), size=0, seed=0)
    p2.push_back(array([9.,9.,9.]), array([5.]))
    p2.push_back(array([8.,9.,9.]), array([6.]))
    p2.push_back(array([7.,9.,9.]), array([7.]))
    p2.push_back(array([6.,9.,9.]), array([8.]))

    r = FairRPolicy()
    # should replace worst two decision vectors
    r.replace(p2,candidates,candidate_f)
    sorted_candidates,sorted_f = sort_by_fitness(p2)
    assert array_equal(sorted_candidates, array([
        [1.,2.,3.],
        [4.,5.,6.],
        [9.,9.,9.],
        [8.,9.,9.]]))
    assert array_equal(sorted_f, array([
        [1.],
        [2.],
        [5.],
        [6.]]))

def test_uniform_migration_policy():
    '''
    Test the uniform migration policy.
    '''
    from sabaody.topology import TopologyFactory
    topology_factory = TopologyFactory(None, island_size=5, migrant_pool_size=5)
    topology = topology_factory.createBidirChain(None, number_of_islands=3)
    assert len(topology.island_ids) == 3
    assert len(topology.endpoints) == 2

    middle_node = topology.island(tuple(set(topology.island_ids) - set(topology.endpoints))[0])
    assert len(topology.neighbor_ids(middle_node.id)) == 2

    migrants = array([[9.]*4]*5)
    fitness = array([[0.]]*5)
    from sabaody.migration import MigrationPolicyUniform
    uniform_policy = MigrationPolicyUniform()

    from numpy import vstack
    all_migrants = vstack(
      map(
      lambda x: x[1],
      uniform_policy.disperse(middle_node.id, topology, migrants, fitness)))
    assert array_equal(all_migrants, array([
        [9.,9.,9.,9.],
        [9.,9.,9.,9.],
        [9.,9.,9.,9.],
        [9.,9.,9.,9.],
        [9.,9.,9.,9.]]))