from __future__ import print_function, division, absolute_import

from .topology import Topology, DiTopology

from numpy import array, argsort, flipud, ndarray, vstack
import pygmo as pg
import attr
import arrow
from functools import reduce

from abc import ABC, abstractmethod
from typing import Union, Tuple, List, Any

def convert_to_2d_array(array_or_list):
    # type: (Union[ndarray,List[ndarray]]) -> ndarray
    '''
    Convert ``array_or_list`` into a 2d array.
    ``array_or_list`` can be a list of decision vectors,
    a single decision vector, or a 2d (in which case
    it is returned as-is).
    '''
    if isinstance(array_or_list,list):
        for m in array_or_list:
            if not isinstance(m,ndarray):
                raise RuntimeError('`array_or_list` should be a list of ndarrays, instead found element of type {}'.format(type(m)))
            if not (m.ndim < 2 or (m.ndim == 2 and m.shape[0] == 1)):
                raise RuntimeError('Received 2d array for migrant - array_or_list should be 1d arrays or row vectors')
        return vstack(tuple(m for m in array_or_list))
    elif isinstance(array_or_list,ndarray):
        if array_or_list.ndim == 1:
            return array_or_list.reshape((1,-1))
        elif array_or_list.ndim == 2:
            return array_or_list
        else:
            raise RuntimeError('Wrong n dims for array_or_list: {}'.format(array_or_list.ndim))
    else:
        raise RuntimeError('Wrong type for array_or_list - should be list or ndarray but received {}'.format(type(array_or_list)))

@attr.s
class MigrantData:
    migrants = attr.ib(type=array)
    fitness = attr.ib(type=array)
    timestamp = attr.ib(type=arrow.Arrow, converter=arrow.get) # type: ignore
    src_id = attr.ib(type=str)

# vstack with empties
def myvstack(u,v):
    if u is None or u.shape == (0,):
        return v
    elif v is None or v.shape == (0,):
        return u
    else:
        return vstack([u,v])

def truncate(a,n):
    if a.shape[0] > n:
        return array(a[:n,:])
    else:
        return a

def truncate_list(l,n):
    if len(l) > n:
        return list(l[:n])
    else:
        return l

def to_migrant_tuple(migrants, n):
    def reducer(a,m):
        marray, farray, sid = a
        if marray.shape[0] < n or n == 0:
            return (myvstack(marray,m.migrants),
                    myvstack(farray,m.fitness),
                    sid + [m.src_id])
        else:
            return (marray, farray, sid)

    migrant_array, fitness_array, source_ids = reduce(reducer, migrants, (array([]),array([]),[])) # type: ignore

    return (truncate(migrant_array,n), truncate(fitness_array,n), truncate_list(source_ids,n))

class MigrationPolicyBase(ABC):
    '''
    Controls how migrants are dispersed.
    '''
    @abstractmethod
    def disperse(self, island_id, topology, candidates, candidate_f):
        pass

class SelectionPolicyBase(ABC):
    '''
    Selects migrants to be sent to other islands.
    '''
    @abstractmethod
    def select(self, population):
        pass

class ReplacementPolicyBase(ABC):
    '''
    Policy controlling whether to replace an individual
    in a population with a migrant.
    '''
    @abstractmethod
    def replace(self, population, candidates, candidate_f):
        pass

def sort_by_fitness(population):
    '''
    Returns a tuple of the decision vectors and corresponding
    fitness values, both sorted according to fitness (best
    first).
    '''
    indices = argsort(population.get_f(), axis=0)
    return (population.get_x()[indices[:,0]],
            population.get_f()[indices[:,0]])

def sort_candidates_by_fitness(candidates,candidate_f):
    if candidates.size == 0:
        assert candidate_f.size == 0
        return (candidates,candidate_f)
    assert len(candidate_f.shape) == 2
    assert candidate_f.shape[1] == 1
    indices = argsort(candidate_f, axis=0)
    return (candidates[indices[:,0]],
            candidate_f[indices[:,0]])

# ** Migration Policies **

class MigrationPolicyEachToAll(MigrationPolicyBase):
    '''
    A migration policy that sends the migration candidates to all
    connected islands, resulting in duplication of the candidates
    for every connected island. This speeds convergence at the
    cost of population diversity.
    '''
    def disperse(self, island_id, topology, candidates, candidate_f):
        for connected_island in topology.outgoing_ids(island_id):
            yield connected_island, candidates, candidate_f

class MigrationPolicyUniform(MigrationPolicyBase):
    '''
    Uniformly distributes the migration candidates among the
    connected islands. Since the number of candidates is discrete,
    the dispersal pattern is random.
    '''
    # TODO: add support for weights
    def disperse(self, island_id, topology, candidates, candidate_f):
        if len(candidates.shape) <= 1:
            assert len(candidate_f.shape) == len(candidates.shape)
            from numpy import reshape
            candidates = reshape(candidates,(1,-1))
            candidate_f = reshape(candidate_f,(1,-1))
        total_num_migrants = candidates.shape[0]
        # pick the neighbors to receive migrants based on the total number of migrants
        from numpy.random import choice
        choices = choice(topology.outgoing_ids(island_id), total_num_migrants)
        # get each destination and the number of migrants to send to it
        from numpy import unique
        neighbors,counts = unique(choices, return_counts=True)
        # send migrants to the respective neighbors
        k=0
        for neighbor,num_migrants in zip(neighbors,counts):
            yield (neighbor,candidates[k:k+num_migrants,:],candidate_f[k:k+num_migrants,:])
            k += num_migrants

