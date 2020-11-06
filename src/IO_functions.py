import json
from main_objects import RouteSection


def verify_flow_demand_input(flow, list_routes_id):
    # Verify origin and destination nodes exist
    if flow.OriginMacroNode is not None and flow.DestMacroNode is not None:
        verify = True
        for k in range(len(flow.RouteAssignments["Data"])):
            list_data_routes_id = []

            for data in flow.RouteAssignments["Data"][k]:
                if data["ID"] in list_routes_id and data["ID"] not in list_data_routes_id:
                    list_data_routes_id.append(data["ID"])
                else:
                    verify = False

        if verify:
            return True
        else:
            print("Route is unknown or already used, this demand won't be added to the list of demands")
            return False
    else:
        print("Origin or destination node is incorrect, this demand won't be added to the list of demands.")
        return False


def verify_discrete_demand_input(trip, list_trip_id):
    # Verify route id is unique
    if trip.TripID not in list_trip_id:
        # Verify origin and destination nodes exist
        if trip.OriginMacroNode is not None and trip.DestMacroNode is not None:
            # Verify route exists
            if trip.Route is not None:
                list_trip_id.append(trip.TripID)
                return True
            else:
                print("Route is incorrect, this trip won't be added to the list of trips.")
                return False
        else:
            print("Origin or destination node is incorrect, this trip won't be added to the list of trips.")
            return False
    else:
        print("Trip ID already used, this trip won't be added to the list of trips.")
        return False


def init_variables(reservoirs, routes, macronodes):
    # --- Init Res --- #
    # Loop on all reservoirs
    for res in reservoirs:
        # Loop on all macronodes
        for mn in macronodes:
            # Init MacroNodesID & AdjacentResID
            if type(mn.ResID) == str:
                mn.ResID = [mn.ResID]

            if res in mn.ResID:
                res.MacroNodes.append(mn)

                if len(mn.ResID) == 2:
                    if mn.ResID[0] != res:
                        res.AdjacentResID.append(mn.ResID[0])
                    else:
                        res.AdjacentResID.append(mn.ResID[1])
                else:
                    res.AdjacentResID.append(None)

    # --- Init RouteSection --- #
    for route in routes:
        previous_route_section = 0
        ind = 0
        
        for reservoir in route.CrossedReservoirs:
            entry_node = route.NodePath[ind]
            exit_node = route.NodePath[ind+1]

            if entry_node is None:
                print(route.ID)
                print(reservoir.ID)
            
            rs = RouteSection.RouteSection(route, reservoir, entry_node, exit_node, route.TripLengths[ind])
            rs.PreviousRouteSection = previous_route_section
            reservoir.RouteSections.append(rs)
            
            route.RouteSections.append(rs)
            
            if entry_node.Type == 'externalentry':
                reservoir.NumberOfExtRouteSection += reservoir.NumberOfExtRouteSection
                
            previous_route_section = rs
            ind = ind + 1

    # --- Init Routes --- #
    # Loop on all routes
    for route in routes:
        
        temp_tt = 0
        ind = 0
        for reservoir in route.CrossedReservoirs:
            temp_tt += route.TripLengths[ind] // reservoir.get_MFD_setting('FreeflowSpeed', route.Mode)
            ind = ind+1
            
        route.TotalTime = temp_TT
        route.FreeFlowTravelTime = temp_TT
        route.OldTT = temp_TT
        
def save_output(outputfile, simulation, reservoirs, routes, vehicle=None):
    # --- SIMULATION ---#
    if vehicle is None:
        vehicle = []
    simulation_out = [{"Date": simulation.Date, "Version": simulation.Version}]

    # --- RESERVOIR ---#
    reservoirs_out = []
    for i in range(len(Reservoirs)):
        
        reservoir_data = []
        
        routes_data = []
        for j in range(len(Reservoirs[i].RouteSections)):
            routes_data.append({"RouteID":Reservoirs[i].RouteSections[j].Route.ID, "Data":[]})

            for k in range(len(Reservoirs[i].RouteSections[j].Data)):
                routes_data[j]["Data"].append({"Time":Reservoirs[i].RouteSections[j].Data[k]["Time"], "Acc":Reservoirs[i].RouteSections[j].Data[k]["Acc"], "AccCircu":Reservoirs[i].RouteSections[j].Data[k]["AccCircu"],
                                               "AccQueue":Reservoirs[i].RouteSections[j].Data[k]["AccQueue"], "Inflow":Reservoirs[i].RouteSections[j].Data[k]["Inflow"], "Outflow":Reservoirs[i].RouteSections[j].Data[k]["Outflow"],
                                               "OutflowDemand":Reservoirs[i].RouteSections[j].Data[k]["OutflowDemand"], "Nin":Reservoirs[i].RouteSections[j].Data[k]["Nin"], "Nout":Reservoirs[i].RouteSections[j].Data[k]["Nout"],
                                               "NoutCircu":Reservoirs[i].RouteSections[j].Data[k]["NoutCircu"]})        
        
        reservoirs_out.append({"ID": Reservoirs[i].ID, "ReservoirData": reservoir_data, "DataPerRoute": routes_data})

        reservoirs_out.append({"ID": res.ID, "ReservoirData": reservoir_data, "DataPerRoute": routes_data})

    # --- ROUTES --- #
    routes_out = []
    for i in range(len(routes)):
        data = []
        # TODO
        
        routes_out.append({"ID": routes[i].ID, "Data": data, "NVehicles": routes[i].NVehicles})

    if vehicle is not None:
        # --- VEHICLE --- #
        vehicle_out = []
        for veh in vehicle:
            data = []

            vehicle_out.append({"ID": veh.ID, "Mode": veh.Mode, "RouteID": veh.RouteID,
                                "CreationTimes": veh.CreationTime, "Data": data})

        output = {"SIMULATION": simulation_out, "RESERVOIRS": reservoirs_out, "ROUTES": routes_out,
                  "VEHICLES": vehicle_out}

    else:
        output = {"SIMULATION":simulation_out, "RESERVOIRS":reservoirs_out, "ROUTES":routes_out}

    with open(outputfile, "w") as of:
        json.dump(output, of, indent = 4)
