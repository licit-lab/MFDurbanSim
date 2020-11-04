import json
from src.main_objects import RouteSection

def Init(Res, Routes, MacroNodes):

    num_res = len(Res)
    num_routes = len(Routes)
    num_mn = len(MacroNodes)

    ### Init Res ###
    
    # Loop on all reservoirs
    for res in Res:
        # Loop on all macronodes
        for mn in MacroNodes:
            # Init MacroNodesID & AdjacentResID
            if type(mn.ResID) == int:
                mn.ResID = [mn.ResID]

            if res.ID in mn.ResID:
                res.MacroNodes.append(mn)

                if len(mn.ResID) == 2:
                    if mn.ResID[0] != res.ID:
                        res.AdjacentResID.append(mn.ResID[0])
                    else:
                        res.AdjacentResID.append(mn.ResID[1])
                else:
                    res.AdjacentResID.append(None)

    #Init RouteSection
    for route in Routes:            
        previous_route_section = 0
        ind = 0
        
        for reservoir in route.CrossedReservoirs:
            EntryNode = route.NodePath[ind]
            ExitNode = route.NodePath[ind+1]

            if EntryNode is None:
                print(EntryNode)
                print(route.ID)
                print(reservoir.ID)
            
            rs = RouteSection.RouteSection(route, reservoir, EntryNode, ExitNode, route.TripLengths[ind])
            rs.PreviousRouteSection = previous_route_section
            reservoir.RouteSections.append(rs)
            
            route.RouteSections.append(rs)
            
            if EntryNode.Type == 'externalentry':
                reservoir.NumberOfExtRouteSection += reservoir.NumberOfExtRouteSection
                
            previous_route_section = rs
            ind = ind + 1

    #Loop on all routes
    for route in Routes:
        
        temp_TT = 0
        ind = 0
        for reservoir in route.CrossedReservoirs:
            temp_TT += route.TripLengths[ind] // reservoir.get_MFD_setting('FreeflowSpeed',route.Mode)
            ind = ind+1
            
        route.TotalTime = temp_TT
        route.FreeFlowTravelTime = temp_TT
        route.OldTT = temp_TT
        
def SaveOutput(Simulation, Reservoirs, Routes, Vehicle = []):
    output = {}

    ##SIMULATION##
    simulation_out = [{"Date": Simulation.Date, "Version": Simulation.Version}]

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
        
        reservoirs_out.append({"ID": Reservoirs[i].ID, "ReservoirData": reservoir_data, "DataPerRoute": routes_data})

    ##ROUTES##
    routes_out = []
    for i in range(len(Routes)):
        data = []
        #TODO
        
        routes_out.append({"ID": Routes[i].ID, "Data": data, "NVehicles": Routes[i].NVehicles})

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
        json.dump(output, fichier, indent = 4)












        
