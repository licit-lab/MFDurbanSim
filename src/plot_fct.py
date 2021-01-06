import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import matplotlib.colors as colors
from matplotlib import cm
from matplotlib.lines import Line2D
import matplotlib.animation as animation

import math
import numpy as np

DEBUG = False


def plot_res_ball_config(reservoirs, plot_borders, res_radius, coord_scale):
    # Plot the reservoirs configuration (ball shapes and connections)
    # INPUTS
    # ---- reservoirs: reservoirs list
    # ---- plot_borders: boolean, plot the reservoirs borders if = 1
    # ---- res_radius: scalar, radius of the disk used to symbolize reservoirs
    # ---- coord_scale: 1 - by - 2 vector, scale factors along x and y axis [fx fy]

    num_res = len(reservoirs)
    flow_space = 0   # spacing between flow lines
    c_map0 = np.array([(51, 51, 255), (0, 204, 51), (204, 0, 0), (204, 153, 0), (153, 0, 102), (51, 153, 153),
                      (204, 102, 204), (204, 204, 102)]) / 255  # default

    # Normalization of reservoirs coordinates
    x0 = reservoirs[0].Centroid[0]["x"]
    y0 = reservoirs[0].Centroid[0]["y"]
    x1 = 0
    y1 = 0

    for res in reservoirs:
        if res.ID == reservoirs[0].AdjacentResID[0] or len(reservoirs) == 1:
            x1 = res.Centroid[0]["x"]
            y1 = res.Centroid[0]["y"]

    dx0 = max([abs(x1 - x0), abs(y1 - y0)])
    dx0 = (0 < dx0) * dx0 + (0 == dx0) * 1

    x_links = []
    y_links = []
    if plot_borders == 1:
        # Plot the reservoirs
        for r in range(num_res):
            if len(reservoirs[r].BorderPoints) != 0:
                x_res_bp = []
                y_res_bp = []
                for bp in reservoirs[r].BorderPoints:
                    x_res_bp_tmp = (coord_scale[0] * bp["x"] - x0) / dx0
                    y_res_bp_tmp = (coord_scale[1] * bp["y"] - y0) / dx0
                    x_res_bp.append(x_res_bp_tmp)
                    y_res_bp.append(y_res_bp_tmp)

                    x_links.append(x_res_bp_tmp)
                    y_links.append(y_res_bp_tmp)

                plt.fill(x_res_bp, y_res_bp, color=c_map0[r], ec='none', alpha=0.5)
                plt.plot(x_res_bp, y_res_bp, color=c_map0[r])

    x_list = []
    y_list = []
    for r in range(num_res):
        x_res_c = coord_scale[0] * (reservoirs[r].Centroid[0]["x"] - x0) / dx0
        y_res_c = coord_scale[1] * (reservoirs[r].Centroid[0]["y"] - y0) / dx0

        x_list.append(x_res_c)
        y_list.append(y_res_c)

        # Plot flow exchanges
        if r < num_res:  # to avoid flow line duplication
            for adjID in reservoirs[r].AdjacentResID:
                for res2 in reservoirs:
                    if adjID == res2.ID:
                        x_res_adj = coord_scale[0] * (res2.Centroid[0]["x"] - x0) / dx0
                        y_res_adj = coord_scale[1] * (res2.Centroid[0]["y"] - y0) / dx0

                        ang = math.atan2(x_res_adj - y_res_c, x_res_adj - x_res_c) + math.pi / 2

                        dx = flow_space * math.cos(ang)
                        dy = flow_space * math.sin(ang)

                        xi1 = x_res_c + dx
                        yi1 = y_res_c + dy
                        xj1 = x_res_adj + dx
                        yj1 = y_res_adj + dy

                        # Effective flow from Ri to Rj
                        plt.plot([xi1, xj1], [yi1, yj1], '-', color='k')

        # Plot reservoirs disk
        step = 0.01
        th = list(np.arange(0, 2 * math.pi + step, step))
        x = [x_res_c + res_radius * math.cos(element) for element in th]
        y = [y_res_c + res_radius * math.sin(element) for element in th]

        plt.fill(x, y, 'k', edgecolor='none')
        plt.text(x_res_c, y_res_c, f'$R_{str(r + 1)}$',
                 ha='center', color='w', fontname='arial', fontweight='bold', fontsize=18)

    # Plot size
    x_border = 0.1  # increasing factor > 0 for the border spacing along x
    y_border = 0.1  # increasing factor > 0 for the border spacing along x
    if plot_borders == 1:
        if max(x_links) == min(x_links):
            dx = max(y_links) - min(y_links)
        else:
            dx = max(x_links) - min(x_links)

        if max(y_links) == min(y_links):
            dy = max(x_links) - min(x_links)
        else:
            dy = max(y_links) - min(y_links)

        x_min = min(x_links) - x_border * dx
        x_max = max(x_links) + x_border * dx
        y_min = min(y_links) - y_border * dy
        y_max = max(y_links) + y_border * dy
    else:
        if max(x_list) == min(x_list):
            dx = max(y_list) - min(y_list)
        else:
            dx = max(x_list) - min(x_list)

        if max(y_list) == min(y_list):
            dy = max(x_list) - min(x_list)
        else:
            dy = max(y_list) - min(y_list)

        x_min = min(x_list) - res_radius - x_border * dx
        x_max = max(x_list) + res_radius + x_border * dx
        y_min = min(y_list) - res_radius - y_border * dy
        y_max = max(y_list) + res_radius + y_border * dy

    plt.axis([x_min, x_max, y_min, y_max])
    plt.axis('off')


