import json

from main_objects import Simulation, Reservoir, Route, MacroNode, Demand, Vehicle
from IO_functions import *
from Solver import *

DEBUG = 0

root='../examples/'
folder='Braess/'

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

numRoutes = len(loadNetwork["ROUTES"])

for i in range(numRoutes):
    route = Route.Route()
    route.load_input(loadNetwork, i)
    routes.append(route)
    if DEBUG == 1:
        print(route.Length, route.ResOriginID, route.ResDestinationID, route.NodeOriginID, route.NodeDestinationID)

numMacroNodes = len(loadNetwork["MACRONODES"])

for i in range(numMacroNodes):
    macronode = MacroNode.MacroNode()
    macronode.load_input(loadNetwork, i)
    macronodes.append(macronode)
    if DEBUG == 1:
        print(macronode.ResID)
    
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
    
elif simulation_settings.DemandType == "DiscreteDemand":
    numDemand = len(loadDemand["DISCRETE DEMAND"])
    if DEBUG == 1:
        print(numDemand)
    for i in range(numDemand):
        GlobalDemand[i] = Demand.DiscreteDemand()
        GlobalDemand[i].load_input(loadDemand, i)
    if DEBUG == 1:
        print(GlobalDemand[0].TripID)
else:
    print("Demand Type error")

#### Initialize variables ####
if simulation_settings.Solver == "TripBased":
    Vehicles = {}   
    
for r in reservoirs:
    r.init_fct_param(0.8, 1, 1, len(simulation_settings.Modes))
    if DEBUG == 1:
        print(r.EntryfctParam)
    
Init(reservoirs, routes, macronodes, GlobalDemand)

#### Algorithms ####

if simulation_settings.Solver == "AccBased":
    AccBased(simulation_settings, reservoirs, routes, macronodes, GlobalDemand)
elif simulation_settings.Solver == "TripBased":
    TripBased(simulation_settings, reservoirs, routes, macronodes, Vehicle)

#### Outputs ####

## Reservoir config and states
SimulTime = list(range(0, Simu.Duration, Simu.TimeStep))
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
    plotResBallConfig(Res, 1, 0.5, [1.5, 1.5])
    plt.show()

    # Plot reservoir state (total accumulation) at t, schematic representation
    plt.figure
    plotResBallAcc(t0, Res, ResOutput, SimulTime, 0.5, [1.5, 1.5])
    plt.show()

    # Plot reservoir state (accumulation per route) at t, schematic representation
    plt.figure
    plotResBallAccPerRoute(t0, Res, ResOutput, Routes, SimulTime, 0.5, [1.5, 1.5])
    plt.show()

    # Plot reservoir state (mean speed) at t, real network
    plt.figure
    plotResNetSpeed(t0, Res, ResOutput, SimulTime, SpeedRange)
    plt.show()

    # Plot reservoir total number or demand of routes
    plt.figure
    plotResRouteDem(Res, Routes, MacroNodes, Demands, Simu.DemandType, 'demand')
    plt.show()

# Plot macro nodes with route paths
#plt.figure
#plotMacroNodes(Res, 1, MacroNodes, 0, Routes, 0)
#plt.show()

if DYNAMIC_PLOT == 1:
    plt.figure
    for t in range(0, 50, Simu.TimeStep):
        plt.clf()
        # Plot reservoir state (total accumulation) at t, schematic representation
        plotResBallAcc(t, Res, ResOutput, SimulTime, 0.5, [1.5, 1.5])
        plt.draw()
        plt.pause(0.5)
    plt.show()

    plt.figure
    for t in range(0, 50, Simu.TimeStep):
        plt.clf()
        # Plot reservoir state (accumulation per route) at t, schematic representation
        plotResBallAccPerRoute(t, Res, ResOutput, Routes, SimulTime, 0.5, [1.5, 1.5])
        plt.draw()
        plt.pause(0.5)
    plt.show()

    plt.figure
    for t in range(0, 50, Simu.TimeStep):
        plt.clf()
        # Plot reservoir state (mean speed) at t, real network
        plotResNetSpeed(t, Res, ResOutput, SimulTime, SpeedRange)
        plt.draw()
        plt.pause(0.5)
    plt.show()
