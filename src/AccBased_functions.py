def Compute_Res(Reservoirs, Routes):

    for i in range(len(Reservoirs)):
        Reservoirs[i].Acc.append({"Time":0, "Acc":0})
        Reservoirs[i].MeanSpeed.append({"Time":0, "MeanSpeed":Reservoirs[i].FreeflowSpeed})

        #for j in range(len(Routes)):
            #for k in range(len(Routes[j].ResPath)):
                #if Reservoirs[i].ID in Routes[j].ResPath[k]["ID"]:
                    #Reservoirs[i].AccPerRoute.append({"Time":0, "Data":{"RouteID":Routes[j].ID, "Acc":0}})
                    #Reservoirs[i].AccCircuPerRoute.append({"Time":0, "Data":{"RouteID":Routes[j].ID, "AccCircu":0}})
                    #Reservoirs[i].AccQueuePerRoute.append({"Time":0, "Data":{"RouteID":Routes[j].ID, "AccQueue":0}})
                    #Reservoirs[i].NinPerRoute.append({"Time":0, "Data":{"RouteID":Routes[j].ID, "Nin":0}})
                    #Reservoirs[i].NoutPerRoute.append({"Time":0, "Data":{"RouteID":Routes[j].ID, "Nout":0}})
                    #Reservoirs[i].NoutCircuPerRoute.append({"Time":0, "Data":{"RouteID":Routes[j].ID, "NoutCircu":0}})