def plot_res_ball_acc(t, reservoirs, res_output, simul_time, res_radius, coord_scale):
    # Plot the state of reservoirs at time t (accumulation and flow)
    # INPUTS
    # ---- t           : scalar, time [s]
    # ---- reservoirs   : reservoirs list
    # ---- simul_time   : vector, simulation time [s]
    # ---- res_radius   : scalar, radius of the disk used to symbolize reservoirs
    # ---- coord_scale  : 1-by-2 vector, scale factors along x and y axis [fx fy]

    num_res = len(reservoirs)
    time_step = simul_time[1] - simul_time[0]
    time_id = 0

    # Index of the current time
    for i in range(len(simul_time)):
        if t == simul_time[i] or abs(t - simul_time[i]) <= time_step / 2:
            time_id = i

    # Options
    font_name = 'arial'
    font_size = 16
    t_label = f't = {str(t)} s'
    show_flow_val = 1
    txt_color = [0.9, 0.9, 1]
    flow_space = 0.2    # spacing between flow lines
    max_width = 30      # flow line max width

    x_list = []
    y_list = []

    # Normalization of reservoirs coordinates
    x0 = reservoirs[0].Centroid[0]["x"]
    y0 = reservoirs[0].Centroid[0]["y"]
    x1 = 0
    y1 = 0

    for res in reservoirs:
        if res.ID == reservoirs[0].AdjacentResID[0]:
            x1 = res.Centroid[0]["x"]
            y1 = res.Centroid[0]["y"]

    dx0 = max([abs(x1 - x0), abs(y1 - y0)])
    dx0 = (0 < dx0) * dx0 + (0 == dx0) * 1

    # Define max flow for plotting purpose
    for r in range(num_res):
        flow = []
        avg_trip_length = reservoirs[r].Data[time_id]["AvgTripLength"]

        if avg_trip_length != 0:
            flow.append(reservoirs[r].MFDsetting[0]["MaxProd"] / avg_trip_length)

    max_flow = max(flow)

    for r in range(num_res):
        x_res_c = coord_scale[0] * (reservoirs[r].Centroid[0]["x"] - x0) / dx0
        y_res_c = coord_scale[1] * (reservoirs[r].Centroid[0]["y"] - y0) / dx0

        x_list.append(x_res_c)
        y_list.append(y_res_c)

        # Plot flow exchanges
        if r < num_res:     # to avoid flow line duplication
            for adjID in reservoirs[r].AdjacentResID:
                for res2 in reservoirs:
                    if adjID == res2.ID:
                        x_res_adj = coord_scale[0] * (res2.Centroid[0]["x"] - x0) / dx0
                        y_res_adj = coord_scale[1] * (res2.Centroid[0]["y"] - y0) / dx0

                        ang = math.atan2(y_res_adj - y_res_c, x_res_adj - x_res_c) + math.pi / 2

                        dx = flow_space * math.cos(ang)
                        dy = flow_space * math.sin(ang)

                        x_res1 = x_res_c + dx
                        y_res1 = y_res_c + dy
                        x_res2 = x_res_c - dx
                        y_res2 = y_res_c - dy
                        x_res_adj1 = x_res_adj + dx
                        y_res_adj1 = y_res_adj + dy
                        x_res_adj2 = x_res_adj - dx
                        y_res_adj2 = y_res_adj - dy

                        # Effective flow from Ri to Rj
                        outflow_ij = 0.35    # sum(reservoirs(r).OutflowPerResPerDest(x_res_adj,:, time_id))
                        line_width = max([outflow_ij / max_flow * max_width, 0.1])
                        plt.plot([x_res1, x_res_adj1], [y_res1, y_res_adj1], '-', color='k', linewidth=line_width)
                        if show_flow_val == 1:
                            plt.text(1 / 3 * x_res1 + 2 / 3 * x_res_adj1, 1 / 3 * y_res1 + 2 / 3 * y_res_adj1,
                                     str(outflow_ij), rotation=ang * 180 / math.pi, ha='center', color='k',
                                     backgroundcolor='w', fontname=font_name, fontsize=0.5 * font_size)

                        # Effective flow from Rj to Ri
                        outflow_ji = 0.2    # sum(reservoirs(r2).OutflowPerResPerDest(r,:, time_id))
                        line_width = max([outflow_ji / max_flow * max_width, 0.1])
                        plt.plot([x_res2, x_res_adj2], [y_res2, y_res_adj2], '-', color='k', linewidth=line_width)
                        if show_flow_val == 1:
                            plt.text(2 / 3 * x_res2 + 1 / 3 * x_res_adj2, 2 / 3 * y_res2 + 1 / 3 * y_res_adj2, 
                                     str(outflow_ji), rotation=ang * 180 / math.pi, ha='center', color='k', 
                                     backgroundcolor='w', fontname=font_name, fontsize=0.5 * font_size)

        # Plot reservoirs disk
        step = 0.01
        th = list(np.arange(0, 2 * math.pi + step, step))
        x = [x_res_c + res_radius * math.cos(element) for element in th]
        y = [y_res_c + res_radius * math.sin(element) for element in th]
        plt.fill(x, y, 'k', edgecolor='none')

        # Plot accumulation evolution
        acc_ratio = reservoirs[r].Data[time_id]["Acc"] / reservoirs[r].MFDsetting[0]["MaxAcc"]
        height_level = acc_ratio * 2 * res_radius
        th0 = math.asin((height_level - res_radius) / res_radius)
        th = list(np.arange(-math.pi - th0, th0 + step, step))
        x = [x_res_c + res_radius * math.cos(element) for element in th]
        y = [y_res_c + res_radius * math.sin(element) for element in th]

        str_acc = str(round(reservoirs[r].Data[time_id]["Acc"]))
        plt.fill(x, y, 'k', ec='none')
        plt.text(x_res_c, y_res_c, f'$R_{str(r + 1)}$' + '\n' + str_acc,
                 ha='center', color=txt_color, fontname=font_name, fontweight='bold', fontsize=font_size)

    # Plot size
    x_border = 0.05     # increasing factor > 0 for the border spacing along x
    y_border = 0.1      # increasing factor > 0 for the border spacing along x
    if max(x_list) == min(x_list):
        dx = max(y_list) - min(y_list)
    else:
        dx = max(x_list) - min(x_list)

    if max(y_list) == min(y_list):
        dy = max(x_list) - min(x_list)
    else:
        dy = max(y_list) - min(y_list)

    x_min = min(x_list) - res_radius - x_border * dx
    x_max = max(x_list) + res_radius + x_border * dx
    y_min = min(y_list) - res_radius - y_border * dy
    y_max = max(y_list) + res_radius + y_border * dy

    plt.text((x_min + x_max) / 2, y_max, t_label,
             color=[0.5, 0.5, 0.5], ha='center', va='top', fontname=font_name, fontsize=font_size, fontweight='bold')
    plt.axis([x_min, x_max, y_min, y_max])
    plt.axis('off')


