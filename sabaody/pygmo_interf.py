from __future__ import print_function, division, absolute_import

from .utils import expect, check_vector

from pymemcache.client.base import Client

from abc import ABC, abstractmethod
from numpy import array
from typing import SupportsFloat
from uuid import uuid4


class Evaluator(ABC):
    """
    Evaluates an objective function.
    Required to implement at least the functino evaluate,
    which returns a double precision float.
    """
    @abstractmethod
    def evaluate(self):
        # type: () -> SupportsFloat
        """Evaluates the objective function."""
        pass


class Problem:
    def __init__(self, evaluator, lb, ub):
        # type: (Evaluator, array, array) -> None
        """
        Inits the problem with an objective evaluator
        (implementing the method evaluate), the parameter
        vector lower bound (a numpy array) and upper bound.
        Both bounds must have the same dimension.
        """
        check_vector(lb)
        check_vector(ub)
        expect(len(lb) == len(ub), 'Bounds mismatch')
        self.evaluator = evaluator
        self.lb = lb
        self.ub = ub

    def fitness(self, x):
        return evaluator.evaluate(x)

    def get_bounds(self):
        return (lb,ub)

class Island:
    def __init__(self, id, problem):
        self.id = id
        self.problem = problem

class Archipelago:
    def __init__(self, num_islands, problem, topology, mc_host, mc_port=11211):
        self.num_islands = num_islands
        self.problem = problem
        self.topology = topology
        self.mc_host = mc_host
        self.mc_port = mc_port
        self.mc_client = Client((mc_host,mc_port))
        uuids = (uuid4() for x in range(self.num_islands))
        self.islands = sc.parallelize(uuids).map(lamda u: Island(u, self.problem))
        print(self.islands.map(lambda i: i.id).collect())

