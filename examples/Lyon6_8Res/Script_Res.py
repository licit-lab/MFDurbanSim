import json

with open("Network.json", "r") as file:
    Network = json.load(file)
file.close()

## RESERVOIRS
with open("ResStruct_Matlab.json", "r") as file:
    ReservoirMatlab = json.load(file)
file.close()

with open("MFDStruct_Matlab.json", "r") as file:
    MFDMatlab = json.load(file)
file.close()
    
numRes = len(ReservoirMatlab)
numMFD = len(MFDMatlab)

Network["RESERVOIRS"] = []
strRes_temp = {}

if numRes == numMFD:
    for i in range(numRes):
        strBorderPoints = []

        for j in range(len(ReservoirMatlab[i]["BorderPoints"][0])):
            strBorderPoints.append({"x": ReservoirMatlab[i]["BorderPoints"][0][j], "y": ReservoirMatlab[i]["BorderPoints"][1][j]})

        strRes_temp = {"ID": "Res" + str(i+1),
                       "FreeflowSpeed": [{"mode": "VL", "value": MFDMatlab[i]["u"]}],
                       "MaxProd": [{"mode": "VL", "value": MFDMatlab[i]["Pc"]}],
                       "MaxAcc": [{"mode": "VL", "value": MFDMatlab[i]["njam"]}],
                       "CritAcc": [{"mode": "VL", "value": MFDMatlab[i]["nc"]}],
                       "Centroid": [{"x": ReservoirMatlab[i]["Centroid"][0], "y": ReservoirMatlab[i]["Centroid"][1]}],
                       "BorderPoints": strBorderPoints}

        Network["RESERVOIRS"].append(strRes_temp)
else:
    print("Number of Reservoirs different than number of MFD points")
    
## MACRONODES
with open("NodeStruct_Matlab.json", "r") as file:
    NodeMatlab = json.load(file)
file.close()

numNodes = len(NodeMatlab)

Network["MACRONODES"] = []
strNode_temp = {}
for i in range(numNodes):
    strType = ""
    if NodeMatlab[i]["Type"] == 1:
        strType = "origin"
    elif NodeMatlab[i]["Type"] == 2:
        strType =  "destination"
    elif NodeMatlab[i]["Type"] == 3:
        strType = "externalentry"
    elif NodeMatlab[i]["Type"] == 4:
        strTpe = "externalexit"
    elif NodeMatlab[i]["Type"] == 5:
        strType = "border"
    else:
        strType = "origin"
        
    strNode_temp = {"ID": NodeMatlab[i]["ID"],
                    "Type": strType,
                    "ResID": "Res" + str(NodeMatlab[i]["ResID"]),
                    "Capacity": [{"Time": 0, "Data": 0}],
                    "Coord": [{"x": NodeMatlab[i]["Coord"][0], "y": NodeMatlab[i]["Coord"][1]}]}
                    
    Network["MACRONODES"].append(strNode_temp)

with open("Network.json", "w") as file:
    json.dump(Network, file, indent = 4)
file.close()
