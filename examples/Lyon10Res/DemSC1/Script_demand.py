import json

with open("RoutesStruct_Matlab.json", "r") as file:
    routes_matlab = json.load(file)

with open("Configuration.json", "r") as file:
    configuration = json.load(file)

simulation = configuration['SIMULATION'][0]

Demand = {"FLOW DEMAND": []}

routes_list = []
demand_list = []
demand_per_route = []

mn_pair = [f'MacroNode{routes_matlab[0]["NodePath"][0]}', f'MacroNode{routes_matlab[0]["NodePath"][-1]}']
od = 1
i_route = 0
for route in routes_matlab:
    od_id = route['ODmacroID']

    if od_id == od:
        routes_list.append({"ID": f'Route{i_route + 1}', "Coeff": route["AssignCoeff"]})
        demand_per_route.append({"ID": f'Route{i_route + 1}', "Data": route['Demand']})
    else:
        demand_list.append({"OriginMacroNodeID": mn_pair[0],
                            "DestMacroNodeID": mn_pair[1],
                            "Routes": routes_list,
                            "DemandPerRoute": demand_per_route})
        od = od_id
        routes_list = [{"ID": f'Route{i_route + 1}', "Coeff": route["AssignCoeff"]}]
        demand_per_route = [{"ID": f'Route{i_route + 1}', "Data": route['Demand']}]
        mn_pair = [f'MacroNode{route["NodePath"][0]}', f'MacroNode{route["NodePath"][-1]}']

    if i_route == len(routes_matlab) - 1:
        demand_list.append({"OriginMacroNodeID": mn_pair[0],
                            "DestMacroNodeID": mn_pair[1],
                            "Routes": routes_list,
                            "DemandPerRoute": demand_per_route})

    i_route += 1

t_start = 0
t_stop = simulation['Duration']
step = simulation['TimeStep']
time_list = list(range(t_start, t_stop + step, step))
for demand in demand_list:
    route_str = [{"Time": 0, "Data": demand['Routes']}]

    demand_tmp = []
    t = 0
    for time in time_list:
        data = 0
        for route in demand['DemandPerRoute']:
            data += route['Data'][t]

        demand_tmp.append({'Time': time, 'Data': data})

        t += 1

    Demand["FLOW DEMAND"].append({"OriginMacroNodeID": demand['OriginMacroNodeID'],
                                  "DestMacroNodeID": demand['DestMacroNodeID'],
                                  "Demand": demand_tmp,
                                  "Route": route_str})

with open("Demand.json", "w") as file:
    json.dump(Demand, file, indent=4)
