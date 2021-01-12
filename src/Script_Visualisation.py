import json
import sys
import os

from main_objects import Simulation, Reservoir, Route, MacroNode

import IO_functions
import plot_fct

DEBUG = 0
PLOT_NETWORK = True
PLOT_MS = True
PLOT_GRAPH_PER_RES = True
PLOT_GRAPH_PER_RES_PER_ROUTE = True

(head, tail) = os.path.split(os.getcwd())
root = os.path.normpath(os.path.join(head, "examples"))
folder = f'{sys.argv[1]}/{sys.argv[2]}/'

path = os.path.normpath(os.path.join(root, folder))

path_config = os.path.join(path, "Configuration.json")

with open(path_config, "r") as file:
    load_simulation = json.load(file)

simulation_settings = Simulation.Simulation()
simulation_settings.load_input(load_simulation, path)

path_network = os.path.join(path, simulation_settings.Network)
path_output = os.path.join(path, "Output.json")

with open(path_network, "r") as file:
    load_network = json.load(file)

with open(path_output, "r") as file:
    load_output = json.load(file)

reservoirs = []
macronodes = []
routes = []

num_res = len(load_network["RESERVOIRS"])
num_mn = len(load_network["MACRONODES"])
num_routes = len(load_network["ROUTES"])

list_res_id = []
for i in range(num_res):
    res = Reservoir.Reservoir(simulation_settings.Modes)
    res.load_input(load_network, i, simulation_settings.MFDType)

    if IO_functions.verify_reservoir_input(res, list_res_id):
        reservoirs.append(res)

    if DEBUG == 1:
        print(res.ID)

list_mn_id = []
for i in range(num_mn):
    macronode = MacroNode.MacroNode()
    macronode.load_input(load_network, i, reservoirs)

    if IO_functions.verify_nodes_input(macronode, list_mn_id, list_res_id):
        macronodes.append(macronode)

    if DEBUG == 1:
        print(macronode.ResID)

list_routes_id = []
for i in range(num_routes):
    route = Route.Route()
    route.load_input(load_network, i, reservoirs, macronodes)

    if IO_functions.verify_routes_input(route, list_routes_id):
        routes.append(route)

    if DEBUG == 1:
        print(route.Length, route.ResOriginID, route.ResDestinationID, route.OriginMacroNode, route.DestMacroNode)

IO_functions.init_variables(reservoirs, routes, macronodes)

res_output = load_output["RESERVOIRS"]
routes_output = load_output["ROUTES"]

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
    plot_fct.plot_graph_per_res(reservoirs, res_output, 'Inflow', y_label2='Outflow', options=options)

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
