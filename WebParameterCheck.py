import InformationModels as IM
import GraphFunctions as GF

from itertools import product

allowed = dict([ \
("sims_per_sample", frozenset(range(1,10) + range(10,101,5))), \
("nodes", frozenset(range(10,100))), \
("events", frozenset([10000.0])), \
("def_alpha", frozenset(range(1,10))), \
("def_beta", frozenset(range(1,100))), \
("buy_rates", frozenset(["random.paretovariate(2)"])), \
("buy_values", frozenset(["random.uniform(" + str(l) +","+ str(h) +")" for l,h \
	in product([0,1], range(1,6)+[1.2])])), \
("sell_costs", frozenset(range(2))), \
("prices", frozenset(["c", "(v+c)/2.0"])), \
])

def check_params(web_params):
	info = web_params.pop("information")
	assert hasattr(IM, info)
	graph = web_params.pop("graph")
	assert hasattr(GF, graph)
	for p in web_params:
		assert web_params[p] in allowed[p], "invalid value '" + \
				str(web_params[p]) + "' for web parameter '" + p + "'"
	web_params["information"] = info
	web_params["graph"] = graph

