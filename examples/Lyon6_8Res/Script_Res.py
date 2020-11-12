import json

# RESERVOIRS
with open("ResStruct_Matlab.json", "r") as file:
    ReservoirMatlab = json.load(file)

with open("MFDStruct_Matlab.json", "r") as file:
    MFDMatlab = json.load(file)
    
numRes = len(ReservoirMatlab)
numMFD = len(MFDMatlab)

Network = {}
strRes_temp = {}

Network["RESERVOIRS"] = []
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
    
# MACRONODES
with open("NodeStruct_Matlab.json", "r") as file:
    NodeMatlab = json.load(file)
file.close()

numNodes = len(NodeMatlab)

Network["MACRONODES"] = []
strNode_temp = {}
for mn in NodeMatlab:
    strType = ""

    if mn["Type"] == 1:
        strType = "origin"
        res_id = f"Res{str(mn['ResID'])}"
    elif mn["Type"] == 2:
        strType = "destination"
        res_id = f"Res{str(mn['ResID'])}"
    elif mn["Type"] == 0:
        strType = "border"

        if type(mn['ResID']) is list:
            res_id = []
            for mn_res_id in mn['ResID']:
                res_id.append(f"Res{str(mn_res_id)}")
        else:
            res_id = f"Res{str(mn['ResID'])}"
    else:
        print(f"Type {mn['Type']} unknown")
        continue
        
    strNode_temp = {"ID": mn["ID"],
                    "Type": strType,
                    "ResID": res_id,
                    "Capacity": [{"Time": 0, "Data": 0}],
                    "Coord": [{"x": mn["Coord"][0], "y": mn["Coord"][1]}]}
                    
    Network["MACRONODES"].append(strNode_temp)

with open("Network.json", "w") as file:
    json.dump(Network, file, indent=4)

