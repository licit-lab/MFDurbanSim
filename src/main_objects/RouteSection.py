class RouteSection:
    def __init__(self, routeID, macronodeIn, macronodeOut, tripLength):

        ## Fixed variables ##
        self.RouteID = routeID
        self.EntryNode = macronodeIn
        self.ExitNode = macronodeOut
        self.TripLength = tripLength

        ## Dynamic variables ##

        self.Time = []
        self.ExitCoeff = []
        self.Acc = []
        self.Inflow = []
        self.Outflow = []
        self.Nin = []
        self.Nout = []

        #Acc-based
        self.InflowDemand = []
        self.InflowSupply = []
        self.OutflowDemand = []
        self.OutflowSupply = []
        self.AccCircu = []
        self.AccQueue = []
        self.OutflowCircu = []
        self.NoutCircu = []

        #Trip-based
        self.DemandEntryTime = []
        self.DemandEntryVeh = []
        self.VehList = []
        self.DemandTimeIndex = []
        self.LastEntryTime = []
        self.LastExitTime = []
        self.DesiredEntryTime = []
        self.DesiredExitTime = []
        self.DesiredEntryVeh = []
        self.DesiredExitVeh = []
        self.EntrySupplyTime = []
        self.ExitSupplyTime = []
        self.EntryTimes = []
        self.ExitTimes = []

    def init_fixed_variables(self, routeID, macronodeIn, macronodeOut, tripLength):
        self.RouteID = routeID
        self.EntryNode = macronodeIn
        self.ExitNode = macronodeOut
        self.TripLength = tripLength
        
