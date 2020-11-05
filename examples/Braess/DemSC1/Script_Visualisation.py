import json

import matplotlib.pyplot as plt

import IO_functions
import plot_fct
import main_objects.Reservoir as Reservoir
import main_objects.MacroNode as MacroNode
import main_objects.Route as Route

with open("Network.json", "r") as file:
    network = json.load(file)

reservoirs = []
macronodes = []
routes = []

num_res = len(network["RESERVOIRS"])
num_mn = len(network["MACRONODES"])
num_routes = len(network["ROUTES"])

for i in range(num_res):
    res = Reservoir.Reservoir()
    res.load_input(network, i)
    reservoirs.append(res)

for i in range(num_mn):
    mn = MacroNode.MacroNode()
    mn.load_input(network, i, reservoirs)
    macronodes.append(mn)

for i in range(num_routes):
    route = Route.Route()
    route.load_input(network, i, reservoirs, macronodes)
    routes.append(route)

IO_functions.Init(reservoirs, routes, macronodes)

# Plot reservoirs, nodes and route paths
plt.figure
plot_fct.plot_network(reservoirs, macronodes, routes)
plt.show()
