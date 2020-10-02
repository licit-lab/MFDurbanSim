from main_objects.Element import Element

class RouteSection(Element):
    def __init__(self, route, reservoir, macronodeIn, macronodeOut, tripLength):

        ## Dynamic variables ##
        DataKeys = [ "Time", 
                      "MergeCoeff",              # partial merge coefficient (only for internal route section - not for an origin route section )
                      "ExitCoeff",
                      "Acc",                     # partial accumulation (veh)
                      "Inflow", 
                      "Outflow", 
                      "Nin", 
                      "Nout",
                      "InflowDemand",             # partial inflow demand (veh/s)
                      "InflowSupply",             # partial inflow supply (veh/s)
                      "LocalInflowSupply",        # partial and local inflow supply (veh/s)
                      "OutflowDemand",            # partial outflow demand (veh/s)
                      "OutflowSupply",            # partial outflow supply (veh/s)
                      "AccCircu",                 # partial accumulation (veh)
                      "AccQueue",                 # partial queuing accumulation (veh)
                      "NoutCircu",
                      "DemandEntryTime", 
                      "DemandEntryVeh", 
                      "VehList", 
                      "DemandTimeIndex", 
                      "LastEntryTime", 
                      "LastExitTime", 
                      "DesiredEntryTime",
                      "DesiredExitTime", 
                      "DesiredEntryVeh", 
                      "DesiredExitVeh", 
                      "EntrySupplyTime", 
                      "ExitSupplyTime", 
                      "EntryTimes", 
                      "ExitTimes"]
        
        Element.__init__(self, DataKeys)
        
        # Fixed variables ##
        self.Route = route
        self.Reservoir = reservoir
        self.EntryNode = macronodeIn
        self.ExitNode = macronodeOut
        self.TripLength = tripLength              # trip length portion (m)
        self.PreviousRouteSection = 0               # previous route section of the path (RouteSection)


