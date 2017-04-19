from Analysis_Tools import *
import numpy as np
import itertools
from bokeh.models import HoverTool, BoxSelectTool
from bokeh.palettes import Dark2_5 as palette
from bokeh.io import output_file, show
from bokeh.plotting import figure


def bokeh_plot(dvh):
    x_axis = np.linspace(0, dvh.bin_count, dvh.bin_count)
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
    TOOLS = ['box_zoom,crosshair,reset,wheel_zoom,resize', hover, BoxSelectTool()]
    colors = itertools.cycle(palette)

    dvh_plots = figure(plot_width=800, plot_height=800, tools=TOOLS, title=dvh.query)
    x_patch = np.append(x_axis, x_axis[::-1])
    y_patch = np.append(dvh.q3_dvh, dvh.q1_dvh[::-1])
    dvh_plots.patch(x_patch, y_patch, alpha=0.1)

    for i, color in itertools.izip(xrange(dvh.count), colors):
        dvh_plots.line(x_data[i], y_data[i], line_width=2, color=color, legend=legend[i])

    dvh_plots.line(x_axis, dvh.median_dvh, line_width=2, color='firebrick', legend='Median')

    dvh_plots.legend.click_policy = "hide"

    dvh_plots.xaxis.axis_label = "Dose (cGy)"
    dvh_plots.yaxis.axis_label = "Normalized Volume"

    dvh_plots.xaxis.bounds = (0, dvh.bin_count)
    dvh_plots.yaxis.bounds = (0, 1)

    show(dvh_plots)


if __name__ == '__main__':
    pass
