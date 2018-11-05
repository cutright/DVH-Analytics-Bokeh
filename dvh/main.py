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
from bokeh.models.widgets import Button, Div, DataTable, Panel, Tabs, TextInput, PasswordInput
import time
import options
from bokeh_components import columns, sources
from bokeh_components.custom_titles import custom_title
from bokeh_components.mlc_analyzer import MLC_Analyzer
from bokeh_components.time_series import TimeSeries
from bokeh_components.correlation import Correlation
from bokeh_components.roi_viewer import ROI_Viewer
from bokeh_components.rad_bio import RadBio
from bokeh_components.regression import Regression
from bokeh_components.query import Query
from bokeh_components.dvhs import DVHs


options = load_options(options)


# This depends on a user defined function in dvh/auth.py.  By default, this returns True
# It is up to the user/installer to write their own function (e.g., using python-ldap)
# Proper execution of this requires placing Bokeh behind a reverse proxy with SSL setup (HTTPS)
# Please see Bokeh documentation for more information
ACCESS_GRANTED = not options.AUTH_USER_REQ

# Categories map of dropdown values, SQL column, and SQL table (and data source for range_categories)
selector_categories = {'ROI Institutional Category': {'var_name': 'institutional_roi', 'table': 'DVHs'},
                       'ROI Physician Category': {'var_name': 'physician_roi', 'table': 'DVHs'},
                       'ROI Type': {'var_name': 'roi_type', 'table': 'DVHs'},
                       'Beam Type': {'var_name': 'beam_type', 'table': 'Beams'},
                       'Collimator Rotation Direction': {'var_name': 'collimator_rot_dir', 'table': 'Beams'},
                       'Couch Rotation Direction': {'var_name': 'couch_rot_dir', 'table': 'Beams'},
                       'Dose Grid Resolution': {'var_name': 'dose_grid_res', 'table': 'Plans'},
                       'Gantry Rotation Direction': {'var_name': 'gantry_rot_dir', 'table': 'Beams'},
                       'Radiation Type': {'var_name': 'radiation_type', 'table': 'Beams'},
                       'Patient Orientation': {'var_name': 'patient_orientation', 'table': 'Plans'},
                       'Patient Sex': {'var_name': 'patient_sex', 'table': 'Plans'},
                       'Physician': {'var_name': 'physician', 'table': 'Plans'},
                       'Tx Modality': {'var_name': 'tx_modality', 'table': 'Plans'},
                       'Tx Site': {'var_name': 'tx_site', 'table': 'Plans'},
                       'Normalization': {'var_name': 'normalization_method', 'table': 'Rxs'},
                       'Treatment Machine': {'var_name': 'treatment_machine', 'table': 'Beams'},
                       'Heterogeneity Correction': {'var_name': 'heterogeneity_correction', 'table': 'Plans'},
                       'Scan Mode': {'var_name': 'scan_mode', 'table': 'Beams'},
                       'MRN': {'var_name': 'mrn', 'table': 'Plans'},
                       'UID': {'var_name': 'study_instance_uid', 'table': 'Plans'},
                       'Baseline': {'var_name': 'baseline', 'table': 'Plans'}}
