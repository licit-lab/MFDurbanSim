import json

with open("Network.json", "r") as file:
    Network = json.load(file)

# RESERVOIRS
with open("ResStruct_Matlab.json", "r") as file:
    ReservoirMatlab = json.load(file)

Network["RESERVOIRS"] = []
i = 1

for res in ReservoirMatlab:
    str_border_points = []

    for j in range(len(res["BorderPoints"][0])):
        str_border_points.append({"x": res["BorderPoints"][0][j], "y": res["BorderPoints"][1][j]})

    str_res_tmp = {"ID": f'Res{i}',
                   "FreeflowSpeed": [{"mode": "VL", "value": res["FreeflowSpeed"]}],
                   "MaxProd": [{"mode": "VL", "value": res["MaxProd"]}],
                   "MaxAcc": [{"mode": "VL", "value": res["MaxAcc"]}],
                   "CritAcc": [{"mode": "VL", "value": res["CritAcc"]}],
                   "Centroid": [{"x": res["Centroid"][0], "y": res["Centroid"][1]}],
                   "BorderPoints": str_border_points}

    i += 1

    Network["RESERVOIRS"].append(str_res_tmp)


# MACRONODES
with open("MNStruct_Matlab.json", "r") as file:
    NodeMatlab = json.load(file)

Network["MACRONODES"] = []
i = 1

for mn in NodeMatlab:
    if mn["Type"] == "border":
        res_id = [f'Res{mn["ResID"][0]}', f'Res{mn["ResID"][1]}']
    else:
        res_id = f'Res{mn["ResID"]}'

    str_node_tmp = {"ID": "MacroNode" + str(i),
                    "Type": mn["Type"],
                    "ResID": res_id,
                    "Capacity": [{'Time': mn['Capacity']['Time'], 'Data': mn['Capacity']['Data']}],
                    "Coord": [{"x": mn["Coord"][0], "y": mn["Coord"][1]}]}
                    
    Network["MACRONODES"].append(str_node_tmp)

    i += 1

# ROUTES
with open("RoutesStruct_Matlab.json", "r") as file:
    RoutesMatlab = json.load(file)

Network["ROUTES"] = []
i = 1

for route in RoutesMatlab:
    res_path = []

    if type(route["ResPath"]) is int:
        res_path.append({"ID": f'Res{route["ResPath"]}', "TripLength": route["TripLengths"]})
    else:
        for res in range(len(route["ResPath"])):
            res_path.append({"ID": f'Res{route["ResPath"][res]}', "TripLength": route["TripLengths"][res]})

    node_path = []
    for node in route["NodePath"]:
        node_path.append(f'MacroNode{node}')

    str_routes_tmp = {"ID": f'Route{i}',
                      "Mode": "VL",
                      "ResPath": res_path,
                      "NodePath": node_path}

    Network["ROUTES"].append(str_routes_tmp)

    i += 1

with open("Network.json", "w") as file:
    json.dump(Network, file, indent=4)
