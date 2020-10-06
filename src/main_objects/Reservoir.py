import copy
from main_objects.Element import Element

def get_reservoir(reservoirs,reservoir_id):
    
    for r in reservoirs:
        if r.ID==reservoir_id:
            return r
        
    return 0

class Reservoir(Element):
    
    def __init__(self):
        
        DataKeys = [
                            "Time",           
                            "InternalProd", 
                            "MeanSpeed", 
                            "AvgTripLength",      # average trip length (m) corresponding to the routes orignating outside reservoir only
                            "Acc",                # accumulation (veh)
                            "ProductionSupply",   # modified entry production supply (veh.m/s)
                            "Inflow",
                            "Outflow", 
                            "Nin", 
                            "Nout"
                            ]
        
        Element.__init__(self, DataKeys)
        
        #Input
        self.ID = ""                        #ID of the reservoir
        self.FreeflowSpeed = []             #Free-flow speed in the reservoir per mode
        self.MaxProd = []                   #Reservoir maximum production per mode
        self.MaxAcc = []                    #Reservoir maximum accumulation per mode
        self.CritAcc = []                   #Reservoir critical accumulation per mode
        self.Centroid = []                  #Abscissa and ordinate of reservoir center (plotting purpose)
        self.BorderPoints = []              #List of abscissa and ordinates of the N points delimiting the reservoir (plotting purpose)

        #Both solvers
        self.MFDfctParam = []               #Parameters of the MFD function
        self.EntryfctParam = []             #Parameters of the entry supply function
        self.MacroNodes = []                #List of the MacroNodes in the reservoir
        self.AdjacentResID = []             #List of adjacent reservoirs
        
        self.RouteSections = []              #List of all "per route" data

        # Usefull variables
        self.NumberOfExtRouteSection = 0    # route section number whose origin of the section is an external entry
        
        #Acc-based solver
        self.NumWaitingVeh = []             #Number of vehicles waiting to enter the reservoir when reservoir is the begining of the route

        #Trip-based solver
        self.MFDpts = []                    #
        self.EntryFctpts = []               #
        self.VehList = []                   #List of vehicles in the reservoir

        self.LastEntryTime = 0              #
        self.LastExitTime = 0               #
        self.NextEntryTime = 0              #
        self.NextExitTime = 0               #
        self.NextEntryVehID = 0             #
        self.NextExitVehID = 0              #
        self.SupplyIndex = 0                # utile ? 
        self.DesiredExitTime = 0            #
        self.DesiredExitVeh = 0             #
        self.EntrySupplyTime = 0            #
        self.ExitSupplyTime = 0             #
        self.EntryTimes = []                #
        self.ExitTimes = []                 #
        self.CurrentMeanSpeed = 0           #
        self.MeanSpeed2 = []                #

    def load_input(self, loadNetwork, i):               
        self.ID = loadNetwork["RESERVOIRS"][i]["ID"]
        self.FreeflowSpeed = loadNetwork["RESERVOIRS"][i]["FreeflowSpeed"]
        self.MaxProd = loadNetwork["RESERVOIRS"][i]["MaxProd"]
        self.MaxAcc = loadNetwork["RESERVOIRS"][i]["MaxAcc"]
        self.CritAcc = loadNetwork["RESERVOIRS"][i]["CritAcc"]
        self.Centroid = loadNetwork["RESERVOIRS"][i]["Centroid"]
        self.BorderPoints = loadNetwork["RESERVOIRS"][i]["BorderPoints"]

    def init_fct_param(self, EntryCoeff4, EntryCoeff5, EntryCoeff6, numModes):
        self.MFDfctParam = [self.MaxAcc, self.CritAcc, self.MaxProd]

        coeff4 = copy.deepcopy(self.CritAcc)
        coeff5 = copy.deepcopy(self.CritAcc)
        coeff6 = copy.deepcopy(self.MaxProd)
        for i in range(numModes):
            coeff4[i]["value"] *= EntryCoeff4
            coeff5[i]["value"] *= EntryCoeff5
            coeff6[i]["value"] *= EntryCoeff6

        self.EntryfctParam = [self.MaxAcc, self.CritAcc, self.MaxProd, coeff4, coeff5, coeff6]
        
    def get_entry_supply(self, accumulation):
        
        # self.EntryfctParam = []             #Parameters of the entry supply function
# % Entry supply function
# % param = [nj nc Pc a1*nc a2*nc b*Pc], with 0 < a1 < 1 < a2, and 1 < b
    #     Entryfct = @(n,param) (n <= param(4)).*param(6) + ...
    # (param(4) < n).*(n <= param(5)).*(param(6)+(n-param(4))./(param(5)-param(4)).*(MFDfct(param(5),param(1:3))-param(6))) + ...
    # (param(5) < n).*MFDfct(n,param(1:3));

        
        entry_supply=0
        return entry_supply
        
