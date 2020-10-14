import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import math
import numpy as np

def plotResBallConfig(Reservoir, plotborders, ResRadius, coordscale):
    # Plot the reservoir configuration (ball shapes and connections)

    # INPUTS
    # ---- Reservoir: Reservoir list
    # ---- plotborders: boolean, plot the reservoir borders if = 1
    # ---- ResRadius: scalar, radius of the disk used to symbolize reservoirs
    # ---- coordscale: 1 - by - 2 vector, scale factors along x and y axis [fx fy]

    numRes = len(Reservoir)
    flowspace = 0 # spacing between flow lines
    cmap0 = np.array([(51, 51, 255), (0, 204, 51), (204, 0, 0), (204, 153, 0), (153, 0, 102), (51, 153, 153), (204, 102, 204), (204, 204, 102)]) / 255  # default

    # Normalization of reservoir coordinates
    x0 = Reservoir[0].Centroid[0]["x"]
    y0 = Reservoir[0].Centroid[0]["y"]
    x1 = 0
    y1 = 0

    for r in range(0, numRes):
        if Reservoir[r].ID == Reservoir[0].AdjacentResID[0]:
            x1 = Reservoir[r].Centroid[0]["x"]
            y1 = Reservoir[r].Centroid[0]["y"]

    dx0 = max([abs(x1 - x0), abs(y1 - y0)])
    dx0 = (0 < dx0) * dx0 + (0 == dx0) * 1

    xLinks = []
    yLinks = []
    if plotborders == 1:
        # Plot the reservoirs
        for r in range(numRes):
            if len(Reservoir[r].BorderPoints) != 0:
                xResbp = []
                yResbp = []
                for bp in range(len(Reservoir[r].BorderPoints)):
                    xResbp_tmp = (coordscale[0] * Reservoir[r].BorderPoints[bp]["x"] - x0) / dx0
                    yResbp_tmp = (coordscale[1] * Reservoir[r].BorderPoints[bp]["y"] - y0) / dx0
                    xResbp.append(xResbp_tmp)
                    yResbp.append(yResbp_tmp)

                    xLinks.append(xResbp_tmp)
                    yLinks.append(yResbp_tmp)

                plt.fill(xResbp, yResbp, color = cmap0[r], ec = 'none', alpha = 0.5)
                plt.plot(xResbp, yResbp, color = cmap0[r])

    xList = []
    yList = []
    for r in range(numRes):
        xResC = coordscale[0] * (Reservoir[r].Centroid[0]["x"] - x0) / dx0
        yResC = coordscale[1] * (Reservoir[r].Centroid[0]["y"] - y0) / dx0

        xList.append(xResC)
        yList.append(yResC)

        # Plot flow exchanges
        if r < numRes: # to avoid flow line duplication
            for i in range(len(Reservoir[r].AdjacentResID)):
                adjID = Reservoir[r].AdjacentResID[i]
                for j in range(numRes):
                    if adjID == Reservoir[j].ID:
                        xResAdj = coordscale[0] * (Reservoir[j].Centroid[0]["x"] - x0) / dx0
                        yResAdj = coordscale[1] * (Reservoir[j].Centroid[0]["y"] - y0) / dx0

                        ang = math.atan2(xResAdj - yResC, xResAdj - xResC) + math.pi / 2

                        dx = flowspace * math.cos(ang)
                        dy = flowspace * math.sin(ang)

                        xi1 = xResC + dx
                        yi1 = yResC + dy
                        xj1 = xResAdj + dx
                        yj1 = yResAdj + dy

                        # Effective flow from Ri to Rj
                        plt.plot([xi1, xj1], [yi1, yj1], '-', color = 'k')

        # Plot reservoir disk
        step = 0.01
        th = list(np.arange(0, 2 * math.pi + step, step))
        x = [xResC + ResRadius * math.cos(element) for element in th]
        y = [yResC + ResRadius * math.sin(element) for element in th]
        plt.fill(x, y, 'k', edgecolor = 'none')
        plt.text(xResC, yResC, r'$R_{' + str(r + 1) + '}$', ha = 'center', color = 'w', fontname = 'arial', fontweight = 'bold', fontsize = 18)

    # Plot size
    xborder = 0.1 # increasing factor > 0 for the border spacing along x
    yborder = 0.1 # increasing factor > 0 for the border spacing along x
    if plotborders == 1:
        if max(xLinks) == min(xLinks):
            dx = max(yLinks) - min(yLinks)
        else:
            dx = max(xLinks) - min(xLinks)

        if max(yLinks) == min(yLinks):
            dy = max(xLinks) - min(xLinks)
        else:
            dy = max(yLinks) - min(yLinks)

        xmin = min(xLinks) - xborder * dx
        xmax = max(xLinks) + xborder * dx
        ymin = min(yLinks) - yborder * dy
        ymax = max(yLinks) + yborder * dy
    else:
        if max(xList) == min(xList):
            dx = max(yList) - min(yList)
        else:
            dx = max(xList) - min(xList)

        if max(yList) == min(yList):
            dy = max(xList) - min(xList)
        else:
            dy = max(yList) - min(yList)

        xmin = min(xList) - ResRadius - xborder * dx
        xmax = max(xList) + ResRadius + xborder * dx
        ymin = min(yList) - ResRadius - yborder * dy
        ymax = max(yList) + ResRadius + yborder * dy

    plt.axis([xmin, xmax, ymin, ymax])
    plt.axis('off')

