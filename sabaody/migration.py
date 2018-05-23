from __future__ import print_function, division, absolute_import

from numpy import argsort

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
    def replace(self, population):
        pass

# ** Policies **
class TopCandidateSelectionPolicy(SelectionPolicyBase):
    '''
    Selection policy based on the top N individuals in the population.
    '''
    def __init__(self, pop_fraction):
        self.pop_fraction = pop_fraction

    def select(self, population):
        indices = argsort(population.get_f(), axis=0)
        n_migrants = int(indices.size*self.pop_fraction)
        # WARNING: single objective only
        return population.get_x()[indices[:n_migrants,0]]