import json

class Reservoir:
     def __init__(self):
             self.ID = "Res1"
             self.FreeflowSpeed = [{"mode":"VL", "value":10},{"mode":"BUS", "value":15}]
             self.MaxProd = {"mode":"VL", "value":50},{"mode":"BUS", "value":25}
             self.MaxAcc = {"mode":"VL", "value":20},{"mode":"BUS", "value":10}
             self.CritAcc = [{"mode":"VL", "value":10},{"mode":"BUS", "value":5}]
             self.Centroid = [{"x":0, "y":0}]
             self.BorderPoints = [{"x":0, "y":0}, {"x":10, "y":10}, {"x":-10, "y":-10}, {"x":10, "y":-10}]

             
class MacroNode:
     def __init__(self):
             self.ID = "MacroNode1"
             self.Type = "origin"
             self.ResID = "Res1"
             self.Capacity = [{"Time":0, "Data":40}, {"Time":5, "Data":50}, {"Time":10, "Data":60}, {"Time":15, "Data":70}]
             self.Coord = [{"x":0, "y":0}]
             
class Route:
     def __init__(self):
             self.ID = "Route1"
             self.Mode = "car"
             self.ResPath = [{"ID":"Res1", "TripLength":1150}, {"ID":"Res2", "TripLength":560}]
             self.NodePath = ["MacroNode3", "MacroNode4", "MacroNode5"]

reservoir1 = Reservoir()
macronode1 = MacroNode()
route1 = Route()



with open("Network.json", "w") as fichier:
    json.dump({"RESERVOIRS":[reservoir1.__dict__], "MACRONODES":[macronode1.__dict__], "ROUTES":[route1.__dict__]}, fichier, indent = 4)

