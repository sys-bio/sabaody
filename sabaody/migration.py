from __future__ import print_function, division, absolute_import

from .topology import Topology, DiTopology

from numpy import argsort, flipud, ndarray
import pygmo as pg
import arrow

from abc import ABC, abstractmethod
import typing

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
    indices = argsort(candidate_f, axis=0)
    return (candidates[indices[:,0]],
            candidate_f[indices[:,0]])

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
        indices = flipud(argsort(population.get_f(), axis=0))
        pop_f = population.get_f()
        deltas = []
        for i,k,f in zip(indices[:,0],range(len(candidate_f)),candidate_f):
            if f < pop_f[i,0]:
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

    def __init__(self, selection_policy, replacement_policy):
        self.selection_policy = selection_policy
        self.replacement_policy = replacement_policy

    def sendMigrants(self, island_id, island, topology):
        # type: (str, pg.island, typing.Union[Topology,DiTopology]) -> None
        '''
        Sends migrants from a pagmo island to other connected islands.
        '''
        pop = island.get_population()
        candidates,candidate_f = self.selection_policy.select(pop)
        for connected_island in topology.outgoing_ids(island_id):
            for candidate,f in zip(candidates,candidate_f):
                self.pushMigrant(connected_island, candidate, f, src_island_id=island_id)

    def send_migrants(self, island_id, island, topology, generation=1):
        # type: (str, pg.island, typing.Union[Topology,DiTopology], int) -> None
        '''
        Sends migrants from a pagmo island to other connected islands.
        '''
        from sabaody.kafka_migration_service import KafkaMigrator, KafkaBuilder
        pop = island.get_population()
        candidates,candidate_f = self.selection_policy.select(pop)
        migrator = KafkaMigrator(KafkaBuilder('unknown_host','unknown_port'))

        for connected_island in topology.outgoing_ids(island_id):
            migrator.migrate(zip(candidates,candidate_f),island_id,connected_island,generation)


    def receiveMigrants(self, island_id, island, topology):
        # type: (str, pg.island, typing.Union[Topology,DiTopology]) -> typing.Tuple[typing.List,typing.List]
        '''
        Receives migrants from other islands.
        '''
        pop = island.get_population()
        deltas,src_ids = self.replace(island_id, pop)
        island.set_population(pop)
        return (deltas,src_ids)

    def receive_migrants(self,island_id, island, topology, generation =1):

        # type: (str, pg.island, typing.Union[Topology,DiTopology], int) -> typing.Tuple[typing.List,typing.List]
        '''
        Receives migrants from other islands.
        '''
        from sabaody.kafka_migration_service import KafkaMigrator
        incoming_ids = topology.incoming_ids(island_id)
        pop = island.get_population()
        deltas , src_ids = self.replace_migrants(island_id , pop,len(incoming_ids),generation)
        island.set_population(pop)
        return (deltas , src_ids)

    def replace_migrants(self, island_id, population, buffer_length, generation):
        # type: (str, pg.population, int, int) -> typing.Tuple[typing.List,typing.List]
        '''
        Replace migrants in the specified population with candidates
        in the pool according to the specified policy.
        '''
        candidates,candidate_f,src_ids = self.pull_migrants(island_id,buffer_length, generation)
        return (self.replacement_policy.replace(population,candidates,candidate_f),src_ids)



    def replace(self, island_id, population):
        # type: (str, pg.population) -> typing.Tuple[typing.List,typing.List]
        '''
        Replace migrants in the specified population with candidates
        in the pool according to the specified policy.
        '''
        candidates,candidate_f,src_ids = self.pullMigrants(island_id)
        return (self.replacement_policy.replace(population,candidates,candidate_f),src_ids)

    @abstractmethod
    def pushMigrant(self, dest_island_id, migrant_vector, fitness, src_island_id=None, expiration_time=arrow.utcnow().shift(days=+1)):
        # type: (str, ndarray, float, str, arrow.Arrow) -> None
        pass

    @abstractmethod
    def pullMigrants(self, island_id, n=0):
        # type: (ndarray, int) -> typing.Tuple[ndarray,ndarray,typing.List[str]]
        pass


    def pull_migrants(self,island_id, buffer_length, generation=1):
        from sabaody.kafka_migration_service import KafkaMigrator
        return KafkaMigrator.welcome(island_id,buffer_length,generation)

