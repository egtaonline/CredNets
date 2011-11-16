from numpy.random import binomial, beta

def CompleteInformation(creditor, debtor, credit_network):
	return credit_network.defaults[debtor], 0.0

def BetaSamples_100_10_1(creditor, debtor, credit_network):
	dist = len(credit_network.graph.shortestPath(creditor, debtor)) - 1
	a = credit_network._params["def_alpha"]
	b = credit_network._params["def_beta"]
	if 0 < dist < 4:
		defaults = binomial(10**(3-dist), credit_network.defaults[debtor])
		a += float(defaults)
		b += float(10**(3-dist) - defaults)
	return float(a) / (a + b), (a*b) / ((a+b)**2 * (a+b+1))

def BetaSamples_64_16_4_1(creditor, debtor, credit_network):
	dist = len(credit_network.graph.shortestPath(creditor, debtor)) - 1
	a = credit_network._params["def_alpha"]
	b = credit_network._params["def_beta"]
	if 0 < dist < 5:
		defaults = binomial(4**(4-dist), credit_network.defaults[debtor])
		a += float(defaults)
		b += float(4**(4-dist) - defaults)
	return float(a) / (a + b), (a*b) / ((a+b)**2 * (a+b+1))

#named for testbed consistency; should be: BetaSamples_10_1
def BetaSamples(*args):
	return BetaSamples_10_1(*args)

def BetaSamples_10_1(creditor, debtor, credit_network):
	dist = len(credit_network.graph.shortestPath(creditor, debtor)) - 1
	a = credit_network._params["def_alpha"]
	b = credit_network._params["def_beta"]
	if 0 < dist < 3:
		defaults = binomial(10**(2-dist), credit_network.defaults[debtor])
		a += float(defaults)
		b += float(10**(2-dist) - defaults)
	return float(a) / (a + b), (a*b) / ((a+b)**2 * (a+b+1))
