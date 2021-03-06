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
from random import choice, randint
from typing import Union, Callable

class AlgorithmCtorFactory(ABC):
    '''
    A base class for constructing algorithms.
    If the algorithm you wish to use depends on properties
    of the topology (such as node degree etc.), you can
    derive from this class to construct your own algorithm
    per island.
    It is called during topology creation with the node (island)
    and topology.
    '''
    @abstractmethod
    def __call__(self,island,topology):
        pass

class Topology(nx.Graph):
    '''
    nx.Graph with additional convenience methods.
    '''

    def island(self, id):
        return self.nodes[id]['island']


    def neighbor_ids(self, id):
        return tuple(self.neighbors(id))


    def predicated_node_search_with_origin(self, p, origin_id, max_depth, visited=None):
        if visited is None:
            visited = set(origin_id)
        nodes = set()
        if max_depth > 0:
            for id in self.neighbor_ids(origin_id):
                nodes += self.predicated_node_search_with_origin(p, id, max_depth-1)
        return (set(origin_id) if p(origin_id) else set()) + \
                nodes


    def compute_every_other_id(self):
        if len(self.islands) < 1:
            return []
        boundary = frozenset({self.island_ids[0]})
        visited = boundary
        toggle = True
        result = set()

        def sprout_and_continue(nodes):
            result = set()
            for n in nodes:
                if len(self.neighbor_ids(n)) > 2:
                    raise RuntimeError('every_other_id only works for linear or cyclic graphs')
                result.update(node for node in self.neighbor_ids(n) if node not in visited)
            return result

        while len(boundary)>0:
            if toggle:
                result.update(boundary)
                toggle = False
            else:
                toggle = True
            boundary = sprout_and_continue(boundary)
            visited = visited.union(boundary)
            if len(boundary) > 2:
                raise RuntimeError('every_other_id only works for linear or cyclic graphs')

        return tuple(result)


    def every_other_island(self):
        return tuple(self.nodes[n]['island'] for n in self.every_other_id)


    def outgoing_ids(self, id):
        '''
        For an undirected topology, the outgoing ids are just
        the neighbor ids.
        '''
        return tuple(self.neighbors(id))



    def neighbor_islands(self, id):
        return tuple(self.nodes[n]['island'] for n in self.neighbors(id))


    def outgoing_islands(self, id):
        return self.neighbor_islands(id)


class FullyConnectedTopology(Topology):
    pass


class DiTopology(nx.DiGraph,Topology):
    '''
    nx.DiGraph with additional convenience methods.
    '''

    def outgoing_ids(self, id):
        '''
        For a directed topology, the outgoing ids can be
        different from the incomming ids.
        '''
        return tuple(self.successors(id))

    def outgoing_islands(self, id):
        return tuple(self.nodes[n]['island'] for n in self.successors(id))

    def neighbor_ids(self, id):
        return tuple(chain(self.successors(id),self.predecessors(id)))

    def incoming_ids(self , id):
        node_list = []
        for each_node in list(self.nodes):
            if id in list(self.neighbors(each_node)):
                node_list.append(each_node)
        return node_list

    def neighbor_islands(self, id):
        return tuple(self.nodes[n]['island'] for n in chain(self.successors(id),self.predecessors(id)))


