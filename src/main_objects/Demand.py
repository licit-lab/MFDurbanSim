# Demand per origin and destination macronode

import pandas

class FlowDemand:
    def __init__(self):
        self.OriginMacroNodeID = ""            #ID of macronode of origin
        self.DestMacroNodeID = ""              #ID of macronode of destination
        self.Demands = pandas.DataFrame()      # Values of demand veh/s (may be dynamic)
        self.RouteAssignments = pandas.DataFrame()      # Assignment coeff per route (may be dynamic)
        
    def load_input(self, loadDemand, i):
        self.OriginMacroNodeID = loadDemand["FLOW DEMAND"][i]["OriginMacroNodeID"]
        self.DestMacroNodeID = loadDemand["FLOW DEMAND"][i]["DestMacroNodeID"]
        
        self.Demands=pandas.DataFrame.from_dict(loadDemand["FLOW DEMAND"][i]["Demand"])
        self.Demands.set_index('Time')
        
        self.RouteAssignments=pandas.DataFrame.from_dict(loadDemand["FLOW DEMAND"][i]["Route"])
        self.RouteAssignments.set_index('Time')
        
    def get_levelofdemand(self, time):
        return float(self.Demands.loc[:time].tail(1)['Data'].iloc[0])
    
    def get_assignmentcoefficient(self, routeID, time):
        data = self.RouteAssignments.loc[:time].tail(1)['Data'].iloc[0]
        for d in range(len(data)):
            if data[d]['ID'] == routeID:
                return data[d]['Coeff']
        
        return 0
        
        
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

def get_partial_demand(GlobalDemand, RouteSection, t):
    
    if RouteSection.EntryNode['Type'] != 'externalentry':
        return 0
    
    for d in GlobalDemand:
        if GlobalDemand[d].OriginMacroNodeID == RouteSection.EntryNode and GlobalDemand[d].DestMacroNodeID == RouteSection.EntryNode:
            levelofdemand = GlobalDemand[d].get_levelofdemand(t)
            coeff = GlobalDemand[d].get_assignmentcoefficient(RouteSection.Route.ID, t)
            return levelofdemand*coeff