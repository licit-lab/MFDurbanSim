import json
import math


def tray_fct(t_list, t_start, t_tray1, t_tray2, t_end, tray_factor, final_factor):
    # Return a tray function: initial value, then sinusoidal transition to a
    # steady value, and finally another sinusoidal transition to a final value
    #
    # INPUTS
    # ---- t           : scalar or vector, time [s]
    # ---- t_start      : scalar, tray start time [s]
    # ---- t_tray1      : scalar, tray start transition end time [s]
    # ---- t_tray2      : scalar, tray end transition start time [s]
    # ---- t_end        : scalar, tray end time [s]
    # ---- tray_factor  : scalar, multiplier factor, amplitude of the tray
    # ---- final_factor : scalar, multiplier factor, amplitude of the new value
    #                   after the tray
    #
    # OUTPUTS
    # --- tray_f : vector, same size as t, function values

    tray_width1 = 2 * (t_tray1 - t_start)
    tray_width2 = 2 * (t_end - t_tray2)

    tray_f = []

    for t in t_list:
        a = int(t_start <= t)
        b = int(t < t_tray1)
        c = int(t_tray1 <= t)
        d = int(t < t_tray2)
        e = int(t_tray2 <= t)
        f = int(t < t_end)
        g = int(t_end <= t)

        tray_f.append(
            1 + a * b * (tray_factor - 1) * (1 + math.sin(2 * math.pi * (t - t_start) / tray_width1 - math.pi / 2)) / 2
            + c * d * (tray_factor - 1)
            + e * f * (final_factor - 1 + (tray_factor - final_factor) * (
                        1 + math.sin(2 * math.pi * (t - t_end + tray_width2) / tray_width2 - math.pi / 2)) / 2)
            + g * (final_factor - 1))

    return tray_f


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
    else:
        demand_list.append({"OriginMacroNodeID": mn_pair[0],
                            "DestMacroNodeID": mn_pair[1],
                            "Routes": routes_list})
        od = od_id
        routes_list = [{"ID": f'Route{i_route + 1}', "Coeff": route["AssignCoeff"]}]
        demand_per_route = [{"ID": f'Route{i_route + 1}', "Data": route['Demand']}]
        mn_pair = [f'MacroNode{route["NodePath"][0]}', f'MacroNode{route["NodePath"][-1]}']

    if i_route == len(routes_matlab) - 1:
        demand_list.append({"OriginMacroNodeID": mn_pair[0],
                            "DestMacroNodeID": mn_pair[1],
                            "Routes": routes_list})

    i_route += 1

# For all macro nodes couple
tStart1 = 1000
tStop1 = 3000
step1 = 60

time_temp1 = list(range(tStart1, tStop1 + step1, step1))

q01 = 0.01
q11 = 0.015
q21 = 0.01
fact11 = q11/q01
fact21 = q21/q01

data_temp1 = tray_fct(time_temp1, tStart1, tStart1 + 500, tStop1 - 500, tStop1, fact11, fact21)
data_temp1 = [element * q01 for element in data_temp1]

time_temp1.insert(0, 0)
data_temp1.insert(0, q01)
data_temp1.append(q21)

demand_tmp = []
for i in range(len(time_temp1)):
    demand_tmp.append({"Time": time_temp1[i], "Data": data_temp1[i]})

for demand in demand_list:
    route_str = [{"Time": 0, "Data": demand['Routes']}]

    Demand["FLOW DEMAND"].append({"OriginMacroNodeID": demand['OriginMacroNodeID'],
                                  "DestMacroNodeID": demand['DestMacroNodeID'],
                                  "Demand": demand_tmp,
                                  "Route": route_str})

with open("Demand.json", "w") as file:
    json.dump(Demand, file, indent=4)
