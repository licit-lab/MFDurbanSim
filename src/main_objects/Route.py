import pandas
from main_objects import MacroNode

class Route:
    def __init__(self):

        #Input
        self.ID = ""                        #ID of the route
        self.Mode = ""                      #Mode of the route
        self.CrossedReservoirs = []         #List of ID of the successive reservoirs of the route associated with trip lengths
        self.NodePath = []                  #List of ID of the successive macroscopic nodes of the route
        
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

    def load_input(self, loadNetwork, i):               
        
        self.ID = loadNetwork["ROUTES"][i]["ID"]
        self.Mode = loadNetwork["ROUTES"][i]["Mode"]
        self.CrossedReservoirs = loadNetwork["ROUTES"][i]["ResPath"]
        self.NodePath = loadNetwork["ROUTES"][i]["NodePath"]

        self.ResOriginID = self.CrossedReservoirs[0]["ID"]
        self.ResDestinationID = self.CrossedReservoirs[len(self.CrossedReservoirs) - 1]["ID"]
        self.OriginMacroNode = MacroNode.get_macronode(self.NodePath[0])
        self.DestMacroNode = MacroNode.get_macronode(self.NodePath[len(self.NodePath) - 1])
        for i in range(len(self.CrossedReservoirs)):
            self.Length += self.CrossedReservoirs[i]["TripLength"]
            
    def get_demand(self, time):
        return self.Demand.loc[:time].tail(1)



        
 
