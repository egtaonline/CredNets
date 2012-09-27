from Graphs import *

from itertools import combinations
from random import choice
from sys import modules
from functools import partial

from numpy.random import multinomial, uniform
from numpy import zeros


def ErdosRenyiGraph(n, p=0.05):
	"""Each possiblfe edge is included with probability p."""
	nodes = range(n)
	edges = filter(lambda x: uniform(0,1) < p, combinations(nodes, 2))
	return UndirectedGraph(nodes, edges)


def BarabasiAlbertGraph(n, d):
	"""Preferential atachment graph on n nodes; most nodes have degree >= d."""
	nodes = range(n)
	edges = set()
	degrees = zeros(n)
	for node in nodes:
		degrees[node] += 1
		new_edges = set()
		while degrees[node] <= d and degrees[node] <= node:
			neighbor = list(multinomial(1, degrees / degrees.sum())).index(1)
			e = (node, neighbor)
			if e in new_edges:
				continue
			new_edges.add(e)
			degrees[neighbor] += 1
			degrees[node] += 1
		edges.update(new_edges)
	return UndirectedGraph(nodes, edges)


def UniformSpanningTree(n):
	"""Uniform spanning tree over the complete graph on n edges."""
	new_nodes = range(n)
	tree_nodes = set()
	edges = set()
	first_node = new_nodes.pop(choice(new_nodes))
	tree_nodes.add(first_node)
	while len(tree_nodes) < n:
		src_node = choice(new_nodes)
		path = [src_node]
		while src_node in new_nodes:
			tree_nodes.add(src_node)
			new_nodes.pop(new_nodes.index(src_node))
			dst_node = choice(range(n))
			while dst_node in path:
				dst_node = choice(range(n))
			edges.add(Edge(src_node, dst_node))
			path.append(dst_node)
			src_node = dst_node
	Graph.__init__(self, tree_nodes, edges)


def ERGd(n, d):
	return ErdosRenyiGraph(n, float(d)/n)

for i in range(1,11):
	setattr(modules[__name__], 'ERGd'+str(i), partial(ERGd, d=i))


def BAGd(n, d):
	return BarabasiAlbertGraph(n, (d+1)/2)

for i in range(2,11):
	setattr(modules[__name__], 'BAGd'+str(i), partial(BAGd, d=i))



def BalancedBinaryTree(n):
	return UndirectedGraph(range(n), [(i, (i-1)/2) for i in range(1,n)])


def LineGraph(n):
	return UndirectedGraph(range(n), [(i, i+1) for i in range(n-1)])


def RingGraph(n):
	return UndirectedGraph(range(n), [(i, i+1) for i in range(n-1)] + [(n-1,0)])


def EmptyGraph(n):
	return UndirectedGraph(range(n))


def CompleteGraph(n):
	return UndirectedGraph(range(n), combinations(range(n), 2))


def RandomEdgeDirections(graph):
	edges = []
	for src, dst in set(map(lambda e: tuple(sorted(e)), graph.allEdges())):
		if uniform(0,1) < 0.5:
			edges.append((src, dst))
		else:
			edges.append((dst, src))
	return DirectedGraph(graph.nodes, edges)


def AddWeights(graph):
	edges = [(e[0], e[1], 1) for e in graph.allEdges()]
	return WeightedDirectedGraph(graph.nodes, edges)


