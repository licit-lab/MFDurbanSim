class RouteSection:
    def __init__(self, routeID, macronodeIn, macronodeOut, tripLength):

        ## Fixed variables ##
        self.RouteID = routeID
        self.EntryNode = macronodeIn
        self.ExitNode = macronodeOut
        self.TripLength = tripLength

        ## Dynamic variables ##
        self.DataCommon = [] #[{"Time":0, "MergeCoeff":0, "ExitCoeff":0, "Acc":0, "Inflow":0, "Outflow":0, "Nin":0, "Nout":0}]

        #Acc-based
        self.DataAccBased = [] #[{"Time":0, "InflowDemand":0, "InflowSupply":0, "OutflowDemand":0, "OutflowSupply":0, "AccCircu":0, "AccQueue":0, "OutflowCircu":0, "NoutCircu":0}]

        #Trip-based
        self.DataTripBased = [] #[{"Time":0, "DemandEntryTime":0, "DemandEntryVeh":0, "VehList":0, "DemandTimeIndex":0, "LastEntryTime":0, "LastExitTime":0, "DesiredEntryTime":0,
                                #   "DesiredExitTime":0, "DesiredEntryVeh":0, "DesiredExitVeh":0, "EntrySupplyTime":0, "ExitSupplyTime":0, "EntryTimes":0, "ExitTimes":0}]
