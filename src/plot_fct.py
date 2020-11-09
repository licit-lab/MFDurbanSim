import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
from matplotlib import cm
from matplotlib.lines import Line2D

import math
import numpy as np


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
    list_max_flow = []
    for r in range(num_res):
        flow = []
        avg_trip_length = res_output[r]["ReservoirData"][time_id]["AvgTripLength"]

        if avg_trip_length != 0:
            flow.append(reservoirs[r].MFDsetting[0]["MaxProd"] / avg_trip_length)

        list_max_flow.append(max(flow))

    max_flow = max(list_max_flow)

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
        acc_ratio = res_output[r]["ReservoirData"][time_id]["Acc"] / reservoirs[r].MFDsetting[0]["MaxAcc"]
        height_level = acc_ratio * 2 * res_radius
        th0 = math.asin((height_level - res_radius) / res_radius)
        th = list(np.arange(-math.pi - th0, th0 + step, step))
        x = [x_res_c + res_radius * math.cos(element) for element in th]
        y = [y_res_c + res_radius * math.sin(element) for element in th]

        str_acc = str(round(res_output[r]["ReservoirData"][time_id]["Acc"]))
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


def plot_res_net_speed(t, reservoirs, res_output, simul_time, speed_range):
    # Plot the state of reservoirs at time t(mean speed), with links and/or shape borders
    #
    # INPUTS
    # ---- t: scalar, time[s]
    # ---- reservoirs: reservoirs structure
    # ---- simul_time: vector, simulation time[s]
    # ---- speed_range: vector[V_min V_max], speed range[m / s] to define the colormap

    num_res = len(reservoirs)

    # Index of the current time
    time_step = simul_time[1] - simul_time[0]
    time_id = 0
    for i in range(len(simul_time)):
        if t == simul_time[i] or abs(t - simul_time[i]) <= time_step / 2:
            time_id = i

    # Choice of a colormap
    nb_color = 800
    rd_yl_gn = cm.get_cmap('rd_yl_gn', nb_color)

    txt_color = [0.1, 0.1, 0]
    font_name = 'Arial'
    font_size = 16
    line_width = 1
    t_label = "Mean speed at t = " + str(t) + " s"

    x_links = []
    y_links = []

    # Plot reservoirs
    for r in range(num_res):
        mean_speed = res_output[r]["ReservoirData"][time_id]["MeanSpeed"]
        speed_ratio = (mean_speed - speed_range[0]) / (speed_range[1] - speed_range[0])
        ind_color = min([max([math.floor(speed_ratio * nb_color), 1]), nb_color])
        color_i = rd_yl_gn(ind_color)

        if len(reservoirs[r].BorderPoints) != 0:
            x_res_bp = []
            y_res_bp = []
            for bp in range(len(reservoirs[r].BorderPoints)):
                x_res_bp.append(reservoirs[r].BorderPoints[bp]["x"])
                y_res_bp.append(reservoirs[r].BorderPoints[bp]["y"])

                x_links.append(reservoirs[r].BorderPoints[bp]["x"])
                y_links.append(reservoirs[r].BorderPoints[bp]["y"])

            plt.fill(x_res_bp, y_res_bp, color=color_i, ec='none', alpha=0.5)
            plt.plot(x_res_bp, y_res_bp, '-', color=color_i, linewidth=line_width)

    for r in range(num_res):
        xr = reservoirs[r].Centroid[0]["x"]
        yr = reservoirs[r].Centroid[0]["y"]
        str_mean_speed = str(round(res_output[r]["ReservoirData"][time_id]["MeanSpeed"] * 3.6))
        plt.text(xr, yr, f'$R_{str(r + 1)}$' + '\n' + str_mean_speed + ' km/h',
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

    x_min = min(x_links) - x_border * dx
    x_max = max(x_links) + x_border * dx
    y_min = min(y_links) - y_border * dy
    y_max = max(y_links) + y_border * dy

    plt.axis([x_min, x_max, y_min, y_max])
    plt.axis('off')
    plt.text((x_min + x_max) / 2, y_max - y_border * dy / 4, t_label,
             ha='center', fontname=font_name, fontsize=font_size, fontweight="bold")


def plot_res_route_dem(reservoirs, routes, nodes, demand, demand_type, plot_charact):
    # Plot the number or demand of a given route list crossing the reservoirs
    # INPUTS
    # ---- reservoirs   : reservoirs structure
    # ---- routes       : routes structure
    # ---- plot_charact : string, 'number' or 'demand'

    num_res = len(reservoirs)

    # Choice of a colormap
    nb_color = 800
    rd_yl_gn = cm.get_cmap('rd_yl_gn', nb_color)

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
            for dem_t in dem.Demands:
                flow_demand += dem_t["Data"]
            flow_demand /= len(dem.Demands)

            for node in nodes:
                if node.ID == dem.OriginMacroNodeID or node.ID == dem.DestMacroNodeID:
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
    marker_size = 10
    color_map_0 = np.array([(51, 51, 255), (0, 204, 51), (204, 0, 0), (204, 153, 0), (153, 0, 102), (51, 153, 153),
                            (204, 102, 204), (204, 204, 102)]) / 255

    default_color = [0.1, 0.1, 0]
    txt_color = [0.9, 0.9, 1]

    # Lines
    line_0 = np.array(['', '-', '--', ':', '-.'])

    # Plot the reservoirs
    x_links = []
    y_links = []

    while num_res > len(color_map_0):
        color_map_0 = np.concatenate((color_map_0, color_map_0))

    while num_routes > len(line_0):
        line_0 = np.concatenate((line_0, line_0))

    res_plot = []
    # Plot the reservoirs
    for r in range(num_res):
        if plot_res_color:
            color_r = color_map_0[r]
        else:
            color_r = default_color

        if len(reservoirs[r].BorderPoints) != 0:
            x_res_bp = []
            y_res_bp = []
            for bp in reservoirs[r].BorderPoints:
                x_res_bp_tmp = bp["x"]
                y_res_bp_tmp = bp["y"]
                x_res_bp.append(x_res_bp_tmp)
                y_res_bp.append(y_res_bp_tmp)

                x_links.append(x_res_bp_tmp)
                y_links.append(y_res_bp_tmp)

            res_plot.append(ax.fill(x_res_bp, y_res_bp, color=color_r, ec='none', alpha=0.5))
            res_plot.append(ax.plot(x_res_bp, y_res_bp, color=color_r))
    
    # Plot the routes
    legend_routes = []
    i = 1

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
    if plot_mn_color:
        color1 = color_map_0[-1, :]
        color2 = color_map_0[-2, :]
        color3 = color_map_0[-3, :]
    else:
        color1 = default_color
        color2 = default_color
        color3 = default_color

    marker_size_1 = marker_size
    marker_size_2 = 1.25 * marker_size
    marker_size_3 = 0.75 * marker_size

    entry_nodes_list = []
    exit_nodes_list = []
    border_nodes_list = []

    for mn in nodes:
        if mn.Type == 'origin' or mn.Type == 'externalentry':
            entry_nodes_list.append(mn)
        elif mn.Type == 'destination' or mn.Type == 'externalexit':
            exit_nodes_list.append(mn)
        else:
            border_nodes_list.append(mn)

    node_plot = []
    for node in exit_nodes_list:
        node_plot.append(ax.plot(node.Coord[0]["x"], node.Coord[0]["y"], 'o',
                         color=color2, markerfacecolor=color2, markersize=marker_size_2))
    for node in entry_nodes_list:
        node_plot.append(ax.plot(node.Coord[0]["x"], node.Coord[0]["y"], 'o',
                         color=color1, markerfacecolor=color1, markersize=marker_size_1))
    for node in border_nodes_list:
        node_plot.append(ax.plot(node.Coord[0]["x"], node.Coord[0]["y"], 'o',
                         color=color3, markerfacecolor=color3, markersize=marker_size_3))

    legend_mn = [Line2D([0], [0], color=color2, marker='o', markerfacecolor=color2, markersize=marker_size_2,
                        label='Destination', lw=0),
                 Line2D([0], [0], color=color1, marker='o', markerfacecolor=color1, markersize=marker_size_1,
                        label='Origin', lw=0),
                 Line2D([0], [0], color=color3, marker='o', markerfacecolor=color3, markersize=marker_size_3,
                        label='Border', lw=0)]

    # Plot the reservoirs numbers
    plot_res_id = []
    for r in range(num_res):
        xr = reservoirs[r].Centroid[0]["x"]
        yr = reservoirs[r].Centroid[0]["y"]
        plot_res_id.append(ax.text(xr, yr, f'$R_{str(r + 1)}$', ha='center', color=txt_color, fontname=font_name,
                           fontweight='bold', fontsize=font_size, visible=plot_res_names))

    # Plot size
    x_border = 0.1      # increasing factor > 0 for the border spacing along x
    y_border = 0.1      # increasing factor > 0 for the border spacing along y
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

    # Plot the macro node numbers
    simil_nodes = []
    for node_i in nodes:
        node_i_added = False
        for node_j in nodes:
            dist = math.sqrt((node_i.Coord[0]["x"] - node_j.Coord[0]["x"]) ** 2
                              + (node_i.Coord[0]["y"] - node_j.Coord[0]["y"]) ** 2)
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
    if plot_legend:
        legend1 = ax.legend(handles=legend_routes, loc='upper right')
        legend2 = ax.legend(handles=legend_mn, loc='lower left')

        plt.gca().add_artist(legend1)
        plt.gca().add_artist(legend2)

    plt.title('Network')
    ax.axis([x_min, x_max, y_min, y_max])
    ax.axis('off')

    rax = plt.axes([0.05, 0.4, 0.1, 0.15])
    check = widgets.CheckButtons(rax, ('Reservoirs', 'MacroNodes', 'Routes'), (True, True, True))


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





