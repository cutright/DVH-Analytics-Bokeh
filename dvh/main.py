#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
main program for Bokeh server (re-write for new query UI)
Created on Sun Apr 21 2017
@author: Dan Cutright, PhD
"""


from __future__ import print_function
from future.utils import listitems
from analysis_tools import DVH, calc_eud
from utilities import Temp_DICOM_FileSet, get_planes_from_string, get_union,\
    collapse_into_single_dates, moving_avg, calc_stats, get_study_instance_uids
import auth
from sql_connector import DVH_SQL
from sql_to_python import QuerySQL
import numpy as np
import itertools
from datetime import datetime
from os.path import dirname, join
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Legend, CustomJS, HoverTool, Slider, Spacer
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.palettes import Colorblind8 as palette
from bokeh.models.widgets import Select, Button, Div, TableColumn, DataTable, Panel, Tabs, NumberFormatter,\
    RadioButtonGroup, TextInput, RadioGroup, CheckboxButtonGroup, Dropdown, CheckboxGroup, PasswordInput
from dicompylercore import dicomparser, dvhcalc
from bokeh import events
from scipy.stats import ttest_ind, ranksums, normaltest, pearsonr, linregress
from math import pi
import statsmodels.api as sm
import matplotlib.colors as plot_colors
import time
from options import *

# This depends on a user defined function in dvh/auth.py.  By default, this returns True
# It is up to the user/installer to write their own function (e.g., using python-ldap)
# Proper execution of this requires placing Bokeh behind a reverse proxy with SSL setup (HTTPS)
# Please see Bokeh documentation for more information
ACCESS_GRANTED = not AUTH_USER_REQ

SELECT_CATEGORY1_DEFAULT = 'ROI Institutional Category'
SELECT_CATEGORY_DEFAULT = 'Rx Dose'

# Used to keep Query UI clean
ALLOW_SOURCE_UPDATE = True

# Declare variables
colors = itertools.cycle(palette)
current_dvh, current_dvh_group_1, current_dvh_group_2 = [], [], []
anon_id_map = {}
x, y = [], []
uids_1, uids_2 = [], []
correlation_1, correlation_2 = {}, {}

temp_dvh_info = Temp_DICOM_FileSet()
dvh_review_mrns = temp_dvh_info.mrn
if dvh_review_mrns[0] != '':
    dvh_review_rois = temp_dvh_info.get_roi_names(dvh_review_mrns[0]).values()
    dvh_review_mrns.append('')
else:
    dvh_review_rois = ['']


roi_viewer_data, roi2_viewer_data, roi3_viewer_data, roi4_viewer_data, roi5_viewer_data = {}, {}, {}, {}, {}
tv_data = {}


# Bokeh column data sources
source = ColumnDataSource(data=dict(color=[], x=[], y=[], mrn=[]))
source_selectors = ColumnDataSource(data=dict(row=[1], category1=[''], category2=[''],
                                              group=[''], group_label=[''], not_status=['']))
source_ranges = ColumnDataSource(data=dict(row=[], category=[], min=[], max=[], min_display=[], max_display=[],
                                           group=[], group_label=[], not_status=[]))
source_endpoint_defs = ColumnDataSource(data=dict(row=[], output_type=[], input_type=[], input_value=[],
                                                  label=[], units_in=[], units_out=[]))
source_endpoint_calcs = ColumnDataSource(data=dict())
source_endpoint_view = ColumnDataSource(data=dict(mrn=[], group=[], roi_name=[], ep1=[], ep2=[], ep3=[], ep4=[], ep5=[],
                                                  ep6=[], ep7=[], ep8=[], ep9=[], ep10=[]))
source_beams = ColumnDataSource(data=dict())
source_plans = ColumnDataSource(data=dict())
source_rxs = ColumnDataSource(data=dict())
source_patch_1 = ColumnDataSource(data=dict(x_patch=[], y_patch=[]))
source_patch_2 = ColumnDataSource(data=dict(x_patch=[], y_patch=[]))
source_stats_1 = ColumnDataSource(data=dict(x=[], min=[], q1=[], mean=[], median=[], q3=[], max=[]))
source_stats_2 = ColumnDataSource(data=dict(x=[], min=[], q1=[], mean=[], median=[], q3=[], max=[]))
source_roi_viewer = ColumnDataSource(data=dict(x=[], y=[]))
source_roi2_viewer = ColumnDataSource(data=dict(x=[], y=[]))
source_roi3_viewer = ColumnDataSource(data=dict(x=[], y=[]))
source_roi4_viewer = ColumnDataSource(data=dict(x=[], y=[]))
source_roi5_viewer = ColumnDataSource(data=dict(x=[], y=[]))
source_tv = ColumnDataSource(data=dict(x=[], y=[]))
source_rad_bio = ColumnDataSource(data=dict(mrn=[], uid=[], roi_name=[], ptv_overlap=[], roi_type=[], rx_dose=[],
                                            fxs=[], fx_dose=[], eud_a=[], gamma_50=[], td_tcp=[], eud=[], ntcp_tcp=[]))
source_time_1 = ColumnDataSource(data=dict(x=[], y=[], mrn=[]))
source_time_2 = ColumnDataSource(data=dict(x=[], y=[], mrn=[]))
source_time_trend_1 = ColumnDataSource(data=dict(x=[], y=[], w=[], mrn=[]))
source_time_trend_2 = ColumnDataSource(data=dict(x=[], y=[], w=[], mrn=[]))
source_time_collapsed = ColumnDataSource(data=dict(x=[], y=[], w=[], mrn=[]))
source_time_bound_1 = ColumnDataSource(data=dict(x=[], upper=[], avg=[], lower=[], mrn=[]))
source_time_bound_2 = ColumnDataSource(data=dict(x=[], upper=[], avg=[], lower=[], mrn=[]))
source_time_patch_1 = ColumnDataSource(data=dict(x=[], y=[]))
source_time_patch_2 = ColumnDataSource(data=dict(x=[], y=[]))
source_histogram_1 = ColumnDataSource(data=dict(x=[], top=[], width=[]))
source_histogram_2 = ColumnDataSource(data=dict(x=[], top=[], width=[]))
source_corr_matrix_line = ColumnDataSource(data=dict(x=[], y=[]))
source_correlation_1_pos = ColumnDataSource(data=dict(x=[], y=[], x_name=[], y_name=[], color=[], alpha=[], r=[], p=[],
                                                      group=[], size=[], x_normality=[], y_normality=[]))
source_correlation_1_neg = ColumnDataSource(data=dict(x=[], y=[], x_name=[], y_name=[], color=[], alpha=[], r=[], p=[],
                                                      group=[], size=[], x_normality=[], y_normality=[]))
source_correlation_2_pos = ColumnDataSource(data=dict(x=[], y=[], x_name=[], y_name=[], color=[], alpha=[], r=[], p=[],
                                                      group=[], size=[], x_normality=[], y_normality=[]))
source_correlation_2_neg = ColumnDataSource(data=dict(x=[], y=[], x_name=[], y_name=[], color=[], alpha=[], r=[], p=[],
                                                      group=[], size=[], x_normality=[], y_normality=[]))
source_corr_chart_1 = ColumnDataSource(data=dict(x=[], y=[], mrn=[]))
source_corr_chart_2 = ColumnDataSource(data=dict(x=[], y=[], mrn=[]))
source_corr_trend_1 = ColumnDataSource(data=dict(x=[], y=[]))
source_corr_trend_2 = ColumnDataSource(data=dict(x=[], y=[]))
corr_chart_stats_row_names = ['slope', 'y-intercept', 'R-squared', 'p-value', 'std. err.', 'sample size']
source_corr_chart_stats = ColumnDataSource(data=dict(stat=corr_chart_stats_row_names,
                                                     group_1=[''] * 6, group_2=[''] * 6))
source_multi_var_include = ColumnDataSource(data=dict(var_name=[]))
source_multi_var_coeff_results_1 = ColumnDataSource(data=dict(var_name=[], coeff=[], coeff_str=[], p=[], p_str=[]))
source_multi_var_model_results_1 = ColumnDataSource(data=dict(model_p=[], model_p_str=[],
                                                              r_sq=[], r_sq_str=[], y_var=[]))
source_multi_var_coeff_results_2 = ColumnDataSource(data=dict(var_name=[], coeff=[], coeff_str=[], p=[], p_str=[]))
source_multi_var_model_results_2 = ColumnDataSource(data=dict(model_p=[], model_p_str=[],
                                                              r_sq=[], r_sq_str=[], y_var=[]))


# Categories map of dropdown values, SQL column, and SQL table (and data source for range_categories)
selector_categories = {'ROI Institutional Category': {'var_name': 'institutional_roi', 'table': 'DVHs'},
                       'ROI Physician Category': {'var_name': 'physician_roi', 'table': 'DVHs'},
                       'ROI Type': {'var_name': 'roi_type', 'table': 'DVHs'},
                       'Beam Type': {'var_name': 'beam_type', 'table': 'Beams'},
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
range_categories = {'Age': {'var_name': 'age', 'table': 'Plans', 'units': '', 'source': source_plans},
                    'Beam Energy Min': {'var_name': 'beam_energy_min', 'table': 'Beams', 'units': '', 'source': source_beams},
                    'Beam Energy Max': {'var_name': 'beam_energy_max', 'table': 'Beams', 'units': '', 'source': source_beams},
                    'Birth Date': {'var_name': 'birth_date', 'table': 'Plans', 'units': '', 'source': source_plans},
                    'Planned Fractions': {'var_name': 'fxs', 'table': 'Plans', 'units': '', 'source': source_plans},
                    'Rx Dose': {'var_name': 'rx_dose', 'table': 'Plans', 'units': 'Gy', 'source': source_plans},
                    'Rx Isodose': {'var_name': 'rx_percent', 'table': 'Rxs', 'units': '%', 'source': source_rxs},
                    'Simulation Date': {'var_name': 'sim_study_date', 'table': 'Plans', 'units': '', 'source': source_plans},
                    'Total Plan MU': {'var_name': 'total_mu', 'table': 'Plans', 'units': 'MU', 'source': source_plans},
                    'Fraction Dose': {'var_name': 'fx_dose', 'table': 'Rxs', 'units': 'Gy', 'source': source_rxs},
                    'Beam Dose': {'var_name': 'beam_dose', 'table': 'Beams', 'units': 'Gy', 'source': source_beams},
                    'Beam MU': {'var_name': 'beam_mu', 'table': 'Beams', 'units': '', 'source': source_beams},
                    'Control Point Count': {'var_name': 'control_point_count', 'table': 'Beams', 'units': '', 'source': source_beams},
                    'Collimator Start Angle': {'var_name': 'collimator_start', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Collimator End Angle': {'var_name': 'collimator_end', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Collimator Min Angle': {'var_name': 'collimator_min', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Collimator Max Angle': {'var_name': 'collimator_max', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Collimator Range': {'var_name': 'collimator_range', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Couch Start Angle': {'var_name': 'couch_start', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Couch End Angle': {'var_name': 'couch_end', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Couch Min Angle': {'var_name': 'couch_min', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Couch Max Angle': {'var_name': 'couch_max', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Couch Range': {'var_name': 'couch_range', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Gantry Start Angle': {'var_name': 'gantry_start', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Gantry End Angle': {'var_name': 'gantry_end', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Gantry Min Angle': {'var_name': 'gantry_min', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Gantry Max Angle': {'var_name': 'gantry_max', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Gantry Range': {'var_name': 'gantry_range', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'SSD': {'var_name': 'ssd', 'table': 'Beams', 'units': 'cm', 'source': source_beams},
                    'ROI Min Dose': {'var_name': 'min_dose', 'table': 'DVHs', 'units': 'Gy', 'source': source},
                    'ROI Mean Dose': {'var_name': 'mean_dose', 'table': 'DVHs', 'units': 'Gy', 'source': source},
                    'ROI Max Dose': {'var_name': 'max_dose', 'table': 'DVHs', 'units': 'Gy', 'source': source},
                    'ROI Volume': {'var_name': 'volume', 'table': 'DVHs', 'units': 'cc', 'source': source},
                    'ROI Surface Area': {'var_name': 'surface_area', 'table': 'DVHs', 'units': 'cm^2', 'source': source},
                    'PTV Distance (Min)': {'var_name': 'dist_to_ptv_min', 'table': 'DVHs', 'units': 'cm', 'source': source},
                    'PTV Distance (Mean)': {'var_name': 'dist_to_ptv_mean', 'table': 'DVHs', 'units': 'cm', 'source': source},
                    'PTV Distance (Median)': {'var_name': 'dist_to_ptv_median', 'table': 'DVHs', 'units': 'cm', 'source': source},
                    'PTV Distance (Max)': {'var_name': 'dist_to_ptv_max', 'table': 'DVHs', 'units': 'cm', 'source': source},
                    'PTV Overlap': {'var_name': 'ptv_overlap', 'table': 'DVHs', 'units': 'cc', 'source': source},
                    'Scan Spots': {'var_name': 'scan_spot_count', 'table': 'Beams', 'units': '', 'source': source_beams},
                    'Beam MU per deg': {'var_name': 'beam_mu_per_deg', 'table': 'Beams', 'units': '', 'source': source_beams},
                    'Beam MU per control point': {'var_name': 'beam_mu_per_cp', 'table': 'Beams', 'units': '', 'source': source_beams}}

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
multi_var_reg_vars = {name: False for name in multi_var_reg_var_names}

# The following block of code is a work-around for Bokeh 0.12.7 - 0.12.9 (current version)
source.js_on_change('data', CustomJS(args=dict(source=source), code="source.change.emit()"))
source_beams.js_on_change('data', CustomJS(args=dict(source=source_beams), code="source.change.emit()"))
source_plans.js_on_change('data', CustomJS(args=dict(source=source_plans), code="source.change.emit()"))
source_rxs.js_on_change('data', CustomJS(args=dict(source=source_rxs), code="source.change.emit()"))
source_rad_bio.js_on_change('data', CustomJS(args=dict(source=source_rad_bio), code="source.change.emit()"))
source_multi_var_include.js_on_change('data', CustomJS(args=dict(source=source_multi_var_include),
                                                       code="source.change.emit()"))
source_multi_var_coeff_results_1.js_on_change('data', CustomJS(args=dict(source=source_multi_var_coeff_results_1),
                                                               code="source.change.emit()"))
source_multi_var_coeff_results_2.js_on_change('data', CustomJS(args=dict(source=source_multi_var_coeff_results_2),
                                                               code="source.change.emit()"))
source_multi_var_model_results_1.js_on_change('data', CustomJS(args=dict(source=source_multi_var_model_results_1),
                                                               code="source.change.emit()"))
source_multi_var_model_results_2.js_on_change('data', CustomJS(args=dict(source=source_multi_var_model_results_2),
                                                               code="source.change.emit()"))


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Functions for Querying by categorical data
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def update_select_category2_values():
    new = select_category1.value
    table_new = selector_categories[new]['table']
    var_name_new = selector_categories[new]['var_name']
    new_options = DVH_SQL().get_unique_values(table_new, var_name_new)
    select_category2.options = new_options
    select_category2.value = new_options[0]


def ensure_selector_group_is_assigned(attr, old, new):
    if not group_selector.active:
        group_selector.active = [-old[0] + 1]
    update_selector_source()


def update_selector_source():
    if selector_row.value:
        r = int(selector_row.value) - 1
        group = sum([i+1 for i in group_selector.active])
        group_labels = ['1', '2', '1 & 2']
        group_label = group_labels[group-1]
        not_status = ['', 'Not'][len(selector_not_operator_checkbox.active)]

        patch = {'category1': [(r, select_category1.value)], 'category2': [(r, select_category2.value)],
                 'group': [(r, group)], 'group_label': [(r, group_label)], 'not_status': [(r, not_status)]}
        source_selectors.patch(patch)


def add_selector_row():
    if source_selectors.data['row']:
        temp = source_selectors.data

        for key in list(temp):
            temp[key].append('')
        temp['row'][-1] = len(temp['row'])

        source_selectors.data = temp
        new_options = [str(x+1) for x in range(0, len(temp['row']))]
        selector_row.options = new_options
        selector_row.value = new_options[-1]
        select_category1.value = SELECT_CATEGORY1_DEFAULT
        select_category2.value = select_category2.options[0]
        selector_not_operator_checkbox.active = []
    else:
        selector_row.options = ['1']
        selector_row.value = '1'
        source_selectors.data = dict(row=[1], category1=[''], category2=[''],
                                     group=[], group_label=[''], not_status=[''])
    update_selector_source()

    clear_source_selection(source_selectors)


def select_category1_ticker(attr, old, new):
    update_select_category2_values()
    update_selector_source()


def select_category2_ticker(attr, old, new):
    update_selector_source()


def selector_not_operator_ticker(attr, old, new):
    update_selector_source()


def selector_row_ticker(attr, old, new):
    if source_selectors.data['category1'] and source_selectors.data['category1'][-1]:
        r = int(selector_row.value) - 1
        category1 = source_selectors.data['category1'][r]
        category2 = source_selectors.data['category2'][r]
        group = source_selectors.data['group'][r]
        not_status = source_selectors.data['not_status'][r]

        select_category1.value = category1
        select_category2.value = category2
        group_selector.active = [[0], [1], [0, 1]][group-1]
        if not_status:
            selector_not_operator_checkbox.active = [0]
        else:
            selector_not_operator_checkbox.active = []


def update_selector_row_on_selection(attr, old, new):
    if new['1d']['indices']:
        selector_row.value = selector_row.options[min(new['1d']['indices'])]


def delete_selector_row():
    if selector_row.value:
        new_selectors_source = source_selectors.data
        index_to_delete = int(selector_row.value) - 1
        new_source_length = len(source_selectors.data['category1']) - 1

        if new_source_length == 0:
            source_selectors.data = dict(row=[], category1=[], category2=[], group=[], group_label=[], not_status=[])
            selector_row.options = ['']
            selector_row.value = ''
            group_selector.active = [0]
            selector_not_operator_checkbox.active = []
            select_category1.value = SELECT_CATEGORY1_DEFAULT
            select_category2.value = select_category2.options[0]
        else:
            for key in list(new_selectors_source):
                new_selectors_source[key].pop(index_to_delete)

            for i in range(index_to_delete, new_source_length):
                new_selectors_source['row'][i] -= 1

            selector_row.options = [str(x+1) for x in range(0, new_source_length)]
            if selector_row.value not in selector_row.options:
                selector_row.value = selector_row.options[-1]
            source_selectors.data = new_selectors_source

        clear_source_selection(source_selectors)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Functions for Querying by numerical data
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def add_range_row():
    if source_ranges.data['row']:
        temp = source_ranges.data

        for key in list(temp):
            temp[key].append('')
        temp['row'][-1] = len(temp['row'])
        source_ranges.data = temp
        new_options = [str(x+1) for x in range(0, len(temp['row']))]
        range_row.options = new_options
        range_row.value = new_options[-1]
        select_category.value = SELECT_CATEGORY_DEFAULT
        group_range.active = [0]
        range_not_operator_checkbox.active = []
    else:
        range_row.options = ['1']
        range_row.value = '1'
        source_ranges.data = dict(row=['1'], category=[''], min=[''], max=[''], min_display=[''], max_display=[''],
                                  group=[''], group_label=[''], not_status=[''])

    update_range_titles(reset_values=True)
    update_range_source()

    clear_source_selection(source_ranges)


def update_range_source():
    if range_row.value:
        table = range_categories[select_category.value]['table']
        var_name = range_categories[select_category.value]['var_name']

        r = int(range_row.value) - 1
        group = sum([i+1 for i in group_range.active])  # a result of 3 means group 1 & 2
        group_labels = ['1', '2', '1 & 2']
        group_label = group_labels[group-1]
        not_status = ['', 'Not'][len(range_not_operator_checkbox.active)]

        try:
            min_float = float(text_min.value)
        except ValueError:
            try:
                min_float = float(DVH_SQL().get_min_value(table, var_name))
            except TypeError:
                min_float = ''

        try:
            max_float = float(text_max.value)
        except ValueError:
            try:
                max_float = float(DVH_SQL().get_max_value(table, var_name))
            except TypeError:
                max_float = ''

        if min_float or min_float == 0.:
            min_display = "%s %s" % (str(min_float), range_categories[select_category.value]['units'])
        else:
            min_display = 'None'

        if max_float or max_float == 0.:
            max_display = "%s %s" % (str(max_float), range_categories[select_category.value]['units'])
        else:
            max_display = 'None'

        patch = {'category': [(r, select_category.value)], 'min': [(r, min_float)], 'max': [(r, max_float)],
                 'min_display': [(r, min_display)], 'max_display': [(r, max_display)],
                 'group': [(r, group)], 'group_label': [(r, group_label)], 'not_status': [(r, not_status)]}
        source_ranges.patch(patch)

        group_range.active = [[0], [1], [0, 1]][group - 1]
        text_min.value = str(min_float)
        text_max.value = str(max_float)


def update_range_titles(reset_values=False):
    table = range_categories[select_category.value]['table']
    var_name = range_categories[select_category.value]['var_name']
    min_value = DVH_SQL().get_min_value(table, var_name)
    text_min.title = 'Min: ' + str(min_value) + ' ' + range_categories[select_category.value]['units']
    max_value = DVH_SQL().get_max_value(table, var_name)
    text_max.title = 'Max: ' + str(max_value) + ' ' + range_categories[select_category.value]['units']

    if reset_values:
        text_min.value = str(min_value)
        text_max.value = str(max_value)


def range_row_ticker(attr, old, new):
    global ALLOW_SOURCE_UPDATE
    if source_ranges.data['category'] and source_ranges.data['category'][-1]:
        r = int(new) - 1
        category = source_ranges.data['category'][r]
        min_new = source_ranges.data['min'][r]
        max_new = source_ranges.data['max'][r]
        group = source_ranges.data['group'][r]
        not_status = source_ranges.data['not_status'][r]

        ALLOW_SOURCE_UPDATE = False
        select_category.value = category
        text_min.value = str(min_new)
        text_max.value = str(max_new)
        update_range_titles()
        group_range.active = [[0], [1], [0, 1]][group - 1]
        ALLOW_SOURCE_UPDATE = True
        if not_status:
            range_not_operator_checkbox.active = [0]
        else:
            range_not_operator_checkbox.active = []


def select_category_ticker(attr, old, new):
    if ALLOW_SOURCE_UPDATE:
        update_range_titles(reset_values=True)
        update_range_source()


def min_text_ticker(attr, old, new):
    if ALLOW_SOURCE_UPDATE:
        update_range_source()


def max_text_ticker(attr, old, new):
    if ALLOW_SOURCE_UPDATE:
        update_range_source()


def range_not_operator_ticker(attr, old, new):
    if ALLOW_SOURCE_UPDATE:
        update_range_source()


def delete_range_row():
    if range_row.value:
        new_range_source = source_ranges.data
        index_to_delete = int(range_row.value) - 1
        new_source_length = len(source_ranges.data['category']) - 1

        if new_source_length == 0:
            source_ranges.data = dict(row=[], category=[], min=[], max=[], min_display=[], max_display=[],
                                      group=[], group_label=[''], not_status=[])
            range_row.options = ['']
            range_row.value = ''
            group_range.active = [0]
            range_not_operator_checkbox.active = []
            select_category.value = SELECT_CATEGORY_DEFAULT
            text_min.value = ''
            text_max.value = ''
        else:
            for key in list(new_range_source):
                new_range_source[key].pop(index_to_delete)

            for i in range(index_to_delete, new_source_length):
                new_range_source['row'][i] -= 1

            range_row.options = [str(x+1) for x in range(0, new_source_length)]
            if range_row.value not in range_row.options:
                range_row.value = range_row.options[-1]
            source_ranges.data = new_range_source

        clear_source_selection(source_ranges)


def ensure_range_group_is_assigned(attrname, old, new):
    if not group_range.active:
        group_range.active = [-old[0] + 1]
    update_range_source()


def update_range_row_on_selection(attr, old, new):
    if new['1d']['indices']:
        range_row.value = range_row.options[min(new['1d']['indices'])]


def clear_source_selection(src):
    src.selected = {'0d': {'glyph': None, 'indices': []},
                    '1d': {'indices': []},
                    '2d': {'indices': {}}}


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Functions for adding DVH endpoints
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def add_endpoint():
    if source_endpoint_defs.data['row']:
        temp = source_endpoint_defs.data

        for key in list(temp):
            temp[key].append('')
        temp['row'][-1] = len(temp['row'])
        source_endpoint_defs.data = temp
        new_options = [str(x+1) for x in range(0, len(temp['row']))]
        ep_row.options = new_options
        ep_row.value = new_options[-1]
    else:
        ep_row.options = ['1']
        ep_row.value = '1'
        source_endpoint_defs.data = dict(row=['1'], output_type=[''], input_type=[''], input_value=[''],
                                         label=[''], units_in=[''], units_out=[''])
        if not ep_text_input.value:
            ep_text_input.value = '1'

    update_ep_source()

    clear_source_selection(source_endpoint_defs)


def update_ep_source():
    if ep_row.value:

        r = int(ep_row.value) - 1

        if 'Dose' in select_ep_type.value:
            input_type, output_type = 'Volume', 'Dose'
            if '%' in select_ep_type.value:
                units_out = '%'
            else:
                units_out = 'Gy'
            units_in = ['cc', '%'][ep_units_in.active]
            label = "D_%s%s" % (ep_text_input.value, units_in)
        else:
            input_type, output_type = 'Dose', 'Volume'
            if '%' in select_ep_type.value:
                units_out = '%'
            else:
                units_out = 'cc'
            units_in = ['Gy', '%'][ep_units_in.active]
            label = "V_%s%s" % (ep_text_input.value, units_in)

        try:
            input_value = float(ep_text_input.value)
        except:
            input_value = 1

        patch = {'output_type': [(r, output_type)], 'input_type': [(r, input_type)],
                 'input_value': [(r, input_value)], 'label': [(r, label)],
                 'units_in': [(r, units_in)], 'units_out': [(r, units_out)]}
        source_endpoint_defs.patch(patch)
        update_source_endpoint_calcs()


def ep_units_in_ticker(attr, old, new):
    if ALLOW_SOURCE_UPDATE:
        update_ep_text_input_title()
        update_ep_source()


def update_ep_text_input_title():
    if 'Dose' in select_ep_type.value:
        ep_text_input.title = "Input Volume (%s):" % ['cc', '%'][ep_units_in.active]
    else:
        ep_text_input.title = "Input Dose (%s):" % ['Gy', '%'][ep_units_in.active]


def select_ep_type_ticker(attr, old, new):
    if ALLOW_SOURCE_UPDATE:
        if 'Dose' in new:
            ep_units_in.labels = ['cc', '%']
        else:
            ep_units_in.labels = ['Gy', '%']

        update_ep_text_input_title()
        update_ep_source()


def ep_text_input_ticker(attr, old, new):
    if ALLOW_SOURCE_UPDATE:
        update_ep_source()


def delete_ep_row():
    if ep_row.value:
        new_ep_source = source_endpoint_defs.data
        index_to_delete = int(ep_row.value) - 1
        new_source_length = len(source_endpoint_defs.data['output_type']) - 1

        if new_source_length == 0:
            source_endpoint_defs.data = dict(row=[], output_type=[], input_type=[], input_value=[],
                                             label=[], units_in=[], units_out=[])
            ep_row.options = ['']
            ep_row.value = ''
        else:
            for key in list(new_ep_source):
                new_ep_source[key].pop(index_to_delete)

            for i in range(index_to_delete, new_source_length):
                new_ep_source['row'][i] -= 1

            ep_row.options = [str(x+1) for x in range(0, new_source_length)]
            if ep_row.value not in ep_row.options:
                ep_row.value = ep_row.options[-1]
            source_endpoint_defs.data = new_ep_source

        update_source_endpoint_calcs()  # not efficient, but still relatively quick
        clear_source_selection(source_endpoint_defs)


def update_ep_row_on_selection(attr, old, new):
    global ALLOW_SOURCE_UPDATE
    ALLOW_SOURCE_UPDATE = False

    if new['1d']['indices']:
        data = source_endpoint_defs.data
        r = min(new['1d']['indices'])

        # update row
        ep_row.value = ep_row.options[r]

        # update input value
        ep_text_input.value = str(data['input_value'][r])

        # update input units radio button
        if '%' in data['units_in'][r]:
            ep_units_in.active = 1
        else:
            ep_units_in.active = 0

        # update output
        if 'Dose' in data['output_type'][r]:
            if '%' in data['units_in'][r]:
                select_ep_type.value = ep_options[1]
            else:
                select_ep_type.value = ep_options[0]
        else:
            if '%' in data['units_in'][r]:
                select_ep_type.value = ep_options[3]
            else:
                select_ep_type.value = ep_options[2]

    ALLOW_SOURCE_UPDATE = True


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Query functions
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!

# This function returns the list of information needed to execute QuerySQL from
# SQL_to_Python.py (i.e., uids and dvh_condition)
# This function can be used for one group at a time, or both groups. Using both groups is useful so that duplicate
# DVHs do not show up in the plot (i.e., if a DVH satisfies both group criteria)
def get_query(group=None):

    if group:
        if group == 1:
            active_groups = [1]
        elif group == 2:
            active_groups = [2]
    else:
        active_groups = [1, 2]

    # Used to accumulate lists of query strings for each table
    # Will assume each item in list is complete query for that SQL column
    queries = {'Plans': [], 'Rxs': [], 'Beams': [], 'DVHs': []}

    # Used to group queries by variable, will combine all queries of same variable with an OR operator
    # e.g., queries_by_sql_column['Plans'][key] = list of strings, where key is sql column
    queries_by_sql_column = {'Plans': {}, 'Rxs': {}, 'Beams': {}, 'DVHs': {}}

    for active_group in active_groups:

        # Accumulate categorical query strings
        data = source_selectors.data
        for r in data['row']:
            r = int(r)
            if data['group'][r-1] in {active_group, 3}:
                var_name = selector_categories[data['category1'][r-1]]['var_name']
                table = selector_categories[data['category1'][r-1]]['table']
                value = data['category2'][r-1]
                if data['not_status'][r-1]:
                    operator = "!="
                else:
                    operator = "="

                query_str = "%s %s '%s'" % (var_name, operator, value)

                # Append query_str in query_by_sql_column
                if var_name not in queries_by_sql_column[table].keys():
                    queries_by_sql_column[table][var_name] = []
                queries_by_sql_column[table][var_name].append(query_str)

        # Accumulate numerical query strings
        data = source_ranges.data
        for r in data['row']:
            r = int(r)
            if data['group'][r-1] in {active_group, 3}:
                var_name = range_categories[data['category'][r-1]]['var_name']
                table = range_categories[data['category'][r-1]]['table']

                value_low = float(data['min'][r-1])
                value_high = float(data['max'][r-1])

                # Modify value_low and value_high so SQL interprets values as dates, if applicable
                if var_name in {'sim_study_date', 'birth_date'}:
                    value_low = "'%s'::date" % value_low
                    value_high = "'%s'::date" % value_high

                if data['not_status'][r-1]:
                    query_str = var_name + " NOT BETWEEN " + str(value_low) + " AND " + str(value_high)
                else:
                    query_str = var_name + " BETWEEN " + str(value_low) + " AND " + str(value_high)

                # Append query_str in query_by_sql_column
                if var_name not in queries_by_sql_column[table]:
                    queries_by_sql_column[table][var_name] = []
                queries_by_sql_column[table][var_name].append(query_str)

    for table in queries:
        temp_str = []
        for v in queries_by_sql_column[table].keys():

            # collect all constraints for a given sql column into one list
            q_by_sql_col = [q for q in queries_by_sql_column[table][v]]

            # combine all constraints for a given sql column with 'or' operators
            temp_str.append("(%s)" % ' OR '.join(q_by_sql_col))

        queries[table] = ' AND '.join(temp_str)
        print(str(datetime.now()), '%s = %s' % (table, queries[table]), sep=' ')

    # Get a list of UIDs that fit the plan, rx, and beam query criteria.  DVH query criteria will not alter the
    # list of UIDs, therefore dvh_query is not needed to get the UID list
    print(str(datetime.now()), 'getting uids', sep=' ')
    uids = get_study_instance_uids(plans=queries['Plans'], rxs=queries['Rxs'], beams=queries['Beams'])['union']

    # uids: a unique list of all uids that satisfy the criteria
    # queries['DVHs']: the dvh query string for SQL
    return uids, queries['DVHs']


# main update function
def update_data():
    global current_dvh, current_dvh_group_1, current_dvh_group_2
    old_update_button_label = query_button.label
    old_update_button_type = query_button.button_type
    query_button.label = 'Updating...'
    query_button.button_type = 'warning'
    print(str(datetime.now()), 'Constructing query for complete dataset', sep=' ')
    uids, dvh_query_str = get_query()
    print(str(datetime.now()), 'getting dvh data', sep=' ')
    current_dvh = DVH(uid=uids, dvh_condition=dvh_query_str)
    if current_dvh.count:
        print(str(datetime.now()), 'initializing source data ', current_dvh.query, sep=' ')
        current_dvh_group_1, current_dvh_group_2 = update_dvh_data(current_dvh)
        print(str(datetime.now()), 'updating correlation data')
        update_correlation()
        print(str(datetime.now()), 'correlation data updated')
        update_source_endpoint_calcs()
        calculate_review_dvh()
        initialize_rad_bio_source()
        control_chart_y.value = ''
        update_roi_viewer_mrn()
    else:
        print(str(datetime.now()), 'empty dataset returned', sep=' ')
        query_button.label = 'No Data'
        query_button.button_type = 'danger'
        time.sleep(2.5)

    query_button.label = old_update_button_label
    query_button.button_type = old_update_button_type


# input is a DVH class from Analysis_Tools.py
# This function creates a new ColumnSourceData and calls
# the functions to update beam, rx, and plans ColumnSourceData variables
def update_dvh_data(dvh):
    global uids_1, uids_2, anon_id_map

    dvh_group_1, dvh_group_2 = [], []
    group_1_constraint_count, group_2_constraint_count = group_constraint_count()

    if group_1_constraint_count and group_2_constraint_count:
        extra_rows = 12
    elif group_1_constraint_count or group_2_constraint_count:
        extra_rows = 6
    else:
        extra_rows = 0

    print(str(datetime.now()), 'updating dvh data', sep=' ')
    line_colors = [color for j, color in itertools.izip(range(0, dvh.count + extra_rows), colors)]

    x_axis = np.round(np.add(np.linspace(0, dvh.bin_count, dvh.bin_count) / 100., 0.005), 3)

    print(str(datetime.now()), 'beginning stat calcs', sep=' ')

    if radio_group_dose.active == 1:
        stat_dose_scale = 'relative'
        x_axis_stat = dvh.get_resampled_x_axis()
    else:
        stat_dose_scale = 'absolute'
        x_axis_stat = x_axis
    if radio_group_volume.active == 0:
        stat_volume_scale = 'absolute'
    else:
        stat_volume_scale = 'relative'

    print(str(datetime.now()), 'calculating patches', sep=' ')

    if group_1_constraint_count == 0:
        uids_1 = []
        source_patch_1.data = {'x_patch': [],
                               'y_patch': []}
        source_stats_1.data = {'x': [],
                               'min': [],
                               'q1': [],
                               'mean': [],
                               'median': [],
                               'q3': [],
                               'max': []}
    else:
        print(str(datetime.now()), 'Constructing Group 1 query', sep=' ')
        uids_1, dvh_query_str = get_query(group=1)
        dvh_group_1 = DVH(uid=uids_1, dvh_condition=dvh_query_str)
        uids_1 = dvh_group_1.study_instance_uid
        stat_dvhs_1 = dvh_group_1.get_standard_stat_dvh(dose_scale=stat_dose_scale, volume_scale=stat_volume_scale)

        if radio_group_dose.active == 1:
            x_axis_1 = dvh_group_1.get_resampled_x_axis()
        else:
            x_axis_1 = np.add(np.linspace(0, dvh_group_1.bin_count, dvh_group_1.bin_count) / 100., 0.005)

        source_patch_1.data = {'x_patch': np.append(x_axis_1, x_axis_1[::-1]).tolist(),
                               'y_patch': np.append(stat_dvhs_1['q3'], stat_dvhs_1['q1'][::-1]).tolist()}
        source_stats_1.data = {'x': x_axis_1.tolist(),
                               'min': stat_dvhs_1['min'].tolist(),
                               'q1': stat_dvhs_1['q1'].tolist(),
                               'mean': stat_dvhs_1['mean'].tolist(),
                               'median': stat_dvhs_1['median'].tolist(),
                               'q3': stat_dvhs_1['q3'].tolist(),
                               'max': stat_dvhs_1['max'].tolist()}
    if group_2_constraint_count == 0:
        uids_2 = []
        source_patch_2.data = {'x_patch': [],
                               'y_patch': []}
        source_stats_2.data = {'x': [],
                               'min': [],
                               'q1': [],
                               'mean': [],
                               'median': [],
                               'q3': [],
                               'max': []}
    else:
        print(str(datetime.now()), 'Constructing Group 2 query', sep=' ')
        uids_2, dvh_query_str = get_query(group=2)
        dvh_group_2 = DVH(uid=uids_2, dvh_condition=dvh_query_str)
        uids_2 = dvh_group_2.study_instance_uid
        stat_dvhs_2 = dvh_group_2.get_standard_stat_dvh(dose_scale=stat_dose_scale, volume_scale=stat_volume_scale)

        if radio_group_dose.active == 1:
            x_axis_2 = dvh_group_2.get_resampled_x_axis()
        else:
            x_axis_2 = np.add(np.linspace(0, dvh_group_2.bin_count, dvh_group_2.bin_count) / 100., 0.005)

        source_patch_2.data = {'x_patch': np.append(x_axis_2, x_axis_2[::-1]).tolist(),
                               'y_patch': np.append(stat_dvhs_2['q3'], stat_dvhs_2['q1'][::-1]).tolist()}
        source_stats_2.data = {'x': x_axis_2.tolist(),
                               'min': stat_dvhs_2['min'].tolist(),
                               'q1': stat_dvhs_2['q1'].tolist(),
                               'mean': stat_dvhs_2['mean'].tolist(),
                               'median': stat_dvhs_2['median'].tolist(),
                               'q3': stat_dvhs_2['q3'].tolist(),
                               'max': stat_dvhs_2['max'].tolist()}

    print(str(datetime.now()), 'patches calculated', sep=' ')

    if radio_group_dose.active == 0:
        x_scale = ['Gy'] * (dvh.count + extra_rows + 1)
        dvh_plots.xaxis.axis_label = "Dose (Gy)"
    else:
        x_scale = ['%RxDose'] * (dvh.count + extra_rows + 1)
        dvh_plots.xaxis.axis_label = "Relative Dose (to Rx)"
    if radio_group_volume.active == 0:
        y_scale = ['cm^3'] * (dvh.count + extra_rows + 1)
        dvh_plots.yaxis.axis_label = "Absolute Volume (cc)"
    else:
        y_scale = ['%Vol'] * (dvh.count + extra_rows + 1)
        dvh_plots.yaxis.axis_label = "Relative Volume"

    # new_endpoint_columns = [''] * (dvh.count + extra_rows + 1)

    x_data, y_data = [], []
    for n in range(0, dvh.count):
        if radio_group_dose.active == 0:
            x_data.append(x_axis.tolist())
        else:
            x_data.append(np.divide(x_axis, dvh.rx_dose[n]).tolist())
        if radio_group_volume.active == 0:
            y_data.append(np.multiply(dvh.dvh[:, n], dvh.volume[n]).tolist())
        else:
            y_data.append(dvh.dvh[:, n].tolist())

    y_names = ['Max', 'Q3', 'Median', 'Mean', 'Q1', 'Min']

    # Determine Population group (blue (1) or red (2))
    dvh_groups = []
    for r in range(0, len(dvh.study_instance_uid)):

        current_uid = dvh.study_instance_uid[r]
        current_roi = dvh.roi_name[r]

        if dvh_group_1:
            for r1 in range(0, len(dvh_group_1.study_instance_uid)):
                if dvh_group_1.study_instance_uid[r1] == current_uid and dvh_group_1.roi_name[r1] == current_roi:
                    dvh_groups.append('Group 1')

        if dvh_group_2:
            for r2 in range(0, len(dvh_group_2.study_instance_uid)):
                if dvh_group_2.study_instance_uid[r2] == current_uid and dvh_group_2.roi_name[r2] == current_roi:
                    if len(dvh_groups) == r + 1:
                        dvh_groups[r] = 'Group 1 & 2'
                    else:
                        dvh_groups.append('Group 2')

        if len(dvh_groups) < r + 1:
            dvh_groups.append('error')

    dvh_groups.insert(0, 'Review')

    for n in range(0, 6):
        if group_1_constraint_count > 0:
            dvh.mrn.append(y_names[n])
            dvh.roi_name.append('N/A')
            x_data.append(x_axis_stat.tolist())
            current = stat_dvhs_1[y_names[n].lower()].tolist()
            y_data.append(current)
            dvh_groups.append('Group 1')
        if group_2_constraint_count > 0:
            dvh.mrn.append(y_names[n])
            dvh.roi_name.append('N/A')
            x_data.append(x_axis_stat.tolist())
            current = stat_dvhs_2[y_names[n].lower()].tolist()
            y_data.append(current)
            dvh_groups.append('Group 2')

    # Adjust dvh object to include stats data
    if extra_rows > 0:
        dvh.study_instance_uid.extend(['N/A'] * extra_rows)
        dvh.institutional_roi.extend(['N/A'] * extra_rows)
        dvh.physician_roi.extend(['N/A'] * extra_rows)
        dvh.roi_type.extend(['Stat'] * extra_rows)
    if group_1_constraint_count > 0:
        dvh.rx_dose.extend(calc_stats(dvh_group_1.rx_dose))
        dvh.volume.extend(calc_stats(dvh_group_1.volume))
        dvh.surface_area.extend(calc_stats(dvh_group_1.surface_area))
        dvh.min_dose.extend(calc_stats(dvh_group_1.min_dose))
        dvh.mean_dose.extend(calc_stats(dvh_group_1.mean_dose))
        dvh.max_dose.extend(calc_stats(dvh_group_1.max_dose))
        dvh.dist_to_ptv_min.extend(calc_stats(dvh_group_1.dist_to_ptv_min))
        dvh.dist_to_ptv_median.extend(calc_stats(dvh_group_1.dist_to_ptv_median))
        dvh.dist_to_ptv_mean.extend(calc_stats(dvh_group_1.dist_to_ptv_mean))
        dvh.dist_to_ptv_max.extend(calc_stats(dvh_group_1.dist_to_ptv_max))
        dvh.ptv_overlap.extend(calc_stats(dvh_group_1.ptv_overlap))
    if group_2_constraint_count > 0:
        dvh.rx_dose.extend(calc_stats(dvh_group_2.rx_dose))
        dvh.volume.extend(calc_stats(dvh_group_2.volume))
        dvh.surface_area.extend(calc_stats(dvh_group_2.surface_area))
        dvh.min_dose.extend(calc_stats(dvh_group_2.min_dose))
        dvh.mean_dose.extend(calc_stats(dvh_group_2.mean_dose))
        dvh.max_dose.extend(calc_stats(dvh_group_2.max_dose))
        dvh.dist_to_ptv_min.extend(calc_stats(dvh_group_2.dist_to_ptv_min))
        dvh.dist_to_ptv_median.extend(calc_stats(dvh_group_2.dist_to_ptv_median))
        dvh.dist_to_ptv_mean.extend(calc_stats(dvh_group_2.dist_to_ptv_mean))
        dvh.dist_to_ptv_max.extend(calc_stats(dvh_group_2.dist_to_ptv_max))
        dvh.ptv_overlap.extend(calc_stats(dvh_group_2.ptv_overlap))

    # Adjust dvh object for review dvh
    dvh.dvh = np.insert(dvh.dvh, 0, 0, 1)
    dvh.count += 1
    dvh.mrn.insert(0, select_reviewed_mrn.value)
    dvh.study_instance_uid.insert(0, '')
    dvh.institutional_roi.insert(0, '')
    dvh.physician_roi.insert(0, '')
    dvh.roi_name.insert(0, select_reviewed_dvh.value)
    dvh.roi_type.insert(0, 'Review')
    dvh.rx_dose.insert(0, 0)
    dvh.volume.insert(0, 0)
    dvh.surface_area.insert(0, '')
    dvh.min_dose.insert(0, '')
    dvh.mean_dose.insert(0, '')
    dvh.max_dose.insert(0, '')
    dvh.dist_to_ptv_min.insert(0, 'N/A')
    dvh.dist_to_ptv_mean.insert(0, 'N/A')
    dvh.dist_to_ptv_median.insert(0, 'N/A')
    dvh.dist_to_ptv_max.insert(0, 'N/A')
    dvh.ptv_overlap.insert(0, 'N/A')
    line_colors.insert(0, 'green')
    x_data.insert(0, [0])
    y_data.insert(0, [0])

    # anonymize ids
    anon_id_map = {mrn: i for i, mrn in enumerate(list(set(dvh.mrn)))}
    anon_id = [anon_id_map[dvh.mrn[i]] for i in range(0, len(dvh.mrn))]

    print(str(datetime.now()), 'writing source.data', sep=' ')
    source.data = {'mrn': dvh.mrn,
                   'anon_id': anon_id,
                   'group': dvh_groups,
                   'uid': dvh.study_instance_uid,
                   'roi_institutional': dvh.institutional_roi,
                   'roi_physician': dvh.physician_roi,
                   'roi_name': dvh.roi_name,
                   'roi_type': dvh.roi_type,
                   'rx_dose': dvh.rx_dose,
                   'volume': dvh.volume,
                   'surface_area': dvh.surface_area,
                   'min_dose': dvh.min_dose,
                   'mean_dose': dvh.mean_dose,
                   'max_dose': dvh.max_dose,
                   'dist_to_ptv_min': dvh.dist_to_ptv_min,
                   'dist_to_ptv_mean': dvh.dist_to_ptv_mean,
                   'dist_to_ptv_median': dvh.dist_to_ptv_median,
                   'dist_to_ptv_max': dvh.dist_to_ptv_max,
                   'ptv_overlap': dvh.ptv_overlap,
                   'x': x_data,
                   'y': y_data,
                   'color': line_colors,
                   'x_scale': x_scale,
                   'y_scale': y_scale}

    print(str(datetime.now()), 'begin updating beam, plan, rx data sources', sep=' ')
    update_beam_data(dvh.study_instance_uid)
    update_plan_data(dvh.study_instance_uid)
    update_rx_data(dvh.study_instance_uid)
    print(str(datetime.now()), 'all sources set', sep=' ')

    return dvh_group_1, dvh_group_2


# updates beam ColumnSourceData for a given list of uids
def update_beam_data(uids):

    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    beam_data = QuerySQL('Beams', cond_str)

    groups = get_group_list(beam_data.study_instance_uid)

    anon_id = [anon_id_map[beam_data.mrn[i]] for i in range(0, len(beam_data.mrn))]

    source_beams.data = {'mrn': beam_data.mrn,
                         'anon_id': anon_id,
                         'group': groups,
                         'uid': beam_data.study_instance_uid,
                         'beam_dose': beam_data.beam_dose,
                         'beam_energy_min': beam_data.beam_energy_min,
                         'beam_energy_max': beam_data.beam_energy_max,
                         'beam_mu': beam_data.beam_mu,
                         'beam_mu_per_deg': beam_data.beam_mu_per_deg,
                         'beam_mu_per_cp': beam_data.beam_mu_per_cp,
                         'beam_name': beam_data.beam_name,
                         'beam_number': beam_data.beam_number,
                         'beam_type': beam_data.beam_type,
                         'scan_mode': beam_data.scan_mode,
                         'scan_spot_count': beam_data.scan_spot_count,
                         'control_point_count': beam_data.control_point_count,
                         'fx_count': beam_data.fx_count,
                         'fx_grp_beam_count': beam_data.fx_grp_beam_count,
                         'fx_grp_number': beam_data.fx_grp_number,
                         'gantry_start': beam_data.gantry_start,
                         'gantry_end': beam_data.gantry_end,
                         'gantry_rot_dir': beam_data.gantry_rot_dir,
                         'gantry_range': beam_data.gantry_range,
                         'gantry_min': beam_data.gantry_min,
                         'gantry_max': beam_data.gantry_max,
                         'collimator_start': beam_data.collimator_start,
                         'collimator_end': beam_data.collimator_end,
                         'collimator_rot_dir': beam_data.collimator_rot_dir,
                         'collimator_range': beam_data.collimator_range,
                         'collimator_min': beam_data.collimator_min,
                         'collimator_max': beam_data.collimator_max,
                         'couch_start': beam_data.couch_start,
                         'couch_end': beam_data.couch_end,
                         'couch_rot_dir': beam_data.couch_rot_dir,
                         'couch_range': beam_data.couch_range,
                         'couch_min': beam_data.couch_min,
                         'couch_max': beam_data.couch_max,
                         'radiation_type': beam_data.radiation_type,
                         'ssd': beam_data.ssd,
                         'treatment_machine': beam_data.treatment_machine}


# updates plan ColumnSourceData for a given list of uids
def update_plan_data(uids):

    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    plan_data = QuerySQL('Plans', cond_str)

    # Determine Groups
    groups = get_group_list(plan_data.study_instance_uid)

    anon_id = [anon_id_map[plan_data.mrn[i]] for i in range(0, len(plan_data.mrn))]

    source_plans.data = {'mrn': plan_data.mrn,
                         'anon_id': anon_id,
                         'uid': plan_data.study_instance_uid,
                         'group': groups,
                         'age': plan_data.age,
                         'birth_date': plan_data.birth_date,
                         'dose_grid_res': plan_data.dose_grid_res,
                         'fxs': plan_data.fxs,
                         'patient_orientation': plan_data.patient_orientation,
                         'patient_sex': plan_data.patient_sex,
                         'physician': plan_data.physician,
                         'rx_dose': plan_data.rx_dose,
                         'sim_study_date': plan_data.sim_study_date,
                         'total_mu': plan_data.total_mu,
                         'tx_modality': plan_data.tx_modality,
                         'tx_site': plan_data.tx_site,
                         'heterogeneity_correction': plan_data.heterogeneity_correction,
                         'baseline': plan_data.baseline}


# updates rx ColumnSourceData for a given list of uids
def update_rx_data(uids):

    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    rx_data = QuerySQL('Rxs', cond_str)

    groups = get_group_list(rx_data.study_instance_uid)

    anon_id = [anon_id_map[rx_data.mrn[i]] for i in range(0, len(rx_data.mrn))]

    source_rxs.data = {'mrn': rx_data.mrn,
                       'anon_id': anon_id,
                       'uid': rx_data.study_instance_uid,
                       'group': groups,
                       'plan_name': rx_data.plan_name,
                       'fx_dose': rx_data.fx_dose,
                       'rx_percent': rx_data.rx_percent,
                       'fxs': rx_data.fxs,
                       'rx_dose': rx_data.rx_dose,
                       'fx_grp_count': rx_data.fx_grp_count,
                       'fx_grp_name': rx_data.fx_grp_name,
                       'fx_grp_number': rx_data.fx_grp_number,
                       'normalization_method': rx_data.normalization_method,
                       'normalization_object': rx_data.normalization_object}


def get_group_list(uids):

    groups = []
    for r in range(0, len(uids)):
        if uids[r] in uids_1:
            if uids[r] in uids_2:
                groups.append('Group 1 & 2')
            else:
                groups.append('Group 1')
        else:
            groups.append('Group 2')

    return groups


def group_constraint_count():
    data = source_selectors.data
    g1a = len([r for r in data['row'] if data['group'][int(r)-1] in {1, 3}])
    g2a = len([r for r in data['row'] if data['group'][int(r)-1] in {2, 3}])

    data = source_ranges.data
    g1b = len([r for r in data['row'] if data['group'][int(r)-1] in {1, 3}])
    g2b = len([r for r in data['row'] if data['group'][int(r)-1] in {2, 3}])

    return g1a + g1b, g2a + g2b


def update_source_endpoint_calcs():
    if current_dvh:
        group_1_constraint_count, group_2_constraint_count = group_constraint_count()

        ep = {'mrn': ['']}
        ep_1, ep_2 = {}, {}

        table_columns = []

        ep['mrn'] = current_dvh.mrn
        ep['uid'] = current_dvh.study_instance_uid
        ep['group'] = source.data['group']
        ep['roi_name'] = source.data['roi_name']

        table_columns.append(TableColumn(field='mrn', title='MRN'))
        table_columns.append(TableColumn(field='group', title='Group'))
        table_columns.append(TableColumn(field='roi_name', title='ROI Name'))

        data = source_endpoint_defs.data
        for r in range(0, len(data['row'])):
            ep_name = str(data['label'][r])
            table_columns.append(TableColumn(field=ep_name, title=ep_name, formatter=NumberFormatter(format="0.00")))
            x = data['input_value'][r]

            if '%' in data['units_in'][r]:
                endpoint_input = 'relative'
                x /= 100.
            else:
                endpoint_input = 'absolute'

            if '%' in data['units_out'][r]:
                endpoint_output = 'relative'
            else:
                endpoint_output = 'absolute'

            if 'Dose' in data['output_type'][r]:
                ep[ep_name] = current_dvh.get_dose_to_volume(x, volume_scale=endpoint_input, dose_scale=endpoint_output)
                if current_dvh_group_1:
                    ep_1[ep_name] = current_dvh_group_1.get_dose_to_volume(x,
                                                                           volume_scale=endpoint_input,
                                                                           dose_scale=endpoint_output)
                if current_dvh_group_2:
                    ep_2[ep_name] = current_dvh_group_2.get_dose_to_volume(x,
                                                                           volume_scale=endpoint_input,
                                                                           dose_scale=endpoint_output)

            else:
                ep[ep_name] = current_dvh.get_volume_of_dose(x, dose_scale=endpoint_input, volume_scale=endpoint_output)
                if current_dvh_group_1:
                    ep_1[ep_name] = current_dvh_group_1.get_volume_of_dose(x,
                                                                           dose_scale=endpoint_input,
                                                                           volume_scale=endpoint_output)
                if current_dvh_group_2:
                    ep_2[ep_name] = current_dvh_group_2.get_volume_of_dose(x,
                                                                           dose_scale=endpoint_input,
                                                                           volume_scale=endpoint_output)

            if group_1_constraint_count and group_2_constraint_count:
                ep_1_stats = calc_stats(ep_1[ep_name])
                ep_2_stats = calc_stats(ep_2[ep_name])
                stats = []
                for i in range(0, len(ep_1_stats)):
                    stats.append(ep_1_stats[i])
                    stats.append(ep_2_stats[i])
                ep[ep_name].extend(stats)
            else:
                ep[ep_name].extend(calc_stats(ep[ep_name]))

        source_endpoint_calcs.data = ep
        update_endpoint_view()

    update_time_series_options()


def update_endpoint_view():
    if current_dvh:
        rows = len(source_endpoint_calcs.data['mrn'])
        ep_view = {'mrn': source_endpoint_calcs.data['mrn'],
                   'group': source_endpoint_calcs.data['group'],
                   'roi_name': source_endpoint_calcs.data['roi_name']}
        for i in range(1, ENDPOINT_COUNT+1):
            ep_view["ep%s" % i] = [''] * rows  # filling table with empty strings

        for r in range(0, len(source_endpoint_defs.data['row'])):
            if r < ENDPOINT_COUNT:  # limiting UI to 10 columns since create a whole new table is very slow in Bokeh
                key = source_endpoint_defs.data['label'][r]
                ep_view["ep%s" % (r+1)] = source_endpoint_calcs.data[key]

        source_endpoint_view.data = ep_view
        update_endpoints_in_correlation()


def update_time_series_options():
    new_options = list(range_categories)
    new_options.extend(['EUD', 'NTCP/TCP'])

    for ep in source_endpoint_calcs.data:
        if ep.startswith('V_') or ep.startswith('D_'):
            new_options.append("DVH Endpoint: %s" % ep)

    new_options.sort()
    new_options.insert(0, '')

    control_chart_y.options = new_options
    control_chart_y.value = ''


def update_roi_viewer_mrn():
    options = [mrn for mrn in source_plans.data['mrn']]
    if options:
        options.sort()
        roi_viewer_mrn_select.options = options
        roi_viewer_mrn_select.value = options[0]
    else:
        roi_viewer_mrn_select.options = ['']
        roi_viewer_mrn_select.value = ''


def roi_viewer_mrn_ticker(attr, old, new):

    if new == '':
        roi_viewer_study_date_select.options = ['']
        roi_viewer_study_date_select.value = ''
        roi_viewer_uid_select.options = ['']
        roi_viewer_uid_select.value = ''
        roi_viewer_roi_select.options = ['']
        roi_viewer_roi_select.value = ''
        roi_viewer_roi2_select.options = ['']
        roi_viewer_roi2_select.value = ''
        roi_viewer_roi3_select.options = ['']
        roi_viewer_roi3_select.value = ''
        roi_viewer_roi4_select.options = ['']
        roi_viewer_roi4_select.value = ''
        roi_viewer_roi5_select.options = ['']
        roi_viewer_roi5_select.value = ''

    else:
        # Clear out additional ROIs since current values may not exist in new patient set
        roi_viewer_roi2_select.value = ''
        roi_viewer_roi3_select.value = ''
        roi_viewer_roi4_select.value = ''
        roi_viewer_roi5_select.value = ''

        options = []
        for i in range(0, len(source_plans.data['mrn'])):
            if source_plans.data['mrn'][i] == new:
                options.append(source_plans.data['sim_study_date'][i])
        options.sort()
        old_sim_date = roi_viewer_study_date_select.value
        roi_viewer_study_date_select.options = options
        roi_viewer_study_date_select.value = options[0]
        if old_sim_date == options[0]:
            update_roi_viewer_uid()


def roi_viewer_study_date_ticker(attr, old, new):
    update_roi_viewer_uid()


def update_roi_viewer_uid():
    if roi_viewer_mrn_select.value != '':
        options = []
        for i in range(0, len(source_plans.data['mrn'])):
            if source_plans.data['mrn'][i] == roi_viewer_mrn_select.value and \
                            source_plans.data['sim_study_date'][i] == roi_viewer_study_date_select.value:
                options.append(source_plans.data['uid'][i])
        roi_viewer_uid_select.options = options
        roi_viewer_uid_select.value = options[0]


def roi_viewer_uid_ticker(attr, old, new):
    update_roi_viewer_rois()


def roi_viewer_roi_ticker(attr, old, new):
    global roi_viewer_data
    roi_viewer_data = update_roi_viewer_data(roi_viewer_roi_select.value)
    update_roi_viewer_slice()


def roi_viewer_roi2_ticker(attr, old, new):
    global roi2_viewer_data
    roi2_viewer_data = update_roi_viewer_data(roi_viewer_roi2_select.value)
    update_roi2_viewer()


def roi_viewer_roi3_ticker(attr, old, new):
    global roi3_viewer_data
    roi3_viewer_data = update_roi_viewer_data(roi_viewer_roi3_select.value)
    update_roi3_viewer()


def roi_viewer_roi4_ticker(attr, old, new):
    global roi4_viewer_data
    roi4_viewer_data = update_roi_viewer_data(roi_viewer_roi4_select.value)
    update_roi4_viewer()


def roi_viewer_roi5_ticker(attr, old, new):
    global roi5_viewer_data
    roi5_viewer_data = update_roi_viewer_data(roi_viewer_roi5_select.value)
    update_roi5_viewer()


def roi_viewer_roi1_color_ticker(attr, old, new):
    roi_viewer_patch1.glyph.fill_color = new
    roi_viewer_patch1.glyph.line_color = new


def roi_viewer_roi2_color_ticker(attr, old, new):
    roi_viewer_patch2.glyph.fill_color = new
    roi_viewer_patch2.glyph.line_color = new


def roi_viewer_roi3_color_ticker(attr, old, new):
    roi_viewer_patch3.glyph.fill_color = new
    roi_viewer_patch3.glyph.line_color = new


def roi_viewer_roi4_color_ticker(attr, old, new):
    roi_viewer_patch4.glyph.fill_color = new
    roi_viewer_patch4.glyph.line_color = new


def roi_viewer_roi5_color_ticker(attr, old, new):
    roi_viewer_patch5.glyph.fill_color = new
    roi_viewer_patch5.glyph.line_color = new


def roi_viewer_slice_ticker(attr, old, new):
    update_roi_viewer()
    update_roi2_viewer()
    update_roi3_viewer()
    update_roi4_viewer()
    update_roi5_viewer()
    source_tv.data = {'x': [], 'y': [], 'z': []}


def update_roi_viewer_slice():
    options = list(roi_viewer_data)
    options.sort()
    roi_viewer_slice_select.options = options
    roi_viewer_slice_select.value = options[len(options) / 2]  # default to the middle slice


def roi_viewer_go_to_previous_slice():
    index = roi_viewer_slice_select.options.index(roi_viewer_slice_select.value)
    roi_viewer_slice_select.value = roi_viewer_slice_select.options[index - 1]


def roi_viewer_go_to_next_slice():
    index = roi_viewer_slice_select.options.index(roi_viewer_slice_select.value)
    if index + 1 == len(roi_viewer_slice_select.options):
        index = -1
    roi_viewer_slice_select.value = roi_viewer_slice_select.options[index + 1]


def update_roi_viewer_rois():

    options = DVH_SQL().get_unique_values('DVHs', 'roi_name', "study_instance_uid = '%s'" % roi_viewer_uid_select.value)
    options.sort()

    roi_viewer_roi_select.options = options
    # default to an external like ROI if found
    if 'external' in options:
        roi_viewer_roi_select.value = 'external'
    elif 'ext' in options:
        roi_viewer_roi_select.value = 'ext'
    elif 'body' in options:
        roi_viewer_roi_select.value = 'body'
    elif 'skin' in options:
        roi_viewer_roi_select.value = 'skin'
    else:
        roi_viewer_roi_select.value = options[0]

    roi_viewer_roi2_select.options = [''] + options
    roi_viewer_roi2_select.value = ''

    roi_viewer_roi3_select.options = [''] + options
    roi_viewer_roi3_select.value = ''

    roi_viewer_roi4_select.options = [''] + options
    roi_viewer_roi4_select.value = ''

    roi_viewer_roi5_select.options = [''] + options
    roi_viewer_roi5_select.value = ''


def update_roi_viewer_data(roi_name):

    # if roi_name is an empty string (default selection), return an empty data set
    if not roi_name:
        return {'0': {'x': [], 'y': [], 'z': []}}

    roi_data = {}
    uid = roi_viewer_uid_select.value
    roi_coord_string = DVH_SQL().query('dvhs',
                                       'roi_coord_string',
                                       "study_instance_uid = '%s' and roi_name = '%s'" % (uid, roi_name))
    roi_planes = get_planes_from_string(roi_coord_string[0][0])
    for z_plane in list(roi_planes):
        x, y, z = [], [], []
        for polygon in roi_planes[z_plane]:
            initial_polygon_index = len(x)
            for point in polygon:
                x.append(point[0])
                y.append(point[1])
                z.append(point[2])
            x.append(x[initial_polygon_index])
            y.append(y[initial_polygon_index])
            z.append(z[initial_polygon_index])
            x.append(float('nan'))
            y.append(float('nan'))
            z.append(float('nan'))
        roi_data[z_plane] = {'x': x, 'y': y, 'z': z}

    return roi_data


def update_tv_data():
    global tv_data
    tv_data = {}

    uid = roi_viewer_uid_select.value
    ptv_coordinates_strings = DVH_SQL().query('dvhs',
                                              'roi_coord_string',
                                              "study_instance_uid = '%s' and roi_type like 'PTV%%'"
                                              % uid)

    if ptv_coordinates_strings:

        ptvs = [get_planes_from_string(ptv[0]) for ptv in ptv_coordinates_strings]
        tv_planes = get_union(ptvs)

    for z_plane in list(tv_planes):
        x, y, z = [], [], []
        for polygon in tv_planes[z_plane]:
            initial_polygon_index = len(x)
            for point in polygon:
                x.append(point[0])
                y.append(point[1])
                z.append(point[2])
            x.append(x[initial_polygon_index])
            y.append(y[initial_polygon_index])
            z.append(z[initial_polygon_index])
            x.append(float('nan'))
            y.append(float('nan'))
            z.append(float('nan'))
            tv_data[z_plane] = {'x': x,
                                'y': y,
                                'z': z}


def update_roi_viewer():
    z = roi_viewer_slice_select.value
    source_roi_viewer.data = roi_viewer_data[z]


def update_roi2_viewer():
    z = roi_viewer_slice_select.value
    if z in list(roi2_viewer_data):
        source_roi2_viewer.data = roi2_viewer_data[z]
    else:
        source_roi2_viewer.data = {'x': [], 'y': [], 'z': []}


def update_roi3_viewer():
    z = roi_viewer_slice_select.value
    if z in list(roi3_viewer_data):
        source_roi3_viewer.data = roi3_viewer_data[z]
    else:
        source_roi3_viewer.data = {'x': [], 'y': [], 'z': []}


def update_roi4_viewer():
    z = roi_viewer_slice_select.value
    if z in list(roi4_viewer_data):
        source_roi4_viewer.data = roi4_viewer_data[z]
    else:
        source_roi4_viewer.data = {'x': [], 'y': [], 'z': []}


def update_roi5_viewer():
    z = roi_viewer_slice_select.value
    if z in list(roi5_viewer_data):
        source_roi5_viewer.data = roi5_viewer_data[z]
    else:
        source_roi5_viewer.data = {'x': [], 'y': [], 'z': []}


def roi_viewer_flip_y_axis():
    if roi_viewer.y_range.flipped:
        roi_viewer.y_range.flipped = False
    else:
        roi_viewer.y_range.flipped = True


def roi_viewer_flip_x_axis():
    if roi_viewer.x_range.flipped:
        roi_viewer.x_range.flipped = False
    else:
        roi_viewer.x_range.flipped = True


def roi_viewer_plot_tv():
    update_tv_data()
    z = roi_viewer_slice_select.value
    if z in list(tv_data) and not source_tv.data['x']:
        source_tv.data = tv_data[z]
    else:
        source_tv.data = {'x': [], 'y': [], 'z': []}


def roi_viewer_wheel_event(event):
    if roi_viewer_scrolling.active:
        if event.delta > 0:
            roi_viewer_go_to_next_slice()
        elif event.delta < 0:
            roi_viewer_go_to_previous_slice()


def get_include_map():
    # remove review and stats from source
    group_1_constraint_count, group_2_constraint_count = group_constraint_count()
    if group_1_constraint_count > 0 and group_2_constraint_count > 0:
        extra_rows = 12
    elif group_1_constraint_count > 0 or group_2_constraint_count > 0:
        extra_rows = 6
    else:
        extra_rows = 0
    include = [True] * (len(source.data['uid']) - extra_rows)
    include[0] = False
    include.extend([False] * extra_rows)

    return include


def initialize_rad_bio_source():
    include = get_include_map()

    # Get data from DVH Table
    mrn = [j for i, j in enumerate(source.data['mrn']) if include[i]]
    uid = [j for i, j in enumerate(source.data['uid']) if include[i]]
    group = [j for i, j in enumerate(source.data['group']) if include[i]]
    roi_name = [j for i, j in enumerate(source.data['roi_name']) if include[i]]
    ptv_overlap = [j for i, j in enumerate(source.data['ptv_overlap']) if include[i]]
    roi_type = [j for i, j in enumerate(source.data['roi_type']) if include[i]]
    rx_dose = [j for i, j in enumerate(source.data['rx_dose']) if include[i]]

    # Get data from beam table
    fxs, fx_dose = [], []
    for eud_uid in uid:
        plan_index = source_plans.data['uid'].index(eud_uid)
        fxs.append(source_plans.data['fxs'][plan_index])

        rx_uids, rx_fxs = source_rxs.data['uid'], source_rxs.data['fxs']
        rx_indices = [i for i, rx_uid in enumerate(rx_uids) if rx_uid == eud_uid]
        max_rx_fxs = max([source_rxs.data['fxs'][i] for i in rx_indices])
        rx_index = [i for i, rx_uid in enumerate(rx_uids) if rx_uid == eud_uid and rx_fxs[i] == max_rx_fxs][0]
        fx_dose.append(source_rxs.data['fx_dose'][rx_index])

    source_rad_bio.data = {'mrn': mrn,
                           'uid': uid,
                           'group': group,
                           'roi_name': roi_name,
                           'ptv_overlap': ptv_overlap,
                           'roi_type': roi_type,
                           'rx_dose': rx_dose,
                           'fxs': fxs,
                           'fx_dose': fx_dose,
                           'eud_a': [0] * len(uid),
                           'gamma_50': [0] * len(uid),
                           'td_tcd': [0] * len(uid),
                           'eud': [0] * len(uid),
                           'ntcp_tcp': [0] * len(uid)}


def rad_bio_apply():
    row_count = len(source_rad_bio.data['uid'])

    if rad_bio_apply_filter.active == [0, 1]:
        include = [i for i in range(0, row_count)]
    elif 0 in rad_bio_apply_filter.active:
        include = [i for i in range(0, row_count) if source_rad_bio.data['group'][i] in {'Group 1', 'Group 1 & 2'}]
    elif 1 in rad_bio_apply_filter.active:
        include = [i for i in range(0, row_count) if source_rad_bio.data['group'][i] in {'Group 2', 'Group 1 & 2'}]
    else:
        include = []

    if 2 in rad_bio_apply_filter.active:
        include.extend([i for i in range(0, row_count) if i in source_rad_bio.selected['1d']['indices']])

    try:
        new_eud_a = float(rad_bio_eud_a_input.value)
    except:
        new_eud_a = 1.
    try:
        new_gamma_50 = float(rad_bio_gamma_50_input.value)
    except:
        new_gamma_50 = 1.
    try:
        new_td_tcd = float(rad_bio_td_tcd_input.value)
    except:
        new_td_tcd = 1.

    patch = {'eud_a': [(i, new_eud_a) for i in range(0, row_count) if i in include],
             'gamma_50': [(i, new_gamma_50) for i in range(0, row_count) if i in include],
             'td_tcd': [(i, new_td_tcd) for i in range(0, row_count) if i in include]}

    source_rad_bio.patch(patch)

    update_eud()


def update_eud():
    uid_roi_list = ["%s_%s" % (uid, source.data['roi_name'][i]) for i, uid in enumerate(source.data['uid'])]

    eud, ntcp_tcp = [], []
    for i, uid in enumerate(source_rad_bio.data['uid']):
        uid_roi = "%s_%s" % (uid, source_rad_bio.data['roi_name'][i])
        source_index = uid_roi_list.index(uid_roi)
        dvh = source.data['y'][source_index]
        a = source_rad_bio.data['eud_a'][i]
        try:
            eud.append(round(calc_eud(dvh, a), 2))
        except:
            eud.append(0)
        td_tcd = source_rad_bio.data['td_tcd'][i]
        gamma_50 = source_rad_bio.data['gamma_50'][i]
        if eud[-1] > 0:
            ntcp_tcp.append(1 / (1 + (td_tcd / eud[-1]) ** (4. * gamma_50)))
        else:
            ntcp_tcp.append(0)

    source_rad_bio.patch({'eud': [(i, j) for i, j in enumerate(eud)],
                          'ntcp_tcp': [(i, j) for i, j in enumerate(ntcp_tcp)]})

    update_eud_in_correlation()
    if control_chart_y.value in {'EUD', 'NTCP/TCP'}:
        update_control_chart()


def emami_selection(attr, old, new):
    row_index = source_emami.selected['1d']['indices'][0]
    rad_bio_eud_a_input.value = str(source_emami.data['eud_a'][row_index])
    rad_bio_gamma_50_input.value = str(source_emami.data['gamma_50'][row_index])
    rad_bio_td_tcd_input.value = str(source_emami.data['td_tcd'][row_index])


def update_correlation():

    global correlation_1, correlation_2
    correlation_1, correlation_2 = {}, {}

    # remove review and stats from source
    include = get_include_map()

    # Get data from DVHs table
    for key in correlation_variables:
        src = range_categories[key]['source']
        curr_var = range_categories[key]['var_name']
        table = range_categories[key]['table']
        units = range_categories[key]['units']

        if table in {'DVHs'}:
            uids_dvh_1, mrns_dvh_1, data_dvh_1, uids_dvh_2, mrns_dvh_2, data_dvh_2 = [], [], [], [], [], []
            for i in range(0, len(src.data['uid'])):
                if include[i]:
                    if src.data['group'][i] in {'Group 1', 'Group 1 & 2'}:
                        uids_dvh_1.append(src.data['uid'][i])
                        mrns_dvh_1.append(src.data['mrn'][i])
                        data_dvh_1.append(src.data[curr_var][i])
                    if src.data['group'][i] in {'Group 2', 'Group 1 & 2'}:
                        uids_dvh_2.append(src.data['uid'][i])
                        mrns_dvh_2.append(src.data['mrn'][i])
                        data_dvh_2.append(src.data[curr_var][i])
            correlation_1[key] = {'uid': uids_dvh_1, 'mrn': mrns_dvh_1, 'data': data_dvh_1, 'units': units}
            correlation_2[key] = {'uid': uids_dvh_2, 'mrn': mrns_dvh_2, 'data': data_dvh_2, 'units': units}

    uid_list_1 = correlation_1['ROI Max Dose']['uid']
    uid_list_2 = correlation_2['ROI Max Dose']['uid']

    # Get Data from Plans table
    for key in correlation_variables:
        src = range_categories[key]['source']
        curr_var = range_categories[key]['var_name']
        table = range_categories[key]['table']
        units = range_categories[key]['units']

        if table in {'Plans'}:
            uids_plans_1, mrns_plans_1, data_plans_1 = [], [], []
            for i in range(0, len(uid_list_1)):
                uid = uid_list_1[i]
                uid_index = src.data['uid'].index(uid)
                mrn = src.data['mrn'][uid_index]
                plan_value = src.data[curr_var][uid_index]
                uids_plans_1.append(uid)
                mrns_plans_1.append(mrn)
                data_plans_1.append(plan_value)

            uids_plans_2, mrns_plans_2, data_plans_2 = [], [], []
            for i in range(0, len(uid_list_2)):
                uid = uid_list_2[i]
                uid_index = src.data['uid'].index(uid)
                mrn = src.data['mrn'][uid_index]
                plan_value = src.data[curr_var][uid_index]
                uids_plans_2.append(uid)
                mrns_plans_2.append(mrn)
                data_plans_2.append(plan_value)

            correlation_1[key] = {'uid': uids_plans_1, 'mrn': mrns_plans_1, 'data': data_plans_1, 'units': units}
            correlation_2[key] = {'uid': uids_plans_2, 'mrn': mrns_plans_2, 'data': data_plans_2, 'units': units}

    # Get data from Beams table
    for key in correlation_variables:

        src = range_categories[key]['source']
        curr_var = range_categories[key]['var_name']
        table = range_categories[key]['table']
        units = range_categories[key]['units']
        if table in {'Beams'}:
            beam_data_1 = {'min': [], 'mean': [], 'median': [], 'max': [], 'uid': [], 'mrn': []}
            beam_data_2 = {'min': [], 'mean': [], 'median': [], 'max': [], 'uid': [], 'mrn': []}
            for i in range(0, len(uid_list_1)):
                uid = uid_list_1[i]
                uid_indices = [j for j, x in enumerate(src.data['uid']) if x == uid]
                plan_values = [src.data[curr_var][j] for j in uid_indices]
                mrn = src.data['mrn'][uid_indices[0]]

                beam_data_1['min'].append(np.min(plan_values))
                beam_data_1['mean'].append(np.mean(plan_values))
                beam_data_1['median'].append(np.median(plan_values))
                beam_data_1['max'].append(np.max(plan_values))
                beam_data_1['uid'].append(uid)
                beam_data_1['mrn'].append(mrn)

            for i in range(0, len(uid_list_2)):
                uid = uid_list_2[i]
                uid_indices = [j for j, x in enumerate(src.data['uid']) if x == uid]
                plan_values = [src.data[curr_var][j] for j in uid_indices]
                mrn = src.data['mrn'][uid_indices[0]]

                beam_data_2['min'].append(np.min(plan_values))
                beam_data_2['mean'].append(np.mean(plan_values))
                beam_data_2['median'].append(np.median(plan_values))
                beam_data_2['max'].append(np.max(plan_values))
                beam_data_2['uid'].append(uid)
                beam_data_2['mrn'].append(mrn)

            for stat in ['min', 'mean', 'median', 'max']:
                correlation_1["%s (%s)" % (key, stat.capitalize())] = {'uid': beam_data_1['uid'],
                                                                       'mrn': beam_data_1['mrn'],
                                                                       'data': beam_data_1[stat],
                                                                       'units': units}
                correlation_2["%s (%s)" % (key, stat.capitalize())] = {'uid': beam_data_2['uid'],
                                                                       'mrn': beam_data_2['mrn'],
                                                                       'data': beam_data_2[stat],
                                                                       'units': units}

    categories = list(correlation_1)
    categories.sort()
    corr_chart_x.options = [''] + categories
    corr_chart_y.options = [''] + categories

    validate_correlation()


def update_endpoints_in_correlation():
    global correlation_1, correlation_2

    include = get_include_map()

    # clear out any old DVH endpoint data
    if correlation_1:
        for key in list(correlation_1):
            if key.startswith('ep'):
                correlation_1.pop(key, None)
    if correlation_2:
        for key in list(correlation_2):
            if key.startswith('ep'):
                correlation_2.pop(key, None)

    src = source_endpoint_calcs
    for j in range(0, len(source_endpoint_defs.data['label'])):
        key = source_endpoint_defs.data['label'][j]
        units = source_endpoint_defs.data['units_out'][j]
        ep = "DVH Endpoint: %s" % key

        uids_ep_1, mrns_ep_1, data_ep_1, uids_ep_2, mrns_ep_2, data_ep_2 = [], [], [], [], [], []
        for i in range(0, len(src.data['uid'])):
            if include[i]:
                if src.data['group'][i] in {'Group 1', 'Group 1 & 2'}:
                    uids_ep_1.append(src.data['uid'][i])
                    mrns_ep_1.append(src.data['mrn'][i])
                    data_ep_1.append(src.data[key][i])
                if src.data['group'][i] in {'Group 2', 'Group 1 & 2'}:
                    uids_ep_2.append(src.data['uid'][i])
                    mrns_ep_2.append(src.data['mrn'][i])
                    data_ep_2.append(src.data[key][i])
        correlation_1[ep] = {'uid': uids_ep_1, 'mrn': mrns_ep_1, 'data': data_ep_1, 'units': units}
        correlation_2[ep] = {'uid': uids_ep_2, 'mrn': mrns_ep_2, 'data': data_ep_2, 'units': units}

        if ep not in list(multi_var_reg_vars):
            multi_var_reg_vars[ep] = False

    # declare space to tag variables to be used for multi variable regression
    for key, value in listitems(correlation_1):
        correlation_1[key]['include'] = [False] * len(value['uid'])
    for key, value in listitems(correlation_2):
        correlation_2[key]['include'] = [False] * len(value['uid'])

    categories = list(correlation_1)
    categories.sort()
    corr_chart_x.options = [''] + categories
    corr_chart_y.options = [''] + categories

    update_correlation_matrix()
    update_corr_chart()


def update_eud_in_correlation():
    global correlation_1, correlation_2, multi_var_reg_vars

    # Get data from EUD data
    uid_roi_list = ["%s_%s" % (uid, source.data['roi_name'][i]) for i, uid in enumerate(source.data['uid'])]
    eud_1, eud_2, ntcp_tcp_1, ntcp_tcp_2 = [], [], [], []
    uids_rad_bio_1, mrns_rad_bio_1, uids_rad_bio_2, mrns_rad_bio_2 = [], [], [], []
    for i, uid in enumerate(source_rad_bio.data['uid']):
        uid_roi = "%s_%s" % (uid, source_rad_bio.data['roi_name'][i])
        source_index = uid_roi_list.index(uid_roi)
        group = source.data['group'][source_index]
        if group in {'Group 1', 'Group 1 & 2'}:
            eud_1.append(source_rad_bio.data['eud'][i])
            ntcp_tcp_1.append(source_rad_bio.data['ntcp_tcp'][i])
            uids_rad_bio_1.append(uid)
            mrns_rad_bio_1.append(source.data['mrn'][source_index])
        if group in {'Group 2', 'Group 1 & 2'}:
            eud_2.append(source_rad_bio.data['eud'][i])
            ntcp_tcp_2.append(source_rad_bio.data['ntcp_tcp'][i])
            uids_rad_bio_2.append(uid)
            mrns_rad_bio_2.append(source.data['mrn'][source_index])
    correlation_1['EUD'] = {'uid': uids_rad_bio_1, 'mrn': mrns_rad_bio_1, 'data': eud_1, 'units': 'Gy'}
    correlation_1['NTCP/TCP'] = {'uid': uids_rad_bio_1, 'mrn': mrns_rad_bio_1, 'data': ntcp_tcp_1, 'units': []}
    correlation_2['EUD'] = {'uid': uids_rad_bio_2, 'mrn': mrns_rad_bio_2, 'data': eud_2, 'units': 'Gy'}
    correlation_2['NTCP/TCP'] = {'uid': uids_rad_bio_2, 'mrn': mrns_rad_bio_2, 'data': ntcp_tcp_2, 'units': []}

    # declare space to tag variables to be used for multi variable regression
    for key, value in listitems(correlation_1):
        correlation_1[key]['include'] = [False] * len(value['uid'])
    for key, value in listitems(correlation_2):
        correlation_2[key]['include'] = [False] * len(value['uid'])

    categories = list(correlation_1)
    categories.sort()
    corr_chart_x.options = [''] + categories
    corr_chart_y.options = [''] + categories

    update_correlation_matrix()
    update_corr_chart()


def update_correlation_matrix():
    categories = [key for index, key in enumerate(correlation_names) if index in corr_fig_include.active]

    if 0 in corr_fig_include_2.active:
        if correlation_1:
            categories.extend([x for x in list(correlation_1) if x.startswith("DVH Endpoint")])
        elif correlation_2:
            categories.extend([x for x in list(correlation_2) if x.startswith("DVH Endpoint")])

    if 1 in corr_fig_include_2.active:
        if "EUD" in list(correlation_1) or "EUD" in list(correlation_2):
            categories.append("EUD")

    if 2 in corr_fig_include_2.active:
        if "NTCP/TCP" in list(correlation_1) or "NTCP/TCP" in list(correlation_2):
            categories.append("NTCP/TCP")

    categories.sort()

    categories_count = len(categories)

    categories_for_label = [category.replace("Control Point", "CP") for category in categories]
    categories_for_label = [category.replace("control point", "CP") for category in categories_for_label]
    categories_for_label = [category.replace("Distance", "Dist") for category in categories_for_label]

    for i, category in enumerate(categories_for_label):
        if category.startswith('DVH'):
            categories_for_label[i] = category.split("DVH Endpoint: ")[1]

    corr_fig.x_range.factors = categories_for_label
    corr_fig.y_range.factors = categories_for_label[::-1]
    # 0.5 offset due to Bokeh 0.12.9 bug
    source_corr_matrix_line.data = {'x': [0.5, len(categories) - 0.5], 'y': [len(categories)-0.5, 0.5]}

    s = {'1_pos': {'x': [], 'y': [], 'x_name': [], 'y_name': [], 'color': [],
                   'alpha': [], 'r': [], 'p': [], 'group': [], 'size': [], 'x_normality': [], 'y_normality': []},
         '1_neg': {'x': [], 'y': [], 'x_name': [], 'y_name': [], 'color': [],
                   'alpha': [], 'r': [], 'p': [], 'group': [], 'size': [], 'x_normality': [], 'y_normality': []},
         '2_pos': {'x': [], 'y': [], 'x_name': [], 'y_name': [], 'color': [],
                   'alpha': [], 'r': [], 'p': [], 'group': [], 'size': [], 'x_normality': [], 'y_normality': []},
         '2_neg': {'x': [], 'y': [], 'x_name': [], 'y_name': [], 'color': [],
                   'alpha': [], 'r': [], 'p': [], 'group': [], 'size': [], 'x_normality': [], 'y_normality': []}}

    max_size = 45
    for x in range(0, categories_count):
        for y in range(0, categories_count):
            if x != y:
                data_to_enter = False
                if x > y and correlation_1[categories[0]]['uid']:
                    x_data = correlation_1[categories[x]]['data']
                    y_data = correlation_1[categories[y]]['data']
                    if x_data:
                        r, p_value = pearsonr(x_data, y_data)
                    else:
                        r, p_value = 0, 0
                    if r >= 0:
                        k = '1_pos'
                        s[k]['color'].append(GROUP_1_COLOR)
                        s[k]['group'].append('Group 1')
                    else:
                        k = '1_neg'
                        s[k]['color'].append(GROUP_1_COLOR_NEG_CORR)
                        s[k]['group'].append('Group 1')
                    data_to_enter = True
                elif x < y and correlation_2[categories[0]]['uid']:
                    x_data = correlation_2[categories[x]]['data']
                    y_data = correlation_2[categories[y]]['data']
                    if x_data:
                        r, p_value = pearsonr(x_data, y_data)
                    else:
                        r, p_value = 0, 0
                    if r >= 0:
                        k = '2_pos'
                        s[k]['color'].append(GROUP_2_COLOR)
                        s[k]['group'].append('Group 2')
                    else:
                        k = '2_neg'
                        s[k]['color'].append(GROUP_2_COLOR_NEG_CORR)
                        s[k]['group'].append('Group 2')
                    data_to_enter = True

                if data_to_enter:
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

    source_correlation_1_pos.data = s['1_pos']
    source_correlation_1_neg.data = s['1_neg']
    source_correlation_2_pos.data = s['2_pos']
    source_correlation_2_neg.data = s['2_neg']

    group_1_count, group_2_count = 0, 0
    if correlation_1:
        group_1_count = len(correlation_1[list(correlation_1)[0]]['uid'])
    if correlation_2:
        group_2_count = len(correlation_2[list(correlation_2)[0]]['uid'])

    corr_fig_text_1.text = "Group 1: %d" % group_1_count
    corr_fig_text_2.text = "Group 2: %d" % group_2_count


def update_corr_chart_ticker_x(attr, old, new):
    if multi_var_reg_vars[corr_chart_x.value]:
        corr_chart_x_include.active = [0]
    else:
        corr_chart_x_include.active = []
    update_corr_chart()


def update_corr_chart_ticker_y(attr, old, new):
    update_corr_chart()


def corr_fig_include_ticker(attr, old, new):
    if len(corr_fig_include.active) + len(corr_fig_include_2.active) > 1:
        update_correlation_matrix()


def update_corr_chart():
    if corr_chart_x.value and corr_chart_y.value:
        x_units = correlation_1[corr_chart_x.value]['units']
        y_units = correlation_1[corr_chart_y.value]['units']
        x_1, y_1 = correlation_1[corr_chart_x.value]['data'], correlation_1[corr_chart_y.value]['data']
        x_2, y_2 = correlation_2[corr_chart_x.value]['data'], correlation_2[corr_chart_y.value]['data']
        mrn_1, mrn_2 = correlation_1[corr_chart_x.value]['mrn'], correlation_2[corr_chart_x.value]['mrn']
        if x_units:
            if corr_chart_x.value.startswith('DVH Endpoint'):
                corr_chart.xaxis.axis_label = "%s" % x_units
            else:
                corr_chart.xaxis.axis_label = "%s (%s)" % (corr_chart_x.value, x_units)
        else:
            corr_chart.xaxis.axis_label = corr_chart_x.value.replace('/', ' or ')
        if y_units:
            if corr_chart_y.value.startswith('DVH Endpoint'):
                corr_chart.yaxis.axis_label = "%s" % y_units
            else:
                corr_chart.yaxis.axis_label = "%s (%s)" % (corr_chart_y.value, y_units)
        else:
            corr_chart.yaxis.axis_label = corr_chart_y.value.replace('/', ' or ')
        source_corr_chart_1.data = {'x': x_1, 'y': y_1, 'mrn': mrn_1}
        source_corr_chart_2.data = {'x': x_2, 'y': y_2, 'mrn': mrn_2}

        if x_1:
            slope, intercept, r_value, p_value, std_err = linregress(x_1, y_1)
            group_1_stats = [round(slope, 3),
                             round(intercept, 3),
                             round(r_value ** 2, 3),
                             round(p_value, 3),
                             round(std_err, 3),
                             len(x_1)]
            x_trend = [min(x_1), max(x_1)]
            y_trend = np.add(np.multiply(x_trend, slope), intercept)
            source_corr_trend_1.data = {'x': x_trend, 'y': y_trend}
        else:
            group_1_stats = [''] * 6
            source_corr_trend_1.data = {'x': [], 'y': []}

        if x_2:
            slope, intercept, r_value, p_value, std_err = linregress(x_2, y_2)
            group_2_stats = [round(slope, 3),
                             round(intercept, 3),
                             round(r_value ** 2, 3),
                             round(p_value, 3),
                             round(std_err, 3),
                             len(x_2)]
            x_trend = [min(x_2), max(x_2)]
            y_trend = np.add(np.multiply(x_trend, slope), intercept)
            source_corr_trend_2.data = {'x': x_trend, 'y': y_trend}
        else:
            group_2_stats = [''] * 6
            source_corr_trend_2.data = {'x': [], 'y': []}

        source_corr_chart_stats.data = {'stat': corr_chart_stats_row_names,
                                        'group_1': group_1_stats,
                                        'group_2': group_2_stats}
    else:
        source_corr_chart_stats.data = {'stat': corr_chart_stats_row_names,
                                        'group_1': [''] * 6,
                                        'group_2': [''] * 6}
        source_corr_chart_1.data = {'x': [], 'y': [], 'mrn': []}
        source_corr_chart_2.data = {'x': [], 'y': [], 'mrn': []}
        source_corr_trend_1.data = {'x': [], 'y': []}
        source_corr_trend_2.data = {'x': [], 'y': []}


def corr_chart_x_prev_ticker():
    current_index = corr_chart_x.options.index(corr_chart_x.value)
    corr_chart_x.value = corr_chart_x.options[current_index - 1]


def corr_chart_y_prev_ticker():
    current_index = corr_chart_y.options.index(corr_chart_y.value)
    corr_chart_y.value = corr_chart_y.options[current_index - 1]


def corr_chart_x_next_ticker():
    current_index = corr_chart_x.options.index(corr_chart_x.value)
    if current_index == len(corr_chart_x.options) - 1:
        new_index = 0
    else:
        new_index = current_index + 1
    corr_chart_x.value = corr_chart_x.options[new_index]


def corr_chart_y_next_ticker():
    current_index = corr_chart_y.options.index(corr_chart_y.value)
    if current_index == len(corr_chart_y.options) - 1:
        new_index = 0
    else:
        new_index = current_index + 1
    corr_chart_y.value = corr_chart_y.options[new_index]


def corr_chart_x_include_ticker(attr, old, new):
    if new and not multi_var_reg_vars[corr_chart_x.value]:
        multi_var_reg_vars[corr_chart_x.value] = True
    if not new and multi_var_reg_vars[corr_chart_x.value]:
        multi_var_reg_vars[corr_chart_x.value] = False
    included_vars = [key for key, value in listitems(multi_var_reg_vars) if value]
    included_vars.sort()
    source_multi_var_include.data = {'var_name': included_vars}


def update_control_chart_ticker(attr, old, new):
    update_control_chart()


def update_control_chart_y_ticker(attr, old, new):
    update_control_chart()


def update_control_chart_trend_ticker(attr, old, new):
    control_chart_update_trend()


def update_control_chart_y_axis_label():
    new = str(control_chart_y.value)

    if new:

        # If new has something in parenthesis, extract and put in front
        new_split = new.split(' (')
        if len(new_split) > 1:
            new_display = "%s %s" % (new_split[1].split(')')[0], new_split[0])
        else:
            new_display = new

        if new.startswith('DVH Endpoint'):
            control_chart.yaxis.axis_label = str(control_chart_y.value).split(': ')[1]
        elif new == 'EUD':
            control_chart.yaxis.axis_label = 'EUD (Gy)'
        elif new == 'NTCP/TCP':
            control_chart.yaxis.axis_label = 'NTCP or TCP'
        elif range_categories[new]['units']:
            control_chart.yaxis.axis_label = "%s (%s)" % (new_display, range_categories[new]['units'])
        else:
            control_chart.yaxis.axis_label = new_display


def update_control_chart():
    new = str(control_chart_y.value)
    if new:

        clear_source_selection(source_time_1)
        clear_source_selection(source_time_2)

        if new.startswith('DVH Endpoint: '):
            y_var_name = new.split(': ')[1]
            y_source_values = source_endpoint_calcs.data[y_var_name]
            y_source_uids = source_endpoint_calcs.data['uid']
            y_source_mrns = source_endpoint_calcs.data['mrn']
        elif new == 'EUD':
            y_source_values = source_rad_bio.data['eud']
            y_source_uids = source_rad_bio.data['uid']
            y_source_mrns = source_rad_bio.data['mrn']
        elif new == 'NTCP/TCP':
            y_source_values = source_rad_bio.data['ntcp_tcp']
            y_source_uids = source_rad_bio.data['uid']
            y_source_mrns = source_rad_bio.data['mrn']
        else:
            y_source = range_categories[new]['source']
            y_var_name = range_categories[new]['var_name']
            y_source_values = y_source.data[y_var_name]
            y_source_uids = y_source.data['uid']
            y_source_mrns = y_source.data['mrn']

        update_control_chart_y_axis_label()

        sim_study_dates = source_plans.data['sim_study_date']
        sim_study_dates_uids = source_plans.data['uid']

        x_values = []
        skipped = []
        colors = []
        for v in range(0, len(y_source_values)):
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
                        or range_categories[new]['source'] == source:
                    if new in {'EUD', 'NTCP/TCP'}:
                        roi = source_rad_bio.data['roi_name'][v]
                    else:
                        roi = source.data['roi_name'][v]

                    found = {'Group 1': False, 'Group 2': False}

                    if current_dvh_group_1:
                        r1, r1_max = 0, len(current_dvh_group_1.study_instance_uid)
                        while r1 < r1_max and not found['Group 1']:
                            if current_dvh_group_1.study_instance_uid[r1] == uid and \
                                            current_dvh_group_1.roi_name[r1] == roi:
                                found['Group 1'] = True
                                color = GROUP_1_COLOR
                            r1 += 1

                    if current_dvh_group_2:
                        r2, r2_max = 0, len(current_dvh_group_2.study_instance_uid)
                        while r2 < r2_max and not found['Group 2']:
                            if current_dvh_group_2.study_instance_uid[r2] == uid and \
                                            current_dvh_group_2.roi_name[r2] == roi:
                                found['Group 2'] = True
                                if found['Group 1']:
                                    color = GROUP_1_and_2_COLOR
                                else:
                                    color = GROUP_2_COLOR
                            r2 += 1

                    colors.append(color)
                else:
                    if current_dvh_group_1 and current_dvh_group_2:
                        if uid in current_dvh_group_1.study_instance_uid and uid in current_dvh_group_2.study_instance_uid:
                            colors.append(GROUP_1_and_2_COLOR)
                        elif uid in current_dvh_group_1.study_instance_uid:
                            colors.append(GROUP_1_COLOR)
                        else:
                            colors.append(GROUP_2_COLOR)
                    elif current_dvh_group_1:
                        colors.append(GROUP_1_COLOR)
                    else:
                        colors.append(GROUP_2_COLOR)

        y_values = []
        y_mrns = []
        for v in range(0, len(y_source_values)):
            if not skipped[v]:
                y_values.append(y_source_values[v])
                y_mrns.append(y_source_mrns[v])
                if not isinstance(y_values[-1], (int, long, float)):
                    y_values[-1] = 0

        sort_index = sorted(range(len(x_values)), key=lambda k: x_values[k])
        x_values_sorted, y_values_sorted, y_mrns_sorted, colors_sorted = [], [], [], []
        for s in range(0, len(x_values)):
            x_values_sorted.append(x_values[sort_index[s]])
            y_values_sorted.append(y_values[sort_index[s]])
            y_mrns_sorted.append(y_mrns[sort_index[s]])
            colors_sorted.append(colors[sort_index[s]])

        source_time_1_data = {'x': [], 'y': [], 'mrn': []}
        source_time_2_data = {'x': [], 'y': [], 'mrn': []}
        for i in range(0, len(x_values_sorted)):
            if colors_sorted[i] in {GROUP_1_COLOR, GROUP_1_and_2_COLOR}:
                source_time_1_data['x'].append(x_values_sorted[i])
                source_time_1_data['y'].append(y_values_sorted[i])
                source_time_1_data['mrn'].append(y_mrns_sorted[i])
            if colors_sorted[i] in {GROUP_2_COLOR, GROUP_1_and_2_COLOR}:
                source_time_2_data['x'].append(x_values_sorted[i])
                source_time_2_data['y'].append(y_values_sorted[i])
                source_time_2_data['mrn'].append(y_mrns_sorted[i])

        source_time_1.data = source_time_1_data
        source_time_2.data = source_time_2_data
    else:
        source_time_1.data = {'x': [], 'y': [], 'mrn': []}
        source_time_2.data = {'x': [], 'y': [], 'mrn': []}

    control_chart_update_trend()


def control_chart_update_trend():
    if control_chart_y.value:
        selected_indices_1 = source_time_1.selected['1d']['indices']
        selected_indices_2 = source_time_2.selected['1d']['indices']

        if not selected_indices_1:
            selected_indices_1 = range(0, len(source_time_1.data['x']))
        if not selected_indices_2:
            selected_indices_2 = range(0, len(source_time_2.data['x']))

        group_1 = {'x': [], 'y': []}
        group_2 = {'x': [], 'y': []}
        for i in range(0, len(source_time_1.data['x'])):
            if i in selected_indices_1:
                group_1['x'].append(source_time_1.data['x'][i])
                group_1['y'].append(source_time_1.data['y'][i])
        for i in range(0, len(source_time_2.data['x'])):
            if i in selected_indices_2:
                group_2['x'].append(source_time_2.data['x'][i])
                group_2['y'].append(source_time_2.data['y'][i])

        try:
            avg_len = int(control_chart_text_lookback_distance.value)
        except:
            avg_len = 1

        try:
            percentile = float(control_chart_percentile.value)
        except:
            percentile = 90.

        # average daily data and keep track of points per day, calculate moving average
        if group_1['x']:
            group_1_collapsed = collapse_into_single_dates(group_1['x'], group_1['y'])
            x_trend_1, moving_avgs_1 = moving_avg(group_1_collapsed, avg_len)

            y_np_1 = np.array(group_1['y'])
            upper_bound_1 = float(np.percentile(y_np_1, 50. + percentile / 2.))
            average_1 = float(np.percentile(y_np_1, 50))
            lower_bound_1 = float(np.percentile(y_np_1, 50. - percentile / 2.))
            source_time_trend_1.data = {'x': x_trend_1,
                                        'y': moving_avgs_1,
                                        'mrn': ['Avg'] * len(x_trend_1)}
            source_time_bound_1.data = {'x': group_1['x'],
                                        'mrn': ['Bound'] * len(group_1['x']),
                                        'upper': [upper_bound_1] * len(group_1['x']),
                                        'avg': [average_1] * len(group_1['x']),
                                        'lower': [lower_bound_1] * len(group_1['x'])}
            source_time_patch_1.data = {'x': [group_1['x'][0], group_1['x'][-1], group_1['x'][-1], group_1['x'][0]],
                                        'y': [upper_bound_1, upper_bound_1, lower_bound_1, lower_bound_1]}
        else:
            source_time_trend_1.data = {'x': [], 'y': [], 'mrn': []}
            source_time_bound_1.data = {'x': [], 'mrn': [], 'upper': [], 'avg': [], 'lower': []}
            source_time_patch_1.data = {'x': [], 'y': []}
        if group_2['x']:
            group_2_collapsed = collapse_into_single_dates(group_2['x'], group_2['y'])
            x_trend_2, moving_avgs_2 = moving_avg(group_2_collapsed, avg_len)

            y_np_2 = np.array(group_2['y'])
            upper_bound_2 = float(np.percentile(y_np_2, 50. + percentile / 2.))
            average_2 = float(np.percentile(y_np_2, 50))
            lower_bound_2 = float(np.percentile(y_np_2, 50. - percentile / 2.))
            source_time_trend_2.data = {'x': x_trend_2,
                                        'y': moving_avgs_2,
                                        'mrn': ['Avg'] * len(x_trend_2)}
            source_time_bound_2.data = {'x': group_2['x'],
                                        'mrn': ['Bound'] * len(group_2['x']),
                                        'upper': [upper_bound_2] * len(group_2['x']),
                                        'avg': [average_2] * len(group_2['x']),
                                        'lower': [lower_bound_2] * len(group_2['x'])}
            source_time_patch_2.data = {'x': [group_2['x'][0], group_2['x'][-1],
                                              group_2['x'][-1], group_2['x'][0]],
                                        'y': [upper_bound_2,  upper_bound_2, lower_bound_2, lower_bound_2]}
        else:
            source_time_trend_2.data = {'x': [], 'y': [], 'mrn': []}
            source_time_bound_2.data = {'x': [], 'mrn': [], 'upper': [], 'avg': [], 'lower': []}
            source_time_patch_2.data = {'x': [], 'y': []}

        x_var = str(control_chart_y.value)
        if x_var.startswith('DVH Endpoint'):
            x_var_name = "ep%s" % x_var[-1]
            # histograms.xaxis.axis_label = source_endpoint_names.data[x_var_name][0]
        elif x_var == 'EUD':
            histograms.xaxis.axis_label = "%s (Gy)" % x_var
        elif x_var == 'NTCP/TCP':
            histograms.xaxis.axis_label = "NTCP or TCP"
        else:
            if range_categories[x_var]['units']:
                histograms.xaxis.axis_label = "%s (%s)" % (x_var, range_categories[x_var]['units'])
            else:
                histograms.xaxis.axis_label = x_var

        # Normal Test for Blue Group
        if group_1['y']:
            s1, p1 = normaltest(group_1['y'])
            p1 = "%0.3f" % p1
        else:
            p1 = ''

        # Normal Test for Red Group
        if group_2['y']:
            s2, p2 = normaltest(group_2['y'])
            p2 = "%0.3f" % p2
        else:
            p2 = ''

        # t-Test and Rank Sums
        if group_1['y'] and group_2['y']:
            st, pt = ttest_ind(group_1['y'], group_2['y'])
            sr, pr = ranksums(group_1['y'], group_2['y'])
            pt = "%0.3f" % pt
            pr = "%0.3f" % pr
        else:
            pt = ''
            pr = ''
        histogram_normaltest_1_text.text = "Group 1 Normal Test p-value = %s" % p1
        histogram_normaltest_2_text.text = "Group 2 Normal Test p-value = %s" % p2
        histogram_ttest_text.text = "Two Sample t-Test (Group 1 vs 2) p-value = %s" % pt
        histogram_ranksums_text.text = "Wilcoxon rank-sum (Group 1 vs 2) p-value = %s" % pr

    else:
        source_time_trend_1.data = {'x': [], 'y': [], 'mrn': []}
        source_time_bound_1.data = {'x': [], 'mrn': [], 'upper': [], 'avg': [], 'lower': []}
        source_time_patch_1.data = {'x': [], 'y': []}

        source_time_trend_2.data = {'x': [], 'y': [], 'mrn': []}
        source_time_bound_2.data = {'x': [], 'mrn': [], 'upper': [], 'avg': [], 'lower': []}
        source_time_patch_2.data = {'x': [], 'y': []}

        histogram_normaltest_1_text.text = "Group 1 Normal Test p-value = "
        histogram_normaltest_2_text.text = "Group 2 Normal Test p-value = "
        histogram_ttest_text.text = "Two Sample t-Test (Group 1 vs 2) p-value = "
        histogram_ranksums_text.text = "Wilcoxon rank-sum (Group 1 vs 2) p-value = "

    update_histograms()


def update_histograms():

    if control_chart_y.value != '':
        # Update Histograms
        bin_size = int(histogram_bin_slider.value)
        width_fraction = 0.9

        hist, bins = np.histogram(source_time_1.data['y'], bins=bin_size)
        if histogram_radio_group.active == 1:
            hist = np.divide(hist, np.float(np.max(hist)))
            histograms.yaxis.axis_label = "Relative Frequency"
        else:
            histograms.yaxis.axis_label = "Frequency"
        width = [width_fraction * (bins[1] - bins[0])] * bin_size
        center = (bins[:-1] + bins[1:]) / 2.
        source_histogram_1.data = {'x': center,
                                   'top': hist,
                                   'width': width}

        hist, bins = np.histogram(source_time_2.data['y'], bins=bin_size)
        if histogram_radio_group.active == 1:
            hist = np.divide(hist, np.float(np.max(hist)))
        width = [width_fraction * (bins[1] - bins[0])] * bin_size
        center = (bins[:-1] + bins[1:]) / 2.
        source_histogram_2.data = {'x': center,
                                   'top': hist,
                                   'width': width}
    else:
        source_histogram_1.data = {'x': [], 'top': [], 'width': []}
        source_histogram_2.data = {'x': [], 'top': [], 'width': []}


def histograms_ticker(attr, old, new):
    update_histograms()


def multi_var_linear_regression():
    print(str(datetime.now()), 'Performing multivariable regression', sep=' ')

    included_vars = [key for key in list(correlation_1) if multi_var_reg_vars[key]]
    included_vars.sort()

    # Blue Group
    if current_dvh_group_1:
        x = []
        x_count = len(correlation_1[list(correlation_1)[0]]['data'])
        for i in range(0, x_count):
            current_x = []
            for k in included_vars:
                current_x.append(correlation_1[k]['data'][i])
            x.append(current_x)
        x = sm.add_constant(x)  # explicitly add constant to calculate intercept
        y = correlation_1[corr_chart_y.value]['data']

        fit = sm.OLS(y, x).fit()

        coeff = fit.params
        coeff_p = fit.pvalues
        r_sq = fit.rsquared
        model_p = fit.f_pvalue

        coeff_str = ["%0.3E" % i for i in coeff]
        coeff_p_str = ["%0.3f" % i for i in coeff_p]
        r_sq_str = ["%0.3f" % r_sq]
        model_p_str = ["%0.3f" % model_p]

        source_multi_var_coeff_results_1.data = {'var_name': ['Constant'] + included_vars,
                                                 'coeff': coeff, 'coeff_str': coeff_str,
                                                 'p': coeff_p, 'p_str': coeff_p_str}
        source_multi_var_model_results_1.data = {'model_p': [model_p], 'model_p_str': model_p_str,
                                                 'r_sq': [r_sq], 'r_sq_str': r_sq_str,
                                                 'y_var': [corr_chart_y.value]}
    else:
        source_multi_var_coeff_results_1.data = {'var_name': [], 'coeff': [],
                                                 'coeff_str': [], 'p': [], 'p_str': []}
        source_multi_var_model_results_1.data = {'model_p': [], 'model_p_str': [],
                                                 'r_sq': [], 'r_sq_str': [], 'y_var': []}

    # Red Group
    if current_dvh_group_2:
        x = []
        x_count = len(correlation_2[list(correlation_2)[0]]['data'])
        for i in range(0, x_count):
            current_x = []
            for k in included_vars:
                current_x.append(correlation_2[k]['data'][i])
            x.append(current_x)
        x = sm.add_constant(x)  # explicitly add constant to calculate intercept
        y = correlation_2[corr_chart_y.value]['data']

        fit = sm.OLS(y, x).fit()

        coeff = fit.params
        coeff_p = fit.pvalues
        r_sq = fit.rsquared
        model_p = fit.f_pvalue

        coeff_str = ["%0.3E" % i for i in coeff]
        coeff_p_str = ["%0.3f" % i for i in coeff_p]
        r_sq_str = ["%0.3f" % r_sq]
        model_p_str = ["%0.3f" % model_p]

        source_multi_var_coeff_results_2.data = {'var_name': ['Constant'] + included_vars, 'coeff': coeff, 'coeff_str': coeff_str,
                                                 'p': coeff_p, 'p_str': coeff_p_str}
        source_multi_var_model_results_2.data = {'model_p': [model_p], 'model_p_str': model_p_str,
                                                 'r_sq': [r_sq], 'r_sq_str': r_sq_str,
                                                 'y_var': [corr_chart_y.value]}
    else:
        source_multi_var_coeff_results_2.data = {'var_name': [], 'coeff': [],
                                                 'coeff_str': [], 'p': [], 'p_str': []}
        source_multi_var_model_results_2.data = {'model_p': [], 'model_p_str': [],
                                                 'r_sq': [], 'r_sq_str': [], 'y_var': []}


def multi_var_include_selection(attr, old, new):
    row_index = source_multi_var_include.selected['1d']['indices'][0]
    corr_chart_x.value = source_multi_var_include.data['var_name'][row_index]


def update_source_endpoint_view_selection(attr, old, new):
    if new['1d']['indices']:
        source_endpoint_view.selected = new


def update_dvh_table_selection(attr, old, new):
    if new['1d']['indices']:
        source.selected = new


def update_dvh_review_rois(attr, old, new):
    global temp_dvh_info, dvh_review_rois
    if select_reviewed_mrn.value:
        if new != '':
            dvh_review_rois = temp_dvh_info.get_roi_names(new).values()
            select_reviewed_dvh.options = dvh_review_rois
            select_reviewed_dvh.value = dvh_review_rois[0]
        else:
            select_reviewed_dvh.options = ['']
            select_reviewed_dvh.value = ['']

    else:
        select_reviewed_dvh.options = ['']
        select_reviewed_dvh.value = ''
        patches = {'x': [(0, [])],
                   'y': [(0, [])],
                   'roi_name': [(0, '')],
                   'volume': [(0, '')],
                   'min_dose': [(0, '')],
                   'mean_dose': [(0, '')],
                   'max_dose': [(0, '')],
                   'mrn': [(0, '')],
                   'rx_dose': [(0, '')]}
        source.patch(patches)


def calculate_review_dvh():
    global temp_dvh_info, dvh_review_rois, x, y

    patches = {'x': [(0, [])],
               'y': [(0, [])],
               'roi_name': [(0, '')],
               'volume': [(0, 1)],
               'min_dose': [(0, '')],
               'mean_dose': [(0, '')],
               'max_dose': [(0, '')],
               'mrn': [(0, '')],
               'rx_dose': [(0, 1)]}

    try:
        if not source.data['x']:
            update_data()

        else:
            file_index = temp_dvh_info.mrn.index(select_reviewed_mrn.value)
            roi_index = dvh_review_rois.index(select_reviewed_dvh.value)
            structure_file = temp_dvh_info.structure[file_index]
            plan_file = temp_dvh_info.plan[file_index]
            dose_file = temp_dvh_info.dose[file_index]
            key = list(temp_dvh_info.get_roi_names(select_reviewed_mrn.value))[roi_index]

            rt_st = dicomparser.DicomParser(structure_file)
            rt_structures = rt_st.GetStructures()
            review_dvh = dvhcalc.get_dvh(structure_file, dose_file, key)
            dicompyler_plan = dicomparser.DicomParser(plan_file).GetPlan()

            roi_name = rt_structures[key]['name']
            volume = review_dvh.volume
            min_dose = review_dvh.min
            mean_dose = review_dvh.mean
            max_dose = review_dvh.max
            if not review_rx.value:
                rx_dose = float(dicompyler_plan['rxdose']) / 100.
                review_rx.value = str(round(rx_dose, 2))
            else:
                rx_dose = round(float(review_rx.value), 2)

            x = review_dvh.bincenters
            if max(review_dvh.counts):
                y = np.divide(review_dvh.counts, max(review_dvh.counts))
            else:
                y = review_dvh.counts

            if radio_group_dose.active == 1:
                f = 5000
                bin_count = len(x)
                new_bin_count = int(bin_count * f / (rx_dose * 100.))

                x1 = np.linspace(0, bin_count, bin_count)
                x2 = np.multiply(np.linspace(0, new_bin_count, new_bin_count), rx_dose * 100. / f)
                y = np.interp(x2, x1, review_dvh.counts)
                y = np.divide(y, np.max(y))
                x = np.divide(np.linspace(0, new_bin_count, new_bin_count), f)

            if radio_group_volume.active == 0:
                y = np.multiply(y, volume)

            patches = {'x': [(0, x)],
                       'y': [(0, y)],
                       'roi_name': [(0, roi_name)],
                       'volume': [(0, volume)],
                       'min_dose': [(0, min_dose)],
                       'mean_dose': [(0, mean_dose)],
                       'max_dose': [(0, max_dose)],
                       'mrn': [(0, select_reviewed_mrn.value)],
                       'rx_dose': [(0, rx_dose)]}

    except:
        pass

    source.patch(patches)


def select_reviewed_dvh_ticker(attr, old, new):
    calculate_review_dvh()


def review_rx_ticker(attr, old, new):
    if radio_group_dose.active == 0:
        source.patch({'rx_dose': [(0, round(float(review_rx.value), 2))]})
    else:
        calculate_review_dvh()


# Ticker function for abs/rel dose radio buttons
# any change will call update_data, if any source data has been retrieved from SQL
def radio_group_dose_ticker(attr, old, new):
    if source.data['x'] != '':
        update_data()
        calculate_review_dvh()


# Ticker function for abs/rel volume radio buttons
# any change will call update_data, if any source data has been retrieved from SQL
def radio_group_volume_ticker(attr, old, new):
    if source.data['x'] != '':
        update_data()
        calculate_review_dvh()


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


def validate_correlation():
    global correlation_1, correlation_2

    if correlation_1:
        bad_data = []
        for range_var in list(correlation_1):
            for i, j in enumerate(correlation_1[range_var]['data']):
                if j == 'None':
                    bad_data.append(i)
                    print("%s[%s] is non-numerical, will remove all data from correlation for this patient"
                          % (range_var, i))
        bad_data = list(set(bad_data))
        bad_data.sort()

        new_correlation_1 = {}
        for range_var in list(correlation_1):
            new_correlation_1[range_var] = {'mrn': [],
                                            'uid': [],
                                            'data': [],
                                            'units': correlation_1[range_var]['units']}
            for i in range(0, len(correlation_1[range_var]['data'])):
                if i not in bad_data:
                    for j in {'mrn', 'uid', 'data'}:
                        new_correlation_1[range_var][j].append(correlation_1[range_var][j][i])

        correlation_1 = new_correlation_1

    if correlation_2:
        bad_data = []
        for range_var in list(correlation_2):
            for i, j in enumerate(correlation_2[range_var]['data']):
                if j == 'None':
                    bad_data.append(i)
                    print("%s[%s] is non-numerical, will remove all data from correlation for this patient"
                          % (range_var, i))
        bad_data = list(set(bad_data))
        bad_data.sort()

        new_correlation_2 = {}
        for range_var in list(correlation_1):
            new_correlation_2[range_var] = {'mrn': [],
                                            'uid': [],
                                            'data': [],
                                            'units': correlation_2[range_var]['units']}
            for i in range(0, len(correlation_2[range_var]['data'])):
                if i not in bad_data:
                    for j in {'mrn', 'uid', 'data'}:
                        new_correlation_2[range_var][j].append(correlation_2[range_var][j][i])

        correlation_2 = new_correlation_2


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Selection Filter UI objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
category_options = list(selector_categories)
category_options.sort()

div_selector = Div(text="<b>Query by Categorical Data</b>", width=1000)
div_selector_end = Div(text="<hr>", width=1050)

# Add Current row to source
add_selector_row_button = Button(label="Add Selection Filter", button_type="primary", width=200)
add_selector_row_button.on_click(add_selector_row)

# Row
selector_row = Select(value='1', options=['1'], width=50, title="Row")
selector_row.on_change('value', selector_row_ticker)

# Category 1
select_category1 = Select(value="ROI Institutional Category", options=category_options, width=300, title="Category 1")
select_category1.on_change('value', select_category1_ticker)

# Category 2
cat_2_sql_table = selector_categories[select_category1.value]['table']
cat_2_var_name = selector_categories[select_category1.value]['var_name']
category2_values = DVH_SQL().get_unique_values(cat_2_sql_table, cat_2_var_name)
select_category2 = Select(value=category2_values[0], options=category2_values, width=300, title="Category 2")
select_category2.on_change('value', select_category2_ticker)

# Misc
delete_selector_row_button = Button(label="Delete", button_type="warning", width=100)
delete_selector_row_button.on_click(delete_selector_row)
group_selector = CheckboxButtonGroup(labels=["Group 1", "Group 2"], active=[0], width=180)
group_selector.on_change('active', ensure_selector_group_is_assigned)
selector_not_operator_checkbox = CheckboxGroup(labels=['Not'], active=[])
selector_not_operator_checkbox.on_change('active', selector_not_operator_ticker)

# Selector Category table
columns = [TableColumn(field="row", title="Row", width=60),
           TableColumn(field="category1", title="Selection Category 1", width=280),
           TableColumn(field="category2", title="Selection Category 2", width=280),
           TableColumn(field="group_label", title="Group", width=170),
           TableColumn(field="not_status", title="Apply Not Operator", width=150)]
selection_filter_data_table = DataTable(source=source_selectors,
                                        columns=columns, width=1000, height=150, row_headers=False)
source_selectors.on_change('selected', update_selector_row_on_selection)
update_selector_source()

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Range Filter UI objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
category_options = list(range_categories)
category_options.sort()

div_range = Div(text="<b>Query by Numerical Data</b>", width=1000)

# Add Current row to source
add_range_row_button = Button(label="Add Range Filter", button_type="primary", width=200)
add_range_row_button.on_click(add_range_row)

# Row
range_row = Select(value='', options=[''], width=50, title="Row")
range_row.on_change('value', range_row_ticker)

# Category
select_category = Select(value=SELECT_CATEGORY_DEFAULT, options=category_options, width=240, title="Category")
select_category.on_change('value', select_category_ticker)

# Min and max
text_min = TextInput(value='', title='Min: ', width=180)
text_min.on_change('value', min_text_ticker)
text_max = TextInput(value='', title='Max: ', width=180)
text_max.on_change('value', max_text_ticker)

# Misc
delete_range_row_button = Button(label="Delete", button_type="warning", width=100)
delete_range_row_button.on_click(delete_range_row)
group_range = CheckboxButtonGroup(labels=["Group 1", "Group 2"], active=[0], width=180)
group_range.on_change('active', ensure_range_group_is_assigned)
range_not_operator_checkbox = CheckboxGroup(labels=['Not'], active=[])
range_not_operator_checkbox.on_change('active', range_not_operator_ticker)

# Selector Category table
columns = [TableColumn(field="row", title="Row", width=60),
           TableColumn(field="category", title="Range Category", width=230),
           TableColumn(field="min_display", title="Min", width=170),
           TableColumn(field="max_display", title="Max", width=170),
           TableColumn(field="group_label", title="Group", width=180),
           TableColumn(field="not_status", title="Apply Not Operator", width=150)]
range_filter_data_table = DataTable(source=source_ranges,
                                    columns=columns, width=1000, height=150, row_headers=False)
source_ranges.on_change('selected', update_range_row_on_selection)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# DVH Endpoint Filter UI objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
div_endpoint = Div(text="<b>Define Endpoints</b>", width=1000)

# Add Current row to source
add_endpoint_row_button = Button(label="Add Endpoint", button_type="primary", width=200)
add_endpoint_row_button.on_click(add_endpoint)

ep_row = Select(value='', options=[''], width=50, title="Row")
ep_options = ["Dose (Gy)", "Dose (%)", "Volume (cc)", "Volume (%)"]
select_ep_type = Select(value=ep_options[0], options=ep_options, width=180, title="Output")
select_ep_type.on_change('value', select_ep_type_ticker)
ep_text_input = TextInput(value='', title="Input Volume (cc):", width=180)
ep_text_input.on_change('value', ep_text_input_ticker)
ep_units_in = RadioButtonGroup(labels=["cc", "%"], active=0, width=100)
ep_units_in.on_change('active', ep_units_in_ticker)
delete_ep_row_button = Button(label="Delete", button_type="warning", width=100)
delete_ep_row_button.on_click(delete_ep_row)
div_endpoint_start = Div(text="<hr>", width=1050)

# endpoint  table
columns = [TableColumn(field="row", title="Row", width=60),
           TableColumn(field="label", title="Endpoint", width=180),
           TableColumn(field="units_out", title="Units", width=60)]
ep_data_table = DataTable(source=source_endpoint_defs, columns=columns, width=300, height=150, row_headers=False)

source_endpoint_defs.on_change('selected', update_ep_row_on_selection)

query_button = Button(label="Query", button_type="success", width=100)
query_button.on_click(update_data)

# define Download button and call download.js on click
menu = [("All Data", "all"), ("Lite", "lite"), ("Only DVHs", "dvhs"), ("Anonymized DVHs", "anon_dvhs")]
download_dropdown = Dropdown(label="Download", button_type="default", menu=menu, width=100)
download_dropdown.callback = CustomJS(args=dict(source=source,
                                                source_rxs=source_rxs,
                                                source_plans=source_plans,
                                                source_beams=source_beams),
                                      code=open(join(dirname(__file__), "download.js")).read())


def custom_title_blue_ticker(attr, old, new):
    custom_title_query_blue.value = new
    custom_title_dvhs_blue.value = new
    custom_title_rad_bio_blue.value = new
    custom_title_roi_viewer_blue.value = new
    custom_title_planning_blue.value = new
    custom_title_time_series_blue.value = new
    custom_title_correlation_blue.value = new
    custom_title_regression_blue.value = new


def custom_title_red_ticker(attr, old, new):
    custom_title_query_red.value = new
    custom_title_dvhs_red.value = new
    custom_title_rad_bio_red.value = new
    custom_title_roi_viewer_red.value = new
    custom_title_planning_red.value = new
    custom_title_time_series_red.value = new
    custom_title_correlation_red.value = new
    custom_title_regression_red.value = new


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Set up Layout
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
min_border = 75
tools = "pan,wheel_zoom,box_zoom,reset,crosshair,save"
dvh_plots = figure(plot_width=1050, plot_height=500, tools=tools, logo=None, active_drag="box_zoom")
dvh_plots.min_border_left = min_border
dvh_plots.min_border_bottom = min_border
dvh_plots.add_tools(HoverTool(show_arrow=False, line_policy='next',
                              tooltips=[('Label', '@mrn @roi_name'),
                                        ('Dose', '$x'),
                                        ('Volume', '$y')]))
dvh_plots.xaxis.axis_label_text_font_size = PLOT_AXIS_LABEL_FONT_SIZE
dvh_plots.yaxis.axis_label_text_font_size = PLOT_AXIS_LABEL_FONT_SIZE
dvh_plots.xaxis.major_label_text_font_size = PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
dvh_plots.yaxis.major_label_text_font_size = PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
dvh_plots.yaxis.axis_label_text_baseline = "bottom"
dvh_plots.lod_factor = LOD_FACTOR  # level of detail during interactive plot events

# Add statistical plots to figure
stats_median_1 = dvh_plots.line('x', 'median', source=source_stats_1,
                                line_width=STATS_1_MEDIAN_LINE_WIDTH, color=GROUP_1_COLOR,
                                line_dash=STATS_1_MEDIAN_LINE_DASH, alpha=STATS_1_MEDIAN_ALPHA)
stats_mean_1 = dvh_plots.line('x', 'mean', source=source_stats_1,
                              line_width=STATS_1_MEAN_LINE_WIDTH, color=GROUP_1_COLOR,
                              line_dash=STATS_1_MEAN_LINE_DASH, alpha=STATS_1_MEAN_ALPHA)
stats_median_2 = dvh_plots.line('x', 'median', source=source_stats_2,
                                line_width=STATS_2_MEDIAN_LINE_WIDTH, color=GROUP_2_COLOR,
                                line_dash=STATS_2_MEDIAN_LINE_DASH, alpha=STATS_2_MEDIAN_ALPHA)
stats_mean_2 = dvh_plots.line('x', 'mean', source=source_stats_2,
                              line_width=STATS_2_MEAN_LINE_WIDTH, color=GROUP_2_COLOR,
                              line_dash=STATS_2_MEAN_LINE_DASH, alpha=STATS_2_MEAN_ALPHA)

# Add all DVHs, but hide them until selected
dvh_plots.multi_line('x', 'y', source=source,
                     selection_color='color', line_width=DVH_LINE_WIDTH, alpha=0,
                     nonselection_alpha=0, selection_alpha=1)

# Shaded region between Q1 and Q3
iqr_1 = dvh_plots.patch('x_patch', 'y_patch', source=source_patch_1, alpha=IQR_1_ALPHA, color=GROUP_1_COLOR)
iqr_2 = dvh_plots.patch('x_patch', 'y_patch', source=source_patch_2, alpha=IQR_2_ALPHA, color=GROUP_2_COLOR)

# Set x and y axis labels
dvh_plots.xaxis.axis_label = "Dose (Gy)"
dvh_plots.yaxis.axis_label = "Normalized Volume"

# Set the legend (for stat dvhs only)
legend_stats = Legend(items=[("Median", [stats_median_1]),
                             ("Mean", [stats_mean_1]),
                             ("IQR", [iqr_1]),
                             ("Median", [stats_median_2]),
                             ("Mean", [stats_mean_2]),
                             ("IQR", [iqr_2])],
                      location=(25, 0))

# Add the layout outside the plot, clicking legend item hides the line
dvh_plots.add_layout(legend_stats, 'right')
dvh_plots.legend.click_policy = "hide"

# Set up DataTable for dvhs
data_table_title = Div(text="<b>DVHs</b>", width=1200)
columns = [TableColumn(field="mrn", title="MRN / Stat", width=175),
           TableColumn(field="group", title="Group", width=175),
           TableColumn(field="roi_name", title="ROI Name"),
           TableColumn(field="roi_type", title="ROI Type", width=80),
           TableColumn(field="rx_dose", title="Rx Dose", width=100, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="volume", title="Volume", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="min_dose", title="Min Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="mean_dose", title="Mean Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="max_dose", title="Max Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="dist_to_ptv_min", title="Dist to PTV", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="ptv_overlap", title="PTV Overlap", width=80, formatter=NumberFormatter(format="0.0"))]
data_table = DataTable(source=source, columns=columns, width=1200, editable=True)
source.on_change('selected', update_source_endpoint_view_selection)

# Set up EndPoint DataTable
endpoint_table_title = Div(text="<b>DVH Endpoints</b>", width=1200)
columns = [TableColumn(field="mrn", title="MRN / Stat", width=175),
           TableColumn(field="group", title="Group", width=175),
           TableColumn(field="roi_name", title="ROI Name"),
           TableColumn(field="ep1", title="ep1", width=100, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="ep2", title="ep2", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="ep3", title="ep3", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="ep4", title="ep4", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="ep5", title="ep5", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="ep6", title="ep6", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="ep7", title="ep7", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="ep8", title="ep8", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="ep9", title="ep9", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="ep10", title="ep10", width=80, formatter=NumberFormatter(format="0.00"))]
data_table_endpoints = DataTable(source=source_endpoint_view, columns=columns, width=1200, editable=True)
source_endpoint_view.on_change('selected', update_dvh_table_selection)

# Set up Beams DataTable
beam_table_title = Div(text="<b>Beams</b>", width=1500)
columns = [TableColumn(field="mrn", title="MRN", width=105),
           TableColumn(field="group", title="Group", width=230),
           TableColumn(field="beam_number", title="Beam", width=50),
           TableColumn(field="fx_count", title="Fxs", width=50),
           TableColumn(field="fx_grp_beam_count", title="Beams", width=50),
           TableColumn(field="fx_grp_number", title="Rx Grp", width=60),
           TableColumn(field="beam_name", title="Name", width=150),
           TableColumn(field="beam_dose", title="Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="beam_energy_min", title="Energy Min", width=80),
           TableColumn(field="beam_energy_max", title="Energy Max", width=80),
           TableColumn(field="beam_mu", title="MU", width=100, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="beam_mu_per_deg", title="MU/deg", width=100, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="beam_mu_per_cp", title="MU/CP", width=100, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="beam_type", title="Type", width=100),
           TableColumn(field="scan_mode", title="Scan Mode", width=100),
           TableColumn(field="scan_spot_count", title="Scan Spots", width=100),
           TableColumn(field="control_point_count", title="CPs", width=80),
           TableColumn(field="radiation_type", title="Rad. Type", width=80),
           TableColumn(field="ssd", title="SSD", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="treatment_machine", title="Tx Machine", width=80)]
data_table_beams = DataTable(source=source_beams, columns=columns, width=1300, editable=True)
beam_table_title2 = Div(text="<b>Beams Continued</b>", width=1500)
columns = [TableColumn(field="mrn", title="MRN", width=105),
           TableColumn(field="group", title="Group", width=230),
           TableColumn(field="beam_name", title="Name", width=150),
           TableColumn(field="gantry_start", title="Gan Start", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="gantry_end", title="End", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="gantry_rot_dir", title="Rot Dir", width=80),
           TableColumn(field="gantry_range", title="Range", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="gantry_min", title="Min", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="gantry_max", title="Max", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="collimator_start", title="Col Start", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="collimator_end", title="End", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="collimator_rot_dir", title="Rot Dir", width=80),
           TableColumn(field="collimator_range", title="Range", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="collimator_min", title="Min", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="collimator_max", title="Max", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="couch_start", title="Couch Start", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="couch_end", title="End", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="couch_rot_dir", title="Rot Dir", width=80),
           TableColumn(field="couch_range", title="Range", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="couch_min", title="Min", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="couch_max", title="Max", width=80, formatter=NumberFormatter(format="0.0"))]
data_table_beams2 = DataTable(source=source_beams, columns=columns, width=1300, editable=True)

# Set up Plans DataTable
plans_table_title = Div(text="<b>Plans</b>", width=1200)
columns = [TableColumn(field="mrn", title="MRN", width=420),
           TableColumn(field="group", title="Group", width=230),
           TableColumn(field="age", title="Age", width=80),
           TableColumn(field="birth_date", title="Birth Date"),
           TableColumn(field="dose_grid_res", title="Dose Grid Res"),
           TableColumn(field="heterogeneity_correction", title="Heterogeneity"),
           TableColumn(field="fxs", title="Fxs", width=80),
           TableColumn(field="patient_orientation", title="Orientation"),
           TableColumn(field="patient_sex", title="Sex", width=80),
           TableColumn(field="physician", title="Rad Onc"),
           TableColumn(field="rx_dose", title="Rx Dose", formatter=NumberFormatter(format="0.00")),
           TableColumn(field="sim_study_date", title="Sim Study Date"),
           TableColumn(field="total_mu", title="Total MU", formatter=NumberFormatter(format="0.0")),
           TableColumn(field="tx_modality", title="Tx Modality"),
           TableColumn(field="tx_site", title="Tx Site"),
           TableColumn(field="baseline", title="Baseline")]
data_table_plans = DataTable(source=source_plans, columns=columns, width=1300, editable=True)

# Set up Rxs DataTable
rxs_table_title = Div(text="<b>Rxs</b>", width=1000)
columns = [TableColumn(field="mrn", title="MRN"),
           TableColumn(field="group", title="Group", width=230),
           TableColumn(field="plan_name", title="Plan Name"),
           TableColumn(field="fx_dose", title="Fx Dose", formatter=NumberFormatter(format="0.00")),
           TableColumn(field="rx_percent", title="Rx Isodose", formatter=NumberFormatter(format="0.0")),
           TableColumn(field="fxs", title="Fxs", width=80),
           TableColumn(field="rx_dose", title="Rx Dose", formatter=NumberFormatter(format="0.00")),
           TableColumn(field="fx_grp_number", title="Fx Grp"),
           TableColumn(field="fx_grp_count", title="Fx Groups"),
           TableColumn(field="fx_grp_name", title="Fx Grp Name"),
           TableColumn(field="normalization_method", title="Norm Method"),
           TableColumn(field="normalization_object", title="Norm Object")]
data_table_rxs = DataTable(source=source_rxs, columns=columns, width=1300, editable=True)


# Control Chart layout
tools = "pan,wheel_zoom,box_zoom,lasso_select,poly_select,reset,crosshair,save"
control_chart = figure(plot_width=1050, plot_height=400, tools=tools, logo=None,
                       active_drag="box_zoom", x_axis_type='datetime')
control_chart.xaxis.axis_label_text_font_size = PLOT_AXIS_LABEL_FONT_SIZE
control_chart.yaxis.axis_label_text_font_size = PLOT_AXIS_LABEL_FONT_SIZE
control_chart.xaxis.major_label_text_font_size = PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
control_chart.yaxis.major_label_text_font_size = PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
# control_chart.min_border_left = min_border
control_chart.min_border_bottom = min_border
control_chart_data_1 = control_chart.circle('x', 'y', size=TIME_SERIES_1_CIRCLE_SIZE, color=GROUP_1_COLOR,
                                            alpha=TIME_SERIES_1_CIRCLE_ALPHA, source=source_time_1)
control_chart_data_2 = control_chart.circle('x', 'y', size=TIME_SERIES_2_CIRCLE_SIZE, color=GROUP_2_COLOR,
                                            alpha=TIME_SERIES_2_CIRCLE_ALPHA, source=source_time_2)
control_chart_trend_1 = control_chart.line('x', 'y', color=GROUP_1_COLOR, source=source_time_trend_1,
                                           line_width=TIME_SERIES_1_TREND_LINE_WIDTH,
                                           line_dash=TIME_SERIES_1_TREND_LINE_DASH)
control_chart_trend_2 = control_chart.line('x', 'y', color=GROUP_2_COLOR, source=source_time_trend_2,
                                           line_width=TIME_SERIES_2_TREND_LINE_WIDTH,
                                           line_dash=TIME_SERIES_2_TREND_LINE_DASH)
control_chart_avg_1 = control_chart.line('x', 'avg', color=GROUP_1_COLOR, source=source_time_bound_1,
                                         line_width=TIME_SERIES_1_AVG_LINE_WIDTH,
                                         line_dash=TIME_SERIES_1_AVG_LINE_DASH)
control_chart_avg_2 = control_chart.line('x', 'avg', color=GROUP_2_COLOR, source=source_time_bound_2,
                                         line_width=TIME_SERIES_2_AVG_LINE_WIDTH,
                                         line_dash=TIME_SERIES_2_AVG_LINE_DASH)
control_chart_patch_1 = control_chart.patch('x', 'y', color=GROUP_1_COLOR, source=source_time_patch_1,
                                            alpha=TIME_SERIES_1_PATCH_ALPHA)
control_chart_patch_2 = control_chart.patch('x', 'y', color=GROUP_2_COLOR, source=source_time_patch_2,
                                            alpha=TIME_SERIES_1_PATCH_ALPHA)
control_chart.add_tools(HoverTool(show_arrow=True,
                                  tooltips=[('ID', '@mrn'),
                                            ('Date', '@x{%F}'),
                                            ('Value', '@y{0.2f}')],
                                  formatters={'x': 'datetime'}))
control_chart.xaxis.axis_label = "Simulation Date"
control_chart.yaxis.axis_label = ""
# Set the legend
legend_control_chart = Legend(items=[("Group 1", [control_chart_data_1]),
                                     ("Series Average", [control_chart_avg_1]),
                                     ("Rolling Average", [control_chart_trend_1]),
                                     ("Percentile Region", [control_chart_patch_1]),
                                     ("Group 2", [control_chart_data_2]),
                                     ("Series Average", [control_chart_avg_2]),
                                     ("Rolling Average", [control_chart_trend_2]),
                                     ("Percentile Region", [control_chart_patch_2]),],
                              location=(25, 0))

# Add the layout outside the plot, clicking legend item hides the line
control_chart.add_layout(legend_control_chart, 'right')
control_chart.legend.click_policy = "hide"

control_chart_options = list(range_categories)
control_chart_options.sort()
control_chart_options.insert(0, '')
control_chart_y = Select(value=control_chart_options[0], options=control_chart_options, width=300)
control_chart_y.title = "Select a Range Variable"
control_chart_y.on_change('value', update_control_chart_y_ticker)

control_chart_text_lookback_distance = TextInput(value='1', title="Lookback Distance", width=200)
control_chart_text_lookback_distance.on_change('value', update_control_chart_trend_ticker)

control_chart_percentile = TextInput(value='90', title="Percentile", width=200)
control_chart_percentile.on_change('value', update_control_chart_trend_ticker)

lookback_units_options = ['Dates with a Sim', 'Days', 'Patients']
control_chart_lookback_units = Select(value=lookback_units_options[0], options=lookback_units_options, width=200)
control_chart_lookback_units.title = 'Lookback Units'
control_chart_lookback_units.on_change('value', update_control_chart_ticker)

# source_time.on_change('selected', control_chart_update_trend)
trend_update_button = Button(label="Update Trend", button_type="primary", width=150)
trend_update_button.on_click(control_chart_update_trend)

div_horizontal_bar = Div(text="<hr>", width=1050)

# histograms
tools = "pan,wheel_zoom,box_zoom,reset,crosshair,save"
histograms = figure(plot_width=1050, plot_height=400, tools=tools, logo=None, active_drag="box_zoom")
histograms.xaxis.axis_label_text_font_size = PLOT_AXIS_LABEL_FONT_SIZE
histograms.yaxis.axis_label_text_font_size = PLOT_AXIS_LABEL_FONT_SIZE
histograms.xaxis.major_label_text_font_size = PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
histograms.yaxis.major_label_text_font_size = PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
histograms.min_border_left = min_border
histograms.min_border_bottom = min_border
hist_1 = histograms.vbar(x='x', width='width', bottom=0, top='top', source=source_histogram_1,
                         color=GROUP_1_COLOR, alpha=HISTOGRAM_1_ALPHA)
hist_2 = histograms.vbar(x='x', width='width', bottom=0, top='top', source=source_histogram_2,
                         color=GROUP_2_COLOR, alpha=HISTOGRAM_2_ALPHA)
histograms.xaxis.axis_label = ""
histograms.yaxis.axis_label = "Frequency"
histogram_bin_slider = Slider(start=1, end=100, value=10, step=1, title="Number of Bins")
histogram_bin_slider.on_change('value', histograms_ticker)
histogram_radio_group = RadioGroup(labels=["Absolute Y-Axis", "Relative Y-Axis (to Group Max)"], active=0)
histogram_radio_group.on_change('active', histograms_ticker)
histogram_normaltest_1_text = Div(text="Group 1 Normal Test p-value = ", width=400)
histogram_normaltest_2_text = Div(text="Group 2 Normal Test p-value = ", width=400)
histogram_ttest_text = Div(text="Two Sample t-Test (Group 1 vs 2) p-value = ", width=400)
histogram_ranksums_text = Div(text="Wilcoxon rank-sum (Group 1 vs 2) p-value = ", width=400)
histograms.add_tools(HoverTool(show_arrow=True,
                               line_policy='next',
                               tooltips=[('x', '@x{0.2f}'),
                                         ('Counts', '@top')]))
# Set the legend
legend_hist = Legend(items=[("Group 1", [hist_1]),
                            ("Group 2", [hist_2])],
                     location=(25, 0))

# Add the layout outside the plot, clicking legend item hides the line
histograms.add_layout(legend_hist, 'right')
histograms.legend.click_policy = "hide"

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Correlation
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Plot
corr_fig = figure(plot_width=900, plot_height=700,
                  x_axis_location="above",
                  tools="pan, box_zoom, wheel_zoom, reset",
                  logo=None,
                  x_range=[''], y_range=[''])
corr_fig.xaxis.axis_label_text_font_size = PLOT_AXIS_LABEL_FONT_SIZE
corr_fig.yaxis.axis_label_text_font_size = PLOT_AXIS_LABEL_FONT_SIZE
corr_fig.xaxis.major_label_text_font_size = PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
corr_fig.yaxis.major_label_text_font_size = PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
corr_fig.min_border_left = 175
corr_fig.min_border_top = 130
corr_fig.xaxis.major_label_orientation = pi / 4
corr_fig.toolbar.active_scroll = "auto"
corr_fig.title.align = 'center'
corr_fig.title.text_font_style = "italic"
corr_fig.xaxis.axis_line_color = None
corr_fig.xaxis.major_tick_line_color = None
corr_fig.xaxis.minor_tick_line_color = None
corr_fig.xgrid.grid_line_color = None
corr_fig.ygrid.grid_line_color = None
corr_fig.yaxis.axis_line_color = None
corr_fig.yaxis.major_tick_line_color = None
corr_fig.yaxis.minor_tick_line_color = None
corr_fig.outline_line_color = None
corr_1_pos = corr_fig.circle(x='x', y='y', color='color', alpha='alpha', size='size', source=source_correlation_1_pos)
corr_1_neg = corr_fig.circle(x='x', y='y', color='color', alpha='alpha', size='size', source=source_correlation_1_neg)
corr_2_pos = corr_fig.circle(x='x', y='y', color='color', alpha='alpha', size='size', source=source_correlation_2_pos)
corr_2_neg = corr_fig.circle(x='x', y='y', color='color', alpha='alpha', size='size', source=source_correlation_2_neg)
corr_fig.add_tools(HoverTool(show_arrow=True,
                             line_policy='next',
                             tooltips=[('Group', '@group'),
                                       ('x', '@x_name'),
                                       ('y', '@y_name'),
                                       ('r', '@r'),
                                       ('p', '@p'),
                                       ('Norm p-value x', '@x_normality{0.4f}'),
                                       ('Norm p-value y', '@y_normality{0.4f}')],))
corr_fig.line(x='x', y='y', source=source_corr_matrix_line,
              line_width=3, line_dash='dotted', color='black', alpha=0.8)
# Set the legend
legend_corr = Legend(items=[("+r Group 1", [corr_1_pos]),
                            ("-r Group 1", [corr_1_neg]),
                            ("+r Group 2", [corr_2_pos]),
                            ("-r Group 2", [corr_2_neg])],
                     location=(0, -575))

# Add the layout outside the plot, clicking legend item hides the line
corr_fig.add_layout(legend_corr, 'right')
corr_fig.legend.click_policy = "hide"

corr_fig_text = Div(text="<b>Sample Sizes</b>", width=100)
corr_fig_text_1 = Div(text="Group 1:", width=110)
corr_fig_text_2 = Div(text="Group 2:", width=110)

corr_fig_include = CheckboxGroup(labels=correlation_names, active=[])
corr_fig_include_2 = CheckboxGroup(labels=['DVH Endpoints', 'EUD', 'NTCP / TCP'],
                                   active=[])
corr_fig_include.on_change('active', corr_fig_include_ticker)
corr_fig_include_2.on_change('active', corr_fig_include_ticker)

# Control Chart layout
tools = "pan,wheel_zoom,box_zoom,reset,crosshair,save"
corr_chart = figure(plot_width=1050, plot_height=400, tools=tools, logo=None, active_drag="box_zoom")
corr_chart.xaxis.axis_label_text_font_size = PLOT_AXIS_LABEL_FONT_SIZE
corr_chart.yaxis.axis_label_text_font_size = PLOT_AXIS_LABEL_FONT_SIZE
corr_chart.xaxis.major_label_text_font_size = PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
corr_chart.yaxis.major_label_text_font_size = PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
corr_chart.min_border_left = min_border
corr_chart.min_border_bottom = min_border
corr_chart_data_1 = corr_chart.circle('x', 'y', size=CORRELATION_1_CIRCLE_SIZE, color=GROUP_1_COLOR,
                                      alpha=CORRELATION_1_ALPHA, source=source_corr_chart_1)
corr_chart_data_2 = corr_chart.circle('x', 'y', size=CORRELATION_2_CIRCLE_SIZE, color=GROUP_2_COLOR,
                                      alpha=CORRELATION_2_ALPHA, source=source_corr_chart_2)
corr_chart_trend_1 = corr_chart.line('x', 'y', color=GROUP_1_COLOR,
                                     line_width=CORRELATION_1_LINE_WIDTH,
                                     line_dash=CORRELATION_1_LINE_DASH,
                                     source=source_corr_trend_1)
corr_chart_trend_2 = corr_chart.line('x', 'y', color=GROUP_2_COLOR,
                                     line_width=CORRELATION_2_LINE_WIDTH,
                                     line_dash=CORRELATION_1_LINE_DASH,
                                     source=source_corr_trend_2)
corr_chart.add_tools(HoverTool(show_arrow=True,
                               tooltips=[('MRN', '@mrn'),
                                         ('x', '@x{0.2f}'),
                                         ('y', '@y{0.2f}')]))

# Set the legend
legend_corr_chart = Legend(items=[("Group 1", [corr_chart_data_1]),
                                  ("Lin Reg", [corr_chart_trend_1]),
                                  ("Group 2", [corr_chart_data_2]),
                                  ("Lin Reg", [corr_chart_trend_2])],
                           location=(25, 0))

# Add the layout outside the plot, clicking legend item hides the line
corr_chart.add_layout(legend_corr_chart, 'right')
corr_chart.legend.click_policy = "hide"

corr_chart_x_include = CheckboxGroup(labels=["Include this ind. var. in multi-var regression"], active=[], width=400)
corr_chart_x_prev = Button(label="<", button_type="primary", width=50)
corr_chart_x_next = Button(label=">", button_type="primary", width=50)
corr_chart_y_prev = Button(label="<", button_type="primary", width=50)
corr_chart_y_next = Button(label=">", button_type="primary", width=50)
corr_chart_x_prev.on_click(corr_chart_x_prev_ticker)
corr_chart_x_next.on_click(corr_chart_x_next_ticker)
corr_chart_y_prev.on_click(corr_chart_y_prev_ticker)
corr_chart_y_next.on_click(corr_chart_y_next_ticker)
corr_chart_x_include.on_change('active', corr_chart_x_include_ticker)

corr_chart_do_reg_button = Button(label="Perform Multi-Var Regression", button_type="primary", width=200)
corr_chart_do_reg_button.on_click(multi_var_linear_regression)

corr_chart_x = Select(value='', options=[''], width=300)
corr_chart_x.title = "Select an Independent Variable (x-axis)"
corr_chart_x.on_change('value', update_corr_chart_ticker_x)

corr_chart_y = Select(value='', options=[''], width=300)
corr_chart_y.title = "Select a Dependent Variable (y-axis)"
corr_chart_y.on_change('value', update_corr_chart_ticker_y)

corr_chart_text_1 = Div(text="<b>Group 1</b>:", width=1050)
corr_chart_text_2 = Div(text="<b>Group 2</b>:", width=1050)

columns = [TableColumn(field="stat", title="Single-Var Regression", width=100),
           TableColumn(field="group_1", title="Group 1", width=60),
           TableColumn(field="group_2", title="Group 2", width=60)]
data_table_corr_chart = DataTable(source=source_corr_chart_stats, columns=columns, editable=True,
                                  height=180, width=300, row_headers=False)

columns = [TableColumn(field="var_name", title="Variables for Multi-Var Regression", width=100)]
data_table_multi_var_include = DataTable(source=source_multi_var_include, columns=columns,
                                         height=175, width=275, row_headers=False)

div_horizontal_bar_2 = Div(text="<hr>", width=1050)

multi_var_text_1 = Div(text="<b>Group 1</b>", width=500)
columns = [TableColumn(field="var_name", title="Independent Variable", width=300),
           TableColumn(field="coeff_str", title="coefficient",  width=150),
           TableColumn(field="p_str", title="p-value", width=150)]
data_table_multi_var_model_1 = DataTable(source=source_multi_var_coeff_results_1, columns=columns, editable=True,
                                         height=200, row_headers=False)
columns = [TableColumn(field="y_var", title="Dependent Variable", width=150),
           TableColumn(field="r_sq_str", title="R-squared", width=150),
           TableColumn(field="model_p_str", title="Prob for F-statistic", width=150)]
data_table_multi_var_coeff_1 = DataTable(source=source_multi_var_model_results_1, columns=columns, editable=True,
                                         height=60, row_headers=False)

multi_var_text_2 = Div(text="<b>Group 2</b>", width=500)
columns = [TableColumn(field="var_name", title="Independent Variable", width=300),
           TableColumn(field="coeff_str", title="coefficient",  width=150),
           TableColumn(field="p_str", title="p-value", width=150)]
data_table_multi_var_model_2 = DataTable(source=source_multi_var_coeff_results_2, columns=columns, editable=True,
                                         height=200, row_headers=False)
columns = [TableColumn(field="y_var", title="Dependent Variable", width=150),
           TableColumn(field="r_sq_str", title="R-squared", width=150),
           TableColumn(field="model_p_str", title="Prob for F-statistic", width=150)]
data_table_multi_var_coeff_2 = DataTable(source=source_multi_var_model_results_2, columns=columns, editable=True,
                                         height=60, row_headers=False)

source_multi_var_include.on_change('selected', multi_var_include_selection)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Custom group titles
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
group_1_title = 'Group 1 (%s) Custom Title:' % GROUP_1_COLOR.capitalize()
group_2_title = 'Group 2 (%s) Custom Title:' % GROUP_2_COLOR.capitalize()
custom_title_query_blue = TextInput(value='', title=group_1_title, width=300)
custom_title_query_red = TextInput(value='', title=group_2_title, width=300)
custom_title_dvhs_blue = TextInput(value='', title=group_1_title, width=300)
custom_title_dvhs_red = TextInput(value='', title=group_2_title, width=300)
custom_title_rad_bio_blue = TextInput(value='', title=group_1_title, width=300)
custom_title_rad_bio_red = TextInput(value='', title=group_2_title, width=300)
custom_title_roi_viewer_blue = TextInput(value='', title=group_1_title, width=300)
custom_title_roi_viewer_red = TextInput(value='', title=group_2_title, width=300)
custom_title_planning_blue = TextInput(value='', title=group_1_title, width=300)
custom_title_planning_red = TextInput(value='', title=group_2_title, width=300)
custom_title_time_series_blue = TextInput(value='', title=group_1_title, width=300)
custom_title_time_series_red = TextInput(value='', title=group_2_title, width=300)
custom_title_correlation_blue = TextInput(value='', title=group_1_title, width=300)
custom_title_correlation_red = TextInput(value='', title=group_2_title, width=300)
custom_title_regression_blue = TextInput(value='', title=group_1_title, width=300)
custom_title_regression_red = TextInput(value='', title=group_2_title, width=300)

custom_title_query_blue.on_change('value', custom_title_blue_ticker)
custom_title_query_red.on_change('value', custom_title_red_ticker)
custom_title_dvhs_blue.on_change('value', custom_title_blue_ticker)
custom_title_dvhs_red.on_change('value', custom_title_red_ticker)
custom_title_rad_bio_blue.on_change('value', custom_title_blue_ticker)
custom_title_rad_bio_red.on_change('value', custom_title_red_ticker)
custom_title_roi_viewer_blue.on_change('value', custom_title_blue_ticker)
custom_title_roi_viewer_red.on_change('value', custom_title_red_ticker)
custom_title_planning_blue.on_change('value', custom_title_blue_ticker)
custom_title_planning_red.on_change('value', custom_title_red_ticker)
custom_title_time_series_blue.on_change('value', custom_title_blue_ticker)
custom_title_time_series_red.on_change('value', custom_title_red_ticker)
custom_title_correlation_blue.on_change('value', custom_title_blue_ticker)
custom_title_correlation_red.on_change('value', custom_title_red_ticker)
custom_title_regression_blue.on_change('value', custom_title_blue_ticker)
custom_title_regression_red.on_change('value', custom_title_red_ticker)

# Setup axis normalization radio buttons
radio_group_dose = RadioGroup(labels=["Absolute Dose", "Relative Dose (Rx)"], active=0, width=200)
radio_group_dose.on_change('active', radio_group_dose_ticker)
radio_group_volume = RadioGroup(labels=["Absolute Volume", "Relative Volume"], active=1, width=200)
radio_group_volume.on_change('active', radio_group_volume_ticker)

# Setup selectors for dvh review
select_reviewed_mrn = Select(title='MRN to review',
                             value='',
                             options=dvh_review_mrns,
                             width=300)
select_reviewed_mrn.on_change('value', update_dvh_review_rois)

select_reviewed_dvh = Select(title='ROI to review',
                             value='',
                             options=[''],
                             width=360)
select_reviewed_dvh.on_change('value', select_reviewed_dvh_ticker)

review_rx = TextInput(value='', title="Rx Dose (Gy):", width=170)
review_rx.on_change('value', review_rx_ticker)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Radbio Objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
rad_bio_eud_a_input = TextInput(value='', title='EUD a-value:', width=150)
rad_bio_gamma_50_input = TextInput(value='', title=u"\u03b3_50:", width=150)
rad_bio_td_tcd_input = TextInput(value='', title='TD_50 or TCD_50:', width=150)
rad_bio_apply_button = Button(label="Apply parameters", button_type="primary", width=150)
rad_bio_apply_filter = CheckboxButtonGroup(labels=["Group 1", "Group 2", "Selected"], active=[0], width=300)

rad_bio_apply_button.on_click(rad_bio_apply)

columns = [TableColumn(field="mrn", title="MRN", width=150),
           TableColumn(field="group", title="Group", width=100),
           TableColumn(field="roi_name", title="ROI Name", width=250),
           TableColumn(field="ptv_overlap", title="PTV Overlap",  width=150),
           TableColumn(field="roi_type", title="ROI Type", width=100),
           TableColumn(field="rx_dose", title="Rx Dose", width=100, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="fxs", title="Total Fxs", width=100),
           TableColumn(field="fx_dose", title="Fx Dose", width=100, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="eud_a", title="a", width=50),
           TableColumn(field="gamma_50", title=u"\u03b3_50", width=75),
           TableColumn(field="td_tcd", title="TD or TCD", width=150),
           TableColumn(field="eud", title="EUD", width=75, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="ntcp_tcp", title="NTCP or TCP", width=150, formatter=NumberFormatter(format="0.000"))]
data_table_rad_bio = DataTable(source=source_rad_bio, columns=columns, editable=False, width=1100)

source_emami = ColumnDataSource(data=dict(roi=['Brain', 'Brainstem', 'Optic Chiasm', 'Colon', 'Ear (mid/ext)',
                                               'Ear (mid/ext)', 'Esophagus', 'Heart', 'Kidney', 'Lens', 'Liver',
                                               'Lung', 'Optic Nerve', 'Retina'],
                                          ep=['Necrosis', 'Necrosis', 'Blindness', 'Obstruction/Perforation',
                                              'Acute serous otitus', 'Chronic serous otitus', 'Peforation',
                                              'Pericarditus', 'Nephritis', 'Cataract', 'Liver Failure',
                                              'Pneumonitis', 'Blindness', 'Blindness'],
                                          eud_a=[5, 7, 25, 6, 31, 31, 19, 3, 1, 3, 3, 1, 25, 15],
                                          gamma_50=[3, 3, 3, 4, 3, 4, 4, 3, 3, 1, 3, 2, 3, 2],
                                          td_tcd=[60, 65, 65, 55, 40, 65, 68, 50, 28, 18, 40, 24.5, 65, 65]))
columns = [TableColumn(field="roi", title="Structure", width=150),
           TableColumn(field="ep", title="Endpoint", width=250),
           TableColumn(field="eud_a", title="a", width=75),
           TableColumn(field="gamma_50", title=u"\u03b3_50", width=75),
           TableColumn(field="td_tcd", title="TD_50", width=150)]
data_table_emami = DataTable(source=source_emami, columns=columns, editable=False, width=1100)
source_emami.on_change('selected', emami_selection)
emami_text = Div(text="<b>Published EUD Parameters from Emami et. al. for 1.8-2.0Gy fractions</b> (Click to apply)",
                 width=600)
rad_bio_custom_text = Div(text="<b>Applied Parameters:</b>", width=150)
data_table_rad_bio_text = Div(text="<b>EUD Calculations for Query</b>", width=500)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ROI Viewer Objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
roi_colors = plot_colors.cnames.keys()
roi_colors.sort()
roi_viewer_options = [''] + source.data['mrn']
roi_viewer_mrn_select = Select(value='', options=roi_viewer_options, width=200, title='MRN')
roi_viewer_study_date_select = Select(value='', options=[''], width=200, title='Sim Study Date')
roi_viewer_uid_select = Select(value='', options=[''], width=400, title='Study Instance UID')
roi_viewer_roi_select = Select(value='', options=[''], width=250, title='ROI 1 Name')
roi_viewer_roi2_select = Select(value='', options=[''], width=200, title='ROI 2 Name')
roi_viewer_roi3_select = Select(value='', options=[''], width=200, title='ROI 3 Name')
roi_viewer_roi4_select = Select(value='', options=[''], width=200, title='ROI 4 Name')
roi_viewer_roi5_select = Select(value='', options=[''], width=200, title='ROI 5 Name')
roi_viewer_roi1_select_color = Select(value='blue', options=roi_colors, width=150, title='ROI 1 Color')
roi_viewer_roi2_select_color = Select(value='green', options=roi_colors, width=200, height=100, title='ROI 2 Color')
roi_viewer_roi3_select_color = Select(value='red', options=roi_colors, width=200, height=100, title='ROI 3 Color')
roi_viewer_roi4_select_color = Select(value='orange', options=roi_colors, width=200, height=100, title='ROI 4 Color')
roi_viewer_roi5_select_color = Select(value='lightgreen', options=roi_colors, width=200, height=100, title='ROI 5 Color')
roi_viewer_slice_select = Select(value='', options=[''], width=200, title='Slice: z = ')
roi_viewer_previous_slice = Button(label="<", button_type="primary", width=50)
roi_viewer_next_slice = Button(label=">", button_type="primary", width=50)
roi_viewer_flip_text = Div(text="<b>NOTE:</b> Axis flipping requires a figure reset (Click the circular double-arrow)",
                           width=1025)
roi_viewer_flip_x_axis_button = Button(label='Flip X-Axis', button_type='primary', width=100)
roi_viewer_flip_y_axis_button = Button(label='Flip Y-Axis', button_type='primary', width=100)
roi_viewer_plot_tv_button = Button(label='Plot TV', button_type='primary', width=100)

roi_viewer_mrn_select.on_change('value', roi_viewer_mrn_ticker)
roi_viewer_study_date_select.on_change('value', roi_viewer_study_date_ticker)
roi_viewer_uid_select.on_change('value', roi_viewer_uid_ticker)
roi_viewer_roi_select.on_change('value', roi_viewer_roi_ticker)
roi_viewer_roi2_select.on_change('value', roi_viewer_roi2_ticker)
roi_viewer_roi3_select.on_change('value', roi_viewer_roi3_ticker)
roi_viewer_roi4_select.on_change('value', roi_viewer_roi4_ticker)
roi_viewer_roi5_select.on_change('value', roi_viewer_roi5_ticker)
roi_viewer_roi1_select_color.on_change('value', roi_viewer_roi1_color_ticker)
roi_viewer_roi2_select_color.on_change('value', roi_viewer_roi2_color_ticker)
roi_viewer_roi3_select_color.on_change('value', roi_viewer_roi3_color_ticker)
roi_viewer_roi4_select_color.on_change('value', roi_viewer_roi4_color_ticker)
roi_viewer_roi5_select_color.on_change('value', roi_viewer_roi5_color_ticker)
roi_viewer_slice_select.on_change('value', roi_viewer_slice_ticker)
roi_viewer_previous_slice.on_click(roi_viewer_go_to_previous_slice)
roi_viewer_next_slice.on_click(roi_viewer_go_to_next_slice)
roi_viewer_flip_x_axis_button.on_click(roi_viewer_flip_x_axis)
roi_viewer_flip_y_axis_button.on_click(roi_viewer_flip_y_axis)
roi_viewer_plot_tv_button.on_click(roi_viewer_plot_tv)

roi_viewer = figure(plot_width=825, plot_height=600, logo=None, match_aspect=True,
                    tools="pan,wheel_zoom,reset,crosshair,save")
roi_viewer.xaxis.axis_label_text_font_size = PLOT_AXIS_LABEL_FONT_SIZE
roi_viewer.yaxis.axis_label_text_font_size = PLOT_AXIS_LABEL_FONT_SIZE
roi_viewer.xaxis.major_label_text_font_size = PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
roi_viewer.yaxis.major_label_text_font_size = PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
roi_viewer.min_border_left = min_border
roi_viewer.min_border_bottom = min_border
roi_viewer.y_range.flipped = True
roi_viewer_patch1 = roi_viewer.patch('x', 'y', source=source_roi_viewer, color='blue', alpha=0.5)
roi_viewer_patch2 = roi_viewer.patch('x', 'y', source=source_roi2_viewer, color='green', alpha=0.5)
roi_viewer_patch3 = roi_viewer.patch('x', 'y', source=source_roi3_viewer, color='red', alpha=0.5)
roi_viewer_patch4 = roi_viewer.patch('x', 'y', source=source_roi4_viewer, color='orange', alpha=0.5)
roi_viewer_patch5 = roi_viewer.patch('x', 'y', source=source_roi5_viewer, color='lightgreen', alpha=0.5)
roi_viewer.patch('x', 'y', source=source_tv, color='black', alpha=0.5)
roi_viewer.xaxis.axis_label = "Lateral DICOM Coordinate (mm)"
roi_viewer.yaxis.axis_label = "Anterior/Posterior DICOM Coordinate (mm)"
roi_viewer.on_event(events.MouseWheel, roi_viewer_wheel_event)
roi_viewer_scrolling = CheckboxGroup(labels=["Enable Slice Scrolling with Mouse Wheel"], active=[])

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Layout objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
layout_query = column(row(custom_title_query_blue, Spacer(width=50), custom_title_query_red,
                          Spacer(width=50), query_button, Spacer(width=50), download_dropdown),
                      div_selector,
                      add_selector_row_button,
                      row(selector_row, Spacer(width=10), select_category1, select_category2, group_selector,
                          delete_selector_row_button, Spacer(width=10), selector_not_operator_checkbox),
                      selection_filter_data_table,
                      div_selector_end,
                      div_range,
                      add_range_row_button,
                      row(range_row, Spacer(width=10), select_category, text_min, text_max, group_range,
                          delete_range_row_button, Spacer(width=10), range_not_operator_checkbox),
                      range_filter_data_table)

layout_dvhs = column(row(custom_title_dvhs_blue, Spacer(width=50), custom_title_dvhs_red),
                     row(radio_group_dose, radio_group_volume),
                     row(select_reviewed_mrn, select_reviewed_dvh, review_rx),
                     dvh_plots,
                     data_table_title,
                     data_table,
                     div_endpoint_start,
                     div_endpoint,
                     add_endpoint_row_button,
                     row(ep_row, Spacer(width=10), select_ep_type, ep_text_input, ep_units_in, delete_ep_row_button),
                     ep_data_table,
                     endpoint_table_title,
                     data_table_endpoints)

layout_rad_bio = column(row(custom_title_rad_bio_blue, Spacer(width=50), custom_title_rad_bio_red),
                        emami_text,
                        data_table_emami,
                        rad_bio_custom_text,
                        row(rad_bio_eud_a_input, Spacer(width=50),
                            rad_bio_gamma_50_input, Spacer(width=50), rad_bio_td_tcd_input, Spacer(width=50),
                            rad_bio_apply_filter, Spacer(width=50), rad_bio_apply_button),
                        data_table_rad_bio_text,
                        data_table_rad_bio,
                        Spacer(width=1000, height=100))

layout_planning_data = column(row(custom_title_planning_blue, Spacer(width=50), custom_title_planning_red),
                              rxs_table_title, data_table_rxs,
                              plans_table_title, data_table_plans,
                              beam_table_title, data_table_beams, beam_table_title2, data_table_beams2)

layout_time_series = column(row(custom_title_time_series_blue, Spacer(width=50), custom_title_time_series_red),
                            row(control_chart_y, control_chart_lookback_units, control_chart_text_lookback_distance,
                                Spacer(width=10), control_chart_percentile, Spacer(width=10), trend_update_button),
                            control_chart,
                            div_horizontal_bar,
                            row(histogram_bin_slider, histogram_radio_group),
                            row(histogram_normaltest_1_text, histogram_ttest_text),
                            row(histogram_normaltest_2_text, histogram_ranksums_text),
                            histograms,
                            Spacer(width=1000, height=100))

layout_roi_viewer = column(row(custom_title_roi_viewer_blue, Spacer(width=50), custom_title_roi_viewer_red),
                           row(roi_viewer_mrn_select, roi_viewer_study_date_select, roi_viewer_uid_select),
                           Div(text="<hr>", width=800),
                           row(roi_viewer_roi_select, roi_viewer_roi1_select_color, roi_viewer_slice_select,
                               roi_viewer_previous_slice, roi_viewer_next_slice),
                           Div(text="<hr>", width=800),
                           row(roi_viewer_roi2_select, roi_viewer_roi3_select,
                               roi_viewer_roi4_select, roi_viewer_roi5_select),
                           row(roi_viewer_roi2_select_color, roi_viewer_roi3_select_color,
                               roi_viewer_roi4_select_color, roi_viewer_roi5_select_color),
                           row(roi_viewer_flip_text),
                           row(roi_viewer_flip_x_axis_button, roi_viewer_flip_y_axis_button,
                               roi_viewer_plot_tv_button),
                           row(roi_viewer_scrolling),
                           row(roi_viewer),
                           row(Spacer(width=1000, height=100)))

layout_correlation_matrix = column(row(custom_title_correlation_blue, Spacer(width=50), custom_title_correlation_red),
                                   row(corr_fig_text, corr_fig_text_1, corr_fig_text_2),
                                   row(corr_fig, corr_fig_include, corr_fig_include_2))

layout_regression = column(row(custom_title_regression_blue, Spacer(width=50), custom_title_regression_red),
                           row(column(corr_chart_x_include,
                                      row(corr_chart_x_prev, corr_chart_x_next, Spacer(width=10), corr_chart_x),
                                      row(corr_chart_y_prev, corr_chart_y_next, Spacer(width=10), corr_chart_y)),
                               Spacer(width=10, height=175), data_table_corr_chart,
                               Spacer(width=10, height=175), data_table_multi_var_include),
                           corr_chart,
                           div_horizontal_bar_2,
                           corr_chart_do_reg_button,
                           multi_var_text_1,
                           data_table_multi_var_coeff_1,
                           data_table_multi_var_model_1,
                           multi_var_text_2,
                           data_table_multi_var_coeff_2,
                           data_table_multi_var_model_2,
                           Spacer(width=1000, height=100))

query_tab = Panel(child=layout_query, title='Query')
dvh_tab = Panel(child=layout_dvhs, title='DVHs')
rad_bio_tab = Panel(child=layout_rad_bio, title='Rad Bio')
roi_viewer_tab = Panel(child=layout_roi_viewer, title='ROI Viewer')
planning_data_tab = Panel(child=layout_planning_data, title='Planning Data')
time_series_tab = Panel(child=layout_time_series, title='Time-Series')
correlation_matrix_tab = Panel(child=layout_correlation_matrix, title='Correlation')
correlation_tab = Panel(child=layout_regression, title='Regression')

tabs = Tabs(tabs=[query_tab, dvh_tab, rad_bio_tab, roi_viewer_tab, planning_data_tab, time_series_tab,
                  correlation_matrix_tab, correlation_tab])


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
