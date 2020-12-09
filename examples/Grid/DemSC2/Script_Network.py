import json

with open("Network.json", "r") as file:
    Network = json.load(file)

# MACRONODES
with open("MNStruct_Matlab.json", "r") as file:
    NodeMatlab = json.load(file)

Network["MACRONODES"] = []
capacity_data = []
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
