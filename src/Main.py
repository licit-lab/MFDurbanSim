import os
import json

from main_objects import Simulation, Reservoir, Route, MacroNode, Demand, Vehicle

import IO_functions
import Solver 
import plot_fct

DEBUG = 0
PLOT = 0
DYNAMIC_PLOT = 0

#root='../../../samples/'
#folder='3reservoirs/'

(head, tail) = os.path.split(os.getcwd())
root = os.path.normpath(os.path.join(head, "examples"))
folder = 'Braess/DemSC1/'
path = os.path.normpath(os.path.join(root, folder))

reservoirs = []                 # list of reservoirs
routes = []                     # list of routes
macronodes = []                 # list of macro-nodes

#### Load Input Parameters ####

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

    # Verify reservoir id is unique
    if res.ID not in list_res_id:
        # Verify Critical accumulation < Maximum accumulation
        i = 0
        for mode in range(len(res.MFDsetting)):
            if res.MFDsetting[mode]["CritAcc"] < res.MFDsetting[mode]["MaxAcc"]:
                i = i + 1

        if i == len(res.MFDsetting):
            list_res_id.append(res.ID)
        else:
            print("MaxAcc <= CritAcc, this reservoir won't be added to the list of reservoirs.")
            continue
    else:
        print("ResID already used, this reservoir won't be added to the list of reservoirs.")
        continue

    reservoirs.append(res)

    if DEBUG == 1:
        print(res.ID)
        
num_mn = len(loadNetwork["MACRONODES"])
list_mn_id = []
for i in range(num_mn):
    macronode = MacroNode.MacroNode()
    macronode.load_input(loadNetwork, i)

    # Verify macro node id is unique
    if macronode.ID not in list_mn_id:
        list_mn_id.append(macronode.ID)
    else:
        print("Macro node ID already used, this macro node won't be added to the list of macro nodes.")
        continue

    macronodes.append(macronode)
    if DEBUG == 1:
        print(macronode.ResID)

'''
    # Verify reservoir is well-defined
    for res_id in macronode.ResID:
        if res_id not in list_res_id:
            print("Reservoir doesn't exist, this macro node won't be added to the list of macro nodes.")
        continue'''



num_routes = len(loadNetwork["ROUTES"])
list_routes_id = []
for i in range(num_routes):
    route = Route.Route()
    route.load_input(loadNetwork, i, reservoirs, macronodes)

    # Verify route id is unique
    if route.ID not in list_routes_id:
        list_routes_id.append(route.ID)
    else:
        print("Route ID already used, this route won't be added to the list of routes.")
        continue

    routes.append(route)
    if DEBUG == 1:
        print(route.Length, route.ResOriginID, route.ResDestinationID, route.OriginMacroNode, route.DestMacroNode)
'''
    # Verify reservoir is well-defined
    for res in route.CrossedReservoirs:
        if res not in reservoirs:
            print("Reservoir doesn't exist, this route won't be added to the list of routes.")
        continue

    # Verify macro node is well-defined
    for node in route.NodePath:
        if node not in macronodes:
            print("Macro node doesn't exist, this route won't be added to the list of routes.")
        continue

    # Verify nb of nodes = nb of reservoirs + 1
    if len(route.NodePath) != len(route.CrossedReservoirs) + 1:
        print("Number of nodes isn't equal to number of reservoirs + 1, this route won't be added to the list of routes.")
        continue'''




#Demand
path_demand = os.path.join(path, simulation_settings.Demand)
with open(path_demand, "r") as file:
    loadDemand = json.load(file)

GlobalDemand = {}  
if simulation_settings.DemandType == "FlowDemand":
    numDemand = len(loadDemand["FLOW DEMAND"])
    if DEBUG == 1:
        print(numDemand)
    for i in range(numDemand):
        GlobalDemand[i] = Demand.FlowDemand()
        GlobalDemand[i].load_input(loadDemand, i)
    
