from datetime import date, time, datetime

class Simulation:
     def __init__(self):
         self.Network = ""              #Name of the network file to load
         self.Demand = ""               #Name of the demand file to load
         self.Solver = ""               #Solver used: Acc-based or Trip-based
         self.Name = ""                 #Name of the current simulation
         self.Duration = 0              #Simulation duration
         self.TimeStep = 0              #Simulation time step
         self.MergeModel = ""           #Inflow merging model
         self.DivergeModel = ""         #Outflow diverging model
         self.MFDtype = ""              #Type of MFD function used
         self.Modes = []                #Modes used
         self.DemandType = ""           #Demand type: FlowDemand or DiscreteDemand

         self.Date = 0                  #Date time
         self.Version = ""              #Version used
         
     def load_input(self, loadSimulation):      
          self.Network = loadSimulation["SIMULATION"][0]["Network"]
          self.Demand = loadSimulation["SIMULATION"][0]["Demand"]
          self.Solver = loadSimulation["SIMULATION"][0]["Solver"]
          self.Name = loadSimulation["SIMULATION"][0]["Name"]
          self.Duration = loadSimulation["SIMULATION"][0]["Duration"]
          self.TimeStep = loadSimulation["SIMULATION"][0]["TimeStep"]
          self.MergeModel = loadSimulation["SIMULATION"][0]["MergeModel"]
          self.DivergeModel = loadSimulation["SIMULATION"][0]["DivergeModel"]
          self.MFDType = loadSimulation["SIMULATION"][0]["MFDType"]
          self.Modes = loadSimulation["SIMULATION"][0]["Modes"]
          self.DemandType = loadSimulation["SIMULATION"][0]["DemandType"]
          
          self.Date = datetime.now().isocalendar()
          self.Version = "0.1"
