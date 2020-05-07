import json

from main_objects import Simulation, Reservoir, Route, MacroNode, Demand, Vehicle
from IO_functions import *

DEBUG = 0

#### Load Input Parameters ####

#Configuration
with open("config_files\Configuration.json", "r") as file:
    loadSimulation = json.load(file)
file.close()

Simu = Simulation.Simulation()
Simu.load_input(loadSimulation)

#Network
with open("config_files/Network.json", "r") as file:
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
    
#Demand
with open("config_files/Demand.json", "r") as file:
    loadDemand = json.load(file)
file.close()

Demands = {}
if Simu.DemandType == "FlowDemand":
    Demands[0] = Demand.FlowDemand()
    Demands[0].load_input(loadDemand)
    if DEBUG == 1:
        print(Demands[0].Route)
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
if Simu.Solver == "trip-based":
    Vehicles = {}   
    
for i in range(numRes):
    Res[i].init_fct_param(0.8, 1, 1, len(Simu.Modes))
    if DEBUG == 1:
        print(Res[i].EntryfctParam)
    
Init(Res, Routes, MacroNodes, Demands)

if DEBUG == 1:
    print(Res[0].MacroNodesID)
    print(Res[1].MacroNodesID)
    print(Res[0].AdjacentResID)
    print(Res[1].AdjacentResID)
    print(Res[1].TripLengthPerRoute)
    print(Res[0].DestNodesIndex)
    print(Res[1].OriNodesIndex)


#### Algorithms ####

#### Outputs ####

    
