class Route:
    def __init__(self):

        #Input
        self.ID = ""                        #ID of the route
        self.Mode = ""                      #Mode of the route
        self.ResPath = []                   #List of ID of the successive reservoirs of the route associated with trip lengths
        self.NodePath = []                  #List of ID of the successive macroscopic nodes of the route
        

        #Both Solvers
        self.ResOriginID = ""               #Origin reservoir
        self.ResDestinationID = ""          #Destination reservoir
        self.ResPathID = ""                 # utile ? 
        self.NodeOriginID = ""              #Origin node
        self.NodeDestinationID = ""         #Destination node
        self.Length = 0                     #Total length in the successive reservoirs
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

    def load_input(self, loadNetwork, i):               
        self.ID = loadNetwork["ROUTES"][i]["ID"]
        self.Mode = loadNetwork["ROUTES"][i]["Mode"]
        self.ResPath = loadNetwork["ROUTES"][i]["ResPath"]
        self.NodePath = loadNetwork["ROUTES"][i]["NodePath"]

        self.ResOriginID = self.ResPath[0]["ID"]
        self.ResDestinationID = self.ResPath[len(self.ResPath) - 1]["ID"]
        #self.ResPathID
        self.NodeOriginID = self.NodePath[0]
        self.NodeDestinationID = self.NodePath[len(self.NodePath) - 1]
        for i in range(len(self.ResPath)):
            self.Length += self.ResPath[i]["TripLength"]



        
 
