#!/usr/bin/python2.6

from Graphs import *
from GraphFunctions import *

from math import fsum
from itertools import permutations, cycle
from operator import add
from numpy import zeros, array, reshape
import numpy.random as R

class CreditNetwork(FlowNetwork):
	def __init__(self, *args):
		FlowNetwork.__init__(self, *args)
		self.defaulters = set()

	def makePayment(self, sender, receiver, amount):
		"""Transfer an IOU for <amount> from <sender> to connected <receiver>.

		There must be an edge with credit capacity >= amount from the receiver
		to the sender; otherwise the assert fails.

		The credit edge from receiver to sender is debited by amount, while the
		credit edge from sender to receiver is increased by amount.
		"""
		assert amount > 0
		assert self.getEdgeCapacity(Edge(receiver, sender)) >= amount
		self.decreaseEdgeCapacity(Edge(receiver, sender), amount)
		self.increaseEdgeCapacity(Edge(sender, receiver), amount)

	def routePayment(self, sender, receiver, amount):
		"""Transfer IOUs through the credit network from sender to receiver.

		There must be directed paths from reciever to sender with total capacity
		of at least amount. If not, findFlowPaths raises an uncaught
		CapacityError.
		"""
		paths = self.findFlowPaths(receiver, sender, amount)
		while amount:
			path = paths.pop(0)
			capacity = self.getPathCapacity(path)
			for edge in zip(path[1:], path):
				self.makePayment(*edge, amount=min(capacity, amount))
			amount = max(amount - capacity, 0)

	def default(self, defaulter):
		"""Defaulter exhausts all available credit and leaves the network."""
		for sucker in self.getParents(defaulter):
			self.makePayment(defaulter, sucker, \
					self.getEdgeCapacity((sucker, defaulter)))
		self.removeAllEdges(defaulter)
		self.defaulters.add(defaulter)


class EGTA_CreditNetwork(CreditNetwork):
	"""Credit Network with all the trappings for EGTA simulation."""
	def __init__(self, n=60, numEvents=10000, \
			def_alpha=1, def_beta=1, \
			graph_func=lambda n: ErdosRenyiGraph(n), \
			rate_func=lambda b,s,g: R.pareto(2), \
			value_func=lambda b,s,g: R.uniform(1,2), \
			cost_func=lambda b,s,g: 1, \
			price_func=lambda v,c: c, \
			info_func=lambda c,d,cn: (cn.defaults[d],0), \
			strategies=[lambda n,cn: []]):
		self._params = {"n":n, "numEvents":numEvents, "graph_func":graph_func, \
				"rate_func":rate_func, "def_alpha":def_alpha, \
				"def_beta":def_beta, "value_func":value_func, \
				"cost_func":cost_func, "price_func":price_func, \
				"info_func":info_func, "strategies":strategies}
		self.graph = graph_func(n)
		CreditNetwork.__init__(self, self.graph.nodes, [])
		self.numEvents = numEvents
		self.defaults = R.beta(def_alpha, def_beta, [n])
		self.rates = zeros([n,n])
		self.values = zeros([n,n])
		self.costs = zeros([n,n])
		self.payoffs = zeros(n)
		for i,j in permutations(self.nodes, 2):
			self.rates[i,j] = rate_func(i, j, self.graph)
			self.values[i,j] = value_func(i, j, self.graph)
			self.costs[i,j] = cost_func(i, j, self.graph)
		self.rates /= self.rates.sum()
		self.price_func = price_func
		self.info_func = info_func
		self.strategy_list = sorted(strategies)
		self.node_strategies = dict(zip(R.permutation(list(self.nodes)), \
				cycle(self.strategy_list)))
		for node, strategy in self.node_strategies.items():
			for recipient, credit in strategy(node, self):
				self.addEdge(WeightedEdge(node, recipient, credit))

	def simulate(self):
		for d in filter(lambda n: R.binomial(1, self.defaults[n]), self.nodes):
			for n in self.getNeighbors(d):
				self.payoffs[n] -= self.getEdgeCapacity(Edge(n, d))
			self.default(d)
		l = len(self.nodes)
		m = R.multinomial(self.numEvents, reshape(self.rates, l**2))
		events = reduce(add, ([(i/l,i%l)]*m[i] for i in range(l**2)))
		R.shuffle(events)
		for b,s in events:
			try:
				v = self.values[b,s]
				c = self.costs[b,s]
				self.routePayment(b, s, self.price_func(v,c))
				self.payoffs[b] += v
				self.payoffs[s] -= c
			except CapacityError:
				continue

	#warning: gives s:0 if all agents playing strategy s defaulted
	def getStrategyPayoffs(self):
		sp = dict(((s.__name__, array([self.payoffs[a] for a in \
				filter(lambda n: self.node_strategies[n]==s and n not in \
				self.defaulters, self.nodes)])) for s in self.strategy_list))
		return dict(((s, float(a.mean()) if len(a) > 0 else 0) for s,a in sp))



import Strategies as S
import InformationModels as IM
from itertools import combinations

def social_graph_hist(cn):
	paths = dict((((v0,v1),cn.graph.shortestPath(v0,v1)) for v0,v1 in \
			combinations(cn.nodes, 2)))
	path_lengths = [len(p)-1 for p in paths.values()]
	len_hist = [path_lengths.count(i) / float(len(path_lengths)) \
			for i in range(1,11)]
	return len_hist

def credit_distance_hist(cn):
	credit_distances = []
	for agent in cn.nodes:
		credit_distances.extend([len(cn.graph.shortestPath(agent, neighbor)) \
				- 1 for neighbor in cn.getChildren(agent)])
	cred_dist_hist = [credit_distances.count(i) / float(len(cn.nodes) * 5) \
			for i in range(1,11)]
	return cred_dist_hist

if __name__ == "__main__":
	D_hist = zeros(10)
	U_hist = zeros(10)
	TD_hist = zeros(10)
	WTD_hist = zeros(10)
	dist_hist = zeros(10)
	iterations = 1000
	for i in range(iterations):
		cn_D = EGTA_CreditNetwork(n=60, def_beta=2, info_func=\
				IM.BetaSamples_10_1, strategies=[S.DefProb_best5_get5])
		D_hist += array(credit_distance_hist(cn_D))/float(iterations)
		cn_U = EGTA_CreditNetwork(n=60, def_beta=2, info_func= \
				IM.BetaSamples_10_1, strategies=[S.EU_best5_get5])
		U_hist += array(credit_distance_hist(cn_U))/float(iterations)
		cn_TD = EGTA_CreditNetwork(n=60, def_beta=2, info_func=\
				IM.BetaSamples_10_1, strategies=[S.Trade_Def_best5_get5])
		TD_hist += array(credit_distance_hist(cn_TD))/float(iterations)
		cn_WTD = EGTA_CreditNetwork(n=60, def_beta=2, info_func=\
				IM.BetaSamples_10_1, strategies=[S.Wght_Trade_Def_best5_get5])
		WTD_hist += array(credit_distance_hist(cn_WTD))/float(iterations)
		dist_hist += array(social_graph_hist(cn_D))/float(iterations)
	print "DP:", map(lambda x: round(100*x,1), D_hist)
	print "DT:", map(lambda x: round(100*x,1), TD_hist)
	print "TD:", map(lambda x: round(100*x,1), WTD_hist)
	print "EU:", map(lambda x: round(100*x,1), U_hist)
	print "distances:", map(lambda x: round(100*x,1), dist_hist)
