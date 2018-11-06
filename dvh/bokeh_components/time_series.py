#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
All Time Series tab objects and functions for the main DVH Analytics bokeh program
Created on Sat Nov 3 2018
@author: Dan Cutright, PhD
"""
from bokeh.plotting import figure
from bokeh.models import Select, TextInput, RadioGroup, Slider, Div, Legend, CustomJS, HoverTool, Button, Spacer
from bokeh.layouts import column, row
import options
from bokeh_components.utilities import clear_source_data, collapse_into_single_dates, moving_avg,\
    moving_avg_by_calendar_day, clear_source_selection
from scipy.stats import ttest_ind, ranksums, normaltest
import numpy as np
from options import GROUP_LABELS
from datetime import datetime
from os.path import dirname, join


class TimeSeries:
    def __init__(self, sources, range_categories, custom_title, data_tables):

        self.sources = sources
        self.range_categories = range_categories
        self.current_dvh_group = {n: [] for n in GROUP_LABELS}

        # Control Chart layout (Time-Series)
        tools = "pan,wheel_zoom,box_zoom,lasso_select,poly_select,reset,crosshair,save"
        self.plot = figure(plot_width=1050, plot_height=400, tools=tools, logo=None,
                           active_drag="box_zoom", x_axis_type='datetime')
        self.plot.xaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.plot.yaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.plot.xaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.plot.yaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        # plot.min_border_left = min_border
        self.plot.min_border_bottom = options.MIN_BORDER
        self.plot_data_1 = self.plot.circle('x', 'y', size=options.TIME_SERIES_1_CIRCLE_SIZE,
                                            color=options.GROUP_1_COLOR,
                                            alpha=options.TIME_SERIES_1_CIRCLE_ALPHA,
                                            source=sources.time_1)
        self.plot_data_2 = self.plot.circle('x', 'y', size=options.TIME_SERIES_2_CIRCLE_SIZE,
                                            color=options.GROUP_2_COLOR,
                                            alpha=options.TIME_SERIES_2_CIRCLE_ALPHA,
                                            source=sources.time_2)
        self.plot_trend_1 = self.plot.line('x', 'y', color=options.GROUP_1_COLOR, source=sources.time_trend_1,
                                           line_width=options.TIME_SERIES_1_TREND_LINE_WIDTH,
                                           line_dash=options.TIME_SERIES_1_TREND_LINE_DASH)
        self.plot_trend_2 = self.plot.line('x', 'y', color=options.GROUP_2_COLOR, source=sources.time_trend_2,
                                           line_width=options.TIME_SERIES_2_TREND_LINE_WIDTH,
                                           line_dash=options.TIME_SERIES_2_TREND_LINE_DASH)
        self.plot_avg_1 = self.plot.line('x', 'avg', color=options.GROUP_1_COLOR, source=sources.time_bound_1,
                                         line_width=options.TIME_SERIES_1_AVG_LINE_WIDTH,
                                         line_dash=options.TIME_SERIES_1_AVG_LINE_DASH)
        self.plot_avg_2 = self.plot.line('x', 'avg', color=options.GROUP_2_COLOR, source=sources.time_bound_2,
                                         line_width=options.TIME_SERIES_2_AVG_LINE_WIDTH,
                                         line_dash=options.TIME_SERIES_2_AVG_LINE_DASH)
        self.plot_patch_1 = self.plot.patch('x', 'y', color=options.GROUP_1_COLOR, source=sources.time_patch_1,
                                            alpha=options.TIME_SERIES_1_PATCH_ALPHA)
        self.plot_patch_2 = self.plot.patch('x', 'y', color=options.GROUP_2_COLOR, source=sources.time_patch_2,
                                            alpha=options.TIME_SERIES_1_PATCH_ALPHA)
        self.plot.add_tools(HoverTool(show_arrow=True,
                                      tooltips=[('ID', '@mrn'),
                                                ('Date', '@x{%F}'),
                                                ('Value', '@y{0.2f}')],
                                      formatters={'x': 'datetime'}))
        self.plot.xaxis.axis_label = "Simulation Date"
        self.plot.yaxis.axis_label = ""
        # Set the legend
        legend_plot = Legend(items=[("Group 1", [self.plot_data_1]),
                                    ("Series Average", [self.plot_avg_1]),
                                    ("Rolling Average", [self.plot_trend_1]),
                                    ("Percentile Region", [self.plot_patch_1]),
                                    ("Group 2", [self.plot_data_2]),
                                    ("Series Average", [self.plot_avg_2]),
                                    ("Rolling Average", [self.plot_trend_2]),
                                    ("Percentile Region", [self.plot_patch_2])],
                             location=(25, 0))

        # Add the layout outside the plot, clicking legend item hides the line
        self.plot.add_layout(legend_plot, 'right')
        self.plot.legend.click_policy = "hide"

        plot_options = list(range_categories)
        plot_options.sort()
        plot_options.insert(0, '')
        self.y_axis = Select(value=plot_options[0], options=plot_options, width=300)
        self.y_axis.title = "Select a Range Variable"
        self.y_axis.on_change('value', self.update_y_axis_ticker)

        self.look_back_distance = TextInput(value='1', title="Lookback Distance", width=200)
        self.look_back_distance.on_change('value', self.update_plot_trend_ticker)

        self.plot_percentile = TextInput(value='90', title="Percentile", width=200)
        self.plot_percentile.on_change('value', self.update_plot_trend_ticker)

        look_back_units_options = ['Dates with a Sim', 'Days']
        self.look_back_units = Select(value=look_back_units_options[0], options=look_back_units_options, width=200)
        self.look_back_units.title = 'Lookback Units'
        self.look_back_units.on_change('value', self.update_plot_ticker)

        # source_time.on_change('selected', plot_update_trend)
        self.trend_update_button = Button(label="Update Trend", button_type="primary", width=150)
        self.trend_update_button.on_click(self.plot_update_trend)

        self.download_time_plot = Button(label="Download Plot Data", button_type="default", width=150)
        self.download_time_plot.callback = CustomJS(args=dict(source_1=sources.time_1,
                                                              source_2=sources.time_2),
                                                    code=open(join(dirname(dirname(__file__)),
                                                                   "download_time_plot.js")).read())

        # histograms
        tools = "pan,wheel_zoom,box_zoom,reset,crosshair,save"
        self.histograms = figure(plot_width=1050, plot_height=400, tools=tools, logo=None, active_drag="box_zoom")
        self.histograms.xaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.histograms.yaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.histograms.xaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.histograms.yaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.histograms.min_border_left = options.MIN_BORDER
        self.histograms.min_border_bottom = options.MIN_BORDER
        self.hist_1 = self.histograms.vbar(x='x', width='width', bottom=0, top='top', source=sources.histogram_1,
                                           color=options.GROUP_1_COLOR, alpha=options.HISTOGRAM_1_ALPHA)
        self.hist_2 = self.histograms.vbar(x='x', width='width', bottom=0, top='top', source=sources.histogram_2,
                                           color=options.GROUP_2_COLOR, alpha=options.HISTOGRAM_2_ALPHA)
        self.histograms.xaxis.axis_label = ""
        self.histograms.yaxis.axis_label = "Frequency"
        self.histogram_bin_slider = Slider(start=1, end=100, value=10, step=1, title="Number of Bins")
        self.histogram_bin_slider.on_change('value', self.histograms_ticker)
        self.histogram_radio_group = RadioGroup(labels=["Absolute Y-Axis", "Relative Y-Axis (to Group Max)"], active=0)
        self.histogram_radio_group.on_change('active', self.histograms_ticker)
        self.histogram_normaltest_1_text = Div(text="Group 1 Normal Test p-value = ", width=400)
        self.histogram_normaltest_2_text = Div(text="Group 2 Normal Test p-value = ", width=400)
        self.histogram_ttest_text = Div(text="Two Sample t-Test (Group 1 vs 2) p-value = ", width=400)
        self.histogram_ranksums_text = Div(text="Wilcoxon rank-sum (Group 1 vs 2) p-value = ", width=400)
        self.histograms.add_tools(HoverTool(show_arrow=True, line_policy='next',
                                            tooltips=[('x', '@x{0.2f}'),
                                                      ('Counts', '@top')]))
        # Set the legend
        legend_hist = Legend(items=[("Group 1", [self.hist_1]),
                                    ("Group 2", [self.hist_2])],
                             location=(25, 0))

        # Add the layout outside the plot, clicking legend item hides the line
        self.histograms.add_layout(legend_hist, 'right')
        self.histograms.legend.click_policy = "hide"

        self.layout = column(Div(text="<b>DVH Analytics v%s</b>" % options.VERSION),
                             row(custom_title['1']['time_series'], Spacer(width=50),
                                 custom_title['2']['time_series']),
                             row(self.y_axis, self.look_back_units, self.look_back_distance,
                                 Spacer(width=10), self.plot_percentile, Spacer(width=10),
                                 self.trend_update_button),
                             self.plot,
                             self.download_time_plot,
                             Div(text="<hr>", width=1050),
                             row(self.histogram_bin_slider, self.histogram_radio_group),
                             row(self.histogram_normaltest_1_text, self.histogram_ttest_text),
                             row(self.histogram_normaltest_2_text, self.histogram_ranksums_text),
                             self.histograms,
                             Spacer(width=1000, height=10))

    def update_current_dvh_group(self, data):
        self.current_dvh_group = data

    def update_plot_ticker(self, attr, old, new):
        self.update_plot()

    def update_y_axis_ticker(self, attr, old, new):
        self.update_plot()

    def update_plot_trend_ticker(self, attr, old, new):
        self.plot_update_trend()

    def histograms_ticker(self, attr, old, new):
        self.update_histograms()

    def update_plot(self):
        new = str(self.y_axis.value)
        if new:
            clear_source_selection(self.sources, 'time_1')
            clear_source_selection(self.sources, 'time_2')

            if new.startswith('DVH Endpoint: '):
                y_var_name = new.split(': ')[1]
                y_source_values = self.sources.endpoint_calcs.data[y_var_name]
                y_source_uids = self.sources.endpoint_calcs.data['uid']
                y_source_mrns = self.sources.endpoint_calcs.data['mrn']
            elif new == 'EUD':
                y_source_values = self.sources.rad_bio.data['eud']
                y_source_uids = self.sources.rad_bio.data['uid']
                y_source_mrns = self.sources.rad_bio.data['mrn']
            elif new == 'NTCP/TCP':
                y_source_values = self.sources.rad_bio.data['ntcp_tcp']
                y_source_uids = self.sources.rad_bio.data['uid']
                y_source_mrns = self.sources.rad_bio.data['mrn']
            else:
                y_source = self.range_categories[new]['source']
                y_var_name = self.range_categories[new]['var_name']
                y_source_values = y_source.data[y_var_name]
                y_source_uids = y_source.data['uid']
                y_source_mrns = y_source.data['mrn']

            self.update_y_axis_label()

            sim_study_dates = self.sources.plans.data['sim_study_date']
            sim_study_dates_uids = self.sources.plans.data['uid']

            x_values = []
            skipped = []
            colors = []
            for v in range(len(y_source_values)):
                uid = y_source_uids[v]
                try:
                    sim_study_dates_index = sim_study_dates_uids.index(uid)
                    current_date_str = sim_study_dates[sim_study_dates_index]
                    if current_date_str == 'None':
                        current_date = datetime.now()
                    else:
                        current_date = datetime(int(current_date_str[0:4]),
                                                int(current_date_str[5:7]),
                                                int(current_date_str[8:10]))
                    x_values.append(current_date)
                    skipped.append(False)
                except:
                    skipped.append(True)

                # Get group color
                if not skipped[-1]:
                    if new.startswith('DVH Endpoint') or new in {'EUD', 'NTCP/TCP'} \
                            or self.range_categories[new]['source'] == self.sources.dvhs:
                        if new in {'EUD', 'NTCP/TCP'}:
                            roi = self.sources.rad_bio.data['roi_name'][v]
                        else:
                            roi = self.sources.dvhs.data['roi_name'][v]

                        found = {'Group 1': False, 'Group 2': False}

                        color = None

                        if self.current_dvh_group['1']:
                            r1, r1_max = 0, len(self.current_dvh_group['1'].study_instance_uid)
                            while r1 < r1_max and not found['Group 1']:
                                if self.current_dvh_group['1'].study_instance_uid[r1] == uid and \
                                        self.current_dvh_group['1'].roi_name[r1] == roi:
                                    found['Group 1'] = True
                                    color = options.GROUP_1_COLOR
                                r1 += 1

                        if self.current_dvh_group['2']:
                            r2, r2_max = 0, len(self.current_dvh_group['2'].study_instance_uid)
                            while r2 < r2_max and not found['Group 2']:
                                if self.current_dvh_group['2'].study_instance_uid[r2] == uid and \
                                        self.current_dvh_group['2'].roi_name[r2] == roi:
                                    found['Group 2'] = True
                                    if found['Group 1']:
                                        color = options.GROUP_1_and_2_COLOR
                                    else:
                                        color = options.GROUP_2_COLOR
                                r2 += 1

                        colors.append(color)
                    else:
                        if self.current_dvh_group['1'] and self.current_dvh_group['2']:
                            if uid in self.current_dvh_group['1'].study_instance_uid and \
                                    uid in self.current_dvh_group['2'].study_instance_uid:
                                colors.append(options.GROUP_1_and_2_COLOR)
                            elif uid in self.current_dvh_group['1'].study_instance_uid:
                                colors.append(options.GROUP_1_COLOR)
                            else:
                                colors.append(options.GROUP_2_COLOR)
                        elif self.current_dvh_group['1']:
                            colors.append(options.GROUP_1_COLOR)
                        else:
                            colors.append(options.GROUP_2_COLOR)

            y_values = []
            y_mrns = []
            for v in range(len(y_source_values)):
                if not skipped[v]:
                    y_values.append(y_source_values[v])
                    y_mrns.append(y_source_mrns[v])
                    if not isinstance(y_values[-1], (int, long, float)):
                        y_values[-1] = 0

            sort_index = sorted(range(len(x_values)), key=lambda k: x_values[k])
            x_values_sorted, y_values_sorted, y_mrns_sorted, colors_sorted = [], [], [], []

            for s in range(len(x_values)):
                x_values_sorted.append(x_values[sort_index[s]])
                y_values_sorted.append(y_values[sort_index[s]])
                y_mrns_sorted.append(y_mrns[sort_index[s]])
                colors_sorted.append(colors[sort_index[s]])

            source_time_1_data = {'x': [], 'y': [], 'mrn': [], 'date_str': []}
            source_time_2_data = {'x': [], 'y': [], 'mrn': [], 'date_str': []}
            for i in range(len(x_values_sorted)):
                if colors_sorted[i] in {options.GROUP_1_COLOR, options.GROUP_1_and_2_COLOR}:
                    source_time_1_data['x'].append(x_values_sorted[i])
                    source_time_1_data['y'].append(y_values_sorted[i])
                    source_time_1_data['mrn'].append(y_mrns_sorted[i])
                    source_time_1_data['date_str'].append(x_values_sorted[i].strftime("%Y-%m-%d"))
                if colors_sorted[i] in {options.GROUP_2_COLOR, options.GROUP_1_and_2_COLOR}:
                    source_time_2_data['x'].append(x_values_sorted[i])
                    source_time_2_data['y'].append(y_values_sorted[i])
                    source_time_2_data['mrn'].append(y_mrns_sorted[i])
                    source_time_2_data['date_str'].append(x_values_sorted[i].strftime("%Y-%m-%d"))

            self.sources.time_1.data = source_time_1_data
            self.sources.time_2.data = source_time_2_data
        else:
            clear_source_data(self.sources, 'time_1')
            clear_source_data(self.sources, 'time_2')

        self.plot_update_trend()

    def plot_update_trend(self):
        if self.y_axis.value:

            selected_indices = {n: getattr(self.sources, 'time_%s' % n).selected.indices for n in GROUP_LABELS}
            for n in GROUP_LABELS:
                if not selected_indices[n]:
                    selected_indices[n] = range(len(getattr(self.sources, 'time_%s' % n).data['x']))

            group = {n: {'x': [], 'y': []} for n in GROUP_LABELS}

            for n in GROUP_LABELS:
                for i in range(len(getattr(self.sources, 'time_%s' % n).data['x'])):
                    if i in selected_indices[n]:
                        for v in ['x', 'y']:
                            group[n][v].append(getattr(self.sources, 'time_%s' % n).data[v][i])

            try:
                avg_len = int(self.look_back_distance.value)
            except:
                avg_len = 1

            try:
                percentile = float(self.plot_percentile.value)
            except:
                percentile = 90.

            # average daily data and keep track of points per day, calculate moving average

            group_collapsed = {n: [] for n in GROUP_LABELS}
            for n in GROUP_LABELS:
                if group[n]['x']:
                    group_collapsed[n] = collapse_into_single_dates(group[n]['x'], group[n]['y'])
                    if self.look_back_units.value == "Dates with a Sim":
                        x_trend, moving_avgs = moving_avg(group_collapsed[n], avg_len)
                    else:
                        x_trend, moving_avgs = moving_avg_by_calendar_day(group_collapsed[n], avg_len)

                    y_np = np.array(group[n]['y'])
                    upper_bound = float(np.percentile(y_np, 50. + percentile / 2.))
                    average = float(np.percentile(y_np, 50))
                    lower_bound = float(np.percentile(y_np, 50. - percentile / 2.))
                    getattr(self.sources, 'time_trend_%s' % n).data = {'x': x_trend,
                                                                  'y': moving_avgs,
                                                                  'mrn': ['Avg'] * len(x_trend)}
                    getattr(self.sources, 'time_bound_%s' % n).data = {'x': group[n]['x'],
                                                                  'mrn': ['Bound'] * len(group[n]['x']),
                                                                  'upper': [upper_bound] * len(group[n]['x']),
                                                                  'avg': [average] * len(group[n]['x']),
                                                                  'lower': [lower_bound] * len(group[n]['x'])}
                    getattr(self.sources, 'time_patch_%s' % n).data = {'x': [group[n]['x'][0], group[n]['x'][-1],
                                                                        group[n]['x'][-1], group[n]['x'][0]],
                                                                  'y': [upper_bound, upper_bound, lower_bound, lower_bound]}
                else:
                    for v in ['trend', 'bound', 'patch']:
                        clear_source_data(self.sources, 'time_%s_%s' % (v, n))

            x_var = str(self.y_axis.value)
            if x_var.startswith('DVH Endpoint'):
                self.histograms.xaxis.axis_label = x_var.split("DVH Endpoint: ")[1]
            elif x_var == 'EUD':
                self.histograms.xaxis.axis_label = "%s (Gy)" % x_var
            elif x_var == 'NTCP/TCP':
                self.histograms.xaxis.axis_label = "NTCP or TCP"
            else:
                if self.range_categories[x_var]['units']:
                    self.histograms.xaxis.axis_label = "%s (%s)" % (x_var, self.range_categories[x_var]['units'])
                else:
                    self.histograms.xaxis.axis_label = x_var

            # Normal Test
            s, p = {n: '' for n in GROUP_LABELS}, {n: '' for n in GROUP_LABELS}
            for n in GROUP_LABELS:
                if group[n]['y']:
                    s[n], p[n] = normaltest(group[n]['y'])
                    p[n] = "%0.3f" % p[n]

            # t-Test and Rank Sums
            pt, pr = '', ''
            if group['1']['y'] and group['2']['y']:
                st, pt = ttest_ind(group['1']['y'], group['2']['y'])
                sr, pr = ranksums(group['1']['y'], group['2']['y'])
                pt = "%0.3f" % pt
                pr = "%0.3f" % pr

            self.histogram_normaltest_1_text.text = "Group 1 Normal Test p-value = %s" % p['1']
            self.histogram_normaltest_2_text.text = "Group 2 Normal Test p-value = %s" % p['2']
            self.histogram_ttest_text.text = "Two Sample t-Test (Group 1 vs 2) p-value = %s" % pt
            self.histogram_ranksums_text.text = "Wilcoxon rank-sum (Group 1 vs 2) p-value = %s" % pr

        else:
            for n in GROUP_LABELS:
                for k in ['trend', 'bound', 'patch']:
                    clear_source_data(self.sources, "time_%s_%s" % (k, n))

            self.histogram_normaltest_1_text.text = "Group 1 Normal Test p-value = "
            self.histogram_normaltest_2_text.text = "Group 2 Normal Test p-value = "
            self.histogram_ttest_text.text = "Two Sample t-Test (Group 1 vs 2) p-value = "
            self.histogram_ranksums_text.text = "Wilcoxon rank-sum (Group 1 vs 2) p-value = "

        self.update_histograms()

    def update_histograms(self):

        if self.y_axis.value != '':
            # Update Histograms
            bin_size = int(self.histogram_bin_slider.value)
            width_fraction = 0.9

            for n in GROUP_LABELS:
                hist, bins = np.histogram(getattr(self.sources, 'time_%s' % n).data['y'], bins=bin_size)
                if self.histogram_radio_group.active == 1:
                    hist = np.divide(hist, np.float(np.max(hist)))
                    self.histograms.yaxis.axis_label = "Relative Frequency"
                else:
                    self.histograms.yaxis.axis_label = "Frequency"
                width = [width_fraction * (bins[1] - bins[0])] * bin_size
                center = (bins[:-1] + bins[1:]) / 2.
                getattr(self.sources, 'histogram_%s' % n).data = {'x': center,
                                                             'top': hist,
                                                             'width': width}
        else:
            for n in GROUP_LABELS:
                    clear_source_data(self.sources, 'histogram_%s' % n)

    def update_y_axis_label(self):
        new = str(self.y_axis.value)

        if new:

            # If new has something in parenthesis, extract and put in front
            new_split = new.split(' (')
            if len(new_split) > 1:
                new_display = "%s %s" % (new_split[1].split(')')[0], new_split[0])
            else:
                new_display = new

            if new.startswith('DVH Endpoint'):
                self.plot.yaxis.axis_label = str(self.y_axis.value).split(': ')[1]
            elif new == 'EUD':
                self.plot.yaxis.axis_label = 'EUD (Gy)'
            elif new == 'NTCP/TCP':
                self.plot.yaxis.axis_label = 'NTCP or TCP'
            elif self.range_categories[new]['units']:
                self.plot.yaxis.axis_label = "%s (%s)" % (new_display, self.range_categories[new]['units'])
            else:
                self.plot.yaxis.axis_label = new_display

    def update_options(self):
        new_options = list(self.range_categories)
        new_options.extend(['EUD', 'NTCP/TCP'])

        for ep in self.sources.endpoint_calcs.data:
            if ep.startswith('V_') or ep.startswith('D_'):
                new_options.append("DVH Endpoint: %s" % ep)

        new_options.sort()
        new_options.insert(0, '')

        self.y_axis.options = new_options
        self.y_axis.value = ''
