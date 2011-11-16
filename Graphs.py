from heapq import heappush, heappop
from itertools import chain, permutations
from collections import namedtuple


Edge = namedtuple('Edge', 'src dst')
Edge.backEdge = lambda e: Edge(*reversed(e))


WeightedEdge = namedtuple('WeightedEdge', 'src dst weight')
WeightedEdge.edge = lambda e: Edge(*e[:2])


class Graph:
	def __init__(self, nodes=[], edges=[]):
		self.nodes = set()
		self.outEdges = {}
		for node in nodes:
			self.addNode(node)
		for edge in edges:
			self.addEdge(edge)

	def addNode(self, node):
		assert node not in self.nodes, "node already exists"
		self.nodes.add(node)
		self.outEdges[node] = set()

	def addEdge(self, edge):
		for node in edge[:2]:
			assert node in self.nodes, "node " + str(node) + " doesn't exist"
		self.outEdges[edge.src].add(edge)
		self.outEdges[edge.dst].add(edge.backEdge())

	def removeNode(self, node):
		self.removeAllEdges(node)
		self.nodes.remove(node)

	def removeEdge(self, edge):
		self.outEdges[edge.src].remove(edge)
		self.outEdges[edge.dst].remove(edge.backEdge())

	def removeAllEdges(self, node):
		for c in self.getChildren(node):
			self.removeEdge(Edge(node, c))

	def adjacent(self, n0, n1):
		return Edge(n0, n1) in self.outEdges[n0]

	def getAllEdges(self):
		edges = set()
		for node in self.nodes:
			for edge in self.outEdges[node]:
				if edge.backEdge() not in edges:
					edges.add(edge)
		return edges

	def getNeighbors(self, node):
		return [e.dst for e in self.outEdges[node]]

	getParents = getNeighbors
	getChildren = getNeighbors

	def getInDegree(self, node):
		return len(self.getParents(node))

	def getOutDegree(self, node):
		return len(self.getChildren(node))

	def getDegree(self, node):
		return self.getInDegree(node)

	def allNodeDegrees(self):
		return sorted((self.getDegree(n) for n in self.nodes))

	def averageDegree(self):
		return sum(self.allNodeDegrees()) / float(len(self.nodes))

	def minimumDegree(self):
		return self.allNodeDegrees()[0]

	def maximumDegree(self):
		return self.allNodeDegrees()[-1]

	def allPathLengths(self):
		return sorted(filter(lambda p: p, (len(self.shortestPath(o,d)) - 1 \
				for o,d in permutations(self.nodes, 2))))

	def averagePathLength(self):
		path_lengths = self.allPathLengths()
		return sum(path_lengths) / float(len(path_lengths))

	def pathsLongerThan(self, l=2):
		path_lengths = self.allPathLengths()
		long_paths = filter(lambda p: p>l, path_lengths)
		return len(long_paths) / float(len(path_lengths))

	def __eq__(self, other):
		try:
			return self.nodes == other.nodes and self.outEdges == other.outEdges
		except AttributeError:
			return False

	def __hash__(self):
		return hash(tuple(self.getAllEdges()))

	def __repr__(self):
		return self.__class__.__name__ + ': ' + str(len(self.nodes)) + \
				' nodes, ' + str(len(self.getAllEdges())) + ' edges'

	def connectedComponent(self, node):
		"""Return a list of nodes in the same connected component sorted by
		distance from node."""
		cc = [node]
		to_visit = self.getNeighbors(node)
		while len(to_visit) > 0:
			new_node = to_visit.pop(0)
			cc.append(new_node)
			for n in self.getNeighbors(new_node):
				if n not in cc and n not in to_visit:
					to_visit.append(n)
		return cc


	def allPaths(self, origin, destination, max_len=0, path=[]):
		"""Find all paths between origin and destination up to a maximum length.

		note: If max_len<2 (which it is by default) all paths of any length will
		be found.

		return: A list containing lists of nodes along each path including the
				origin and destination.
		"""
		path = path + [origin]
		if origin == destination:
			return [path]
		paths = []
		if max_len < 2:
			max_len = len(self.nodes)
		if len(path) > max_len:
			return paths
		for node in self.getChildren(origin):
			if node not in path:
				newpaths = self.allPaths(node, destination, max_len, path)
				for newpath in newpaths:
					paths.append(newpath)
		return paths

	def undirectedPaths(self, origin, destination, path=[]):
		"""Find all paths between origin and destination.

		return: A list containing lists of nodes along each path including the
				origin and destination.
		"""
		path = path + [origin]
		if origin == destination:
			return [path]
		paths = []
		for node in self.getNeighbors(origin):
			if node not in path:
				newpaths = self.allPaths(node, destination, path)
				for newpath in newpaths:
					paths.append(newpath)
		return paths

	def shortestPath(self, origin, destination, edgeCost=lambda e: 1, \
				heuristic=lambda e: 0):
		""" Find the shortest path between origin and destination.

		The shortest path is found by A* search, so the distance heuristic
		should be admissable (never overestimating). With the default values for
		edgeCost and heuristic, the search reduces to BFS.

		The path is returned as a list of nodes.
		"""
		queue = []
		visited = set()
		pathCosts = {origin:0}
		parents = {origin:None}
		heappush(queue, (0, origin))
		while queue:
			priority, node = heappop(queue)
			if node == destination:
				break
			if node in visited:
				continue
			visited.add(node)
			for childNode in self.getChildren(node):
				if childNode in visited:
					continue
				newPathCost = pathCosts[node] + edgeCost(Edge(node, childNode))
				if childNode in pathCosts:
					if pathCosts[childNode] <= newPathCost:
						continue
				parents[childNode] = node
				pathCosts[childNode] = newPathCost
				heappush(queue, (heuristic(Edge(childNode, destination)) + \
						newPathCost, childNode))
		if node != destination:
			return []
		path = []
		while node != None:
			path = [node] + path
			node = parents[node]
		return path


