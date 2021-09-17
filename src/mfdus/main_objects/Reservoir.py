from mfdus.main_objects.FlowElement import FlowElement


def get_reservoir(reservoirs, reservoir_id):
    for r in reservoirs:
        if r.ID == reservoir_id:
            return r
        
    return None


class Reservoir(FlowElement):
    
    def __init__(self, modes):
        data_keys = [   
                     # Accumulation based model
                     "InternalProd",
                     "MeanSpeed",
                     "AvgTripLength",      # average trip length (m) of routes originating outside reservoir only
                     "Acc",                # accumulation (veh)
                     "ProductionSupply",   # modified entry production supply (veh.m/s)
                     "Inflow",
                     "Outflow",
                     "Nin",
                     "Nout",
                     "Demand",
                     "Production"
                            
                     # Trip based model
                     # "PossibleNextEntryTime"
                     # "PossibleNextExitTime"
                     # "TotalTraveledDistance"

                     ]
        
        FlowElement.__init__(self, data_keys, modes)
        
        # Input
        self.ID = ""                        # ID of the reservoir
        
        self.MFDsetting = []                # MFD setting by mode (mode, free flow speed, max prod, max acc)
        
        # Plotting purpose
        self.Centroid = None                # Coordinates of reservoir center
        self.BorderPoints = None            # List of coordinates of the points delimiting the reservoir

        # Both solvers
        self.MFDfctParam = []               # Parameters of the MFD function
        self.EntryfctParam = []             # Parameters of the entry supply function
        self.MacroNodes = []                # List of the MacroNodes in the reservoir
        self.AdjacentResID = []             # List of adjacent reservoirs
        
        self.RouteSections = []             # List of all "per route" data

        # Useful variables
        self.NumberOfExtRouteSection = 0    # route section number whose origin of the section is an external entry
        
        # Acc-based solver
        # to keep ?
        self.NumWaitingVeh = []             # Number of vehicles waiting to enter the reservoir when reservoir is
                                            # the beginning of the route

        # Trip-based solver
        self.t_in = -1
        self.t_out = -1
        
        # to keep 
        self.MFDpts = []                    #
        self.EntryFctpts = []               #
        self.VehList = []                   # List of vehicles in the reservoir

    # Loading from input data
    def load_input(self, load_network, item, mfd_type=None):
        
        load_res = load_network["RESERVOIRS"][item]
        
        # ID
        self.ID = load_res["ID"]
        
        # Geographic coordinates
        if 'Centroid' in load_res:
            self.Centroid = load_res["Centroid"]
            
        if 'BorderPoints' in load_res:
            self.BorderPoints = load_res["BorderPoints"]

        # MFD setting
        for m in load_res["FreeflowSpeed"]:
            mfd_set = {'mode': m['mode'], 'FreeflowSpeed': m['value'],
                       'MaxProd': [tag for tag in load_res["MaxProd"] if tag['mode'] == 'VL'][0]['value'],
                       'MaxAcc': [tag for tag in load_res["MaxAcc"] if tag['mode'] == 'VL'][0]['value'],
                       'CritAcc': [tag for tag in load_res["CritAcc"] if tag['mode'] == m['mode']][0]['value']}
            self.MFDsetting.append(mfd_set)
        
        if mfd_type == '3d_parabolic':
            if 'MarginalEffect_Mode1onMode2' in load_res:
                me_bus_car = 0
                me_car_bus = 0
                me_bus_bus = 0
                for me in load_res['MarginalEffect_Mode1onMode2']:
                    if me['mode1'] == 'BUS' and me['mode2'] == 'VL':
                        me_bus_car = me['value']
                    elif me['mode1'] == 'VL' and me['mode2'] == 'BUS':
                        me_car_bus = me['value']
                    elif me['mode1'] == 'BUS' and me['mode2'] == 'BUS':
                        me_bus_bus = me['value']

                i_vl = 0
                i_bus = 0
                for i in range(len(self.MFDsetting)):
                    if self.MFDsetting[i]['mode'] == 'VL':
                        i_vl = i
                    elif self.MFDsetting[i]['mode'] == 'BUS':
                        i_bus = i

                # Free-flow speed of cars
                ffs_car = self.MFDsetting[i_vl]['FreeflowSpeed']
                # Free-flow speed of buses
                ffs_bus = self.MFDsetting[i_bus]['FreeflowSpeed']
                # Marginal effect of cars on car speed
                eff_cc = - self.MFDsetting[i_vl]['MaxProd'] / self.MFDsetting[i_vl]['CritAcc'] ** 2
                # Marginal effect of buses on car speed
                eff_bc = me_bus_car
                # Marginal effect of cars on bus speed
                eff_cb = me_car_bus * eff_cc
                # Marginal effect of buses on bus speed
                eff_bb = me_bus_bus * eff_bc

                self.MFDfctParam = [ffs_car, ffs_bus, eff_cc, eff_bc, eff_cb, eff_bb]



    def get_production_from_accumulation_by_mode(self, n, mode):
        
        mfd_set = [tag for tag in self.MFDsetting if tag['mode'] == mode][0]
        
        crit_acc = mfd_set['CritAcc']
        max_prod = mfd_set['MaxProd']
        max_acc = mfd_set['MaxAcc']
        
        production = (0 <= n) * (n <= crit_acc) * (max_prod / (crit_acc ** 2) * n * (2 * crit_acc - n)) + \
                         (crit_acc < n) * (n < max_acc) * (max_prod / (max_acc - crit_acc) ** 2 * (max_acc - n) *
                                                           (max_acc + n - 2 * crit_acc))

        return production

    # n and production output are a dictionnary (keys: mode)
    def get_production_from_accumulation(self, n):
        
        production=dict()
        for mode in n:
            production[mode]=self.get_production_from_accumulation_by_mode(n[mode],mode)
         
        return production 

    def get_speed_from_accumulation(self, n):
        
        speed = dict()
        
        for mode in n:
            
            mfd_set = [tag for tag in self.MFDsetting if tag['mode'] == mode][0]
        
            if n[mode] > 0:
                production = self.get_production_from_accumulation_by_mode(n[mode], mode)
                speed[mode] = production / n[mode]
            else:
                speed[mode] = mfd_set['FreeflowSpeed']
        
        return speed 


    def get_MFD_setting(self, data, mode):
        mfd_set = [tag for tag in self.MFDsetting if tag['mode'] == mode][0]
        return mfd_set[data]


    def get_entry_supply_from_accumulation(self, accumulation, mode):
        mfd_set = [tag for tag in self.MFDsetting if tag['mode'] == mode][0]

        a1 = 0.5
        a2 = 1.5
        b = 1.4
        
        param = [mfd_set['MaxAcc'], mfd_set['CritAcc'], mfd_set['MaxProd'],
                 a1 * mfd_set['CritAcc'], a2 * mfd_set['CritAcc'], b * mfd_set['MaxProd']]
        
        n = accumulation[mode]
        
        entry_supply = (n <= param[3]) * param[5] + \
                       (param[3] < n) * (n <= param[4]) * \
                       (param[5] + (n-param[3]) / (param[4] - param[3]) *
                        (self.get_production_from_accumulation_by_mode(a2 * mfd_set['CritAcc'], mode)-param[5])) + \
                       (param[4] < n) * self.get_production_from_accumulation_by_mode(n, mode)

        return entry_supply
