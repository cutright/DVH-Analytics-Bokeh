#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
All Correlation tab objects and functions for the main DVH Analytics bokeh program
Created on Sat Nov 3 2018
@author: Dan Cutright, PhD
"""
from future.utils import listitems
from bokeh.models import Legend, CustomJS, HoverTool, CheckboxGroup
from bokeh.models.widgets import Button, Div
from bokeh.plotting import figure
import options
from options import N
from math import pi
from scipy.stats import normaltest, pearsonr
from os.path import dirname, join
import numpy as np
from bokeh_components.utilities import get_include_map


class Correlation:
    def __init__(self, sources, correlation_names, range_categories):

        self.sources = sources
        self.correlation_names = correlation_names
        self.range_categories = range_categories
        self.regression = None

        self.data = {n: [] for n in N}
        self.bad_uid = {n: [] for n in N}

        self.fig = figure(plot_width=900, plot_height=700, x_axis_location="above",
                          tools="pan, box_zoom, wheel_zoom, reset, save", logo=None,  x_range=[''], y_range=[''])
        self.fig.xaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.fig.yaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.fig.xaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.fig.yaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.fig.min_border_left = 175
        self.fig.min_border_top = 130
        self.fig.xaxis.major_label_orientation = pi / 4
        self.fig.toolbar.active_scroll = "auto"
        self.fig.title.align = 'center'
        self.fig.title.text_font_style = "italic"
        self.fig.xaxis.axis_line_color = None
        self.fig.xaxis.major_tick_line_color = None
        self.fig.xaxis.minor_tick_line_color = None
        self.fig.xgrid.grid_line_color = None
        self.fig.ygrid.grid_line_color = None
        self.fig.yaxis.axis_line_color = None
        self.fig.yaxis.major_tick_line_color = None
        self.fig.yaxis.minor_tick_line_color = None
        self.fig.outline_line_color = None
        corr_1_pos = self.fig.circle(x='x', y='y', color='color', alpha='alpha',
                                     size='size', source=sources.correlation_1_pos)
        corr_1_neg = self.fig.circle(x='x', y='y', color='color', alpha='alpha',
                                     size='size', source=sources.correlation_1_neg)
        corr_2_pos = self.fig.circle(x='x', y='y', color='color', alpha='alpha',
                                     size='size', source=sources.correlation_2_pos)
        corr_2_neg = self.fig.circle(x='x', y='y', color='color', alpha='alpha',
                                     size='size', source=sources.correlation_2_neg)
        self.fig.add_tools(HoverTool(show_arrow=True, line_policy='next',
                                     tooltips=[('Group', '@group'),
                                               ('x', '@x_name'),
                                               ('y', '@y_name'),
                                               ('r', '@r'),
                                               ('p', '@p'),
                                               ('Norm p-value x', '@x_normality{0.4f}'),
                                               ('Norm p-value y', '@y_normality{0.4f}')],))
        self.fig.line(x='x', y='y', source=sources.corr_matrix_line,
                      line_width=3, line_dash='dotted', color='black', alpha=0.8)
        # Set the legend
        legend_corr = Legend(items=[("+r Group 1", [corr_1_pos]),
                                    ("-r Group 1", [corr_1_neg]),
                                    ("+r Group 2", [corr_2_pos]),
                                    ("-r Group 2", [corr_2_neg])],
                             location=(0, -575))

        # Add the layout outside the plot, clicking legend item hides the line
        self.fig.add_layout(legend_corr, 'right')
        self.fig.legend.click_policy = "hide"

        self.fig_text_1 = Div(text="Group 1:", width=110)
        self.fig_text_2 = Div(text="Group 2:", width=110)

        self.fig_include = CheckboxGroup(labels=correlation_names, active=options.CORRELATION_MATRIX_DEFAULTS_1)
        self.fig_include_2 = CheckboxGroup(labels=['DVH Endpoints', 'EUD', 'NTCP / TCP'],
                                           active=options.CORRELATION_MATRIX_DEFAULTS_2)
        self.fig_include.on_change('active', self.fig_include_ticker)
        self.fig_include_2.on_change('active', self.fig_include_ticker)

        self.download_corr_fig = Button(label="Download Correlation Figure Data", button_type="default", width=150)
        self.download_corr_fig.callback = CustomJS(args=dict(source_1_neg=sources.correlation_1_neg,
                                                             source_1_pos=sources.correlation_1_pos,
                                                             source_2_neg=sources.correlation_2_neg,
                                                             source_2_pos=sources.correlation_2_pos),
                                                   code=open(join(dirname(dirname(__file__)),
                                                                  "download_correlation_matrix.js")).read())

    def fig_include_ticker(self, attr, old, new):
        if len(self.fig_include.active) + len(self.fig_include_2.active) > 1:
            self.update_correlation_matrix()

    def update_correlation_matrix(self):
        categories = [key for index, key in enumerate(self.correlation_names) if index in self.fig_include.active]

        if 0 in self.fig_include_2.active:
            if self.data['1']:
                categories.extend([x for x in list(self.data['1']) if x.startswith("DVH Endpoint")])
            elif self.data['2']:
                categories.extend([x for x in list(self.data['2']) if x.startswith("DVH Endpoint")])

        if 1 in self.fig_include_2.active:
            if "EUD" in list(self.data['1']) or "EUD" in list(self.data['2']):
                categories.append("EUD")

        if 2 in self.fig_include_2.active:
            if "NTCP/TCP" in list(self.data['1']) or "NTCP/TCP" in list(self.data['2']):
                categories.append("NTCP/TCP")

        categories.sort()

        categories_count = len(categories)

        categories_for_label = [category.replace("Control Point", "CP") for category in categories]
        categories_for_label = [category.replace("control point", "CP") for category in categories_for_label]
        categories_for_label = [category.replace("Distance", "Dist") for category in categories_for_label]

        for i, category in enumerate(categories_for_label):
            if category.startswith('DVH'):
                categories_for_label[i] = category.split("DVH Endpoint: ")[1]

        self.fig.x_range.factors = categories_for_label
        self.fig.y_range.factors = categories_for_label[::-1]
        # 0.5 offset due to Bokeh 0.12.9 bug
        self.sources.corr_matrix_line.data = {'x': [0.5, len(categories) - 0.5], 'y': [len(categories) - 0.5, 0.5]}

        s_keys = ['x', 'y', 'x_name', 'y_name', 'color', 'alpha', 'r', 'p', 'group', 'size', 'x_normality',
                  'y_normality']
        s = {k: {sk: [] for sk in s_keys} for k in ['1_pos', '1_neg', '2_pos', '2_neg']}

        max_size = 45
        for x in range(categories_count):
            for y in range(categories_count):
                if x != y:
                    data_to_enter = False
                    if x > y and self.data['1'][categories[0]]['uid']:
                        n = '1'
                        data_to_enter = True
                    elif x < y and self.data['2'][categories[0]]['uid']:
                        n = '2'
                        data_to_enter = True

                    if data_to_enter:
                        x_data = self.data[n][categories[x]]['data']
                        y_data = self.data[n][categories[y]]['data']
                        if x_data and len(x_data) == len(y_data):
                            r, p_value = pearsonr(x_data, y_data)
                        else:
                            r, p_value = 0, 0
                        if r >= 0:
                            k = '%s_pos' % n
                            s[k]['color'].append(getattr(options, 'GROUP_%s_COLOR' % n))
                            s[k]['group'].append('Group %s' % n)
                        else:
                            k = '%s_neg' % n
                            s[k]['color'].append(getattr(options, 'GROUP_%s_COLOR_NEG_CORR' % n))
                            s[k]['group'].append('Group %s' % n)

                        if np.isnan(r):
                            r = 0
                        s[k]['r'].append(r)
                        s[k]['p'].append(p_value)
                        s[k]['alpha'].append(abs(r))
                        s[k]['size'].append(max_size * abs(r))
                        # 0.5 offset due to bokeh 0.12.9 bug
                        s[k]['x'].append(x + 0.5)
                        s[k]['y'].append(categories_count - y - 0.5)
                        s[k]['x_name'].append(categories_for_label[x])
                        s[k]['y_name'].append(categories_for_label[y])

                        x_norm, x_p = normaltest(x_data)
                        y_norm, y_p = normaltest(y_data)
                        s[k]['x_normality'].append(x_p)
                        s[k]['y_normality'].append(y_p)

        for k in ['1_pos', '1_neg', '2_pos', '2_neg']:
            getattr(self.sources, "correlation_%s" % k).data = s[k]

        group_count = {n: 0 for n in N}
        for n in N:
            if self.data[n]:
                group_count[n] = len(self.data[n][list(self.data[n])[0]]['uid'])

        self.fig_text_1.text = "Group 1: %d" % group_count[N[0]]
        self.fig_text_2.text = "Group 2: %d" % group_count[N[1]]

    def validate_data(self):

        for n in N:
            if self.data[n]:
                for range_var in list(self.data[n]):
                    for i, j in enumerate(self.data[n][range_var]['data']):
                        if j == 'None':
                            current_uid = self.data[n][range_var]['uid'][i]
                            if current_uid not in self.bad_uid[n]:
                                self.bad_uid[n].append(current_uid)
                            print("%s[%s] is non-numerical, will remove this patient from correlation data"
                                  % (range_var, i))

                new_correlation = {}
                for range_var in list(self.data[n]):
                    new_correlation[range_var] = {'mrn': [], 'uid': [], 'data': [],
                                                  'units': self.data['1'][range_var]['units']}
                    for i in range(len(self.data[n][range_var]['data'])):
                        current_uid = self.data[n][range_var]['uid'][i]
                        if current_uid not in self.bad_uid[n]:
                            for j in {'mrn', 'uid', 'data'}:
                                new_correlation[range_var][j].append(self.data[n][range_var][j][i])

                self.data[n] = new_correlation

    def update_data(self, correlation_variables):

        self.data = {'1': {}, '2': {}}

        temp_keys = ['uid', 'mrn', 'data', 'units']
        # remove review and stats from source
        include = get_include_map(self.sources)
        # Get data from DVHs table
        for key in correlation_variables:
            src = self.range_categories[key]['source']
            curr_var = self.range_categories[key]['var_name']
            table = self.range_categories[key]['table']
            units = self.range_categories[key]['units']

            if table in {'DVHs'}:
                temp = {n: {k: [] for k in temp_keys} for n in N}
                temp['units'] = units
                for i in range(len(src.data['uid'])):
                    if include[i]:
                        for n in N:
                            if src.data['group'][i] in {'Group %s' % n, 'Group 1 & 2'}:
                                temp[n]['uid'].append(src.data['uid'][i])
                                temp[n]['mrn'].append(src.data['mrn'][i])
                                temp[n]['data'].append(src.data[curr_var][i])
                for n in N:
                    self.data[n][key] = {k: temp[n][k] for k in temp_keys}

        uid_list = {n: self.data[n]['ROI Max Dose']['uid'] for n in N}

        # Get Data from Plans table
        for key in correlation_variables:
            src = self.range_categories[key]['source']
            curr_var = self.range_categories[key]['var_name']
            table = self.range_categories[key]['table']
            units = self.range_categories[key]['units']

            if table in {'Plans'}:
                temp = {n: {k: [] for k in temp_keys} for n in N}
                temp['units'] = units

                for n in N:
                    for i in range(len(uid_list[n])):
                        uid = uid_list[n][i]
                        uid_index = src.data['uid'].index(uid)
                        temp[n]['uid'].append(uid)
                        temp[n]['mrn'].append(src.data['mrn'][uid_index])
                        temp[n]['data'].append(src.data[curr_var][uid_index])

                for n in N:
                    self.data[n][key] = {k: temp[n][k] for k in temp_keys}

        # Get data from Beams table
        for key in correlation_variables:

            src = self.range_categories[key]['source']
            curr_var = self.range_categories[key]['var_name']
            table = self.range_categories[key]['table']
            units = self.range_categories[key]['units']

            stats = ['min', 'mean', 'median', 'max']

            if table in {'Beams'}:
                beam_keys = stats + ['uid', 'mrn']
                temp = {n: {bk: [] for bk in beam_keys} for n in N}
                for n in N:
                    for i in range(len(uid_list[n])):
                        uid = uid_list[n][i]
                        uid_indices = [j for j, x in enumerate(src.data['uid']) if x == uid]
                        plan_values = [src.data[curr_var][j] for j in uid_indices]

                        temp[n]['uid'].append(uid)
                        temp[n]['mrn'].append(src.data['mrn'][uid_indices[0]])
                        for s in stats:
                            temp[n][s].append(getattr(np, s)(plan_values))

                for s in stats:
                    for n in N:
                        corr_key = "%s (%s)" % (key, s.capitalize())
                        self.data[n][corr_key] = {'uid': temp[n]['uid'],
                                                  'mrn': temp[n]['mrn'],
                                                  'data': temp[n][s],
                                                  'units': units}

    def update_or_add_endpoints_to_correlation(self):

        include = get_include_map(self.sources)

        # clear out any old DVH endpoint data
        for n in N:
            if self.data[n]:
                for key in list(self.data[n]):
                    if key.startswith('ep'):
                        self.data[n].pop(key, None)

        src = self.sources.endpoint_calcs
        for j in range(len(self.sources.endpoint_defs.data['label'])):
            key = self.sources.endpoint_defs.data['label'][j]
            units = self.sources.endpoint_defs.data['units_out'][j]
            ep = "DVH Endpoint: %s" % key

            temp_keys = ['uid', 'mrn', 'data', 'units']
            temp = {n: {k: [] for k in temp_keys} for n in N}
            temp['units'] = units

            for i in range(len(src.data['uid'])):
                if include[i]:
                    for n in N:
                        if src.data['group'][i] in {'Group %s' % n, 'Group 1 & 2'}:
                            temp[n]['uid'].append(src.data['uid'][i])
                            temp[n]['mrn'].append(src.data['mrn'][i])
                            temp[n]['data'].append(src.data[key][i])

            for n in N:
                self.data[n][ep] = {k: temp[n][k] for k in temp_keys}

            if ep not in list(self.regression.multi_var_reg_vars):
                self.regression.multi_var_reg_vars[ep] = False

        # declare space to tag variables to be used for multi variable regression
        for n in N:
            for key, value in listitems(self.data[n]):
                self.data[n][key]['include'] = [False] * len(value['uid'])

    def update_eud_in_correlation(self):

        # Get data from EUD data
        uid_roi_list = ["%s_%s" % (uid, self.sources.dvhs.data['roi_name'][i]) for i, uid in
                        enumerate(self.sources.dvhs.data['uid'])]
        temp_keys = ['eud', 'ntcp_tcp', 'uid', 'mrn']
        temp = {n: {tk: [] for tk in temp_keys} for n in N}
        for i, uid in enumerate(self.sources.rad_bio.data['uid']):
            uid_roi = "%s_%s" % (uid, self.sources.rad_bio.data['roi_name'][i])
            source_index = uid_roi_list.index(uid_roi)
            group = self.sources.dvhs.data['group'][source_index]
            for n in N:
                if group in {'Group %s' % n, 'Group 1 & 2'}:
                    temp[n]['eud'].append(self.sources.rad_bio.data['eud'][i])
                    temp[n]['ntcp_tcp'].append(self.sources.rad_bio.data['ntcp_tcp'][i])
                    temp[n]['uid'].append(uid)
                    temp[n]['mrn'].append(self.sources.dvhs.data['mrn'][source_index])

        for n in N:
            self.data[n]['EUD'] = {'uid': temp[n]['uid'], 'mrn': temp[n]['mrn'],
                                   'data': temp[n]['eud'], 'units': 'Gy'}
            self.data[n]['NTCP/TCP'] = {'uid': temp[n]['uid'], 'mrn': temp[n]['mrn'],
                                        'data': temp[n]['ntcp_tcp'], 'units': ''}

        # declare space to tag variables to be used for multi variable regression
        for n in N:
            for key, value in listitems(self.data[n]):
                self.data[n][key]['include'] = [False] * len(value['uid'])

        self.validate_data()
        self.update_correlation_matrix()

    def clear_old_endpoints(self):
        # This function will remove endpoint data no longer in the endpoint calcs from self.data
        pass

    def clear_bad_uids(self):
        self.bad_uid = {n: [] for n in N}

    def add_regression_link(self, regression):
        self.regression = regression
