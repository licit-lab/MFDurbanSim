class RouteSection:
    def __init__(self, route, reservoir, macronodeIn, macronodeOut, tripLength):

        ## Fixed variables ##
        self.Route = route
        self.Reservoir = reservoir
        self.EntryNode = macronodeIn
        self.ExitNode = macronodeOut
        self.TripLength = tripLength              # trip length portion (m)

        ## Dynamic variables ##
        self.Data = [{"Time":0, 
                      "MergeCoeff":0,              # partial merge coefficient (only for internal route section - not for an origin route section )
                      "ExitCoeff":0,
                      "Acc":0,                     # partial accumulation (veh)
                      "Inflow":0, 
                      "Outflow":0, 
                      "Nin":0, 
                      "Nout":0,
                      "InflowDemand":0,             # partial inflow demand (veh/s)
                      "InflowSupply":0,             # partial inflow supply (m/s) the computation is different if EntryNode is a border or not
                      "OutflowDemand":0, 
                      "OutflowSupply":0,            # partial outflow supply (veh/s)
                      "AccCircu":0, 
                      "AccumulationQueue":0,        # partial queuing accumulation (veh)
                      "OutflowCircu":0,             # partial circulating outflow (veh/s)
                      "NoutCircu":0,
                      "DemandEntryTime":0, 
                      "DemandEntryVeh":0, 
                      "VehList":0, 
                      "DemandTimeIndex":0, 
                      "LastEntryTime":0, 
                      "LastExitTime":0, 
                      "DesiredEntryTime":0,
                      "DesiredExitTime":0, 
                      "DesiredEntryVeh":0, 
                      "DesiredExitVeh":0, 
                      "EntrySupplyTime":0, 
                      "ExitSupplyTime":0, 
                      "EntryTimes":0, 
                      "ExitTimes":0}]

