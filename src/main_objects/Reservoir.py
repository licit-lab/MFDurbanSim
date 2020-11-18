import copy
from main_objects.Element import Element


def get_reservoir(reservoirs, reservoir_id):
    
    for r in reservoirs:
        if r.ID == reservoir_id:
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
        
        # Input
        self.ID = ""                        #ID of the reservoir
        
        self.MFDsetting = []                # Setting of the MFD by mode (mode, free flow speed, max production, max accumulation)
      
        self.Centroid = None                # Abscissa and ordinate of reservoir center (plotting purpose)
        self.BorderPoints = None            # List of abscissa and ordinates of the N points delimiting the reservoir (plotting purpose)

        # Both solvers
        self.MFDfctParam = []               # Parameters of the MFD function
        self.EntryfctParam = []             # Parameters of the entry supply function
        self.MacroNodes = []                # List of the MacroNodes in the reservoir
        self.AdjacentResID = []             # List of adjacent reservoirs
        
        self.RouteSections = []             # List of all "per route" data

        # Useful variables
        self.NumberOfExtRouteSection = 1    # route section number whose origin of the section is an external entry
        
        # Acc-based solver
        # to keep ?
        self.NumWaitingVeh = []             # Number of vehicles waiting to enter the reservoir when reservoir is the begining of the route

        # Trip-based solver
        self.t_in = -1
        self.t_out = -1
        
        # to keep 
        self.MFDpts = []                    #
        self.EntryFctpts = []               #
        self.VehList = []                   # List of vehicles in the reservoir

    def load_input(self, load_network, i):
        self.ID = load_network["RESERVOIRS"][i]["ID"]
        
        MFDs = {}
        
        for m in load_network["RESERVOIRS"][i]["FreeflowSpeed"]:
            MFDs['mode'] = m['mode']
            MFDs['FreeflowSpeed'] = m['value']
            MFDs['MaxProd'] = [tag for tag in load_network["RESERVOIRS"][i]["MaxProd"] if tag['mode']=='VL'][0]['value']
            MFDs['MaxAcc'] = [tag for tag in load_network["RESERVOIRS"][i]["MaxAcc"] if tag['mode']=='VL'][0]['value']
            MFDs['CritAcc'] = [tag for tag in load_network["RESERVOIRS"][i]["CritAcc"] if tag['mode']=='VL'][0]['value']
           
        self.MFDsetting.append(MFDs)
        
        if 'Centroid' in load_network["RESERVOIRS"][i]:
            self.Centroid = load_network["RESERVOIRS"][i]["Centroid"]
            
        if 'BorderPoints' in load_network["RESERVOIRS"][i]:
            self.BorderPoints = load_network["RESERVOIRS"][i]["BorderPoints"]


    def get_production_from_accumulation(self, n, mode):
        
        # nj = param(1); % jam accumulation (max. accumulation) [veh]
        # nc = param(2); % critical accumulation [veh]
        # Pc = param(3); % critical production (max. production) [veh.m/s]
        
        # P = (0 <= n).*(n <= nc).* (Pc./nc.^2.*n.*(2*nc - n)) + ...
        #     (nc < n).*(n < nj).*  (Pc./(nj - nc).^2.*(nj - n).*(nj + n - 2*nc));
                
        MFDset = [tag for tag in self.MFDsetting if tag['mode'] == mode][0]
        
        production = (0<=n)*(n<=MFDset['CritAcc'])*(MFDset['MaxProd']/(MFDset['CritAcc']**2)*n*(2*MFDset['CritAcc']-n)) + \
                    (MFDset['CritAcc']<n)*(n<MFDset['MaxAcc'])*(MFDset['MaxProd']/(MFDset['MaxAcc']-MFDset['CritAcc'])**2*(MFDset['MaxAcc']-n)*(MFDset['MaxAcc']+n-2*MFDset['CritAcc']))
        
        # if accumulation>= MFDset['MaxAcc'] or accumulation<=0.:
        #     return 0.
        
        # a = MFDset['MaxProd'] / (MFDset['CritAcc']*(MFDset['CritAcc']-MFDset['MaxAcc']))
        # b = -a * MFDset['MaxAcc']
        # c = 0
        # return ( (a*accumulation**2) + (b*accumulation) + c)
    
        return production
    
    def get_speed_from_accumulation(self, accumulation, mode):
        MFDset = [tag for tag in self.MFDsetting if tag['mode']==mode][0]
        
        if accumulation>0:
            production = self.get_production_from_accumulation(accumulation,mode)
            return production / accumulation
        
        return MFDset['FreeflowSpeed']


    def get_MFD_setting(self, data, mode):
        MFDset = [tag for tag in self.MFDsetting if tag['mode']==mode][0]
        return MFDset[data]
        
    def get_entry_supply_from_accumulation(self, accumulation, mode):
        
        MFDset = [tag for tag in self.MFDsetting if tag['mode'] == mode][0]
        a1 = 0.8
        a2 = 1
        b = 1
        param=[ MFDset['MaxAcc'], MFDset['CritAcc'], MFDset['MaxProd'], a1*MFDset['CritAcc'], a2*MFDset['CritAcc'], b*MFDset['MaxProd'] ]
        
        entry_supply =  (accumulation <= param[3]) * param[5] + \
                        (param[3]< accumulation)*(accumulation<=param[4]) * \
                        (param[5]+(accumulation-param[3])/(param[4]-param[3])*(self.get_production_from_accumulation(a2*MFDset['CritAcc'], mode)-param[5])) + \
                        (param[4]< accumulation)*self.get_production_from_accumulation(accumulation, mode)
            
        
        # % Entry supply function
        # % param = [nj nc Pc a1*nc a2*nc b*Pc], with 0 < a1 < 1 < a2, and 1 < b
        # Entryfct = @(n,param) (n <= param(4)).*param(6) + ...
        # (param(4) < n).*(n <= param(5)).*(param(6)+(n-param(4))./(param(5)-param(4)).*(MFDfct(param(5),param(1:3))-param(6))) + ...
        # (param(5) < n).*MFDfct(n,param(1:3));
        
        return entry_supply
