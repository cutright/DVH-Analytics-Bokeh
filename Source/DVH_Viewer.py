"""
View data with a DVH object created by Analysis_Tools.
Created on Th Apr 19 2017
@author: Dan Cutright, PhD
"""

from Analysis_Tools import *
import numpy as np
import itertools
from bokeh.models import HoverTool, Legend, Range1d
from bokeh.palettes import Category20_9 as palette
from bokeh.io import output_file, show
from bokeh.plotting import figure, gridplot


def bokeh_plot(dvh):
    x_axis = np.linspace(0, dvh.bin_count, dvh.bin_count) / float(100)
    x_data = []
    y_data = []
    for i in range(0, dvh.count):
        x_data.append(x_axis)
        y_data.append(dvh.dvh[:, i])

    output_file("test.html")
    if 'mrn' in dvh.query:
        legend = dvh.roi_name
    else:
        legend = dvh.mrn

    hover = HoverTool(tooltips=[])
    tools = 'pan,box_zoom,crosshair,reset,wheel_zoom,resize'
    colors = itertools.cycle(palette)

    dvh_plots = figure(plot_width=700, plot_height=400, tools=[tools, hover], title='Individual results for ' + str(dvh.query))
    dvh_plots.x_range = Range1d(0, dvh.bin_count/float(100))
    dvh_plots.y_range = Range1d(0, 1)

    dvh_stats = figure(plot_width=700, plot_height=400, tools=tools, title='Population Statistics',
                       x_range=dvh_plots.x_range, y_range=dvh_plots.y_range)

    x_patch = np.append(x_axis, x_axis[::-1])
    y_patch = np.append(dvh.q3_dvh, dvh.q1_dvh[::-1])
    dvh_stats.patch(x_patch, y_patch, alpha=0.1)
    dvh_plots.patch(x_patch, y_patch, alpha=0.2)

    stats_min = dvh_stats.line(x_axis, dvh.min_dvh, line_width=2, color='black', alpha=0.2, line_dash='dotted')
    dvh_stats.add_tools(HoverTool(renderers=[stats_min], tooltips=[('Plot', 'Min'), ("Dose", "@x"), ("Volume", "@y")]))
    stats_q1 = dvh_stats.line(x_axis, dvh.q1_dvh, line_width=1, color='black', alpha=0.2)
    dvh_stats.add_tools(HoverTool(renderers=[stats_q1], tooltips=[('Plot', 'Q1'), ("Dose", "@x"), ("Volume", "@y")]))
    stats_median = dvh_stats.line(x_axis, dvh.median_dvh, line_width=2, color='green')
    dvh_stats.add_tools(HoverTool(renderers=[stats_median], tooltips=[('Plot', 'Median'), ("Dose", "@x"), ("Volume", "@y")]))
    stats_mean = dvh_stats.line(x_axis, dvh.mean_dvh, line_width=2, color='blue')
    dvh_stats.add_tools(HoverTool(renderers=[stats_mean], tooltips=[('Plot', 'Mean'), ("Dose", "@x"), ("Volume", "@y")]))
    stats_q3 = dvh_stats.line(x_axis, dvh.q3_dvh, line_width=1, color='black', alpha=0.2)
    dvh_stats.add_tools(HoverTool(renderers=[stats_q3], tooltips=[('Plot', 'Q3'), ("Dose", "@x"), ("Volume", "@y")]))
    stats_max = dvh_stats.line(x_axis, dvh.max_dvh, line_width=2, color='black', alpha=0.2, line_dash='dotted')
    dvh_stats.add_tools(HoverTool(renderers=[stats_max], tooltips=[('Plot', 'Max'), ("Dose", "@x"), ("Volume", "@y")]))

    legend_dvhs = []
    l = {}
    for i, color in itertools.izip(xrange(dvh.count), colors):
        l[i] = dvh_plots.line(x_data[i], y_data[i],
                           line_width=2,
                           color=color,
                           muted_alpha=0.1)
        legend_dvhs.append((str(legend[i]), [l[i]]))
        dvh_plots.add_tools(HoverTool(renderers=[l[i]],
                                      tooltips=[('Plot', legend[i]),
                                                ("Dose", "@x"),
                                                ("Volume", "@y")]))

    legend_stats = Legend(items=[
        ("Min", [stats_min]),
        ("Q1", [stats_q1]),
        ("Median", [stats_median]),
        ("Mean", [stats_mean]),
        ("Q3", [stats_q3]),
        ("Max", [stats_max])
    ], location=(0, 45))

    legend_dvhs = Legend(items=legend_dvhs, location=(0, 45))

    dvh_stats.add_layout(legend_stats, 'right')
    dvh_plots.add_layout(legend_dvhs, 'right')

    dvh_plots.legend.click_policy = "mute"
    dvh_stats.legend.click_policy = "hide"

    dvh_plots.xaxis.axis_label = "Dose (Gy)"
    dvh_plots.yaxis.axis_label = "Normalized Volume"
    dvh_stats.xaxis.axis_label = "Dose (Gy)"
    dvh_stats.yaxis.axis_label = "Normalized Volume"

    p = gridplot([[dvh_plots], [dvh_stats]])

    show(p)


if __name__ == '__main__':
    pass
