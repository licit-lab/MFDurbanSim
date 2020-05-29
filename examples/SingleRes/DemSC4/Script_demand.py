import math
import json

#function trayf = trayfct(t,tstart,ttray1,ttray2,tend,trayfactor,finalfactor)
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

tStart = 1000
tStop = 3000
step = 20

#Route 1
time_temp1 = list(range(tStart, tStop + step, step))

q0 = 0.3
q1 = 0.8
q2 = 0.3
fact1 = q1/q0
fact2 = q2/q0

data_temp1 = trayfct(time_temp1, tStart, tStart + 500, tStop - 500, tStop, fact1, fact2)
data_temp1 = [element * q0 for element in data_temp1]

time_temp1.insert(0, 0)
time_temp1.append(tStop + step)
data_temp1.insert(0, q0)
data_temp1.append(q2)

demand_temp1 = []
for i in range(len(time_temp1)):
    demand_temp1.append({"Time": time_temp1[i], "Data": data_temp1[i]})

Demand["FLOW DEMAND"][0]["Demand"] = demand_temp1

#Route 2
time_temp2 = list(range(tStart, tStop + step, step))

q0 = 0.3
q1 = 1.1
q2 = 0.3
fact1 = q1/q0
fact2 = q2/q0

data_temp2 = trayfct(time_temp2, tStart, tStart + 500, tStop - 500, tStop, fact1, fact2)
data_temp2 = [element * q0 for element in data_temp2]

time_temp2.insert(0, 0)
time_temp2.append(tStop + step)
data_temp2.insert(0, q0)
data_temp2.append(q2)

demand2_temp = []
for i in range(len(time_temp2)):
    demand2_temp.append({"Time": time_temp2[i], "Data": data_temp2[i]})

Demand["FLOW DEMAND"][1]["Demand"] = demand2_temp

#Write file
with open("Demand.json", "w") as file:
    json.dump(Demand, file, indent = 4)
file.close()
