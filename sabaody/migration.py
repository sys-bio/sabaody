from __future__ import print_function, division, absolute_import

from numpy import argsort, flipud

from abc import ABC, abstractmethod

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
    indices = argsort(candidates, axis=0)
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
class Migrator:
    pass