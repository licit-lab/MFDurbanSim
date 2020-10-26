import os
import json

from main_objects import Simulation, Reservoir, Route, MacroNode, Demand, Vehicle

import IO_functions
import Solver 
import plot_fct

DEBUG = 0
PLOT = 0
DYNAMIC_PLOT = 1

root = os.getcwd()
root = os.path.join(root, "symures-dev/examples")

#root='../../../samples/'
#folder='3reservoirs/'
folder = 'SingleRes/DemSC1/'
path = os.path.join(root, folder)

reservoirs = []                 # list of reservoirs
routes = []                     # list of routes
macronodes=[]                   # list of macro-nodes

#### Load Input Parameters ####

# Configuration
path_config = os.path.join(path, "Configuration.json")
with open(path_config, "r") as file:
    loadSimulation = json.load(file)

simulation_settings = Simulation.Simulation()
simulation_settings.load_input(loadSimulation, path)

# Network loading
with open(root + folder + simulation_settings.Network, "r") as file:
    loadNetwork = json.load(file)

numRes = len(loadNetwork["RESERVOIRS"])

for i in range(numRes):
    res = Reservoir.Reservoir()
    res.load_input(loadNetwork, i)
    reservoirs.append(res)
    if DEBUG == 1:
        print(res.ID)
        
numMacroNodes = len(loadNetwork["MACRONODES"])

for i in range(numMacroNodes):
    macronode = MacroNode.MacroNode()
    macronode.load_input(loadNetwork, i)
    macronodes.append(macronode)
    if DEBUG == 1:
        print(macronode.ResID)

numRoutes = len(loadNetwork["ROUTES"])

for i in range(numRoutes):
    route = Route.Route()
    route.load_input(loadNetwork, i, reservoirs, macronodes)
    routes.append(route)
    if DEBUG == 1:
        print(route.Length, route.ResOriginID, route.ResDestinationID, route.OriginMacroNode, route.DestMacroNode)


    
#Demand
with open(root + folder + simulation_settings.Demand, "r") as file:
    loadDemand = json.load(file)
file.close()

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
    GlobalDemand =  []
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

with open(root + folder + "Output.json", "r") as file:
    Output = json.load(file)
file.close()

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