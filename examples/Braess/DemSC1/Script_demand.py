import math
import json


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


# Open file
with open("Demand.json", "r") as file:
    Demand = json.load(file)

# ROUTE 1
tStart1 = 500
tStop1 = 2500
step1 = 60

time_temp1 = list(range(tStart1, tStop1 + step1, step1))

q01 = 0.1
q11 = 0.8
q21 = 0.1
fact11 = q11/q01
fact21 = q21/q01

data_temp1 = tray_fct(time_temp1, tStart1, tStart1 + 500, tStop1 - 500, tStop1, fact11, fact21)
data_temp1 = [element * q01 for element in data_temp1]

time_temp1.insert(0, 0)
data_temp1.insert(0, q01)
data_temp1.append(q21)

# ROUTE 2
tStart2 = 500
tStop2 = 2000
step2 = 60

time_temp2 = list(range(tStart2, tStop2 + step2, step2))

q02 = 0.2
q12 = 0.9
q22 = 0.2
fact12 = q12/q02
fact22 = q22/q02

data_temp2 = tray_fct(time_temp2, tStart2, tStart2 + 500, tStop2 - 500, tStop2, fact12, fact22)
data_temp2 = [element * q02 for element in data_temp2]

time_temp2.insert(0, 0)
time_temp2.append(tStop2 + step2)
data_temp2.insert(0, q02)
data_temp2.append(q22)

# - For a same macronodes couple and same mode :
# - Routes coefficients + Global demand = Demand sum - #
data_sum = []
data_coeff = []
for i in range(len(data_temp2)):
    data_sum.append(data_temp1[i] + data_temp2[i])
    data_coeff.append([{"ID": "Route1", "Coeff": data_temp1[i] / data_sum[i]},
                       {"ID": "Route2", "Coeff": data_temp2[i] / data_sum[i]}])
for i in range(len(data_temp2), len(data_temp1)):
    data_sum.append(data_temp1[i] + q22)
    data_coeff.append([{"ID": "Route1", "Coeff": data_temp1[i] / data_sum[i]},
                       {"ID": "Route2", "Coeff": q22 / data_sum[i]}])

demand_temp = []
route_temp = []
for i in range(len(time_temp1)):
    demand_temp.append({"Time": time_temp1[i], "Data": data_sum[i]})
    route_temp.append({"Time": time_temp1[i], "Data": data_coeff[i]})

Demand["FLOW DEMAND"][0]["Demand"] = demand_temp
Demand["FLOW DEMAND"][0]["Route"] = route_temp

with open("Demand.json", "w") as file:
    json.dump(Demand, file, indent=4)
