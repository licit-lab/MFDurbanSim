import math
import json

# trayf = trayfct(t,tstart,ttray1,ttray2,tend,trayfactor,finalfactor)
# Return a tray function: initial value, then sinusoidal transition to a
# steady value, and finally another sinusoidal transition to a final value
#
# INPUTS
#---- t           : scalar or vector, time [s]
#---- tstart      : scalar, tray start time [s]
#---- ttray1      : scalar, tray start transition end time [s]
#---- ttray2      : scalar, tray end transition start time [s]
#---- tend        : scalar, tray end time [s]
#---- trayfactor  : scalar, multiplier factor, amplitude of the tray
#---- finalfactor : scalar, multiplier factor, amplitude of the new value
#                   after the tray
#
# OUTPUTS
#--- trayf : vector, same size as t, function values

def trayfct(t, tStart, tTray1, tTray2, tEnd, trayFactor, finalFactor):
    trayWidth1 = 2 * (tTray1 - tStart);
    trayWidth2 = 2 * (tEnd - tTray2);

    trayf = []

    for i in range(len(t)):
        a = int(tStart <= t[i])
        b = int(t[i] < tTray1)
        c = int(tTray1 <= t[i])
        d = int(t[i] < tTray2)
        e = int(tTray2 <= t[i])
        f = int(t[i] < tEnd)
        g = int(tEnd <= t[i])
                
        trayf.append(1 + a * b *(trayFactor - 1) * (1 + math.sin(2 * math.pi * (t[i] - tStart) / trayWidth1 - math.pi / 2)) / 2
                        + c * d * (trayFactor - 1)
                        + e * f * (finalFactor - 1 + (trayFactor - finalFactor) * (1 + math.sin(2 * math.pi * (t[i] - tEnd + trayWidth2) / trayWidth2 - math.pi / 2)) / 2)
                        + g * (finalFactor - 1))
            

    return trayf

#Open file
with open("Demand.json", "r") as file:
    Demand = json.load(file)
file.close()

#ROUTE 1
tStart1 = 500
tStop1 = 2500
step1 = 60

time_temp1 = list(range(tStart1, tStop1 + step1, step1))

q01 = 0.35
q11 = 1.1
q21 = 0.35
fact11 = q11/q01
fact21 = q21/q01

data_temp1 = trayfct(time_temp1, tStart1, tStart1 + 500, tStop1 - 500, tStop1, fact11, fact21)
data_temp1 = [element * q01 for element in data_temp1]

time_temp1.insert(0, 0)
data_temp1.insert(0, q01)
data_temp1.append(q21)

#ROUTE 2
tStart2 = 500
tStop2 = 2000
step2 = 60

time_temp2 = list(range(tStart2, tStop2 + step2, step2))

q02 = 0.2
q12 = 0.9
q22 = 0.2
fact12 = q12/q02
fact22 = q22/q02

data_temp2 = trayfct(time_temp2, tStart2, tStart2 + 500, tStop2 - 500, tStop2, fact12, fact22)
data_temp2 = [element * q02 for element in data_temp2]

time_temp2.insert(0, 0)
time_temp2.append(tStop2 + step2)
data_temp2.insert(0, q02)
data_temp2.append(q22)

#ROUTE 3
tStart3 = 500
tStop3 = 2500
step3 = 60

time_temp3 = list(range(tStart3, tStop3 + step3, step3))

q03 = 0.1
q13 = 0.2
q23 = 0.1
fact13 = q13/q03
fact23 = q23/q03

data_temp3 = trayfct(time_temp3, tStart3, tStart3 + 500, tStop3 - 500, tStop3, fact13, fact23)
data_temp3 = [element * q03 for element in data_temp3]

time_temp3.insert(0, 0)
data_temp3.insert(0, q03)
data_temp3.append(q23)

##CALCUL COEFF DES ROUTES + DEMANDE GLOBALE -> somme des demandes pour un même couple de macronodes
data_sum = []
data_coeff = []
for i in range(len(data_temp2)):
    data_sum.append(data_temp1[i] + data_temp2[i] + data_temp3[i])
    data_coeff.append([{"ID":"Route1", "Coeff":data_temp1[i] / data_sum[i]}, {"ID":"Route2", "Coeff":data_temp2[i] / data_sum[i]}, {"ID":"Route3", "Coeff":data_temp3[i] / data_sum[i]}])
for i in range(len(data_temp2), len(data_temp1)):
    data_sum.append(data_temp1[i] + q22 + data_temp3[i])
    data_coeff.append([{"ID":"Route1", "Coeff":data_temp1[i] / data_sum[i]}, {"ID":"Route2", "Coeff":q22 / data_sum[i]}, {"ID":"Route3", "Coeff":data_temp3[i] / data_sum[i]}])

demand_temp = []
route_temp = []
for i in range(len(time_temp3)):
    demand_temp.append({"Time": time_temp1[i], "Data": data_sum[i]})
    route_temp.append({"Time": time_temp1[i], "Data": data_coeff[i]})

Demand["FLOW DEMAND"][0]["Demand"] = demand_temp
Demand["FLOW DEMAND"][0]["Route"] = route_temp

with open("Demand.json", "w") as file:
    json.dump(Demand, file, indent = 4)
file.close()
