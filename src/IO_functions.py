import json
import pandas
from main_objects import RouteSection, MacroNode

def Init(Res, Routes, MacroNodes, GlobalDemand):

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
                
                Res[i].MacroNodes.append(MacroNodes[j])

                if len(MacroNodes[j].ResID) == 2:
                    if MacroNodes[j].ResID[0] != Res[i].ID:
                        Res[i].AdjacentResID.append(MacroNodes[j].ResID[0])
                    else:
                        Res[i].AdjacentResID.append(MacroNodes[j].ResID[1])       

        #Loop on all routes
        #Init RouteSection
        for j in range(numRoutes):            
            for k in range(len(Routes[j].CrossedReservoirs)):                
                if Res[i].ID in Routes[j].CrossedReservoirs[k]["ID"]:                    
                    EntryNode = Routes[j].OriginMacroNode
                    ExitNode = Routes[j].DestMacroNode
                    
                    
                    # ???
                    # for l in range(numMN):
                    #     if EntryNode["ID"] == MacroNodes[l].ID:
                    #         EntryNode["Type"] = MacroNodes[l].Type
                    #     if ExitNode["ID"] == MacroNodes[l].ID:
                    #         ExitNode["Type"] = MacroNodes[l].Type

                    Res[i].RouteSection.append(RouteSection.RouteSection(Routes[j], Routes[j].CrossedReservoirs[k], EntryNode, ExitNode, Routes[j].CrossedReservoirs[k]["TripLength"]))
                    
                    if EntryNode.Type=='externalentry':
                        Res[i].NumberOfExtRouteSection=Res[i].NumberOfExtRouteSection+1

    ### Init Routes ###

    #Loop on all routes
    for i in range(numRoutes):
        temp_TT = 0
        
        #Loop on all reservoirs on the path
        for j in range(len(Routes[i].CrossedReservoirs)):
            for k in range(numRes):
                if Res[k].ID in Routes[i].CrossedReservoirs[j]["ID"]:
                    if Routes[i].Mode == Res[k].FreeflowSpeed[0]["mode"]:
                        temp_TT += Routes[i].CrossedReservoirs[j]["TripLength"] // Res[k].FreeflowSpeed[0]["value"]
                    elif Routes[i].Mode == Res[k].FreeflowSpeed[1]["mode"]:
                        temp_TT += Routes[i].CrossedReservoirs[j]["TripLength"] // Res[k].FreeflowSpeed[1]["value"]

        Routes[i].TotalTime = temp_TT
        Routes[i].FreeFlowTravelTime = temp_TT
        Routes[i].OldTT = temp_TT
        
    # Demand: useless?? à récupérer directement à partir structure demand ???
    # TODO: discrete demand
    # Values=pandas.DataFrame.from_dict(Demands[0].Demands)
    # Values.set_index('Time')
        
    # RouteAssignment=pandas.DataFrame.from_dict(Demands[0].RouteAssignments)
    # RouteAssignment.set_index('Time')
    
    # newTime=pandas.concat([Values['Time'],RouteAssignment['Time']]).drop_duplicates().reset_index(drop=True)
    
    # TODO
        
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












        
