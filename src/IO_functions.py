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
        #Init TripLengthPerRoute
        for j in range(numRoutes):
            for k in range(len(Routes[j].ResPath)):
                if Res[i].ID in Routes[j].ResPath[k]["ID"]:
                    Res[i].TripLengthPerRoute.append({"RouteID":Routes[j].ID, "TripLength":Routes[j].ResPath[k]["TripLength"]})

                    #Init RoutesNodeID
                    Res[i].RoutesNodeID.append({"RouteID":Routes[j].ID, "EntryNodeID":Routes[j].NodeOriginID, "ExitNodeID":Routes[j].NodeDestinationID})

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
        
                
