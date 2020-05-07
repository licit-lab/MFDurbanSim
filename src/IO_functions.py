def Init(Res, Routes, MacroNodes, Demands):

    ### Init Res ###
    
    #Loop on all reservoirs
    for i in range(len(Res)):
        #Loop on all macronodes
        for j in range(len(MacroNodes)):
            if Res[i].ID in MacroNodes[j].ResID:
                Res[i].MacroNodesID.append({"ID":MacroNodes[j].ID, "Type":MacroNodes[j].Type})

                if len(MacroNodes[j].ResID) == 2:
                    if MacroNodes[j].ResID[0] != Res[i].ID:
                        Res[i].AdjacentResID.append(MacroNodes[j].ResID[0])
                    else:
                        Res[i].AdjacentResID.append(MacroNodes[j].ResID[1])       

        #Loop on all routes            
        for j in range(len(Routes)):
            for k in range(len(Routes[j].ResPath)):
                if Res[i].ID in Routes[j].ResPath[k]["ID"]:
                    Res[i].TripLengthPerRoute.append({"RouteID":Routes[j].ID, "TripLength":Routes[j].ResPath[k]["TripLength"]})
            
#Res[i].RoutesID inutile cf TripLenghtPerRoute
#Res[i].RoutesPathIndex -> pas compris à quoi ça correspond
#Res[i].OriginRes -> pas compris à quoi ça correspond
#Res[i].DestinationRes -> pas compris à quoi ça correspond

    for i in range(len(Res)):
        for j in range(len(Res[i].MacroNodesID)):
            if Res[i].MacroNodesID[j]["Type"] == "origin":
                Res[i].OriNodesIndex.append(Res[i].MacroNodesID[j]["ID"])
            elif Res[i].MacroNodesID[j]["Type"] == "destination":
                Res[i].DestNodesIndex.append(Res[i].MacroNodesID[j]["ID"])
            elif Res[i].MacroNodesID[j]["Type"] == "externalentry":
                Res[i].EntryNodesIndex.append(Res[i].MacroNodesID[j]["ID"])
            elif Res[i].MacroNodesID[j]["Type"] == "externalexit":
                Res[i].ExitNodesIndex.append(Res[i].MacroNodesID[j]["ID"])
            elif Res[i].MacroNodesID[j]["Type"] == "border": #à vérifier
                Res[i].EntryNodesIndex.append(Res[i].MacroNodesID[j]["ID"])
                Res[i].ExitNodesIndex.append(Res[i].MacroNodesID[j]["ID"])



                
