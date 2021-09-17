import json

class Simulation:
     def __init__(self):
             self.Network = "NetworkTest"
             self.Solver = "AccBased"
             self.Name = "SimulationTest"
             self.Duration = 5000;
             self.TimeStep = 10
             self.MergeModel = "demprorata"
             self.DivergeModel = "maxdem"
             self.Modes = [{"ID":"VL"}, {"ID":"BUS"}]
             self.DemandType = "FlowDemand"
             self.MFDType = "parabolic"
             

simulation1 = Simulation()

with open("Configuration.json", "w") as fichier:
    json.dump({"SIMULATION":[simulation1.__dict__]}, fichier, indent = 4, sort_keys = True)
