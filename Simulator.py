#! /usr/bin/env python2.7

import CreditNetworks as CN

from argparse import ArgumentParser
import sys
import json


def read_json(json_folder):
	with open(json_folder + "/simulation_spec.json") as f:
		simulator_input = json.load(f)
	config = simulator_input["configuration"]
	parameters = {}
	parameters["role"] = simulator_input["assignment"].keys()[0]
	parameters["strategies"] = simulator_input["assignment"].values()[0]
	parameters["json_folder"] = json_folder
	parameters["events"] = int(config["events"])
	parameters["def_alpha"] = float(config["def_alpha"])
	parameters["def_beta"] = float(config["def_beta"])
	parameters["rate_alpha"] = float(config["rate_alpha"])
	parameters["min_value"] = float(config["min_value"])
	parameters["max_value"] = float(config["max_value"])
	parameters["min_cost"] = float(config["min_cost"])
	parameters["max_cost"] = float(config["max_cost"])
	parameters["price"] = getattr(sys.modules[__name__], config["price"])
	parameters["def_samples"] = str(config["def_samples"])
	parameters["social_network"] = str(config["social_network"])
	parameters["bank_policy"] = str(config["bank_policy"])
	parameters["num_banks"] = int(config["num_banks"])
	parameters["sims_per_sample"] = int(config["sims_per_sample"])
	parameters["prevent_zeros"] = True if config["prevent_zeros"] == "True" \
									else False
	return parameters


def parse_args():
	parser = ArgumentParser()
	parser.add_argument("json_folder", type=str)
	parser.add_argument("samples", type=int)
	args = parser.parse_args()
	parameters = read_json(args.json_folder)
	parameters["samples"] = args.samples
	return parameters


def run_simulator(parameters):
	n = len(parameters["strategies"])
	payoffs = dict(zip(range(n), [0]*n))
	for sim in range(parameters["sims_per_sample"]):
		matrices = CN.InitMatrices(parameters)
		crednet = CN.InitCrednet(matrices, parameters)
		sim_payoffs = CN.SimulateCreditNetwork(crednet, parameters, **matrices)
		for agent, value in sim_payoffs.items():
			payoffs[agent] += value
	for agent in range(n):
		payoffs[agent] /= parameters["sims_per_sample"]
	return payoffs


def write_payoffs(payoffs, parameters, obs_name):
	payoff_json = {"players":[]}
	for player in payoffs.keys():
		payoff_json["players"].append({"role":parameters["role"], \
				"strategy":parameters["strategies"][player], "payoff": \
				payoffs[player], "features":{"defaulted":0}})
	for p in set(range(len(parameters["strategies"]))) - set(payoffs.keys()):
		payoff_json["players"].append({"role":parameters["role"], \
				"strategy":parameters["strategies"][p], "payoff": \
				0, "features":{"defaulted":1}})
	payoff_json["features"] = {"defaults" : len(parameters["strategies"]) - \
			len(payoffs)}
	with open(parameters["json_folder"] + "/observation_" + obs_name + \
			".json", "w") as payoff_file:
		json.dump(payoff_json, payoff_file, indent=2)


#price functions
cost = lambda v,c: c
avg = lambda v,c: (v+c)/2.


def main():
	parameters = parse_args()
	for i in range(parameters["samples"]):
		payoffs = run_simulator(parameters)
		write_payoffs(payoffs, parameters, str(i))


if __name__ == "__main__":
	main()

