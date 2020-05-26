import json
from main_objects import RouteSection

def Init(Res, Routes, MacroNodes, Demands):

    numRes = len(Res)
    numRoutes = len(Routes)
    numMN = len(MacroNodes)
    
    ### Init Res ###
    
    #Loop on all reservoirs
    for i in range(numRes):
        #Loop on all macronodes
        #Init MacroNodesID & AdjacentResID
        for j in range(numMN):
            if Res[i].ID in MacroNodes[j].ResID:
                Res[i].MacroNodesID.append({"ID":MacroNodes[j].ID, "Type":MacroNodes[j].Type})

                if len(MacroNodes[j].ResID) == 2:
                    if MacroNodes[j].ResID[0] != Res[i].ID:
                        Res[i].AdjacentResID.append(MacroNodes[j].ResID[0])
                    else:
                        Res[i].AdjacentResID.append(MacroNodes[j].ResID[1])       

        #Loop on all routes
        #Init RouteSection
        for j in range(numRoutes):            
            for k in range(len(Routes[j].ResPath)):                
                if Res[i].ID in Routes[j].ResPath[k]["ID"]:                    
                    EntryNode = {"ID":Routes[j].NodeOriginID, "Type":""}
                    ExitNode = {"ID":Routes[j].NodeDestinationID, "Type":""}
                    for l in range(numMN):
                        if EntryNode["ID"] in MacroNodes[l].ResID:
                            EntryNode["Type"] = MacroNodes[l].Type
                        if ExitNode["ID"] in MacroNodes[l].ResID:
                            ExitNode["Type"] = MacroNodes[l].Type

                    Res[i].RouteSection.append(RouteSection.RouteSection(Routes[j].ID, EntryNode, ExitNode, Routes[j].ResPath[k]["TripLength"]))

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
    simulation_out = [{"Date":Simulation.Date, "Version":Simulation.Version}]

    reservoirs_out = []
    for i in range(len(Reservoirs)):
        reservoir_data = []
        routes_data = []

        
        
        reservoir_out = append({"ID":Reservoir[i].ID, "ReservoirData":reservoir_data, "DataPerRoute":routes_data})

    routes_out = []
    for i in range(len(Routes)):
        data = []

        routes_out = append({"ID":Routes[i].ID, "Data":data, "NVehicles":Routes[i].NVehicles})

    if len(Vehicle) > 0:
        vehicle_out = []
        for i in range(len(Vehicle)):
            data = []

            vehicle_out.append({"ID":Vehicle[i].ID, "Mode":Vehicle[i].Mode, "RouteID":Vehicle[i].RouteID, "CreationTimes":Vehicle[i].CreationTime, "Data":data})

        output = {"SIMULATION":simulation_out, "RESERVOIRS":reservoirs_out, "ROUTES":routes_out, "VEHICLES":vehicles_out}

    else:
        output = {"SIMULATION":simulation_out, "RESERVOIRS":reservoirs_out, "ROUTES":routes_out}

    with open("Output.json", "w") as fichier:
        json.dump(output)












        