def plot_res_ball_acc_per_route(t, reservoirs, res_output, routes, simul_time, res_radius, coord_scale):
    # Plot the state of reservoirs at time t(accumulation and flow)
    # Plot accumulation ratio of each route in the reservoirs
    #
    # INPUTS
    # ---- t: scalar, time[s]
    # ---- reservoirs: reservoirs structure
    # ---- routes: routes structure
    # ---- simul_time: vector, simulation time[s]
    # ---- res_radius: scalar, radius of the disk used to symbolize reservoirs
    # ---- coord_scale: 1 - by - 2 vector, scale factors along x and y axis[fx fy]

    num_res = len(reservoirs)
    num_routes = len(routes)

    # Index of the current time
    time_step = simul_time[1] - simul_time[0]
    time_id = 0
    for i in range(len(simul_time)):
        if t == simul_time[i] or abs(t - simul_time[i]) <= time_step / 2:
            time_id = i

    # Options
    font_name = 'Arial' 
    font_size = 16    
    c_map0 = np.array([(51, 51, 255), (0, 204, 51), (204, 0, 0), (204, 153, 0), (153, 0, 102), (51, 153, 153), 
                      (204, 102, 204), (204, 204, 102)]) / 255 
    txt_color = [0.9, 0.9, 1]
    t_label = f't = {str(t)} s'
    show_legend = 1
    show_flow_val = 1  

    c_map = c_map0

    while np.size(c_map, 1) < num_routes:
        c_map = np.vstack(c_map, c_map0)

    flow_space = 0.2  # spacing between flow lines
    max_width = 30   # flow line max width

    x_list = []
    y_list = []

    # Normalization of reservoirs coordinates
    x0 = reservoirs[0].Centroid[0]["x"]
    y0 = reservoirs[0].Centroid[0]["y"]
    x1 = 0
    y1 = 0

    for res in reservoirs:
        if res.ID == reservoirs[0].AdjacentResID[0]:
            x1 = res.Centroid[0]["x"]
            y1 = res.Centroid[0]["y"]

    dx0 = max([abs(x1 - x0), abs(y1 - y0)])
    dx0 = (0 < dx0) * dx0 + (0 == dx0) * 1

    # Define max flow
    list_max_flow = []    # max flow per reservoirs
    for r in range(num_res):
        flow = []
        avg_trip_length = res_output[r]["ReservoirData"][time_id]["AvgTripLength"]

        if avg_trip_length != 0:
            flow.append(reservoirs[r].MFDsetting[0]["MaxProd"] / avg_trip_length)

        list_max_flow.append(max(flow))

    max_flow = max(list_max_flow)

    hf = []
    str_legend = []
    legend_list = []

    for r in range(num_res):
        x_res_c = coord_scale[0] * (reservoirs[r].Centroid[0]["x"] - x0) / dx0
        y_res_c = coord_scale[1] * (reservoirs[r].Centroid[0]["y"] - y0) / dx0

        x_list.append(x_res_c)
        y_list.append(y_res_c)

        # Plot flow exchanges
        if r < num_res:  # avoid flow line duplication
            for adjID in reservoirs[r].AdjacentResID:
                for j in range(num_res):
                    if adjID == reservoirs[j].ID:
                        x_res_adj = coord_scale[0] * (reservoirs[j].Centroid[0]["x"] - x0) / dx0
                        y_res_adj = coord_scale[1] * (reservoirs[j].Centroid[0]["y"] - y0) / dx0

                        ang = math.atan2(y_res_adj - y_res_c, x_res_adj - x_res_c) + math.pi / 2

                        dx = flow_space * math.cos(ang)
                        dy = flow_space * math.sin(ang)

                        x_res1 = x_res_c + dx
                        y_res1 = y_res_c + dy
                        x_res2 = x_res_c - dx
                        y_res2 = y_res_c - dy
                        x_res_adj1 = x_res_adj + dx
                        y_res_adj1 = y_res_adj + dy
                        x_res_adj2 = x_res_adj - dx
                        y_res_adj2 = y_res_adj - dy

                        # Effective flow from Ri to Rj
                        # TODO
                        outflow_ij = 0.8  # sum(reservoirs(r).OutflowPerResPerDest(x_res_adj,:, time_id))
                        line_width = max([outflow_ij / max_flow * max_width, 0.1])
                        plt.plot([x_res1, x_res_adj1], [y_res1, y_res_adj1],
                                 '-', color='k', linewidth=line_width, zorder=0)
                        if show_flow_val == 1:
                            plt.text(1 / 3 * x_res1 + 2 / 3 * x_res_adj1, 1 / 3 * y_res1 + 2 / 3 * y_res_adj1,
                                     str(outflow_ij),
                                     rotation=ang * 180 / math.pi, ha='center', color='k', backgroundcolor='w',
                                     fontname=font_name, fontsize=0.5 * font_size)

                        # Effective flow from Rj to Ri
                        # TODO
                        outflow_ji = 0.2  # sum(reservoirs(r2).OutflowPerResPerDest(r,:, time_id))
                        line_width = max([outflow_ji / max_flow * max_width, 0.1])
                        plt.plot([x_res2, x_res_adj2], [y_res2, y_res_adj2],
                                 '-', color='k', linewidth=line_width, zorder=0)
                        if show_flow_val == 1:
                            plt.text(2 / 3 * x_res2 + 1 / 3 * x_res_adj2, 2 / 3 * y_res2 + 1 / 3 * y_res_adj2,
                                     str(outflow_ji),
                                     rotation=ang * 180 / math.pi, ha='center', color='k', backgroundcolor='w',
                                     fontname=font_name, fontsize=0.5 * font_size)

        # Plot reservoirs disk
        step = 0.01
        th = list(np.arange(0, 2 * math.pi + step, step))
        x = [x_res_c + res_radius * math.cos(element) for element in th]
        y = [y_res_c + res_radius * math.sin(element) for element in th]
        plt.fill(x, y, 'grey', edgecolor='none')

        # Plot accumulation evolution
        ang_start = 0
        k_r = 0
        for route in routes:
            for i_routeSect in range(len(res_output[r]["DataPerRoute"])):
                route_sect = res_output[r]["DataPerRoute"][i_routeSect]

                if route_sect["IDRoute"] == route.ID:
                    acc_ratio = route_sect["Data"][time_id]["Acc"] / reservoirs[r].MFDsetting[0]["MaxAcc"]
                    ang_end = ang_start + acc_ratio * 2 * math.pi
                    th_route = list(np.arange(ang_start, ang_end + step, step))
                    x = [x_res_c + res_radius * math.cos(element) for element in th_route]
                    y = [y_res_c + res_radius * math.sin(element) for element in th_route]
                    ang_start = ang_end

                    if i_routeSect in legend_list:  # add to the legend
                        for i in range(len(x)):
                            hf.append(plt.fill([x_res_c, x[i]], [y_res_c, y[i]], color=c_map[k_r], ec='none'))
                    else:
                        str_label = '[ '
                        for i in range(len(route.CrossedReservoirs)):
                            str_label += route.CrossedReservoirs[i].ID + ' '

                        str_label += ']'

                        for i in range(len(x)):
                            hf.append(plt.fill([x_res_c, x[i]], [y_res_c, y[i]],
                                               color=c_map[k_r], ec='none', label=str_label))
                        legend_list.append(i_routeSect)
            k_r += 1

        plt.text(x_res_c, y_res_c,
                 f'$R_{str(r + 1)}$' + '\n' + str(round(res_output[r]["ReservoirData"][time_id]["Acc"])),
                 ha='center', color=txt_color, fontname=font_name, fontweight='bold', fontsize=font_size)

    # Plot size
    x_border = 0.05  # increasing factor > 0 for the border spacing along x
    y_border = 0.1  # increasing factor > 0 for the border spacing along x
    if max(x_list) == min(x_list):
        dx = max(y_list) - min(y_list)
    else:
        dx = max(x_list) - min(x_list)

    if max(y_list) == min(y_list):
        dy = max(x_list) - min(x_list)
    else:
        dy = max(y_list) - min(y_list)

    x_min = min(x_list) - res_radius - x_border * dx
    x_max = max(x_list) + res_radius + x_border * dx
    y_min = min(y_list) - res_radius - y_border * dy
    y_max = max(y_list) + res_radius + y_border * dy

    plt.text((x_min + x_max) / 2, y_max, t_label,
             color=[0.5, 0.5, 0.5], ha='center', va='top', fontname=font_name, fontsize=font_size, fontweight='bold')
    plt.axis([x_min, x_max, y_min, y_max])
    plt.axis('off')

    if show_legend == 1:
        plt.legend(hf, str_legend, bbox_to_anchor=(1.05, 1), loc='center right', borderaxespad=0., fontsize=font_size)


