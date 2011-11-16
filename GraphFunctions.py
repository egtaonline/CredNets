from Graphs import *
from itertools import permutations, combinations
from random import choice, random
from numpy.random import multinomial


class ErdosRenyiGraph(Graph):
	"""Each possible edge is included with probability p."""
	def __init__(self, n):
		p = 5.0/n
		nodes = range(n)
		edges = filter(lambda x: random() < p, combinations(nodes, 2))
		Graph.__init__(self, nodes, [Edge(*e) for e in edges])


class ErdosRenyiByDegree(ErdosRenyiGraph):
	def __init__(self, n, d=5):
		ErdosRenyiGraph.__init__(self, n, 2.0* d / n)


class BarabasiAlbertGraph(Graph):
	"""Preferential atachment graph on n nodes; most nodes have degree >= d."""
	def __init__(self, n, d=5):
		Graph.__init__(self, [0], [])
		while len(self.nodes) < n:
			s = len(self.getAllEdges()) + len(self.nodes)
			node_index = len(self.nodes)
			self.addNode(node_index)
			for edge in self.chooseEdges(node_index, d):
				self.addEdge(edge)

	def chooseEdges(self, node_index, d):
		if node_index <= d:
			return (Edge(node_index, i) for i in range(node_index))
		s = float(2*len(self.getAllEdges()) + len(self.nodes))
		probs = [(self.getOutDegree(n) + 1) / s for n in range(node_index)]
		edges = set()
		while len(edges) < d and len(edges) < node_index:
			edges.add(Edge(node_index, list(multinomial(1, probs)).index(1)))
		return edges


class UniformSpanningTree(Graph):
	"""Uniform spanning tree over the complete graph on n edges."""
	def __init__(self, n, *args):
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


class BalancedBinaryTree(Graph):
	def __init__(self, n, *args):
		Graph.__init__(self, range(n), [Edge(i, (i-1)/2) for i in range(1,n)])


class LineGraph(Graph):
	def __init__(self, n, *args):
		Graph.__init__(self, range(n), [Edge(i, i+1) for i in range(n-1)])


class EmptyGraph(Graph):
	def __init__(self, n, *args):
		Graph.__init__(self, range(n))


class CompleteGraph(Graph):
	def __init__(self, n, *args):
		Graph.__init__(self, range(n), [Edge(*e) for e in \
				permutations(range(n), 2)])


from optparse import OptionParser
if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-n", "--nodes", help="number of nodes in the graph", \
			default=60)
	parser.add_option("-d", "--degree", help="average degree of each node", \
			default=5)
	parser.add_option("-s", "--statistic", help="graph statistic to compute", \
			default="averageDegree")
	options, args = parser.parse_args()
	assert args[0] in vars(), "unrecognized graph type: " + args[0]
	g = eval(args[0] +"("+ str(options.nodes) +","+ str(options.degree) +")")
	print(g)
	print(options.statistic, "=", eval("g." + options.statistic + "()"))