def plotResBallAcc(t, Reservoir, ResOutput, SimulTime, ResRadius, coordscale):
# Plot the state of reservoirs at time t (accumulation and flow)
#
# INPUTS
#---- t           : scalar, time [s]
#---- Reservoir   : Reservoirs list
#---- SimulTime   : vector, simulation time [s]
#---- ResRadius   : scalar, radius of the disk used to symbolize reservoirs
#---- coordscale  : 1-by-2 vector, scale factors along x and y axis [fx fy]

    numRes = len(Reservoir)
    timeStep = SimulTime[1] - SimulTime[0]
    timeID = 0

    # Index of the current time
    for i in range(len(SimulTime)):
        if t == SimulTime[i] or abs(t - SimulTime[i]) <= timeStep / 2:
            timeID = i

    # Options
    fontname = 'arial' # default
    FS = 16 # default
    tlabel = 't = ' + str(t) + ' s' # default
    showflowval = 1 # default
    txtcolor = [0.9, 0.9, 1]
    flowspac = 0.2 # spacing between flow lines
    maxwidth = 30 # flow line max width

    xList = []
    yList = []

    # Normalization of reservoir coordinates
    x0 = Reservoir[0].Centroid[0]["x"]
    y0 = Reservoir[0].Centroid[0]["y"]
    x1 = 0
    y1 = 0

    for r in range(0, numRes):
        if Reservoir[r].ID == Reservoir[0].AdjacentResID[0]:
            x1 = Reservoir[r].Centroid[0]["x"]
            y1 = Reservoir[r].Centroid[0]["y"]

    dx0 = max([abs(x1 - x0), abs(y1 - y0)])
    dx0 = (0 < dx0) * dx0 + (0 == dx0) * 1

    # Define max flow for plotting purpose
    listMaxFlow = []
    for r in range(numRes):
        flow = []
        if ResOutput[r]["ReservoirData"][timeID]["AvgTripLength"] != 0:
            flow.append(Reservoir[r].MaxProd[0]["value"] / ResOutput[r]["ReservoirData"][timeID]["AvgTripLength"])
        listMaxFlow.append(max(flow))

    maxflow = max(listMaxFlow)

    for r in range(numRes):
        xResC = coordscale[0] * (Reservoir[r].Centroid[0]["x"] - x0) / dx0
        yResC = coordscale[1] * (Reservoir[r].Centroid[0]["y"] - y0) / dx0

        xList.append(xResC)
        yList.append(yResC)

        # Plot flow exchanges
        if r < numRes:
            for i in range(len(Reservoir[r].AdjacentResID)):
                adjID = Reservoir[r].AdjacentResID[i]
                if adjID > Reservoir[r].ID : # to avoid flow line duplication
                    for j in range(numRes):
                        if adjID == Reservoir[j].ID:
                            xResAdj = coordscale[0] * (Reservoir[j].Centroid[0]["x"] - x0) / dx0
                            yResAdj = coordscale[1] * (Reservoir[j].Centroid[0]["y"] - y0) / dx0

                            ang = math.atan2(yResAdj - yResC, xResAdj - xResC) + math.pi / 2

                            dx = flowspac * math.cos(ang)
                            dy = flowspac * math.sin(ang)

                            xRes1 = xResC + dx
                            yRes1 = yResC + dy
                            xRes2 = xResC - dx
                            yRes2 = yResC - dy
                            xResAdj1 = xResAdj + dx
                            yResAdj1 = yResAdj + dy
                            xResAdj2 = xResAdj - dx
                            yResAdj2 = yResAdj - dy

                # Effective flow from Ri to Rj
                outflowij = 0.35;#sum(Reservoir(r).OutflowPerResPerDest(xResAdj,:, timeID))
                LW = max([outflowij / maxflow * maxwidth, 0.1])
                plt.plot([xRes1, xResAdj1], [yRes1, yResAdj1], '-', color = 'k', linewidth = LW)
                if showflowval == 1:
                    plt.text(1 / 3 * xRes1 + 2 / 3 * xResAdj1, 1 / 3 * yRes1 + 2 / 3 * yResAdj1, str(outflowij), rotation = ang * 180 / math.pi, ha = 'center', color = 'k', backgroundcolor = 'w', fontname = fontname, fontsize = 0.5 * FS)

                # Effective flow from Rj to Ri
                outflowji = 0.2;#sum(Reservoir(r2).OutflowPerResPerDest(r,:, timeID))
                LW = max([outflowji / maxflow * maxwidth, 0.1])
                plt.plot([xRes2, xResAdj2], [yRes2, yResAdj2], '-', color = 'k', linewidth = LW)
                if showflowval == 1:
                    plt.text(2 / 3 * xRes2 + 1 / 3 * xResAdj2, 2 / 3 * yRes2 + 1 / 3 * yResAdj2, str(outflowji), rotation = ang * 180 / math.pi, ha = 'center', color = 'k', backgroundcolor = 'w', fontname = fontname, fontsize = 0.5 * FS)


        # Plot reservoir disk
        step = 0.01
        th = list(np.arange(0, 2 * math.pi + step, step))
        x = [xResC + ResRadius * math.cos(element) for element in th]
        y = [yResC + ResRadius * math.sin(element) for element in th]
        plt.fill(x, y, 'k', edgecolor = 'none')

        # Plot accumulation evolution
        accratio = ResOutput[r]["ReservoirData"][timeID]["Acc"] / Reservoir[r].MaxAcc[0]["value"]
        heightlevel = accratio * 2 * ResRadius
        th0 = math.asin((heightlevel - ResRadius) / ResRadius)
        th = list(np.arange(-math.pi - th0, th0 + step, step))
        x = [xResC + ResRadius * math.cos(element) for element in th]
        y = [yResC + ResRadius * math.sin(element) for element in th]

        plt.fill(x, y, 'k', ec = 'none')
        plt.text(xResC, yResC, r'$R_{' + str(r + 1) + '}$' + '\n' + str(round(ResOutput[r]["ReservoirData"][timeID]["Acc"])), ha = 'center', color = txtcolor, fontname = fontname, fontweight = 'bold', fontsize = FS)

    # Plot size
    xborder = 0.05 # increasing factor > 0 for the border spacing along x
    yborder = 0.1 # increasing factor > 0 for the border spacing along x
    if max(xList) == min(xList):
        dx = max(yList) - min(yList)
    else:
        dx = max(xList) - min(xList)

    if max(yList) == min(yList):
        dy = max(xList) - min(xList)
    else:
        dy = max(yList) - min(yList)

    xmin = min(xList) - ResRadius - xborder * dx
    xmax = max(xList) + ResRadius + xborder * dx
    ymin = min(yList) - ResRadius - yborder * dy
    ymax = max(yList) + ResRadius + yborder * dy

    plt.text((xmin + xmax) / 2, ymax, tlabel, color = [0.5, 0.5, 0.5], ha = 'center', va = 'top', fontname = fontname, fontsize = FS, fontweight = 'bold')
    plt.axis([xmin, xmax, ymin, ymax])
    plt.axis('off')

