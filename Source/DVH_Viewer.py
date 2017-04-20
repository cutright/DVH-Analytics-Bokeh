from Analysis_Tools import *
import numpy as np
import itertools
from bokeh.models import HoverTool
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

    hover = HoverTool(
        tooltips=[
            ("(x,y)", "($x, $y)")
        ]
    )
    TOOLS = ['pan,box_zoom,crosshair,reset,wheel_zoom,resize', hover]
    TOOLS2 = 'pan,box_zoom,crosshair,reset,wheel_zoom,resize'
    colors = itertools.cycle(palette)

    dvh_plots = figure(plot_width=700, plot_height=400, tools=TOOLS, title='Individual results for ' + str(dvh.query))
    dvh_stats = figure(plot_width=700, plot_height=400, tools=TOOLS2, title='Population Statistics',
                       x_range=dvh_plots.x_range, y_range=dvh_plots.y_range,)
    x_patch = np.append(x_axis, x_axis[::-1])
    y_patch = np.append(dvh.q3_dvh, dvh.q1_dvh[::-1])
    dvh_stats.patch(x_patch, y_patch, alpha=0.1)

    l = dvh_stats.line(x_axis, dvh.min_dvh, line_width=2, color='black', legend='Min', alpha=0.2, line_dash='dotted')
    dvh_stats.add_tools(HoverTool(renderers=[l], tooltips=[('Name', 'Min'), ("Dose", "@x"), ("Volume", "@y")]))
    l = dvh_stats.line(x_axis, dvh.q1_dvh, line_width=1, color='black', legend='Q1', alpha=0.2)
    dvh_stats.add_tools(HoverTool(renderers=[l], tooltips=[('Name', 'Q1'), ("Dose", "@x"), ("Volume", "@y")]))
    l = dvh_stats.line(x_axis, dvh.median_dvh, line_width=2, color='green', legend='Median')
    dvh_stats.add_tools(HoverTool(renderers=[l], tooltips=[('Name', 'Median'), ("Dose", "@x"), ("Volume", "@y")]))
    l = dvh_stats.line(x_axis, dvh.mean_dvh, line_width=2, color='blue', legend='Mean')
    dvh_stats.add_tools(HoverTool(renderers=[l], tooltips=[('Name', 'Mean'), ("Dose", "@x"), ("Volume", "@y")]))
    l = dvh_stats.line(x_axis, dvh.q3_dvh, line_width=1, color='black', legend='Q3', alpha=0.2)
    dvh_stats.add_tools(HoverTool(renderers=[l], tooltips=[('Name', 'Q3'), ("Dose", "@x"), ("Volume", "@y")]))
    l = dvh_stats.line(x_axis, dvh.max_dvh, line_width=2, color='black', legend='Max', alpha=0.2, line_dash='dotted')
    dvh_stats.add_tools(HoverTool(renderers=[l], tooltips=[('Name', 'Max'), ("Dose", "@x"), ("Volume", "@y")]))
    for i, color in itertools.izip(xrange(dvh.count), colors):
        l = dvh_plots.line(np.around(x_data[i], decimals=2), y_data[i], line_width=2, color=color, legend=legend[i])
        dvh_plots.add_tools(HoverTool(renderers=[l],
                                      tooltips=[('Name', dvh.mrn[i]),
                                                ("Dose", "@x"),
                                                ("Volume", "@y")]))

    dvh_plots.legend.click_policy = "hide"
    dvh_stats.legend.click_policy = "hide"

    dvh_plots.xaxis.axis_label = "Dose (Gy)"
    dvh_plots.yaxis.axis_label = "Normalized Volume"
    dvh_stats.xaxis.axis_label = "Dose (Gy)"
    dvh_stats.yaxis.axis_label = "Normalized Volume"

    dvh_plots.xaxis.bounds = (0, dvh.bin_count)
    dvh_plots.yaxis.bounds = (0, 1)
    dvh_stats.xaxis.bounds = (0, dvh.bin_count)
    dvh_stats.yaxis.bounds = (0, 1)

    p = gridplot([[dvh_plots], [dvh_stats]])

    show(p)


if __name__ == '__main__':
    pass
