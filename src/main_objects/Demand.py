# Demand per origin and destination macronode

import pandas

from main_objects import MacroNode
from main_objects import Route

class FlowDemand:
    def __init__(self):
        self.OriginMacroNode = ""                       # Macronode of origin
        self.DestMacroNode = ""                         # Macronode of destination
        self.Demands = pandas.DataFrame()               # Values of demand veh/s (may be dynamic)
        self.RouteAssignments = pandas.DataFrame()      # Assignment coeff per route (may be dynamic)
        
    def load_input(self, load_demand, i, macronodes):
        flow_demand = load_demand["FLOW DEMAND"][i]

        self.OriginMacroNode = MacroNode.get_macronode(macronodes, flow_demand["OriginMacroNodeID"])
        self.DestMacroNode = MacroNode.get_macronode(macronodes, flow_demand["DestMacroNodeID"])
        
        self.Demands = pandas.DataFrame.from_dict(flow_demand["Demand"])
        self.Demands.set_index('Time')

        self.RouteAssignments = pandas.DataFrame.from_dict(flow_demand["Route"])
        self.RouteAssignments.set_index('Time')
        
    def get_levelofdemand(self, time):
        return float(self.Demands.loc[self.Demands['Time']<=time].tail(1)['Data'].iloc[0])
    
    def get_assignmentcoefficient(self, route_id, time):
        data = self.RouteAssignments.loc[self.RouteAssignments['Time']<=1].tail(1)['Data'].iloc[0]
        for d in range(len(data)):
            if data[d]['ID'] == route_id:
                return data[d]['Coeff']
        
        return 0
        
        
class DiscreteDemand:
    def __init__(self):
        self.TripID = ""                        #ID of the trip
        self.OriginMacroNode = ""               #ID of macronode of origin
        self.DestMacroNode = ""                 #ID of macronode of destination
        self.Mode = ""                          #Used mode of the trip
        self.Time = 0                           #Time at which the simulation starts
        self.Route = ""                         #ID of route used
        self.PrevTripID = ""                    #ID of previous trip

    def load_input(self, load_demand, i, routes, macronodes):
        micro_demand = load_demand["MICRO"][i]

        self.TripID = micro_demand["TripID"]

        self.OriginMacroNode = MacroNode.get_macronode(macronodes, micro_demand["OriginMacroNodeID"])
        self.DestMacroNode = MacroNode.get_macronode(macronodes, micro_demand["DestMacroNodeID"])
        
        self.Mode = micro_demand["Mode"]
        self.Time = micro_demand["Time"]
        self.Route = Route.get_route(routes, micro_demand["RouteID"])

        if 'PrevTripID' in micro_demand:
            self.PrevTripID = micro_demand["PrevTripID"]
            
def get_partial_demand(GlobalDemand, RouteSection, t):
    if RouteSection.EntryNode.Type != 'externalentry' and RouteSection.EntryNode.Type != 'origin':
        return 0.
    
    if type(GlobalDemand[0]) is FlowDemand:
        for d in range(len(GlobalDemand)):
            if GlobalDemand[d].OriginMacroNode == RouteSection.EntryNode and GlobalDemand[d].DestMacroNode == RouteSection.Route.DestMacroNode:
                levelofdemand = GlobalDemand[d].get_levelofdemand(t)
                coeff = GlobalDemand[d].get_assignmentcoefficient(RouteSection.Route.ID, t)
                return levelofdemand*coeff
        return 0.
    else:
        next_t = get_next_trip_from_origin(GlobalDemand,RouteSection.EntryNode.ID,t)
        prev_t = get_previous_trip_from_origin(GlobalDemand,RouteSection.EntryNode.ID,t)
        
        return 1. / (next_t-prev_t) 
        
def get_next_trip(global_demand, t):
    # To improve ?
    if global_demand[0] is DiscreteDemand:
        for trip in global_demand:
            if trip.Time > t:
                return trip
        
def get_next_trip_from_origin(global_demand, originID, t):
    if global_demand[0] is DiscreteDemand:
        for trip in global_demand:
            if trip.Time > t and trip.OriginMacroNodeID == originID:
                return trip
        
    return float('inf')
        
def get_previous_trip_from_origin(global_demand, originID, t):
    if global_demand[0] is DiscreteDemand:
        for trip in reversed(global_demand):
            if trip.Time < t and trip.OriginMacroNodeID == originID:
                return trip
    
    return 0.