class TopologyFactory:
    '''
    Has methods for constructing a variety of topologies.
    '''

    def __init__(self, island_size = 20, migrant_pool_size = 5, domain_qualifier=None, mc_host=None, mc_port=None, seed=None):
        self.domain_qualifier = domain_qualifier
        self.mc_host = mc_host
        self.mc_port = mc_port
        self.island_size = island_size
        self.seed = seed


    def getSeed(self, seed=None):
        if seed is not None:
            return seed
        elif self.seed is not None:
            return self.seed
        else:
            return randint(0,10000)


    # DEPRECATED
    def _getAlgorithmConstructor(self, algorithm, node, graph):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int, Union[nx.Graph,nx.DiGraph]) -> Callable[[],pg.algorithm]
        '''
        If algorithm is a factory, call it with the node and graph.
        If instead it is a list of constructors, choose one at random.
        If it is simply a direct constructor for a pagmo algorithm,
        just return it.
        '''
        if isinstance(algorithm, AlgorithmCtorFactory):
            return algorithm(node, graph)
        elif isinstance(algorithm, collections.abc.Sequence):
            return choice(algorithm)
        else:
            return algorithm


    def _processTopology(self,raw,algorithm,topology_class,compute_every_other_id=False,every_other_id=None):
        '''
        Converts a graph of indices (generated by nxgraph) into a topology
        of island ids.
        '''
        m = dict((k,Island(str(uuid4()),
                           algorithm,
                           self.island_size,
                           self.domain_qualifier,
                           self.mc_host,
                           self.mc_port)) for k in raw.nodes)
        g = topology_class()
        g.add_nodes_from(island.id for island in m.values())
        for k,i in m.items():
            g.nodes[m[k].id]['island'] = m[k]
        g.add_edges_from((m[u].id, m[v].id)
                         for u, nbrs in raw._adj.items()
                         for v, data in nbrs.items())
        g.island_ids = tuple(id for id in g.nodes)
        g.islands = tuple(g.nodes[i]['island'] for i in g.nodes)
        if compute_every_other_id:
            g.every_other_id = g.compute_every_other_id()
        elif every_other_id is not None:
            g.every_other_id = tuple(m[k].id for k in every_other_id)
        return g


    @classmethod
    def prefixIds(self,topology,prefix):
        topology_class = topology.__class__
        m = {id: topology.nodes[id]['island'] for id in topology.nodes}
        g = topology_class()
        g.add_nodes_from(prefix+island.id for island in m.values())
        for k,i in m.items():
            g.nodes[prefix+m[k].id]['island'] = m[k]
        g.add_edges_from((prefix+m[u].id, prefix+m[v].id)
                         for u, nbrs in topology._adj.items()
                         for v, data in nbrs.items())
        g.island_ids = tuple(id for id in g.nodes)
        g.islands = tuple(g.nodes[i]['island'] for i in g.nodes)
        for i in g.islands:
            i.id = prefix+i.id
        return g

    def _assignHub(self,t):
        t.hub = list(sorted(t.islands, key = lambda i: len(tuple(t.neighbors(i.id)))))[0]
        return t


    def createOneWayRing(self, algorithm, number_of_islands = 100):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int) -> DiTopology
        '''
        Creates a one way ring topology.
        '''
        g = self._processTopology(nx.cycle_graph(number_of_islands, create_using=nx.DiGraph()), algorithm, DiTopology, compute_every_other_id=True)
        return g


    def createBidirRing(self, algorithm, number_of_islands = 100):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int) -> DiTopology
        '''
        Creates a bidirectional ring topology.
        '''
        g = self._processTopology(nx.cycle_graph(number_of_islands, create_using=nx.Graph()), algorithm, Topology, compute_every_other_id=True)
        return g


    def createBidirChain(self, algorithm, number_of_islands = 100):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int) -> Topology
        '''
        Creates a linear chain topology.
        '''
        g = self._processTopology(nx.path_graph(number_of_islands, create_using=nx.Graph()), algorithm, Topology, compute_every_other_id=True)
        # label head and tail nodes
        endpoints = set()
        for n in g.nodes:
            if len(tuple(g.neighbors(n))) == 1:
                endpoints.add(g.nodes[n]['island'])
        g.endpoints = tuple(endpoints)
        return g


    def createLollipop(self, algorithm, complete_subgraph_size = 100, chain_size = 10):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int, int) -> Topology
        '''
        Creates a topology from a lollipop graph.
        '''
        # TODO: chain should be one-way
        g = self._processTopology(nx.lollipop_graph(complete_subgraph_size, chain_size, create_using=nx.Graph()), algorithm, Topology)
        # label tail nodes
        endpoints = set()
        for n in g.nodes:
            if len(tuple(g.neighbors(n))) == 1:
                endpoints.add(g.nodes[n]['island'])
        g.endpoints = tuple(endpoints)
        return g


    def createRim(self, algorithm, number_of_islands = 100):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int) -> Topology
        '''
        Creates a rim topology (ring with all nodes connected to a single node).
        '''
        g = self._processTopology(nx.cycle_graph(number_of_islands, create_using=nx.Graph()), algorithm, Topology, compute_every_other_id=True)
        g.hub = tuple(g.nodes)[0]
        for n in g.nodes:
            if n != g.hub:
                g.add_edge(n,g.hub)
        return g


    def create_12_Ring(self, algorithm, number_of_islands = 100):
        '''
        Creates a 1-2 ring, where every node in the ring is connected to
        its neighbors and the neighbors of its neighbors.
        '''
        g = nx.Graph()
        g.add_nodes_from(range(1, number_of_islands + 1))
        for each_island in range(1, number_of_islands + 1):
            for step in range(1,3):
                to_edge = each_island + step
                if to_edge > number_of_islands:
                    to_edge = to_edge % number_of_islands
                g.add_edge(each_island,to_edge)
        return self._processTopology(g, algorithm, Topology, every_other_id=range(1, number_of_islands + 1, 2))


    def create_123_Ring(self, algorithm, number_of_islands = 100):
        '''
        Creates a 1-2-3 ring, where every node in the ring is connected to
        its neighbors, the neighbors of its neighbors, and nodes three steps away.
        '''
        g = nx.Graph()
        g.add_nodes_from(range(1, number_of_islands + 1))
        for each_island in range(1, number_of_islands + 1):
            for step in range(1, 4):
                to_edge = each_island + step
                if to_edge > number_of_islands:
                    to_edge = to_edge % number_of_islands
                g.add_edge(each_island, to_edge)
        return self._processTopology(g, algorithm, Topology, every_other_id=range(1, number_of_islands + 1, 2))


    def createFullyConnected(self, algorithm, number_of_islands = 100):
        '''
        A fully connected (complete) topology.
        '''
        return  self._processTopology(nx.complete_graph(number_of_islands, create_using=nx.Graph()), algorithm, FullyConnectedTopology)


    def createBroadcast(self, algorithm, number_of_islands = 100, central_node = 1):
        '''
        A collection of islands not connected to each other but
        connected to a central node.
        '''
        g = nx.Graph()
        g.add_nodes_from(range(1, number_of_islands + 1))
        for each_island in range(1,number_of_islands+1):
            if central_node == each_island:
                continue
            g.add_edge(central_node,each_island)
        return self._processTopology(g, algorithm, Topology)


    def createHypercube(self, algorithm, dimension = 10):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int) -> Topology
        '''
        Creates a hypercube topology.
        '''
        return self._processTopology(nx.hypercube_graph(dimension), algorithm, Topology)


    def createWattsStrogatz(self, algorithm, num_nodes=100, k=10, p=0.1, seed = None):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int, int, float, int) -> Topology
        '''
        Creates a Watts Strogatz topology - a ring lattice (i.e. a ring of n nodes each connected to k
        neighbors) in which the rightmost k/2 nodes are rewired with probability p.
        These graphs tend to exhibit high clustering and short average path lengths.
        `See also: PaGMO's description. <http://esa.github.io/pygmo/documentation/topology.html>`_
        '''
        seed = self.getSeed(seed)
        return self._processTopology(nx.watts_strogatz_graph(num_nodes,k,p,seed), algorithm, Topology)


    def createErdosRenyi(self, algorithm, num_nodes=100, p=0.1, directed = False, seed = None):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int, float, bool, int) -> Topology
        '''
        Creates a topology based on an Erdős-Rényi random graph.
        '''
        seed = self.getSeed(seed)
        return self._processTopology(nx.erdos_renyi_graph(num_nodes,p,seed,directed), algorithm, Topology)


    def createBarabasiAlbert(self, algorithm, num_nodes=100, m=3, seed = None):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int, int, int) -> Topology
        '''
        Creates a topology based on a Barabási-Albert graph.
        '''
        seed = self.getSeed(seed)
        return self._assignHub(self._processTopology(nx.barabasi_albert_graph(num_nodes,m,seed), algorithm, Topology))


    def createExtendedBarabasiAlbert(self, algorithm, num_nodes=100, m=3, p=0.3, q=0.1, seed = None):
        # type: (Union[AlgorithmCtorFactory,collections.abc.Sequence,Callable[[],pg.algorithm]], int, int, float, float, int) -> Topology
        '''
        Creates a topology based on the extended Barabási-Albert method.
        '''
        seed = self.getSeed(seed)
        return self._assignHub(self._processTopology(nx.extended_barabasi_albert_graph(num_nodes,m,p,q,seed), algorithm, Topology))


    def createAgeingExtendedBarabasiAlbert(self, algorithm, n=100, m=10, p=0.3, q=0.1, max_age=10, seed = None):
        '''
        Create an extended Barabási-Albert graph with ageing.
        Ageing means that nodes older than max_age do not continue to receive connections as the network expands.
        Adapted from networkx source code.
        '''
        import random
        from networkx.generators.random_graphs import _random_subset
        seed = self.getSeed(seed)

        if m < 1 or m >= n:
            msg = "Extended ageing Barabasi-Albert network needs m>=1 and m<n, m=%d, n=%d"
            raise nx.NetworkXError(msg % (m, n))
        if p + q >= 1:
            msg = "Extended ageing Barabasi-Albert network needs p + q <= 1, p=%d, q=%d"
            raise nx.NetworkXError(msg % (p, q))
        if seed is not None:
            random.seed(seed)

        # Add m initial nodes (m0 in barabasi-speak)
        G = nx.empty_graph(m)

        # List of nodes to represent the preferential attachment random selection.
        # At the creation of the graph, all nodes are added to the list
        # so that even nodes that are not connected have a chance to get selected,
        # for rewiring and adding of edges.
        # With each new edge, nodes at the ends of the edge are added to the list.
        attachment_preference = []
        attachment_preference.extend(range(m))

        def has_young_neighbor(node):
            for neighbor in G[node]:
                if neighbor > new_node-max_age:
                    return True
            return False

        # Start adding the other n-m nodes. The first node is m.
        new_node = m
        while new_node < n:
            a_probability = random.random()

            # Total number of edges of a Clique of all the nodes
            clique_degree = len(G) - 1
            clique_size = (len(G) * clique_degree) / 2

            # Adding m new edges, if there is room to add them
            if a_probability < p and G.size() <= clique_size - m:
                # Select the nodes where an edge can be added
                elligible_nodes = [nd for nd, deg in G.degree()
                                  if deg < clique_degree and nd > new_node-max_age]
                for i in range(m):
                    # Choosing a random source node from elligible_nodes
                    src_node = random.choice(elligible_nodes)

                    # Picking a possible node that is not 'src_node' or
                    # neighbor with 'src_node', with preferential attachment
                    prohibited_nodes = list(G[src_node])
                    prohibited_nodes.append(src_node)
                    # This will raise an exception if the sequence is empty
                    dest_node = random.choice([nd for nd in attachment_preference
                                              if nd not in prohibited_nodes and nd > new_node-max_age])
                    # Adding the new edge
                    G.add_edge(src_node, dest_node)

                    # Appending both nodes to add to their preferential attachment
                    attachment_preference.append(src_node)
                    attachment_preference.append(dest_node)

                    # Adjusting the elligible nodes. Degree may be saturated.
                    if G.degree(src_node) == clique_degree:
                        elligible_nodes.remove(src_node)
                    if G.degree(dest_node) == clique_degree \
                            and dest_node in elligible_nodes:
                        elligible_nodes.remove(dest_node)

            # Rewiring m edges, if there are enough edges
            elif p <= a_probability < (p + q) and m <= G.size() < clique_size:
                # Selecting nodes that have at least 1 edge but that are not
                # fully connected to ALL other nodes (center of star).
                # These nodes are the pivot nodes of the edges to rewire
                elligible_nodes = [nd for nd, deg in G.degree()
                                  if 0 < deg < clique_degree and has_young_neighbor(nd)]
                for i in range(m):
                    # Choosing a random source node
                    node = random.choice(elligible_nodes)

                    # The available nodes do have a neighbor at least.
                    neighbor_nodes = [nd for nd in G[node] if nd > new_node-max_age]

                    # Choosing the other end that will get dettached
                    src_node = random.choice(neighbor_nodes)

                    # Picking a target node that is not 'node' or
                    # neighbor with 'node', with preferential attachment
                    neighbor_nodes.append(node)
                    dest_node = random.choice([nd for nd in attachment_preference
                                              if nd not in neighbor_nodes and nd > new_node-max_age])
                    # Rewire
                    G.remove_edge(node, src_node)
                    G.add_edge(node, dest_node)

                    # Adjusting the preferential attachment list
                    attachment_preference.remove(src_node)
                    attachment_preference.append(dest_node)

                    # Adjusting the elligible nodes.
                    # nodes may be saturated or isolated.
                    if G.degree(src_node) == 0 and src_node in elligible_nodes:
                        elligible_nodes.remove(src_node)
                    if dest_node in elligible_nodes:
                        if G.degree(dest_node) == clique_degree:
                            elligible_nodes.remove(dest_node)
                    else:
                        if G.degree(dest_node) == 1:
                            elligible_nodes.append(dest_node)

            # Adding new node with m edges
            else:
                # Select the edges' nodes by preferential attachment
                targets = _random_subset([nd for nd in attachment_preference if nd > new_node-max_age], m, random)
                G.add_edges_from(zip([new_node] * m, targets))

                # Add one node to the list for each new edge just created.
                attachment_preference.extend(targets)
                # The new node has m edges to it, plus itself: m + 1
                attachment_preference.extend([new_node] * (m + 1))
                new_node += 1
        return self._assignHub(self._processTopology(G, algorithm, Topology))

    def fromNetworkxGraph(self, algorithm, g, directed=False):
        '''
        Create a custom topology from a networkx graph.
        '''
        return self._processTopology(g, algorithm, DiTopology if directed else Topology)
