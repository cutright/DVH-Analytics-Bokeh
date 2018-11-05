#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
main program for Bokeh server (re-write for new query UI)
Created on Sun Apr 21 2017
@author: Dan Cutright, PhD
"""

from __future__ import print_function
from utilities import load_options
import auth
from bokeh.layouts import column, row
from bokeh.models import Spacer
from bokeh.io import curdoc
from bokeh.models.widgets import Button, Div, Panel, Tabs, TextInput, PasswordInput
import time
import options
from bokeh_components import sources
from bokeh_components.custom_titles import custom_title
from bokeh_components.mlc_analyzer import MLC_Analyzer
from bokeh_components.time_series import TimeSeries
from bokeh_components.correlation import Correlation
from bokeh_components.roi_viewer import ROI_Viewer
from bokeh_components.rad_bio import RadBio
from bokeh_components.regression import Regression
from bokeh_components.query import Query
from bokeh_components.dvhs import DVHs
from bokeh_components.data_tables import DataTables
from bokeh_components.categories import Categories

options = load_options(options)


# This depends on a user defined function in dvh/auth.py.  By default, this returns True
# It is up to the user/installer to write their own function (e.g., using python-ldap)
# Proper execution of this requires placing Bokeh behind a reverse proxy with SSL setup (HTTPS)
# Please see Bokeh documentation for more information
ACCESS_GRANTED = not options.AUTH_USER_REQ

# Categories map of dropdown values, SQL column, and SQL table (and data source for range_categories)
categories = Categories(sources)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Correlation and Regression variable names
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
correlation_variables, correlation_names = [], []
correlation_variables_beam = ['Beam Dose', 'Beam MU', 'Control Point Count', 'Gantry Range',
                              'SSD', 'Beam MU per control point']
for key in list(categories.range):
    if key.startswith('ROI') or key.startswith('PTV') or key in {'Total Plan MU', 'Rx Dose'}:
        correlation_variables.append(key)
        correlation_names.append(key)
    if key in correlation_variables_beam:
        correlation_variables.append(key)
        for stat in ['Min', 'Mean', 'Median', 'Max']:
            correlation_names.append("%s (%s)" % (key, stat))
correlation_variables.sort()
correlation_names.sort()
multi_var_reg_var_names = correlation_names + ['EUD', 'NTCP/TCP']

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Bokeh component classes
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
data_tables = DataTables(sources)

roi_viewer = ROI_Viewer(sources)
mlc_analyzer = MLC_Analyzer(sources)
time_series = TimeSeries(sources, categories.range)
correlation = Correlation(sources, correlation_names, categories.range)
regression = Regression(sources, time_series, correlation, multi_var_reg_var_names)
correlation.add_regression_link(regression)
rad_bio = RadBio(sources, time_series, correlation, regression)
dvhs = DVHs(sources, time_series, correlation, regression)
query = Query(sources, categories, correlation_variables,
              dvhs, rad_bio, roi_viewer, time_series, correlation, regression, mlc_analyzer)
dvhs.add_query_link(query)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Listen for changes to sources
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
class SourceSelection:
    def __init__(self, table):
        self.table = table

    def ticker(self, attr, old, new):
        if query.allow_source_update:
            src = getattr(sources, self.table)
            uids = list(set([src.data['uid'][i] for i in new]))
            self.update_planning_data_selections(uids)

    @staticmethod
    def update_planning_data_selections(uids):

        query.allow_source_update = False
        for k in ['rxs', 'plans', 'beams']:
            src = getattr(sources, k)
            src.selected.indices = [i for i, j in enumerate(src.data['uid']) if j in uids]

        query.allow_source_update = True


sources.selectors.selected.on_change('indices', query.update_selector_row_on_selection)
query.update_selector_source()

sources.ranges.selected.on_change('indices', query.update_range_row_on_selection)
sources.endpoint_defs.selected.on_change('indices', dvhs.update_ep_row_on_selection)

source_selection = {s: SourceSelection(s) for s in ['rxs', 'plans', 'beams']}
for s in ['rxs', 'plans', 'beams']:
    getattr(sources, s).selected.on_change('indices', source_selection[s].ticker)
sources.dvhs.selected.on_change('indices', dvhs.update_source_endpoint_view_selection)
sources.endpoint_view.selected.on_change('indices', dvhs.update_dvh_table_selection)
sources.emami.selected.on_change('indices', rad_bio.emami_selection)
sources.multi_var_include.selected.on_change('indices', regression.multi_var_include_selection)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Layout objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
layout_query = column(row(custom_title['1']['query'], Spacer(width=50), custom_title['2']['query'],
                          Spacer(width=50), query.query_button, Spacer(width=50), query.download_dropdown),
                      Div(text="<b>Query by Categorical Data</b>", width=1000),
                      query.add_selector_row_button,
                      row(query.selector_row, Spacer(width=10), query.select_category1, query.select_category2,
                          query.group_selector, query.delete_selector_row_button, Spacer(width=10),
                          query.selector_not_operator_checkbox),
                      data_tables.selection_filter,
                      Div(text="<hr>", width=1050),
                      Div(text="<b>Query by Numerical Data</b>", width=1000),
                      query.add_range_row_button,
                      row(query.range_row, Spacer(width=10), query.select_category, query.text_min, Spacer(width=30),
                          query.text_max, Spacer(width=30), query.group_range,
                          query.delete_range_row_button, Spacer(width=10), query.range_not_operator_checkbox),
                      data_tables.range_filter)

if options.LITE_VIEW:
    layout_dvhs = column(row(dvhs.radio_group_dose, dvhs.radio_group_volume),
                         dvhs.add_endpoint_row_button,
                         row(dvhs.ep_row, Spacer(width=10), dvhs.select_ep_type, dvhs.ep_text_input, Spacer(width=20),
                             dvhs.ep_units_in, dvhs.delete_ep_row_button, Spacer(width=50),
                             dvhs.download_endpoints_button),
                         data_tables.ep)
else:
    layout_dvhs = column(row(custom_title['1']['dvhs'], Spacer(width=50), custom_title['2']['dvhs']),
                         row(dvhs.radio_group_dose, dvhs.radio_group_volume),
                         row(dvhs.select_reviewed_mrn, dvhs.select_reviewed_dvh, dvhs.review_rx),
                         dvhs.plot,
                         Div(text="<b>DVHs</b>", width=1200),
                         data_tables.dvhs,
                         Div(text="<hr>", width=1050),
                         Div(text="<b>Define Endpoints</b>", width=1000),
                         dvhs.add_endpoint_row_button,
                         row(dvhs.ep_row, Spacer(width=10), dvhs.select_ep_type, dvhs.ep_text_input, Spacer(width=20),
                             dvhs.ep_units_in, dvhs.delete_ep_row_button, Spacer(width=50),
                             dvhs.download_endpoints_button),
                         data_tables.ep,
                         Div(text="<b>DVH Endpoints</b>", width=1200),
                         data_tables.endpoints)

layout_rad_bio = column(row(custom_title['1']['rad_bio'], Spacer(width=50), custom_title['2']['rad_bio']),
                        Div(text="<b>Published EUD Parameters from Emami"
                                 " et. al. for 1.8-2.0Gy fractions</b> (Click to apply)",
                            width=600),
                        data_tables.emami,
                        Div(text="<b>Applied Parameters:</b>", width=150),
                        row(rad_bio.eud_a_input, Spacer(width=50),
                            rad_bio.gamma_50_input, Spacer(width=50), rad_bio.td_tcd_input, Spacer(width=50),
                            rad_bio.apply_filter, Spacer(width=50), rad_bio.apply_button),
                        Div(text="<b>EUD Calculations for Query</b>", width=500),
                        data_tables.rad_bio,
                        Spacer(width=1000, height=100))

layout_planning_data = column(row(custom_title['1']['planning'], Spacer(width=50), custom_title['2']['planning']),
                              Div(text="<b>Rxs</b>", width=1000), data_tables.rxs,
                              Div(text="<b>Plans</b>", width=1200), data_tables.plans,
                              Div(text="<b>Beams</b>", width=1500), data_tables.beams,
                              Div(text="<b>Beams Continued</b>", width=1500), data_tables.beams2)

layout_time_series = column(row(custom_title['1']['time_series'], Spacer(width=50), custom_title['2']['time_series']),
                            row(time_series.y_axis, time_series.look_back_units,
                                time_series.look_back_distance,
                                Spacer(width=10), time_series.plot_percentile, Spacer(width=10),
                                time_series.trend_update_button),
                            time_series.plot,
                            time_series.download_time_plot,
                            Div(text="<hr>", width=1050),
                            row(time_series.histogram_bin_slider, time_series.histogram_radio_group),
                            row(time_series.histogram_normaltest_1_text, time_series.histogram_ttest_text),
                            row(time_series.histogram_normaltest_2_text, time_series.histogram_ranksums_text),
                            time_series.histograms,
                            Spacer(width=1000, height=100))

layout_roi_viewer = column(row(custom_title['1']['roi_viewer'], Spacer(width=50), custom_title['2']['roi_viewer']),
                           row(roi_viewer.mrn_select, roi_viewer.study_date_select, roi_viewer.uid_select),
                           Div(text="<hr>", width=800),
                           row(roi_viewer.roi_select['1'], roi_viewer.roi_select_color['1'], roi_viewer.slice_select,
                               roi_viewer.previous_slice, roi_viewer.next_slice),
                           Div(text="<hr>", width=800),
                           row(roi_viewer.roi_select['2'], roi_viewer.roi_select['3'],
                               roi_viewer.roi_select['4'], roi_viewer.roi_select['5']),
                           row(roi_viewer.roi_select_color['2'], roi_viewer.roi_select_color['3'],
                               roi_viewer.roi_select_color['4'], roi_viewer.roi_select_color['5']),
                           row(Div(text="<b>NOTE:</b> Axis flipping requires a figure reset "
                                        "(Click the circular double-arrow)", width=1025)),
                           row(roi_viewer.flip_x_axis_button, roi_viewer.flip_y_axis_button,
                               roi_viewer.plot_tv_button),
                           row(roi_viewer.scrolling),
                           row(roi_viewer.fig),
                           row(Spacer(width=1000, height=100)))

layout_correlation_matrix = column(row(custom_title['1']['correlation'], Spacer(width=50),
                                       custom_title['2']['correlation']),
                                   correlation.download_corr_fig,
                                   row(Div(text="<b>Sample Sizes</b>", width=100), correlation.fig_text_1,
                                       correlation.fig_text_2),
                                   row(correlation.fig, correlation.fig_include, correlation.fig_include_2))

layout_regression = column(row(custom_title['1']['regression'], Spacer(width=50), custom_title['2']['regression']),
                           row(column(regression.x_include,
                                      row(regression.x_prev, regression.x_next, Spacer(width=10), regression.x),
                                      row(regression.y_prev, regression.y_next, Spacer(width=10), regression.y)),
                               Spacer(width=10, height=175), data_tables.corr_chart,
                               Spacer(width=10, height=175), data_tables.multi_var_include),
                           regression.figure,
                           Div(text="<hr>", width=1050),
                           regression.do_reg_button,
                           regression.residual_figure,
                           Div(text="<b>Group 1</b>", width=500),
                           data_tables.multi_var_coeff_1,
                           data_tables.multi_var_model_1,
                           Div(text="<b>Group 2</b>", width=500),
                           data_tables.multi_var_coeff_2,
                           data_tables.multi_var_model_2,
                           Spacer(width=1000, height=100))

layout_mlc_analyzer = column(row(custom_title['1']['mlc_analyzer'], Spacer(width=50),
                                 custom_title['2']['mlc_analyzer']),
                             row(mlc_analyzer.mrn_select, mlc_analyzer.study_date_select, mlc_analyzer.uid_select),
                             row(mlc_analyzer.plan_select),
                             Div(text="<hr>", width=800),
                             row(mlc_analyzer.fx_grp_select, mlc_analyzer.beam_select,
                                 mlc_analyzer.mlc_viewer_previous_cp, mlc_analyzer.mlc_viewer_next_cp,
                                 Spacer(width=10), mlc_analyzer.mlc_viewer_play_button, Spacer(width=10),
                                 mlc_analyzer.mlc_viewer_beam_score),
                             row(mlc_analyzer.mlc_viewer, data_tables.mlc_viewer))


query_tab = Panel(child=layout_query, title='Query')
dvh_tab = Panel(child=layout_dvhs, title='DVHs')
rad_bio_tab = Panel(child=layout_rad_bio, title='Rad Bio')
optional_tabs = [('ROI Viewer', Panel(child=layout_roi_viewer, title='ROI Viewer')),
                 ('Planning Data', Panel(child=layout_planning_data, title='Planning Data')),
                 ('Time-Series', Panel(child=layout_time_series, title='Time-Series')),
                 ('Correlation', Panel(child=layout_correlation_matrix, title='Correlation')),
                 ('Regression', Panel(child=layout_regression, title='Regression')),
                 ('MLC Analyzer', Panel(child=layout_mlc_analyzer, title='MLC Analyzer'))]

if options.LITE_VIEW:
    rendered_tabs = [query_tab, dvh_tab]
else:
    rendered_tabs = [query_tab, dvh_tab, rad_bio_tab] + \
                    [tab for (title, tab) in optional_tabs if options.OPTIONAL_TABS[title]]

tabs = Tabs(tabs=rendered_tabs)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Custom authorization
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def auth_button_click():
    global ACCESS_GRANTED

    if not ACCESS_GRANTED:
        ACCESS_GRANTED = auth.check_credentials(auth_user.value, auth_pass.value, 'generic')
        if ACCESS_GRANTED:
            auth_button.label = 'Access Granted'
            auth_button.button_type = 'success'
            curdoc().clear()
            curdoc().add_root(tabs)
        else:
            auth_button.label = 'Failed'
            auth_button.button_type = 'danger'
            time.sleep(3)
            auth_button.label = 'Authenticate'
            auth_button.button_type = 'warning'


auth_user = TextInput(value='', title='User Name:', width=150)
auth_pass = PasswordInput(value='', title='Password:', width=150)
auth_button = Button(label="Authenticate", button_type="warning", width=100)
auth_button.on_click(auth_button_click)
layout_login = row(auth_user, Spacer(width=50), auth_pass, Spacer(width=50), auth_button)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Create the document Bokeh server will use to generate the web page
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
if ACCESS_GRANTED:
    curdoc().add_root(tabs)
else:
    curdoc().add_root(layout_login)

curdoc().title = "DVH Analytics"
