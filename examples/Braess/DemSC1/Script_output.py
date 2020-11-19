import json
from datetime import datetime
import random

with open("Network.json", "r") as file:
    Network = json.load(file)

with open("Configuration.json", "r") as file:
    Configuration = json.load(file)

with open("Demand.json", "r") as file:
    Demand = json.load(file)

numRes = len(Network["RESERVOIRS"])
numRoutes = len(Network["ROUTES"])
numNodes = len(Network["MACRONODES"])

timeStep = Configuration["SIMULATION"][0]["TimeStep"]
timeStop = Configuration["SIMULATION"][0]["Duration"]

# -- SIMULATION -- #
simulation = {"Date": datetime.now().isocalendar(), "Version": "1.1"}

# -- RESERVOIRS --#
reservoirs = []

for res in Network["RESERVOIRS"]:
    reservoir_data = []

    for t in range(0, timeStop + timeStep, timeStep):
        reservoir_data.append({"Time": t, "MeanSpeed": random.randrange(0, 50),
                               "AvgTripLength": random.randrange(0, 1000), "Acc": random.randrange(0, 100),
                               "Inflow": random.randint(0, 50), "Outflow": random.randint(0, 50),
                               "Nin": random.randint(0, 500), "Nout": random.randint(0, 500)})

    data_per_route = []
    for route in Network["ROUTES"]:
        data = []
        for res_path in range(len(route["ResPath"])):
            if route["ResPath"][res_path]["ID"] == res["ID"]:
                for t in range(0, timeStop + timeStep, timeStep):
                    data.append({"Time": t, "Acc": random.randrange(0, 50), "AccCircu": random.randrange(0, 50),
                                 "AccQueue": random.randrange(0, 50), "Inflow": random.randint(0, 25),
                                 "Outflow": random.randint(0, 25), "OutflowCircu": random.randint(0, 25),
                                 "Nin": random.randint(0, 250), "Nout": random.randint(0, 250),
                                 "NoutCircu": random.randint(0, 250)})

                data_per_route.append({"IDRoute": route["ID"], "Data": data})

    reservoirs.append({"ID": res["ID"], "ReservoirData": reservoir_data,
                       "DataPerRoute": data_per_route})

# -- ROUTES --#
routes = []

for r in range(numRoutes):
    route_data = []
    for t in range(timeStep, timeStop + timeStep, timeStep):
        route_data.append({"Time": t, "TravelTime": random.randint(0, 1000), "Demand": random.randrange(0, 10)})
    routes.append({"ID": Network["ROUTES"][r]["ID"], "Data": route_data, "NVehicules": random.randint(0, 1000)})


with open("Output.json", "w") as fichier:
    json.dump({"SIMULATION": [simulation], "RESERVOIRS":reservoirs, "ROUTES":[routes]}, fichier, indent = 4)