class DirectedGraph(Graph):
	def __init__(self, nodes=[], edges=[]):
		self.inEdges = {}
		Graph.__init__(self, nodes, edges)

	def addNode(self, node):
		Graph.addNode(self, node)
		self.inEdges[node] = set()

	def addEdge(self, edge):
		for node in edge[:2]:
			assert node in self.nodes, "node " + str(node) + " doesn't exist"
		self.outEdges[edge.src].add(edge)
		self.inEdges[edge.dst].add(edge)

	def removeEdge(self, edge):
		self.outEdges[edge.src].remove(edge)
		self.inEdges[edge.dst].remove(edge)

	def removeAllEdges(self, node):
		Graph.removeAllEdges(self, node)
		for p in self.getParents(node):
			self.removeEdge(Edge(p, node))

	def getParents(self, node):
		return [e.src for e in self.inEdges[node]]

	def getChildren(self, node):
		return [e.dst for e in self.outEdges[node]]

	def getNeighbors(self, node):
		return list(set(self.getParents(node)).union(set(\
				self.getChildren(node))))

	def getAllEdges(self):
		return set(chain(*(edgeList for edgeList in self.outEdges.values())))

	def getDegree(self, node):
		return self.getInDegree(node) + self.getOutDegree(node)


class WeightedDirectedGraph(DirectedGraph):
	def __init__(self, nodes=[], weightedEdges=[]):
		self.weights = dict(((e.edge(), e.weight) for e in weightedEdges))
		DirectedGraph.__init__(self, nodes, weightedEdges)

	def addEdge(self, weightedEdge):
		DirectedGraph.addEdge(self, weightedEdge.edge())
		self.weights[weightedEdge.edge()] = weightedEdge.weight

	def removeEdge(self, edge):
		DirectedGraph.removeEdge(self, edge)
		del self.weights[edge]

	def getEdgeWeight(self, edge):
		return self.weights[edge]

	def getAllEdges(self):
		return [WeightedEdge(e.src, e.dst, self.weights[e]) for e in \
				DirectedGraph.getAllEdges(self)]

	def __eq__(self, other):
		try:
			return Graph.__eq__(self, other) and self.weights == other.weights
		except AttributeError:
			return False


