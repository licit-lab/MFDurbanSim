from AccBased_functions import *
from main_objects import Demand, Vehicle

import math


# Compute effective inflows from demand flows with respective merge coefficients and flow capacity
def Merge(DemandFlows,MergeCoeffs,Capacity):
    
    # init
    Q = [0. for i in range(len(DemandFlows))]
    UnservedFlows = [1 for i in range(len(DemandFlows))]
    TotalServedInflow = 0
    alpha = 1
    
    for i in range(len(UnservedFlows)):
        if MergeCoeffs[i]==0 or DemandFlows[i]==0:
            UnservedFlows[i]=0
    
    while max(UnservedFlows) > 0:
        
        TmpUnservedFlows = [0 for i in range(len(DemandFlows))]
        TmpTotalServedInflow = 0
        TmpAlpha = 0       
        
        for i in range(len(UnservedFlows)):
            if UnservedFlows[i]==1:
                if DemandFlows[i] < MergeCoeffs[i]/alpha * (Capacity-TotalServedInflow):
                    # demand i is served
                    Q[i]=DemandFlows[i]
                    TmpUnservedFlows[i]=0
                    TmpTotalServedInflow+=Q[i]
                else:
                    # demand i is not served
                    Q[i]=MergeCoeffs[i]/alpha * (Capacity-TotalServedInflow)
                   
                    TmpUnservedFlows[i]=1
                    TmpAlpha+=MergeCoeffs[i]
                    
        UnservedFlows=TmpUnservedFlows
        alpha=TmpAlpha
        TotalServedInflow+=TmpTotalServedInflow
        
        if math.isclose(sum(Q), Capacity, rel_tol=1e-6):
            UnservedFlows = [0 for i in range(len(DemandFlows))]
        
    return Q

# Compute entry supply times with multiple incoming flows
def MergeTime(t_in_demands,trip_lengths, last_entries_times, mergecoeffs,capacity):
    
    # init
    t_in_supplies = [0. for i in range(len(t_in_demands))]
    UnservedFlows = [1 for i in range(len(t_in_demands))]
    
    while max(UnservedFlows) > 0:
        
        TmpUnservedFlows = [0 for i in range(len(DemandFlows))]
        TmpTotalServedInflow = 0
        alpha_u = 1        
        
        for i in range(len(UnservedFlows)):
            
            # Inflow supply for demand i
            Q_s_i = MergeCoeffs[i] / alpha_u * (capacity - TmpTotalServedInflow) / trip_lengths[i]
            
            # Entry supply times for demand i
            t_in_supplies[i] = last_entries_times[i] + (1./Q_s_i)
            
            # Effective flow for demand i
            Q_i = trip_lengths[i] * Q_s_i

            if UnservedFlows[i]==1:
                if t_in_demands[i] >= t_in_supplies[i]:
                    # demand i is served
                    UnservedFlows[i]=0
                    TmpTotalServedInflow+=Q_i
                else:
                    # demand i is not served
                    Q[i]=alpha/MergeCoeffs[i] * (Capacity-TotalServedInflow)
                    TmpUnservedFlows[i]=0
                    alpha_u= alpha_u+mergecoeffs[i]
        
        if math.isclose(sum(Q), Capacity, rel_tol=1e-6):
            UnservedFlows = [0 for i in range(len(t_in_demands))]
    
    return t_in_supplies
    
