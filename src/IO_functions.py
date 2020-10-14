import json
import pandas
from main_objects import RouteSection, MacroNode

def Init(Res, Routes, MacroNodes):

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

    #Init RouteSection
    for route in Routes:            
        previousroutesection=0
        ind = 0
        
        for reservoir in route.CrossedReservoirs:
            
            EntryNode = route.NodePath[ind]
            ExitNode = route.NodePath[ind+1]
            
            rs = RouteSection.RouteSection(route, reservoir, EntryNode, ExitNode, route.TripLengths[ind])
            rs.PreviousRouteSection = previousroutesection
            reservoir.RouteSections.append(rs)
            
            route.RouteSections.append(rs)
            
            if EntryNode.Type=='externalentry':
                reservoir.NumberOfExtRouteSection=reservoir.NumberOfExtRouteSection+1
                
            previousroutesection=rs
            ind = ind+1

    #Loop on all routes
    for route in Routes:
        
        temp_TT = 0
        ind = 0
        for reservoir in route.CrossedReservoirs:
            temp_TT += route.TripLengths[ind] // reservoir.FreeflowSpeed[0]['value'] # multimodality management to do
            ind = ind+1
            
        route.TotalTime = temp_TT
        route.FreeFlowTravelTime = temp_TT
        route.OldTT = temp_TT
        
def SaveOutput(Simulation, Reservoirs, Routes, Vehicle = []):
    output = {}

    ##SIMULATION##
    simulation_out = [{"Date":Simulation.Date, "Version":Simulation.Version}]

    ##RESERVOIR##
    reservoirs_out = []
    for i in range(len(Reservoirs)):
        reservoir_data = []
        routes_data = []
        for j in range(len(Reservoirs[i].RouteSections)):
            routes_data.append({"RouteID":Reservoirs[i].RouteSections[j].RouteID, "Data":[]})

            for k in range(len(Reservoirs[i].RouteSections[j].Data)):
                routes_data[j]["Data"].append({"Time":Reservoirs[i].RouteSections[j].Data[k]["Time"], "Acc":Reservoirs[i].RouteSections[j].Data[k]["Acc"], "AccCircu":Reservoirs[i].RouteSections[j].Data[k]["AccCircu"],
                                               "AccQueue":Reservoirs[i].RouteSections[j].Data[k]["AccQueue"], "Inflow":Reservoirs[i].RouteSections[j].Data[k]["Inflow"], "Outflow":Reservoirs[i].RouteSections[j].Data[k]["Outflow"],
                                               "OutflowDemand":Reservoirs[i].RouteSections[j].Data[k]["OutflowDemand"], "Nin":Reservoirs[i].RouteSections[j].Data[k]["Nin"], "Nout":Reservoirs[i].RouteSections[j].Data[k]["Nout"],
                                               "NoutCircu":Reservoirs[i].RouteSections[j].Data[k]["NoutCircu"]})        
        
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












        
