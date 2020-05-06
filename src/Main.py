import json

import Simulation
import Reservoir
import Route
import Vehicle
import MacroNode

####Load Input Parameters####

#Configuration
newSimulation = Simulation.Simulation()
newSimulation.load_input("config_files\Configuration.json")

#Network
with open("config_files/Network.json", "r") as file:
    loadNetwork = json.load(file)

numRes = len(loadNetwork["RESERVOIRS"])
Res = {}
for i in range(numRes):
    Res[i] = Reservoir.Reservoir()
    Res[i].load_input(loadNetwork, i)

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