elif simulation_settings.DemandType == "micro":
    numDemand = len(loadDemand["MICRO"])
    GlobalDemand = []
    if DEBUG == 1:
        print(numDemand)
    for i in range(numDemand):
        trip = Demand.DiscreteDemand()
        trip.load_input(loadDemand, i)
        GlobalDemand.append(trip)
    
    # Sorts trips by creation time
    GlobalDemand = sorted(GlobalDemand,key=lambda trip: trip.Time)
else:
    print("Demand Type error")

#### Initialize variables ####
# for r in reservoirs:
#     r.init_fct_param(0.8, 1, 1, len(simulation_settings.Modes))
#     if DEBUG == 1:
#         print(r.EntryfctParam)
    
IO_functions.Init(reservoirs, routes, macronodes)

#### Algorithms ####

if simulation_settings.Solver == "AccBased":
    Solver.AccBased(simulation_settings, reservoirs, routes, macronodes, GlobalDemand)
elif simulation_settings.Solver == "TripBased":
    Solver.TripBased(simulation_settings, reservoirs, routes, macronodes, GlobalDemand)

#### Outputs ####

## Reservoir config and states
SimulTime = list(range(0, simulation_settings.Duration, simulation_settings.TimeStep))
SpeedRange = [3, 14]
t0 = 10

path_output = os.path.join(path, "Output.json")
with open(path_output, "r") as file:
    Output = json.load(file)

ResOutput = Output["RESERVOIRS"]
RoutesOutput = Output["ROUTES"]

if PLOT == 1:
    # Plot reservoir schematic representation (borders and adjacent connections)
    plot_fct.plt.figure
    plot_fct.plotResBallConfig(reservoirs, 1, 0.5, [1.5, 1.5])
    plot_fct.plt.show()

    # Plot reservoir state (total accumulation) at t, schematic representation
    plot_fct.plt.figure
    plot_fct.plotResBallAcc(t0, reservoirs, ResOutput, SimulTime, 0.5, [1.5, 1.5])
    plot_fct.plt.show()

    # Plot reservoir state (accumulation per route) at t, schematic representation
    plot_fct.plt.figure
    plot_fct.plotResBallAccPerRoute(t0, reservoirs, ResOutput, routes, SimulTime, 0.5, [1.5, 1.5])
    plot_fct.plt.show()

    # Plot reservoir state (mean speed) at t, real network
    plot_fct.plt.figure
    plot_fct.plotResNetSpeed(t0, reservoirs, ResOutput, SimulTime, SpeedRange)
    plot_fct.plt.show()

    # Plot reservoir total number or demand of routes
    plot_fct.plt.figure
    plot_fct.plotResRouteDem(reservoirs, routes, macronodes, GlobalDemand, simulation_settings.DemandType, 'demand')
    plot_fct.plt.show()

# Plot macro nodes with route paths
#plt.figure
#plotMacroNodes(Res, 1, MacroNodes, 0, Routes, 0)
#plt.show()

if DYNAMIC_PLOT == 1:
    plot_fct.plt.figure
    for t in range(0, 50, simulation_settings.TimeStep):
        plot_fct.plt.clf()
        # Plot reservoir state (total accumulation) at t, schematic representation
        plot_fct.plotResBallAcc(t, reservoirs, ResOutput, SimulTime, 0.5, [1.5, 1.5])
        plot_fct.plt.draw()
        plot_fct.plt.pause(0.5)
    plot_fct.plt.show()

    plot_fct.plt.figure
    for t in range(0, 50, simulation_settings.TimeStep):
        plot_fct.plt.clf()
        # Plot reservoir state (accumulation per route) at t, schematic representation
        plot_fct.plotResBallAccPerRoute(t, reservoirs, ResOutput, routes, SimulTime, 0.5, [1.5, 1.5])
        plot_fct.plt.draw()
        plot_fct.plt.pause(0.5)
    plot_fct.plt.show()

    plot_fct.plt.figure
    for t in range(0, 50, simulation_settings.TimeStep):
        plot_fct.plt.clf()
        # Plot reservoir state (mean speed) at t, real network
        plot_fct.plotResNetSpeed(t, reservoirs, ResOutput, SimulTime, SpeedRange)
        plot_fct.plt.draw()
        plot_fct.plt.pause(0.5)
    plot_fct.plt.show()