from main_objects.Element import Element


def get_reservoir(reservoirs, reservoir_id):
    for r in reservoirs:
        if r.ID == reservoir_id:
            return r
        
    return None


class Reservoir(Element):
    def __init__(self):
        data_keys = ["Time",
                            
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
                     "MeanSpeed",
                     "Demand"
                            
                     # Trip based model
                     # "PossibleNextEntryTime"
                     # "PossibleNextExitTime"
                     # "TotalTraveledDistance"

                     ]
        
        Element.__init__(self, data_keys)
        
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

    def load_input(self, load_network, i, mfd_type=None):
        load_res = load_network["RESERVOIRS"][i]
        self.ID = load_res["ID"]

        for m in load_res["FreeflowSpeed"]:
            mfd_set = {'mode': m['mode'], 'FreeflowSpeed': m['value'],
                       'MaxProd': [tag for tag in load_res["MaxProd"] if tag['mode'] == 'VL'][0]['value'],
                       'MaxAcc': [tag for tag in load_res["MaxAcc"] if tag['mode'] == 'VL'][0]['value'],
                       'CritAcc': [tag for tag in load_res["CritAcc"] if tag['mode'] == m['mode']][0]['value']}
            self.MFDsetting.append(mfd_set)
        
        if 'Centroid' in load_res:
            self.Centroid = load_res["Centroid"]
            
        if 'BorderPoints' in load_res:
            self.BorderPoints = load_res["BorderPoints"]

        if mfd_type == '3dmfd':
            if 'ParamBusOnCar' in load_res and 'ParamCarOnBus' in load_res and 'ParamBusOnBus' in load_res:
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
                eff_bc = load_res['ParamBusOnCar']
                # Marginal effect of cars on bus speed
                eff_cb = load_res['ParamCarOnBus'] * eff_cc
                # Marginal effect of buses on bus speed
                eff_bb = load_res['ParamBusOnBus'] * eff_bc

                self.MFDfctParam = [ffs_car, ffs_bus, eff_cc, eff_bc, eff_cb, eff_bb]
                self.MFDsetting[i_bus]['CritAcc'] = - ffs_car / (eff_bc + eff_cb)


    def get_production_from_accumulation(self, n, mode):
        mfd_set = [tag for tag in self.MFDsetting if tag['mode'] == mode][0]
        crit_acc = mfd_set['CritAcc']
        max_prod = mfd_set['MaxProd']
        max_acc = mfd_set['MaxAcc']

        production = (0 <= n) * (n <= crit_acc) * (max_prod / (crit_acc ** 2) * n * (2 * crit_acc - n)) + \
                     (crit_acc < n) * (n < max_acc) * (max_prod / (max_acc - crit_acc) ** 2 * (max_acc - n) *
                                                       (max_acc + n - 2 * crit_acc))

        return production


    def get_speed_from_accumulation(self, accumulation, mode):
        mfd_set = [tag for tag in self.MFDsetting if tag['mode'] == mode][0]
        
        if accumulation > 0:
            production = self.get_production_from_accumulation(accumulation, mode)
            return production / accumulation
        
        return mfd_set['FreeflowSpeed']


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
        
        entry_supply = (accumulation <= param[3]) * param[5] + \
                       (param[3] < accumulation) * (accumulation <= param[4]) * \
                       (param[5] + (accumulation-param[3]) / (param[4] - param[3]) *
                        (self.get_production_from_accumulation(a2 * mfd_set['CritAcc'], mode)-param[5])) + \
                       (param[4] < accumulation) * self.get_production_from_accumulation(accumulation, mode)

        return entry_supply
