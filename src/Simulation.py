import json

class Simulation:
     def __init__(self):
         self.Network = ""              #Name of the network folder to simulate
         self.Solver = ""               #Solver used: Acc-based or Trip-based
         self.Name = ""                 #Name of the current simulation
         self.Duration = 0              #Simulation duration
         self.TimeStep = 0              #Simulation time step
         self.MergeModel = ""           #Inflow merging model
         self.DivergeModel = ""         #Outflow diverging model
         self.MFDtype = ""              #Type of MFD function used
         self.Modes = []                #Modes used
         self.DemandType = ""           #Demand type: FlowDemand or DiscreteDemand

     def load_input(self, filename):
          with open(filename, "r", encoding="utf-8") as file:
              loadSimulation = json.load(file)

          self.Network = loadSimulation["SIMULATION"][0]["Network"]
          self.Solver = loadSimulation["SIMULATION"][0]["Solver"]
          self.Name = loadSimulation["SIMULATION"][0]["Name"]
          self.Duration = loadSimulation["SIMULATION"][0]["Duration"]
          self.TimeStep = loadSimulation["SIMULATION"][0]["TimeStep"]
          self.MergeModel = loadSimulation["SIMULATION"][0]["MergeModel"]
          self.DivergeModel = loadSimulation["SIMULATION"][0]["DivergeModel"]
          self.MFDType = loadSimulation["SIMULATION"][0]["MFDType"]
          self.Modes = loadSimulation["SIMULATION"][0]["Modes"]
          self.DemandType = loadSimulation["SIMULATION"][0]["DemandType"]
          
