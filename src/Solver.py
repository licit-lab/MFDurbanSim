from AccBased_functions import *

def AccBased(Simulation, Reservoirs, Routes, MacroNodes, Demand):

    Compute_Res(Reservoirs, Routes)
    
    
    #Time loop
    for t in range(0, Simulation.Duration, Simulation.TimeStep):
        test = 0

    print(Reservoirs[0].AccPerRoute)



def TripBased(Simulation, Reservoirs, Routes, MacroNodes, Demand, Vehicles):

    #Time loop
    for t in range(0, Simulation.Duration, Simulation.TimeStep):
        print("TripBased")