def plot_res_route_dem(reservoirs, routes, nodes, demand, demand_type, plot_charact):
    # Plot the number or demand of a given route list crossing the reservoirs
    # INPUTS
    # ---- reservoirs   : reservoirs structure
    # ---- routes       : routes structure
    # ---- plot_charact : string, 'number' or 'demand'

    num_res = len(reservoirs)

    # Choice of a colormap
    nb_color = 800
    rd_yl_gn = cm.get_cmap('RdYlGn', nb_color)

    # Options
    txt_color = [0.1, 0.1, 0]
    font_name = 'Arial'
    font_size = 18
    line_width = 2

    x_links = []
    y_links = []
    res_values = []

    # demand per reservoirs
    demand_per_res = []

    # TODO
    if demand_type == "FlowDemand":
        for dem in demand:
            flow_demand = 0
            for dem_t in dem.Demands['Data']:
                flow_demand += dem_t
            flow_demand /= len(dem.Demands)

            for node in nodes:
                if node is dem.OriginMacroNode or node is dem.DestMacroNode:
                    res_id = node.ResID[0]
                    demand_per_res.append({"ID": res_id, "demand": demand})
    # TODO
    elif demand_type == "DiscreteDemand":
        toto = 0

    for res in reservoirs:
        nb_routes = 0
        total_dem = 0

        for route in routes:
            for cr in route.CrossedReservoirs:
                if res.ID == cr.ID:
                    nb_routes += 1

        for dem_res in demand_per_res:
            if res.ID == dem_res["ID"]:
                total_dem = dem_res["demand"]

        if plot_charact == 'number':
            res_values.append(nb_routes)
        elif plot_charact == 'demand':
            res_values.append(total_dem)

    maxvalue = max(res_values)

    # Plot reservoirs
    for r in range(num_res):
        ratio = res_values[r] / maxvalue
        ind_color = max([math.floor(ratio * nb_color), 1])
        color_i = rd_yl_gn(ind_color)

        if len(reservoirs[r].BorderPoints) != 0:
            x_res_bp = []
            y_res_bp = []
            for bp in reservoirs[r].BorderPoints:
                x_res_bp.append(bp["x"])
                y_res_bp.append(bp["y"])

                x_links.append(bp["x"])
                y_links.append(bp["y"])

            plt.fill(x_res_bp, y_res_bp, color=color_i, ec='none', alpha=0.5)
            plt.plot(x_res_bp, y_res_bp, '-', color=color_i, linewidth=line_width)

    for r in range(num_res):
        xr = reservoirs[r].Centroid[0]["x"]
        yr = reservoirs[r].Centroid[0]["y"]
        plt.text(xr, yr, f'$R_{str(r + 1)}$' + '\n' + str(res_values[r]),
                 ha='center', color=txt_color, fontname=font_name, fontweight='bold', fontsize=font_size)

    # Plot size
    x_border = 0.1  # increasing factor > 0 for the border spacing along x
    y_border = 0.1  # increasing factor > 0 for the border spacing along x
    if max(x_links) == min(x_links):
        dx = max(y_links) - min(y_links)
    else:
        dx = max(x_links) - min(x_links)

    if max(y_links) == min(y_links):
        dy = max(x_links) - min(x_links)
    else:
        dy = max(y_links) - min(y_links)

    x_min = min(x_links) - x_border*dx
    x_max = max(x_links) + x_border*dx
    y_min = min(y_links) - y_border*dy
    y_max = max(y_links) + y_border*dy

    # #hcb = plt.colorbar()
    # if plot_charact == 'number':
    #     hcb.Label.String = 'Number of routes [-]'
    #     str_title = 'Number of routes \rm[-]'
    # elif plot_charact == 'demand':
    #     hcb.Label.String = 'Cumul. mean demand on routes [veh/s]'
    #     str_title = 'Cumul. mean demand on routes \rm[veh/s]'

    plt.axis([x_min, x_max, y_min, y_max])
    plt.axis('off')