def plotResBallAccPerRoute(t, Reservoir, ResOutput, Route, SimulTime, ResRadius, coordscale):
# Plot the state of reservoirs at time t(accumulation and flow)
# Plot accumulation ratio of each route in the reservoirs
#
# INPUTS
# ---- t: scalar, time[s]
# ---- Reservoir: Reservoir structure
# ---- Route: Route structure
# ---- SimulTime: vector, simulation time[s]
# ---- ResRadius: scalar, radius of the disk used to symbolize reservoirs
# ---- coordscale: 1 - by - 2 vector, scale factors along x and y axis[fx fy]

    numRes = len(Reservoir)
    numRoutes = len(Route)

    # Index of the current time
    timeStep = SimulTime[1] - SimulTime[0]
    timeID = 0
    for i in range(len(SimulTime)):
        if t == SimulTime[i] or abs(t - SimulTime[i]) <= timeStep / 2:
            timeID = i

    # Options
    fontname = 'Arial' # default
    FS = 16 # default
    cmap0 = np.array([(51, 51, 255), (0, 204, 51), (204, 0, 0), (204, 153, 0), (153, 0, 102), (51, 153, 153), (204, 102, 204), (204, 204, 102)]) / 255 # default
    txtcolor = [0.9, 0.9, 1] # default
    tlabel = 't = ' + str(t) + ' s'
    showleg = 1
    legloc = 'best' # default
    showflowval = 1 # default

    cmap = cmap0

    while np.size(cmap, 1) < numRoutes:
        cmap = np.vstack(cmap, cmap0)

    flowspac = 0.2 # spacing between flow lines
    maxwidth = 30 # flow line max width

    xList = []
    yList = []

    # Normalization of reservoir coordinates
    x0 = Reservoir[0].Centroid[0]["x"]
    y0 = Reservoir[0].Centroid[0]["y"]
    x1 = 0
    y1 = 0

    for r in range(0, numRes):
        if Reservoir[r].ID == Reservoir[0].AdjacentResID[0]:
            x1 = Reservoir[r].Centroid[0]["x"]
            y1 = Reservoir[r].Centroid[0]["y"]

    dx0 = max([abs(x1 - x0), abs(y1 - y0)])
    dx0 = (0 < dx0) * dx0 + (0 == dx0) * 1

    # Define max flow
    listMaxFlow = [] # max flow per reservoir
    for r in range(numRes):
        flow = []
        if ResOutput[r]["ReservoirData"][timeID]["AvgTripLength"] != 0:
            flow.append(Reservoir[r].MaxProd[0]["value"] / ResOutput[r]["ReservoirData"][timeID]["AvgTripLength"])
        listMaxFlow.append(max(flow))

    maxflow = max(listMaxFlow)

    hf = []
    strleg = []
    LegList = []

    for r in range(numRes):
        xResC = coordscale[0] * (Reservoir[r].Centroid[0]["x"] - x0) / dx0
        yResC = coordscale[1] * (Reservoir[r].Centroid[0]["y"] - y0) / dx0

        xList.append(xResC)
        yList.append(yResC)

        # Plot flow exchanges
        if r < numRes:  # avoid flow line duplication
            for i in range(len(Reservoir[r].AdjacentResID)):
                adjID = Reservoir[r].AdjacentResID[i]
                if adjID > Reservoir[r].ID: # avoid flow line duplication
                    for j in range(numRes):
                        if adjID == Reservoir[j].ID:
                            xResAdj = coordscale[0] * (Reservoir[j].Centroid[0]["x"] - x0) / dx0
                            yResAdj = coordscale[1] * (Reservoir[j].Centroid[0]["y"] - y0) / dx0

                            ang = math.atan2(yResAdj - yResC, xResAdj - xResC) + math.pi / 2

                            dx = flowspac * math.cos(ang)
                            dy = flowspac * math.sin(ang)

                            xRes1 = xResC + dx
                            yRes1 = yResC + dy
                            xRes2 = xResC - dx
                            yRes2 = yResC - dy
                            xResAdj1 = xResAdj + dx
                            yResAdj1 = yResAdj + dy
                            xResAdj2 = xResAdj - dx
                            yResAdj2 = yResAdj - dy

                # Effective flow from Ri to Rj
                outflowij = 0.8  # sum(Reservoir(r).OutflowPerResPerDest(xResAdj,:, timeID))
                LW = max([outflowij / maxflow * maxwidth, 0.1])
                plt.plot([xRes1, xResAdj1], [yRes1, yResAdj1], '-', color='k', linewidth=LW, zorder = 0)
                if showflowval == 1:
                    plt.text(1 / 3 * xRes1 + 2 / 3 * xResAdj1, 1 / 3 * yRes1 + 2 / 3 * yResAdj1, str(outflowij), rotation=ang * 180 / math.pi, ha='center', color='k', backgroundcolor='w', fontname=fontname, fontsize=0.5 * FS)

                # Effective flow from Rj to Ri
                outflowji = 0.2  # sum(Reservoir(r2).OutflowPerResPerDest(r,:, timeID))
                LW = max([outflowji / maxflow * maxwidth, 0.1])
                plt.plot([xRes2, xResAdj2], [yRes2, yResAdj2], '-', color='k', linewidth=LW, zorder = 0)
                if showflowval == 1:
                    plt.text(2 / 3 * xRes2 + 1 / 3 * xResAdj2, 2 / 3 * yRes2 + 1 / 3 * yResAdj2, str(outflowji), rotation=ang * 180 / math.pi, ha='center', color='k', backgroundcolor='w', fontname=fontname, fontsize=0.5 * FS)

        # Plot reservoir disk
        step = 0.01
        th = list(np.arange(0, 2 * math.pi + step, step))
        x = [xResC + ResRadius * math.cos(element) for element in th]
        y = [yResC + ResRadius * math.sin(element) for element in th]
        plt.fill(x, y, 'grey', edgecolor = 'none')

        # Plot accumulation evolution
        legend = []
        angstart = 0
        k_r = 0
        for iroute in range(numRoutes):
            for iRouteSect in range(len(ResOutput[r]["DataPerRoute"])):
                if ResOutput[r]["DataPerRoute"][iRouteSect]["IDRoute"] == Route[iroute].ID:
                    accratio = ResOutput[r]["DataPerRoute"][iRouteSect]["Data"][timeID]["Acc"] / Reservoir[r].MaxAcc[0]["value"]
                    angend = angstart + accratio * 2 * math.pi
                    thRoute = list(np.arange(angstart, angend + step, step))
                    x = [xResC + ResRadius * math.cos(element) for element in thRoute]
                    y = [yResC + ResRadius * math.sin(element) for element in thRoute]
                    angstart = angend

                    if iRouteSect in LegList: # add to the legend
                        for i in range(len(x)):
                            hf.append(plt.fill([xResC, x[i]], [yResC, y[i]], color = cmap[k_r], ec = 'none'))
                    else:
                        strlabel = '[ '
                        for i in range(len(Route[iroute].CrossedReservoirs)):
                            strlabel += Route[iroute].CrossedReservoirs[i].ID + ' '
                        strlabel += ']'
                        for i in range(len(x)):
                            hf.append(plt.fill([xResC, x[i]], [yResC, y[i]], color = cmap[k_r], ec = 'none', label = strlabel))
                        LegList.append(iRouteSect)
            k_r += 1
        plt.text(xResC, yResC, r'$R_{' + str(r + 1) + '}$' + '\n' + str(round(ResOutput[r]["ReservoirData"][timeID]["Acc"])), ha = 'center', color = txtcolor, fontname = fontname, fontweight = 'bold', fontsize = FS)

    # Plot size
    xborder = 0.05  # increasing factor > 0 for the border spacing along x
    yborder = 0.1  # increasing factor > 0 for the border spacing along x
    if max(xList) == min(xList):
        dx = max(yList) - min(yList)
    else:
        dx = max(xList) - min(xList)

    if max(yList) == min(yList):
        dy = max(xList) - min(xList)
    else:
        dy = max(yList) - min(yList)

    xmin = min(xList) - ResRadius - xborder * dx
    xmax = max(xList) + ResRadius + xborder * dx
    ymin = min(yList) - ResRadius - yborder * dy
    ymax = max(yList) + ResRadius + yborder * dy

    plt.text((xmin + xmax) / 2, ymax, tlabel, color = [0.5, 0.5, 0.5], ha = 'center', va = 'top', fontname = fontname, fontsize = FS, fontweight = 'bold')
    plt.axis([xmin, xmax, ymin, ymax])
    plt.axis('off')

    if showleg == 1:
        plt.legend(hf, strleg, bbox_to_anchor=(1.05, 1), loc='center right', borderaxespad=0., fontsize = FS)

