import math
import json
import collections

with open("RoutesStruct_Matlab.json", "r") as file:
    routes_matlab = json.load(file)

with open("Network.json", "r") as file:
    network = json.load(file)

demand_tmp = []
routes_per_node_couple = []

for route in range(len(routes_matlab)):
    node_origin = routes_matlab[route]["NodePath"][0]
    node_dest = routes_matlab[route]["NodePath"][-1]

    routes_per_node_couple.append({"node_pair": [node_origin, node_dest], "routes": []})

    for route2 in range(len(routes_matlab)):
        node_origin2 = routes_matlab[route2]["NodePath"][0]
        node_dest2 = routes_matlab[route2]["NodePath"][-1]

        if node_origin2 == node_origin and node_dest2 == node_dest:
            routes_per_node_couple[route]["routes"].append({"id": route2+1, "assign_coeff": routes_matlab[route2]["AssignCoeff"]})

routes_per_node_couple_new = []
for item in routes_per_node_couple:
    if item not in routes_per_node_couple_new:
        routes_per_node_couple_new.append(item)

#Open file
with open("Demand.json", "r") as file:
    Demand = json.load(file)

Demand["FLOW DEMAND"] = []

for item in routes_per_node_couple_new:
    data_str = []
    route_str = []
    for route in item["routes"]:
        data_str.append({"ID": "Route" + str(route["id"]), "Coeff": route["assign_coeff"]})

    route_str.append({"Time": 0, "Data": data_str})

    Demand["FLOW DEMAND"].append({"OriginMacroNodeID": "MacroNode" + str(item["node_pair"][0]),
                                  "DestMacroNodeID": "MacroNode" + str(item["node_pair"][-1]),
                                  "Demand": [],
                                  "Route": route_str})


with open("Demand.json", "w") as file:
    json.dump(Demand, file, indent = 4)
