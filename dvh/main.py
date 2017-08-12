#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
main program for Bokeh server
Created on Sun Apr 21 2017
@author: Dan Cutright, PhD
"""


from __future__ import print_function
from analysis_tools import DVH, get_study_instance_uids, calc_eud, get_eud_a_values
from utilities import Temp_DICOM_FileSet, get_planes_from_string, get_union, get_roi_coordinates_from_planes
from sql_connector import DVH_SQL
from sql_to_python import QuerySQL
import numpy as np
import itertools
from datetime import datetime
from os.path import dirname, join
from bokeh.layouts import layout, column, row
from bokeh.models import ColumnDataSource, Legend, CustomJS, HoverTool, DatetimeTickFormatter
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.palettes import Colorblind8 as palette
from bokeh.models.widgets import Select, Button, Div, TableColumn, DataTable, Panel, Tabs, \
    NumberFormatter, RadioButtonGroup, TextInput, RadioGroup, CheckboxButtonGroup, Dropdown
from dicompylercore import dicomparser, dvhcalc

# Declare variables
colors = itertools.cycle(palette)
current_dvh = []
current_dvh_group_1 = []
current_dvh_group_2 = []
update_warning = True
query_row = []
query_row_type = []
endpoint_columns = {}
x = []
y = []
uids_1, uids_2 = [], []
eud_a_values = get_eud_a_values()
widget_row_start = 0

for i in range(0, 10):
    endpoint_columns[i] = ''

temp_dvh_info = Temp_DICOM_FileSet()
dvh_review_mrns = temp_dvh_info.mrn
if dvh_review_mrns[0] != '':
    dvh_review_rois = temp_dvh_info.get_roi_names(dvh_review_mrns[0]).values()
    dvh_review_mrns.append('')

else:
    dvh_review_rois = ['']

roi_viewer_data = {}
roi2_viewer_data = {}
roi3_viewer_data = {}
roi4_viewer_data = {}
tv_data = {}

# Initialize ColumnDataSource variables
source = ColumnDataSource(data=dict(color=[], x=[], y=[], mrn=[],
                                    ep1=[], ep2=[], ep3=[], ep4=[], ep5=[], ep6=[], ep7=[], ep8=[]))
source_patch_1 = ColumnDataSource(data=dict(x_patch=[], y_patch=[]))
source_patch_2 = ColumnDataSource(data=dict(x_patch=[], y_patch=[]))
source_stats_1 = ColumnDataSource(data=dict(x=[], min=[], q1=[], mean=[], median=[], q3=[], max=[]))
source_stats_2 = ColumnDataSource(data=dict(x=[], min=[], q1=[], mean=[], median=[], q3=[], max=[]))
source_beams = ColumnDataSource(data=dict())
source_plans = ColumnDataSource(data=dict())
source_rxs = ColumnDataSource(data=dict())
source_endpoint_names = ColumnDataSource(data=dict(ep1=[], ep2=[], ep3=[], ep4=[], ep5=[], ep6=[], ep7=[], ep8=[]))
source_endpoints = ColumnDataSource(data=dict())
source_time = ColumnDataSource(data=dict(x=[], y=[], mrn=[], color=[]))
source_time_trend = ColumnDataSource(data=dict(x=[], y=[], w=[], mrn=[]))
source_time_collapsed = ColumnDataSource(data=dict(x=[], y=[], w=[], mrn=[]))
source_time_bound = ColumnDataSource(data=dict(x=[], upper=[], avg=[], lower=[], mrn=[]))
source_roi_viewer = ColumnDataSource(data=dict(x=[], y=[]))
source_roi2_viewer = ColumnDataSource(data=dict(x=[], y=[]))
source_roi3_viewer = ColumnDataSource(data=dict(x=[], y=[]))
source_roi4_viewer = ColumnDataSource(data=dict(x=[], y=[]))
source_tv = ColumnDataSource(data=dict(x=[], y=[]))


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
                    'Distance to PTV Min': {'var_name': 'dist_to_ptv_min', 'table': 'DVHs', 'units': 'cm', 'source': source},
                    'Distance to PTV Mean': {'var_name': 'dist_to_ptv_mean', 'table': 'DVHs', 'units': 'cm', 'source': source},
                    'Distance to PTV Median': {'var_name': 'dist_to_ptv_median', 'table': 'DVHs', 'units': 'cm', 'source': source},
                    'Distance to PTV Max': {'var_name': 'dist_to_ptv_max', 'table': 'DVHs', 'units': 'cm', 'source': source},
                    'Scan Spots': {'var_name': 'scan_spot_count', 'table': 'Beams', 'units': '', 'source': source_beams},
                    'Beam MU per deg': {'var_name': 'beam_mu_per_deg', 'table': 'Beams', 'units': '', 'source': source_beams},
                    'Beam MU per control point': {'var_name': 'beam_mu_per_cp', 'table': 'Beams', 'units': '', 'source': source_beams}}


# Functions that add widget rows
def button_add_selector_row():
    global query_row_type
    old_label = main_add_selector_button.label
    old_type = main_add_selector_button.button_type
    main_add_selector_button.label = 'Updating Layout...'
    main_add_selector_button.button_type = 'warning'
    query_row.append(SelectorRow())
    layout_query.children.insert(widget_row_start + len(query_row_type), query_row[-1].row)
    query_row_type.append('selector')
    update_update_button_status()
    main_add_selector_button.label = old_label
    main_add_selector_button.button_type = old_type


def button_add_range_row():
    global query_row_type
    old_label = main_add_range_button.label
    old_type = main_add_range_button.button_type
    main_add_range_button.label = 'Updating Layout...'
    main_add_range_button.button_type = 'warning'
    query_row.append(RangeRow())
    layout_query.children.insert(widget_row_start + len(query_row_type), query_row[-1].row)
    query_row_type.append('range')
    update_update_button_status()
    main_add_range_button.label = old_label
    main_add_range_button.button_type = old_type


def button_add_endpoint_row():
    global query_row_type
    old_label = main_add_endpoint_button.label
    old_type = main_add_endpoint_button.button_type
    main_add_endpoint_button.label = 'Updating Layout...'
    main_add_endpoint_button.button_type = 'warning'
    query_row.append(EndPointRow())
    layout_query.children.insert(widget_row_start + len(query_row_type), query_row[-1].row)
    query_row_type.append('endpoint')
    main_add_endpoint_button.label = old_label
    main_add_endpoint_button.button_type = old_type


# Updates query row ids (after row deletion)
def update_query_row_ids():
    global query_row
    for i in range(1, len(query_row)):
        query_row[i].id = i


# find the widget rows that need text input title updates
# and then call update_range_values to the needed widget row
def update_all_range_endpoints():
    global query_row, query_row_type
    for i in range(1, len(query_row)):
        if query_row_type[i] == 'range':
            query_row[i].update_range_values(query_row[i].select_category.value)


# Determines if the physician has been specified
# will be used to remove the ability to select two physicians
# and also update physician rois for only the specified physician
def is_physician_set():
    global query_row, query_row_type
    for i in range(1, len(query_row)):
        if query_row_type[i] == 'selector':
            if query_row[i].select_category.value == "Physician":
                return True
    return False


# returns the physician specified
def get_physician():
    global query_row, query_row_type
    for i in range(1, len(query_row)):
        if query_row_type[i] == 'selector':
            if query_row[i].select_category.value == "Physician":
                return query_row[i].select_value.value
    return None


# main update function
def update_data():
    global query_row_type, query_row, current_dvh, current_dvh_group_1, current_dvh_group_2
    old_update_button_label = update_button.label
    old_update_button_type = update_button.button_type
    update_button.label = 'Updating...'
    update_button.button_type = 'warning'
    uids, dvh_query_str = get_query()
    print(str(datetime.now()), 'getting dvh data', sep=' ')
    current_dvh = DVH(uid=uids, dvh_condition=dvh_query_str)
    print(str(datetime.now()), 'initializing source data ', current_dvh.query, sep=' ')
    current_dvh_group_1, current_dvh_group_2 = update_dvh_data(current_dvh)
    calculate_review_dvh()
    update_all_range_endpoints()
    update_endpoint_data(current_dvh, current_dvh_group_1, current_dvh_group_2)
    update_button.label = old_update_button_label
    update_button.button_type = old_update_button_type
    control_chart_y.value = ''
    update_roi_viewer_mrn()


# Checks size of current query, changes update button to orange if over 50 DVHs
def update_update_button_status():
    uids, dvh_query_str = get_query()
    count = DVH_SQL().get_roi_count_from_query(dvh_condition=dvh_query_str, uid=uids)
    if count > 50:
        update_button.button_type = "warning"
        update_button.label = "Large Update (" + str(count) + ")"
    else:
        update_button.button_type = "success"
        update_button.label = "Update"


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


# This function retuns the list of information needed to execute QuerySQL from
# SQL_to_Python.py (i.e., uids and dvh_condition
def get_query(**kwargs):
    global query_row_type, query_row, current_dvh

    if kwargs and 'group' in kwargs:
        if kwargs['group'] == 1:
            active_groups = [0]
        elif kwargs['group'] == 2:
            active_groups = [1]
    else:
        active_groups = [0, 1]

    plan_query = []
    rx_query = []
    beam_query = []
    dvh_query = []

    for active_group in active_groups:
        plan_query_map = {}
        rx_query_map = {}
        beam_query_map = {}
        dvh_query_map = {}

        for i in range(1, len(query_row)):
            if query_row_type[i] in {'selector', 'range'} and \
                    (active_group in query_row[i].pop_grp.active or active_group == 2):
                if query_row_type[i] == 'selector':
                    var_name = selector_categories[query_row[i].select_category.value]['var_name']
                    table = selector_categories[query_row[i].select_category.value]['table']
                    value = query_row[i].select_value.value
                    query_str = var_name + " = '" + value + "'"
                elif query_row_type[i] == 'range':
                    query_row[i].select_category.value
                    var_name = range_categories[query_row[i].select_category.value]['var_name']
                    table = range_categories[query_row[i].select_category.value]['table']
                    if query_row[i].text_min.value != '':
                        value_low = query_row[i].text_min.value
                    else:
                        value_low = query_row[i].min_value
                    if query_row[i].text_max.value != '':
                        value_high = query_row[i].text_max.value
                    else:
                        value_high = query_row[i].max_value
                    if var_name in {'sim_study_date', 'birth_date'}:
                        value_low = "'" + value_low + "'::date"
                        value_high = "'" + value_high + "'::date"
                    query_str = var_name + " between " + str(value_low) + " and " + str(value_high)

                if table == 'Plans':
                    if var_name not in plan_query_map:
                        plan_query_map[var_name] = []
                    plan_query_map[var_name].append(query_str)
                elif table == 'Rxs':
                    if var_name not in rx_query_map:
                        rx_query_map[var_name] = []
                    rx_query_map[var_name].append(query_str)
                elif table == 'Beams':
                    if var_name not in beam_query_map:
                        beam_query_map[var_name] = []
                    beam_query_map[var_name].append(query_str)
                elif table == 'DVHs':
                    if var_name not in dvh_query_map:
                        dvh_query_map[var_name] = []
                    dvh_query_map[var_name].append(query_str)

        # The multiple entries of the same variable are found, assume an 'or' condition
        plan_query_str = []
        for key in plan_query_map.iterkeys():
            plan_query_str.append('(' + ' or '.join(plan_query_map[key]) + ')')

        rx_query_str = []
        for key in rx_query_map.iterkeys():
            rx_query_str.append('(' + ' or '.join(rx_query_map[key]) + ')')

        beam_query_str = []
        for key in beam_query_map.iterkeys():
            beam_query_str.append('(' + ' or '.join(beam_query_map[key]) + ')')

        dvh_query_str = []
        skip_roi_names = False
        roi_categories = {'physician_roi',
                          'institutional_roi'}
        if 'physician_roi' in dvh_query_map.keys():
            if 'institutional_roi' in dvh_query_map.keys():
                roi_name_query = dvh_query_map['physician_roi'] + \
                                 dvh_query_map['institutional_roi']
                dvh_query_str.append('(' + ' or '.join(roi_name_query) + ')')
                skip_roi_names = True
        for key in dvh_query_map.iterkeys():
            if skip_roi_names and key in roi_categories:
                pass
            else:
                dvh_query_str.append('(' + ' or '.join(dvh_query_map[key]) + ')')

        # assumes an 'and' condition between variable types
        plan_query.append(' and '.join(plan_query_str))
        rx_query.append(' and '.join(rx_query_str))
        beam_query.append(' and '.join(beam_query_str))
        dvh_query.append(' and '.join(dvh_query_str))

    if len(active_groups) == 2:
        plan_query = combine_query(plan_query)
        rx_query = combine_query(rx_query)
        beam_query = combine_query(beam_query)
        dvh_query = combine_query(dvh_query)

    else:
        plan_query = plan_query[0]
        rx_query = rx_query[0]
        beam_query = beam_query[0]
        dvh_query = dvh_query[0]

    print(str(datetime.now()), 'getting uids', sep=' ')
    print(str(datetime.now()), 'Plans =', plan_query, sep=' ')
    print(str(datetime.now()), 'Rxs =', rx_query, sep=' ')
    print(str(datetime.now()), 'Beams =', beam_query, sep=' ')
    uids = get_study_instance_uids(Plans=plan_query, Rxs=rx_query, Beams=beam_query)['union']

    return uids, dvh_query


def combine_query(query):
    if query[0] and query[1]:
        query = '(' + ') or ('.join(query) + ')'
    elif query[0]:
        query = query[0]
    elif query[1]:
        query = query[1]
    else:
        query = []
    return query


# This class adds a row suitable to filter discrete data from the SQL database
class SelectorRow:
    def __init__(self):

        self.id = len(query_row)
        self.category_options = selector_categories.keys()
        self.category_options.sort()
        self.select_category = Select(value="ROI Institutional Category", options=self.category_options, width=300)
        self.select_category.on_change('value', self.update_selector_values)

        self.sql_table = selector_categories[self.select_category.value]['table']
        self.var_name = selector_categories[self.select_category.value]['var_name']
        self.values = DVH_SQL().get_unique_values(self.sql_table, self.var_name)
        self.select_value = Select(value=self.values[0], options=self.values, width=420)
        self.select_value.on_change('value', self.selector_values_ticker)

        self.pop_grp = CheckboxButtonGroup(labels=["Blue Group", "Red Group"], active=[0], width=180)

        self.delete_last_row = Button(label="Delete", button_type="warning", width=100)
        self.delete_last_row.on_click(self.delete_row)

        self.row = row(self.select_category,
                       self.select_value,
                       self.pop_grp,
                       self.delete_last_row)

    def update_selector_values(self, attrname, old, new):
        table_new = selector_categories[self.select_category.value]['table']
        var_name_new = selector_categories[new]['var_name']
        if var_name_new == 'physician_roi':
            physicians = []
            for i in range(1, len(query_row)):
                if query_row_type[i] in {'selector'} and query_row[i].select_category.value in {'Physician'}:
                    physicians.append("'" + query_row[i].select_value.value + "'")
            if physicians:
                get_uid_condition = 'physician in (' + ','.join(physicians) + ')'
                uids = DVH_SQL().get_unique_values('Plans', 'study_instance_uid', get_uid_condition)
                condition = "study_instance_uid in ('" + "','".join(uids) + "')"
                new_options = DVH_SQL().get_unique_values(table_new, var_name_new, condition)
            else:
                new_options = DVH_SQL().get_unique_values(table_new, var_name_new)
        else:
            new_options = DVH_SQL().get_unique_values(table_new, var_name_new)
        self.select_value.options = new_options
        self.select_value.value = new_options[0]
        update_update_button_status()

    def selector_values_ticker(self, attrname, old, new):
        update_update_button_status()

    def delete_row(self):
        del (layout_query.children[widget_row_start + self.id])
        query_row_type.pop(self.id)
        query_row.pop(self.id)
        update_query_row_ids()
        update_update_button_status()


# This class adds a row suitable to filter continuous data from the SQL database
class RangeRow:
    def __init__(self):
        self.id = len(query_row)
        self.category_options = range_categories.keys()
        self.category_options.sort()
        self.select_category = Select(value=self.category_options[-1], options=self.category_options, width=300)
        self.select_category.on_change('value', self.update_range_values_ticker)

        self.sql_table = range_categories[self.select_category.value]['table']
        self.var_name = range_categories[self.select_category.value]['var_name']
        self.min_value = []
        self.max_value = []
        self.text_min = TextInput(value='', title='', width=210)
        self.text_min.on_change('value', self.check_for_start_date_ticker)
        self.text_max = TextInput(value='', title='', width=210)
        self.text_max.on_change('value', self.check_for_end_date_ticker)
        self.update_range_values(self.select_category.value)

        self.pop_grp = CheckboxButtonGroup(labels=["Blue Group", "Red Group"], active=[0], width=180)

        self.delete_last_row = Button(label="Delete", button_type="warning", width=100)
        self.delete_last_row.on_click(self.delete_row)

        self.row = row([self.select_category,
                        self.text_min,
                        self.text_max,
                        self.pop_grp,
                        self.delete_last_row])

    def check_for_start_date_ticker(self, attrname, old, new):
        if self.select_category.value.lower().find("date") > -1:
            self.text_min.value = date_str_to_sql_format(new, type='start')

    def check_for_end_date_ticker(self, attrname, old, new):
        if self.select_category.value.lower().find("date") > -1:
            self.text_max.value = date_str_to_sql_format(new, type='end')

    def update_range_values_ticker(self, attrname, old, new):
        self.update_range_values(new)

    def update_range_values(self, new):
        table_new = range_categories[new]['table']
        var_name_new = range_categories[new]['var_name']
        if source.data['mrn']:
            values = range_categories[new]['source'].data[var_name_new]
            if 'date' not in var_name_new:
                values = [v for v in values if type(v) in {float, int}]
            else:
                values = [v for v in values if 'None' not in v]
            self.min_value = min(values)
            self.max_value = max(values)
        else:
            self.min_value = DVH_SQL().get_min_value(table_new, var_name_new)
            self.max_value = DVH_SQL().get_max_value(table_new, var_name_new)
        self.text_min.title = 'Min: ' + str(self.min_value) + ' ' + range_categories[new]['units']
        self.text_max.title = 'Max: ' + str(self.max_value) + ' ' + range_categories[new]['units']
        update_update_button_status()

    def delete_row(self):
        del (layout_query.children[widget_row_start + self.id])
        query_row_type.pop(self.id)
        query_row.pop(self.id)
        update_query_row_ids()
        update_update_button_status()


# This class adds a row to calculate specified DVH endpoints
class EndPointRow:
    def __init__(self):

        self.id = len(query_row)
        self.options = ["Dose to Vol", "Vol of Dose"]
        self.select_category = RadioButtonGroup(labels=self.options, active=0, width=200)
        self.select_category.on_change('active', self.endpoint_category_ticker)

        self.unit_labels = [["%", "cc"], ["%", "Gy"]]

        self.units_out = RadioButtonGroup(labels=self.unit_labels[1], active=1, width=100)
        self.units_out.on_change('active', self.endpoint_units_out_ticker)

        self.text_input = TextInput(value='', title="Volume (%):", width=260)
        self.text_input.on_change('value', self.endpoint_calc_ticker)

        self.units = RadioButtonGroup(labels=self.unit_labels[0], active=0, width=340)
        self.units.on_change('active', self.endpoint_units_ticker)

        self.delete_last_row = Button(label="Delete", button_type="warning", width=100)
        self.delete_last_row.on_click(self.delete_row)

        self.row = row(self.select_category,
                       self.units_out,
                       self.text_input,
                       self.units,
                       self.delete_last_row)

    def endpoint_category_ticker(self, attrname, old, new):
        self.update_text_input_title()
        self.units.labels = self.unit_labels[new]
        self.units_out.labels = self.unit_labels[old]
        if self.text_input.value != '':
            update_endpoint_data(current_dvh, current_dvh_group_1, current_dvh_group_2)

    def endpoint_calc_ticker(self, attrname, old, new):
        if self.text_input.value != '':
            update_endpoint_data(current_dvh, current_dvh_group_1, current_dvh_group_2)

    def endpoint_units_ticker(self, attrname, old, new):
        self.update_text_input_title()
        if self.text_input.value != '':
            update_endpoint_data(current_dvh, current_dvh_group_1, current_dvh_group_2)

    def endpoint_units_out_ticker(self, attrname, old, new):
        if self.text_input.value != '':
            update_endpoint_data(current_dvh, current_dvh_group_1, current_dvh_group_2)

    def delete_row(self):
        del (layout_query.children[widget_row_start + self.id])
        query_row_type.pop(self.id)
        query_row.pop(self.id)
        update_query_row_ids()
        update_endpoint_data(current_dvh, current_dvh_group_1, current_dvh_group_2)

    def update_text_input_title(self):
        if self.select_category.active == 0:
            self.text_input.title = 'Volume (' + self.unit_labels[0][self.units.active] + '):'
        elif self.select_category.active == 1:
            self.text_input.title = 'Dose (' + self.unit_labels[1][self.units.active] + '):'


def get_group_list(uids):

    groups = []
    for r in range(0, len(uids)):
        if uids[r] in uids_1:
            if uids[r] in uids_2:
                groups.append('Blue & Red')
            else:
                groups.append('Blue')
        else:
            groups.append('Red')

    return groups


# input is a DVH class from Analysis_Tools.py
# This function creates a new ColumnSourceData and calls
# the functions to update beam, rx, and plans ColumnSourceData variables
def update_dvh_data(dvh):

    global uids_1, uids_2

    dvh_group_1 = []
    dvh_group_2 = []

    group_1_count, group_2_count = group_count()
    if group_1_count > 0 and group_2_count > 0:
        extra_rows = 12
    elif group_1_count > 0 or group_2_count > 0:
        extra_rows = 6
    else:
        extra_rows = 0

    print(str(datetime.now()), 'updating dvh data', sep=' ')
    line_colors = []
    for j, color in itertools.izip(range(0, dvh.count + extra_rows), colors):
        line_colors.append(color)

    x_axis = np.round(np.add(np.linspace(0, dvh.bin_count, dvh.bin_count) / 100., 0.005), 3)

    print(str(datetime.now()), 'beginning stat calcs', sep=' ')

    if radio_group_dose.active == 1:
        stat_dose_scale = 'relative'
        x_axis = dvh.get_stat_dvh(type=False, dose=stat_dose_scale)
    else:
        stat_dose_scale = 'absolute'
    if radio_group_volume.active == 0:
        stat_volume_scale = 'absolute'
    else:
        stat_volume_scale = 'relative'

    print(str(datetime.now()), 'calculating patches', sep=' ')

    # stat_dvhs = dvh.get_standard_stat_dvh(dose=stat_dose_scale, volume=stat_volume_scale)

    if group_1_count == 0:
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
        uids_1, dvh_query_str = get_query(group=1)
        dvh_group_1 = DVH(uid=uids_1, dvh_condition=dvh_query_str)
        uids_1 = dvh_group_1.study_instance_uid
        stat_dvhs_1 = dvh_group_1.get_standard_stat_dvh(dose=stat_dose_scale, volume=stat_volume_scale)

        if radio_group_dose.active == 1:
            x_axis_1 = dvh_group_1.get_stat_dvh(type=False, dose=stat_dose_scale)
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
    if group_2_count == 0:
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
        uids_2, dvh_query_str = get_query(group=2)
        dvh_group_2 = DVH(uid=uids_2, dvh_condition=dvh_query_str)
        uids_2 = dvh_group_2.study_instance_uid
        stat_dvhs_2 = dvh_group_2.get_standard_stat_dvh(dose=stat_dose_scale, volume=stat_volume_scale)

        if radio_group_dose.active == 1:
            x_axis_2 = dvh_group_2.get_stat_dvh(type=False, dose=stat_dose_scale)
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

    new_endpoint_columns = [''] * (dvh.count + extra_rows + 1)

    x_data = []
    y_data = []
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

        if dvh_group_1:
            if dvh.study_instance_uid[r] in uids_1:
                index_1 = dvh_group_1.study_instance_uid.index(dvh.study_instance_uid[r])
                if dvh.roi_name[r] in {dvh_group_1.roi_name[index_1]}:
                    dvh_groups.append('Blue')

        if dvh_group_2:
            if dvh.study_instance_uid[r] in uids_2:
                index_2 = dvh_group_2.study_instance_uid.index(dvh.study_instance_uid[r])
                if dvh.roi_name[r] in {dvh_group_2.roi_name[index_2]}:
                    if len(dvh_groups) == r + 1:
                        dvh_groups[r] = 'Blue & Red'
                    else:
                        dvh_groups.append('Red')
    dvh_groups.insert(0, 'Review')

    for n in range(0, 6):
        if group_1_count > 0:
            dvh.mrn.append(y_names[n])
            dvh.roi_name.append('Blue Group')
            x_data.append(x_axis.tolist())
            current = stat_dvhs_1[y_names[n].lower()].tolist()
            y_data.append(current)
            dvh_groups.append('Blue')
        if group_2_count > 0:
            dvh.mrn.append(y_names[n])
            dvh.roi_name.append('Red Group')
            x_data.append(x_axis.tolist())
            current = stat_dvhs_2[y_names[n].lower()].tolist()
            y_data.append(current)
            dvh_groups.append('Red')

    # Adjust dvh object to include stats data
    if extra_rows > 0:
        dvh.study_instance_uid.extend(['N/A'] * extra_rows)
        dvh.institutional_roi.extend(['N/A'] * extra_rows)
        dvh.physician_roi.extend(['N/A'] * extra_rows)
        dvh.roi_type.extend(['Stat'] * extra_rows)
        dvh.eud_a_value.extend(['N/A'] * extra_rows)
        dvh.dist_to_ptv_min.extend(['N/A'] * extra_rows)
        dvh.dist_to_ptv_median.extend(['N/A'] * extra_rows)
        dvh.dist_to_ptv_mean.extend(['N/A'] * extra_rows)
        dvh.dist_to_ptv_max.extend(['N/A'] * extra_rows)
        dvh.ptv_overlap.extend(['N/A'] * extra_rows)
    if group_1_count > 0:
        dvh.rx_dose.extend(calc_stats(dvh_group_1.rx_dose))
        dvh.volume.extend(calc_stats(dvh_group_1.volume))
        dvh.surface_area.extend(calc_stats(dvh_group_1.surface_area))
        dvh.min_dose.extend(calc_stats(dvh_group_1.min_dose))
        dvh.mean_dose.extend(calc_stats(dvh_group_1.mean_dose))
        dvh.max_dose.extend(calc_stats(dvh_group_1.max_dose))
        dvh.eud.extend(calc_stats(dvh_group_1.eud))
    if group_2_count > 0:
        dvh.rx_dose.extend(calc_stats(dvh_group_2.rx_dose))
        dvh.volume.extend(calc_stats(dvh_group_2.volume))
        dvh.surface_area.extend(calc_stats(dvh_group_2.surface_area))
        dvh.min_dose.extend(calc_stats(dvh_group_2.min_dose))
        dvh.mean_dose.extend(calc_stats(dvh_group_2.mean_dose))
        dvh.max_dose.extend(calc_stats(dvh_group_2.max_dose))
        dvh.eud.extend(calc_stats(dvh_group_2.eud))

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
    dvh.eud.insert(0, 'N/A')
    dvh.eud_a_value.insert(0, 'N/A')
    dvh.dist_to_ptv_min.insert(0, 'N/A')
    dvh.dist_to_ptv_mean.insert(0, 'N/A')
    dvh.dist_to_ptv_median.insert(0, 'N/A')
    dvh.dist_to_ptv_max.insert(0, 'N/A')
    dvh.ptv_overlap.insert(0, 'N/A')
    line_colors.insert(0, 'green')
    x_data.insert(0, [0])
    y_data.insert(0, [0])

    print(str(datetime.now()), 'writing source.data', sep=' ')
    source.data = {'mrn': dvh.mrn,
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
                   'eud': dvh.eud,
                   'eud_a_value': dvh.eud_a_value,
                   'dist_to_ptv_min': dvh.dist_to_ptv_min,
                   'dist_to_ptv_mean': dvh.dist_to_ptv_mean,
                   'dist_to_ptv_median': dvh.dist_to_ptv_median,
                   'dist_to_ptv_max': dvh.dist_to_ptv_max,
                   'ptv_overlap': dvh.ptv_overlap,
                   'x': x_data,
                   'y': y_data,
                   'color': line_colors,
                   'ep1': new_endpoint_columns,
                   'ep2': new_endpoint_columns,
                   'ep3': new_endpoint_columns,
                   'ep4': new_endpoint_columns,
                   'ep5': new_endpoint_columns,
                   'ep6': new_endpoint_columns,
                   'ep7': new_endpoint_columns,
                   'ep8': new_endpoint_columns,
                   'x_scale': x_scale,
                   'y_scale': y_scale}
    print(str(datetime.now()), 'source.data set', sep=' ')

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

    source_beams.data = {'mrn': beam_data.mrn,
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

    source_plans.data = {'mrn': plan_data.mrn,
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

    source_rxs.data = {'mrn': rx_data.mrn,
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


# updates endpoint ColumnSourceData for a given DVH class from Analysis_Tools.py
# note that endpoint ColumnSourceData exits in dvh data ColumnSourceData (i.e.,
# the main ColumnSourceData variable, or 'source')
def update_endpoint_data(dvh, dvh_group_1, dvh_group_2):
    group_1_count, group_2_count = group_count()
    if group_1_count > 0 and group_2_count > 0:
        extra_rows = 12
    elif group_1_count > 0 or group_2_count > 0:
        extra_rows = 6
    else:
        extra_rows = 0

    global query_row, query_row_type, endpoint_columns
    for i in range(0, 8):
        endpoint_columns[i] = ''
    endpoints_map = {}
    endpoints_map_1 = {}
    endpoints_map_2 = {}

    counter = 0
    for i in range(0, len(query_row)):
        if query_row_type[i] == 'endpoint' and counter < 8:
            output_unit = ['Gy', 'cc']
            x = float(query_row[i].text_input.value)
            x_for_text = x
            if query_row[i].units.active == 0:
                endpoint_input = 'relative'
                units = query_row[i].units.labels[0]
                x /= 100.
            else:
                endpoint_input = 'absolute'
                units = query_row[i].units.labels[1]
            if query_row[i].units_out.active == 0:
                endpoint_output = 'relative'
                output_unit = ['%', '%']
            else:
                endpoint_output = 'absolute'
            if query_row[i].select_category.active == 0:
                endpoint_columns[counter] = 'D_' + str(x_for_text) + units + ' (' + output_unit[0] + ')'
                endpoints_map[counter] = dvh.get_dose_to_volume(x, input=endpoint_input, output=endpoint_output)
                if group_1_count > 0:
                    endpoints_map_1[counter] = dvh_group_1.get_dose_to_volume(x,
                                                                              input=endpoint_input,
                                                                              output=endpoint_output)
                if group_2_count > 0:
                    endpoints_map_2[counter] = dvh_group_2.get_dose_to_volume(x,
                                                                              input=endpoint_input,
                                                                              output=endpoint_output)
            else:
                endpoint_columns[counter] = 'V_' + str(x_for_text) + units + ' (' + output_unit[1] + ')'
                endpoints_map[counter] = dvh.get_volume_of_dose(x, input=endpoint_input, output=endpoint_output)
                if group_1_count > 0:
                    endpoints_map_1[counter] = dvh_group_1.get_volume_of_dose(x,
                                                                              input=endpoint_input,
                                                                              output=endpoint_output)
                if group_2_count > 0:
                    endpoints_map_2[counter] = dvh_group_2.get_volume_of_dose(x,
                                                                              input=endpoint_input,
                                                                              output=endpoint_output)
            if extra_rows == 6:
                endpoints_map[counter].extend(calc_stats(endpoints_map[counter][1:dvh.count]))
            elif extra_rows == 12:
                group_1_stats = calc_stats(endpoints_map_1[counter])
                group_2_stats = calc_stats(endpoints_map_2[counter])
                stats = []
                for q in range(0, 6):
                    stats.append(group_1_stats[q])
                    stats.append(group_2_stats[q])
                endpoints_map[counter].extend(stats)

            counter += 1

    for i in range(counter, 8):
        endpoints_map[i] = []
        for j in range(0, dvh.count + extra_rows):
            endpoints_map[i].append('')

    tuple_list = {}
    for i in range(0, 8):
        current_tuple_list = []
        for j in range(0, dvh.count + extra_rows):
            current_tuple_list.append(tuple([j, endpoints_map[i][j]]))
        tuple_list[i] = current_tuple_list

    patches = {'ep1': tuple_list[0],
               'ep2': tuple_list[1],
               'ep3': tuple_list[2],
               'ep4': tuple_list[3],
               'ep5': tuple_list[4],
               'ep6': tuple_list[5],
               'ep7': tuple_list[6],
               'ep8': tuple_list[7]}

    source.patch(patches)

    source_endpoint_names.data = {'ep1': [endpoint_columns[0]],
                                  'ep2': [endpoint_columns[1]],
                                  'ep3': [endpoint_columns[2]],
                                  'ep4': [endpoint_columns[3]],
                                  'ep5': [endpoint_columns[4]],
                                  'ep6': [endpoint_columns[5]],
                                  'ep7': [endpoint_columns[6]],
                                  'ep8': [endpoint_columns[7]]}

    # Update table column names based on the query
    for i in range(0, counter):
        data_table_endpoints.columns[i+1] = TableColumn(field=str('ep' + str(i+1)),
                                                        title=endpoint_columns[i],
                                                        width=100,
                                                        formatter=NumberFormatter(format="0.00"))


def date_str_to_sql_format(date, **kwargs):

    if kwargs and 'type' in kwargs and kwargs['type'] == 'start':
        append_month = '-01-01'
        append_day = '-01'
    else:
        append_month = '-12-31'
        append_day = '-31'
    date_len = len(date)
    if date.isdigit():
        if date_len == 4:
            date = date + append_month
        elif date_len == 5:
            date = date[0:4] + '0' + date[4] + append_day
        elif date_len == 6:
            date = date + append_day
    else:
        non_digit_count = date_len - sum(x.isdigit() for x in date)
        if non_digit_count == 1:
            date = date[0:4] + date[5:date_len]
        else:
            date = date[0:4] + date[5:7] + date[8:date_len]

    return date


def calc_stats(data):
    data_np = np.array(data)
    rtn_data = [np.max(data_np),
                np.percentile(data_np, 75),
                np.median(data_np),
                np.mean(data_np),
                np.percentile(data_np, 25),
                np.min(data_np)]
    return rtn_data


def update_dvh_review_rois(attr, old, new):
    global temp_dvh_info, dvh_review_rois
    if select_reviewed_mrn.value:
        initial_button_type = calculate_review_dvh_button.button_type
        calculate_review_dvh_button.button_type = "warning"

        initial_label = calculate_review_dvh_button.label
        calculate_review_dvh_button.label = "Updating..."
        if new != '':
            dvh_review_rois = temp_dvh_info.get_roi_names(new).values()
            select_reviewed_dvh.options = dvh_review_rois
            select_reviewed_dvh.value = dvh_review_rois[0]
        else:
            select_reviewed_dvh.options = ['']
            select_reviewed_dvh.value = ['']

        calculate_review_dvh_button.button_type = initial_button_type
        calculate_review_dvh_button.label = initial_label
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
                   'rx_dose': [(0, '')],
                   'eud_a_value': [(0, '')],
                   'eud': [(0, '')]}
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
               'rx_dose': [(0, 1)],
               'eud_a_value': [(0, '')],
               'eud': [(0, '')]}

    try:
        if not source.data['x']:
            calculate_review_dvh_button.button_type = 'warning'
            calculate_review_dvh_button.label = 'Waiting...'
            update_data()

        else:
            calculate_review_dvh_button.button_type = 'warning'
            calculate_review_dvh_button.label = 'Calculating...'

            file_index = temp_dvh_info.mrn.index(select_reviewed_mrn.value)
            roi_index = dvh_review_rois.index(select_reviewed_dvh.value)
            structure_file = temp_dvh_info.structure[file_index]
            plan_file = temp_dvh_info.plan[file_index]
            dose_file = temp_dvh_info.dose[file_index]
            key = temp_dvh_info.get_roi_names(select_reviewed_mrn.value).keys()[roi_index]

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
            if not review_eud_a_value.value:
                eud_a_value = 1.
            else:
                eud_a_value = float(review_eud_a_value.value)

            x = review_dvh.bincenters
            y = np.divide(review_dvh.counts, max(review_dvh.counts))

            eud = calc_eud(y, eud_a_value)

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
                       'rx_dose': [(0, rx_dose)],
                       'eud_a_value': [(0, eud_a_value)],
                       'eud': [(0, eud)]}

    except:
        pass

    source.patch(patches)

    calculate_review_dvh_button.button_type = 'success'
    calculate_review_dvh_button.label = 'Calculate Review DVH'


def group_count():
    global query_row, query_row_type
    group_1 = 0
    group_2 = 0
    for i in range(0, len(query_row)):
        if query_row_type[i] in {'selector', 'range'}:
            if 0 in query_row[i].pop_grp.active:
                group_1 += 1
            if 1 in query_row[i].pop_grp.active:
                group_2 += 1
    return group_1, group_2


def select_reviewed_dvh_ticker(attr, old, new):
    calculate_review_dvh()


def review_rx_ticker(attr, old, new):
    if radio_group_dose.active == 0:
        source.patch({'rx_dose': [(0, round(float(review_rx.value), 2))]})
    else:
        calculate_review_dvh()


def review_eud_a_value_ticker(attr, old, new):
    calculate_review_dvh()


def update_control_chart_ticker(attr, old, new):
    update_control_chart()


def update_control_chart_y_ticker(attr, old, new):
    update_control_chart()


def update_control_chart_text_ticker(attr, old, new):
    update_control_chart()


def collapse_into_single_dates(x, y):

    # average daily data and keep track of points per day
    x_collapsed = [x[0]]
    y_collapsed = [y[0]]
    w_collapsed = [1]
    for n in range(1, len(x)):
        if x[n] == x_collapsed[-1]:
            y_collapsed[-1] = (y_collapsed[-1] + y[n])
            w_collapsed[-1] += 1
        else:
            x_collapsed.append(x[n])
            y_collapsed.append(y[n])
            w_collapsed.append(1)

    return x_collapsed, y_collapsed, w_collapsed


def update_control_chart():
    new = control_chart_y.value
    if new:

        # reset selection
        selected = {'0d': {'glyph': None, 'indices': []},
                    '1d': {'indices': []},
                    '2d': {'indices': {}}}
        source_time.selected = selected

        y_source = range_categories[new]['source']
        y_var_name = range_categories[new]['var_name']
        y_source_values = y_source.data[y_var_name]
        y_source_uids = y_source.data['uid']
        y_source_mrns = y_source.data['mrn']
        sim_study_dates = source_plans.data['sim_study_date']
        sim_study_dates_uids = source_plans.data['uid']

        if range_categories[new]['units']:
            control_chart.yaxis.axis_label = new + " (" + range_categories[new]['units'] + ")"
        else:
            control_chart.yaxis.axis_label = new

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

            if not skipped[-1]:
                if current_dvh_group_1 and current_dvh_group_2:
                    if uid in current_dvh_group_1.study_instance_uid and uid in current_dvh_group_2.study_instance_uid:
                        colors.append('purple')
                    elif uid in current_dvh_group_1.study_instance_uid:
                        colors.append('blue')
                    else:
                        colors.append('red')
                elif current_dvh_group_1:
                    colors.append('blue')
                else:
                    colors.append('red')

        y_values = []
        y_mrns = []
        for v in range(0, len(y_source_values)):
            if not skipped[v]:
                y_values.append(y_source_values[v])
                y_mrns.append(y_source_mrns[v])
                if not isinstance(y_values[-1], (int, long, float)):
                    y_values[-1] = 0

        sort_index = sorted(range(len(x_values)), key=lambda k: x_values[k])
        x_values_sorted = []
        y_values_sorted = []
        y_mrns_sorted = []
        colors_sorted = []
        for s in range(0, len(x_values)):
            x_values_sorted.append(x_values[sort_index[s]])
            y_values_sorted.append(y_values[sort_index[s]])
            y_mrns_sorted.append(y_mrns[sort_index[s]])
            colors_sorted.append(colors[sort_index[s]])

        # average daily data and keep track of points per day
        x_collapsed, y_collapsed, w_collapsed = collapse_into_single_dates(x_values_sorted, y_values_sorted)

        try:
            avg_len = int(control_chart_text_input.value)
        except:
            avg_len = 1
        cumsum, moving_aves = [0], []

        for i, y in enumerate(y_collapsed, 1):
            cumsum.append(cumsum[i - 1] + y / w_collapsed[i - 1])
            if i >= avg_len:
                moving_ave = (cumsum[i] - cumsum[i - avg_len]) / avg_len
                moving_aves.append(moving_ave)
        x_final = []
        for i in range(avg_len - 1, len(x_collapsed)):
            x_final.append(x_collapsed[i])

        y_np = np.array(y_values_sorted)
        try:
            percentile = float(control_chart_percentile.value)
        except:
            percentile = 90.
        upper_bound = [float(np.percentile(y_np, 50. + percentile / 2.))] * len(x_values)
        average = [float(np.percentile(y_np, 50))] * len(x_values)
        lower_bound = [float(np.percentile(y_np, 50. - percentile / 2.))] * len(x_values)

        source_time.data = {'x': x_values_sorted,
                            'y': y_values_sorted,
                            'mrn': y_mrns_sorted,
                            'color': colors_sorted}
        source_time_trend.data = {'x': x_final,
                                  'y': moving_aves,
                                  'mrn': ['Rolling Avg'] * len(x_final)}
        source_time_bound.data = {'x': x_values_sorted,
                                  'mrn': ['Bound'] * len(x_values),
                                  'upper': upper_bound,
                                  'avg': average,
                                  'lower': lower_bound}
    else:
        source_time.data = {'x': [],
                            'y': [],
                            'mrn': [],
                            'color': [],
                            'avg': []}
        source_time_trend.data = {'x': [],
                                  'y': [],
                                  'mrn': []}
        source_time_bound.data = {'x': [],
                                  'mrn': [],
                                  'upper': [],
                                  'avg': [],
                                  'lower': []}

    control_chart_update_trend()


def control_chart_update_trend():

    selected = source_time.selected['1d']['indices']

    if not selected:
        selected = range(0, len(source_time.data['x']))

    x_selected, y_selected = [], []
    for i in range(0, len(source_time.data['x'])):
        if i in selected:
            x_selected.append(source_time.data['x'][i])
            y_selected.append(source_time.data['y'][i])

    # average daily data and keep track of points per day
    x, y, w = collapse_into_single_dates(x_selected, y_selected)

    try:
        avg_len = int(control_chart_text_input.value)
    except:
        avg_len = 1
    cumsum, moving_aves = [0], []

    for i, y in enumerate(y, 1):
        cumsum.append(cumsum[i - 1] + y / w[i - 1])
        if i >= avg_len:
            moving_ave = (cumsum[i] - cumsum[i - avg_len]) / avg_len
            moving_aves.append(moving_ave)

    x_final = []
    for i in range(avg_len - 1, len(x)):
        x_final.append(x[i])

    y_np = np.array(y_selected)
    try:
        percentile = float(control_chart_percentile.value)
    except:
        percentile = 90.
    upper_bound = [float(np.percentile(y_np, 50. + percentile / 2.))] * len(source_time.data['x'])
    average = [float(np.percentile(y_np, 50))] * len(source_time.data['x'])
    lower_bound = [float(np.percentile(y_np, 50. - percentile / 2.))] * len(source_time.data['x'])

    source_time_trend.data = {'x': x_final,
                              'y': moving_aves,
                              'mrn': ['Avg'] * len(x_final)}
    source_time_bound.data = {'x': source_time.data['x'],
                              'mrn': ['Bound'] * len(source_time.data['x']),
                              'upper': upper_bound,
                              'avg': average,
                              'lower': lower_bound}


def update_roi_viewer_mrn():
    options = []
    for mrn in source_plans.data['mrn']:
        options.append(mrn)
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

    else:
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


def roi_viewer_slice_ticker(attr, old, new):
    update_roi_viewer()
    update_roi2_viewer()
    update_roi3_viewer()
    update_roi4_viewer()
    source_tv.data = {'x': [], 'y': [], 'z': []}


def update_roi_viewer_slice():
    options = roi_viewer_data.keys()
    options.sort()
    roi_viewer_slice_select.options = options
    roi_viewer_slice_select.value = options[0]


def roi_viewer_go_to_previous_slice():
    index = roi_viewer_slice_select.options.index(roi_viewer_slice_select.value)
    roi_viewer_slice_select.value = roi_viewer_slice_select.options[index - 1]


def roi_viewer_go_to_next_slice():
    index = roi_viewer_slice_select.options.index(roi_viewer_slice_select.value)
    if index + 1 == len(roi_viewer_slice_select.options):
        index = -1
    roi_viewer_slice_select.value = roi_viewer_slice_select.options[index + 1]


def update_roi_viewer_rois():
    options = []
    for i in range(0, len(source.data['uid'])):
        if source.data['uid'][i] == roi_viewer_uid_select.value:
            options.append(source.data['roi_name'][i])
    options.sort()
    roi_viewer_roi_select.options = options
    roi_viewer_roi_select.value = options[0]

    roi_viewer_roi2_select.options = [''] + options
    roi_viewer_roi2_select.value = ''

    roi_viewer_roi3_select.options = [''] + options
    roi_viewer_roi3_select.value = ''

    roi_viewer_roi4_select.options = [''] + options
    roi_viewer_roi4_select.value = ''


def update_roi_viewer_data(roi_name):

    roi_data = {}
    uid = roi_viewer_uid_select.value
    roi_coord_string = DVH_SQL().query('dvhs',
                                       'roi_coord_string',
                                       "study_instance_uid = '%s' and roi_name = '%s'" % (uid, roi_name))
    roi_planes = get_planes_from_string(roi_coord_string[0][0])
    for z_plane in roi_planes.keys():
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
        roi_data[z_plane] = {'x': x,
                             'y': y,
                             'z': z}

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

        ptvs = []
        for ptv in ptv_coordinates_strings:
            ptvs.append(get_planes_from_string(ptv[0]))
        tv_planes = get_union(ptvs)

    for z_plane in tv_planes.keys():
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
    if z in roi2_viewer_data.keys():
        source_roi2_viewer.data = roi2_viewer_data[z]
    else:
        source_roi2_viewer.data = {'x': [], 'y': [], 'z': []}


def update_roi3_viewer():
    z = roi_viewer_slice_select.value
    if z in roi3_viewer_data.keys():
        source_roi3_viewer.data = roi3_viewer_data[z]
    else:
        source_roi3_viewer.data = {'x': [], 'y': [], 'z': []}


def update_roi4_viewer():
    z = roi_viewer_slice_select.value
    if z in roi4_viewer_data.keys():
        source_roi4_viewer.data = roi4_viewer_data[z]
    else:
        source_roi4_viewer.data = {'x': [], 'y': [], 'z': []}


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
    if z in tv_data.keys() and not source_tv.data['x']:
        source_tv.data = tv_data[z]
    else:
        source_tv.data = {'x': [], 'y': [], 'z': []}


# set up layout

tools = "pan,wheel_zoom,box_zoom,reset,crosshair,save"
dvh_plots = figure(plot_width=1000, plot_height=400, tools=tools, logo=None, active_drag="box_zoom")
dvh_plots.add_tools(HoverTool(show_arrow=False,
                              line_policy='next',
                              tooltips=[('Label', '@mrn @roi_name'),
                                        ('Dose', '$x'),
                                        ('Volume', '$y')]))

# Add statistical plots to figure
# stats_min = dvh_plots.line('x', 'min',
#                            source=source_stats_1,
#                            line_width=2,
#                            color='black',
#                            line_dash='dotted',
#                            alpha=0.2)
# stats_q1 = dvh_plots.line('x', 'q1',
#                           source=source_stats_1,
#                           line_width=0.5,
#                           color='black',
#                           alpha=0.2)
stats_median_1 = dvh_plots.line('x', 'median',
                                source=source_stats_1,
                                line_width=1,
                                color='blue',
                                line_dash='solid',
                                alpha=0.6)
stats_mean_1 = dvh_plots.line('x', 'mean',
                              source=source_stats_1,
                              line_width=2,
                              color='blue',
                              line_dash='dashed',
                              alpha=0.5)
# stats_q3 = dvh_plots.line('x', 'q3',
#                           source=source_stats_1,
#                           line_width=0.5,
#                           color='black',
#                           alpha=0.2)
# stats_max = dvh_plots.line('x', 'max',
#                            source=source_stats_1,
#                            line_width=2,
#                            color='black',
#                            line_dash='dotted',
#                            alpha=0.2)
stats_median_2 = dvh_plots.line('x', 'median',
                                source=source_stats_2,
                                line_width=1,
                                color='red',
                                line_dash='solid',
                                alpha=0.6)
stats_mean_2 = dvh_plots.line('x', 'mean',
                              source=source_stats_2,
                              line_width=2,
                              color='red',
                              line_dash='dashed',
                              alpha=0.5)

# Add all DVHs, but hide them until selected
dvh_plots.multi_line('x', 'y',
                     source=source,
                     selection_color='color',
                     line_width=2,
                     alpha=0,
                     nonselection_alpha=0,
                     selection_alpha=1)


# Shaded region between Q1 and Q3
dvh_plots.patch('x_patch', 'y_patch',
                source=source_patch_1,
                alpha=0.15)
dvh_plots.patch('x_patch', 'y_patch',
                source=source_patch_2,
                alpha=0.075,
                color='red')

# Set x and y axis labels
dvh_plots.xaxis.axis_label = "Dose (Gy)"
dvh_plots.yaxis.axis_label = "Normalized Volume"

# Set the legend (for stat dvhs only)
legend_stats = Legend(items=[
        # ("Max", [stats_max]),
        # ("Q3", [stats_q3]),
        ("Median", [stats_median_1]),
        ("Mean", [stats_mean_1]),
        # ("Q1", [stats_q1]),
        # ("Min", [stats_min])
        ("Median", [stats_median_2]),
        ("Mean", [stats_mean_2]),
    ], location=(0, -250))

# Add the layout outside the plot, clicking legend item hides the line
dvh_plots.add_layout(legend_stats, 'right')
dvh_plots.legend.click_policy = "hide"

# Set up DataTable for dvhs
data_table_title = Div(text="<b>DVHs</b>", width=1200)
columns = [TableColumn(field="mrn", title="MRN / Stat", width=175),
           TableColumn(field="roi_name", title="ROI Name"),
           TableColumn(field="roi_type", title="ROI Type", width=80),
           TableColumn(field="rx_dose", title="Rx Dose", width=100, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="volume", title="Volume", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="surface_area", title="S Area", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="min_dose", title="Min Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="mean_dose", title="Mean Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="max_dose", title="Max Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="eud", title="EUD", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="eud_a_value", title="a", width=80),
           TableColumn(field="dist_to_ptv_min", title="Dist to PTV", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="ptv_overlap", title="PTV Overlap", width=80, formatter=NumberFormatter(format="0.0"))]
data_table = DataTable(source=source, columns=columns, width=1200)

# Set up EndPoint DataTable
endpoint_table_title = Div(text="<b>DVH Endpoints</b>", width=1200)
columns = [TableColumn(field="mrn", title="MRN", width=160),
           TableColumn(field="ep1", title=endpoint_columns[0], width=120),
           TableColumn(field="ep2", title=endpoint_columns[1], width=120),
           TableColumn(field="ep3", title=endpoint_columns[2], width=120),
           TableColumn(field="ep4", title=endpoint_columns[3], width=120),
           TableColumn(field="ep5", title=endpoint_columns[4], width=120),
           TableColumn(field="ep6", title=endpoint_columns[5], width=120),
           TableColumn(field="ep7", title=endpoint_columns[6], width=120),
           TableColumn(field="ep8", title=endpoint_columns[7], width=120)]
data_table_endpoints = DataTable(source=source, columns=columns, width=1200)

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
data_table_beams = DataTable(source=source_beams, columns=columns, width=1300)
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
data_table_beams2 = DataTable(source=source_beams, columns=columns, width=1300)

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
data_table_plans = DataTable(source=source_plans, columns=columns, width=1300)

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
data_table_rxs = DataTable(source=source_rxs, columns=columns, width=1300)

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
review_eud_a_value = TextInput(value='1', title="EUD a-value:", width=170)
review_eud_a_value.on_change('value', review_eud_a_value_ticker)

calculate_review_dvh_button = Button(label="Calculate Review DVH",
                                     button_type="success",
                                     width=180)
calculate_review_dvh_button.on_click(calculate_review_dvh)

# Begin defining main row of widgets below figure

# define Update button
update_button = Button(label="Update", button_type="success", width=180)
update_button.on_click(update_data)

# define Download button and call download.js on click
menu = [("All Data", "all"), ("Lite", "lite"), ("Only DVHs", "dvhs")]
download_dropdown = Dropdown(label="Download", button_type="default", menu=menu, width=100)
download_dropdown.callback = CustomJS(args=dict(source=source,
                                                source_rxs=source_rxs,
                                                source_plans=source_plans,
                                                source_beams=source_beams,
                                                source_endpoint_names=source_endpoint_names),
                                      code=open(join(dirname(__file__), "download.js")).read())

# define button to widget row for discrete data filtering
main_add_selector_button = Button(label="Add Selection Filter", button_type="primary", width=180)
main_add_selector_button.on_click(button_add_selector_row)

# define button to widget row for continuous data filtering
main_add_range_button = Button(label="Add Range Filter", button_type="primary", width=180)
main_add_range_button.on_click(button_add_range_row)

# define button to widget row for adding DVH endpoints
main_add_endpoint_button = Button(label="Add Endpoint", button_type="primary", width=180)
main_add_endpoint_button.on_click(button_add_endpoint_row)

# not for display, but add these buttons to query_row
# query row is simply used to keep track of pointers to query rows
# allows code to dynamically add widgets and keep button functionality contained
query_row.append(row(update_button, main_add_selector_button, main_add_range_button))
query_row_type.append('main')

# Control Chart layout
tools = "pan,wheel_zoom,box_zoom,lasso_select,reset,crosshair,save"
control_chart = figure(plot_width=1050, plot_height=400, tools=tools, logo=None,
                       active_drag="box_zoom", x_axis_type='datetime')
control_chart.circle('x', 'y', size=10, color='color', alpha=0.25, source=source_time)
control_chart.line('x', 'y', color='black', source=source_time_trend)
control_chart.line('x', 'upper', color='red', source=source_time_bound, line_dash='dashed')
control_chart.line('x', 'avg', color='red', source=source_time_bound, line_dash='dotted')
control_chart.line('x', 'lower', color='red', source=source_time_bound, line_dash='dashed')
control_chart.add_tools(HoverTool(show_arrow=True,
                                  line_policy='next',
                                  tooltips=[('ID', '@mrn'),
                                            ('Date', '@x{%F}'),
                                            ('Value', '@y{0.2f}')],
                                  formatters={'x': 'datetime'}))
control_chart.xaxis.axis_label = "Simulation Date"
control_chart.yaxis.axis_label = ""

control_chart_title = Div(text="<b>Range-Variable Trending</b>", width=1000)
control_chart_options = range_categories.keys()
control_chart_options.sort()
control_chart_options.append('')
control_chart_y = Select(value=control_chart_options[-1], options=control_chart_options, width=300)
control_chart_y.title = "Y Axis"
control_chart_y.on_change('value', update_control_chart_y_ticker)

control_chart_text_input = TextInput(value='1', title="Lookback Distance:", width=200)
control_chart_text_input.on_change('value', update_control_chart_text_ticker)

control_chart_percentile = TextInput(value='90', title="Percentile:", width=200)
control_chart_percentile.on_change('value', update_control_chart_text_ticker)

lookback_units_options = ['Dates with a Sim', 'Days', 'Patients']
control_chart_lookback_units = Select(value=lookback_units_options[0], options=lookback_units_options, width=200)
control_chart_lookback_units.title = 'Lookback Units'
control_chart_lookback_units.on_change('value', update_control_chart_ticker)

# source_time.on_change('selected', control_chart_update_trend)
trend_update_button = Button(label="Update Trend", button_type="primary", width=150)
trend_update_button.on_click(control_chart_update_trend)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ROI Viewer Objects
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
roi_viewer_options = [''] + source.data['mrn']
roi_viewer_mrn_select = Select(value='', options=roi_viewer_options, width=200, title='MRN')
roi_viewer_study_date_select = Select(value='', options=[''], width=200, title='Sim Study Date')
roi_viewer_uid_select = Select(value='', options=[''], width=425, title='Study Instance UID')
roi_viewer_roi_select = Select(value='', options=[''], width=400, title='ROI 1: Blue')
roi_viewer_roi2_select = Select(value='', options=[''], width=200, height=100, title='ROI 2: Green')
roi_viewer_roi3_select = Select(value='', options=[''], width=200, height=100, title='ROI 3: Red')
roi_viewer_roi4_select = Select(value='', options=[''], width=200, height=100, title='ROI 4: Orange')
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
roi_viewer_slice_select.on_change('value', roi_viewer_slice_ticker)
roi_viewer_previous_slice.on_click(roi_viewer_go_to_previous_slice)
roi_viewer_next_slice.on_click(roi_viewer_go_to_next_slice)
roi_viewer_flip_x_axis_button.on_click(roi_viewer_flip_x_axis)
roi_viewer_flip_y_axis_button.on_click(roi_viewer_flip_y_axis)
roi_viewer_plot_tv_button.on_click(roi_viewer_plot_tv)

roi_viewer = figure(plot_width=825, plot_height=600, logo=None)
roi_viewer.patch('x', 'y', source=source_roi_viewer, color='blue', alpha=0.5)
roi_viewer.patch('x', 'y', source=source_roi2_viewer, color='green', alpha=0.5)
roi_viewer.patch('x', 'y', source=source_roi3_viewer, color='red', alpha=0.5)
roi_viewer.patch('x', 'y', source=source_roi4_viewer, color='orange', alpha=0.5)
roi_viewer.patch('x', 'y', source=source_tv, color='black', alpha=0.5)
roi_viewer.xaxis.axis_label = "Lateral DICOM Coordinate (mm)"
roi_viewer.yaxis.axis_label = "Anterior/Posterior DICOM Coordinate (mm)"

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# define main layout to pass to curdoc()
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
layout_query = column(row(main_add_selector_button,
                          main_add_range_button,
                          main_add_endpoint_button,
                          update_button,
                          calculate_review_dvh_button,
                          download_dropdown))


layout_dvhs = column(row(radio_group_dose, radio_group_volume),
                     row(select_reviewed_mrn, select_reviewed_dvh, review_rx, review_eud_a_value),
                     dvh_plots,
                     data_table_title,
                     data_table,
                     endpoint_table_title,
                     data_table_endpoints)

roi_viewer_layout = layout([[roi_viewer_mrn_select, roi_viewer_study_date_select, roi_viewer_uid_select],
                            [roi_viewer_roi_select, roi_viewer_slice_select,
                             roi_viewer_previous_slice, roi_viewer_next_slice],
                            [roi_viewer_roi2_select, roi_viewer_roi3_select, roi_viewer_roi4_select],
                            [roi_viewer_flip_text],
                            [roi_viewer_flip_x_axis_button, roi_viewer_flip_y_axis_button, roi_viewer_plot_tv_button],
                            [roi_viewer]])

layout_planning_data = column(rxs_table_title,
                              data_table_rxs,
                              plans_table_title,
                              data_table_plans,
                              beam_table_title,
                              data_table_beams,
                              beam_table_title2,
                              data_table_beams2)

layout_trending = column(control_chart_title,
                         row(control_chart_y, control_chart_lookback_units, control_chart_text_input,
                             control_chart_percentile, trend_update_button),
                         control_chart)

query_tab = Panel(child=layout_query, title='Query')
dvh_tab = Panel(child=layout_dvhs, title='DVHs')
roi_viewer_tab = Panel(child=roi_viewer_layout, title='ROI Viewer')
planning_data_tab = Panel(child=layout_planning_data, title='Planning Data')
trending_tab = Panel(child=layout_trending, title='Range-Variable Trending')

tabs = Tabs(tabs=[query_tab, dvh_tab, roi_viewer_tab, planning_data_tab, trending_tab])

# go ahead and add a selector row for the user
button_add_selector_row()

# Create the document Bokeh server will use to generate the webpage
curdoc().add_root(tabs)
curdoc().title = "DVH Analytics"
