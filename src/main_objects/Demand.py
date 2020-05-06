class FlowDemand:
    def __init__(self):
        self.OriginMacroNodeID = ""            #ID of macronode of origin
        self.DestMacroNodeID = ""              #ID of macronode of destination
        self.Demand = []                       #Value of demand associated with the time of change
        self.Route = []                        #Assignment coeff per route

    def load_input(self, loadDemand):
        self.OriginMacroNodeID = loadDemand["FLOW DEMAND"][0]["OriginMacroNodeID"]
        self.DestMacroNodeID = loadDemand["FLOW DEMAND"][0]["DestMacroNodeID"]
        self.Demand = loadDemand["FLOW DEMAND"][0]["Demand"]
        self.Route = loadDemand["FLOW DEMAND"][0]["Route"]
        
class DiscreteDemand:
    def __init__(self):
        self.TripID = ""                       #ID of the trip
        self.OriginMacroNodeID = ""            #ID of macronode of origin
        self.DestMacroNodeID = ""              #ID of macronode of destination
        self.Time = 0                          #Time at which the simulation starts
        self.RouteID = ""                      #ID of route used
        self.PrevTripID = ""                   #ID of previous trip

    def load_input(self, loadDemand, i):
        self.TripID = loadDemand["DISCRETE DEMAND"][i]["TripID"]                        
        self.OriginMacroNodeID = loadDemand["DISCRETE DEMAND"][i]["OriginMacroNodeID"]            
        self.DestMacroNodeID = loadDemand["DISCRETE DEMAND"][i]["DestMacroNodeID"]               
        self.Time = loadDemand["DISCRETE DEMAND"][i]["Time"]                           
        self.RouteID = loadDemand["DISCRETE DEMAND"][i]["RouteID"]                       
        self.PrevTripID = loadDemand["DISCRETE DEMAND"][i]["PrevTripID"]   
