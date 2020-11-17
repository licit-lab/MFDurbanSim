import json
from main_objects import RouteSection

def verify_reservoir_input(reservoir, list_res_id):
    # Verify reservoir id is unique
    if reservoir.ID not in list_res_id:
        # Verify Critical accumulation < Maximum accumulation
        i = 0
        for mode in range(len(reservoir.MFDsetting)):
            if reservoir.MFDsetting[mode]["CritAcc"] < reservoir.MFDsetting[mode]["MaxAcc"]:
                i = i + 1

        if i == len(reservoir.MFDsetting):
            list_res_id.append(reservoir.ID)
            return True
        else:
            print("MaxAcc <= CritAcc, this reservoir won't be added to the list of reservoirs.")
            return False
    else:
        print("ResID already used, this reservoir won't be added to the list of reservoirs.")
        return False


def verify_nodes_input(macronode, list_mn_id, list_res_id):
    # Verify macro node id is unique
    if macronode.ID not in list_mn_id:
        # Verify macro node type is well-defined
        if macronode.Type is not None:
            # Verify reservoir is well-defined
            i = 0
            for res_id in macronode.ResID:
                if res_id.ID in list_res_id:
                    i = i + 1

            if i == len(macronode.ResID):
                list_mn_id.append(macronode.ID)
                return True
            else:
                print("Reservoir doesn't exist, this macro node won't be added to the list of macro nodes.")
                return False
        else:
            print("Macro node type unknown, this macro node won't be added to the list of macro nodes")
            return False
    else:
        print("Macro node ID already used, this macro node won't be added to the list of macro nodes.")
        return False


def verify_routes_input(route, list_routes_id):
    # Verify route id is unique
    if route.ID not in list_routes_id:
        # Verify reservoir is well-defined
        i = 0
        for res in route.CrossedReservoirs:
            if res is not None:
                i = i + 1

        if i == len(route.CrossedReservoirs):
            # Verify macro node is well-defined
            j = 0
            for node in route.NodePath:
                if node is not None:
                    j = j + 1

            if j == len(route.NodePath):
                # Verify nb of nodes = nb of reservoirs + 1
                if len(route.NodePath) == len(route.CrossedReservoirs) + 1:
                    list_routes_id.append(route.ID)
                    return True
                else:
                    print("Number of nodes isn't equal to number of reservoirs + 1, this route won't be added "
                          "to the list of routes.")
                    return False
            else:
                print("Node path incorrect, this route won't be added to the list of routes.")
                return False
        else:
            print("Reservoir path incorrect, this route won't be added to the list of routes.")
            return False
    else:
        print("Route ID already used, this route won't be added to the list of routes.")
        return False


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
            
        route.TotalTime = temp_tt
        route.FreeFlowTravelTime = temp_tt
        route.OldTT = temp_tt


def save_output(outputfile, simulation, reservoirs, routes, vehicle=None):
    # --- SIMULATION ---#
    if vehicle is None:
        vehicle = []
    simulation_out = [{"Date": simulation.Date, "Version": simulation.Version}]

    # --- RESERVOIR ---#
    reservoirs_out = []
    for res in reservoirs:
        
        reservoir_data = []
        #reservoir_data.append({"Data": []})
        for data in res.Data:
            reservoir_data.append({"Time": data["Time"], "Acc": data["Acc"], "MeanSpeed": data["MeanSpeed"]})
        
        routes_data = []
        j = 0
        for rs in res.RouteSections:
            routes_data.append({"RouteID": rs.Route.ID, "Data": []})

            for data in rs.Data:
                routes_data[j]["Data"].append({"Time": data["Time"], "Acc": data["Acc"], "AccCircu": data["AccCircu"],
                                               "AccQueue": data["AccQueue"], "Inflow": data["Inflow"],
                                               "Outflow": data["Outflow"], "OutflowDemand": data["OutflowDemand"],
                                               "Nin": data["Nin"], "Nout": data["Nout"],
                                               "NoutCircu": data["NoutCircu"]})

            j += 1

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
