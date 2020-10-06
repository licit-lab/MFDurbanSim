import json
import matplotlib.pyplot as plt

from main_objects import Simulation, Reservoir, Route, MacroNode, Demand, Vehicle
import IO_functions
import Solver
import plot_fct

DEBUG = 0
PLOT = 0
DYNAMIC_PLOT = 0
root = "C:/Dev/symures-dev-master/symures-dev/examples/"
folder = "SingleRes/DemSC1/"

#### Load Input Parameters ####

# Configuration
with open(root + folder + "Configuration.json", "r") as file:
    load_simulation = json.load(file)

simulation = Simulation.Simulation()
simulation.load_input(load_simulation)

# Network
with open(root + folder + simulation.Network, "r") as file:
    load_network = json.load(file)

num_res = len(load_network["RESERVOIRS"])
reservoirs_list = {}
for i in range(num_res):
    reservoirs_list[i] = Reservoir.Reservoir()
    reservoirs_list[i].load_input(load_network, i)
    if DEBUG == 1:
        print(reservoirs_list[i].ID)

num_routes = len(load_network["routes_list"])
routes_list = {}
for i in range(num_routes):
    routes_list[i] = Route.Route()
    routes_list[i].load_input(load_network, i)
    if DEBUG == 1:
        print(routes_list[i].Length)
        print(routes_list[i].ResOriginID)
        print(routes_list[i].ResDestinationID)
        print(routes_list[i].NodeOriginID)
        print(routes_list[i].NodeDestinationID)

num_macronodes = len(load_network["macronodes_list"])
macronodes_list = {}
for i in range(num_macronodes):
    macronodes_list[i] = MacroNode.MacroNode()
    macronodes_list[i].load_input(load_network, i)
    if DEBUG == 1:
        print(macronodes_list[i].ResID)

# Demand
with open(root + folder + simulation.Demand, "r") as file:
    load_demand = json.load(file)
file.close()

demands_list = {}
if simulation.DemandType == "FlowDemand":
    numDemand = len(load_demand["FLOW DEMAND"])
    if DEBUG == 1:
        print(numDemand)
    for i in range(numDemand):
        demands_list[i] = Demand.FlowDemand()
        demands_list[i].load_input(load_demand, i)
        if DEBUG == 1:
            print(demands_list[i].Route)
elif simulation.DemandType == "DiscreteDemand":
    numDemand = len(load_demand["DISCRETE DEMAND"])
    if DEBUG == 1:
        print(numDemand)
    for i in range(numDemand):
        demands_list[i] = Demand.DiscreteDemand()
        demands_list[i].load_input(load_demand, i)
    if DEBUG == 1:
        print(demands_list[0].TripID)
else:
    print("Demand Type error")

#### Initialize variables ####
if simulation.Solver == "TripBased":
    Vehicles = {}

for i in range(num_res):
    reservoirs_list[i].init_fct_param(0.8, 1, 1, len(simulation.Modes))
    if DEBUG == 1:
        print(reservoirs_list[i].EntryfctParam)

IO_functions.Init(reservoirs_list, routes_list, macronodes_list, demands_list)

if DEBUG == 1:
    print(reservoirs_list[0].MacroNodesID)
    print(reservoirs_list[0].AdjacentResID)
    print(routes_list[0].TotalTime)

#### Algorithms ####

if simulation.Solver == "AccBased":
    Solver.AccBased(simulation, reservoirs_list, routes_list, macronodes_list, demands_list)
elif simulation.Solver == "TripBased":
    Solver.TripBased(simulation, reservoirs_list, routes_list, macronodes_list, demands_list, Vehicle)

#### Outputs ####


#### Plotting results ####

## Reservoir config and states
simu_time = list(range(0, simulation.Duration, simulation.TimeStep))
speed_range = [3, 14]
t0 = 10

with open(root + folder + "output.json", "r") as file:
    output = json.load(file)

reservoirs_output = output["RESERVOIRS"]
routes_output = output["routes_list"]

if PLOT == 1:
    # Plot reservoir schematic representation (borders and adjacent connections)
    plt.figure
    plot_fct.plotResBallConfig(reservoirs_list, 1, 0.5, [1.5, 1.5])
    plt.show()

    # Plot reservoir state (total accumulation) at t, schematic representation
    plt.figure
    plot_fct.plotResBallAcc(t0, reservoirs_list, reservoirs_output, simu_time, 0.5, [1.5, 1.5])
    plt.show()

    # Plot reservoir state (accumulation per route) at t, schematic representation
    plt.figure
    plot_fct.plotResBallAccPerRoute(t0, reservoirs_list, reservoirs_output, routes_list, simu_time, 0.5, [1.5, 1.5])
    plt.show()

    # Plot reservoir state (mean speed) at t, real network
    plt.figure
    plot_fct.plotResNetSpeed(t0, reservoirs_list, reservoirs_output, simu_time, speed_range)
    plt.show()

    # Plot reservoir total number or demand of routes_list
    plt.figure
    plot_fct.plotResRouteDem(reservoirs_list, routes_list, macronodes_list, demands_list, simulation.DemandType, 'demand')
    plt.show()

# Plot macro nodes with route paths
#plt.figure
#plot_fct.plotMacroNodes(reservoirs_list, 1, macronodes_list, 0, routes_list, 0)
#plt.show()

if DYNAMIC_PLOT == 1:
    plt.figure
    for t in range(0, 50, simulation.TimeStep):
        plt.clf()
        # Plot reservoir state (total accumulation) at t, schematic representation
        plot_fct.plotResBallAcc(t, reservoirs_list, reservoirs_output, simu_time, 0.5, [1.5, 1.5])
        plt.draw()
        plt.pause(0.5)
    plt.show()

    plt.figure
    for t in range(0, 50, simulation.TimeStep):
        plt.clf()
        # Plot reservoir state (accumulation per route) at t, schematic representation
        plot_fct.plotResBallAccPerRoute(t, reservoirs_list, reservoirs_output, routes_list, simu_time, 0.5, [1.5, 1.5])
        plt.draw()
        plt.pause(0.5)
    plt.show()

    plt.figure
    for t in range(0, 50, simulation.TimeStep):
        plt.clf()
        # Plot reservoir state (mean speed) at t, real network
        plot_fct.plotResNetSpeed(t, reservoirs_list, reservoirs_output, simu_time, speed_range)
        plt.draw()
        plt.pause(0.5)
    plt.show()