def plot_res_net_speed(fig, ax, t, reservoirs, speed_range, simul_time, res_output, mode='VL'):
    # Plot the state of reservoirs at time t(mean speed), with links and/or shape borders
    #
    # INPUTS
    # ---- ax: axes of the figure
    # ---- t: scalar, time[s]
    # ---- reservoirs: reservoirs structure
    # ---- speed_range: vector[V_min V_max], speed range[m/s] to define the colormap
    # ---- simul_time:
    # ---- res_output:
    # ---- mode: string designating for which mode we want this graphic, VL by default

    num_res = len(reservoirs)

    # Verify mode
    if (mode != 'VL' and mode != 'BUS'):
        print("WARNING: Mode is not known")

    # Verify plot information
    res_bp_filled = True
    res_centroid_filled = True
    for r in reservoirs:
        if r.BorderPoints is None:
            res_bp_filled = False
        if r.Centroid is None:
            res_centroid_filled = False

    if not res_bp_filled:
        print("WARNING: Border Points are missing in reservoirs.")
    if not res_centroid_filled:
        print("WARNING: Centroid coordinates are missing.")

    # Index of the current time
    time_step = simul_time[1] - simul_time[0]
    time_id = 0
    for i in range(len(simul_time)):
        if t == simul_time[i] or abs(t - simul_time[i]) <= time_step / 2:
            time_id = i

    # Choice of a colormap
    nb_color = 20
    rd_yl_gn = cm.get_cmap('RdYlGn', nb_color)

    # Plot colorbar
    v_max = speed_range[1] * 3.6
    c_bar = plt.colorbar(cm.ScalarMappable(norm=colors.Normalize(0, v_max), cmap=rd_yl_gn))
    c_bar.ax.set_ylabel('Speed [km/h]', rotation=-90, va="bottom")

    # Plot title
    t_label = f"Mean speed at t = {t} s"
    title = plt.title(t_label)

    # Slider
    ax_time = plt.axes([0.1, 0.05, 0.6, 0.03])
    slider_time = widgets.Slider(ax_time, 'Time', simul_time[0], simul_time[-1], valinit=t, valstep=10)

    txt_color = [0.1, 0.1, 0]
    font_name = 'Arial'
    font_size = 16
    line_width = 1

    x_links = []
    y_links = []

    # Plot reservoirs
    list_res_fill = []
    list_res_cont = []
    list_ms_txt = []
    for r in range(num_res):
        if mode in res_output[r]['ReservoirData'][time_id]["MeanSpeed"]:
            mean_speed = res_output[r]['ReservoirData'][time_id]["MeanSpeed"][mode]
        else:
            print(f'WARNING: Mode {mode} is not present in this example.')

        speed_ratio = (mean_speed - speed_range[0]) / (speed_range[1] - speed_range[0])
        ind_color = min([max([math.floor(speed_ratio * nb_color), 1]), nb_color])
        color_i = rd_yl_gn(ind_color)

        if DEBUG:
            print(f'mean speed : {mean_speed}')
            print(f'speed ratio : {speed_ratio}')
            print(f'ind color : {ind_color}')

        if res_bp_filled:
            x_res_bp = []
            y_res_bp = []
            for bp in reservoirs[r].BorderPoints:
                x_res_bp.append(bp["x"])
                y_res_bp.append(bp["y"])

                x_links.append(bp["x"])
                y_links.append(bp["y"])

            list_res_fill.append(ax.fill(x_res_bp, y_res_bp, color=color_i, ec='none', alpha=0.3))
            list_res_cont.append(ax.plot(x_res_bp, y_res_bp, '-', color=color_i, linewidth=line_width))

            # Plot mean speed
            if res_centroid_filled:
                xr = reservoirs[r].Centroid[0]["x"]
                yr = reservoirs[r].Centroid[0]["y"]
            else:
                bp_x = []
                bp_y = []
                for bp in reservoirs[r].BorderPoints:
                    bp_x.append(bp["x"])
                    bp_y.append(bp["y"])

                max_x = max(bp_x)
                min_x = min(bp_x)
                max_y = max(bp_y)
                min_y = min(bp_y)

                xr = (max_x + min_x) / 2
                yr = (max_y + min_y) / 2

            mean_speed_kmh = round(mean_speed * 3.6)
            list_ms_txt.append(ax.text(xr, yr, f'$R_{str(r + 1)}$ \n {mean_speed_kmh} km/h', ha='center',
                                       color=txt_color, fontname=font_name, fontweight='bold', fontsize=font_size))

    # Plot size
    x_border = 0.1  # increasing factor > 0 for the border spacing along x
    y_border = 0.1  # increasing factor > 0 for the border spacing along x
    if max(x_links) == min(x_links):
        dx = max(y_links) - min(y_links)
    else:
        dx = max(x_links) - min(x_links)

    if max(y_links) == min(y_links):
        dy = max(x_links) - min(x_links)
    else:
        dy = max(y_links) - min(y_links)

    x_min = min(x_links) - x_border * dx
    x_max = max(x_links) + x_border * dx
    y_min = min(y_links) - y_border * dy
    y_max = max(y_links) + y_border * dy

    ax.axis([x_min, x_max, y_min, y_max])
    ax.axis('off')


    def update_time(val):
        new_time = int(slider_time.val)

        # Index of the current time
        new_time_id = 0
        for i in range(len(simul_time)):
            if new_time == simul_time[i] or abs(new_time - simul_time[i]) <= time_step / 2:
                new_time_id = i

        title.set_text(f"Mean speed at t = {new_time} s")

        for r in range(len(list_res_fill)):
            # Previous draw invisible
            list_res_fill[r][0].set_visible(False)
            list_res_cont[r][0].set_visible(False)
            list_ms_txt[r].set_visible(False)

            # New color
            ms = res_output[r]['ReservoirData'][new_time_id]["MeanSpeed"][mode]
            sr = (ms - speed_range[0]) / (speed_range[1] - speed_range[0])
            i_color = min([max([math.floor(sr * nb_color), 1]), nb_color])
            c_i = rd_yl_gn(i_color)

            # New reservoir polygons
            x = [element[0] for element in list_res_fill[r][0].xy]
            y = [element[1] for element in list_res_fill[r][0].xy]

            list_res_fill[r] = ax.fill(x, y, color=c_i, ec='none', alpha=0.3)
            list_res_cont[r] = ax.plot(x, y, '-', color=c_i, linewidth=line_width)

            # New mean speed text
            x, y = list_ms_txt[r].get_position()

            ms_kmh = round(ms * 3.6)
            txt = f'$R_{str(r + 1)}$ \n {ms_kmh} km/h'

            list_ms_txt[r] = ax.text(x, y, txt, ha='center', color=txt_color, fontname=font_name,
                                     fontweight='bold', fontsize=font_size)

        plt.draw()

    slider_time.on_changed(update_time)

    plt.show()


