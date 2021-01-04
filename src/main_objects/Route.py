import pandas
from main_objects import MacroNode, Reservoir
from main_objects.FlowElement import FlowElement


def get_route(routes, route_id):
    for r in routes:
        if r.ID == route_id:
            return r
        
    return None


class Route(FlowElement):
    def __init__(self):
        # Input
        self.ID = ""                        # ID of the route
        self.Mode = ""                      # Mode of the route
        self.CrossedReservoirs = []         # List of the successive reservoirs of the route
        self.RouteSections = []             # List of the successive route sections
        self.TripLengths = []               # List of the successive trip lengths of the route
        
        self.NodePath = []                  # List of the successive macroscopic nodes of the route
        
        self.Demand = pandas.DataFrame()    # Demand 
        
        # Both Solvers
        self.ResOriginID = ""               # Origin reservoir
        self.ResDestinationID = ""          # Destination reservoir
        self.OriginMacroNode = 0            # Origin macro-node
        self.DestMacroNode = 0              # Destination macro-node
        self.Length = 0                     # Total length in the successive reservoirs
        self.TotalTime = 0                  # Route free-flow travel time
        self.FreeFlowTravelTime = []        #
        self.OldTT = 0                      # ?
        self.TravelTime = []                # Route experienced travel time at each time step

        self.NVehicles = 0                  # Number of vehicles created during simulation to travel on the route

        # Trip-based solver
        self.EntryTimes = []                #
        self.EntryPurpose = []              #
        self.PrevDemandTime = 0             #
        self.PrevDemandData = 0             #
        self.NumEntryTimes = []             #
        self.TravelTime2 = []               #
        
        # Dynamic variables
        self.data_keys = [
                     "TravelTime"]

        


    def load_input(self, load_network, i, reservoirs, macronodes):
        load_route = load_network["ROUTES"][i]

        self.ID = load_route["ID"]
        self.Mode = load_route["Mode"]
        
        reservoirs_data = load_route["ResPath"]
        for rd in reservoirs_data:
            self.CrossedReservoirs.append(Reservoir.get_reservoir(reservoirs, rd['ID']))
            self.TripLengths.append(rd['TripLength'])
        
        node_id_path = load_route["NodePath"]
        for nid in node_id_path:
            self.NodePath.append(MacroNode.get_macronode(macronodes, nid))

        if self.CrossedReservoirs[0] is None:
            self.ResOriginID = None
        else:
            self.ResOriginID = self.CrossedReservoirs[0].ID

        if self.CrossedReservoirs[-1] is None:
            self.ResDestinationID = None
        else:
            self.ResDestinationID = self.CrossedReservoirs[-1].ID

        if self.NodePath[0] is None:
            self.OriginMacroNode = None
        else:
            self.OriginMacroNode = self.NodePath[0]

        if self.NodePath[-1] is None:
            self.DestMacroNode = None
        else:
            self.DestMacroNode = self.NodePath[-1]
        
        self.Length = sum(self.TripLengths)
        
        FlowElement.__init__(self, self.data_keys,[self.Mode])


    def get_demand(self, time):
        return self.Demand.loc[:time].tail(1)
