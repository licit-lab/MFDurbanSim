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
        for i in range(UnservedFlows):
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
        
    
def AccBased(Simulation, Reservoirs, Routes, MacroNodes, GlobalDemand):

# Init variables
    Compute_Res(Reservoirs, Routes)

# Time loop
    for t in range(0, Simulation.Duration, Simulation.TimeStep):

        print("Time step :" , t)

        # First reservoir loop (outflow demand, production supply and average trip length updates)
        for reservoir in Reservoirs:

            print("Reservoir : ", reservoir.ID)
          
            # Production modification (todo for queue dyn model)
         
            # Outflow demand update
            for rs in reservoir.RouteSection:
                if reservoir.Data[t]['Acc']>0:
                    rs.Data[t]['OutflowCircu']=rs.Data[t]['Acc']/reservoir.Data[t]['Acc']*reservoir.Data[t]['Production']/reservoir.Data[t]['AvgTripLength']
                else:
                  rs.Data[t]['OutflowCircu']=0.
  
             # todo: maxdem,queuedyn, and decrdem diverge cases
             
             # Entry production supply update
            tmp=0
            for rs in reservoir.RouteSection:
                if rs.EntryNode['Type'] == 'externalentry':
                    tmp=tmp+rs.TripLength*Demand.get_partial_demand(GlobalDemand, rs, t)

            reservoir.Data[t]['ProductionSupply']=reservoir.get_entry_supply(reservoir.Data[t]['Acc'])-tmp
            
            # Average trip length update
            tmp = 0
            for rs in reservoir.RouteSection:
                tmp=tmp+rs.Data[t]['Acc']/rs.TripLength
                
            if tmp>0:
                reservoir.Data[t]['AvgTripLength']=reservoir.Data[t]['Acc']/tmp
                
        # Second reservoir loop (inflow demand, merging coefficients, border inflow supply and reservoir inflow supply updates)
        for reservoir in Reservoirs:
            # Inflow demand updates
            for rs in reservoir.RouteSection:
                if rs.EntryNode['Type'] == 'origin' or rs.EntryNode['Type'] =='externalentry':
                    if rs.Data[t]['AccumulationQueue']>0:
                        rs.Data[t]['InflowDemand']=rs.EntryNode.get_capacity(t)
                    else:
                        rs.Data[t]['InflowDemand']=Demand.get_partial_demand(GlobalDemand, rs, t)
                            
            # Merging coefficients (equiproba merge case)
            for rs in reservoir.RouteSection:
                if rs.EntryNode['Type'] == 'externalentry':
                    rs.Data[t]['MergeCoeff']=1/reservoir.NumberOfExtRouteSection
                else:
                    rs.Data[t]['MergeCoeff']=1
            
            # Border inflow supply
            Iexternalentry=[]
            for macronode in reservoir.MacroNodes:
                
                if macronode.Type == 'externalentry':
                    demandflows=[]
                    mergecoeffs=[]
                    for rs in reservoir.RouteSection:
                        if rs.EntryNode == macronode:  # to check
                            demandflows.append(Demand.get_partial_demand(GlobalDemand, rs, t))
                            mergecoeffs.append(rs.Data[t]['MergeCoeff'])
                            
                    Iexternalentry=[].append(Merge(demandflows,mergecoeffs,macronode.get_capacity(t)))
                            
            # Reservoir inflow supply
            
        # Third reservoir loop (outflow supply, effective outflow, effective inflow, external queue and accumulation at next time step updates)
        for reservoir in Reservoirs:
            # outflow supply update
            for rs in reservoir.RouteSection:
                if rs.ExitNode['Type'] == 'destination' or rs.ExitNode['Type'] =='externalexit':
                    rs.Data[t]['OutflowSupply']=rs.ExitNode.get_capacity(t)
                else:
                    rs.Data[t]['OutflowSupply']=0

def TripBased(Simulation, Reservoirs, Routes, MacroNodes, Demand, Vehicles):

    #Time loop
    for t in range(0, Simulation.Duration, Simulation.TimeStep):
        print("TripBased")