def plot_network(ax, reservoirs, nodes, routes, options=None):
    # Plot the real network configuration with reservoirs, nodes and route path.
    # INPUTS
    # ---- ax                   : figure
    # ---- reservoirs           : reservoirs structure
    # ---- nodes                : nodes structure
    # ---- routes               : routes structure
    # ---- options              : plot options

    num_res = len(reservoirs)
    num_routes = len(routes)
    
    # Options
    if options is not None:
        plot_legend = options['legend']
        plot_res_names = options['res_names']
        plot_mn_names = options['mn_names']
        plot_res_color = options['res_color']
        plot_routes_color = options['routes_color']
        plot_mn_color = options['mn_color']
    else:
        plot_legend = True
        plot_res_names = True
        plot_mn_names = True
        plot_res_color = True
        plot_routes_color = True
        plot_mn_color = True

    font_name = 'Arial'
    font_size = 28
    marker_size = 8
    color_map_0 = np.array([(51, 51, 255), (0, 204, 51), (204, 0, 0), (204, 153, 0), (153, 0, 102), (51, 153, 153),
                            (204, 102, 204), (204, 204, 102)]) / 255

    default_color = [0.1, 0.1, 0]
    txt_color = [1, 1, 1]

    # Lines
    line_0 = np.array(['-', '--', ':', '-.'])

    while num_res > len(color_map_0):
        color_map_0 = np.concatenate((color_map_0, color_map_0))

    while num_routes > len(line_0):
        line_0 = np.concatenate((line_0, line_0))
        color_map_0 = np.concatenate((color_map_0, color_map_0))

    # Verify plot information
    res_bp_filled = True
    res_centroid_filled = True
    for r in reservoirs:
        if r.BorderPoints is None:
            res_bp_filled = False
        if r.Centroid is None:
            res_centroid_filled = False

    mn_coord_filled = True
    for mn in nodes:
        if mn.Coord is None:
            mn_coord_filled = False

    if not res_bp_filled:
        print("WARNING: Border Points are missing in reservoirs.")
    if not res_centroid_filled:
        print("WARNING: Centroid coordinates are missing.")
    if not mn_coord_filled:
        print("WARNING: Macro-nodes coordinates are missing.")

    # Plot the reservoirs
    x_links = None
    y_links = None
    if res_bp_filled:
        x_links = []
        y_links = []

    res_plot = []
    # Plot the reservoirs
    for r in range(num_res):
        if plot_res_color:
            color_r = color_map_0[r]
        else:
            color_r = default_color

        if res_bp_filled:
            x_res_bp = []
            y_res_bp = []
            for bp in reservoirs[r].BorderPoints:
                x_res_bp_tmp = bp["x"]
                y_res_bp_tmp = bp["y"]
                x_res_bp.append(x_res_bp_tmp)
                y_res_bp.append(y_res_bp_tmp)

                x_links.append(x_res_bp_tmp)
                y_links.append(y_res_bp_tmp)

            res_plot.append(ax.fill(x_res_bp, y_res_bp, color=color_r, ec='none', alpha=0.3))
            res_plot.append(ax.plot(x_res_bp, y_res_bp, color=color_r))
        else:
            if res_centroid_filled:
                res_plot.append(ax.plot(reservoirs[r].Centroid[0]["x"], reservoirs[r].Centroid[0]["y"], 'x',
                                        color=color_r))


    # Plot the routes
    legend_routes = []
    i = 1

    if mn_coord_filled:
        route_plot = []
        for route in routes:
            if plot_routes_color:
                color_i = color_map_0[i]
            else:
                color_i = default_color

            line_style_i = line_0[i]

            list_x = []
            list_y = []
            for node in route.NodePath:
                xn = node.Coord[0]["x"]
                yn = node.Coord[0]["y"]
                list_x.append(xn)
                list_y.append(yn)

            list_res_id = []
            for res in route.CrossedReservoirs:
                list_res_id.append(res.ID)

            for j in range(len(list_x) - 1):
                route_plot.append(ax.annotate("",
                                              xy=(list_x[j], list_y[j]), xycoords='data',
                                              xytext=(list_x[j+1], list_y[j+1]), textcoords='data',
                                              arrowprops=dict(arrowstyle="<-", color=color_i,
                                                              shrinkA=5, shrinkB=5,
                                                              patchA=None, patchB=None,
                                                              connectionstyle='arc3,rad=-0.3',
                                                              linestyle=line_style_i)))

            i += 1

            legend_routes.append(Line2D([0], [0], color=color_i, linestyle=line_style_i, label=route.ID))

    # Plot the macro nodes
    legend_mn = []

    if plot_mn_color:
        color_entry = color_map_0[-5, :]
        color_ext_entry = color_map_0[-1, :]
        color_exit = color_map_0[-4, :]
        color_ext_exit = color_map_0[-2, :]
        color_border = color_map_0[-3, :]
    else:
        color_entry = default_color
        color_ext_entry = default_color
        color_exit = default_color
        color_ext_exit = default_color
        color_border = default_color

    marker_size_1 = marker_size
    marker_size_2 = 1.25 * marker_size
    marker_size_3 = 0.75 * marker_size

    entry_nodes_list = []
    ext_entry_nodes_list = []
    exit_nodes_list = []
    ext_exit_nodes_list = []
    border_nodes_list = []

    for mn in nodes:
        if mn.Type == 'origin':
            entry_nodes_list.append(mn)
        elif mn.Type == 'externalentry':
            ext_entry_nodes_list.append(mn)
        elif mn.Type == 'destination':
            exit_nodes_list.append(mn)
        elif mn.Type == 'externalexit':
            ext_exit_nodes_list.append(mn)
        else:
            border_nodes_list.append(mn)

    if mn_coord_filled:
        node_plot = []
        for node in exit_nodes_list:
            node_plot.append(ax.plot(node.Coord[0]["x"], node.Coord[0]["y"], 'o',
                             color=color_exit, markerfacecolor=color_exit, markersize=marker_size_2))
        for node in ext_exit_nodes_list:
            node_plot.append(ax.plot(node.Coord[0]["x"], node.Coord[0]["y"], 'o',
                             color=color_ext_exit, markerfacecolor=color_ext_exit, markersize=marker_size_2))
        for node in entry_nodes_list:
            node_plot.append(ax.plot(node.Coord[0]["x"], node.Coord[0]["y"], 'o',
                             color=color_entry, markerfacecolor=color_entry, markersize=marker_size_1))
        for node in ext_entry_nodes_list:
            node_plot.append(ax.plot(node.Coord[0]["x"], node.Coord[0]["y"], 'o',
                             color=color_ext_entry, markerfacecolor=color_ext_entry, markersize=marker_size_1))
        for node in border_nodes_list:
            node_plot.append(ax.plot(node.Coord[0]["x"], node.Coord[0]["y"], 'o',
                             color=color_border, markerfacecolor=color_border, markersize=marker_size_3))

        if len(exit_nodes_list) > 0:
            legend_mn.append(Line2D([0], [0], color=color_exit, marker='o', markerfacecolor=color_exit,
                             markersize=marker_size_2, label='Destination', lw=0))
        if len(ext_exit_nodes_list) > 0:
            legend_mn.append(Line2D([0], [0], color=color_ext_exit, marker='o', markerfacecolor=color_ext_exit,
                             markersize=marker_size_2, label='External Exit', lw=0))
        if len(entry_nodes_list) > 0:
            legend_mn.append(Line2D([0], [0], color=color_entry, marker='o', markerfacecolor=color_entry,
                             markersize=marker_size_1, label='Origin', lw=0))
        if len(ext_entry_nodes_list) > 0:
            legend_mn.append(Line2D([0], [0], color=color_ext_entry, marker='o', markerfacecolor=color_ext_entry,
                             markersize=marker_size_1, label='External Entry', lw=0))
        if len(border_nodes_list) > 0:
            legend_mn.append(Line2D([0], [0], color=color_border, marker='o', markerfacecolor=color_border,
                             markersize=marker_size_3, label='Border', lw=0))

    # Plot the reservoirs numbers
    plot_res_id = []
    if res_bp_filled:
        color_r = txt_color
    else:
        color_r = 'k'

    for r in range(num_res):
        if res_centroid_filled:
            xr = reservoirs[r].Centroid[0]["x"]
            yr = reservoirs[r].Centroid[0]["y"]
        else:
            bp_x = []
            bp_y = []
            for bp in reservoirs[r].BorderPoints:
                bp_x.append(bp["x"])
                bp_y.append(bp["y"])

            max_x = max(bp_x)
            min_x = min(bp_x)
            max_y = max(bp_y)
            min_y = min(bp_y)

            xr = (max_x + min_x) / 2
            yr = (max_y + min_y) / 2

        plot_res_id.append(ax.text(xr, yr, f'$R_{str(r + 1)}$', ha='center', color=color_r, fontname=font_name,
                           fontweight='bold', fontsize=font_size, visible=plot_res_names))

    # Plot size
    x_border = 0.1      # increasing factor > 0 for the border spacing along x
    y_border = 0.1      # increasing factor > 0 for the border spacing along y

    if x_links is not None:
        if max(x_links) == min(x_links):
            dx = max(y_links) - min(y_links)
        else:
            dx = max(x_links) - min(x_links)

        if max(y_links) == min(y_links):
            dy = max(x_links) - min(x_links)
        else:
            dy = max(y_links) - min(y_links)

        x_min = min(x_links) - x_border * dx
        x_max = max(x_links) + x_border * dx
        y_min = min(y_links) - y_border * dy
        y_max = max(y_links) + y_border * dy

        ax.axis([x_min, x_max, y_min, y_max])
    else:
        dx = 1

    # Plot the macro node numbers
    simil_nodes = []
    if mn_coord_filled:
        for node_i in nodes:
            node_i_added = False
            for node_j in nodes:
                dist = math.sqrt(math.fabs((node_i.Coord[0]["x"] - node_j.Coord[0]["x"]) ** 2
                                 + (node_i.Coord[0]["y"] - node_j.Coord[0]["y"]) ** 2))
                if dist < 0.01 * dx:
                    simil_nodes.append([node_i, node_j])    # similar nodes if spatially very close
                    node_i_added = True

            if not node_i_added:
                simil_nodes.append([node_i])

    plot_mn_id = []
    for pair in simil_nodes:
        plot_mn_id.append(ax.text(pair[0].Coord[0]["x"], pair[0].Coord[0]["y"], '  ' + pair[0].ID,
                          color='k', ha='left', fontname=font_name, fontsize=font_size/4, visible=plot_mn_names))

    # Plot the legends
    if plot_legend and mn_coord_filled:
        legend1 = ax.legend(handles=legend_routes, loc='upper right')
        legend2 = ax.legend(handles=legend_mn, loc='lower left')

        plt.gca().add_artist(legend1)
        plt.gca().add_artist(legend2)

    plt.title('Network')
    ax.axis('off')

    rax = plt.axes([0.05, 0.4, 0.1, 0.15])

    list_labels = []
    list_visible = []
    if (res_centroid_filled or res_bp_filled) and mn_coord_filled:
        list_labels = ['Reservoirs', 'MacroNodes', 'Routes']
        list_visible = [True, True, True]
    elif mn_coord_filled and not res_bp_filled and not res_bp_filled:
        list_labels = ['MacroNodes', 'Routes']
        list_visible = [True, True]
    elif res_centroid_filled or res_bp_filled and not mn_coord_filled:
        list_labels = ['Reservoirs']
        list_visible = [True]

    check = widgets.CheckButtons(rax, list_labels, list_visible)

    def func(label):
        if label == 'Reservoirs':
            for plot in res_plot:
                for res in plot:
                    res.set_visible(not res.get_visible())

            if plot_res_names:
                for res_name in plot_res_id:
                    res_name.set_visible(not res_name.get_visible())

        elif label == 'MacroNodes':
            for plot in node_plot:
                for node in plot:
                    node.set_visible(not node.get_visible())

            if plot_mn_names:
                for mn_name in plot_mn_id:
                    mn_name.set_visible(not mn_name.get_visible())

            legend2.set_visible(not legend2.get_visible())

        elif label == 'Routes':
            for route in route_plot:
                route.set_visible(not route.get_visible())

            legend1.set_visible(not legend1.get_visible())
        plt.draw()

    check.on_clicked(func)

    plt.show()