# Accumulation-based solver
def AccBased(Simulation, Reservoirs, Routes, MacroNodes, GlobalDemand):

    # Init variables
    indtime = -1
    init_time_step(0., Reservoirs, Routes)
    modes = Simulation.Modes

    # Time loop
    for t in range(0, Simulation.Duration, Simulation.TimeStep):

        indtime=indtime+1
        print("Time step :" , t)
        
        # First reservoir loop (mean speed, outflow demand, production supply and average trip length updates)
        for reservoir in Reservoirs:

            # Mean speed update

            reservoir.FlowData[indtime]['MeanSpeed']=reservoir.get_speed_from_accumulation(reservoir.FlowData[indtime]['Acc'])
          
            # Production update (TO DO for queue dyn model)
            reservoir.FlowData[indtime]['Production'] = reservoir.get_production_from_accumulation(reservoir.FlowData[indtime]['Acc'])
         
            # Outflow demand per route update 
            # TO DO for other models
            
            outflowdemand=dict()
            
            if Simulation.DivergeModel=='maxdem':
                
                for rs in reservoir.RouteSections:
                    mode=rs.Route.Mode
                    if reservoir.FlowData[indtime]['Acc'][mode]>0:
                        if reservoir.FlowData[indtime]['Acc'][mode] < reservoir.get_MFD_setting('CritAcc',mode) and reservoir.FlowData[indtime]['Acc'][mode]>0:
                            outflowdemand[mode] = (rs.FlowData[indtime]['Acc'][mode]/reservoir.FlowData[indtime]['Acc'][mode])*reservoir.FlowData[indtime]['Production'][mode]/rs.TripLength
                        else:
                            outflowdemand[mode] = (rs.FlowData[indtime]['Acc'][mode]/reservoir.FlowData[indtime]['Acc'][mode])*reservoir.get_MFD_setting('MaxProd',mode)/rs.TripLength
                    else:
                         outflowdemand[mode]=0.
                             
                    rs.FlowData[indtime]['OutflowDemand']= outflowdemand
                         
            elif Simulation.DivergeModel=='decrdem':
                
                for rs in reservoir.RouteSections:
                    mode=rs.Route.Mode
                    if reservoir.FlowData[indtime]['Acc'][mode]>0:
                        outflowdemand[mode] = (rs.FlowData[indtime]['Acc'][mode]/reservoir.FlowData[indtime]['Acc'][mode])*reservoir.FlowData[indtime]['Production'][mode]/rs.TripLength
                    else:
                        outflowdemand[mode]=0.
                            
                    rs.FlowData[indtime]['OutflowDemand']= outflowdemand
                         
            # Entry production supply update
            productionsupply=dict()
           
            tmp=dict.fromkeys(modes,0.)
            for rs in reservoir.RouteSections:
                mode=rs.Route.Mode
                #if rs.EntryNode.Type == 'origin' or rs.EntryNode.Type=='externalentry':
                if rs.EntryNode.Type == 'origin':
                    tmp[mode] = tmp[mode] + rs.TripLength * Demand.get_partial_demand(GlobalDemand, rs, t)
    
            for mode in modes:
                productionsupply[mode]=reservoir.get_entry_supply_from_accumulation(reservoir.FlowData[indtime]['Acc'],mode)-tmp[mode]
                
            reservoir.FlowData[indtime]['ProductionSupply']=productionsupply
                
            # Average trip length update
            avgtriplength = dict()
            tmp=dict.fromkeys(modes,0.)
            
            for rs in reservoir.RouteSections:
                mode=rs.Route.Mode
                if rs.EntryNode.Type == 'externalentry' or rs.EntryNode.Type == 'border':
                    tmp[mode]=tmp[mode]+rs.FlowData[indtime]['Acc'][mode]/rs.TripLength
                
            for mode in modes:
                if tmp[mode]>0:
                    avgtriplength[mode]=reservoir.FlowData[indtime]['Acc'][mode]/tmp[mode]
                else:
                    sumtriplength = 0
                    for rs in reservoir.RouteSections:
                        mode=rs.Route.Mode
                        if rs.EntryNode.Type=='externalentry' or rs.EntryNode.Type=='border':  
                            sumtriplength += rs.TripLength
                    if len(reservoir.RouteSections)>0:
                        avgtriplength[mode]=sumtriplength/len(reservoir.RouteSections)
                    else:
                        avgtriplength[mode]=0
                        
            reservoir.FlowData[indtime]['AvgTripLength']=avgtriplength
                    
        # Second reservoir loop (demand, inflow demand, merging coefficients, border inflow supply and reservoir inflow supply updates)
        for reservoir in Reservoirs:
            
            # Demand update
           
            for rs in reservoir.RouteSections:
                
                rsdemand = dict.fromkeys(modes,0.)
                if (rs.EntryNode.Type == 'origin' or rs.EntryNode.Type == 'externalentry'):
                    rsdemand[rs.Route.Mode] = Demand.get_partial_demand(GlobalDemand, rs, t)
                
                rs.FlowData[indtime]['Demand'] = rsdemand
            
            demand=dict.fromkeys(modes,0.)
            
            for rs in reservoir.RouteSections:
                mode=rs.Route.Mode
                if rs.EntryNode.Type == 'origin' or 'externalentry':
                    demand[mode] += rs.FlowData[indtime]['Demand'][mode]
                        
            reservoir.FlowData[indtime]['Demand']=demand   # to check in multimodal case
            
            # Inflow demand updates
            for rs in reservoir.RouteSections:
                
                mode=rs.Route.Mode
                inflowdemand=dict().fromkeys([mode],0.)
                
                if rs.EntryNode.Type == 'origin':
                    inflowdemand[mode] = rs.FlowData[indtime]['Demand'][mode]
                        
                if rs.EntryNode.Type =='externalentry':
                    if rs.FlowData[indtime]['NumWaitingVeh'][mode] > 0:
                        inflowdemand[mode] = rs.EntryNode.get_capacity(t)
                    else:
                        inflowdemand[mode] = rs.FlowData[indtime]['Demand'][mode]
                        
                if rs.EntryNode.Type =='border':
                    inflowdemand = rs.get_previous_routesection().FlowData[indtime]['OutflowDemand']
                    
                rs.FlowData[indtime]['InflowDemand'] = inflowdemand
                            
            # Merging coefficients TODO : endogenous
                
            
            if Simulation.MergeModel == 'equiproba':
                
                for rs in reservoir.RouteSections:
                    
                    mode=rs.Route.Mode
                    reservoirmergecoeff = dict().fromkeys(modes,0.)
                    
                    if rs.EntryNode.Type == 'externalentry':
                        reservoirmergecoeff[mode] = 1 / reservoir.NumberOfExtRouteSection
                    else:
                        reservoirmergecoeff[mode] = 1
                        
                    rs.FlowData[indtime]['ReservoirMergeCoeff']=reservoirmergecoeff
                    
            elif Simulation.MergeModel == 'demprorata':
                
                inflow_demand_sum = dict.fromkeys(modes,0.)
                
                for rs in reservoir.RouteSections:
                    if rs.EntryNode.Type == 'externalentry' or rs.EntryNode.Type == 'border':
                        inflow_demand_sum[rs.Route.Mode] +=rs.FlowData[indtime]['InflowDemand'][rs.Route.Mode]
                        
                for rs in reservoir.RouteSections:
                    reservoirmergecoeff = dict().fromkeys(modes,0.)
                    
                    if (rs.EntryNode.Type == 'externalentry' or rs.EntryNode.Type == 'border') and inflow_demand_sum[rs.Route.Mode]>0:
                        reservoirmergecoeff[rs.Route.Mode] = rs.FlowData[indtime]['InflowDemand'][rs.Route.Mode] / inflow_demand_sum[rs.Route.Mode]
                    else:
                        reservoirmergecoeff[rs.Route.Mode] = 1.
                        
                    rs.FlowData[indtime]['ReservoirMergeCoeff']=reservoirmergecoeff
                        
                for mn in reservoir.MacroNodes:
                    if mn.Type == 'externalentry' or mn.Type == 'border':
                        
                        sum_merge_coeff = dict.fromkeys(modes,0.)
                        
                        for rs in reservoir.RouteSections:
                            if rs.EntryNode == mn:
                                sum_merge_coeff[rs.Route.Mode]+=rs.FlowData[indtime]['ReservoirMergeCoeff'][rs.Route.Mode]
                                
                        for rs in reservoir.RouteSections:    
                            
                            macronodemergecoeff = dict.fromkeys(modes,0)
                            if rs.EntryNode == mn:
                                if sum_merge_coeff[rs.Route.Mode] > 0:
                                    macronodemergecoeff[rs.Route.Mode]=rs.FlowData[indtime]['ReservoirMergeCoeff'][rs.Route.Mode]/sum_merge_coeff[rs.Route.Mode]
                                else:
                                    macronodemergecoeff[rs.Route.Mode]=1.
                                    
                                rs.FlowData[indtime]['MacroNodeMergeCoeff']=macronodemergecoeff
                                    
            # Border inflow supply
            borderinflowsupply=[]
            
            for macronode in reservoir.MacroNodes:
                
                # Loop on external entry
                if macronode.Type == 'externalentry' or macronode.Type == 'border':
                    
                    demandflows=[]
                    localmergecoeffs=[]
                    borderinflowsupply=[]
                    localrs=[]
                    for rs in reservoir.RouteSections:   
                        if rs.EntryNode == macronode:  # Loop on route section from external entry
                            demandflows.append(rs.FlowData[indtime]['InflowDemand'][rs.Route.Mode])
                            localmergecoeffs.append(rs.FlowData[indtime]['MacroNodeMergeCoeff'][rs.Route.Mode])
                            localrs.append(rs)
                            
                    smc = sum(localmergecoeffs)
                    
                    if smc > 0:
                        localmergecoeffs = [coeff / smc for coeff in localmergecoeffs]
                    else:
                        localmergecoeffs = [1. for coeff in localmergecoeffs]
                            
                    if len(demandflows) > 0:
                        borderinflowsupply = Merge(demandflows, localmergecoeffs, macronode.get_capacity(t))
    
                        i = 0
                        localinflowsupply = dict.fromkeys(modes,0.)
                        for rs in localrs:
                            localinflowsupply[rs.Route.Mode] = borderinflowsupply[i]
                            i = i + 1
                            
                        rs.FlowData[indtime]['LocalInflowSupply']=localinflowsupply
                        
            # Reservoir inflow supply
            inflowsupply=[]
            mergecoeffs=[]
            extrs=[]
            
            for rs in reservoir.RouteSections:
                if rs.EntryNode.Type == 'externalentry' or rs.EntryNode.Type=='border' :  # Loop on route section from external entry
                    inflowsupply.append(rs.FlowData[indtime]['LocalInflowSupply'][rs.Route.Mode])
                    mergecoeffs.append(rs.FlowData[indtime]['ReservoirMergeCoeff'][rs.Route.Mode])
                    extrs.append(rs)
                    
            if len(inflowsupply)>0:
                #print(reservoir.ID, mergecoeffs,inflowsupply)
                if max(inflowsupply)>0:
                    inflowsupply=Merge(inflowsupply,mergecoeffs,reservoir.FlowData[indtime]['ProductionSupply'][mode]/reservoir.FlowData[indtime]['AvgTripLength'][mode])
                
                i=0
                for rs in extrs:
                    rsinflowsupply = dict().fromkeys(modes,0.)
                    rsinflowsupply[rs.Route.Mode]=inflowsupply[i]
                    i=i+1
                    rs.FlowData[indtime]['InflowSupply']=rsinflowsupply
            
        # Third reservoir loop (outflow supply, effective outflow, effective inflow, external queue and accumulation at next time step updates)
        for reservoir in Reservoirs:
            
            # outflow supply update
            for rs in reservoir.RouteSections:
                outflowsupply=dict().fromkeys(modes,0.)
                if rs.ExitNode.Type =='externalexit' or rs.ExitNode.Type =='destination':
                    outflowsupply[rs.Route.Mode]=rs.ExitNode.get_capacity(t)
                elif rs.ExitNode.Type =='border':
                    outflowsupply[rs.Route.Mode]=rs.get_next_routesection().FlowData[indtime]['InflowSupply'][rs.Route.Mode]
                    
                rs.FlowData[indtime]['OutflowSupply']=outflowsupply
               
            # effective outflow update
            for rs in reservoir.RouteSections:
                outflow=dict().fromkeys(modes,0.)
                outflow[rs.Route.Mode]=min(rs.FlowData[indtime]['OutflowDemand'][rs.Route.Mode],rs.FlowData[indtime]['OutflowSupply'][rs.Route.Mode])
                rs.FlowData[indtime]['Outflow']=outflow
            
        for reservoir in Reservoirs:
            
            # effective inflow update
            for rs in reservoir.RouteSections:
                
                if rs.EntryNode.Type == 'externalentry':
                    
                    rs.FlowData[indtime]['Inflow']=rs.FlowData[indtime]['InflowSupply']
                    
                    numwaitingveh=dict().fromkeys(modes,0.)
                    if  rs.FlowData[indtime]['Demand'][rs.Route.Mode] > rs.FlowData[indtime]['InflowSupply'][rs.Route.Mode] or rs.FlowData[indtime]['NumWaitingVeh'][rs.Route.Mode]>0:
                        numwaitingveh[rs.Route.Mode]+= Simulation.TimeStep*(rs.FlowData[indtime]['Demand'][rs.Route.Mode] - rs.FlowData[indtime]['InflowSupply'][rs.Route.Mode])        
                    rs.FlowData[indtime]['NumWaitingVeh']=numwaitingveh
                    
                elif rs.EntryNode.Type == 'origin':
                    rs.FlowData[indtime]['Inflow']=rs.FlowData[indtime]['Demand']
                else:
                    rs.FlowData[indtime]['Inflow']=rs.PreviousRouteSection.FlowData[indtime]['Outflow']
                
                    
        if t+Simulation.TimeStep < Simulation.Duration:
            
            init_time_step(t+Simulation.TimeStep, Reservoirs, Routes)
            
            for reservoir in Reservoirs:
                
                reservoir.FlowData[indtime]['Inflow']=dict().fromkeys(modes,0.)
                reservoir.FlowData[indtime]['Outflow']=dict().fromkeys(modes,0.)
                reservoir.FlowData[indtime+1]['Acc']=dict().fromkeys(modes,0.)
                
                # External queue update : TO DO
                for rs in reservoir.RouteSections:
                     rs.FlowData[indtime+1]['AccQueue']=dict().fromkeys(modes,0.)
                    
                # Accumulation update
                for rs in reservoir.RouteSections:
                    
                    rs.FlowData[indtime+1]['AccCircu']=dict().fromkeys(modes,0.)
                    rs.FlowData[indtime+1]['AccCircu'][rs.Route.Mode] = rs.FlowData[indtime]['AccCircu'][rs.Route.Mode] + Simulation.TimeStep * (rs.FlowData[indtime]['Inflow'][rs.Route.Mode] - rs.FlowData[indtime]['Outflow'][rs.Route.Mode])
                    
                    rs.FlowData[indtime+1]['Acc']=dict().fromkeys(modes,0.)
                    rs.FlowData[indtime+1]['Acc'][rs.Route.Mode] = rs.FlowData[indtime+1]['AccCircu'][rs.Route.Mode]+rs.FlowData[indtime+1]['AccQueue'][rs.Route.Mode]
                    
                    rs.FlowData[indtime+1]['NumWaitingVeh'] = rs.FlowData[indtime]['NumWaitingVeh']
                    
                    reservoir.FlowData[indtime]['Inflow'][rs.Route.Mode] += rs.FlowData[indtime]['Inflow'][rs.Route.Mode]
                    reservoir.FlowData[indtime]['Outflow'][rs.Route.Mode] += rs.FlowData[indtime]['Outflow'][rs.Route.Mode]
                    
                    reservoir.FlowData[indtime+1]['Acc'][rs.Route.Mode] += rs.FlowData[indtime+1]['Acc'][rs.Route.Mode]
                    
            for reservoir in Reservoirs:
                print(reservoir.ID, 'accumulation -> ', reservoir.FlowData[indtime+1]['Acc'])
                    
                    
                    
