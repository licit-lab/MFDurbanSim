import json
import matplotlib.pyplot as plt

from main_objects import Simulation, Reservoir, Route, MacroNode, Demand, Vehicle
from IO_functions import *
from Solver import *
from plot_fct import *

DEBUG = 0
PLOT = 0
DYNAMIC_PLOT = 0
root = "C:/Dev/symures-dev-master/symures-dev/examples/"
folder = "Braess/DemSC1/"

#### Load Input Parameters ####

# Configuration
with open(root + folder + "Configuration.json", "r") as file:
    loadSimulation = json.load(file)
file.close()

Simu = Simulation.Simulation()
Simu.load_input(loadSimulation)

# Network
with open(root + folder + Simu.Network, "r") as file:
    loadNetwork = json.load(file)
file.close()

numRes = len(loadNetwork["RESERVOIRS"])
Res = {}
for i in range(numRes):
    Res[i] = Reservoir.Reservoir()
    Res[i].load_input(loadNetwork, i)
    if DEBUG == 1:
        print(Res[i].ID)

numRoutes = len(loadNetwork["ROUTES"])
Routes = {}
for i in range(numRoutes):
    Routes[i] = Route.Route()
    Routes[i].load_input(loadNetwork, i)
    if DEBUG == 1:
        print(Routes[i].Length)
        print(Routes[i].ResOriginID)
        print(Routes[i].ResDestinationID)
        print(Routes[i].NodeOriginID)
        print(Routes[i].NodeDestinationID)

numMacroNodes = len(loadNetwork["MACRONODES"])
MacroNodes = {}
for i in range(numMacroNodes):
    MacroNodes[i] = MacroNode.MacroNode()
    MacroNodes[i].load_input(loadNetwork, i)
    if DEBUG == 1:
        print(MacroNodes[i].ResID)

# Demand
with open(root + folder + Simu.Demand, "r") as file:
    loadDemand = json.load(file)
file.close()

Demands = {}
if Simu.DemandType == "FlowDemand":
    numDemand = len(loadDemand["FLOW DEMAND"])
    if DEBUG == 1:
        print(numDemand)
    for i in range(numDemand):
        Demands[i] = Demand.FlowDemand()
        Demands[i].load_input(loadDemand, i)
        if DEBUG == 1:
            print(Demands[i].Route)
elif Simu.DemandType == "DiscreteDemand":
    numDemand = len(loadDemand["DISCRETE DEMAND"])
    if DEBUG == 1:
        print(numDemand)
    for i in range(numDemand):
        Demands[i] = Demand.DiscreteDemand()
        Demands[i].load_input(loadDemand, i)
    if DEBUG == 1:
        print(Demands[0].TripID)
else:
    print("Demand Type error")

#### Initialize variables ####
if Simu.Solver == "TripBased":
    Vehicles = {}

for i in range(numRes):
    Res[i].init_fct_param(0.8, 1, 1, len(Simu.Modes))
    if DEBUG == 1:
        print(Res[i].EntryfctParam)

Init(Res, Routes, MacroNodes, Demands)

if DEBUG == 1:
    print(Res[0].MacroNodesID)
    print(Res[0].AdjacentResID)
    print(Routes[0].TotalTime)

#### Algorithms ####

if Simu.Solver == "AccBased":
    AccBased(Simu, Res, Routes, MacroNodes, Demands)
elif Simu.Solver == "TripBased":
    TripBased(Simu, Res, Routes, MacroNodes, Demands, Vehicle)

#### Outputs ####


#### Plotting results ####

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