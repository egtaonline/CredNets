from itertools import repeat


# criteria
def default_probability(agent, other, cn, *args):
	return cn.info_func(agent, other, cn)[0]

def buy_value(agent, other, cn, *args):
	return cn.values[agent,other]

def buy_rate(agent, other, cn, *args):
	return cn.rates[agent,other]

def trade_value(agent, other, cn, *args):
	return cn.rates[agent,other] * cn.values[agent,other]

def sell_cost(agent, other, cn, *args):
	return cn.costs[other,agent]

def trade_cost(agent, other, cn, *args):
	return cn.rates[other,agent] * cn.costs[other,agent]

def trade_profit(*args):
	return trade_value(*args) - trade_cost(*args)

def expected_utility(agent, other, cn, numLinks, linkSize):
	dp = default_probability(agent, other, cn)
	return (1-dp)*cn.numEvents*trade_profit(agent, other, cn) + linkSize*dp

def default_variance(agent, other, cn, *args):
	return cn.info_func(agent, other, cn)[1]

def one_sd(agent, other, cn, numLinks, linkSize):
	dp = default_probability(agent, other, cn) + \
			default_variance(agent, other, cn)**0.5
	return (1-dp)*cn.numEvents*trade_profit(agent, other, cn) + linkSize*dp

def graph_distance(agent, other, cn, *args):
	return len(cn.graph.shortestPath(agent, other)) - 1

def index(agent, other, *args):
	return other

def trade_default(agent, other, cn, numLinks, linkSize):
	return trade_value(agent, other, cn) - default_probability(agent, \
			other, cn)*linkSize

def weighted_trade_default(agent, other, cn, numLinks, linkSize):
	dp = default_probability(agent, other, cn)
	return (1-dp)*cn.numEvents*trade_value(agent, other, cn) - dp*linkSize

# generic strategies
def highest_k_get_c(agent, cn, k, c, criterion):
	return zip(sorted(cn.nodes - set([agent]), key=lambda other: \
			criterion(agent, other, cn, k, c))[-k:], repeat(c))

def lowest_k_get_c(agent, cn, k, c, criterion):
	return zip(sorted(cn.nodes - set([agent]), key=lambda other: \
			criterion(agent, other, cn, k, c))[:k], repeat(c))

def above_k_get_c(agent, cn, k, c, criterion):
	return zip(filter(lambda other: criterion(agent, other, cn, k, c) > k, \
			cn.nodes - set([agent])), repeat(c))

def all_get_c(agent, cn, k):
	return [(v,k) for v in cn.nodes - set([n])]

# oblivious strategies
def all_0(agent, cn):
	return []

def all_1(agent, cn):
	return all_get_c(agent, cn, 1)

# strategies based on link counts
def DefProb_best5_get5(agent, cn):
	return lowest_k_get_c(agent, cn, 5, 5, default_probability)

def Index_best5_get5(agent, cn):
	return lowest_k_get_c(agent, cn, 5, 5, index)

def BuyValue_best5_get5(agent, cn):
	return highest_k_get_c(agent, cn, 5, 5, buy_value)

def TradeValue_best5_get5(agent, cn):
	return highest_k_get_c(agent, cn, 5, 5, trade_value)

def TradeProfit_best5_get5(agent, cn):
	return highest_k_get_c(agent, cn, 5, 5, trade_profit)

def EU_best5_get5(agent, cn):
	return highest_k_get_c(agent, cn, 5, 5, expected_utility)

def OneSD_best5_get5(agent, cn):
	return highest_k_get_c(agent, cn, 5, 5, one_sd)

def Trade_Def_best5_get5(agent, cn):
	return highest_k_get_c(agent, cn, 5, 5, trade_default)

def Wght_Trade_Def_best5_get5(agent, cn):
	return highest_k_get_c(agent, cn, 5, 5, weighted_trade_default)

# strategies based on thresholds
#def default_above_5_get_5(agent, cn):
#	return above_k_get_c(agent, cn, 5, 5, default)
#
#def value_above_5_get_5(agent, cn):
#	return above_k_get_c(agent, cn, 5, 5, value)
#
#def cost_above_5_get_5(agent, cn):
#	return above_k_get_c(agent, cn, 5, 5, cost)
#
#def profit_above_5_get_5(agent, cn):
#	return above_k_get_c(agent, cn, 5, 5, profit)
#
#def EV_above_5_get_5(n, cn):
#	return above_k_get_c(agent, cn, 5, 5, EV)