def TripBased(Simulation, Reservoirs, Routes, MacroNodes, GlobalDemand):
    
    vehicles=[]

    prevtime = 0.
    indprevtime = 0
    
    init_time_step(prevtime, Reservoirs, Routes)
    
    # First event
    next_trip = Demand.get_next_trip(GlobalDemand, prevtime)
    
    curtime = next_trip.Time
    
    # Time step (s)
    elapsedtime = curtime - prevtime
    
    nvehs = 0
    u0 = Vehicle.Vehicle(nvehs, next_trip.Mode, next_trip.RouteID, next_trip.Time, Routes)
    
    while curtime < Simulation.Duration:
        
        # initialization
        indcurtime = indprevtime+1
        init_time_step(curtime, Reservoirs, Routes)
        
        for reservoir in Reservoirs:
            for rs in reservoir.RouteSections:
                rs.FlowData[indcurtime]['Acc']=rs.FlowData[indprevtime]['Acc']
                rs.FlowData[indcurtime]['Nin']=rs.FlowData[indprevtime]['Nin']
                rs.FlowData[indcurtime]['Nout']=rs.FlowData[indprevtime]['Nout']
                
            reservoir.FlowData[indcurtime]['MeanSpeed']=reservoir.FlowData[indprevtime]['MeanSpeed']
            
        # Update traveled distances and times for each vehicle on the network
        for vehicle in vehicles:
            curres = Vehicle.get_current_reservoir(vehicle)
            vehicle.TotalTraveledDistance += elapsedtime * curres.FlowData[indcurtime]['MeanSpeed']
            vehicle.TotalTraveledTime += elapsedtime
            vehicle.RemainingLengthOfCurrentReservoir -= elapsedtime * curres.FlowData[indcurtime]['MeanSpeed']
            
        # Update entering and/or exiting reservoir information by considering next vehicle to deal with
        
        # if vehicle u0 exists its current reservoir
        if u0.PathIndex > -1:
            
            creation = False
            ru0 = u0.Path[u0.PathIndex]
            pu0 = u0.RouteSections[u0.PathIndex]
            u0.ExitTimes[u0.PathIndex]=curtime
            
            pu0.FlowData[indcurtime]['Acc']-=1
            pu0.FlowData[indcurtime]['Nout']+=1
            
            ru0.FlowData[indcurtime]['Acc']-=1
            ru0.FlowData[indcurtime]['MeanSpeed']=ru0.get_speed_from_accumulation(ru0.FlowData[indcurtime]['Acc'])
            
            pu0.SortedVehicles.pop(0)           # remove u0 from the list of the route section
            
            # Update route section exit demand times
            if len(pu0.SortedVehicles)>0:
                pu0.t_out_demand = curtime + (pu0.SortedVehicles[0].RemainingLengthOfCurrentReservoir / ru0.FlowData[indcurtime]['MeanSpeed'])
            else:
                pu0.t_out_demand = float('inf')
        else:
            vehicles.append(u0)
            creation=True
        
        # if vehicle u0 enters its next (or first) reservoir
        if u0.PathIndex < len(u0.Path):
            u0.PathIndex+=1
            ru0 = u0.Path[u0.PathIndex]
            pu0 = u0.RouteSections[u0.PathIndex]
            u0.EntryTimes[u0.PathIndex]=curtime
            
            pu0.FlowData[indcurtime]['Acc']+=1
            pu0.FlowData[indcurtime]['Nin']+=1
            
            ru0.FlowData[indcurtime]['Acc']+=1
            ru0.FlowData[indcurtime]['MeanSpeed']=ru0.get_speed_from_accumulation(ru0.FlowData[indcurtime]['Acc'],u0.Mode)
            
            pu0.SortedVehicles.append(u0)   # Added to the end of list
            u0.RemainingLengthOfCurrentReservoir = pu0.TripLength
            
            # Update route section entry demand times and estimated inflow demand
            if creation==True:
                pu0.NextDesiredEntryTime=Demand.get_next_trip_from_origin(GlobalDemand, pu0.EntryNode.ID, curtime).Time
                pu0.t_in_demand = pu0.NextDesiredEntryTime
                
                # TO DO
                #q_in_demand = 
            else:
                prevpu0 = u0.RouteSections[u0.PathIndex-1]
                pu0.t_in_demand = prevpu0.t_out_demand   
                q_in_demand = 1. / (prevpu0.t_out_demand-prevpu0.t_last_out_demand)
                
            # Update route section entry supply times
                
            # 1. Update merging coefficients
            sum_ext_acc = 0
            for rs in ru0.RouteSections:
                if rs.EntryNode.Type=='externalentry' or rs.EntryNode.Type=='border':  
                    sum_ext_acc+=rs.FlowData[indcurtime]['Acc']
        
            for rs in ru0.RouteSections:
                rs.FlowData[indcurtime]['MergeCoeff']=rs.FlowData[indcurtime]['Acc']/sum_ext_acc
                
            # 2. Modification of entry demand times due to border supply
            for macronode in ru0.MacroNodes:
                
                if macronode.Type == 'externalentry' or 'border':
                    
                    localtindemands=[]
                    locallastentriestimes=[]
                    localmergecoeffs=[]
                    localentrydemandtimes=[]
                    rss=[]
                    
                    for rs in ru0.RouteSections: 
                        
                        if rs.EntryNode == macronode:
                            localtindemands.append(rs.t_in_demand)
                            localmergecoeffs.append(rs.FlowData[indcurtime]['MergeCoeff'])
                            locallastentriestimes.append(rs.t_last_entry)
                            rss.append(rs)
                           
                    smc = sum(localmergecoeffs)
                    localmergecoeffs = localmergecoeffs / smc
                    
                    localentrydemandtimes=MergeTime(localtindemands,[1 in range(len(localtindemands))],localmergecoeffs, locallastentriestimes,macronode.get_capacity(curtime))
                    
                    for rs in rss:
                        rs.t_in_demand = max(rs.t_in_demand, localentrydemandtimes[ rss.index(rs) ])
                    
            # 3. Entry supply times
            
            # Production supply
            tmp=0
            for rs in ru0.RouteSections:
                if rs.EntryNode.Type == 'externalentry':
                    tmp+= rs.TripLength*Demand.get_partial_demand(GlobalDemand, rs, t)
 
            ru0.FlowData[indcurtime]['ProductionSupply']=ru0.get_entry_supply(ru0.FlowData[indcurtime]['Acc'])-tmp
            
            # Average trip length
            tmp = 0
            for rs in ru0.RouteSections:
                if rs.EntryNode.Type=='externalentry' or rs.EntryNode.Type=='border':  
                    tmp=tmp+rs.FlowData[indcurtime]['Acc']/rs.TripLength
                
            if tmp>0:
                ru0.FlowData[indcurtime]['AvgTripLength']=ru0.FlowData[indcurtime]['Acc']/tmp
            else:
                sumtriplength = 0
                for rs in ru0.RouteSections:
                    if rs.EntryNode.Type=='externalentry' or rs.EntryNode.Type=='border':  
                        sumtriplength += rs.TripLength
                ru0.FlowData[indcurtime]['AvgTripLength']=sumtriplength/len(ru0.RouteSections)
                
                
            localtindemands =[]
            localmergecoeffs =[]
            localtriplengths =[]
            localentrysupplytimes =[]
            rss = []
            for rs in ru0.RouteSections: 
                        
                if rs.EntryNode == macronode:
                    localtindemands.append(rs.t_in_demand)
                    localmergecoeffs.append(rs.FlowData[indcurtime]['MergeCoeff'])
                    localtriplengths.append(rs.TripLength)
                    locallastentriestimes.append(rs.t_last_entry)
                    rss.append(rs)
                           
                    localentrysupplytimes=MergeTime(localtindemands,localtriplengths, localmergecoeffs, locallastentriestimes,u0.FlowData[indcurtime]['ProductionSupply'])
                    
            for rs in rss:
                rs.t_in_supply = localentrysupplytimes[rss.index(rs)]
                
            for rs in ru0.RouteSections:
                if rs.EntryNode.Type == 'internalentry':
                    rs.t_in_supply = rs.t_in_demand
                
        else:
            # the vehicule u0 completed its trip
            u0.Route.FlowData['Time']['TravelTime']=curtime-u0.EntryTimes[0]
        
        # Update reservoir exit supply times
        if creation==False:
            
            prevpu0 = u0.RouteSections[u0.PathIndex-1]
            
            if u0.PathIndex == len(u0.Path):
                prevpu0.t_out_supply = prevpu0.t_last_out_supply + 1./prevpu0.ExitNode.get_capacity(curtime)
            else:
                prevpu0.t_out_supply = pu0.t_in_supply
                    
        # Next possible entry time (route beginning)
        t_r_in=[]
        rs_min=[]
        for reservoir in reservoirs:
            t_rs_in=[]
            rss=[]
            for rs in reservoir.RouteSections:
                if rs.EntryNode.Type == 'externalentry' or rs.EntryNode.Type == 'origin':
                    t_rs_in.append( max(rs.t_in_demand,rs.t_in_supply) )
                    rss.append(rs)
                    
            t_r_in.append( min(t_rs_in) )
            rs_min.append(rss[t_rs_in.index(min(t_rs_in))])
        
        t_in = min(t_r_in)
        p_min_in = rs_min[t_r_in.index(min(t_r_in))]
        
        # Next possible exit time
        t_r_out=[]
        rs_min=[]
        for reservoir in reservoirs:
            for rs in reservoir.RouteSections:
                t_r_out.append(max(rs.t_out_demand,rs.t_out_supply))
                rs_min.append(rs)
                
        t_out = min(t_r_out)
        p_min_out = rs_min[t_r_out.index(min(t_r_out))]
     
        # Next event time and concerned vehicle
        t_event = min(t_in,t_out)
        
        if t_in < t_out:
            p_event = p_min_in
            nvehs += 1 
            u0 = Vehicle.Vehicle( nvehs, p_event.route.Mode, p_event.route.ID, t_event, Routes)
        else:
            p_event = p_min_out
            u0 = p_event.SortedVehicles[0]
        
        # Times update
        curtime = t_event
        elapsedtime = curtime - prevtime
