#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
main program for Bokeh server (re-write for new query UI)
Created on Sun Apr 21 2017
@author: Dan Cutright, PhD
"""


from __future__ import print_function
from future.utils import listitems
from analysis_tools import DVH, calc_eud, dose_to_volume, volume_of_dose
from utilities import Temp_DICOM_FileSet, get_planes_from_string, get_union, load_options, calc_stats,\
    get_study_instance_uids
import auth
from sql_connector import DVH_SQL
from sql_to_python import QuerySQL
import numpy as np
import itertools
from datetime import datetime
from os.path import dirname, join
from bokeh.layouts import column, row
from bokeh.models import Legend, CustomJS, HoverTool, Spacer
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.palettes import Colorblind8 as palette
from bokeh.models.widgets import Select, Button, Div, TableColumn, DataTable, Panel, Tabs, NumberFormatter,\
    RadioButtonGroup, TextInput, RadioGroup, CheckboxButtonGroup, Dropdown, CheckboxGroup, PasswordInput
from dicompylercore import dicomparser, dvhcalc
from bokeh import events
from scipy.stats import normaltest, pearsonr, linregress
from math import pi
import statsmodels.api as sm
import matplotlib.colors as plot_colors
import time
import options
from dateutil.parser import parse
from options import N
from bokeh_components.custom_titles import custom_title
from bokeh_components import columns, sources
from bokeh_components.utilities import group_constraint_count, get_include_map, get_correlation,\
    validate_correlation, update_or_add_endpoints_to_correlation
from bokeh_components.mlc_analyzer import MLC_Analyzer
from bokeh_components.time_series import TimeSeries
from bokeh_components.correlation import Correlation


options = load_options(options)


# This depends on a user defined function in dvh/auth.py.  By default, this returns True
# It is up to the user/installer to write their own function (e.g., using python-ldap)
# Proper execution of this requires placing Bokeh behind a reverse proxy with SSL setup (HTTPS)
# Please see Bokeh documentation for more information
ACCESS_GRANTED = not options.AUTH_USER_REQ

SELECT_CATEGORY1_DEFAULT = 'ROI Institutional Category'
SELECT_CATEGORY_DEFAULT = 'Rx Dose'

# Used to keep Query UI clean
ALLOW_SOURCE_UPDATE = True

# Declare variables
COLORS = itertools.cycle(palette)
CURRENT_DVH = []
ANON_ID_MAP = {}
x, y = [], []
N = options.N
UIDS = {n: [] for n in N}
CORRELATION = {n: [] for n in N}
BAD_UID = {n: [] for n in N}

temp_dvh_info = Temp_DICOM_FileSet()
dvh_review_mrns = temp_dvh_info.mrn
if dvh_review_mrns[0] != '':
    dvh_review_rois = temp_dvh_info.get_roi_names(dvh_review_mrns[0]).values()
    dvh_review_mrns.append('')
else:
    dvh_review_rois = ['']


ROI_VIEWER_DATA = {str(i): {} for i in range(1, 6)}
tv_data = {}


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
MULTI_VAR_REG_VARS = {name: False for name in multi_var_reg_var_names}


mlc_analyzer = MLC_Analyzer(sources)
time_series = TimeSeries(sources, range_categories)
correlation = Correlation(sources, correlation_names, range_categories)


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
        sources.selectors.patch(patch)


def add_selector_row():
    if sources.selectors.data['row']:
        temp = sources.selectors.data

        for key in list(temp):
            temp[key].append('')
        temp['row'][-1] = len(temp['row'])

        sources.selectors.data = temp
        new_options = [str(x+1) for x in range(len(temp['row']))]
        selector_row.options = new_options
        selector_row.value = new_options[-1]
        select_category1.value = SELECT_CATEGORY1_DEFAULT
        select_category2.value = select_category2.options[0]
        selector_not_operator_checkbox.active = []
    else:
        selector_row.options = ['1']
        selector_row.value = '1'
        sources.selectors.data = dict(row=[1], category1=[''], category2=[''],
                                      group=[], group_label=[''], not_status=[''])
    update_selector_source()

    clear_source_selection('selectors')


def select_category1_ticker(attr, old, new):
    update_select_category2_values()
    update_selector_source()


def select_category2_ticker(attr, old, new):
    update_selector_source()


def selector_not_operator_ticker(attr, old, new):
    update_selector_source()


def selector_row_ticker(attr, old, new):
    if sources.selectors.data['category1'] and sources.selectors.data['category1'][-1]:
        r = int(selector_row.value) - 1
        category1 = sources.selectors.data['category1'][r]
        category2 = sources.selectors.data['category2'][r]
        group = sources.selectors.data['group'][r]
        not_status = sources.selectors.data['not_status'][r]

        select_category1.value = category1
        select_category2.value = category2
        group_selector.active = [[0], [1], [0, 1]][group-1]
        if not_status:
            selector_not_operator_checkbox.active = [0]
        else:
            selector_not_operator_checkbox.active = []


def update_selector_row_on_selection(attr, old, new):
    if new:
        selector_row.value = selector_row.options[min(new)]


def delete_selector_row():
    if selector_row.value:
        new_selectors_source = sources.selectors.data
        index_to_delete = int(selector_row.value) - 1
        new_source_length = len(sources.selectors.data['category1']) - 1

        if new_source_length == 0:
            clear_source_data('selector')
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

            selector_row.options = [str(x+1) for x in range(new_source_length)]
            if selector_row.value not in selector_row.options:
                selector_row.value = selector_row.options[-1]
            sources.selectors.data = new_selectors_source

        clear_source_selection('selectors')


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Functions for Querying by numerical data
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def add_range_row():
    if sources.ranges.data['row']:
        temp = sources.ranges.data

        for key in list(temp):
            temp[key].append('')
        temp['row'][-1] = len(temp['row'])
        sources.ranges.data = temp
        new_options = [str(x+1) for x in range(len(temp['row']))]
        range_row.options = new_options
        range_row.value = new_options[-1]
        select_category.value = SELECT_CATEGORY_DEFAULT
        group_range.active = [0]
        range_not_operator_checkbox.active = []
    else:
        range_row.options = ['1']
        range_row.value = '1'
        sources.ranges.data = dict(row=['1'], category=[''], min=[''], max=[''], min_display=[''], max_display=[''],
                                   group=[''], group_label=[''], not_status=[''])

    update_range_titles(reset_values=True)
    update_range_source()

    clear_source_selection('ranges')


def update_range_source():
    if range_row.value:
        table = range_categories[select_category.value]['table']
        var_name = range_categories[select_category.value]['var_name']

        r = int(range_row.value) - 1
        group = sum([i+1 for i in group_range.active])  # a result of 3 means group 1 & 2
        group_labels = ['1', '2', '1 & 2']
        group_label = group_labels[group-1]
        not_status = ['', 'Not'][len(range_not_operator_checkbox.active)]

        if select_category.value == 'Simulation Date':
            min_value = str(parse(text_min.value).date())
            min_display = min_value

            max_value = str(parse(text_max.value).date())
            max_display = max_value
        else:

            try:
                min_value = float(text_min.value)
            except ValueError:
                try:
                    min_value = float(DVH_SQL().get_min_value(table, var_name))
                except TypeError:
                    min_value = ''

            try:
                max_value = float(text_max.value)
            except ValueError:
                try:
                    max_value = float(DVH_SQL().get_max_value(table, var_name))
                except TypeError:
                    max_value = ''

            if min_value or min_value == 0.:
                min_display = "%s %s" % (str(min_value), range_categories[select_category.value]['units'])
            else:
                min_display = 'None'

            if max_value or max_value == 0.:
                max_display = "%s %s" % (str(max_value), range_categories[select_category.value]['units'])
            else:
                max_display = 'None'

        patch = {'category': [(r, select_category.value)], 'min': [(r, min_value)], 'max': [(r, max_value)],
                 'min_display': [(r, min_display)], 'max_display': [(r, max_display)],
                 'group': [(r, group)], 'group_label': [(r, group_label)], 'not_status': [(r, not_status)]}
        sources.ranges.patch(patch)

        group_range.active = [[0], [1], [0, 1]][group - 1]
        text_min.value = str(min_value)
        text_max.value = str(max_value)


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
    if sources.ranges.data['category'] and sources.ranges.data['category'][-1]:
        r = int(new) - 1
        category = sources.ranges.data['category'][r]
        min_new = sources.ranges.data['min'][r]
        max_new = sources.ranges.data['max'][r]
        group = sources.ranges.data['group'][r]
        not_status = sources.ranges.data['not_status'][r]

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
        new_range_source = sources.ranges.data
        index_to_delete = int(range_row.value) - 1
        new_source_length = len(sources.ranges.data['category']) - 1

        if new_source_length == 0:
            clear_source_data('ranges')
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

            range_row.options = [str(x+1) for x in range(new_source_length)]
            if range_row.value not in range_row.options:
                range_row.value = range_row.options[-1]
            sources.ranges.data = new_range_source

        clear_source_selection('ranges')


def ensure_range_group_is_assigned(attrname, old, new):
    if not group_range.active:
        group_range.active = [-old[0] + 1]
    update_range_source()


def update_range_row_on_selection(attr, old, new):
    if new:
        range_row.value = range_row.options[min(new)]


def clear_source_selection(key):
    getattr(sources, key).selected.indices = []


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Functions for adding DVH endpoints
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def add_endpoint():
    if sources.endpoint_defs.data['row']:
        temp = sources.endpoint_defs.data

        for key in list(temp):
            temp[key].append('')
        temp['row'][-1] = len(temp['row'])
        sources.endpoint_defs.data = temp
        new_options = [str(x+1) for x in range(len(temp['row']))]
        ep_row.options = new_options
        ep_row.value = new_options[-1]
    else:
        ep_row.options = ['1']
        ep_row.value = '1'
        sources.endpoint_defs.data = dict(row=['1'], output_type=[''], input_type=[''], input_value=[''],
                                          label=[''], units_in=[''], units_out=[''])
        if not ep_text_input.value:
            ep_text_input.value = '1'

    update_ep_source()

    clear_source_selection('endpoint_defs')


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
        sources.endpoint_defs.patch(patch)
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
        new_ep_source = sources.endpoint_defs.data
        index_to_delete = int(ep_row.value) - 1
        new_source_length = len(sources.endpoint_defs.data['output_type']) - 1

        if new_source_length == 0:
            clear_source_data('endpoint_defs')
            ep_row.options = ['']
            ep_row.value = ''
        else:
            for key in list(new_ep_source):
                new_ep_source[key].pop(index_to_delete)

            for i in range(index_to_delete, new_source_length):
                new_ep_source['row'][i] -= 1

            ep_row.options = [str(x+1) for x in range(new_source_length)]
            if ep_row.value not in ep_row.options:
                ep_row.value = ep_row.options[-1]
            sources.endpoint_defs.data = new_ep_source

        update_source_endpoint_calcs()  # not efficient, but still relatively quick
        clear_source_selection('endpoint_defs')


def update_ep_row_on_selection(attr, old, new):
    global ALLOW_SOURCE_UPDATE
    ALLOW_SOURCE_UPDATE = False

    if new:
        data = sources.endpoint_defs.data
        r = min(new)

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
        data = sources.selectors.data
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
        data = sources.ranges.data
        for r in data['row']:
            r = int(r)
            if data['group'][r-1] in {active_group, 3}:
                var_name = range_categories[data['category'][r-1]]['var_name']
                table = range_categories[data['category'][r-1]]['table']

                value_low, value_high = data['min'][r-1], data['max'][r-1]
                if data['category'][r-1] != 'Simulation Date':
                    value_low, value_high = float(value_low), float(value_high)

                # Modify value_low and value_high so SQL interprets values as dates, if applicable
                if var_name in {'sim_study_date', 'birth_date'}:
                    value_low = "'%s'" % value_low
                    value_high = "'%s'" % value_high

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
    global CURRENT_DVH, BAD_UID, time_series
    BAD_UID = {n: [] for n in N}
    old_update_button_label = query_button.label
    old_update_button_type = query_button.button_type
    query_button.label = 'Updating...'
    query_button.button_type = 'warning'
    print(str(datetime.now()), 'Constructing query for complete dataset', sep=' ')
    uids, dvh_query_str = get_query()
    print(str(datetime.now()), 'getting dvh data', sep=' ')
    CURRENT_DVH = DVH(uid=uids, dvh_condition=dvh_query_str)
    if CURRENT_DVH.count:
        print(str(datetime.now()), 'initializing source data ', CURRENT_DVH.query, sep=' ')
        time_series.update_current_dvh_group(update_dvh_data(CURRENT_DVH))
        if not options.LITE_VIEW:
            print(str(datetime.now()), 'updating correlation data')
            correlation.update_data(correlation_variables)
            print(str(datetime.now()), 'correlation data updated')
        update_source_endpoint_calcs()
        if not options.LITE_VIEW:
            calculate_review_dvh()
            initialize_rad_bio_source()
            time_series.y_axis.value = ''
            update_roi_viewer_mrn()
            mlc_analyzer.update_mrn()
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
    global UIDS, ANON_ID_MAP

    dvh_group_1, dvh_group_2 = [], []
    group_1_constraint_count, group_2_constraint_count = group_constraint_count(sources)

    if group_1_constraint_count and group_2_constraint_count:
        extra_rows = 12
    elif group_1_constraint_count or group_2_constraint_count:
        extra_rows = 6
    else:
        extra_rows = 0

    print(str(datetime.now()), 'updating dvh data', sep=' ')
    line_colors = [color for j, color in itertools.izip(range(dvh.count + extra_rows), COLORS)]

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
        UIDS['1'] = []
        clear_source_data('patch_1')
        clear_source_data('stats_1')
    else:
        print(str(datetime.now()), 'Constructing Group 1 query', sep=' ')
        UIDS['1'], dvh_query_str = get_query(group=1)
        dvh_group_1 = DVH(uid=UIDS['1'], dvh_condition=dvh_query_str)
        UIDS['1'] = dvh_group_1.study_instance_uid
        stat_dvhs_1 = dvh_group_1.get_standard_stat_dvh(dose_scale=stat_dose_scale, volume_scale=stat_volume_scale)

        if radio_group_dose.active == 1:
            x_axis_1 = dvh_group_1.get_resampled_x_axis()
        else:
            x_axis_1 = np.add(np.linspace(0, dvh_group_1.bin_count, dvh_group_1.bin_count) / 100., 0.005)

        sources.patch_1.data = {'x_patch': np.append(x_axis_1, x_axis_1[::-1]).tolist(),
                                'y_patch': np.append(stat_dvhs_1['q3'], stat_dvhs_1['q1'][::-1]).tolist()}
        sources.stats_1.data = {'x': x_axis_1.tolist(),
                                'min': stat_dvhs_1['min'].tolist(),
                                'q1': stat_dvhs_1['q1'].tolist(),
                                'mean': stat_dvhs_1['mean'].tolist(),
                                'median': stat_dvhs_1['median'].tolist(),
                                'q3': stat_dvhs_1['q3'].tolist(),
                                'max': stat_dvhs_1['max'].tolist()}
    if group_2_constraint_count == 0:
        UIDS['2'] = []
        clear_source_data('patch_2')
        clear_source_data('stats_2')

    else:
        print(str(datetime.now()), 'Constructing Group 2 query', sep=' ')
        UIDS['2'], dvh_query_str = get_query(group=2)
        dvh_group_2 = DVH(uid=UIDS['2'], dvh_condition=dvh_query_str)
        UIDS['2'] = dvh_group_2.study_instance_uid
        stat_dvhs_2 = dvh_group_2.get_standard_stat_dvh(dose_scale=stat_dose_scale, volume_scale=stat_volume_scale)

        if radio_group_dose.active == 1:
            x_axis_2 = dvh_group_2.get_resampled_x_axis()
        else:
            x_axis_2 = np.add(np.linspace(0, dvh_group_2.bin_count, dvh_group_2.bin_count) / 100., 0.005)

        sources.patch_2.data = {'x_patch': np.append(x_axis_2, x_axis_2[::-1]).tolist(),
                                'y_patch': np.append(stat_dvhs_2['q3'], stat_dvhs_2['q1'][::-1]).tolist()}
        sources.stats_2.data = {'x': x_axis_2.tolist(),
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
    for n in range(dvh.count):
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
    for r in range(len(dvh.study_instance_uid)):

        current_uid = dvh.study_instance_uid[r]
        current_roi = dvh.roi_name[r]

        if dvh_group_1:
            for r1 in range(len(dvh_group_1.study_instance_uid)):
                if dvh_group_1.study_instance_uid[r1] == current_uid and dvh_group_1.roi_name[r1] == current_roi:
                    dvh_groups.append('Group 1')

        if dvh_group_2:
            for r2 in range(len(dvh_group_2.study_instance_uid)):
                if dvh_group_2.study_instance_uid[r2] == current_uid and dvh_group_2.roi_name[r2] == current_roi:
                    if len(dvh_groups) == r + 1:
                        dvh_groups[r] = 'Group 1 & 2'
                    else:
                        dvh_groups.append('Group 2')

        if len(dvh_groups) < r + 1:
            dvh_groups.append('error')

    dvh_groups.insert(0, 'Review')

    for n in range(6):
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
    attributes = ['rx_dose', 'volume', 'surface_area', 'min_dose', 'mean_dose', 'max_dose', 'dist_to_ptv_min',
                  'dist_to_ptv_median', 'dist_to_ptv_mean', 'dist_to_ptv_max', 'dist_to_ptv_centroids',
                  'ptv_overlap', 'cross_section_max', 'cross_section_median', 'spread_x', 'spread_y', 'spread_z']
    if extra_rows > 0:
        dvh.study_instance_uid.extend(['N/A'] * extra_rows)
        dvh.institutional_roi.extend(['N/A'] * extra_rows)
        dvh.physician_roi.extend(['N/A'] * extra_rows)
        dvh.roi_type.extend(['Stat'] * extra_rows)
    if group_1_constraint_count > 0:
        for attr in attributes:
            getattr(dvh, attr).extend(calc_stats(getattr(dvh_group_1, attr)))

    if group_2_constraint_count > 0:
        for attr in attributes:
            getattr(dvh, attr).extend(calc_stats(getattr(dvh_group_2, attr)))

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
    dvh.dist_to_ptv_centroids.insert(0, 'N/A')
    dvh.ptv_overlap.insert(0, 'N/A')
    dvh.cross_section_max.insert(0, 'N/A')
    dvh.cross_section_median.insert(0, 'N/A')
    dvh.spread_x.insert(0, 'N/A')
    dvh.spread_y.insert(0, 'N/A')
    dvh.spread_z.insert(0, 'N/A')
    line_colors.insert(0, options.REVIEW_DVH_COLOR)
    x_data.insert(0, [0])
    y_data.insert(0, [0])

    # anonymize ids
    ANON_ID_MAP = {mrn: i for i, mrn in enumerate(list(set(dvh.mrn)))}
    anon_id = [ANON_ID_MAP[dvh.mrn[i]] for i in range(len(dvh.mrn))]

    print(str(datetime.now()), "writing sources.dvhs.data", sep=' ')
    sources.dvhs.data = {'mrn': dvh.mrn,
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
                         'dist_to_ptv_centroids': dvh.dist_to_ptv_centroids,
                         'ptv_overlap': dvh.ptv_overlap,
                         'cross_section_max': dvh.cross_section_max,
                         'cross_section_median': dvh.cross_section_median,
                         'spread_x': dvh.spread_x,
                         'spread_y': dvh.spread_y,
                         'spread_z': dvh.spread_z,
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

    return {'1': dvh_group_1, '2': dvh_group_2}


# updates beam ColumnSourceData for a given list of uids
def update_beam_data(uids):

    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    beam_data = QuerySQL('Beams', cond_str)

    groups = get_group_list(beam_data.study_instance_uid)

    anon_id = [ANON_ID_MAP[beam_data.mrn[i]] for i in range(len(beam_data.mrn))]

    attributes = ['mrn', 'beam_dose', 'beam_energy_min', 'beam_energy_max', 'beam_mu', 'beam_mu_per_deg',
                  'beam_mu_per_cp', 'beam_name', 'beam_number', 'beam_type', 'scan_mode', 'scan_spot_count',
                  'control_point_count', 'fx_count', 'fx_grp_beam_count', 'fx_grp_number', 'gantry_start', 'gantry_end',
                  'gantry_rot_dir', 'gantry_range', 'gantry_min', 'gantry_max', 'collimator_start', 'collimator_end',
                  'collimator_rot_dir', 'collimator_range', 'collimator_min', 'collimator_max', 'couch_start',
                  'couch_end', 'couch_rot_dir', 'couch_range', 'couch_min', 'couch_max', 'radiation_type', 'ssd',
                  'treatment_machine']
    data = {attr: getattr(beam_data, attr) for attr in attributes}
    data['anon_id'] = anon_id
    data['groups'] = groups
    data['uid'] = beam_data.study_instance_uid

    sources.beams.data = data


# updates plan ColumnSourceData for a given list of uids
def update_plan_data(uids):

    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    plan_data = QuerySQL('Plans', cond_str)

    # Determine Groups
    groups = get_group_list(plan_data.study_instance_uid)

    anon_id = [ANON_ID_MAP[plan_data.mrn[i]] for i in range(len(plan_data.mrn))]

    attributes = ['mrn', 'age', 'birth_date', 'dose_grid_res', 'fxs', 'patient_orientation', 'patient_sex', 'physician',
                  'rx_dose', 'sim_study_date', 'total_mu', 'tx_modality', 'tx_site', 'heterogeneity_correction',
                  'baseline']
    data = {attr: getattr(plan_data, attr) for attr in attributes}
    data['anon_id'] = anon_id
    data['groups'] = groups
    data['uid'] = plan_data.study_instance_uid

    sources.plans.data = data


# updates rx ColumnSourceData for a given list of uids
def update_rx_data(uids):

    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    rx_data = QuerySQL('Rxs', cond_str)

    groups = get_group_list(rx_data.study_instance_uid)

    anon_id = [ANON_ID_MAP[rx_data.mrn[i]] for i in range(len(rx_data.mrn))]

    attributes = ['mrn', 'plan_name', 'fx_dose', 'rx_percent', 'fxs', 'rx_dose', 'fx_grp_count', 'fx_grp_name',
                  'fx_grp_number', 'normalization_method', 'normalization_object']
    data = {attr: getattr(rx_data, attr) for attr in attributes}
    data['anon_id'] = anon_id
    data['groups'] = groups
    data['uid'] = rx_data.study_instance_uid

    sources.rxs.data = data


def get_group_list(uids):

    groups = []
    for r in range(len(uids)):
        if uids[r] in UIDS['1']:
            if uids[r] in UIDS['2']:
                groups.append('Group 1 & 2')
            else:
                groups.append('Group 1')
        else:
            groups.append('Group 2')

    return groups


def update_source_endpoint_calcs():

    if CURRENT_DVH:
        group_1_constraint_count, group_2_constraint_count = group_constraint_count(sources)

        ep = {'mrn': ['']}
        ep_group = {'1': {}, '2': {}}

        table_columns = []

        ep['mrn'] = CURRENT_DVH.mrn
        ep['uid'] = CURRENT_DVH.study_instance_uid
        ep['group'] = sources.dvhs.data['group']
        ep['roi_name'] = sources.dvhs.data['roi_name']

        table_columns.append(TableColumn(field='mrn', title='MRN'))
        table_columns.append(TableColumn(field='group', title='Group'))
        table_columns.append(TableColumn(field='roi_name', title='ROI Name'))

        data = sources.endpoint_defs.data
        for r in range(len(data['row'])):
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
                ep[ep_name] = CURRENT_DVH.get_dose_to_volume(x, volume_scale=endpoint_input, dose_scale=endpoint_output)
                for g in N:
                    if time_series.current_dvh_group[g]:
                        ep_group[g][ep_name] = time_series.current_dvh_group[g].get_dose_to_volume(x, volume_scale=endpoint_input,
                                                                                       dose_scale=endpoint_output)

            else:
                ep[ep_name] = CURRENT_DVH.get_volume_of_dose(x, dose_scale=endpoint_input, volume_scale=endpoint_output)
                for g in N:
                    if time_series.current_dvh_group[g]:
                        ep_group[g][ep_name] = time_series.current_dvh_group[g].get_volume_of_dose(x, dose_scale=endpoint_input,
                                                                                       volume_scale=endpoint_output)

            if group_1_constraint_count and group_2_constraint_count:
                ep_1_stats = calc_stats(ep_group['1'][ep_name])
                ep_2_stats = calc_stats(ep_group['2'][ep_name])
                stats = []
                for i in range(len(ep_1_stats)):
                    stats.append(ep_1_stats[i])
                    stats.append(ep_2_stats[i])
                ep[ep_name].extend(stats)
            else:
                ep[ep_name].extend(calc_stats(ep[ep_name]))
        sources.endpoint_calcs.data = ep

        # Update endpoint calc from review_dvh, if available
        if sources.dvhs.data['y'][0] != []:
            review_ep = {}
            rx = float(sources.dvhs.data['rx_dose'][0])
            volume = float(sources.dvhs.data['volume'][0])
            data = sources.endpoint_defs.data
            for r in range(len(data['row'])):
                ep_name = str(data['label'][r])
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
                    if endpoint_input == 'relative':
                        current_ep = dose_to_volume(y, x)
                    else:
                        current_ep = dose_to_volume(y, x / volume)
                    if endpoint_output == 'relative' and rx != 0:
                        current_ep = current_ep / rx

                else:
                    if endpoint_input == 'relative':
                        current_ep = volume_of_dose(y, x * rx)
                    else:
                        current_ep = volume_of_dose(y, x)
                    if endpoint_output == 'absolute' and volume != 0:
                        current_ep = current_ep * volume

                review_ep[ep_name] = [(0, current_ep)]

            review_ep['mrn'] = [(0, select_reviewed_mrn.value)]
            sources.endpoint_calcs.patch(review_ep)

        update_endpoint_view()

    if not options.LITE_VIEW:
        time_series.update_options()


def update_endpoint_view():
    if CURRENT_DVH:
        rows = len(sources.endpoint_calcs.data['mrn'])
        ep_view = {'mrn': sources.endpoint_calcs.data['mrn'],
                   'group': sources.endpoint_calcs.data['group'],
                   'roi_name': sources.endpoint_calcs.data['roi_name']}
        for i in range(1, options.ENDPOINT_COUNT+1):
            ep_view["ep%s" % i] = [''] * rows  # filling table with empty strings

        for r in range(len(sources.endpoint_defs.data['row'])):
            if r < options.ENDPOINT_COUNT:  # limiting UI to ENDPOINT_COUNT for efficieny
                key = sources.endpoint_defs.data['label'][r]
                ep_view["ep%s" % (r+1)] = sources.endpoint_calcs.data[key]

        sources.endpoint_view.data = ep_view
        if not options.LITE_VIEW:
            update_endpoints_in_correlation()


def initialize_rad_bio_source():
    include = get_include_map(sources)

    # Get data from DVH Table
    mrn = [j for i, j in enumerate(sources.dvhs.data['mrn']) if include[i]]
    uid = [j for i, j in enumerate(sources.dvhs.data['uid']) if include[i]]
    group = [j for i, j in enumerate(sources.dvhs.data['group']) if include[i]]
    roi_name = [j for i, j in enumerate(sources.dvhs.data['roi_name']) if include[i]]
    ptv_overlap = [j for i, j in enumerate(sources.dvhs.data['ptv_overlap']) if include[i]]
    roi_type = [j for i, j in enumerate(sources.dvhs.data['roi_type']) if include[i]]
    rx_dose = [j for i, j in enumerate(sources.dvhs.data['rx_dose']) if include[i]]

    # Get data from beam table
    fxs, fx_dose = [], []
    for eud_uid in uid:
        plan_index = sources.plans.data['uid'].index(eud_uid)
        fxs.append(sources.plans.data['fxs'][plan_index])

        rx_uids, rx_fxs = sources.rxs.data['uid'], sources.rxs.data['fxs']
        rx_indices = [i for i, rx_uid in enumerate(rx_uids) if rx_uid == eud_uid]
        max_rx_fxs = max([sources.rxs.data['fxs'][i] for i in rx_indices])
        rx_index = [i for i, rx_uid in enumerate(rx_uids) if rx_uid == eud_uid and rx_fxs[i] == max_rx_fxs][0]
        fx_dose.append(sources.rxs.data['fx_dose'][rx_index])

    sources.rad_bio.data = {'mrn': mrn,
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
    row_count = len(sources.rad_bio.data['uid'])

    if rad_bio_apply_filter.active == [0, 1]:
        include = [i for i in range(row_count)]
    elif 0 in rad_bio_apply_filter.active:
        include = [i for i in range(row_count) if sources.rad_bio.data['group'][i] in {'Group 1', 'Group 1 & 2'}]
    elif 1 in rad_bio_apply_filter.active:
        include = [i for i in range(row_count) if sources.rad_bio.data['group'][i] in {'Group 2', 'Group 1 & 2'}]
    else:
        include = []

    if 2 in rad_bio_apply_filter.active:
        include.extend([i for i in range(row_count) if i in sources.rad_bio.selected.indices])

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

    patch = {'eud_a': [(i, new_eud_a) for i in range(row_count) if i in include],
             'gamma_50': [(i, new_gamma_50) for i in range(row_count) if i in include],
             'td_tcd': [(i, new_td_tcd) for i in range(row_count) if i in include]}

    sources.rad_bio.patch(patch)

    update_eud()


def update_eud():
    uid_roi_list = ["%s_%s" % (uid, sources.dvhs.data['roi_name'][i]) for i, uid in enumerate(sources.dvhs.data['uid'])]

    eud, ntcp_tcp = [], []
    for i, uid in enumerate(sources.rad_bio.data['uid']):
        uid_roi = "%s_%s" % (uid, sources.rad_bio.data['roi_name'][i])
        source_index = uid_roi_list.index(uid_roi)
        dvh = sources.dvhs.data['y'][source_index]
        a = sources.rad_bio.data['eud_a'][i]
        try:
            eud.append(round(calc_eud(dvh, a), 2))
        except:
            eud.append(0)
        td_tcd = sources.rad_bio.data['td_tcd'][i]
        gamma_50 = sources.rad_bio.data['gamma_50'][i]
        if eud[-1] > 0:
            ntcp_tcp.append(1 / (1 + (td_tcd / eud[-1]) ** (4. * gamma_50)))
        else:
            ntcp_tcp.append(0)

    sources.rad_bio.patch({'eud': [(i, j) for i, j in enumerate(eud)],
                           'ntcp_tcp': [(i, j) for i, j in enumerate(ntcp_tcp)]})

    update_eud_in_correlation()
    categories = list(correlation.data[N[0]])
    categories.sort()
    corr_chart_x.options = [''] + categories
    corr_chart_y.options = [''] + categories
    update_corr_chart()
    if time_series.y_axis.value in {'EUD', 'NTCP/TCP'}:
        time_series.update_plot()


def emami_selection(attr, old, new):
    if new:
        row_index = min(new)
        rad_bio_eud_a_input.value = str(sources.emami.data['eud_a'][row_index])
        rad_bio_gamma_50_input.value = str(sources.emami.data['gamma_50'][row_index])
        rad_bio_td_tcd_input.value = str(sources.emami.data['td_tcd'][row_index])


def update_endpoints_in_correlation():

    correlation.update_or_add_endpoints_to_correlation()

    categories = list(correlation.data['1'])
    categories.sort()
    corr_chart_x.options = [''] + categories
    corr_chart_y.options = [''] + categories

    correlation.validate_data()
    correlation.update_correlation_matrix()
    update_corr_chart()


def update_eud_in_correlation():

    # Get data from EUD data
    uid_roi_list = ["%s_%s" % (uid, sources.dvhs.data['roi_name'][i]) for i, uid in enumerate(sources.dvhs.data['uid'])]
    temp_keys = ['eud', 'ntcp_tcp', 'uid', 'mrn']
    temp = {n: {tk: [] for tk in temp_keys} for n in N}
    for i, uid in enumerate(sources.rad_bio.data['uid']):
        uid_roi = "%s_%s" % (uid, sources.rad_bio.data['roi_name'][i])
        source_index = uid_roi_list.index(uid_roi)
        group = sources.dvhs.data['group'][source_index]
        for n in N:
            if group in {'Group %s' % n, 'Group 1 & 2'}:
                temp[n]['eud'].append(sources.rad_bio.data['eud'][i])
                temp[n]['ntcp_tcp'].append(sources.rad_bio.data['ntcp_tcp'][i])
                temp[n]['uid'].append(uid)
                temp[n]['mrn'].append(sources.dvhs.data['mrn'][source_index])

    for n in N:
        correlation.data[n]['EUD'] = {'uid': temp[n]['uid'], 'mrn': temp[n]['mrn'],
                                 'data': temp[n]['eud'], 'units': 'Gy'}
        correlation.data[n]['NTCP/TCP'] = {'uid': temp[n]['uid'], 'mrn': temp[n]['mrn'],
                                      'data': temp[n]['ntcp_tcp'], 'units': ''}

    # declare space to tag variables to be used for multi variable regression
    for n in N:
        for key, value in listitems(CORRELATION[n]):
            correlation.data[n][key]['include'] = [False] * len(value['uid'])

    categories = list(correlation.data['1'])
    categories.sort()
    corr_chart_x.options = [''] + categories
    corr_chart_y.options = [''] + categories

    correlation.validate_data()
    correlation.update_correlation_matrix()
    update_corr_chart()


def update_corr_chart_ticker_x(attr, old, new):
    if MULTI_VAR_REG_VARS[corr_chart_x.value]:
        corr_chart_x_include.active = [0]
    else:
        corr_chart_x_include.active = []
    update_corr_chart()


def update_corr_chart_ticker_y(attr, old, new):
    update_corr_chart()


def update_corr_chart():
    if corr_chart_x.value and corr_chart_y.value:
        x_units = CORRELATION['1'][corr_chart_x.value]['units']
        y_units = CORRELATION['1'][corr_chart_y.value]['units']

        data = {'x': {n: CORRELATION[n][corr_chart_x.value]['data'] for n in N},
                'y': {n: CORRELATION[n][corr_chart_y.value]['data'] for n in N},
                'mrn': {n: CORRELATION[n][corr_chart_x.value]['mrn'] for n in N}}

        if x_units:
            if corr_chart_x.value.startswith('DVH Endpoint'):
                label = corr_chart_x.value[14:]
                label = {'D': 'Dose to ', 'V': 'Volume of '}[label[0]] + corr_chart_x.value.split('_')[1]
                if '%' in label:
                    label = label + {'D': ' ROI Volume', 'V': ' Rx Dose'}[label[0]]
                corr_chart.xaxis.axis_label = "%s (%s)" % (label, x_units)
            else:
                corr_chart.xaxis.axis_label = "%s (%s)" % (corr_chart_x.value, x_units)
        else:
            corr_chart.xaxis.axis_label = corr_chart_x.value.replace('/', ' or ')
        if y_units:
            if corr_chart_y.value.startswith('DVH Endpoint'):
                label = corr_chart_y.value[14:]
                label = {'D': 'Dose to ', 'V': 'Volume of '}[label[0]] + corr_chart_y.value.split('_')[1]
                if '%' in label:
                    label = label + {'D': ' ROI Volume', 'V': ' Rx Dose'}[label[0]]
                corr_chart.yaxis.axis_label = "%s (%s)" % (label, y_units)
            else:
                corr_chart.yaxis.axis_label = "%s (%s)" % (corr_chart_y.value, y_units)
        else:
            corr_chart.yaxis.axis_label = corr_chart_y.value.replace('/', ' or ')

        for n in N:
            getattr(sources, 'corr_chart_%s' % n).data = {v: data[v][n] for v in list(data)}

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
                getattr(sources, 'corr_trend_%s' % n).data = {'x': x_trend, 'y': y_trend}
            else:
                group_stats[n] = [''] * 6
                clear_source_data('corr_trend_%s' % n)

        sources.corr_chart_stats.data = {'stat': sources.CORR_CHART_STATS_ROW_NAMES,
                                         'group_1': group_stats['1'],
                                         'group_2': group_stats['2']}
    else:
        sources.corr_chart_stats.data = {'stat': sources.CORR_CHART_STATS_ROW_NAMES,
                                         'group_1': [''] * 6,
                                         'group_2': [''] * 6}
        for n in N:
            for k in ['corr_chart', 'corr_trend']:
                clear_source_data('%s_%s' % (k, n))


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
    if new and not MULTI_VAR_REG_VARS[corr_chart_x.value]:
        MULTI_VAR_REG_VARS[corr_chart_x.value] = True
    if not new and MULTI_VAR_REG_VARS[corr_chart_x.value]:
        clear_source_selection('multi_var_include')
        MULTI_VAR_REG_VARS[corr_chart_x.value] = False

    included_vars = [key for key, value in listitems(MULTI_VAR_REG_VARS) if value]
    included_vars.sort()
    sources.multi_var_include.data = {'var_name': included_vars}


def multi_var_linear_regression():
    print(str(datetime.now()), 'Performing multivariable regression', sep=' ')

    included_vars = [key for key in list(CORRELATION['1']) if MULTI_VAR_REG_VARS[key]]
    included_vars.sort()

    for n in N:
        if time_series.current_dvh_group[n]:
            x = []
            x_count = len(CORRELATION[n][list(CORRELATION[n])[0]]['data'])
            for i in range(x_count):
                current_x = []
                for k in included_vars:
                    current_x.append(CORRELATION[n][k]['data'][i])
                x.append(current_x)
            x = sm.add_constant(x)  # explicitly add constant to calculate intercept
            y = CORRELATION[n][corr_chart_y.value]['data']

            fit = sm.OLS(y, x).fit()

            coeff = fit.params
            coeff_p = fit.pvalues
            r_sq = fit.rsquared
            model_p = fit.f_pvalue

            coeff_str = ["%0.3E" % i for i in coeff]
            coeff_p_str = ["%0.3f" % i for i in coeff_p]
            r_sq_str = ["%0.3f" % r_sq]
            model_p_str = ["%0.3f" % model_p]

            residual_chart.yaxis.axis_label = "Residual (%s)" % CORRELATION[n][corr_chart_y.value]['units']

            getattr(sources, 'multi_var_coeff_results_%s' % n).data = {'var_name': ['Constant'] + included_vars,
                                                                       'coeff': coeff.tolist(), 'coeff_str': coeff_str,
                                                                       'p': coeff_p.tolist(), 'p_str': coeff_p_str}
            getattr(sources, 'multi_var_model_results_%s' % n).data = {'model_p': [model_p], 'model_p_str': model_p_str,
                                                                       'r_sq': [r_sq], 'r_sq_str': r_sq_str,
                                                                       'y_var': [corr_chart_y.value]}
            getattr(sources, 'residual_chart_%s' % n).data = {'x': range(1, x_count + 1),
                                                              'y': fit.resid.tolist(),
                                                              'mrn': CORRELATION[n][corr_chart_y.value]['mrn'],
                                                              'db_value': CORRELATION[n][corr_chart_y.value]['data']}
        else:
            for k in ['multi_var_coeff_results', 'multi_var_model_results', 'residual_chart']:
                clear_source_data('%s_%s' (k, n))


def multi_var_include_selection(attr, old, new):
    row_index = sources.multi_var_include.selected.indices[0]
    corr_chart_x.value = sources.multi_var_include.data['var_name'][row_index]


def update_source_endpoint_view_selection(attr, old, new):
    if new:
        sources.endpoint_view.selected.indices = new


def update_dvh_table_selection(attr, old, new):
    if new:
        sources.dvhs.selected.indices = new


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
        sources.dvhs.patch(patches)


def calculate_review_dvh():
    global temp_dvh_info, dvh_review_rois, x, y, CURRENT_DVH

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
        if not sources.dvhs.data['x']:
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

    sources.dvhs.patch(patches)

    update_source_endpoint_calcs()


def select_reviewed_dvh_ticker(attr, old, new):
    calculate_review_dvh()


def review_rx_ticker(attr, old, new):
    if radio_group_dose.active == 0:
        sources.dvhs.patch({'rx_dose': [(0, round(float(review_rx.value), 2))]})
    else:
        calculate_review_dvh()


def radio_group_ticker(attr, old, new):
    if sources.dvhs.data['x'] != '':
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


def update_planning_data_selections(uids):
    global ALLOW_SOURCE_UPDATE

    ALLOW_SOURCE_UPDATE = False
    for k in ['rxs', 'plans', 'beams']:
        src = getattr(sources, k)
        src.selected.indices = [i for i, j in enumerate(src.data['uid']) if j in uids]

    ALLOW_SOURCE_UPDATE = True


class SourceSelection:
    def __init__(self, table):
        self.table = table

    def ticker(self, attr, old, new):
        if ALLOW_SOURCE_UPDATE:
            src = getattr(sources, self.table)
            uids = list(set([src.data['uid'][i] for i in new]))
            update_planning_data_selections(uids)


source_selection = {s: SourceSelection(s) for s in ['rxs', 'plans', 'beams']}


def clear_source_data(source_key):
    src = getattr(sources, source_key)
    src.data = {k: [] for k in list(src.data)}


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Selection Filter UI objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
category_options = list(selector_categories)
category_options.sort()

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
selection_filter_data_table = DataTable(source=sources.selectors,
                                        columns=columns.selection_filter, width=1000, height=150, index_position=None)
sources.selectors.selected.on_change('indices', update_selector_row_on_selection)
update_selector_source()

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Range Filter UI objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
category_options = list(range_categories)
category_options.sort()

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
text_min = TextInput(value='', title='Min: ', width=150)
text_min.on_change('value', min_text_ticker)
text_max = TextInput(value='', title='Max: ', width=150)
text_max.on_change('value', max_text_ticker)

# Misc
delete_range_row_button = Button(label="Delete", button_type="warning", width=100)
delete_range_row_button.on_click(delete_range_row)
group_range = CheckboxButtonGroup(labels=["Group 1", "Group 2"], active=[0], width=180)
group_range.on_change('active', ensure_range_group_is_assigned)
range_not_operator_checkbox = CheckboxGroup(labels=['Not'], active=[])
range_not_operator_checkbox.on_change('active', range_not_operator_ticker)

# Selector Category table
range_filter_data_table = DataTable(source=sources.ranges,
                                    columns=columns.range_filter, width=1000, height=150, index_position=None)
sources.ranges.selected.on_change('indices', update_range_row_on_selection)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# DVH Endpoint Filter UI objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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

# endpoint  table
ep_data_table = DataTable(source=sources.endpoint_defs, columns=columns.ep_data, width=300, height=150)

sources.endpoint_defs.selected.on_change('indices', update_ep_row_on_selection)

query_button = Button(label="Query", button_type="success", width=100)
query_button.on_click(update_data)

# define Download button and call download.js on click
menu = [("All Data", "all"), ("Lite", "lite"), ("Only DVHs", "dvhs"), ("Anonymized DVHs", "anon_dvhs")]
download_dropdown = Dropdown(label="Download", button_type="default", menu=menu, width=100)
download_dropdown.callback = CustomJS(args=dict(source=sources.dvhs,
                                                source_rxs=sources.rxs,
                                                source_plans=sources.plans,
                                                source_beams=sources.beams),
                                      code=open(join(dirname(__file__), "download.js")).read())


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
dvh_plots.xaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
dvh_plots.yaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
dvh_plots.xaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
dvh_plots.yaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
dvh_plots.yaxis.axis_label_text_baseline = "bottom"
dvh_plots.lod_factor = options.LOD_FACTOR  # level of detail during interactive plot events

# Add statistical plots to figure
stats_median_1 = dvh_plots.line('x', 'median', source=sources.stats_1,
                                line_width=options.STATS_1_MEDIAN_LINE_WIDTH, color=options.GROUP_1_COLOR,
                                line_dash=options.STATS_1_MEDIAN_LINE_DASH, alpha=options.STATS_1_MEDIAN_ALPHA)
stats_mean_1 = dvh_plots.line('x', 'mean', source=sources.stats_1,
                              line_width=options.STATS_1_MEAN_LINE_WIDTH, color=options.GROUP_1_COLOR,
                              line_dash=options.STATS_1_MEAN_LINE_DASH, alpha=options.STATS_1_MEAN_ALPHA)
stats_median_2 = dvh_plots.line('x', 'median', source=sources.stats_2,
                                line_width=options.STATS_2_MEDIAN_LINE_WIDTH, color=options.GROUP_2_COLOR,
                                line_dash=options.STATS_2_MEDIAN_LINE_DASH, alpha=options.STATS_2_MEDIAN_ALPHA)
stats_mean_2 = dvh_plots.line('x', 'mean', source=sources.stats_2,
                              line_width=options.STATS_2_MEAN_LINE_WIDTH, color=options.GROUP_2_COLOR,
                              line_dash=options.STATS_2_MEAN_LINE_DASH, alpha=options.STATS_2_MEAN_ALPHA)

# Add all DVHs, but hide them until selected
dvh_plots.multi_line('x', 'y', source=sources.dvhs,
                     selection_color='color', line_width=options.DVH_LINE_WIDTH, alpha=0,
                     line_dash=options.DVH_LINE_DASH, nonselection_alpha=0, selection_alpha=1)

# Shaded region between Q1 and Q3
iqr_1 = dvh_plots.patch('x_patch', 'y_patch', source=sources.patch_1, alpha=options.IQR_1_ALPHA, color=options.GROUP_1_COLOR)
iqr_2 = dvh_plots.patch('x_patch', 'y_patch', source=sources.patch_2, alpha=options.IQR_2_ALPHA, color=options.GROUP_2_COLOR)

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
data_table = DataTable(source=sources.dvhs, columns=columns.dvhs, width=1200, editable=True, index_position=None)
data_table_beams = DataTable(source=sources.beams, columns=columns.beams, width=1300, editable=True, index_position=None)
data_table_beams2 = DataTable(source=sources.beams, columns=columns.beams2, width=1300, editable=True, index_position=None)
data_table_plans = DataTable(source=sources.plans, columns=columns.plans, width=1300, editable=True, index_position=None)
data_table_rxs = DataTable(source=sources.rxs, columns=columns.rxs, width=1300, editable=True, index_position=None)
data_table_endpoints = DataTable(source=sources.endpoint_view, columns=columns.endpoints, width=1200,
                                 editable=True, index_position=None)

download_endpoints_button = Button(label="Download Endpoints", button_type="default", width=150)
download_endpoints_button.callback = CustomJS(args=dict(source=sources.endpoint_calcs),
                                              code=open(join(dirname(__file__), "download_endpoints.js")).read())


# Listen for changes to source selections
for s in ['rxs', 'plans', 'beams']:
    getattr(sources, s).selected.on_change('indices', source_selection[s].ticker)
sources.dvhs.selected.on_change('indices', update_source_endpoint_view_selection)
sources.endpoint_view.selected.on_change('indices', update_dvh_table_selection)
sources.emami.selected.on_change('indices', emami_selection)

# Control Chart layout
tools = "pan,wheel_zoom,box_zoom,reset,crosshair,save"
corr_chart = figure(plot_width=1050, plot_height=400, tools=tools, logo=None, active_drag="box_zoom")
corr_chart.xaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
corr_chart.yaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
corr_chart.xaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
corr_chart.yaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
corr_chart.min_border_left = min_border
corr_chart.min_border_bottom = min_border
corr_chart_data_1 = corr_chart.circle('x', 'y', size=options.REGRESSION_1_CIRCLE_SIZE, color=options.GROUP_1_COLOR,
                                      alpha=options.REGRESSION_1_ALPHA, source=sources.corr_chart_1)
corr_chart_data_2 = corr_chart.circle('x', 'y', size=options.REGRESSION_2_CIRCLE_SIZE, color=options.GROUP_2_COLOR,
                                      alpha=options.REGRESSION_2_ALPHA, source=sources.corr_chart_2)
corr_chart_trend_1 = corr_chart.line('x', 'y', color=options.GROUP_1_COLOR,
                                     line_width=options.REGRESSION_1_LINE_WIDTH,
                                     line_dash=options.REGRESSION_1_LINE_DASH,
                                     source=sources.corr_trend_1)
corr_chart_trend_2 = corr_chart.line('x', 'y', color=options.GROUP_2_COLOR,
                                     line_width=options.REGRESSION_2_LINE_WIDTH,
                                     line_dash=options.REGRESSION_1_LINE_DASH,
                                     source=sources.corr_trend_2)
corr_chart.add_tools(HoverTool(show_arrow=True, tooltips=[('MRN', '@mrn'),
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

sources.multi_var_include.selected.on_change('indices', multi_var_include_selection)

# Setup axis normalization radio buttons
radio_group_dose = RadioGroup(labels=["Absolute Dose", "Relative Dose (Rx)"], active=0, width=200)
radio_group_dose.on_change('active', radio_group_ticker)
radio_group_volume = RadioGroup(labels=["Absolute Volume", "Relative Volume"], active=1, width=200)
radio_group_volume.on_change('active', radio_group_ticker)

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

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Radbio
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
rad_bio_eud_a_input = TextInput(value='', title='EUD a-value:', width=150)
rad_bio_gamma_50_input = TextInput(value='', title=u"\u03b3_50:", width=150)
rad_bio_td_tcd_input = TextInput(value='', title='TD_50 or TCD_50:', width=150)
rad_bio_apply_button = Button(label="Apply parameters", button_type="primary", width=150)
rad_bio_apply_filter = CheckboxButtonGroup(labels=["Group 1", "Group 2", "Selected"], active=[0], width=300)

rad_bio_apply_button.on_click(rad_bio_apply)

data_table_rad_bio = DataTable(source=sources.rad_bio, columns=columns.rad_bio, editable=False, width=1100)

data_table_emami = DataTable(source=sources.emami, columns=columns.emami, editable=False, width=1100)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ROI Viewer
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def update_roi_viewer_mrn():
    options = [mrn for mrn in sources.plans.data['mrn']]
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
        for i in range(1, 6):
            roi_viewer_roi_select[str(i)].options = []
            roi_viewer_roi_select[str(i)].value = ''

    else:
        # Clear out additional ROIs since current values may not exist in new patient set
        for i in range(2, 6):
            roi_viewer_roi_select[str(i)].value = ''

        options = []
        for i in range(len(sources.plans.data['mrn'])):
            if sources.plans.data['mrn'][i] == new:
                options.append(sources.plans.data['sim_study_date'][i])
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
        for i in range(len(sources.plans.data['mrn'])):
            if sources.plans.data['mrn'][i] == roi_viewer_mrn_select.value and \
                            sources.plans.data['sim_study_date'][i] == roi_viewer_study_date_select.value:
                options.append(sources.plans.data['uid'][i])
        roi_viewer_uid_select.options = options
        roi_viewer_uid_select.value = options[0]


def roi_viewer_uid_ticker(attr, old, new):
    update_roi_viewer_rois()


def roi_viewer_slice_ticker(attr, old, new):
    for i in range(1, 6):
        roi_number = str(i)
        z = roi_viewer_slice_select.value
        if z in list(ROI_VIEWER_DATA[roi_number]):
            getattr(sources, 'roi%s_viewer' % roi_number).data = ROI_VIEWER_DATA[roi_number][z]
        else:
            clear_source_data('roi%s_viewer' % roi_number)
    clear_source_data('tv')


def update_roi_viewer_slice():
    options = list(ROI_VIEWER_DATA['1'])
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

    roi_viewer_roi_select['1'].options = options
    # default to an external like ROI if found
    if 'external' in options:
        roi_viewer_roi_select['1'].value = 'external'
    elif 'ext' in options:
        roi_viewer_roi_select['1'].value = 'ext'
    elif 'body' in options:
        roi_viewer_roi_select['1'].value = 'body'
    elif 'skin' in options:
        roi_viewer_roi_select['1'].value = 'skin'
    else:
        roi_viewer_roi_select['1'].value = options[0]

    for i in range(2, 6):
        roi_viewer_roi_select[str(i)].options = [''] + options
        roi_viewer_roi_select[str(i)].value = ''


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
    if z in list(tv_data) and not sources.tv.data['x']:
        sources.tv.data = tv_data[z]
    else:
        clear_source_data('tv')


def roi_viewer_wheel_event(event):
    if roi_viewer_scrolling.active:
        if event.delta > 0:
            roi_viewer_go_to_next_slice()
        elif event.delta < 0:
            roi_viewer_go_to_previous_slice()


roi_colors = plot_colors.cnames.keys()
roi_colors.sort()
roi_viewer_options = [''] + sources.dvhs.data['mrn']
roi_viewer_mrn_select = Select(value='', options=roi_viewer_options, width=200, title='MRN')
roi_viewer_study_date_select = Select(value='', options=[''], width=200, title='Sim Study Date')
roi_viewer_uid_select = Select(value='', options=[''], width=400, title='Study Instance UID')
roi_viewer_roi_select = {str(i): Select(value='', options=[''], width=200, title='ROI %s Name' % i) for i in range(1, 6)}
colors = ['blue', 'green', 'red', 'orange', 'lightgreen']
roi_viewer_roi_select_color = {str(i): Select(value=colors[i-1], options=roi_colors, width=150, title='ROI %s Color' % i) for i in range(1, 6)}
roi_viewer_slice_select = Select(value='', options=[''], width=200, title='Slice: z = ')
roi_viewer_previous_slice = Button(label="<", button_type="primary", width=50)
roi_viewer_next_slice = Button(label=">", button_type="primary", width=50)
roi_viewer_flip_x_axis_button = Button(label='Flip X-Axis', button_type='primary', width=100)
roi_viewer_flip_y_axis_button = Button(label='Flip Y-Axis', button_type='primary', width=100)
roi_viewer_plot_tv_button = Button(label='Plot TV', button_type='primary', width=100)

roi_viewer_mrn_select.on_change('value', roi_viewer_mrn_ticker)
roi_viewer_study_date_select.on_change('value', roi_viewer_study_date_ticker)
roi_viewer_uid_select.on_change('value', roi_viewer_uid_ticker)


class RoiViewerRoiTicker:
    def __init__(self, roi_number, select):
        global ROI_VIEWER_DATA

        self.roi_number = str(roi_number)
        self.select = select

    def ticker(self, attr, old, new):
        ROI_VIEWER_DATA[self.roi_number] = update_roi_viewer_data(self.select.value)
        if self.roi_number == '1':
            update_roi_viewer_slice()
        else:
            z = roi_viewer_slice_select.value
            if z in list(ROI_VIEWER_DATA[self.roi_number]):
                getattr(sources, 'roi%s_viewer' % self.roi_number).data = ROI_VIEWER_DATA[self.roi_number][z]
            else:
                clear_source_data('roi%s_viewer' % self.roi_number)


roi_viewer_roi_ticker = {str(i): RoiViewerRoiTicker(i, roi_viewer_roi_select[str(i)]) for i in range(1, 6)}

for i in range(1, 6):
    roi_viewer_roi_select[str(i)].on_change('value', roi_viewer_roi_ticker[str(i)].ticker)


class RoiViewerRoiColorTicker:
    def __init__(self, roi_number):
        self.roi_number = str(roi_number)

    def ticker(self, attr, old, new):
        roi_viewer_patch[self.roi_number].glyph.fill_color = new
        roi_viewer_patch[self.roi_number].glyph.line_color = new


roi_viewer_roi_color_ticker = {str(i): RoiViewerRoiColorTicker(i) for i in range(1, 6)}

for i in range(1, 6):
    roi_viewer_roi_select_color[str(i)].on_change('value', roi_viewer_roi_color_ticker[str(i)].ticker)

roi_viewer_slice_select.on_change('value', roi_viewer_slice_ticker)
roi_viewer_previous_slice.on_click(roi_viewer_go_to_previous_slice)
roi_viewer_next_slice.on_click(roi_viewer_go_to_next_slice)
roi_viewer_flip_x_axis_button.on_click(roi_viewer_flip_x_axis)
roi_viewer_flip_y_axis_button.on_click(roi_viewer_flip_y_axis)
roi_viewer_plot_tv_button.on_click(roi_viewer_plot_tv)

roi_viewer = figure(plot_width=825, plot_height=600, logo=None, match_aspect=True,
                    tools="pan,wheel_zoom,reset,crosshair,save")
roi_viewer.xaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
roi_viewer.yaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
roi_viewer.xaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
roi_viewer.yaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
roi_viewer.min_border_left = min_border
roi_viewer.min_border_bottom = min_border
roi_viewer.y_range.flipped = True
roi_viewer_patch = {str(i): roi_viewer.patch('x', 'y', source=getattr(sources, 'roi%s_viewer' % i),
                                             color=colors[i-1], alpha=0.5) for i in range(1, 6)}

roi_viewer.patch('x', 'y', source=sources.tv, color='black', alpha=0.5)
roi_viewer.xaxis.axis_label = "Lateral DICOM Coordinate (mm)"
roi_viewer.yaxis.axis_label = "Anterior/Posterior DICOM Coordinate (mm)"
roi_viewer.on_event(events.MouseWheel, roi_viewer_wheel_event)
roi_viewer_scrolling = CheckboxGroup(labels=["Enable Slice Scrolling with Mouse Wheel"], active=[])


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Control Chart (for real)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
tools = "pan,wheel_zoom,box_zoom,lasso_select,poly_select,reset,crosshair,save"
residual_chart = figure(plot_width=1050, plot_height=400, tools=tools, logo=None,
                        active_drag="box_zoom")
residual_chart.xaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
residual_chart.yaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
residual_chart.xaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
residual_chart.yaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
# residual_chart.min_border_left = min_border
residual_chart.min_border_bottom = min_border
residual_chart.xaxis.axis_label = 'Patient #'
residual_chart_data_1 = residual_chart.circle('x', 'y', size=options.REGRESSION_1_CIRCLE_SIZE,
                                              color=options.GROUP_1_COLOR, alpha=options.REGRESSION_1_ALPHA,
                                              source=sources.residual_chart_1)
residual_chart_data_2 = residual_chart.circle('x', 'y', size=options.REGRESSION_2_CIRCLE_SIZE,
                                              color=options.GROUP_2_COLOR, alpha=options.REGRESSION_2_ALPHA,
                                              source=sources.residual_chart_2)
residual_chart.add_tools(HoverTool(show_arrow=True,
                                   tooltips=[('ID', '@mrn'),
                                             ('Residual', '@y'),
                                             ('Actual', '@db_value')]))
legend_residual_chart = Legend(items=[("Group 1", [residual_chart_data_1]),
                                      ("Group 2", [residual_chart_data_2])],
                               location=(25, 0))
residual_chart.add_layout(legend_residual_chart, 'right')
residual_chart.legend.click_policy = "hide"

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Layout objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!
layout_query = column(row(custom_title['1']['query'], Spacer(width=50), custom_title['2']['query'],
                          Spacer(width=50), query_button, Spacer(width=50), download_dropdown),
                      Div(text="<b>Query by Categorical Data</b>", width=1000),
                      add_selector_row_button,
                      row(selector_row, Spacer(width=10), select_category1, select_category2, group_selector,
                          delete_selector_row_button, Spacer(width=10), selector_not_operator_checkbox),
                      selection_filter_data_table,
                      Div(text="<hr>", width=1050),
                      Div(text="<b>Query by Numerical Data</b>", width=1000),
                      add_range_row_button,
                      row(range_row, Spacer(width=10), select_category, text_min, Spacer(width=30),
                          text_max, Spacer(width=30), group_range,
                          delete_range_row_button, Spacer(width=10), range_not_operator_checkbox),
                      range_filter_data_table)

if options.LITE_VIEW:
    layout_dvhs = column(row(radio_group_dose, radio_group_volume),
                         add_endpoint_row_button,
                         row(ep_row, Spacer(width=10), select_ep_type, ep_text_input, Spacer(width=20),
                             ep_units_in, delete_ep_row_button, Spacer(width=50), download_endpoints_button),
                         ep_data_table)
else:
    layout_dvhs = column(row(custom_title['1']['dvhs'], Spacer(width=50), custom_title['2']['dvhs']),
                         row(radio_group_dose, radio_group_volume),
                         row(select_reviewed_mrn, select_reviewed_dvh, review_rx),
                         dvh_plots,
                         Div(text="<b>DVHs</b>", width=1200),
                         data_table,
                         Div(text="<hr>", width=1050),
                         Div(text="<b>Define Endpoints</b>", width=1000),
                         add_endpoint_row_button,
                         row(ep_row, Spacer(width=10), select_ep_type, ep_text_input, Spacer(width=20),
                             ep_units_in, delete_ep_row_button, Spacer(width=50), download_endpoints_button),
                         ep_data_table,
                         Div(text="<b>DVH Endpoints</b>", width=1200),
                         data_table_endpoints)

layout_rad_bio = column(row(custom_title['1']['rad_bio'], Spacer(width=50), custom_title['2']['rad_bio']),
                        Div(text="<b>Published EUD Parameters from Emami"
                                 " et. al. for 1.8-2.0Gy fractions</b> (Click to apply)",
                            width=600),
                        data_table_emami,
                        Div(text="<b>Applied Parameters:</b>", width=150),
                        row(rad_bio_eud_a_input, Spacer(width=50),
                            rad_bio_gamma_50_input, Spacer(width=50), rad_bio_td_tcd_input, Spacer(width=50),
                            rad_bio_apply_filter, Spacer(width=50), rad_bio_apply_button),
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
                           row(roi_viewer_mrn_select, roi_viewer_study_date_select, roi_viewer_uid_select),
                           Div(text="<hr>", width=800),
                           row(roi_viewer_roi_select['1'], roi_viewer_roi_select_color['1'], roi_viewer_slice_select,
                               roi_viewer_previous_slice, roi_viewer_next_slice),
                           Div(text="<hr>", width=800),
                           row(roi_viewer_roi_select['2'], roi_viewer_roi_select['3'],
                               roi_viewer_roi_select['4'], roi_viewer_roi_select['5']),
                           row(roi_viewer_roi_select_color['2'], roi_viewer_roi_select_color['3'],
                               roi_viewer_roi_select_color['4'], roi_viewer_roi_select_color['5']),
                           row(Div(text="<b>NOTE:</b> Axis flipping requires a figure reset "
                                        "(Click the circular double-arrow)", width=1025)),
                           row(roi_viewer_flip_x_axis_button, roi_viewer_flip_y_axis_button,
                               roi_viewer_plot_tv_button),
                           row(roi_viewer_scrolling),
                           row(roi_viewer),
                           row(Spacer(width=1000, height=100)))

layout_correlation_matrix = column(row(custom_title['1']['correlation'], Spacer(width=50),
                                       custom_title['2']['correlation']),
                                   correlation.download_corr_fig,
                                   row(Div(text="<b>Sample Sizes</b>", width=100), correlation.fig_text_1,
                                       correlation.fig_text_2),
                                   row(correlation.fig, correlation.fig_include, correlation.fig_include_2))

layout_regression = column(row(custom_title['1']['regression'], Spacer(width=50), custom_title['2']['regression']),
                           row(column(corr_chart_x_include,
                                      row(corr_chart_x_prev, corr_chart_x_next, Spacer(width=10), corr_chart_x),
                                      row(corr_chart_y_prev, corr_chart_y_next, Spacer(width=10), corr_chart_y)),
                               Spacer(width=10, height=175), data_table_corr_chart,
                               Spacer(width=10, height=175), data_table_multi_var_include),
                           corr_chart,
                           Div(text="<hr>", width=1050),
                           corr_chart_do_reg_button,
                           residual_chart,
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
