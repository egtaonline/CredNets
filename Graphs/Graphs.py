from heapq import heappush, heappop

class PathError(Exception):
	def __init__(self):
		Exception.__init__(self, 'origin and destination are disconnected')


class Graph:
	def __init__(self, nodes=[], edges=[]):
		self.nodes = set()
		self.edges = dict()
		for node in nodes:
			self.addNode(node)
		for edge in edges:
			self.addEdge(*edge)

	def addNode(self, node):
		assert node not in self.nodes, "node " +str(node)+ " already exists"
		self.nodes.add(node)
		self.edges[node] = set()

	def removeNode(self, node):
		del self.edges[node]
		map(lambda s: s.discard(node), self.edges.values())
		self.nodes.remove(node)

	def addEdge(self, *args):
		raise NotImplementedError("use DirectedGraph or UndirectedGraph")

	def removeEdge(self, *args):
		raise NotImplementedError("use DirectedGraph or UndirectedGraph")

	def adjacent(self, n1, n2):
		return n2 in self.edges[n1]

	def degree(self, node):
		return len(self.edges[node])

	def allEdges(self):
		return sum([[(node, neighbor) for neighbor in self.edges[node]] for \
				node in self.nodes], [])

	def numEdges(self):
		return sum(map(len, self.edges.values()))

	def adjacencyMatrix(self):
		adj = [[0]*len(self.nodes) for i in range(len(self.nodes))]
		for node in self.nodes:
			for neighbor in self.edges[node]:
				adj[node][neighbor] = 1
		return adj

	def __repr__(self):
		return self.__class__.__name__ + ': ' + str(len(self.nodes)) + \
				' nodes, ' + str(self.numEdges()) + ' edges'

	def shortestPath(self, origin, destination, edgeCost=lambda src,dst: 1, \
				heuristic=lambda src,dst: 0):
		"""
		Find the shortest path between origin and destination.

		The shortest path is found by A* search, so the distance heuristic
		should be admissable (never overestimating). With the default values for
		edgeCost and heuristic, the search reduces to BFS.

		The path is returned as a list of nodes.
		If no path exists, a PathError is raised.
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
			for neighbor in self.edges[node]:
				if neighbor in visited:
					continue
				newPathCost = pathCosts[node] + edgeCost(node, neighbor)
				if neighbor in pathCosts:
					if pathCosts[neighbor] <= newPathCost:
						continue
				parents[neighbor] = node
				pathCosts[neighbor] = newPathCost
				heappush(queue, (heuristic(neighbor, destination) + \
						newPathCost, neighbor))
		if node != destination:
			raise PathError()
		path = []
		while node != None:
			path = [node] + path
			node = parents[node]
		return path

	def distance(self, n1, n2):
		try:
			return len(self.shortestPath(n1,n2)) - 1
		except PathError:
			return -1


class UndirectedGraph(Graph):
	def addEdge(self, n1, n2):
		self.edges[n1].add(n2)
		self.edges[n2].add(n1)

	def removeEdge(self, n1, n2):
		self.edges[n1].remove(n2)
		self.edges[n2].remove(n1)
	
	def numEdges(self):
		return Graph.numEdges(self)/2


class DirectedGraph(Graph):
	def addEdge(self, src, dst):
		self.edges[src].add(dst)

	def removeEdge(self, src, dst):
		self.edges[src].remove(dst)


class WeightedDirectedGraph(DirectedGraph):
	def __init__(self, nodes=[], weightedEdges=[]):
		self.weights = dict()
		DirectedGraph.__init__(self, nodes, weightedEdges)

	def addEdge(self, src, dst, weight):
		DirectedGraph.addEdge(self, src, dst)
		self.weights[(src, dst)] = weight

	def removeNode(self, node):
		for edge in filter(lambda edge: node in edge, self.weights.keys()):
			del self.weights[edge]
		DirectedGraph.removeNode(self, node)

	def removeEdge(self, src, dst):
		DirectedGraph.removeEdge(self, src, dst)
		del self.weights[(src, dst)]

	def allEdges(self):
		return [(src, dst, self.edgeWeight(src, dst)) for src, dst in \
				DirectedGraph.allEdges(self)]

	def adjacencyMatrix(self):
		adj = [[0]*len(self.nodes) for i in range(len(self.nodes))]
		for node in self.nodes:
			for neighbor in self.edges[node]:
				adj[node][neighbor] = self.weights[(node, neighbor)]
		return adj

