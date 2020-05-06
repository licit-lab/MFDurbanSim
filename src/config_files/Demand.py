import json

class FlowDemand:
     def __init__(self):
             self.OriginMacroNodeID = "MacroNode1"
             self.DestMacroNodeID = "MacroNode6"
             self.Demand = [{"Time":0, "Data":10}, {"Time":5, "Data":8}, {"Time":10, "Data":7}]
             self.Route = [{"Time":0, "Data":[{"ID":"Route3", "Coeff":0.3},
                                              {"ID":"Route3", "Coeff":0.7}]},
                           {"Time":50, "Data":[{"ID":"Route3", "Coeff":0.2},
                                              {"ID":"Route3", "Coeff":0.8}]}
                           ]
             
class DiscreteDemand:
     def __init__(self):
             self.TripID = "Trip1"
             self.OriginMacroNodeID = "MacroNode1"
             self.DestMacroNodeID = "MacroNode6"
             self.Time = 0
             self.RouteID = "Route2"
             self.PrevTripID = "Trip0"
             

flow1 = FlowDemand()
discrete1 = DiscreteDemand()

Demand = {"FLOW DEMAND":[flow1.__dict__], "DISCRETE DEMAND":[discrete1.__dict__]}

with open("Demand.json", "w") as fichier:
    json.dump(Demand, fichier, indent = 4)
  
