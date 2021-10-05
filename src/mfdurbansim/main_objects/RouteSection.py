from mfdurbansim.main_objects.FlowElement import FlowElement

class RouteSection(FlowElement):
    def __init__(self, route, reservoir, macronodeIn, macronodeOut, tripLength):

        ## Dynamic variables ##
        DataKeys = [ 
                     # common to both solvers
                     "InflowDemand",             # partial inflow demand (veh/s)
                     
                     # Accumulation based model
                      "MacroNodeMergeCoeff",              # partial merge coefficient (only for internal route section - not for an origin route section ?? )
                      "ReservoirMergeCoeff",              # partial merge coefficient (only for internal route section - not for an origin route section ?? )
                      "ExitCoeff",
                      "Acc",                     # partial accumulation (veh)
                      "Inflow", 
                      "Outflow", 
                      "Nin", 
                      "Nout",
                      "InflowSupply",             # partial inflow supply (veh/s)
                      "LocalInflowSupply",        # partial and local inflow supply (veh/s)
                      "OutflowDemand",            # partial outflow demand (veh/s)
                      "OutflowSupply",            # partial outflow supply (veh/s)
                      "AccCircu",                 # partial accumulation (veh)
                      "AccQueue",                 # partial queuing accumulation (veh)
                      "NoutCircu",
                      "NumWaitingVeh",
                      "Demand",
                      
                      # Trip based model
                      "EntryDemandTime",   # input data ?
                      "EntrySupplyTime",  # input data ?
                      "ExitDemandTime",  # input data ?
                      "ExitSupplyTime",  # input data ?
                      
                      "LastEntryTime",
                      "LastExitTime",
                      
                      #"SortedTravelingVehicles",        # list of traveling vehicles sorted by remaining travel distance
                      
                      "DemandEntryVeh", 
                      "VehList", 
                      "DemandTimeIndex", 
                      
                      "DesiredEntryTime",
                      "DesiredExitTime", 
                      "DesiredEntryVeh", 
                      "DesiredExitVeh", 
                      
                    
                      
                      "EntryTimes", 
                      "ExitTimes"]
        
        FlowElement.__init__(self, DataKeys,[route.Mode])
        
        # Usefull variables for trip based solver
        self.NextDesiredEntryTime = -1
        self.LastCreationTime = -1
        self.NextDesiredExitTime = -1
        
        self.SortedVehicles=[]  # list of vehicle on the route section sorted by remaining distance
        
        self.t_in_demand = -1
        self.t_in_supply = -1
        self.t_last_entry = -1
        
        self.t_out_demand = -1
        self.t_out_supply = -1
        self.t_last_out_demand = -1
        
        self.t_in = -1
        self.t_out = -1
        
        # Fixed variables ##
        self.Route = route
        self.Reservoir = reservoir
        self.EntryNode = macronodeIn
        self.ExitNode = macronodeOut
        self.TripLength = tripLength              # trip length portion (m)
        self.PreviousRouteSection = 0               # previous route section of the path (RouteSection)
        self.NextRouteSection = 0               # next route section of the path (RouteSection)
        

    def get_previous_routesection(self):
        if self.Route.RouteSections.index(self)>0:
            return self.Route.RouteSections[self.Route.RouteSections.index(self)-1]
        else:
            return 0
        
    def get_next_routesection(self):
        if self.Route.RouteSections.index(self)<len(self.Route.RouteSections):
            return self.Route.RouteSections[self.Route.RouteSections.index(self)+1]
        else:
            return 0
