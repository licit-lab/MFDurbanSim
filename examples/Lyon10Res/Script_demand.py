import json

with open("RoutesStruct_Matlab.json", "r") as file:
    routes_matlab = json.load(file)

with open("ODmacroStruct_Matlab.json", "r") as file:
    od_matlab = json.load(file)

Demand = {"FLOW DEMAND": []}

for od in od_matlab:
    data_str = []
    route_str = []

    # Recover assignment coefficients corresponding to a route id
    if isinstance(od["RoutesID"], list):
        for route_id in od["RoutesID"]:
            data_str.append({"ID": "Route" + str(route_id), "Coeff": routes_matlab[route_id - 1]["AssignCoeff"]})
    elif isinstance(od["RoutesID"], int):
        data_str.append({"ID": "Route" + str(od["RoutesID"]), "Coeff": routes_matlab[od["RoutesID"] - 1]["AssignCoeff"]})

    route_str.append({"Time": 0, "Data": data_str})

    demand_tmp = [{"Time": od["Demand"]["Time"][0], "Data": od["Demand"]["Data"][0]}]

    for j in range(1, len(od["Demand"]["Time"])):
        if od["Demand"]["Data"][j] != od["Demand"]["Data"][j-1] and od["Demand"]["Time"][j] < 1802:
            demand_tmp.append({"Time": od["Demand"]["Time"][j], "Data": od["Demand"]["Data"][j]})

    Demand["FLOW DEMAND"].append({"OriginMacroNodeID": "MacroNode" + str(od["NodeOriginID"]),
                                  "DestMacroNodeID": "MacroNode" + str(od["NodeDestinationID"]),
                                  "Demand": demand_tmp,
                                  "Route": route_str})

with open("Demand.json", "w") as file:
    json.dump(Demand, file, indent=4)
