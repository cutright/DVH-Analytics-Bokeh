#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
All Regression tab objects and functions for the main DVH Analytics bokeh program
Created on Sun Nov 4 2018
@author: Dan Cutright, PhD
"""
from __future__ import print_function
from future.utils import listitems
from datetime import datetime
import statsmodels.api as sm
import options
from options import N
from bokeh.plotting import figure
from bokeh.models.widgets import Select, Button, Div, CheckboxGroup
from bokeh.models import Legend, HoverTool, Spacer
from bokeh.layouts import row, column
from scipy.stats import linregress
import numpy as np
from bokeh_components.utilities import clear_source_data, clear_source_selection


class Regression:
    def __init__(self, sources, time_series, correlation, multi_var_reg_var_names, custom_title, data_tables):
        self.sources = sources
        self.time_series = time_series
        self.correlation = correlation
        self.multi_var_reg_vars = {name: False for name in multi_var_reg_var_names}

        # Control Chart layout
        tools = "pan,wheel_zoom,box_zoom,reset,crosshair,save"
        self.figure = figure(plot_width=1050, plot_height=400, tools=tools, logo=None, active_drag="box_zoom")
        self.figure.xaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.figure.yaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.figure.xaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.figure.yaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.figure.min_border_left = options.MIN_BORDER
        self.figure.min_border_bottom = options.MIN_BORDER
        self.data_1 = self.figure.circle('x', 'y',
                                         size=options.REGRESSION_1_CIRCLE_SIZE,
                                         color=options.GROUP_1_COLOR,
                                         alpha=options.REGRESSION_1_ALPHA,
                                         source=sources.corr_chart_1)
        self.data_2 = self.figure.circle('x', 'y',
                                         size=options.REGRESSION_2_CIRCLE_SIZE,
                                         color=options.GROUP_2_COLOR,
                                         alpha=options.REGRESSION_2_ALPHA,
                                         source=sources.corr_chart_2)
        self.trend_1 = self.figure.line('x', 'y',
                                        color=options.GROUP_1_COLOR,
                                        line_width=options.REGRESSION_1_LINE_WIDTH,
                                        line_dash=options.REGRESSION_1_LINE_DASH,
                                        source=sources.corr_trend_1)
        self.trend_2 = self.figure.line('x', 'y',
                                        color=options.GROUP_2_COLOR,
                                        line_width=options.REGRESSION_2_LINE_WIDTH,
                                        line_dash=options.REGRESSION_1_LINE_DASH,
                                        source=sources.corr_trend_2)
        self.figure.add_tools(HoverTool(show_arrow=True,
                                        tooltips=[('MRN', '@mrn'),
                                                  ('x', '@x{0.2f}'),
                                                  ('y', '@y{0.2f}')]))

        # Set the legend
        legend_corr_chart = Legend(items=[("Group 1", [self.data_1]),
                                          ("Lin Reg", [self.trend_1]),
                                          ("Group 2", [self.data_2]),
                                          ("Lin Reg", [self.trend_2])],
                                   location=(25, 0))

        # Add the layout outside the plot, clicking legend item hides the line
        self.figure.add_layout(legend_corr_chart, 'right')
        self.figure.legend.click_policy = "hide"

        self.x_include = CheckboxGroup(labels=["Include this ind. var. in multi-var regression"], active=[],
                                             width=400)
        self.x_prev = Button(label="<", button_type="primary", width=50)
        self.x_next = Button(label=">", button_type="primary", width=50)
        self.y_prev = Button(label="<", button_type="primary", width=50)
        self.y_next = Button(label=">", button_type="primary", width=50)
        self.x_prev.on_click(self.x_prev_ticker)
        self.x_next.on_click(self.x_next_ticker)
        self.y_prev.on_click(self.y_prev_ticker)
        self.y_next.on_click(self.y_next_ticker)
        self.x_include.on_change('active', self.x_include_ticker)

        self.do_reg_button = Button(label="Perform Multi-Var Regression", button_type="primary", width=200)
        self.do_reg_button.on_click(self.multi_var_linear_regression)

        self.x = Select(value='', options=[''], width=300)
        self.x.title = "Select an Independent Variable (x-axis)"
        self.x.on_change('value', self.update_corr_chart_ticker_x)

        self.y = Select(value='', options=[''], width=300)
        self.y.title = "Select a Dependent Variable (y-axis)"
        self.y.on_change('value', self.update_corr_chart_ticker_y)

        self.text_1 = Div(text="<b>Group 1</b>:", width=1050)
        self.text_2 = Div(text="<b>Group 2</b>:", width=1050)

        tools = "pan,wheel_zoom,box_zoom,lasso_select,poly_select,reset,crosshair,save"
        self.residual_figure = figure(plot_width=1050, plot_height=400, tools=tools, logo=None, active_drag="box_zoom")
        self.residual_figure.xaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.residual_figure.yaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.residual_figure.xaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.residual_figure.yaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        # residual_chart.min_border_left = options.MIN_BORDER
        self.residual_figure.min_border_bottom = options.MIN_BORDER
        self.residual_figure.xaxis.axis_label = 'Patient #'
        self.residual_data_1 = self.residual_figure.circle('x', 'y',
                                                           size=options.REGRESSION_1_CIRCLE_SIZE,
                                                           color=options.GROUP_1_COLOR,
                                                           alpha=options.REGRESSION_1_ALPHA,
                                                           source=sources.residual_chart_1)
        self.residual_data_2 = self.residual_figure.circle('x', 'y',
                                                           size=options.REGRESSION_2_CIRCLE_SIZE,
                                                           color=options.GROUP_2_COLOR,
                                                           alpha=options.REGRESSION_2_ALPHA,
                                                           source=sources.residual_chart_2)
        self.residual_figure.add_tools(HoverTool(show_arrow=True,
                                                 tooltips=[('ID', '@mrn'),
                                                           ('Residual', '@y'),
                                                           ('Actual', '@db_value')]))
        legend_residual_chart = Legend(items=[("Group 1", [self.residual_data_1]),
                                              ("Group 2", [self.residual_data_2])],
                                       location=(25, 0))
        self.residual_figure.add_layout(legend_residual_chart, 'right')
        self.residual_figure.legend.click_policy = "hide"

        self.layout = column(row(custom_title['1']['regression'], Spacer(width=50), custom_title['2']['regression']),
                             row(column(self.x_include,
                                        row(self.x_prev, self.x_next, Spacer(width=10), self.x),
                                        row(self.y_prev, self.y_next, Spacer(width=10), self.y)),
                                 Spacer(width=10, height=175), data_tables.corr_chart,
                                 Spacer(width=10, height=175), data_tables.multi_var_include),
                             self.figure,
                             Div(text="<hr>", width=1050),
                             self.do_reg_button,
                             self.residual_figure,
                             Div(text="<b>Group 1</b>", width=500),
                             data_tables.multi_var_coeff_1,
                             data_tables.multi_var_model_1,
                             Div(text="<b>Group 2</b>", width=500),
                             data_tables.multi_var_coeff_2,
                             data_tables.multi_var_model_2,
                             Spacer(width=1000, height=100))

    def update_corr_chart_ticker_x(self, attr, old, new):
        if self.multi_var_reg_vars[self.x.value]:
            self.x_include.active = [0]
        else:
            self.x_include.active = []
        self.update_data()

    def update_corr_chart_ticker_y(self, attr, old, new):
        self.update_data()

    def update_data(self):
        if self.x.value and self.y.value:
            x_units = self.correlation.data[N[0]][self.x.value]['units']
            y_units = self.correlation.data[N[0]][self.y.value]['units']

            data = {'x': {n: self.correlation.data[n][self.x.value]['data'] for n in N},
                    'y': {n: self.correlation.data[n][self.y.value]['data'] for n in N},
                    'mrn': {n: self.correlation.data[n][self.x.value]['mrn'] for n in N}}

            if x_units:
                if self.x.value.startswith('DVH Endpoint'):
                    label = self.x.value[14:]
                    label = {'D': 'Dose to ', 'V': 'Volume of '}[label[0]] + self.x.value.split('_')[1]
                    if '%' in label:
                        label = label + {'D': ' ROI Volume', 'V': ' Rx Dose'}[label[0]]
                    self.figure.xaxis.axis_label = "%s (%s)" % (label, x_units)
                else:
                    self.figure.xaxis.axis_label = "%s (%s)" % (self.x.value, x_units)
            else:
                self.figure.xaxis.axis_label = self.x.value.replace('/', ' or ')

            if y_units:
                if self.y.value.startswith('DVH Endpoint'):
                    label = self.y.value[14:]
                    label = {'D': 'Dose to ', 'V': 'Volume of '}[label[0]] + self.y.value.split('_')[1]
                    if '%' in label:
                        label = label + {'D': ' ROI Volume', 'V': ' Rx Dose'}[label[0]]
                    self.figure.yaxis.axis_label = "%s (%s)" % (label, y_units)
                else:
                    self.figure.yaxis.axis_label = "%s (%s)" % (self.y.value, y_units)
            else:
                self.figure.yaxis.axis_label = self.y.value.replace('/', ' or ')

            for n in N:
                getattr(self.sources, 'corr_chart_%s' % n).data = {v: data[v][n] for v in list(data)}

            group_stats = {n: [] for n in N}

            for n in N:
                if data['x'][n]:
                    slope, intercept, r_value, p_value, std_err = linregress(data['x'][n], data['y'][n])
                    group_stats[n] = [round(slope, 3),
                                      round(intercept, 3),
                                      round(r_value ** 2, 3),
                                      round(p_value, 3),
                                      round(std_err, 3),
                                      len(data['x'][n])]
                    x_trend = [min(data['x'][n]), max(data['x'][n])]
                    y_trend = np.add(np.multiply(x_trend, slope), intercept)
                    getattr(self.sources, 'corr_trend_%s' % n).data = {'x': x_trend, 'y': y_trend}
                else:
                    group_stats[n] = [''] * 6
                    clear_source_data(self.sources, 'corr_trend_%s' % n)

            self.sources.corr_chart_stats.data = {'stat': self.sources.CORR_CHART_STATS_ROW_NAMES,
                                                  'group_1': group_stats['1'],
                                                  'group_2': group_stats['2']}
        else:
            self.sources.corr_chart_stats.data = {'stat': self.sources.CORR_CHART_STATS_ROW_NAMES,
                                                  'group_1': [''] * 6,
                                                  'group_2': [''] * 6}
            for n in N:
                for k in ['corr_chart', 'corr_trend']:
                    clear_source_data(self.sources, '%s_%s' % (k, n))

    def x_prev_ticker(self):
        current_index = self.x.options.index(self.x.value)
        self.x.value = self.x.options[current_index - 1]

    def y_prev_ticker(self):
        current_index = self.y.options.index(self.y.value)
        self.y.value = self.y.options[current_index - 1]

    def x_next_ticker(self):
        current_index = self.x.options.index(self.x.value)
        if current_index == len(self.x.options) - 1:
            new_index = 0
        else:
            new_index = current_index + 1
        self.x.value = self.x.options[new_index]

    def y_next_ticker(self):
        current_index = self.y.options.index(self.y.value)
        if current_index == len(self.y.options) - 1:
            new_index = 0
        else:
            new_index = current_index + 1
        self.y.value = self.y.options[new_index]

    def x_include_ticker(self, attr, old, new):
        if new and not self.multi_var_reg_vars[self.x.value]:
            self.multi_var_reg_vars[self.x.value] = True
        if not new and self.multi_var_reg_vars[self.x.value]:
            clear_source_selection(self.sources, 'multi_var_include')
            self.multi_var_reg_vars[self.x.value] = False

        included_vars = [key for key, value in listitems(self.multi_var_reg_vars) if value]
        included_vars.sort()
        self.sources.multi_var_include.data = {'var_name': included_vars}

    def multi_var_linear_regression(self):
        print(str(datetime.now()), 'Performing multivariable regression', sep=' ')

        included_vars = [key for key in list(self.correlation.data['1']) if self.multi_var_reg_vars[key]]
        included_vars.sort()

        for n in N:
            if self.time_series.current_dvh_group[n]:
                x = []
                x_count = len(self.correlation.data[n][list(self.correlation.data[n])[0]]['data'])
                for i in range(x_count):
                    current_x = []
                    for k in included_vars:
                        current_x.append(self.correlation.data[n][k]['data'][i])
                    x.append(current_x)
                x = sm.add_constant(x)  # explicitly add constant to calculate intercept
                y = self.correlation.data[n][self.y.value]['data']

                fit = sm.OLS(y, x).fit()

                coeff = fit.params
                coeff_p = fit.pvalues
                r_sq = fit.rsquared
                model_p = fit.f_pvalue

                coeff_str = ["%0.3E" % i for i in coeff]
                coeff_p_str = ["%0.3f" % i for i in coeff_p]
                r_sq_str = ["%0.3f" % r_sq]
                model_p_str = ["%0.3f" % model_p]

                self.residual_figure.yaxis.axis_label = "Residual (%s)" % self.correlation.data[n][self.y.value]['units']

                getattr(self.sources, 'multi_var_coeff_results_%s' % n).data = {'var_name': ['Constant'] + included_vars,
                                                                                'coeff': coeff.tolist(),
                                                                                'coeff_str': coeff_str,
                                                                                'p': coeff_p.tolist(),
                                                                                'p_str': coeff_p_str}
                getattr(self.sources, 'multi_var_model_results_%s' % n).data = {'model_p': [model_p],
                                                                                'model_p_str': model_p_str,
                                                                                'r_sq': [r_sq],
                                                                                'r_sq_str': r_sq_str,
                                                                                'y_var': [self.y.value]}
                getattr(self.sources, 'residual_chart_%s' % n).data = {'x': range(1, x_count + 1),
                                                                       'y': fit.resid.tolist(),
                                                                       'mrn': self.correlation.data[n][self.y.value]['mrn'],
                                                                       'db_value': self.correlation.data[n][self.y.value]['data']}
            else:
                for k in ['multi_var_coeff_results', 'multi_var_model_results', 'residual_chart']:
                    clear_source_data(self.sources, '%s_%s'(k, n))

    def multi_var_include_selection(self, attr, old, new):
        row_index = self.sources.multi_var_include.selected.indices[0]
        self.x.value = self.sources.multi_var_include.data['var_name'][row_index]