class FlowNetwork(WeightedDirectedGraph):
	def addEdge(self, weightedEdge):
		assert weightedEdge.weight > 0, "capacity must be positive"
		WeightedDirectedGraph.addEdge(self, weightedEdge)

	def getEdgeCapacity(self, edge):
		try:
			return self.weights[edge]
		except KeyError:
			return 0

	def increaseEdgeCapacity(self, edge, additionalCapacity):
		assert additionalCapacity > 0
		try:
			self.weights[edge] += additionalCapacity
		except KeyError:
			self.addEdge(WeightedEdge(edge.src, edge.dst, additionalCapacity))

	def decreaseEdgeCapacity(self, edge, lostCapacity):
		assert lostCapacity > 0
		if lostCapacity > self.getEdgeCapacity(edge):
			raise CapacityError()
		self.weights[edge] -= lostCapacity
		if self.weights[edge] == 0:
			self.removeEdge(edge)

	def routeFlow(self, path, flow):
		try:
			for src, dst in zip(path, path[1:]):
				edge = Edge(src, dst)
				self.decreaseEdgeCapacity(edge, flow)
		except CapacityError as CE:
			for modifiedEdge in zip(path, path[1:]):
				if modifiedEdge == edge:
					raise CE
				self.increaseEdgeCapacity(modifiedEdge, flow)

	def getPathCapacity(self, path):
		"""returns 0 for degenerate paths with length < 2"""
		try:
			minCapacity = self.getEdgeCapacity(Edge(path[0], path[1]))
		except IndexError:
			return 0
		for src, dst in zip(path, path[1:]):
			edgeCapacity = self.getEdgeCapacity(Edge(src, dst))
			if edgeCapacity < minCapacity:
				minCapacity = edgeCapacity
		return minCapacity

	def bidirectionalCapacity(self, path):
		p = list(path)
		p.reverse()
		return self.getPathCapacity(path) + self.getPathCapacity(p)

	def maxFlow(self, source, sink, edgeCost=lambda e: 1, \
			heuristic=lambda e: 0):
		"""Edmonds-Karp algorithm O(|V|*|E|^2)"""
		fn = FlowNetwork(self.nodes, self.getAllEdges())
		flow = 0
		path = fn.shortestPath(source, sink, edgeCost, heuristic)
		while path:
			capacity = fn.getPathCapacity(path)
			fn.routeFlow(path, capacity)
			flow += capacity
			path = fn.shortestPath(source, sink, edgeCost, heuristic)
		return flow

	def findFlowPaths(self, source, sink, amount, edgeCost=lambda e: 1, \
				heuristic=lambda e: 0):
		"""Returns a list of the shortest paths with combined capacity >= amount
		or raises a CapacityError.

		Avoids copying the flow network if the first path found has sufficient
		capacity.
		"""
		assert amount > 0
		path = self.shortestPath(source, sink, edgeCost, heuristic)
		if path:
			capacity = self.getPathCapacity(path)
			if capacity >= amount:
				return [path]
		else:
			raise CapacityError()
		paths = [path]
		flow = capacity
		fn = FlowNetwork(self.nodes, self.getAllEdges())
		fn.routeFlow(path, capacity)
		paths.append(fn.shortestPath(source, sink, edgeCost, heuristic))
		while paths[-1]:
			capacity = fn.getPathCapacity(paths[-1])
			flow += capacity
			if flow >= amount:
				return paths
			fn.routeFlow(paths[-1], capacity)
			paths.append(fn.shortestPath(source, sink, edgeCost, heuristic))
		raise CapacityError()


class CapacityError(Exception):
	def __init__(self):
		Exception.__init__(self, 'insufficient capacity')

