from itertools import cycle
from functools import partial
from operator import ge, le

from numpy.random import binomial

class AgentStrategies:
	"""
	The folowing parameters are required:
	def_damples..'-' seperated string specifying DefProb posterior estimation
	def_alpha....alpha parameter for default probability beta-distribution
	def_beta.....beta parameter for default probability beta-distribution
	"""
	def __init__(self, matrices, social_network, params):
		self.matrices = matrices
		self.social_network = social_network
		self.params = params
		self.nodes = sorted(social_network.nodes)
		self.def_samples = map(float, params["def_samples"].split("-"))

	def others(self, agent):
		return self.social_network.nodes - {agent}

	#criteria
	def Index(self, agent, other):
		return self.nodes.index(other)

	def TrueDefProb(self, agent, other):
		return self.matrices["DP"][other]

	def DefProb(self, agent, other):
		d = self.social_network.distance(agent, other)
		if d >= len(self.def_samples):
			d = -1
		num_samples = self.def_samples[d]
		if num_samples > 0:
			pos_samples = binomial(num_samples, self.matrices["DP"][other])
		else:
			pos_samples = num_samples = 0
		return float(self.params["def_alpha"] + pos_samples) / float( \
				self.params["def_alpha"] + self.params["def_beta"] + \
				num_samples)

	def BuyRate(self, agent, other):
		return self.matrices["TR"][agent, other]

	def BuyValue(self, agent, other):
		return self.matrices["BV"][agent, other]

	def TradeValue(self, agent, other):
		return self.BuyValue(agent, other) * self.BuyRate(agent, other)

	def SellRate(self, agent, other):
		return self.matrices["TR"][other, agent]

	def SellCost(self, agent, other):
		return self.matrices["SC"][other, agent]

	def TradeCost(self, agent, other):
		return self.SellCost(agent, other) * self.SellRate(agent, other)

	def TradeProfit(self, agent, other):
		return self.TradeValue(agent, other) - self.TradeCost(agent, other)

	#generic strategies
	def all_k(self, agent, k):
		return [(agent, other, k) for other in self.others(agent)]

	def best_n_get_k(self, agent, n, k, criterion, reverse):
		return zip(cycle([agent]), sorted(self.others(agent), \
				key=lambda other: criterion(agent, other), \
				reverse=reverse)[:n], cycle([k]))

	def thresh_t_get_k(self, agent, t, k, criterion, comparator):
		return zip(cycle([agent]), filter(lambda other: comparator(\
				criterion(agent, other), t), self.others(agent)), cycle([k]))

	#explicit strategies
	def all0(self, agent):
		return []

	#strategy generator
	def get_strategy(self, strategy):

		#if strategy already exists, return it
		if hasattr(self, strategy):
			return getattr(self, strategy)

		s = strategy.split("_")
		if hasattr(self, s[0]):
			criterion = getattr(self, s[0])
			k = float(s[-1][3:])

		#generate allk strategies
		if strategy.startswith("all"):
			k = float(s[-1][3:])
			strat = partial(self.all_k, k=k)

		#generate criterion_lowestn_getk strategies
		elif "lowest" in strategy and "get" in strategy:
			n = int(s[1][6:])
			strat = partial(self.best_n_get_k, n=n, k=k, \
					criterion=criterion, reverse=False)

		#generate criterion_highestn_getk strategies
		elif "highest" in strategy and "get" in strategy:
			n = int(s[1][7:])
			strat = partial(self.best_n_get_k, n=n, k=k, \
					criterion=criterion, reverse=True)

		#generate criterion_belowt_getk strategies
		elif "below" in strategy and "get" in strategy:
			t = float(s[1][5:])
			strat = partial(self.thresh_t_get_k, t=t, k=k, \
					criterion=criterion, comparator=le)

		#generate criterion_abovet_getk strategies
		elif "above" in strategy and "get" in strategy:
			t = float(s[1][5:])
			strat = partial(self.thresh_t_get_k, t=t, k=k, \
					criterion=criterion, comparator=ge)

		try:
			setattr(self, strategy, strat) #save strategy for next time
			return strat
		except NameError:
			raise AttributeError("no strategy named " + strategy)


class BankPolicies:
	"""
	The folowing parameters are required:
	num_banks..number of banks to simulate (usually 0 or 1)
	"""
	def __init__(self, matrices, social_network, params):
		self.matrices = matrices
		self.social_network = social_network
		self.params = params
		self.nodes = sorted(social_network.nodes)
		self.banks = range(-params["num_banks"], 0)

	#generic policies
	def agentsk_banksc(self, bank, k, c):
		return sum([[(b,n,k) for n in self.nodes] + [(n,b,c) for n in \
				self.nodes] for b in self.banks], [])

	#policy generator
	def get_policy(self, policy):

		#if policy already exists, return it
		if hasattr(self, policy):
			return getattr(self, policy)

		s = policy.split("_")

		#generate agentsk_banksc policies 
		if "agents" in policy and "banks" in policy:
			k = float(s[0][6:])
			c = float(s[1][5:])
			pol = partial(self.agentsk_banksc, k=k, c=c)

		try:
			setattr(self, policy, pol) #save policy for next time
			return pol
		except NameError:
			raise AttributeError("no policy named " + policy)