def plot_graph_per_res(reservoirs, res_output, y_label1, y_label2=None, mode='VL', options=None):
    # Plot the graph for each reservoir of y_label1 (and y_label2 when defined) in function of x_label
    # INPUTS
    # ---- reservoirs           : reservoirs structure output
    # ---- y_label1             : label of y axe (Acc, Inflow, Outflow, Demand, Speed ...)
    # ---- y_label2             : label of another set of data to plot on the same graph (Inflow and Outflow)

    num_res = len(reservoirs)
    x_label = 'Time'

    # Verify mode
    if (mode != 'VL' and mode != 'BUS'):
        print("WARNING: Mode is not known")

    # Options
    if options is not None:
        nb_col_max = options['nb_col_max']
    else:
        nb_col_max = 5

    # Color map
    color_map_0 = np.array([(51, 51, 255), (0, 204, 51), (204, 0, 0), (204, 153, 0), (153, 0, 102), (51, 153, 153),
                            (204, 102, 204), (204, 204, 102)]) / 255

    while num_res > len(color_map_0):
        color_map_0 = np.concatenate((color_map_0, color_map_0))

    # Display subplots
    if num_res > nb_col_max:
        num_line = int(num_res / nb_col_max)
        if num_res % nb_col_max != 0:
            num_line += 1
        num_col = nb_col_max
    else:
        num_col = num_res
        num_line = 1

    i = 0
    j = 0
    ind_color = 0

    for r in range(num_res):
        i %= num_line
        j %= num_col

        ax = plt.subplot2grid((num_line, num_col), (i, j))
        color_r = color_map_0[ind_color]

        data1_res = []
        data2_res = []
        time_res = []

        for data in res_output[r]['ReservoirData']:
            time_res.append(data[x_label])
            data1_res.append(data[y_label1][mode])
            if y_label2 is not None:
                data2_res.append(data[y_label2][mode])

        data1_max = max(data1_res) + 1
        if data1_max == 0:
            data1_max = 1

        data2_max = 0
        if y_label2 is not None:
            data2_max = max(data2_res) + 1
            if data2_max == 0:
                data2_max = 1

        ax.set_ylabel(y_label1)
        p1, = ax.plot(time_res, data1_res, color=color_r, ls='-', label=y_label1)
        p1 = [p1]

        p2 = None
        if y_label2 is not None:
            if (y_label1 == 'Inflow' and y_label2 == 'Outflow') or (y_label1 == 'Outflow' and y_label2 == 'Inflow'):
                ax.set_ylabel(f'{y_label1}, {y_label2}')
                p, = ax.plot(time_res, data2_res, color=color_r, ls='--', label=y_label2)
                p1.append(p)
            else:
                ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
                ax2.set_ylabel(y_label2)
                p2, = ax2.plot(time_res, data2_res, color=color_r, ls='--', label=y_label2)
                p2 = [p2]

        # If plotting accumulation, display critical and maximum acceleration
        if y_label1 == 'Acc' or y_label2 == 'Acc':
            max_acc = reservoirs[r].get_MFD_setting('MaxAcc', mode)
            crit_acc = reservoirs[r].get_MFD_setting('CritAcc', mode)

            if y_label1 == 'Acc':
                p1.append(ax.axhline(y=max_acc, color="k", ls="--", label='MaxAcc'))
                p1.append(ax.axhline(y=crit_acc, color='k', ls=':', label='CritAcc'))
                data1_max = max_acc + max_acc / 10
            else:
                p2.append(ax2.axhline(y=max_acc, color="k", ls="--"))
                p2.append(ax2.axhline(y=crit_acc, color='k', ls=':'))
                data2_max = max_acc + max_acc / 10

        plt.axis([0, time_res[-1], 0, max(data1_max, data2_max)])
        plt.xlabel(x_label)
        plt.title(reservoirs[r].ID)

        if p2 is not None:
            lines = p1 + p2
        else:
            lines = p1
        legend = plt.legend(lines, [line.get_label() for line in lines], loc='upper right')
        plt.gca().add_artist(legend)

        j += 1
        if j >= num_col:
            i += 1

        ind_color += 1

    if y_label2 is not None:
        sup_title_label = f'{y_label1}, {y_label2} = f({x_label}); mode = {mode}'
    else:
        sup_title_label = f'{y_label1} = f({x_label}); mode = {mode}'
    plt.suptitle(sup_title_label)


