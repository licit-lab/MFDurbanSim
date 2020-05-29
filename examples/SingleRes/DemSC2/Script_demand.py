import math
import json

# bumpf = bumpfct(t,tstartpeak,tendpeak,peakfactor1,peakfactor2)
# Return a bump function (sinusoidal model): a peak function with final
# value different from initial value
#
# INPUTS
#---- t           : scalar or vector, time [s]
#---- tstartpeak  : scalar, peak start time [s]
#---- tendpeak    : scalar, peak end time [s]
#---- peakfactor1 : scalar, multiplier factor, amplitude of the peak
#---- peakfactor2 : scalar, multiplier factor, amplitude of the new value
#                   after the peak
#
# OUTPUTS
#--- bumpf : vector, same size as t, function values
def bumpfct(t, tStartPeak, tEndPeak, peakFactor1, peakFactor2):
    peakWidth = tEndPeak - tStartPeak
    tMidPeak = (tStartPeak + tEndPeak)//2

    bumpf = []
            
    for i in range(len(t)):
        a = int(tStartPeak <= t[i])
        b = int(t[i] < tMidPeak)
        c = int(tMidPeak <= t[i])
        d = int(t[i] < tEndPeak)
        e = int(tEndPeak <= t[i])

        bumpf.append(1 + a * b * (peakFactor1 - 1) * (1 + math.sin(2 * math.pi * (t[i] - tStartPeak) / peakWidth - math.pi / 2)) / 2
                     + c * d * (peakFactor2 - 1 + (peakFactor1 - peakFactor2) * (1 + math.sin(2 * math.pi * (t[i] - tStartPeak) / peakWidth - math.pi / 2)) / 2)
                     + e * (peakFactor2 - 1))

    return bumpf

with open("Network.json", "r") as file:
    Network = json.load(file)
file.close()

tStart = 1000
tStop = 6000
step = 20

time_temp = list(range(tStart, tStop + step, step))

q0 = 1.2
q1 = 0.1
q2 = 1.2
fact1 = q1/q0
fact2 = q2/q0

data_temp = bumpfct(time_temp, tStart, tStop, fact1, fact2)
data_temp = [element * q0 for element in data_temp]

time_temp.insert(0, 0)
time_temp.append(tStop + step)
data_temp.insert(0, q0)
data_temp.append(q2)

network_temp = []
for i in range(len(time_temp)):
    network_temp.append({"Time": time_temp[i], "Data": data_temp[i]})

Network["MACRONODES"][2]["Capacity"] = network_temp

with open("Network.json", "w") as file:
    json.dump(Network, file, indent = 4)
file.close()
