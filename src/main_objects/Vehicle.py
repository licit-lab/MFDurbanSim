class Vehicle:
    def __init__(self):
        
        self.ID = ""                    #ID of the vehicle
        self.Mode = ""                  #Type of vehicle
        self.CurrentResID = ""          #ID of the current reservoir the vehicle is in

        #Both solver
        self.RouteID = ""               #ID of the route on which the vehicle is traveling
        self.CreationTime = 0           #Creation time of the vehicle
        self.EntryTimes = []            #List of entry times in the successive reservoir of the route assigned to the vehicle
        self.ExiTimes = []              #List of exit times in the successive reservoir of the route assigned to the vehicle
        self.TripLength = []            #List of trip lengths in the successive reservoirs
        self.TraveledDistance = []      #List of distances traveled by the vehicle in the successive reservoirs
        self.WaitingTimes = []          #List of waiting times in the successive reservoirs

        #Trip-based solver
        self.PathIndex = 0              #Index of the path
