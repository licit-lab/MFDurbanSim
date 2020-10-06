import json
from main_objects import RouteSection

def Init(Res, Routes, MacroNodes, Demands):

    numRes = len(Res)
    numRoutes = len(Routes)
    numMN = len(MacroNodes)
    
    ### Init Res ###
    
    #Loop on all reservoirs
    """   for i in range(numRes):
        #Loop on all macronodes
        #Init MacroNodesID & AdjacentResID
        for j in range(numMN):
            if Res[i].ID in MacroNodes[j].ResID:
                Res[i].MacroNodesID.append({"ID":MacroNodes[j].ID, "Type":MacroNodes[j].Type})

                if len(MacroNodes[j].ResID) == 2:
                    if MacroNodes[j].ResID[0] != Res[i].ID:
                        Res[i].AdjacentResID.append(MacroNodes[j].ResID[0])
                    else:
                        Res[i].AdjacentResID.append(MacroNodes[j].ResID[1])"""

    for res in Res:
        for mn in MacroNodes:
            if res.ID in mn.ResID:
                res.MacroNodesID.append({"ID": mn.ID, "Type": mn.Type})

                if len(mn.ResID) == 2:
                    if mn.ResID != res.ID:
                        res.AdjacentResID.append(mn.ResID[0])
                    else:
                        res.AdjacentResID.append(mn.ResID[1])

        #Loop on all routes
        #Init RouteSection
        for route in Routes:
            for res_path in route.ResPath:
                if res.ID in res_path["ID"]:
                    EntryNode = {"ID": route.NodeOriginID, "Type": ""}
                    ExitNode = {"ID": route.NodeDestinationID, "Type": ""}
                    for mn in MacroNodes:
                        if EntryNode["ID"] in mn.ResID:
                            EntryNode["Type"] = mn.Type
                        if ExitNode["ID"] in mn.ResID:
                            ExitNode["Type"] = mn.Type

                    res.RouteSection.append(RouteSection.RouteSection(route.ID, EntryNode, ExitNode, res_path["TripLength"]))

    ### Init Routes ###

    #Loop on all routes
    for i in range(numRoutes):
        temp_TT = 0
        
        #Loop on all reservoirs on the path
        for j in range(len(Routes[i].ResPath)):
            for k in range(numRes):
                if Res[k].ID in Routes[i].ResPath[j]["ID"]:
                    if Routes[i].Mode == Res[k].FreeflowSpeed[0]["mode"]:
                        temp_TT += Routes[i].ResPath[j]["TripLength"] // Res[k].FreeflowSpeed[0]["value"]
                    elif Routes[i].Mode == Res[k].FreeflowSpeed[1]["mode"]:
                        temp_TT += Routes[i].ResPath[j]["TripLength"] // Res[k].FreeflowSpeed[1]["value"]

        Routes[i].TotalTime = temp_TT
        Routes[i].FreeFlowTravelTime = temp_TT
        Routes[i].OldTT = temp_TT
        
def SaveOutput(Simulation, Reservoirs, Routes, Vehicle = []):
    output = {}

    ##SIMULATION##
    simulation_out = [{"Date":Simulation.Date, "Version":Simulation.Version}]

    ##RESERVOIR##
    reservoirs_out = []
    for i in range(len(Reservoirs)):
        reservoir_data = []
        routes_data = []
        for j in range(len(Reservoirs[i].RouteSection)):
            routes_data.append({"RouteID":Reservoirs[i].RouteSection[j].RouteID, "Data":[]})

            for k in range(len(Reservoirs[i].RouteSection[j].Data)):
                routes_data[j]["Data"].append({"Time":Reservoirs[i].RouteSection[j].Data[k]["Time"], "Acc":Reservoirs[i].RouteSection[j].Data[k]["Acc"], "AccCircu":Reservoirs[i].RouteSection[j].Data[k]["AccCircu"],
                                               "AccQueue":Reservoirs[i].RouteSection[j].Data[k]["AccQueue"], "Inflow":Reservoirs[i].RouteSection[j].Data[k]["Inflow"], "Outflow":Reservoirs[i].RouteSection[j].Data[k]["Outflow"],
                                               "OutflowCircu":Reservoirs[i].RouteSection[j].Data[k]["OutflowCircu"], "Nin":Reservoirs[i].RouteSection[j].Data[k]["Nin"], "Nout":Reservoirs[i].RouteSection[j].Data[k]["Nout"],
                                               "NoutCircu":Reservoirs[i].RouteSection[j].Data[k]["NoutCircu"]})        
        
        reservoirs_out.append({"ID":Reservoirs[i].ID, "ReservoirData":reservoir_data, "DataPerRoute":routes_data})

    ##ROUTES##
    routes_out = []
    for i in range(len(Routes)):
        data = []
        #TODO
        
        routes_out.append({"ID":Routes[i].ID, "Data":data, "NVehicles":Routes[i].NVehicles})

    if len(Vehicle) > 0:
        ##VEHICLE##
        vehicle_out = []
        for i in range(len(Vehicle)):
            data = []

            vehicle_out.append({"ID":Vehicle[i].ID, "Mode":Vehicle[i].Mode, "RouteID":Vehicle[i].RouteID, "CreationTimes":Vehicle[i].CreationTime, "Data":data})

        output = {"SIMULATION":simulation_out, "RESERVOIRS":reservoirs_out, "ROUTES":routes_out, "VEHICLES":vehicle_out}

    else:
        output = {"SIMULATION":simulation_out, "RESERVOIRS":reservoirs_out, "ROUTES":routes_out}

    with open("Output.json", "w") as fichier:
        json.dump(output)

