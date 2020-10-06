from AccBased_functions import *
from main_objects import Demand

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

            reservoir.Data[indtime]['ProductionSupply']=reservoir.get_entry_supply(reservoir.Data[indtime]['Acc'])-tmp
            
            # Average trip length update
            tmp = 0
            for rs in reservoir.RouteSections:
                tmp=tmp+rs.Data[indtime]['Acc']/rs.TripLength
                
            if tmp>0:
                reservoir.Data[indtime]['AvgTripLength']=reservoir.Data[indtime]['Acc']/tmp
            else:
                sumtriplength = 0
                for rs in reservoir.RouteSections:
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
                    rs.Data[indtime+1]['AccCircu'] = 0
                    
                    rs.Data[indtime+1]['Acc'] = rs.Data[indtime+1]['AccCircu']+rs.Data[indtime+1]['AccQueue']

def TripBased(Simulation, Reservoirs, Routes, MacroNodes, Demand, Vehicles):

    #Time loop
    for t in range(0, Simulation.Duration, Simulation.TimeStep):
        print("TripBased")
