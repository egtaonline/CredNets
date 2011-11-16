#!/usr/bin/python2.6
#!/home/software/rhel5/python/2.6.4/bin/python

import CreditNetworks as CN
import GraphFunctions as G
import WebParameterCheck as W
import Strategies as S
import InformationModels as IM

import random
from optparse import OptionParser
try:
	import yaml
except ImportError:
	import sys
	sys.path.append("/home/wellmangroup/lib64/python")
	import yaml


def check_strategies(strategy_names):
	return [eval("S." + s) for s in strategy_names]


def check_parameters(web_params):
	W.check_params(web_params)
	parameters = {}
	parameters["n"] = int(web_params["nodes"])
	parameters["numEvents"] = int(web_params["events"])
	parameters["def_alpha"] = float(web_params["def_alpha"])
	parameters["def_beta"] = float(web_params["def_beta"])
	parameters["rate_func"] = eval("lambda b,s,g:" + \
			str(web_params["buy_rates"]))
	parameters["value_func"] = eval("lambda b,s,g:" + \
			str(web_params["buy_values"]))
	parameters["cost_func"] = eval("lambda b,s,g:" + \
			str(web_params["sell_costs"]))
	parameters["price_func"] = eval("lambda v,c:" + \
			str(web_params["prices"]))
	parameters["graph_func"] = eval("lambda n:G." + \
			str(web_params["graph"]) + "(n)")
	parameters["info_func"] = eval("IM." + str(web_params["information"]))
	return parameters, int(web_params["sims_per_sample"])


def run_simulator(parameters, samples, sims_per_sample):
	payoff_samples = []
	for i in range(samples):
		payoff_sims = dict(((s.__name__,0) for s in parameters["strategies"]))
		for j in range(sims_per_sample):
			crednet = CN.EGTA_CreditNetwork(**parameters)
			crednet.simulate()
			payoffs = crednet.getStrategyPayoffs()
			for strategy, payoff in crednet.getStrategyPayoffs().items():
				payoff_sims[strategy] += payoff
		payoff_samples.append(dict(((s,p/sims_per_sample) for s,p \
				in payoff_sims.items())))
	return payoff_samples


if __name__ == "__main__":
	parser = OptionParser()
	options, args = parser.parse_args()
	yaml_input = open(args[0] + "/simulation_spec.yaml", "r")
	roles, web_params = list(yaml.load_all(yaml_input))
	strategy_names = roles["All"]
	yaml_input.close()

	parameters, sims_per_sample = check_parameters(web_params)
	parameters["strategies"] = check_strategies(strategy_names)
	payoff_samples = run_simulator(parameters, int(args[1]), sims_per_sample)
	payoff_output = [{"All":samples} for samples in payoff_samples]

	payoff_data = open(args[0] + "/payoff_data", 'w')
	payoff_data.write("---\n")
	payoff_data.write(yaml.dump_all(payoff_output, \
			default_flow_style=False))
	payoff_data.close()

