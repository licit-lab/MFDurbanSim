import math
import json


def qind(t_list, t_start, t_stop, q0, q1):
    qin_d = []
    for t in t_list:
        a = int(t <= t_start)
        b = int(t > 0)
        c = int(t_start < t)
        d = int(t <= t_stop)
        e = int(t_stop < t)

        qin_d.append(q0 * (a * b) + q1 * (c * d) + q0 * e)

    return qin_d


# Open file
with open("Demand.json", "r") as file:
    Demand = json.load(file)

Demand["FLOW DEMAND"] = []

# ROUTE 1
tStart1 = 500
tStop1 = 2500
step1 = 60

time_temp1 = list(range(tStart1, tStop1 + step1, step1))

q01 = 0.05
q11 = 1.2
q21 = 0.05

data_temp1 = qind(time_temp1, tStart1, tStop1, q01, q11)

time_temp1.insert(0, 0)
data_temp1.insert(0, q01)
data_temp1.append(q21)

# ROUTE 2
tStart2 = 500
tStop2 = 2500
step2 = 60

time_temp2 = list(range(tStart2, tStop2 + step2, step2))

q02 = 0.03
q12 = 0.7
q22 = 0.03

data_temp2 = qind(time_temp2, tStart2, tStop2, q02, q12)

time_temp2.insert(0, 0)
data_temp2.insert(0, q02)
data_temp2.append(q22)

# ROUTE 3
tStart3 = 500
tStop3 = 2500
step3 = 60

time_temp3 = list(range(tStart3, tStop3 + step3, step3))

q03 = 0.02
q13 = 0.7
q23 = 0.02

data_temp3 = qind(time_temp3, tStart3, tStop3, q03, q13)

time_temp3.insert(0, 0)
data_temp3.insert(0, q03)
data_temp3.append(q23)

# ROUTE 4
tStart4 = 500
tStop4 = 2500
step4 = 60

time_temp4 = list(range(tStart4, tStop4 + step4, step4))

q04 = 0.01
q14 = 0.22
q24 = 0.01

data_temp4 = qind(time_temp4, tStart4, tStop4, q04, q14)

time_temp4.insert(0, 0)
data_temp4.insert(0, q04)
data_temp4.append(q24)

# - For a same macronodes couple and same mode :
# - Routes coefficients + Global demand = Demand sum - #

# Macronode couple : MN1 -> MN3, mode = VL
data_sum = []
data_coeff = []
for i in range(len(data_temp1)):
    data_sum.append(data_temp1[i] + data_temp2[i] + data_temp3[i])
    data_coeff.append([{"ID": "Route1", "Coeff": data_temp1[i] / data_sum[i]},
                       {"ID": "Route2", "Coeff": data_temp2[i] / data_sum[i]},
                       {"ID": "Route3", "Coeff": data_temp3[i] / data_sum[i]}])

demand_temp = []
route_temp = []
for i in range(len(time_temp1)):
    demand_temp.append({"Time": time_temp1[i], "Data": data_sum[i]})
    route_temp.append({"Time": time_temp1[i], "Data": data_coeff[i]})

Demand["FLOW DEMAND"].append({"OriginMacroNodeID": "MacroNode1", "DestMacroNodeID": "MacroNode3", "Mode": "VL",
                              "Demand": demand_temp, "Route": route_temp})

# Macronode couple : MN1 -> MN3, mode = BUS
data_sum = []
data_coeff = []
for i in range(len(data_temp4)):
    data_sum.append(data_temp4[i])
    data_coeff.append([{"ID": "Route4", "Coeff": data_temp4[i] / data_sum[i]}])

demand_temp = []
route_temp = []
for i in range(len(time_temp4)):
    demand_temp.append({"Time": time_temp4[i], "Data": data_sum[i]})
    route_temp.append({"Time": time_temp4[i], "Data": data_coeff[i]})

Demand["FLOW DEMAND"].append({"OriginMacroNodeID": "MacroNode1", "DestMacroNodeID": "MacroNode3", "Mode": "BUS",
                              "Demand": demand_temp, "Route": route_temp})

with open("Demand.json", "w") as file:
    json.dump(Demand, file, indent=4)
