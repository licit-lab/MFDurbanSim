import os
import json
import sys
import importlib

from main_objects import Simulation, Reservoir, Route, MacroNode, Demand, Vehicle

import IO_functions
import Solver 
import plot_fct

DEBUG = 0

(head, tail) = os.path.split(os.getcwd())

root = os.path.normpath(os.path.join(head, "examples"))

folder = f'{sys.argv[1]}/{sys.argv[2]}/'

path = os.path.normpath(os.path.join(root, folder))

reservoirs = []                 # list of reservoirs
routes = []                     # list of routes
macronodes = []                 # list of macro-nodes

# --- Load Input Parameters --- #

# Configuration
path_config = os.path.join(path, "Configuration.json")
with open(path_config, "r") as file:
    loadSimulation = json.load(file)

simulation_settings = Simulation.Simulation()
simulation_settings.load_input(loadSimulation, path)

# Network loading
path_network = os.path.join(path, simulation_settings.Network)
with open(path_network, "r") as file:
    loadNetwork = json.load(file)

numRes = len(loadNetwork["RESERVOIRS"])
list_res_id = []
for i in range(numRes):
    res = Reservoir.Reservoir(simulation_settings.Modes)
    res.load_input(loadNetwork, i, simulation_settings.MFDType)

    if IO_functions.verify_reservoir_input(res, list_res_id):
        reservoirs.append(res)

    if DEBUG == 1:
        print(res.ID)

num_mn = len(loadNetwork["MACRONODES"])
list_mn_id = []
for i in range(num_mn):
    macronode = MacroNode.MacroNode()
    macronode.load_input(loadNetwork, i, reservoirs)

    if IO_functions.verify_nodes_input(macronode, list_mn_id, list_res_id):
        macronodes.append(macronode)

    if DEBUG == 1:
        print(macronode.ResID)

num_routes = len(loadNetwork["ROUTES"])
list_routes_id = []
for i in range(num_routes):
    route = Route.Route()
    route.load_input(loadNetwork, i, reservoirs, macronodes)

    if IO_functions.verify_routes_input(route, list_routes_id):
        routes.append(route)

    if DEBUG == 1:
        print(route.Length, route.ResOriginID, route.ResDestinationID, route.OriginMacroNode, route.DestMacroNode)

# Demand
path_demand = os.path.join(path, simulation_settings.Demand)
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

        if IO_functions.verify_flow_demand_input(flow, list_routes_id):
            GlobalDemand.append(flow)
    
elif simulation_settings.DemandType == "micro":
    num_demand = len(loadDemand["MICRO"])
    list_trip_id = []

    if DEBUG == 1:
        print(num_demand)

    for i in range(num_demand):
        trip = Demand.DiscreteDemand()
        trip.load_input(loadDemand, i, routes, macronodes)

        if IO_functions.verify_discrete_demand_input(trip, list_trip_id):
            GlobalDemand.append(trip)
    
    # Sorts trips by creation time
    GlobalDemand = sorted(GlobalDemand, key=lambda trip: trip.Time)
else:
    print("Demand Type error")

# --- Initialize variables --- #
IO_functions.init_variables(reservoirs, routes, macronodes)

# --- Algorithms --- #
if simulation_settings.Solver == "AccBased":
    Solver.AccBased(simulation_settings, reservoirs, routes, macronodes, GlobalDemand)
elif simulation_settings.Solver == "TripBased":
    Solver.TripBased(simulation_settings, reservoirs, routes, macronodes, GlobalDemand)

# --- Outputs --- #
file_output = os.path.join(path, "Output.json")
IO_functions.save_output(file_output, simulation_settings, reservoirs, routes)


