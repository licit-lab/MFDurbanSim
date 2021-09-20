import json
import sys
import os
import argparse

import matplotlib.pyplot as plt

from mfdus.main_objects import Simulation, Reservoir, MacroNode
from mfdus.main_objects import Route

from mfdus.plot_fct import plot_network, plot_res_net_speed, plot_graph_per_res, plot_graph_per_res_per_route
from mfdus.IO_functions import verify_nodes_input, init_variables, verify_routes_input, verify_reservoir_input

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('res_dir', help='Directory where the results are', type=str)
    parser.add_argument('--PLOT_NETWORK', action='store_true', help='Plot network')
    parser.add_argument('--PLOT_MS', action='store_true', help='Plot reservoir mean speed')
    parser.add_argument('--PLOT_GRAPH_PER_RES', action='store_true', help='Plot Acc, MeanSpeed, Inflow, Outflow in function of Time per reservoir')
    parser.add_argument('--PLOT_GRAPH_PER_RES_PER_ROUTE', action='store_true', help='Plot Acc in function of Time per reservoir per route')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    DEBUG = 1 if args.verbose else 0
    PLOT_NETWORK = args.PLOT_NETWORK
    PLOT_MS = args.PLOT_MS
    PLOT_GRAPH_PER_RES = args.PLOT_GRAPH_PER_RES
    PLOT_GRAPH_PER_RES_PER_ROUTE = args.PLOT_GRAPH_PER_RES_PER_ROUTE

    path = args.res_dir

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

        if verify_reservoir_input(res, list_res_id):
            reservoirs.append(res)

        if DEBUG == 1:
            print(res.ID)

    list_mn_id = []
    for i in range(num_mn):
        macronode = MacroNode.MacroNode()
        macronode.load_input(load_network, i, reservoirs)

        if verify_nodes_input(macronode, list_mn_id, list_res_id):
            macronodes.append(macronode)

        if DEBUG == 1:
            print(macronode.ResID)

    list_routes_id = []
    for i in range(num_routes):
        route = Route.Route()
        route.load_input(load_network, i, reservoirs, macronodes)

        if verify_routes_input(route, list_routes_id):
            routes.append(route)

        if DEBUG == 1:
            print(route.Length, route.ResOriginID, route.ResDestinationID, route.OriginMacroNode, route.DestMacroNode)

    init_variables(reservoirs, routes, macronodes)

    res_output = load_output["RESERVOIRS"]
    routes_output = load_output["ROUTES"]

    # Reservoir config and states
    simu_time = list(range(0, simulation_settings.Duration, simulation_settings.TimeStep))
    simu_modes = simulation_settings.Modes
    speed_range = [3, 14]
    t0 = 0

    options = {'legend': True, 'res_names': True, 'mn_names': True, 'res_color': True, 'routes_color': True,
               'mn_color': True, 'nb_col_max': 2}

    if PLOT_NETWORK:
        # Plot network
        fig, ax = plt.subplots()
        plot_network(ax, reservoirs, macronodes, routes, options=options)

    if PLOT_MS:
        # Plot reservoir state (mean speed) at each t, real network
        fig2, ax2 = plt.subplots()
        plot_res_net_speed(fig2, ax2, t0, reservoirs, speed_range, simu_time, res_output, simu_modes, mode='VL')

    if PLOT_GRAPH_PER_RES:
        # Plot Acc, MeanSpeed, Inflow, Outflow in function of Time per reservoir
        fig3, ax3 = plt.subplots()
        plot_graph_per_res(reservoirs, res_output, simu_modes, 'Acc', mode='VL', options=options)

        fig4, ax4 = plt.subplots()
        plot_graph_per_res(reservoirs, res_output, simu_modes, 'MeanSpeed', mode='VL', options=options)

        fig5, ax5 = plt.subplots()
        plot_graph_per_res(reservoirs, res_output, simu_modes, 'Inflow', y_label2='Outflow', mode='VL', options=options)

        fig6, ax6 = plt.subplots()
        plot_graph_per_res(reservoirs, res_output, simu_modes, 'Demand', mode='VL', options=options)

        plt.show()

    if PLOT_GRAPH_PER_RES_PER_ROUTE:
        # Plot Acc in function of Time per reservoir per route
        fig7, ax7 = plt.subplots()
        plot_graph_per_res_per_route(reservoirs, res_output, 'Acc', routes, simu_modes, mode='VL', options=options)

        fig8, ax8 = plt.subplots()
        plot_graph_per_res_per_route(reservoirs, res_output, 'Demand', routes, simu_modes, mode='VL', options=options)

        plt.show()

if __name__ == "__main__":
    main()