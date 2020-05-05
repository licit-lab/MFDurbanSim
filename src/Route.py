class Route:
    def __init__(self):

        #Input
        self.ID = ""                        #ID of the route
        self.Mode = ""                      #ID of the route
        self.ResPath = []                   #List of ID of the successive reservoirs of the route
        self.NodePath = []                  #List of ID of the successive macroscopic nodes of the route
        self.TripLengths = []               #List of trip lengths in the reservoirs crossed by the current route

        #Both Solvers
        self.ResOriginID = ""               #Origin reservoir
        self.ResDestinationID = ""          #Destination reservoir
        self.ResPathID = ""                 #
        self.NodeOriginID = ""              #Origin node
        self.NodeDestinationID = ""         #Destination node
        self.Length = []                    #Length in the successive reservoirs
        self.TotalTime = 0                  #Route free-flow travel time
        self.FreeFlowTravelTime = []        #
        self.OldTT = 0                      #?
        self.ResRouteIndex = []             #
        self.TravelTime = []                #Route experienced travel time at each time step
        self.Demand = []                    #Route demand at each time step (utile ?)
        self.NVehicles = 0                  #Number of vehicles created during simulation to travel on the route

        #Trip-based solver
        self.EntryTimes = []                #
        self.EntryPurpose = []              #
        self.PrevDemandTime = 0             #
        self.PrevDemandData = 0             #
        self.NumEntryTimes = []             #
        self.TravelTime2 = []               #
