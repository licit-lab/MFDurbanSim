def init_time_step(t, Reservoirs, Routes):

    for reservoir in Reservoirs:
        reservoir.init_time_step(t)
        
        for routesection in reservoir.RouteSections:
            routesection.init_time_step(t)
