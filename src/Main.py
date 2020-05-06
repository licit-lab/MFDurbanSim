import json

from main_objects import Simulation, Reservoir, Route, MacroNode, Demand, Vehicle


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
    #print(Res[i].ID)

numRoutes = len(loadNetwork["ROUTES"])
Routes = {}
for i in range(numRoutes):
    Routes[i] = Route.Route()
    Routes[i].load_input(loadNetwork, i)

numMacroNodes = len(loadNetwork["MACRONODES"])
MacroNodes = {}
for i in range(numMacroNodes):
    MacroNodes[i] = MacroNode.MacroNode()
    MacroNodes[i].load_input(loadNetwork, i)
    
#Demand
with open("config_files/Demand.json", "r") as file:
    loadDemand = json.load(file)
file.close()

Demands = {}
if Simu.DemandType == "FlowDemand":
    Demands = Demand.FlowDemand()
    Demands.load_input(loadDemand)
    #print(Demands.Route)
elif Simu.DemandType == "DiscreteDemand":
    numDemand = len(loadDemand["DISCRETE DEMAND"])
    #print(numDemand)
    for i in range(numDemand):
        Demands[i] = Demand.DiscreteDemand()
        Demands[i].load_input(loadDemand, i)
        #print(Demands[0].TripID)
else:
    print("Demand Type error")

#### Initialize variables ####


#### Algorithms ####

#### Outputs ####

    