def plotResNetSpeed(t, Reservoir, ResOutput, SimulTime, SpeedRange):
# Plot the state of reservoirs at time t(mean speed), with links and/ or shape borders
#
# INPUTS
# ---- t: scalar, time[s]
# ---- Reservoir: Reservoir structure
# ---- SimulTime: vector, simulation time[s]
# ---- SpeedRange: vector[Vmin Vmax], speed range[m / s] to define the colormap

    numRes = len(Reservoir)

    # Index of the current time
    timeStep = SimulTime[1] - SimulTime[0]
    timeID = 0
    for i in range(len(SimulTime)):
        if t == SimulTime[i] or abs(t - SimulTime[i]) <= timeStep / 2:
            timeID = i

    # Choice of a colormap
    nbColor = 800
    RdYlGn = cm.get_cmap('RdYlGn', nbColor)

    txtcolor = [0.1, 0.1, 0]
    fontname = 'Arial'
    FS = 16
    LW = 1
    tlabel = "Mean speed at t = " + str(t) + " s"

    xLinks = []
    yLinks = []

    # Plot reservoirs
    for r in range(numRes):
        speedratio = (ResOutput[r]["ReservoirData"][timeID]["MeanSpeed"] - SpeedRange[0]) / (SpeedRange[1] - SpeedRange[0])
        indcolor = min([max([math.floor(speedratio * nbColor), 1]), nbColor])
        colori = RdYlGn(indcolor)

        if len(Reservoir[r].BorderPoints) != 0:
            xResbp = []
            yResbp = []
            for bp in range(len(Reservoir[r].BorderPoints)):
                xResbp.append(Reservoir[r].BorderPoints[bp]["x"])
                yResbp.append(Reservoir[r].BorderPoints[bp]["y"])

                xLinks.append(Reservoir[r].BorderPoints[bp]["x"])
                yLinks.append(Reservoir[r].BorderPoints[bp]["y"])

            plt.fill(xResbp, yResbp, color = colori, ec='none', alpha=0.5)
            plt.plot(xResbp, yResbp, '-', color = colori, linewidth = LW)

    for r in range(numRes):
        xr = Reservoir[r].Centroid[0]["x"]
        yr = Reservoir[r].Centroid[0]["y"]
        plt.text(xr, yr, r'$R_{' + str(r + 1) + '}$'+ '\n' + str(round(ResOutput[r]["ReservoirData"][timeID]["MeanSpeed"] * 3.6)) + ' km/h', ha = 'center', color = txtcolor, fontname = fontname, fontweight = 'bold', fontsize = FS)

    # Plot size
    xborder = 0.1 # increasing factor > 0 for the border spacing along x
    yborder = 0.1 # increasing factor > 0 for the border spacing along x
    if max(xLinks) == min(xLinks):
        dx = max(yLinks) - min(yLinks)
    else:
        dx = max(xLinks) - min(xLinks)

    if max(yLinks) == min(yLinks):
        dy = max(xLinks) - min(xLinks)
    else:
        dy = max(yLinks) - min(yLinks)

    xmin = min(xLinks) - xborder * dx
    xmax = max(xLinks) + xborder * dx
    ymin = min(yLinks) - yborder * dy
    ymax = max(yLinks) + yborder * dy

    plt.axis([xmin, xmax, ymin, ymax])
    plt.axis('off')
    plt.text((xmin + xmax) / 2, ymax - yborder * dy / 4, tlabel, ha = 'center', fontname = fontname, fontsize = FS, fontweight = "bold")

