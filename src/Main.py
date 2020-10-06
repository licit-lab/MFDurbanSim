import json

from main_objects import Simulation, Reservoir, Route, MacroNode, Demand, Vehicle
from IO_functions import *
from Solver import *
from plot_fct import *

DEBUG = 0
PLOT = 1

root='../examples/'
folder='Braess/DemSC1/'

reservoirs = []                 # list of reservoirs
routes = []                     # list of routes
macronodes=[]                   # list of macro-nodes

#### Load Input Parameters ####

# Configuration
with open(root + folder +"Configuration.json", "r") as file:
    load_simulation = json.load(file)
file.close()

simulation_settings = Simulation.Simulation()
simulation_settings.load_input(load_simulation)

# Network loading
with open(root + folder + simulation_settings.Network, "r") as file:
    load_network = json.load(file)
file.close()

num_res = len(load_network["RESERVOIRS"])

for i in range(num_res):
    res = Reservoir.Reservoir()
    res.load_input(load_network, i)
    reservoirs.append(res)
    if DEBUG == 1:
        print(res.ID)
        
num_macronodes = len(load_network["MACRONODES"])

for i in range(num_macronodes):
    macronode = MacroNode.MacroNode()
    macronode.load_input(load_network, i)
    macronodes.append(macronode)
    if DEBUG == 1:
        print(macronode.ResID)

num_routes = len(load_network["ROUTES"])

for i in range(num_routes):
    route = Route.Route()
    route.load_input(load_network, i, reservoirs, macronodes)
    routes.append(route)
    if DEBUG == 1:
        print(route.Length, route.ResOriginID, route.ResDestinationID, route.NodeOriginID, route.NodeDestinationID)


    
#Demand
with open(root + folder + simulation_settings.Demand, "r") as file:
    load_demand = json.load(file)
file.close()

global_demand = {}
if simulation_settings.DemandType == "FlowDemand":
    num_demand = len(load_demand["FLOW DEMAND"])
    if DEBUG == 1:
        print(num_demand)
    for i in range(num_demand):
        global_demand[i] = Demand.FlowDemand()
        global_demand[i].load_input(load_demand, i)
    
elif simulation_settings.DemandType == "DiscreteDemand":
    num_demand = len(load_demand["DISCRETE DEMAND"])
    if DEBUG == 1:
        print(num_demand)
    for i in range(num_demand):
        global_demand[i] = Demand.DiscreteDemand()
        global_demand[i].load_input(load_demand, i)
    if DEBUG == 1:
        print(global_demand[0].TripID)
else:
    print("Demand Type error")

#### Initialize variables ####
if simulation_settings.Solver == "TripBased":
    vehicles = {}
    
for r in reservoirs:
    r.init_fct_param(0.8, 1, 1, len(simulation_settings.Modes))
    if DEBUG == 1:
        print(r.EntryfctParam)
    
Init(reservoirs, routes, macronodes, global_demand)

#### Algorithms ####

if simulation_settings.Solver == "AccBased":
    AccBased(simulation_settings, reservoirs, routes, macronodes, global_demand)
elif simulation_settings.Solver == "TripBased":
    TripBased(simulation_settings, reservoirs, routes, macronodes, vehicles)

#### Outputs ####

## Reservoir config and states
simul_time = list(range(0, simulation_settings.Duration, simulation_settings.TimeStep))
speed_range = [3, 14]
t0 = 10

with open(root + folder + "Output.json", "r") as file:
    Output = json.load(file)
file.close()

res_output = Output["RESERVOIRS"]
routes_output = Output["ROUTES"]

if PLOT == 1:
    # Plot reservoir schematic representation (borders and adjacent connections)
    plt.figure
    plotResBallConfig(reservoirs, 1, 0.5, [1.5, 1.5])
    plt.show()

    # Plot reservoir state (total accumulation) at t, schematic representation
    plt.figure
    plotResBallAcc(t0, reservoirs, res_output, simul_time, 0.5, [1.5, 1.5])
    plt.show()

    # Plot reservoir state (accumulation per route) at t, schematic representation
    plt.figure
    plotResBallAccPerRoute(t0, reservoirs, res_output, routes, simul_time, 0.5, [1.5, 1.5])
    plt.show()

    # Plot reservoir state (mean speed) at t, real network
    plt.figure
    plotResNetSpeed(t0, reservoirs, res_output, simul_time, speed_range)
    plt.show()

    # Plot reservoir total number or demand of routes
    plt.figure
    plotResRouteDem(reservoirs, routes, macronodes, demands, simulation_settings.DemandType, 'demand')
    plt.show()

# Plot macro nodes with route paths
#plt.figure
#plotMacroNodes(Res, 1, MacroNodes, 0, Routes, 0)
#plt.show()

if DYNAMIC_PLOT == 1:
    plt.figure
    for t in range(0, 50, simulation_settings.TimeStep):
        plt.clf()
        # Plot reservoir state (total accumulation) at t, schematic representation
        plotResBallAcc(t, reservoirs, res_output, simul_time, 0.5, [1.5, 1.5])
        plt.draw()
        plt.pause(0.5)
    plt.show()

    plt.figure
    for t in range(0, 50, simulation_settings.TimeStep):
        plt.clf()
        # Plot reservoir state (accumulation per route) at t, schematic representation
        plotResBallAccPerRoute(t, reservoirs, res_output, routes, simul_time, 0.5, [1.5, 1.5])
        plt.draw()
        plt.pause(0.5)
    plt.show()

    plt.figure
    for t in range(0, 50, simulation_settings.TimeStep):
        plt.clf()
        # Plot reservoir state (mean speed) at t, real network
        plotResNetSpeed(t, reservoirs, res_output, simul_time, speed_range)
        plt.draw()
        plt.pause(0.5)
    plt.show()
