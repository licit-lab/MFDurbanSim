import matplotlib.pyplot as plt
import matplotlib.colors
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

    # Reservoir colors
    # for r = ResList:
    #     ResAdj {r} = intersect(Reservoir(r).AdjacentRes, ResList)
    #
    # colorRes = plt.vertexcoloring(ResAdj, len(cmap(:, 1)))

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
        for r in range(len(Reservoir)):
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

                plt.fill(xResbp, yResbp, "b", ec = 'none', alpha = 0.5)
                plt.plot(xResbp, yResbp, "b")

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

def plotResBallAcc(t, Reservoir, SimulTime, ResRadius, coordscale):
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
        for dc in range(len(Reservoir[r].DataCommon)):
            if Reservoir[r].DataCommon[dc]["AvgTripLength"] != 0:
                flow.append(Reservoir[r].MaxProd[0]["value"] / Reservoir[r].DataCommon[dc]["AvgTripLength"])
        listMaxFlow.append(max(flow))

    maxflow = max(listMaxFlow)

    for r in range(numRes):
        xResC = coordscale[0] * (Reservoir[r].Centroid[0]["x"] - x0) / dx0
        yResC = coordscale[1] * (Reservoir[r].Centroid[0]["y"] - y0) / dx0

        xList.append(xResC)
        yList.append(yResC)

        # Plot flow exchanges
        if r < numRes: # & r2>rto avoid flow line duplication
            for i in range(len(Reservoir[r].AdjacentResID)):
                adjID = Reservoir[r].AdjacentResID[i]
                if adjID > Reservoir[r].ID :
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
        accratio = Reservoir[r].DataCommon[timeID]["Acc"] / Reservoir[r].MaxAcc[0]["value"]
        heightlevel = accratio * 2 * ResRadius
        th0 = math.asin((heightlevel - ResRadius) / ResRadius)
        th = list(np.arange(-math.pi - th0, th0 + step, step))
        x = [xResC + ResRadius * math.cos(element) for element in th]
        y = [yResC + ResRadius * math.sin(element) for element in th]

        plt.fill(x, y, 'k', ec = 'none')
        plt.text(xResC, yResC, r'$R_{' + str(r + 1) + '}$' + '\n' + str(round(Reservoir[r].DataCommon[timeID]["Acc"])), ha = 'center', color = txtcolor, fontname = fontname, fontweight = 'bold', fontsize = FS)

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

def plotResBallAccPerRoute(t, Reservoir, Route, SimulTime, ResRadius, coordscale):
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
        for dc in range(len(Reservoir[r].DataCommon)):
            if Reservoir[r].DataCommon[dc]["AvgTripLength"] != 0:
                flow.append(Reservoir[r].MaxProd[0]["value"] / Reservoir[r].DataCommon[dc]["AvgTripLength"])
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
        angstart = 0
        k_r = 0
        for iroute in range(numRoutes):
            for iRouteSect in range(len(Reservoir[r].RouteSection)):
                accratio = Reservoir[r].RouteSection[iRouteSect].Data[timeID]["Acc"] / Reservoir[r].MaxAcc[0]["value"]
                angend = angstart + accratio * 2 * math.pi
                thRoute = list(np.arange(angstart, angend + step, step))
                x = [xResC + ResRadius * math.cos(element) for element in thRoute]
                y = [yResC + ResRadius * math.sin(element) for element in thRoute]
                angstart = angend

                if iRouteSect in LegList: # add to the legend
                    for i in range(len(x)):
                        plt.fill([xResC, x[i]], [yResC, y[i]], color = cmap[k_r], ec = 'none')
                else:
                    for i in range(len(x)):
                        hf.append(plt.fill([xResC, x[i]], [yResC, y[i]], color = cmap[k_r], ec = 'none'))
                    LegList.append(iRouteSect)
            k_r = k_r + 1
        plt.text(xResC, yResC, r'$R_{' + str(r + 1) + '}$' + '\n' + str(round(Reservoir[r].DataCommon[timeID]["Acc"])), ha = 'center', color = txtcolor, fontname = fontname, fontweight = 'bold', fontsize = FS)

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
        strleg = '[ '
        for iroute in range(numRoutes):
            for i in range(len(Route[iroute].ResPath)):
                strleg += Route[iroute].ResPath[i]["ID"] + ' '
        strleg += ']'
        for i in range(len(hf)):
            plt.legend(hf[i], strleg, loc = legloc, fontsize = FS)