def plotResRouteDem(Reservoir, Route, Node, Demand, demandType, plotcharact):
# Plot the number or demand of a given route list crossing the reservoirs
#
# INPUTS
#---- Reservoir   : Reservoir structure
#---- Route       : Route structure
#---- plotcharact : string, 'number' or 'demand'

    numRes = len(Reservoir)
    numRoute = len(Route)
    numDemand = len(Demand)
    numNode = len(Node)

    # Choice of a colormap
    nbColor = 800
    RdYlGn = cm.get_cmap('RdYlGn', nbColor)

    # Options
    txtcolor = [0.1, 0.1, 0]
    fontname = 'Arial'
    FS = 18
    LW = 2
    legloc = 'best'

    xLinks = []
    yLinks = []
    resvalues = []

    # Demand per reservoir
    DemandPerRes = []

    #incorrect - TO DO
    if demandType == "FlowDemand":
        for d in range(numDemand):
            demand = 0
            for t in range(len(Demand[d].Demand)):
                demand += Demand[d].Demand[t]["Data"]
            demand /= len(Demand[d].Demand)

            for n in range(numNode):
                if Node[n].ID == Demand[d].OriginMacroNodeID or Node[n].ID == Demand[d].DestMacroNodeID:
                    resID = Node[n].ResID[0]
                    DemandPerRes.append({"ID": resID, "Demand": demand})
    #TODO
    elif demandType == "DiscreteDemand":
        toto = 0

    for r in range(numRes):
        nbroutes = 0
        totaldem = 0
        for iroute in range(numRoute):
            for r2 in range(len(Route[iroute].CrossedReservoirs)):
                if Reservoir[r].ID == Route[iroute].CrossedReservoirs[r2].ID:
                    nbroutes += 1
        for d in range(len(DemandPerRes)):
            if Reservoir[r].ID == DemandPerRes[d]["ID"]:
                totaldem = DemandPerRes[d]["Demand"]

        if plotcharact == 'number':
            resvalues.append(nbroutes)
        elif plotcharact == 'demand':
            resvalues.append(totaldem)

    maxvalue = max(resvalues)

    # Plot reservoirs
    for r in range(numRes):
        ratio = resvalues[r] / maxvalue
        indcolor = max([math.floor(ratio * nbColor), 1])
        colori = RdYlGn(indcolor)

        if len(Reservoir[r].BorderPoints) != 0:
            xResbp = []
            yResbp = []
            for bp in range(len(Reservoir[r].BorderPoints)):
                xResbp.append(Reservoir[r].BorderPoints[bp]["x"])
                yResbp.append(Reservoir[r].BorderPoints[bp]["y"])

                xLinks.append(Reservoir[r].BorderPoints[bp]["x"])
                yLinks.append(Reservoir[r].BorderPoints[bp]["y"])

            plt.fill(xResbp, yResbp, color = colori, ec='none', alpha=0.5)
            plt.plot(xResbp, yResbp, '-', color = colori, linewidth = LW)

    for r in range(numRes):
        xr = Reservoir[r].Centroid[0]["x"]
        yr = Reservoir[r].Centroid[0]["y"]
        plt.text(xr, yr, r'$R_{' + str(r + 1) + '}$' + '\n' + str(resvalues[r]), ha = 'center', color = txtcolor, fontname = fontname, fontweight = 'bold', fontsize = FS)

    # Plot size
    xborder = 0.1 # increasing factor > 0 for the border spacing along x
    yborder = 0.1 # increasing factor > 0 for the border spacing along x
    if max(xLinks) == min(xLinks):
        dx = max(yLinks) - min(yLinks)
    else:
        dx = max(xLinks) - min(xLinks)

    if max(yLinks) == min(yLinks):
        dy = max(xLinks) - min(xLinks)
    else:
        dy = max(yLinks) - min(yLinks)

    xmin = min(xLinks) - xborder*dx
    xmax = max(xLinks) + xborder*dx
    ymin = min(yLinks) - yborder*dy
    ymax = max(yLinks) + yborder*dy

    # #hcb = plt.colorbar()
    # if plotcharact == 'number':
    #     hcb.Label.String = 'Number of routes [-]'
    #     strtitle = 'Number of routes \rm[-]'
    # elif plotcharact == 'demand':
    #     hcb.Label.String = 'Cumul. mean demand on routes [veh/s]'
    #     strtitle = 'Cumul. mean demand on routes \rm[veh/s]'

    plt.axis([xmin, xmax, ymin, ymax])
    plt.axis('off')

