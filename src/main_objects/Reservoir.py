import copy
from main_objects.Element import Element


def get_reservoir(reservoirs,reservoir_id):
    
    for r in reservoirs:
        if r.ID==reservoir_id:
            return r
        
    return None

class Reservoir(Element):
    
    def __init__(self):
        
        DataKeys = [
                            "Time",           
                            
                            # Accumulation based model
                            "InternalProd", 
                            "MeanSpeed", 
                            "AvgTripLength",      # average trip length (m) corresponding to the routes orignating outside reservoir only
                            "Acc",                # accumulation (veh)
                            "ProductionSupply",   # modified entry production supply (veh.m/s)
                            "Inflow",
                            "Outflow", 
                            "Nin", 
                            "Nout",
                            "MeanSpeed"
                            
                            # Trip based model
                            #"PossibleNextEntryTime"
                            #"PossibleNextExitTime"
                            #"TotalTraveledDistance"
                            
                            
                            ]
        
        Element.__init__(self, DataKeys)
        
        #Input
        self.ID = ""                        #ID of the reservoir
        
        self.MFDsetting = []                # Setting of the MFD (mode, free flow speed, max production, max accumulation)
      
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
        # to keep ?
        self.NumWaitingVeh = []             #Number of vehicles waiting to enter the reservoir when reservoir is the begining of the route

        #Trip-based solver
        self.t_in = -1
        self.t_out = -1
        
        # to keep 
        self.MFDpts = []                    #
        self.EntryFctpts = []               #
        self.VehList = []                   #List of vehicles in the reservoir

    def load_input(self, loadNetwork, i):               
        self.ID = loadNetwork["RESERVOIRS"][i]["ID"]
        
        MFDs = {}
        
        for m in loadNetwork["RESERVOIRS"][i]["FreeflowSpeed"]:
            MFDs['mode']=m['mode']
            MFDs['FreeflowSpeed']=m['value']
            MFDs['MaxProd'] = [tag for tag in loadNetwork["RESERVOIRS"][i]["MaxProd"] if tag['mode']=='VL'][0]['value']
            MFDs['MaxAcc'] = [tag for tag in loadNetwork["RESERVOIRS"][i]["MaxAcc"] if tag['mode']=='VL'][0]['value']
            MFDs['CritAcc'] = [tag for tag in loadNetwork["RESERVOIRS"][i]["CritAcc"] if tag['mode']=='VL'][0]['value']
           
        self.MFDsetting.append(MFDs)
        
        if 'Centroid' in loadNetwork["RESERVOIRS"][i]:
            self.Centroid = loadNetwork["RESERVOIRS"][i]["Centroid"]
            
        if 'BorderPoints' in loadNetwork["RESERVOIRS"][i]:
            self.BorderPoints = loadNetwork["RESERVOIRS"][i]["BorderPoints"]

    # def init_fct_param(self, EntryCoeff4, EntryCoeff5, EntryCoeff6, numModes):
    #     self.MFDfctParam = [self.MaxAcc, self.CritAcc, self.MaxProd]

    #     coeff4 = copy.deepcopy(self.CritAcc)
    #     coeff5 = copy.deepcopy(self.CritAcc)
    #     coeff6 = copy.deepcopy(self.MaxProd)
    #     for i in range(numModes):
    #         coeff4[i]["value"] *= EntryCoeff4
    #         coeff5[i]["value"] *= EntryCoeff5
    #         coeff6[i]["value"] *= EntryCoeff6

    #     self.EntryfctParam = [self.MaxAcc, self.CritAcc, self.MaxProd, coeff4, coeff5, coeff6]
        
    def get_entry_supply(self, accumulation, mode):
        
        # self.EntryfctParam = []             #Parameters of the entry supply function
# % Entry supply function
# % param = [nj nc Pc a1*nc a2*nc b*Pc], with 0 < a1 < 1 < a2, and 1 < b
    #     Entryfct = @(n,param) (n <= param(4)).*param(6) + ...
    # (param(4) < n).*(n <= param(5)).*(param(6)+(n-param(4))./(param(5)-param(4)).*(MFDfct(param(5),param(1:3))-param(6))) + ...
    # (param(5) < n).*MFDfct(n,param(1:3));

        
        entry_supply=0
        return entry_supply
    
    def get_production_from_accumulation(self, accumulation, mode):
        MFDset = [tag for tag in self.MFDsetting if tag['mode']==mode][0]
        return MFDset['MaxAcc']*accumulation**2 + MFDset['CritAcc']*accumulation + MFDset['MaxProd']
    
    def get_speed_from_accumulation(self, accumulation, mode):
        MFDset = [tag for tag in self.MFDsetting if tag['mode']==mode][0]
        production = self.get_production_from_accumulation(accumulation,mode)
        
        if production>0:
            return accumulation / production
        
        return MFDset['FreeflowSpeed']
         
    def get_MFD_setting(self, data, mode):
        MFDset = [tag for tag in self.MFDsetting if tag['mode']==mode][0]
        return MFDset[data]
        
