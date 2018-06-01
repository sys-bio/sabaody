# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley
from __future__ import print_function, division, absolute_import

from .pygmo_interf import Island

import networkx as nx
import pygmo as pg

from itertools import chain
from abc import ABC, abstractmethod
from uuid import uuid4
import collections
from random import choice
from typing import Union, Callable

class AlgorithmCtorFactory(ABC):
    @abstractmethod
    def __call__(self,island,topology):
        pass

class Topology(nx.Graph):
    def neighbor_ids(self, id):
        return tuple(chain(self.successors(id),self.predecessors(id)))

    def neighbor_islands(self, id):
        return tuple(self.nodes[n]['island'] for n in chain(self.successors(id),self.predecessors(id)))

class DiTopology(nx.DiGraph,Topology):
    def outgoing_ids(self, id):
        return tuple(self.successors(id))

    def outgoing_islands(self, id):
        return tuple(self.nodes[n]['island'] for n in self.successors(id))

class TopologyFactory:
    def __init__(self, problem_constructor, domain_qualifier, mc_host, mc_port=11211):
        self.problem_constructor = problem_constructor
        self.domain_qualifier = domain_qualifier
        self.mc_host = mc_host
        self.mc_port = mc_port

    def _getAlgorithmConstructor(self, algorithm_factory, node, graph):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int, Union[nx.Graph,nx.DiGraph]) -> Callable[[],pg.algorithm]
        '''
        If algorithm_factory is a factory, call it with the node and graph.
        If instead it is a list of constructors, choose one at random.
        If it is simply a direct constructor for a pagmo algorithm,
        just return it.
        '''
        if isinstance(algorithm_factory, AlgorithmCtorFactory):
            return algorithm_factory(node, graph)
        elif isinstance(algorithm_factory, collections.abc.Sequence):
            return choice(algorithm_factory)
        else:
            return algorithm_factory

    def _addExtraAttributes(self,g):
        g.island_ids = tuple(id for id in g.nodes)
        g.islands = tuple(g.nodes[i]['island'] for i in g.nodes)

    def createOneWayRing(self, algorithm_factory, number_of_islands = 100, island_size = 20):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int, int) -> nx.Graph
        '''
        Creates a one way ring topology.
        '''
        raw = nx.cycle_graph(number_of_islands, create_using=nx.DiGraph())
        m = dict((k,Island(str(uuid4()),
                           self.problem_constructor,
                           self._getAlgorithmConstructor(algorithm_factory,k,raw),
                           island_size,
                           self.domain_qualifier,
                           self.mc_host,
                           self.mc_port)) for k in raw.nodes)
        g = DiTopology()
        g.add_nodes_from(island.id for island in m.values())
        for k,i in m.items():
            g.nodes[m[k].id]['island'] = m[k]
        g.add_edges_from((m[u].id, m[v].id)
                         for u, nbrs in raw._adj.items()
                         for v, data in nbrs.items())
        self._addExtraAttributes(g)
        return g


    #@staticmethod
    #def create_chain(number_of_islands = 4):
        #archipelago = nx.DiGraph()
        #archipelago.add_nodes_from(range(1, number_of_islands + 1))
        #for each_island in range(1, number_of_islands):
            #archipelago.add_edge(each_island, (each_island + 1))
        #return archipelago


    #@staticmethod
    #def create_ring(number_of_islands=4):
        #archipelago = nx.Graph()
        #archipelago.add_nodes_from(range(1, number_of_islands + 1))
        #for each_island in range(1, number_of_islands + 1):
            #if each_island == number_of_islands:
                #archipelago.add_edge(each_island,1)
            #else:
                #archipelago.add_edge(each_island, (each_island + 1))
        #return archipelago


    #@staticmethod
    #def create_1_2_ring(number_of_islands = 4):
        #archipelago = nx.Graph()
        #archipelago.add_nodes_from(range(1, number_of_islands + 1))
        #for each_island in range(1, number_of_islands + 1):

            #for step in range(1,3):
                #to_edge = each_island + step
                #if to_edge > number_of_islands:
                    #to_edge = to_edge % number_of_islands
                #archipelago.add_edge(each_island,to_edge)

        #return archipelago


    #@staticmethod
    #def create_1_2_3_ring(number_of_islands=4):
        #archipelago = nx.Graph()
        #archipelago.add_nodes_from(range(1, number_of_islands + 1))
        #for each_island in range(1, number_of_islands + 1):

            #for step in range(1, 4):
                #to_edge = each_island + step
                #if to_edge > number_of_islands:
                    #to_edge = to_edge % number_of_islands
                #archipelago.add_edge(each_island, to_edge)

        #return archipelago


    #@staticmethod
    #def create_fully_connected(number_of_islands=4):
        #archipelago = nx.Graph()
        #archipelago.add_nodes_from(range(1, number_of_islands + 1))
        #all_edges = itertools.combinations(range(1,number_of_islands+1),2)
        #archipelago.add_edges_from(all_edges)
        #return  archipelago


    #@staticmethod
    #def create_broadcast(number_of_islands = 4, central_node=1):
        #archipelago = nx.Graph()
        #archipelago.add_nodes_from(range(1, number_of_islands + 1))
        #for each_island in range(1,number_of_islands+1):
            #if central_node == each_island:
                #continue
            #archipelago.add_edge(central_node,each_island)
        #return archipelago


    #def add_edge(self,from_node,to_node,weight=0):
        #if self.directed:
            #self.topology.add_edge(from_node,to_node,weight = weight)
        #else:
            #self.topology.add_edge(from_node,to_node)