def plotMacroNodes(Reservoir, coloringres, MacroNode, sizingnodes, Route, coloringroutes):
# Plot the real network configuration with reservoirs and a set of given
# routes represented by smooth lines. The line thickness represent the
# demand on the route. The routes are shown as sequences of macro nodes.
#
# INPUTS
#---- Reservoir      : Reservoir structure
#---- coloringres    : boolean, 1: different colors for the reservoirs
#---- MacroNode      : MacroNode structure
#---- sizingnodes    : boolean, 1: node size depends on the flow transfered
#---- Route          : Route structure
#---- coloringroutes : boolean, 1: different colors for the routes

    numRes = len(Reservoir)
    numNodes = len(MacroNode)
    numRoutes = len(Route)
    
    # Options
    fontname = 'Arial'
    FS = 28
    LW = 2
    MS = 10
    cmap0 = np.array([51, 51, 255], [0, 204, 51], [204, 0, 0], [204, 153, 0], [153, 0, 102], [51, 153, 153], [204, 102, 204], [204, 204, 102] / 255)
    rescolor = [0.1, 0.1, 0]
    txtcolor = [0.9, 0.9, 1]
    plotlegend = 0
    plotnumnodes = 0
    exactsmooth = 1
    
    # Lines
    line0 = {'-', '--', ':', '-.'}
    # Line width
    minLW = 0.2
    maxLW = 5
    # Marker size
    minMS = 0.5 * MS
    maxMS = 3 * MS

    # Plot the reservoirs
    xLinks = []
    yLinks = []

    # Plot the reservoirs
    for r in range(numRes):
        if len(Reservoir[r].BorderPoints) != 0:
            xResbp = []
            yResbp = []
            for bp in range(len(Reservoir[r].BorderPoints)):
                xResbp_tmp = Reservoir[r].BorderPoints[bp]["x"]
                yResbp_tmp = Reservoir[r].BorderPoints[bp]["y"]
                xResbp.append(xResbp_tmp)
                yResbp.append(yResbp_tmp)

                xLinks.append(xResbp_tmp)
                yLinks.append(yResbp_tmp)

            plt.fill(xResbp, yResbp, color=cmap0[r], ec='none', alpha=0.5)
            plt.plot(xResbp, yResbp, color=cmap0[r])
    
    # Plot the routes
    routedem = []
    for iroute in range(numRoutes):
        #TODO
        routedem.append(math.mean(Route(iroute).Demand))

    maxdem = max(routedem)
    mindem = 0.1 * maxdem
    
    arrowL = 0.04 * (max(xLinks) - min(xLinks))
    hp = []
    strleg = []
    i = 1
    for iroute in range(numRoutes):
        if routedem[i] > 0:
            sline = '-';
        else:
            sline = '--';

        colori = cmap0[i]

        listx = []
        listy = []
        for inode in range(numNodes):
            xn = MacroNode[i].Coord[0]["x"]
            yn = MacroNode[i].Coord[0]["y"]
            listx.append(xn)
            listy.append(yn)
        
        # Smooth the route line
        if len(listx) == 1: # one point: internal trip
            xn = listx[0]
            yn = listy[0]

            for bp in range(len(Reservoir[r].BorderPoints)):
                xResbp_tmp += Reservoir[r].BorderPoints[bp]["x"]
                yResbp_tmp += Reservoir[r].BorderPoints[bp]["y"]
            xb = xResbp_tmp / len(Reservoir[r].BorderPoints)
            yb = yResbp_tmp / len(Reservoir[r].BorderPoints)

            d = math.sqrt((xn - xb)^2 + (yn - yb)^2) # centroid-to-border mean distance
            thmax = 7 * math.pi / 4
            th = list(np.arange(0,thmax, 0.05))
            xpath = [xn + 0.7 * d * th[element] / thmax * math.cos(th[element]) for element in th]
            ypath = [yn + 0.7 * d * th[element] / thmax * math.sin(th[element]) for element in th]
        else:
            if exactsmooth == 0:
                # The smoothed route does not necessarily connect all the points
                alpha1 = 0.5 # for way-back turns
                alpha2 = 1.7 # for direct turns
                #TODO
                #[xpath, ypath] = smoothroute(listx, listy, 50, alpha1, alpha2)
            else:
                # The smoothed route connects all the points (exact interpolation)
                tension = 0.5 # smooth coeff
                #TODO
                #[xpath, ypath] = smoothroute2(listx, listy, 50, tension)

        LWroute = minLW + (routedem(i) - mindem)/(maxdem - mindem)*(maxLW - minLW)
        LWroute = max([LWroute, minLW])
        hp.append(plt.plot(xpath, ypath, linestyle = sline, color = colori, linewidth = LWroute))
        strleg.append(str(iroute + 1) + ': [' + str(Route(iroute).ResPath) + ']')
        #TODO
        plt.arrow([xpath(end-1), xpath(end)],[ypath(end-1), ypath(end)], arrowL,'absolute', 1, colori, LWroute)
    
    # Plot the macro nodes
    color1 = cmap0[3,:]
    color2 = cmap0[1,:]
    color3 = cmap0[4,:]
    MS1 = MS
    MS2 = 1.5 * MS
    MS3 = MS
    entrynodeslist = []
    exitnodeslist = []
    bordernodeslist = []
    for n in range(numNodes):
        if MacroNode[n].Type == 'origin' or MacroNode[n].Type == 'externalentry':
            entrynodeslist.append(n)
        elif MacroNode(n).Type == 'destination' or MacroNode[n].Type == 'externalexit':
            exitnodeslist.append(n)
        else:
            bordernodeslist.append(n)

    if sizingnodes == 0:
        for i in range(len(exitnodeslist)):
            plt.plot(MacroNode[i].Coord[0]["x"], MacroNode[i].Coord[0]["y"], 'o', color = color2, markerfacecolor = color2, markersize = MS2)
        for i in range(len(entrynodeslist)):
            plt.plot(MacroNode[i].Coord[0]["x"], MacroNode[i].Coord[0]["y"], 'o', color = color1, markerfacecolor = color1, markersize = MS1)
        for i in range(len(bordernodeslist)):
            plt.plot(MacroNode[i].Coord[0]["x"], MacroNode[i].Coord[0]["y"], 'o', color = color3, markerfacecolor = color3, markersize = MS3)
    else:
        nodeflow = []
        for iroute in range(numRoutes):
            if Route(iroute).AssignCoeff > 0:
                r = Route[iroute].ResPath[0]["ID"]
                #TODO
                #i_r = Route(iroute).ResRouteIndex(r)
                inode = Route[iroute].NodePath[0] # entry node
                #nodeflow[inode] = nodeflow[inode] + mean(Reservoir(r).InflowPerRoute(i_r,:))
                inode = Route[iroute].NodePath[1] # exit node
                #nodeflow[inode] = nodeflow[inode] + mean(Reservoir(r).OutflowPerRoute(i_r,:))
                if len(Route[iroute].ResPath) > 1:
                    k_r = 1
                    for r in range(1,len(Route[iroute].ResPath)):
                        #i_r = Route(iroute).ResRouteIndex(r)
                        inode = Route[iroute].NodePath[k_r + 1] # exit node
                        #nodeflow(inode) = nodeflow(inode) + mean(Reservoir(r).OutflowPerRoute(i_r,:))
                        k_r = k_r + 1

        maxflow = max(nodeflow(MacroNode))
        minflow = 0.1 * maxflow
        for i in range(len(exitnodeslist)):
            MSnode = minMS + (nodeflow(i) - minflow)/(maxflow - minflow) * (maxMS - minMS)
            MSnode = max([MSnode, minMS])
            plt.plot(MacroNode[i].Coord[0]["x"], MacroNode[i].Coord[0]["y"],'o', color = color2, markerfacecolor = color2, markersize = MSnode)
        for i in range(len(entrynodeslist)):
            MSnode = minMS + (nodeflow(i) - minflow) / (maxflow - minflow) * (maxMS - minMS)
            MSnode = max([MSnode, minMS])
            plt.plot(MacroNode[i].Coord[0]["x"], MacroNode[i].Coord[0]["y"], 'o', color = color1, markerfacecolor = color1, markersize = MSnode)
        for i in range(len(bordernodeslist)):
            MSnode = minMS + (nodeflow(i) - minflow) / (maxflow - minflow) * (maxMS - minMS)
            MSnode = max([MSnode, minMS])
            plt.plot(MacroNode[i].Coord[0]["x"], MacroNode[i].Coord[0]["y"], 'o', color = color3, markerfacecolor = color3, markersize = MSnode)

    # Plot the reservoir numbers
    for r in range(numRes):
        xr = Reservoir[r].Centroid[0]["x"]
        yr = Reservoir[r].Centroid[0]["y"]
        plt.text(xr,yr, r'$R_{' + str(r + 1) + '}$', ha = 'center', color = txtcolor, fontname = fontname, fontweight = 'bold', fontsize = FS)
    
    # Plot size
    xborder = 0.1 # increasing factor > 0 for the border spacing along x
    yborder = 0.1 # increasing factor > 0 for the border spacing along y
    if max(xLinks) == min(xLinks):
        dx = max(yLinks) - min(yLinks)
    else:
        dx = max(xLinks) - min(xLinks)

    if max(yLinks) == min(yLinks):
        dy = max(xLinks) - min(xLinks)
    else:
        dy = max(yLinks) - min(yLinks)

    xmin = min(xLinks) - xborder*dx
    xmax = max(xLinks) + xborder*dx
    ymin = min(yLinks) - yborder*dy
    ymax = max(yLinks) + yborder*dy
    
    # Plot the macro node numbers
    if plotnumnodes == 1:
        similnodes = np.array(numNodes, numNodes)
        for i in range(numNodes):
            for j in range(numNodes):
                dist = math.sqrt((MacroNode[i].Coord[0]["x"] - MacroNode[j].Coord[0]["x"]) ^ 2 + (MacroNode[i].Coord[0]["y"] - MacroNode[j].Coord[0]["y"]) ^ 2)
                if dist < 0.01 * dx:
                    similnodes[i,j] = 1 # similar nodes if spatially very close

        #TODO
        pairnodeslist = gatherelements(similnodes) # gather nodes that are very close
        for ipair in range(len(pairnodeslist)):
            i = pairnodeslist[ipair,1]
            plt.text(MacroNode[i].Coord[0]["x"], MacroNode[i].Coord[0]["y"], '  ' + str(i), color = 'k', ha = 'left', fontname = fontname, fontsize = FS)
            if len(pairnodeslist[ipair]) > 1:
                for i in range(1, len(pairnodeslist[ipair])): # plot the node ID on the other side for clarity
                    plt.text(MacroNode[i].Coord[0]["x"], MacroNode[i].Coord[0]["y"], str(i) + '  ', color = 'k', ha = 'right', fontname = fontname, fontsize = FS)
    
    # Plot the legend
    if plotlegend == 1:
        xleg = xmin + 0.75 * (xmax - xmin)
        yleg = ymin + 0.95 * (ymax - ymin)
        wleg = 0.05 * (xmax - xmin) # legend symbol width
        hleg = 0.06 * (ymax - ymin) # height between symbols
        plt.plot([xleg, xleg + wleg], yleg * np.array([1, 1]), '-k', linewidth = minLW)
        plt.text(xleg + wleg, yleg,' < ' + str(mindem) +  ' veh/s', va = 'middle', ha = 'left', fontName = fontname, fontsize = 0.8 * FS)
        plt.plot([xleg, xleg + wleg], (yleg - hleg) * np.array([1, 1]), '-k', linewidth = maxLW)
        plt.text(xleg + wleg, yleg - hleg, ' > ' + str(maxdem) + ' veh/s', va = 'middle', ha = 'left', fontname = fontname, fontsize = 0.8 * FS)
        if sizingnodes == 1:
            plt.plot(xleg + 0.5 * wleg, yleg - 2 * hleg, 'o', color = 'k', markerfacecolor = 'k', markersize = minMS)
            plt.text(xleg + wleg, yleg - 2 * hleg,' < ' + str(minflow) + ' veh/s', va = 'middle', ha = 'left', fontname = fontname, fontsize = 0.8 * FS)
            plt.plot(xleg + 0.5 * wleg, yleg - 3 * hleg,'o', color = 'k', markerfacecolor = 'k', markersize = maxMS)
            plt.text(xleg + wleg, yleg - 3 * hleg, '  > ' + str(maxflow) + ' veh/s', va = 'middle', ha = 'left', fontname = fontname, fontsize = 0.8 * FS)

    plt.axis([xmin, xmax, ymin, ymax])
    plt.axis('off')
