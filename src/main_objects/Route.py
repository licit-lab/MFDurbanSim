import pandas
from main_objects import MacroNode, Reservoir
from main_objects.Element import Element

def get_route(routes,route_id):
    
    for r in routes:
        if r.ID==route_id:
            return r
        
    return 0

class Route(Element):
    def __init__(self):

        #Input
        self.ID = ""                        #ID of the route
        self.Mode = ""                      #Mode of the route
        self.CrossedReservoirs = []         #List of the successive reservoirs of the route
        self.RouteSections = []             #List of the successive route sections
        self.TripLengths = []               #List of the successive trip lengths of the route 
        
        self.NodePath = []                  #List of the successive macroscopic nodes of the route
        
        self.Demand = pandas.DataFrame()    # Demand 
        
        #Both Solvers
        self.ResOriginID = ""               #Origin reservoir
        self.ResDestinationID = ""          #Destination reservoir
        self.OriginMacroNode = 0               #Origin macro-node
        self.DestMacroNode = 0                  #Destination macro-node
        self.Length = 0                     #Total length in the successive reservoirs
        self.TotalTime = 0                  #Route free-flow travel time
        self.FreeFlowTravelTime = []        #
        self.OldTT = 0                      #?
        self.TravelTime = []                #Route experienced travel time at each time step

        self.NVehicles = 0                  #Number of vehicles created during simulation to travel on the route

        #Trip-based solver
        self.EntryTimes = []                #
        self.EntryPurpose = []              #
        self.PrevDemandTime = 0             #
        self.PrevDemandData = 0             #
        self.NumEntryTimes = []             #
        self.TravelTime2 = []               #
        
        ## Dynamic variables ##
        DataKeys = [ "Time", 
                    "TravelTime"
                    ]

    def load_input(self, loadNetwork, i, reservoirs, macronodes):               
        
        self.ID = loadNetwork["ROUTES"][i]["ID"]
        self.Mode = loadNetwork["ROUTES"][i]["Mode"]
        
        reservoirsData = loadNetwork["ROUTES"][i]["ResPath"]
        for rd in reservoirsData:
            self.CrossedReservoirs.append(Reservoir.get_reservoir(reservoirs,rd['ID']))
            self.TripLengths.append(rd['TripLength'])
        
        nodeIDpath = loadNetwork["ROUTES"][i]["NodePath"]
        for nid in nodeIDpath:
            self.NodePath.append(MacroNode.get_macronode(macronodes,nid))
            
        self.ResOriginID = self.CrossedReservoirs[0].ID
        self.ResDestinationID = self.CrossedReservoirs[len(self.CrossedReservoirs) - 1].ID
        
        self.OriginMacroNode = self.NodePath[0]
        self.DestMacroNode = self.NodePath[-1]
        
        self.Length = sum(self.TripLengths)
        
    def get_demand(self, time):
        return self.Demand.loc[:time].tail(1)



        
 