range_categories = {'Age': {'var_name': 'age', 'table': 'Plans', 'units': '', 'source': sources.plans},
                    'Beam Energy Min': {'var_name': 'beam_energy_min', 'table': 'Beams', 'units': '', 'source': sources.beams},
                    'Beam Energy Max': {'var_name': 'beam_energy_max', 'table': 'Beams', 'units': '', 'source': sources.beams},
                    'Birth Date': {'var_name': 'birth_date', 'table': 'Plans', 'units': '', 'source': sources.plans},
                    'Planned Fractions': {'var_name': 'fxs', 'table': 'Plans', 'units': '', 'source': sources.plans},
                    'Rx Dose': {'var_name': 'rx_dose', 'table': 'Plans', 'units': 'Gy', 'source': sources.plans},
                    'Rx Isodose': {'var_name': 'rx_percent', 'table': 'Rxs', 'units': '%', 'source': sources.rxs},
                    'Simulation Date': {'var_name': 'sim_study_date', 'table': 'Plans', 'units': '', 'source': sources.plans},
                    'Total Plan MU': {'var_name': 'total_mu', 'table': 'Plans', 'units': 'MU', 'source': sources.plans},
                    'Fraction Dose': {'var_name': 'fx_dose', 'table': 'Rxs', 'units': 'Gy', 'source': sources.rxs},
                    'Beam Dose': {'var_name': 'beam_dose', 'table': 'Beams', 'units': 'Gy', 'source': sources.beams},
                    'Beam MU': {'var_name': 'beam_mu', 'table': 'Beams', 'units': '', 'source': sources.beams},
                    'Control Point Count': {'var_name': 'control_point_count', 'table': 'Beams', 'units': '', 'source': sources.beams},
                    'Collimator Start Angle': {'var_name': 'collimator_start', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Collimator End Angle': {'var_name': 'collimator_end', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Collimator Min Angle': {'var_name': 'collimator_min', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Collimator Max Angle': {'var_name': 'collimator_max', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Collimator Range': {'var_name': 'collimator_range', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Couch Start Angle': {'var_name': 'couch_start', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Couch End Angle': {'var_name': 'couch_end', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Couch Min Angle': {'var_name': 'couch_min', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Couch Max Angle': {'var_name': 'couch_max', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Couch Range': {'var_name': 'couch_range', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Gantry Start Angle': {'var_name': 'gantry_start', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Gantry End Angle': {'var_name': 'gantry_end', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Gantry Min Angle': {'var_name': 'gantry_min', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Gantry Max Angle': {'var_name': 'gantry_max', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'Gantry Range': {'var_name': 'gantry_range', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                    'SSD': {'var_name': 'ssd', 'table': 'Beams', 'units': 'cm', 'source': sources.beams},
                    'ROI Min Dose': {'var_name': 'min_dose', 'table': 'DVHs', 'units': 'Gy', 'source': sources.dvhs},
                    'ROI Mean Dose': {'var_name': 'mean_dose', 'table': 'DVHs', 'units': 'Gy', 'source': sources.dvhs},
                    'ROI Max Dose': {'var_name': 'max_dose', 'table': 'DVHs', 'units': 'Gy', 'source': sources.dvhs},
                    'ROI Volume': {'var_name': 'volume', 'table': 'DVHs', 'units': 'cc', 'source': sources.dvhs},
                    'ROI Surface Area': {'var_name': 'surface_area', 'table': 'DVHs', 'units': 'cm^2', 'source': sources.dvhs},
                    'ROI Spread X': {'var_name': 'spread_x', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                    'ROI Spread Y': {'var_name': 'spread_y', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                    'ROI Spread Z': {'var_name': 'spread_z', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                    'PTV Distance (Min)': {'var_name': 'dist_to_ptv_min', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                    'PTV Distance (Mean)': {'var_name': 'dist_to_ptv_mean', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                    'PTV Distance (Median)': {'var_name': 'dist_to_ptv_median', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                    'PTV Distance (Max)': {'var_name': 'dist_to_ptv_max', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                    'PTV Distance (Centroids)': {'var_name': 'dist_to_ptv_centroids', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                    'PTV Overlap': {'var_name': 'ptv_overlap', 'table': 'DVHs', 'units': 'cc', 'source': sources.dvhs},
                    'Scan Spots': {'var_name': 'scan_spot_count', 'table': 'Beams', 'units': '', 'source': sources.beams},
                    'Beam MU per deg': {'var_name': 'beam_mu_per_deg', 'table': 'Beams', 'units': '', 'source': sources.beams},
                    'Beam MU per control point': {'var_name': 'beam_mu_per_cp', 'table': 'Beams', 'units': '', 'source': sources.beams},
                    'ROI Cross-Section Max': {'var_name': 'cross_section_max', 'table': 'DVHs', 'units': 'cm^2', 'source': sources.dvhs},
                    'ROI Cross-Section Median': {'var_name': 'cross_section_median', 'table': 'DVHs', 'units': 'cm^2', 'source': sources.dvhs}}


# correlation variable names
correlation_variables, correlation_names = [], []
correlation_variables_beam = ['Beam Dose', 'Beam MU', 'Control Point Count', 'Gantry Range',
                              'SSD', 'Beam MU per control point']
for key in list(range_categories):
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

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Bokeh component classes
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
roi_viewer = ROI_Viewer(sources)
mlc_analyzer = MLC_Analyzer(sources)
time_series = TimeSeries(sources, range_categories)
correlation = Correlation(sources, correlation_names, range_categories)
regression = Regression(sources, time_series, correlation, multi_var_reg_var_names)
correlation.add_regression_link(regression)
rad_bio = RadBio(sources, time_series, correlation, regression)
dvhs = DVHs(sources, time_series, correlation, regression)
query = Query(sources, selector_categories, range_categories, correlation_variables,
              dvhs, rad_bio, roi_viewer, time_series, correlation, regression, mlc_analyzer)
dvhs.add_query_link(query)


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


def update_planning_data_selections(uids):

    query.allow_source_update = False
    for k in ['rxs', 'plans', 'beams']:
        src = getattr(sources, k)
        src.selected.indices = [i for i, j in enumerate(src.data['uid']) if j in uids]

    query.allow_source_update = True


class SourceSelection:
    def __init__(self, table):
        self.table = table

    def ticker(self, attr, old, new):
        if query.allow_source_update:
            src = getattr(sources, self.table)
            uids = list(set([src.data['uid'][i] for i in new]))
            update_planning_data_selections(uids)


source_selection = {s: SourceSelection(s) for s in ['rxs', 'plans', 'beams']}


# Selector Category table
selection_filter_data_table = DataTable(source=sources.selectors,
                                        columns=columns.selection_filter, width=1000, height=150, index_position=None)
sources.selectors.selected.on_change('indices', query.update_selector_row_on_selection)
query.update_selector_source()


# Selector Category table
range_filter_data_table = DataTable(source=sources.ranges,
                                    columns=columns.range_filter, width=1000, height=150, index_position=None)
sources.ranges.selected.on_change('indices', query.update_range_row_on_selection)

# endpoint  table
ep_data_table = DataTable(source=sources.endpoint_defs, columns=columns.ep_data, width=300, height=150)

sources.endpoint_defs.selected.on_change('indices', dvhs.update_ep_row_on_selection)

# Set up DataTable for dvhs
data_table = DataTable(source=sources.dvhs, columns=columns.dvhs, width=1200,
                       editable=True, index_position=None)
data_table_beams = DataTable(source=sources.beams, columns=columns.beams, width=1300,
                             editable=True, index_position=None)
data_table_beams2 = DataTable(source=sources.beams, columns=columns.beams2, width=1300,
                              editable=True, index_position=None)
data_table_plans = DataTable(source=sources.plans, columns=columns.plans, width=1300,
                             editable=True, index_position=None)
data_table_rxs = DataTable(source=sources.rxs, columns=columns.rxs, width=1300,
                           editable=True, index_position=None)
data_table_endpoints = DataTable(source=sources.endpoint_view, columns=columns.endpoints, width=1200,
                                 editable=True, index_position=None)


# Listen for changes to source selections
for s in ['rxs', 'plans', 'beams']:
    getattr(sources, s).selected.on_change('indices', source_selection[s].ticker)
sources.dvhs.selected.on_change('indices', dvhs.update_source_endpoint_view_selection)
sources.endpoint_view.selected.on_change('indices', dvhs.update_dvh_table_selection)
sources.emami.selected.on_change('indices', rad_bio.emami_selection)

data_table_corr_chart = DataTable(source=sources.corr_chart_stats, columns=columns.corr_chart, editable=True,
                                  height=180, width=300, index_position=None)

data_table_multi_var_include = DataTable(source=sources.multi_var_include, columns=columns.multi_var_include,
                                         height=175, width=275, index_position=None)

data_table_multi_var_model_1 = DataTable(source=sources.multi_var_coeff_results_1, columns=columns.multi_var_model_1,
                                         editable=True, height=200, index_position=None)

data_table_multi_var_coeff_1 = DataTable(source=sources.multi_var_model_results_1, columns=columns.multi_var_coeff_1,
                                         editable=True, height=60, index_position=None)

data_table_multi_var_model_2 = DataTable(source=sources.multi_var_coeff_results_2, columns=columns.multi_var_model_2,
                                         editable=True, height=200)

data_table_multi_var_coeff_2 = DataTable(source=sources.multi_var_model_results_2, columns=columns.multi_var_coeff_2,
                                         editable=True,  height=60)

sources.multi_var_include.selected.on_change('indices', regression.multi_var_include_selection)

data_table_rad_bio = DataTable(source=sources.rad_bio, columns=columns.rad_bio, editable=False, width=1100)

data_table_emami = DataTable(source=sources.emami, columns=columns.emami, editable=False, width=1100)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Layout objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
layout_query = column(row(custom_title['1']['query'], Spacer(width=50), custom_title['2']['query'],
                          Spacer(width=50), query.query_button, Spacer(width=50), query.download_dropdown),
                      Div(text="<b>Query by Categorical Data</b>", width=1000),
                      query.add_selector_row_button,
                      row(query.selector_row, Spacer(width=10), query.select_category1, query.select_category2,
                          query.group_selector, query.delete_selector_row_button, Spacer(width=10),
                          query.selector_not_operator_checkbox),
                      selection_filter_data_table,
                      Div(text="<hr>", width=1050),
                      Div(text="<b>Query by Numerical Data</b>", width=1000),
                      query.add_range_row_button,
                      row(query.range_row, Spacer(width=10), query.select_category, query.text_min, Spacer(width=30),
                          query.text_max, Spacer(width=30), query.group_range,
                          query.delete_range_row_button, Spacer(width=10), query.range_not_operator_checkbox),
                      range_filter_data_table)

if options.LITE_VIEW:
    layout_dvhs = column(row(dvhs.radio_group_dose, dvhs.radio_group_volume),
                         dvhs.add_endpoint_row_button,
                         row(dvhs.ep_row, Spacer(width=10), dvhs.select_ep_type, dvhs.ep_text_input, Spacer(width=20),
                             dvhs.ep_units_in, dvhs.delete_ep_row_button, Spacer(width=50),
                             dvhs.download_endpoints_button),
                         ep_data_table)
else:
    layout_dvhs = column(row(custom_title['1']['dvhs'], Spacer(width=50), custom_title['2']['dvhs']),
                         row(dvhs.radio_group_dose, dvhs.radio_group_volume),
                         row(dvhs.select_reviewed_mrn, dvhs.select_reviewed_dvh, dvhs.review_rx),
                         dvhs.plot,
                         Div(text="<b>DVHs</b>", width=1200),
                         data_table,
                         Div(text="<hr>", width=1050),
                         Div(text="<b>Define Endpoints</b>", width=1000),
                         dvhs.add_endpoint_row_button,
                         row(dvhs.ep_row, Spacer(width=10), dvhs.select_ep_type, dvhs.ep_text_input, Spacer(width=20),
                             dvhs.ep_units_in, dvhs.delete_ep_row_button, Spacer(width=50),
                             dvhs.download_endpoints_button),
                         ep_data_table,
                         Div(text="<b>DVH Endpoints</b>", width=1200),
                         data_table_endpoints)

layout_rad_bio = column(row(custom_title['1']['rad_bio'], Spacer(width=50), custom_title['2']['rad_bio']),
                        Div(text="<b>Published EUD Parameters from Emami"
                                 " et. al. for 1.8-2.0Gy fractions</b> (Click to apply)",
                            width=600),
                        data_table_emami,
                        Div(text="<b>Applied Parameters:</b>", width=150),
                        row(rad_bio.eud_a_input, Spacer(width=50),
                            rad_bio.gamma_50_input, Spacer(width=50), rad_bio.td_tcd_input, Spacer(width=50),
                            rad_bio.apply_filter, Spacer(width=50), rad_bio.apply_button),
                        Div(text="<b>EUD Calculations for Query</b>", width=500),
                        data_table_rad_bio,
                        Spacer(width=1000, height=100))

layout_planning_data = column(row(custom_title['1']['planning'], Spacer(width=50), custom_title['2']['planning']),
                              Div(text="<b>Rxs</b>", width=1000), data_table_rxs,
                              Div(text="<b>Plans</b>", width=1200), data_table_plans,
                              Div(text="<b>Beams</b>", width=1500), data_table_beams,
                              Div(text="<b>Beams Continued</b>", width=1500), data_table_beams2)

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
                               Spacer(width=10, height=175), data_table_corr_chart,
                               Spacer(width=10, height=175), data_table_multi_var_include),
                           regression.figure,
                           Div(text="<hr>", width=1050),
                           regression.do_reg_button,
                           regression.residual_figure,
                           Div(text="<b>Group 1</b>", width=500),
                           data_table_multi_var_coeff_1,
                           data_table_multi_var_model_1,
                           Div(text="<b>Group 2</b>", width=500),
                           data_table_multi_var_coeff_2,
                           data_table_multi_var_model_2,
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
                             row(mlc_analyzer.mlc_viewer, mlc_analyzer.mlc_viewer_data_table))


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


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Custom authorization
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
auth_user = TextInput(value='', title='User Name:', width=150)
auth_pass = PasswordInput(value='', title='Password:', width=150)
auth_button = Button(label="Authenticate", button_type="warning", width=100)
auth_button.on_click(auth_button_click)
layout_login = row(auth_user, Spacer(width=50), auth_pass, Spacer(width=50), auth_button)

# Create the document Bokeh server will use to generate the webpage
if ACCESS_GRANTED:
    curdoc().add_root(tabs)
else:
    curdoc().add_root(layout_login)

curdoc().title = "DVH Analytics"
