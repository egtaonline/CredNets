#! /usr/bin/env python2.7
#!/home/wellmangroup/opt/local/Python-2.7.2/python

import CreditNetworks as CN

from argparse import ArgumentParser
import sys
try:
	import yaml
except ImportError:
	sys.path.append("/home/wellmangroup/lib64/python")
	import yaml


def read_yaml(yaml_folder):
	f = open(yaml_folder + "/simulation_spec.yaml")
	strategies, parameters = list(yaml.load_all(f))
	f.close()
	assert len(strategies) == 1, "credit network games must be symmetric"
	parameters["strategies"] = strategies.values()[0]
	parameters["role"] = strategies.keys()[0]
	parameters["yaml_folder"] = yaml_folder
	parameters["sims_per_sample"] = int(parameters["sims_per_sample"])
	parameters["def_samples"] = str(parameters["def_samples"])
	return parameters


def parse_args():
	parser = ArgumentParser()
	parser.add_argument("yaml_folder", type=str)
	parser.add_argument("samples", type=int)
	args = parser.parse_args()
	parameters = read_yaml(args.yaml_folder)
	parameters["samples"] = args.samples
	return parameters


def run_simulator(parameters):
	payoff_samples = []
	for i in range(parameters["samples"]):
		sample = {s:0 for s in parameters["strategies"]}
		for j in range(parameters["sims_per_sample"]):
			matrices = CN.InitMatrices(parameters)
			crednet = CN.InitCrednet(matrices, parameters)
			payoff_sim = CN.SimulateCreditNetwork(crednet, getattr( \
					sys.modules[__name__], parameters["price"]), \
					int(parameters["events"]), **matrices)
			counts = {s:0 for s in parameters["strategies"]}
			sim = {s:0 for s in parameters["strategies"]}
			for n,s in enumerate(parameters["strategies"]):
				if n in payoff_sim: # agent defaulted
					sim[s] += float(payoff_sim[n])
					counts[s] += 1
			for s in sample:
				if counts[s] > 0:
					sample[s] += sim[s] / counts[s]
		payoff_samples.append(sample)
	return payoff_samples


def write_payoffs(payoff_samples, parameters):
	payoff_file = open(parameters["yaml_folder"] + "/payoff_data", "w")
	payoff_file.write("---\n")
	payoff_file.write(yaml.dump_all([{parameters["role"]:payoff} for payoff \
			in payoff_samples], default_flow_style=False))
	payoff_file.close()


#price functions
cost = lambda v,c: c
avg = lambda v,c: (v+c)/2.


if __name__ == "__main__":
	parameters = parse_args()
	payoff_samples = run_simulator(parameters)
	write_payoffs(payoff_samples, parameters)