# ** Selection Policies **
class BestSPolicy(SelectionPolicyBase):
    '''
    Selection policy.
    Selects the best N individuals from a population.
    '''
    def __init__(self, migration_rate=None, pop_fraction=None):
        if migration_rate is None and pop_fraction is None:
            raise RuntimeError('Must specify migration as a rate or fraction.')
        elif migration_rate is not None and pop_fraction is not None:
            raise RuntimeError('Cannot specify both migration rate and fraction.')
        self.migration_rate = migration_rate
        self.pop_fraction = pop_fraction

    def select(self, population):
        '''
        Selects the top pop_fraction*population_size
        individuals and returns them as a 2D array
        (different vectors are in different rows).
        Cannot be used with multiple objectives - partial
        order is requred.

        The returned array of candidates should be sorted descending
        according to best fitness value.
        '''
        indices = argsort(population.get_f(), axis=0)
        n_migrants = self.migration_rate or int(indices.size*self.pop_fraction)
        # WARNING: single objective only
        return (population.get_x()[indices[:n_migrants,0]],
                population.get_f()[indices[:n_migrants,0]])

# ** Replacement Policies **
class FairRPolicy(ReplacementPolicyBase):
    '''
    Fair replacement policy.
    Replaces the worst N individuals in the population if the
    candidates are better.
    '''

    def replace(self, population, candidates, candidate_f):
        '''
        Replaces the worst N individuals in the population if the
        candidates are better.

        :return: The deltas of the replacements made
        :param candidates: Numpy 2D array with candidates in rows.
        '''
        # sort candidates
        candidates,candidate_f = sort_candidates_by_fitness(candidates,candidate_f)
        #print(candidates,candidate_f)
        assert len(candidates.shape) == len(candidate_f.shape)
        indices = flipud(argsort(population.get_f(), axis=0))
        pop_f = population.get_f()
        deltas = []
        for i,k,f in zip(indices[:,0],range(len(candidate_f)),candidate_f):
            if f < pop_f[i,0]:
                #print('candidates {}'.format(candidates[k,:]))
                #print('f {}'.format(f))
                population.set_xf(int(i),candidates[k,:],f)
                deltas.append(float(f - pop_f[i,0]))
            else:
                pass
                # break
        return deltas

# ** Migration Policies **
class Migrator(ABC):
    '''
    Base class for migrator implementations (e.g. Kafka, centralized).
    '''

    def __init__(self, migration_policy, selection_policy, replacement_policy):
        self.migration_policy = migration_policy
        self.selection_policy = selection_policy
        self.replacement_policy = replacement_policy

    def sendMigrants(self, island_id, island, topology):
        # type: (str, pg.island, Union[Topology,DiTopology]) -> None
        '''
        Sends migrants from a pagmo island to other connected islands.
        '''
        pop = island.get_population()
        candidates,candidate_f = self.selection_policy.select(pop)
        #for connected_island in topology.outgoing_ids(island_id):
        for connected_island,outgoing_candidates,outgoing_f in self.migration_policy.disperse(island_id, topology, candidates, candidate_f):
            self._migrate(connected_island, outgoing_candidates, outgoing_f, src_island_id=island_id)


    def receiveMigrants(self, island_id, island, topology):
        # type: (str, pg.island, Union[Topology,DiTopology]) -> Tuple[List,List]
        '''
        Receives migrants from other islands.
        '''
        pop = island.get_population()
        deltas,src_ids = self.replace(island_id, pop)
        island.set_population(pop)
        return (deltas,src_ids)


    def replace(self, island_id, population):
        # type: (str, pg.population) -> Tuple[List,List]
        '''
        Replace migrants in the specified population with candidates
        in the pool according to the specified policy.
        '''
        candidates,candidate_f,src_ids = self._welcome(island_id)
        return (self.replacement_policy.replace(population,candidates,candidate_f),src_ids)

    @abstractmethod
    def _migrate(self, dest_island_id, migrants, fitness, src_island_id=None, *args, **kwars):
        # type: (str, ndarray, ndarray, str, *Any, **Any) -> None
        '''
        Send migrants to a single island. Meant to be called by sendMigrants.
        '''
        pass

    @abstractmethod
    def _welcome(self, island_id, n=0):
        # type: (ndarray, int) -> Tuple[ndarray,ndarray,List[str]]
        '''
        Return all incoming migrants for island_id if n = 0, or all available
        migrants otherwise. Meant to be called by replace.
        '''
        pass


    def pull_migrants(self,island_id, buffer_length, generation=1):
        from sabaody.kafka_migration_service import KafkaMigrator
        return KafkaMigrator.welcome(island_id,buffer_length,generation)

