import json

#Open file
with open("Network.json", "r") as file:
    Network = json.load(file)
file.close()

Reservoirs = Network["RESERVOIRS"]
numRes = len(Reservoirs)
ResSpac = 2
Network["MACRONODES"] = []
MNstr = {}

mn = 1

nRows = 3
nCols = 3
rowID = 0
colID = 0
tmp_dir = 1

for i in range(numRes):
    if i % nRows == 0:
        rowID += 1
        
    colID = colID % nCols + 1

    print(rowID)
    print(colID)
        
    MNstr = {"ID": "MacroNode" + str(mn),
             "Type": "origin",
             "ResID": [Reservoirs[i]["ID"]],
             "Coord": [{"x": Reservoirs[i]["Centroid"][0]["x"] + 0, "y": Reservoirs[i]["Centroid"][0]["y"] + 0.4 * ResSpac / 2}],
             "Capacity": [{"Time": 0, "Data": 100}]}
    Network["MACRONODES"].append(MNstr)
    mn += 1

    MNstr = {"ID": "MacroNode" + str(mn),
             "Type": "destination",
             "ResID": [Reservoirs[i]["ID"]],
             "Coord": [{"x": Reservoirs[i]["Centroid"][0]["x"] + 0, "y": Reservoirs[i]["Centroid"][0]["y"] - 0.4 * ResSpac / 2}],
             "Capacity": [{"Time": 0, "Data": 100}]}
    Network["MACRONODES"].append(MNstr)
    mn += 1

    if rowID == 1 or rowID == nRows:
        if rowID == 1:
            tmp_dir = 1
        elif rowID == nRows:
            tmp_dir = -1
            
        MNstr = {"ID": "MacroNode" + str(mn),
                 "Type": "externalentry",
                 "ResID": [Reservoirs[i]["ID"]],
                 "Coord": [{"x": Reservoirs[i]["Centroid"][0]["x"] - 0.2 * ResSpac / 2, "y": Reservoirs[i]["Centroid"][0]["y"] + tmp_dir * ResSpac / 2}],
                 "Capacity": [{"Time": 0, "Data": 100}]}
        Network["MACRONODES"].append(MNstr)
        mn += 1

        MNstr = {"ID": "MacroNode" + str(mn),
                 "Type": "externalexit",
                 "ResID": [Reservoirs[i]["ID"]],
                 "Coord": [{"x": Reservoirs[i]["Centroid"][0]["x"] + 0.2 * ResSpac / 2, "y": Reservoirs[i]["Centroid"][0]["y"] + tmp_dir * ResSpac / 2}],
                 "Capacity": [{"Time": 0, "Data": 100}]}
        Network["MACRONODES"].append(MNstr)
        mn += 1

    if colID == 1 or colID == nCols:
        if colID == 1:
            tmp_dir = -1
        elif colID == nCols:
            tmp_dir = 1
            
        MNstr = {"ID": "MacroNode" + str(mn),
                 "Type": "externalentry",
                 "ResID": [Reservoirs[i]["ID"]],
                 "Coord": [{"x": Reservoirs[i]["Centroid"][0]["x"] + tmp_dir * ResSpac / 2, "y": Reservoirs[i]["Centroid"][0]["y"] + 0.2 * ResSpac / 2}],
                 "Capacity": [{"Time": 0, "Data": 100}]}
        Network["MACRONODES"].append(MNstr)
        mn += 1

        MNstr = {"ID": "MacroNode" + str(mn),
                 "Type": "externalexit",
                 "ResID": [Reservoirs[i]["ID"]],
                 "Coord": [{"x": Reservoirs[i]["Centroid"][0]["x"] + tmp_dir * ResSpac / 2, "y": Reservoirs[i]["Centroid"][0]["y"] - 0.2 * ResSpac / 2}],
                 "Capacity": [{"Time": 0, "Data": 100}]}
        Network["MACRONODES"].append(MNstr)
        mn += 1

    
# Border nodes
#for i in range(numRes - 1):
    








with open("Network.json", "w") as file:
    json.dump(Network, file, indent = 4)
file.close()
