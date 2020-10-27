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
        self.Mode = ""                           #Used mode of the trip
        self.Time = 0                          #Time at which the simulation starts
        self.RouteID = ""                      #ID of route used
        self.PrevTripID = ""                   #ID of previous trip

    def load_input(self, loadDemand, i):
        self.TripID = loadDemand["MICRO"][i]["TripID"]                        
        self.OriginMacroNodeID = loadDemand["MICRO"][i]["OriginMacroNodeID"]            
        self.DestMacroNodeID = loadDemand["MICRO"][i]["DestMacroNodeID"]            
        self.Mode = loadDemand["MICRO"][i]["Mode"]
        self.Time = loadDemand["MICRO"][i]["Time"]                           
        self.RouteID = loadDemand["MICRO"][i]["RouteID"]    

        if 'PrevTripID' in loadDemand["MICRO"][i]:                   
            self.PrevTripID = loadDemand["MICRO"][i]["PrevTripID"]   
            
def get_partial_demand(GlobalDemand, RouteSection, t):
    if RouteSection.EntryNode.Type != 'externalentry':
        return 0
    
    if GlobalDemand[0] is FlowDemand:
        for d in GlobalDemand:
            if GlobalDemand[d].OriginMacroNodeID == RouteSection.EntryNode and GlobalDemand[d].DestMacroNodeID == RouteSection.EntryNode:
                levelofdemand = GlobalDemand[d].get_levelofdemand(t)
                coeff = GlobalDemand[d].get_assignmentcoefficient(RouteSection.Route.ID, t)
                return levelofdemand*coeff
    else:
        next_t = get_next_trip_from_origin(GlobalDemand,RouteSection.EntryNode.ID,t)
        prev_t = get_previous_trip_from_origin(GlobalDemand,RouteSection.EntryNode.ID,t)
        
        return 1. / (next_t-prev_t) 
        
def get_next_trip(GlobalDemand,t):
    # To improve ?
    if GlobalDemand[0] is DiscreteDemand:
        for trip in GlobalDemand:
            if trip.Time > t:
                return trip
        
def get_next_trip_from_origin(GlobalDemand, originID, t):
    if GlobalDemand[0] is DiscreteDemand:
        for trip in GlobalDemand:
            if trip.Time > t and trip.OriginMacroNodeID == originID:
                return trip
        
    return float('inf')
        
def get_previous_trip_from_origin(GlobalDemand,originID,t):
    if GlobalDemand[0] is DiscreteDemand:
        for trip in reversed(GlobalDemand):
            if trip.Time < t and trip.OriginMacroNodeID == originID:
                return trip
    
    return 0.