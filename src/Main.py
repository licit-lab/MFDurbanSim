import os
import json

from main_objects import Simulation, Reservoir, Route, MacroNode, Demand, Vehicle

import IO_functions
import Solver 
import plot_fct

DEBUG = 0
RUN_ALGO = True
PLOT_NETWORK = False
PLOT_MS = False
PLOT_GRAPH_PER_RES = True
PLOT_GRAPH_PER_RES_PER_ROUTE = False
DYNAMIC_PLOT = 0

(head, tail) = os.path.split(os.getcwd())
root = os.path.normpath(os.path.join(head, "examples"))
folder = 'Braess_2modes/DemSC1/'

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
    res = Reservoir.Reservoir()
    res.load_input(loadNetwork, i)

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
if RUN_ALGO:
    if simulation_settings.Solver == "AccBased":
        Solver.AccBased(simulation_settings, reservoirs, routes, macronodes, GlobalDemand)
    elif simulation_settings.Solver == "TripBased":
        Solver.TripBased(simulation_settings, reservoirs, routes, macronodes, GlobalDemand)

# --- Outputs --- #
file_output = os.path.join(path, "Output.json")
if RUN_ALGO:
    IO_functions.save_output(file_output, simulation_settings, reservoirs, routes)

with open(file_output, "r") as file:
    Output = json.load(file)

res_output = Output["RESERVOIRS"]
routes_output = Output["ROUTES"]

# Reservoir config and states
simu_time = list(range(0, simulation_settings.Duration, simulation_settings.TimeStep))
speed_range = [3, 14]
t0 = 0

options = {'legend': True, 'res_names': True, 'mn_names': True, 'res_color': True, 'routes_color': True,
           'mn_color': True, 'nb_col_max': 2}

if PLOT_NETWORK:
    # Plot network
    fig, ax = plot_fct.plt.subplots()
    plot_fct.plot_network(ax, reservoirs, macronodes, routes, options=options)

if PLOT_MS:
    # Plot reservoir state (mean speed) at each t, real network
    fig2, ax2 = plot_fct.plt.subplots()
    plot_fct.plot_res_net_speed(fig2, ax2, t0, reservoirs, speed_range, simu_time, res_output)

if PLOT_GRAPH_PER_RES:
    # Plot Acc, MeanSpeed, Inflow, Outflow in function of Time per reservoir
    fig3, ax3 = plot_fct.plt.subplots()
    plot_fct.plot_graph_per_res(reservoirs, res_output, 'Acc', options=options)

    fig4, ax4 = plot_fct.plt.subplots()
    plot_fct.plot_graph_per_res(reservoirs, res_output, 'MeanSpeed', options=options)

    fig5, ax5 = plot_fct.plt.subplots()
    plot_fct.plot_graph_per_res(reservoirs, res_output, 'Inflow', 'Outflow', options=options)

    fig6, ax6 = plot_fct.plt.subplots()
    plot_fct.plot_graph_per_res(reservoirs, res_output, 'Demand', options=options)

    plot_fct.plt.show()

if PLOT_GRAPH_PER_RES_PER_ROUTE:
    # Plot Acc in function of Time per reservoir per route
    fig7, ax7 = plot_fct.plt.subplots()
    plot_fct.plot_graph_per_res_per_route(reservoirs, res_output, 'Acc', routes, options=options)

    fig8, ax8 = plot_fct.plt.subplots()
    plot_fct.plot_graph_per_res_per_route(reservoirs, res_output, 'Demand', routes, options=options)

    plot_fct.plt.show()


'''
    # Plot reservoir schematic representation (borders and adjacent connections)
    fig1 = plot_fct.plt.figure
    plot_fct.plot_res_ball_config(reservoirs, 1, 0.5, [1.5, 1.5])
    plot_fct.plt.show()

    # Plot reservoir state (total accumulation) at t, schematic representation
    fig2 = plot_fct.plt.figure
    plot_fct.plot_res_ball_acc(t0, reservoirs, ResOutput, simu_time, 0.5, [1.5, 1.5])
    plot_fct.plt.show()

    # Plot reservoir state (accumulation per route) at t, schematic representation
    fig3 = plot_fct.plt.figure
    plot_fct.plot_res_ball_acc_per_route(t0, reservoirs, ResOutput, routes, simu_time, 0.5, [1.5, 1.5])
    plot_fct.plt.show()

    # Plot reservoir total number or demand of routes
    fig4 = plot_fct.plt.figure
    plot_fct.plot_res_route_dem(reservoirs, routes, macronodes, GlobalDemand, simulation_settings.DemandType, 'demand')
    plot_fct.plt.show()'''


if DYNAMIC_PLOT == 1:
    fig5 = plot_fct.plt.figure
    for t in range(0, simulation_settings.Duration, simulation_settings.TimeStep):
        plot_fct.plt.clf()
        # Plot reservoir state (total accumulation) at t, schematic representation
        plot_fct.plot_res_ball_acc(t, reservoirs, res_output, simu_time, 0.5, [1.5, 1.5])
        plot_fct.plt.draw()
        plot_fct.plt.pause(0.5)
    plot_fct.plt.show()

    fig6 = plot_fct.plt.figure
    for t in range(0, simulation_settings.Duration, simulation_settings.TimeStep):
        plot_fct.plt.clf()
        # Plot reservoir state (accumulation per route) at t, schematic representation
        plot_fct.plot_res_ball_acc_per_route(t, reservoirs, res_output, routes, simu_time, 0.5, [1.5, 1.5])
        plot_fct.plt.draw()
        plot_fct.plt.pause(0.5)
    plot_fct.plt.show()