def plot_graph_per_res_per_route(reservoirs, res_output, y_label, routes, mode='VL', options=None):
    # Plot the graphes per route for each reservoir of y_label in function of x_label
    # INPUTS
    # ---- reservoirs           : reservoirs structure output
    # ---- y_label              : label of y axe (Acc, Inflow, Outflow, Demand, Speed ...)

    num_res = len(reservoirs)
    num_routes = len(routes)
    x_label = 'Time'

    # Verify mode
    if (mode != 'VL' and mode != 'BUS'):
        print("WARNING: Mode is not known")

    # Options
    if options is not None:
        nb_col_max = options['nb_col_max']
    else:
        nb_col_max = 5

    # Color map
    color_map_0 = np.array([(51, 51, 255), (0, 204, 51), (204, 0, 0), (204, 153, 0), (153, 0, 102), (51, 153, 153),
                            (204, 102, 204), (204, 204, 102)]) / 255

    while num_routes > len(color_map_0):
        color_map_0 = np.concatenate((color_map_0, color_map_0))

    # Display subplots
    if num_res > nb_col_max:
        num_line = int(num_res / nb_col_max)
        if num_res % nb_col_max != 0:
            num_line += 1
        num_col = nb_col_max
    else:
        num_col = num_res
        num_line = 1

    ind_routes = {}
    for i in range(num_routes):
        ind_routes[routes[i].ID] = i

    i = 0
    j = 0
    for r in range(num_res):
        i %= num_line
        j %= num_col

        ax = plt.subplot2grid((num_line, num_col), (i, j))

        data_max = []
        time_res = []

        for data in res_output[r]['ReservoirData']:
            time_res.append(data[x_label])

        p1 = []
        for route in res_output[r]['DataPerRoute']:
            # Define color
            color_r = color_map_0[ind_routes[route['RouteID']]]

            data_route = []
            for data in route['Data']:
                data_route.append(data[y_label][mode])

            data_max.append(max(data_route) + 1)

            ax.set_ylabel(y_label)
            p, = ax.plot(time_res, data_route, color=color_r, ls='-', label=route['RouteID'])
            p1.append(p)

        # If plotting accumulation, display critical and maximum acceleration
        if y_label == 'Acc':
            p2 = []
            max_acc = reservoirs[r].get_MFD_setting('MaxAcc', mode)
            crit_acc = reservoirs[r].get_MFD_setting('CritAcc', mode)

            p2.append(ax.axhline(y=max_acc, color="k", ls="--", label='MaxAcc'))
            p2.append(ax.axhline(y=crit_acc, color='k', ls=':', label='CritAcc'))
            data_max = [max_acc + max_acc / 10]

            legend2 = plt.legend(handles=p2, loc='center right')
            plt.gca().add_artist(legend2)

        plt.axis([0, time_res[-1], 0, max(data_max)])
        plt.xlabel(x_label)
        plt.title(reservoirs[r].ID)

        legend1 = plt.legend(handles=p1, loc='upper right')
        plt.gca().add_artist(legend1)


        j += 1
        if j >= num_col:
            i += 1

    sup_title_label = f'{y_label} = f({x_label}); mode = {mode}'
    plt.suptitle(sup_title_label)
