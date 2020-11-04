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
    
    while max(UnservedFlows) > 0:
        
        TmpUnservedFlows = [0 for i in range(len(DemandFlows))]
        TmpTotalServedInflow = 0
        TmpAlpha = 0        
        for i in range(len(UnservedFlows)):
            if UnservedFlows[i]==1:
                if DemandFlows[i] < alpha/MergeCoeffs[i] * (Capacity-TotalServedInflow):
                    # demand i is served
                    Q[i]=DemandFlows[i]
                    TmpUnservedFlows[i]=0
                    TmpTotalServedInflow=TmpTotalServedInflow+Q[i]
                else:
                    # demand i is not served
                    Q[i]=alpha/MergeCoeffs[i] * (Capacity-TotalServedInflow)
                    TmpUnservedFlows[i]=1
                    TmpAlpha= TmpAlpha+MergeCoeffs[i]
                    
        UnservedFlows=TmpUnservedFlows
        alpha=TmpAlpha
        TotalServedInflow=TotalServedInflow+TmpTotalServedInflow
        
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
    
def AccBased(Simulation, Reservoirs, Routes, MacroNodes, GlobalDemand):

# Init variables
    indtime = -1
    init_time_step(0., Reservoirs, Routes)

# Time loop
    for t in range(0, Simulation.Duration, Simulation.TimeStep):

        indtime=indtime+1
        print("Time step :" , t)
        
        # First reservoir loop (outflow demand, production supply and average trip length updates)
        for reservoir in Reservoirs:

            print("Reservoir : ", reservoir.ID)
          
            # Production modification (todo for queue dyn model)
         
            # Outflow demand update
            for rs in reservoir.RouteSections:
                if reservoir.Data[indtime]['Acc']>0:
                    rs.Data[indtime]['OutflowDemand']=rs.Data[indtime]['Acc']/reservoir.Data[indtime]['Acc']*reservoir.Data[indtime]['Production']/reservoir.Data[indtime]['AvgTripLength']
                else:
                  rs.Data[indtime]['OutflowDemand']=0.
  
             # todo: maxdem,queuedyn, and decrdem diverge cases
             
             # Entry production supply update
            tmp=0
            for rs in reservoir.RouteSections:
                if rs.EntryNode.Type == 'externalentry':
                    tmp=tmp+rs.TripLength*Demand.get_partial_demand(GlobalDemand, rs, t)

            reservoir.Data[indtime]['ProductionSupply']=reservoir.get_entry_supply_from_accumulation(reservoir.Data[indtime]['Acc'],'VL')-tmp
            
            # Average trip length update
            tmp = 0
            for rs in reservoir.RouteSections:
                if rs.EntryNode.Type=='externalentry' or rs.EntryNode.Type=='border':  
                    tmp=tmp+rs.Data[indtime]['Acc']/rs.TripLength
                
            if tmp>0:
                reservoir.Data[indtime]['AvgTripLength']=reservoir.Data[indtime]['Acc']/tmp
            else:
                sumtriplength = 0
                for rs in reservoir.RouteSections:
                    if rs.EntryNode.Type=='externalentry' or rs.EntryNode.Type=='border':  
                        sumtriplength += rs.TripLength
                reservoir.Data[indtime]['AvgTripLength']=sumtriplength/len(reservoir.RouteSections)
                
        # Second reservoir loop (inflow demand, merging coefficients, border inflow supply and reservoir inflow supply updates)
        for reservoir in Reservoirs:
            # Inflow demand updates
            for rs in reservoir.RouteSections:
                if rs.EntryNode.Type == 'origin' or rs.EntryNode.Type =='externalentry':
                    if rs.Data[indtime]['AccQueue']>0:
                        rs.Data[indtime]['InflowDemand']=rs.EntryNode.get_capacity(t)
                    else:
                        rs.Data[indtime]['InflowDemand']=Demand.get_partial_demand(GlobalDemand, rs, t)
                            
            # Merging coefficients (equiproba merge case)
            for rs in reservoir.RouteSections:
                if rs.EntryNode.Type == 'externalentry':
                    rs.Data[indtime]['MergeCoeff']=1/reservoir.NumberOfExtRouteSection
                else:
                    rs.Data[indtime]['MergeCoeff']=1
            
            # Border inflow supply
            borderinflowsupply=[]
            for macronode in reservoir.MacroNodes:
                
                # Loop on external entry
                if macronode.Type == 'externalentry':
                    demandflows=[]
                    localmergecoeffs=[]
                    borderinflowsupply=[]
                    localrs=[]
                    for rs in reservoir.RouteSections:   
                        if rs.EntryNode == macronode:  # Loop on route section from external entry
                            demandflows.append(Demand.get_partial_demand(GlobalDemand, rs, t))
                            localmergecoeffs.append(rs.Data[indtime]['MergeCoeff'])
                            localrs.append(rs)
                            
                    smc = sum(localmergecoeffs)
                    localmergecoeffs = localmergecoeffs / smc
                            
                    if len(demandflows)>0:
                        borderinflowsupply=Merge(demandflows,localmergecoeffs,macronode.get_capacity(t))
    
                        i=0
                        for rs in localrs:
                            rs.Data[indtime]['LocalInflowSupply']=borderinflowsupply[i]
                            i=i+1
                            
            # Reservoir inflow supply
            inflowsupply=[]
            mergecoeffs=[]
            extrs=[]
            for rs in reservoir.RouteSections:
                if rs.EntryNode == macronode:  # Loop on route section from external entry
                    inflowsupply.append(rs.Data[indtime]['LocalInflowSupply'])
                    mergecoeffs.append(rs.Data[indtime]['MergeCoeff'])
                    extrs.append(rs)
                    
            if len(inflowsupply)>0:
                inflowsupply=Merge(inflowsupply,mergecoeffs,reservoir.Data[indtime]['ProductionSupply']/reservoir.Data[indtime]['AvgTripLength'])
                
                i=0
                for rs in extrs:
                    rs.Data[indtime]['InflowSupply']=inflowsupply[i]
                    i=i+1
    
            
        # Third reservoir loop (outflow supply, effective outflow, effective inflow, external queue and accumulation at next time step updates)
        for reservoir in Reservoirs:
            
            # outflow supply update
            for rs in reservoir.RouteSections:
                if rs.ExitNode.Type == 'destination' or rs.ExitNode.Type =='externalexit':
                    rs.Data[indtime]['OutflowSupply']=rs.ExitNode.get_capacity(t)
                else:
                    rs.Data[indtime]['OutflowSupply']=0.
                    
            # effective outflow update
            for rs in reservoir.RouteSections:
                rs.Data[indtime]['Outflow']=min(rs.Data[indtime]['OutflowDemand'],rs.Data[indtime]['OutflowSupply'])
                
            # effective inflow update
            for rs in reservoir.RouteSections:
                if rs.EntryNode.Type == 'externalentry':
                    rs.Data[indtime]['Inflow']=rs.Data[indtime]['InflowSupply']
                elif rs.EntryNode.Type == 'origin':
                    rs.Data[indtime]['Inflow']=Demand.get_partial_demand(GlobalDemand, rs, t)
                else:
                    rs.Data[indtime]['Inflow']=rs.PreviousRouteSection.Data[indtime]['Outflow']
                    
            if t+Simulation.TimeStep < Simulation.Duration:
                init_time_step(t+Simulation.TimeStep, Reservoirs, Routes)
                        
                # External queue update : TO DO
                for rs in reservoir.RouteSections:
                    rs.Data[indtime+1]['AccQueue'] = 0
                    
                # Accumulation update
                for rs in reservoir.RouteSections:
                    
                    rs.Data[indtime+1]['AccCircu'] = rs.Data[indtime+1]['AccCircu'] + Simulation.TimeStep * (rs.Data[indtime]['Inflow'] - rs.Data[indtime]['Outflow'])
                    
                    rs.Data[indtime+1]['Acc'] = rs.Data[indtime+1]['AccCircu']+rs.Data[indtime+1]['AccQueue']

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
                rs.Data[indcurtime]['Acc']=rs.Data[indprevtime]['Acc']
                rs.Data[indcurtime]['Nin']=rs.Data[indprevtime]['Nin']
                rs.Data[indcurtime]['Nout']=rs.Data[indprevtime]['Nout']
                
            reservoir.Data[indcurtime]['MeanSpeed']=reservoir.Data[indprevtime]['MeanSpeed']
            
        # Update traveled distances and times for each vehicle on the network
        for vehicle in vehicles:
            curres = Vehicle.get_current_reservoir(vehicle)
            vehicle.TotalTraveledDistance += elapsedtime * curres.Data[indcurtime]['MeanSpeed']
            vehicle.TotalTraveledTime += elapsedtime
            vehicle.RemainingLengthOfCurrentReservoir -= elapsedtime * curres.Data[indcurtime]['MeanSpeed']
            
        # Update entering and/or exiting reservoir information by considering next vehicle to deal with
        
        # if vehicle u0 exists its current reservoir
        if u0.PathIndex > -1:
            
            creation = False
            ru0 = u0.Path[u0.PathIndex]
            pu0 = u0.RouteSections[u0.PathIndex]
            u0.ExitTimes[u0.PathIndex]=curtime
            
            pu0.Data[indcurtime]['Acc']-=1
            pu0.Data[indcurtime]['Nout']+=1
            
            ru0.Data[indcurtime]['Acc']-=1
            ru0.Data[indcurtime]['MeanSpeed']=ru0.get_speed_from_accumulation(ru0.Data[indcurtime]['Acc'])
            
            pu0.SortedVehicles.pop(0)           # remove u0 from the list of the route section
            
            # Update route section exit demand times
            if len(pu0.SortedVehicles)>0:
                pu0.t_out_demand = curtime + (pu0.SortedVehicles[0].RemainingLengthOfCurrentReservoir / ru0.Data[indcurtime]['MeanSpeed'])
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
            
            pu0.Data[indcurtime]['Acc']+=1
            pu0.Data[indcurtime]['Nin']+=1
            
            ru0.Data[indcurtime]['Acc']+=1
            ru0.Data[indcurtime]['MeanSpeed']=ru0.get_speed_from_accumulation(ru0.Data[indcurtime]['Acc'],u0.Mode)
            
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
                    sum_ext_acc+=rs.Data[indcurtime]['Acc']
        
            for rs in ru0.RouteSections:
                rs.Data[indcurtime]['MergeCoeff']=rs.Data[indcurtime]['Acc']/sum_ext_acc
                
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
                            localmergecoeffs.append(rs.Data[indcurtime]['MergeCoeff'])
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
 
            ru0.Data[indcurtime]['ProductionSupply']=ru0.get_entry_supply(ru0.Data[indcurtime]['Acc'])-tmp
            
            # Average trip length
            tmp = 0
            for rs in ru0.RouteSections:
                if rs.EntryNode.Type=='externalentry' or rs.EntryNode.Type=='border':  
                    tmp=tmp+rs.Data[indcurtime]['Acc']/rs.TripLength
                
            if tmp>0:
                ru0.Data[indcurtime]['AvgTripLength']=ru0.Data[indcurtime]['Acc']/tmp
            else:
                sumtriplength = 0
                for rs in ru0.RouteSections:
                    if rs.EntryNode.Type=='externalentry' or rs.EntryNode.Type=='border':  
                        sumtriplength += rs.TripLength
                ru0.Data[indcurtime]['AvgTripLength']=sumtriplength/len(ru0.RouteSections)
                
                
            localtindemands =[]
            localmergecoeffs =[]
            localtriplengths =[]
            localentrysupplytimes =[]
            rss = []
            for rs in ru0.RouteSections: 
                        
                if rs.EntryNode == macronode:
                    localtindemands.append(rs.t_in_demand)
                    localmergecoeffs.append(rs.Data[indcurtime]['MergeCoeff'])
                    localtriplengths.append(rs.TripLength)
                    locallastentriestimes.append(rs.t_last_entry)
                    rss.append(rs)
                           
                    localentrysupplytimes=MergeTime(localtindemands,localtriplengths, localmergecoeffs, locallastentriestimes,u0.Data[indcurtime]['ProductionSupply'])
                    
            for rs in rss:
                rs.t_in_supply = localentrysupplytimes[rss.index(rs)]
                
            for rs in ru0.RouteSections:
                if rs.EntryNode.Type == 'internalentry':
                    rs.t_in_supply = rs.t_in_demand
                
        else:
            # the vehicule u0 completed its trip
            u0.Route.Data['Time']['TravelTime']=curtime-u0.EntryTimes[0]
        
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
