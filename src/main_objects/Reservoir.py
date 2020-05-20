import copy

class Reservoir:
    def __init__(self):
        
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
        self.MacroNodesID = []              #List of the MacroNodes in the reservoir
        self.AdjacentResID = []             #List of adjacent reservoirs
        self.TripLengthPerRoute = []        #Trip lengths of the routes crossing the reservoir associated 
        self.RoutesNodeID = []              #Entry & exit nodes ID for each route crossing the reservoir

        self.MergeCoeffPerRoute = []        #
        self.InternalProd = []              #
        self.ExitCoeffPerRoute = []         #
        self.MeanSpeed = []                 #Reservoir mean speed at each time step
        self.AvgTripLength = []             #Reservoir dynamic average trip length at each time step
        self.Acc = []                       #Reservoir total accumulation at each time step
        self.AccPerRoute = []               #Partial accumulation per route in RoutesID at each time step
        self.InflowPerRoute = []            #Partial inflow per route in RoutesID at each time step
        self.OutflowPerRoute = []           #Partial outflow per route in RoutesID at each time step
        self.NinPerRoute = []               #Partial entry cumulative count per route in RoutesID at each time step
        self.NoutPerRoute = []              #Partial exit cumulative count per route in RoutesID at each time step
        self.Inflow = []                    #Reservoir total inflow at each time step
        self.Outflow = []                   #Reservoir total outflow at each time step
        self.Nin = []                       #Reservoir entry cumulative count at each time step
        self.Nout = []                      #Reservoir exit cumulative count at each time step

        #Acc-based solver
        self.NumWaitingVeh = []             #Number of vehicles waiting to enter the reservoir when reservoir is the begining of the route
        self.InflowDemandPerRoute = []      #
        self.InflowSupplyPerRoute = []      #
        self.OutflowDemandPerRoute = []     #
        self.OutflowSupplyPerRoute = []     #
        self.AccCircuPerRoute = []          #Partial accumulation per route in RoutesID at each time step
        self.AccQueuePerRoute = []          #Partial queuing accumulation per route in RoutesID at each time step
        self.OutflowCircuPerRoute = []      #Partial circulation outflow per route in RoutesID at each time step
        self.NoutCircuPerRoute = []         #Partial exit cumulative count of the circulating outflow per route in RoutesID at each time step
    
        #Trip-based solver
        self.DemandEntryTimePerRoute = []   #
        self.DemandEntryVehPerRoute = []    #
        self.MFDpts = []                    #
        self.EntryFctpts = []               #
        self.VehList = []                   #List of vehicles in the reservoir
        self.VehListPerRoute = []           #List of vehicles per route
        self.DemandTimeIndexPerRoute= []    #
        self.LastEntryTime = 0              #
        self.LastExitTime = 0               #
        self.LastEntryTimePerRoute = []     #
        self.LastExitTimePerRoute = []      #
        self.NextEntryTime = 0              #
        self.NextExitTime = 0               #
        self.NextEntryVehID = 0             #
        self.NextExitVehID = 0              #
        self.SupplyIndex = 0                #
        self.DesiredEntryTimePerRoute = []  #
        self.DesiredExitTimePerRoute = []   #
        self.DesiredExitTime = 0            #
        self.DesiredEntryVehPerRoute = []   #
        self.DesiredExitVehPerRoute = []    #
        self.DesiredExitVeh = 0             #
        self.EntrySupplyTimePerRoute = []   #
        self.ExitSupplyTimePerRoute = []    #
        self.EntrySupplyTime = 0            #
        self.ExitSupplyTime = 0             #
        self.EntryTimes = []                #
        self.ExitTimes = []                 #
        self.EntryTimesPerRoute = []        #
        self.ExitTimesPerRoute = []         #
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
        

        
        
