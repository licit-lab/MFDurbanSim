import json

from main_objects import Simulation, Reservoir, Route, MacroNode, Demand, Vehicle
from IO_functions import *
from Solver import *
from plot_fct import *

DEBUG = 0
PLOT = 0
DYNAMIC_PLOT = 1

root='../examples/'
#root='../../../samples/'
#folder='3reservoirs/'
folder='Braess/DemSC1/'

reservoirs = []                 # list of reservoirs
routes = []                     # list of routes
macronodes=[]                   # list of macro-nodes

#### Load Input Parameters ####

# Configuration
with open(root + folder +"Configuration.json", "r") as file:
    loadSimulation = json.load(file)
file.close()

simulation_settings = Simulation.Simulation()
simulation_settings.load_input(loadSimulation)

# Network loading
with open(root + folder + simulation_settings.Network, "r") as file:
    loadNetwork = json.load(file)
file.close()

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
        print(route.Length, route.ResOriginID, route.ResDestinationID, route.NodeOriginID, route.NodeDestinationID)


    
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
    
Init(reservoirs, routes, macronodes)

#### Algorithms ####

if simulation_settings.Solver == "AccBased":
    AccBased(simulation_settings, reservoirs, routes, macronodes, GlobalDemand)
elif simulation_settings.Solver == "TripBased":
    TripBased(simulation_settings, reservoirs, routes, macronodes, GlobalDemand)

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
    plt.figure
    plotResBallConfig(reservoirs, 1, 0.5, [1.5, 1.5])
    plt.show()

    # Plot reservoir state (total accumulation) at t, schematic representation
    plt.figure
    plotResBallAcc(t0, reservoirs, ResOutput, SimulTime, 0.5, [1.5, 1.5])
    plt.show()

    # Plot reservoir state (accumulation per route) at t, schematic representation
    plt.figure
    plotResBallAccPerRoute(t0, reservoirs, ResOutput, routes, SimulTime, 0.5, [1.5, 1.5])
    plt.show()

    # Plot reservoir state (mean speed) at t, real network
    plt.figure
    plotResNetSpeed(t0, reservoirs, ResOutput, SimulTime, SpeedRange)
    plt.show()

    # Plot reservoir total number or demand of routes
    plt.figure
    plotResRouteDem(reservoirs, routes, macronodes, GlobalDemand, simulation_settings.DemandType, 'demand')
    plt.show()

# Plot macro nodes with route paths
#plt.figure
#plotMacroNodes(Res, 1, MacroNodes, 0, Routes, 0)
#plt.show()

if DYNAMIC_PLOT == 1:
    plt.figure
    for t in range(0, simulation_settings.Duration, simulation_settings.TimeStep):
        plt.clf()
        # Plot reservoir state (total accumulation) at t, schematic representation
        plotResBallAcc(t, reservoirs, ResOutput, SimulTime, 0.5, [1.5, 1.5])
        plt.draw()
        plt.pause(5)
    plt.show()

    plt.figure
    for t in range(0, simulation_settings.Duration, simulation_settings.TimeStep):
        plt.clf()
        # Plot reservoir state (accumulation per route) at t, schematic representation
        plotResBallAccPerRoute(t, reservoirs, ResOutput, routes, SimulTime, 0.5, [1.5, 1.5])
        plt.draw()
        plt.pause(5)
    plt.show()

    plt.figure
    for t in range(0, simulation_settings.Duration, simulation_settings.TimeStep):
        plt.clf()
        # Plot reservoir state (mean speed) at t, real network
        plotResNetSpeed(t, reservoirs, ResOutput, SimulTime, SpeedRange)
        plt.draw()
        plt.pause(5)
    plt.show()
