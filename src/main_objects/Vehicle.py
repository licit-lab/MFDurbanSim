from main_objects import Route

def get_current_reservoir(vehicle):
    return vehicle.Path[vehicle.PathIndex]

class Vehicle:
    def __init__(self, Id, mode, routeID, creationtime, routes ):
        
        self.ID = Id                    #ID of the vehicle
        self.Mode = mode                  #Type of vehicle
        #self.CurrentRes = ""          #ID of the current reservoir the vehicle is in

        #Both solver
        self.RouteID = routeID                 #Route ID on which the vehicle is traveling
        self.CreationTime = creationtime           #Creation time of the vehicle
        
        self.TripLength = []            #List of trip lengths in the successive reservoirs
        self.TraveledDistance = []      #List of distances traveled by the vehicle in the successive reservoirs
        self.WaitingTimes = []          #List of waiting times in the successive reservoirs

        route = Route.get_route(routes, routeID)
        
        self.Path = route.CrossedReservoirs              # list of successive crossed reservoirs
        self.RouteSections = route.RouteSections         # list of successive route sections
        
        self.PathIndex = -1             # index of the current reservoir int the path
        self.RemainingLengthOfCurrentReservoir
        
        self.DesiredExitTimes = [-1 for e in range(len(self.Path))]      # List of desired exit times in the successive reservoir of the route assigned to the vehicle
        
        self.EntryTimes = [-1 for e in range(len(self.Path))]            #List of entry times in the successive reservoir of the route assigned to the vehicle
        self.ExitTimes = [-1 for e in range(len(self.Path))]                                              # List of exit times in the successive reservoir of the route assigned to the vehicle
        
        self.TotalTraveledDistance = 0
        self.TotalTraveledTime = 0