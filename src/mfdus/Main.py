import os
import json
import sys
from pathlib import Path

import argparse

from mfdus.main_objects import Simulation, Reservoir, MacroNode, Demand
from mfdus.main_objects import Route

from mfdus.IO_functions import (verify_reservoir_input, verify_nodes_input, verify_routes_input, verify_flow_demand_input,
                                verify_discrete_demand_input, init_variables, save_output)
from mfdus.Solver import AccBased, TripBased

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('configuration_dir', help='Directory where the Configuration.json is', type=str)
    parser.add_argument('--output_dir', help='Directory to store results', type=str, default=None)
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    if args.output_dir is None:
        args.output_dir = args.configuration_dir
    return args


def main():
    args = parse_args()

    path = args.configuration_dir

    if args.verbose:
        DEBUG = 1
    else:
        DEBUG = 0

    reservoirs = []                 # list of reservoirs
    routes = []                     # list of routes
    macronodes = []                 # list of macro-nodes

    # --- Load Input Parameters --- #

    # Configuration
    path_config = os.path.join(args.configuration_dir, "Configuration.json")
    with open(path_config, "r") as file:
        loadSimulation = json.load(file)

    simulation_settings = Simulation.Simulation()
    simulation_settings.load_input(loadSimulation, args.configuration_dir)

    # Network loading
    path_network = os.path.join(args.configuration_dir, simulation_settings.Network)
    with open(path_network, "r") as file:
        loadNetwork = json.load(file)

    numRes = len(loadNetwork["RESERVOIRS"])
    list_res_id = []
    for i in range(numRes):
        res = Reservoir.Reservoir(simulation_settings.Modes)
        res.load_input(loadNetwork, i, simulation_settings.MFDType)

        if verify_reservoir_input(res, list_res_id):
            reservoirs.append(res)

        if DEBUG == 1:
            print(res.ID)

    num_mn = len(loadNetwork["MACRONODES"])
    list_mn_id = []
    for i in range(num_mn):
        macronode = MacroNode.MacroNode()
        macronode.load_input(loadNetwork, i, reservoirs)

        if verify_nodes_input(macronode, list_mn_id, list_res_id):
            macronodes.append(macronode)

        if DEBUG == 1:
            print(macronode.ResID)

    num_routes = len(loadNetwork["ROUTES"])
    list_routes_id = []
    for i in range(num_routes):
        route = Route.Route()
        route.load_input(loadNetwork, i, reservoirs, macronodes)

        if verify_routes_input(route, list_routes_id):
            routes.append(route)

        if DEBUG == 1:
            print(route.Length, route.ResOriginID, route.ResDestinationID, route.OriginMacroNode, route.DestMacroNode)

    # Demand
    path_demand = os.path.join(args.configuration_dir, simulation_settings.Demand)
    with open(path_demand, "r") as file:
        loadDemand = json.load(file)

    GlobalDemand = []
    if simulation_settings.DemandType == "FlowDemand":
        num_demand = len(loadDemand["FLOW DEMAND"])

        if DEBUG == 1:
            print(num_demand)

        for i in range(num_demand):
            flow = Demand.FlowDemand()
            flow.load_input(loadDemand, i, macronodes)

            if verify_flow_demand_input(flow, list_routes_id):
                GlobalDemand.append(flow)

    elif simulation_settings.DemandType == "micro":
        num_demand = len(loadDemand["MICRO"])
        list_trip_id = []

        if DEBUG == 1:
            print(num_demand)

        for i in range(num_demand):
            trip = Demand.DiscreteDemand()
            trip.load_input(loadDemand, i, routes, macronodes)

            if verify_discrete_demand_input(trip, list_trip_id):
                GlobalDemand.append(trip)

        # Sorts trips by creation time
        GlobalDemand = sorted(GlobalDemand, key=lambda trip: trip.Time)
    else:
        print("Demand Type error")

    # --- Initialize variables --- #
    init_variables(reservoirs, routes, macronodes)

    # --- Algorithms --- #
    if simulation_settings.Solver == "AccBased":
        AccBased(simulation_settings, reservoirs, routes, macronodes, GlobalDemand)
    elif simulation_settings.Solver == "TripBased":
        TripBased(simulation_settings, reservoirs, routes, macronodes, GlobalDemand)

    # --- Outputs --- #
    file_output = os.path.join(args.output_dir, "Output.json")
    save_output(file_output, simulation_settings, reservoirs, routes)


if __name__ == "__main__":
    main()