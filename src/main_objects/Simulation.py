import os

from datetime import date, time, datetime

class Simulation:
    mfd_type_list = ("parabolic")
    modes_list = ("VL", "BUS")
    demand_type_list = ("DiscreteDemand", "FlowDemand")
    solvers_list = ("AccBased", "TripBased")
    merge_models_list = ("demprorata", "endogenous", "equiproba", "demandfifo")
    diverge_models_list = ("maxdem", "decrdem", "queuedyn")
    
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
        self.DemandType = ""           #Demand type: flow or micro

        self.Date = 0                  #Date time
        self.Version = ""              #Version used
         
    def load_input(self, loadSimulation, path):    
        simu = loadSimulation["SIMULATION"][0]
         
        self.Name = simu["Name"]
        
        path_network =  os.path.join(path, simu["Network"])
        path_demand =  os.path.join(path, simu["Demand"])

        if os.path.lexists(path_network):
            self.Network = simu["Network"]
        else:
            print("Network.json doesn't exist.")

        if os.path.lexists(path_demand):
            self.Demand = simu["Demand"]
        else:
            print("Demand.json doesn't exist.")

        if simu["Solver"] in self.solvers_list:
            self.Solver = simu["Solver"]
        else:
            print("Solver unknown, please change the input file entry Solver.")
        
        if simu["Duration"] > 0:
            self.Duration = simu["Duration"]
        else:
            print("Simulation duration is negative or equals to 0, please change the input file entry Duration.")
          
        if self.Solver == 'AccBased':
            self.TimeStep = simu["TimeStep"]
        
        if simu["MergeModel"] in self.merge_models_list:
            self.MergeModel = simu["MergeModel"]
        else:
            print("Merge model unknown, please change the input file entry MergeModel.")

        if simu["DivergeModel"] in self.diverge_models_list:
            self.DivergeModel = simu["DivergeModel"]
        else:
            print("Diverge model unknown, please change the input file entry DivergeModel.")

        if simu["MFDType"] in self.mfd_type_list:
            self.MFDType = simu["MFDType"]
        else:
            print("MFD type unknown, please change the input file entry MFDType.")

        for modes in simu["Modes"]:
            if modes["ID"] in self.modes_list:
                self.Modes = simu["Modes"]
            else:
                print("Mode unknown, please change the input file entry Modes.")

        if simu["DemandType"] in self.demand_type_list:
            self.DemandType = simu["DemandType"]
        else:
            print("Demand type unknown, please change the input file entry DemandType.")
          
        self.Date = datetime.now().isocalendar()
        self.Version = "0.1"
