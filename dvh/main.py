#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
main program for Bokeh server
Created on Sun Apr 21 2017
@author: Dan Cutright, PhD
"""


from __future__ import print_function
from analysis_tools import DVH, get_study_instance_uids, calc_eud, get_eud_a_values
from utilities import Temp_DICOM_FileSet
from sql_connector import DVH_SQL
from sql_to_python import QuerySQL
import numpy as np
import itertools
from datetime import datetime
from os.path import dirname, join
from bokeh.layouts import layout, column, row
from bokeh.models import ColumnDataSource, Legend, CustomJS, HoverTool
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.palettes import Colorblind8 as palette
from bokeh.models.widgets import Select, Button, Div, TableColumn, DataTable, \
    NumberFormatter, RadioButtonGroup, TextInput, RadioGroup, CheckboxButtonGroup
from dicompylercore import dicomparser, dvhcalc

# Declare variables
colors = itertools.cycle(palette)
current_dvh = []
update_warning = True
query_row = []
query_row_type = []
endpoint_columns = {}
x = []
y = []
eud_a_values = get_eud_a_values()
widget_row_start = 3

for i in range(0, 10):
    endpoint_columns[i] = ''

temp_dvh_info = Temp_DICOM_FileSet()
dvh_review_mrns = temp_dvh_info.mrn
if dvh_review_mrns[0] != '':
    dvh_review_rois = temp_dvh_info.get_roi_names(dvh_review_mrns[0]).values()

else:
    dvh_review_rois = ['']

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
                       'Scan Mode': {'var_name': 'scan_mode', 'table': 'Beams'}}
range_categories = {'Age': {'var_name': 'age', 'table': 'Plans', 'units': '', 'source': source_plans},
                    'Beam Energy Min': {'var_name': 'beam_energy_min', 'table': 'Beams', 'units': '', 'source': source_beams},
                    'Beam Energy Max': {'var_name': 'beam_energy_max', 'table': 'Beams', 'units': '', 'source': source_beams},
                    'Birth Date': {'var_name': 'birth_date', 'table': 'Plans', 'units': '', 'source': source_plans},
                    'Planned Fractions': {'var_name': 'fxs', 'table': 'Plans', 'units': '', 'source': source_plans},
                    'Rx Dose': {'var_name': 'rx_dose', 'table': 'Plans', 'units': 'Gy', 'source': source_plans},
                    'Rx Isodose': {'var_name': 'rx_percent', 'table': 'Rxs', 'units': '%', 'source': source_rxs},
                    'Simulation Date': {'var_name': 'sim_study_date', 'table': 'Plans', 'units': '', 'source': source_plans},
                    'Total Plan MU': {'var_name': 'total_mu', 'table': 'Plans', 'units': '', 'source': source_plans},
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
                    'ROI Volume': {'var_name': 'volume', 'table': 'DVHs', 'units': 'cc', 'source': source}}


# Functions that add widget rows
def button_add_selector_row():
    global query_row_type
    old_label = main_add_selector_button.label
    old_type = main_add_selector_button.button_type
    main_add_selector_button.label = 'Updating Layout...'
    main_add_selector_button.button_type = 'warning'
    query_row.append(SelectorRow())
    layout.children.insert(widget_row_start + len(query_row_type), query_row[-1].row)
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
    layout.children.insert(widget_row_start + len(query_row_type), query_row[-1].row)
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
    layout.children.insert(widget_row_start + len(query_row_type), query_row[-1].row)
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
    global query_row_type, query_row, current_dvh
    old_update_button_label = update_button.label
    old_update_button_type = update_button.button_type
    update_button.label = 'Updating...'
    update_button.button_type = 'warning'
    uids, dvh_query_str = get_query()
    print(str(datetime.now()), 'getting dvh data', sep=' ')
    current_dvh = DVH(uid=uids, dvh_condition=dvh_query_str)
    print(str(datetime.now()), 'initializing source data ', current_dvh.query, sep=' ')
    update_dvh_data(current_dvh)
    calculate_review_dvh()
    update_all_range_endpoints()
    update_endpoint_data(current_dvh)
    update_button.label = old_update_button_label
    update_button.button_type = old_update_button_type


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
            active_group = 0
        elif kwargs['group'] == 2:
            active_group = 1
    else:
        active_group = 2

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
    plan_query_str = ' and '.join(plan_query_str)
    rx_query_str = ' and '.join(rx_query_str)
    beam_query_str = ' and '.join(beam_query_str)
    dvh_query_str = ' and '.join(dvh_query_str)

    print(str(datetime.now()), 'getting uids', sep=' ')
    print(str(datetime.now()), 'Plans =', plan_query_str, sep=' ')
    print(str(datetime.now()), 'Rxs =', rx_query_str, sep=' ')
    print(str(datetime.now()), 'Beams =', beam_query_str, sep=' ')
    uids = get_study_instance_uids(Plans=plan_query_str, Rxs=rx_query_str, Beams=beam_query_str)['union']

    return uids, dvh_query_str


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
        new_options = DVH_SQL().get_unique_values(table_new, var_name_new)
        self.select_value.options = new_options
        self.select_value.value = new_options[0]
        update_update_button_status()

    def selector_values_ticker(self, attrname, old, new):
        update_update_button_status()

    def delete_row(self):
        del (layout.children[widget_row_start + self.id])
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
            self.min_value = min(range_categories[new]['source'].data[var_name_new])
            self.max_value = max(range_categories[new]['source'].data[var_name_new])
        else:
            self.min_value = DVH_SQL().get_min_value(table_new, var_name_new)
            self.max_value = DVH_SQL().get_max_value(table_new, var_name_new)
        self.text_min.title = 'Min: ' + str(self.min_value) + ' ' + range_categories[new]['units']
        self.text_max.title = 'Max: ' + str(self.max_value) + ' ' + range_categories[new]['units']
        update_update_button_status()

    def delete_row(self):
        del (layout.children[widget_row_start + self.id])
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

        self.text_input = TextInput(value='', title="Volume (%):", width=210)
        self.text_input.on_change('value', self.endpoint_calc_ticker)

        self.units = RadioButtonGroup(labels=self.unit_labels[0], active=0, width=390)
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
            update_endpoint_data(current_dvh)

    def endpoint_calc_ticker(self, attrname, old, new):
        if self.text_input.value != '':
            update_endpoint_data(current_dvh)

    def endpoint_units_ticker(self, attrname, old, new):
        self.update_text_input_title()
        if self.text_input.value != '':
            update_endpoint_data(current_dvh)

    def endpoint_units_out_ticker(self, attrname, old, new):
        if self.text_input.value != '':
            update_endpoint_data(current_dvh)

    def delete_row(self):
        del (layout.children[widget_row_start + self.id])
        query_row_type.pop(self.id)
        query_row.pop(self.id)
        update_query_row_ids()
        update_endpoint_data(current_dvh)

    def update_text_input_title(self):
        if self.select_category.active == 0:
            self.text_input.title = 'Volume (' + self.unit_labels[0][self.units.active] + '):'
        elif self.select_category.active == 1:
            self.text_input.title = 'Dose (' + self.unit_labels[1][self.units.active] + '):'


# input is a DVH class from Analysis_Tools.py
# This function creates a new ColumnSourceData and calls
# the functions to update beam, rx, and plans ColumnSourceData variables
def update_dvh_data(dvh):

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

    x_axis = np.add(np.linspace(0, dvh.bin_count, dvh.bin_count) / float(100), 0.005)

    print(str(datetime.now()), 'source.data set', sep=' ')
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
        uids, dvh_query_str = get_query(group=1)
        dvh_group_1 = DVH(uid=uids, dvh_condition=dvh_query_str)
        stat_dvhs_1 = dvh_group_1.get_standard_stat_dvh(dose=stat_dose_scale, volume=stat_volume_scale)

        if radio_group_dose.active == 1:
            x_axis_1 = dvh_group_1.get_stat_dvh(type=False, dose=stat_dose_scale)
        else:
            x_axis_1 = np.add(np.linspace(0, dvh_group_1.bin_count, dvh_group_1.bin_count) / float(100), 0.005)

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
        uids, dvh_query_str = get_query(group=2)
        dvh_group_2 = DVH(uid=uids, dvh_condition=dvh_query_str)

        stat_dvhs_2 = dvh_group_2.get_standard_stat_dvh(dose=stat_dose_scale, volume=stat_volume_scale)

        if radio_group_dose.active == 1:
            x_axis_2 = dvh_group_2.get_stat_dvh(type=False, dose=stat_dose_scale)
        else:
            x_axis_2 = np.add(np.linspace(0, dvh_group_2.bin_count, dvh_group_2.bin_count) / float(100), 0.005)

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

    for n in range(0, 6):
        if group_1_count > 0:
            dvh.mrn.append(y_names[n])
            dvh.roi_name.append('Blue Group')
            x_data.append(x_axis.tolist())
            current = stat_dvhs_1[y_names[n].lower()].tolist()
            y_data.append(current)
        if group_2_count > 0:
            dvh.mrn.append(y_names[n])
            dvh.roi_name.append('Red Group')
            x_data.append(x_axis.tolist())
            current = stat_dvhs_2[y_names[n].lower()].tolist()
            y_data.append(current)

    # Adjust dvh object to include stats data
    if extra_rows > 0:
        dvh.study_instance_uid.extend(['N/A'] * extra_rows)
        dvh.institutional_roi.extend(['N/A'] * extra_rows)
        dvh.physician_roi.extend(['N/A'] * extra_rows)
        dvh.roi_type.extend(['Stat'] * extra_rows)
        dvh.eud_a_value.extend(['N/A'] * extra_rows)
    if group_1_count > 0:
        dvh.rx_dose.extend(calc_stats(dvh_group_1.rx_dose))
        dvh.volume.extend(calc_stats(dvh_group_1.volume))
        dvh.min_dose.extend(calc_stats(dvh_group_1.min_dose))
        dvh.mean_dose.extend(calc_stats(dvh_group_1.mean_dose))
        dvh.max_dose.extend(calc_stats(dvh_group_1.max_dose))
        dvh.eud.extend(calc_stats(dvh_group_1.eud))
    if group_2_count > 0:
        dvh.rx_dose.extend(calc_stats(dvh_group_2.rx_dose))
        dvh.volume.extend(calc_stats(dvh_group_2.volume))
        dvh.min_dose.extend(calc_stats(dvh_group_2.min_dose))
        dvh.mean_dose.extend(calc_stats(dvh_group_2.mean_dose))
        dvh.max_dose.extend(calc_stats(dvh_group_2.max_dose))
        dvh.eud.extend(calc_stats(dvh_group_2.eud))

    # Adjust dvh object for review dvh
    dvh.mrn.insert(0, select_reviewed_mrn.value)
    dvh.study_instance_uid.insert(0, '')
    dvh.institutional_roi.insert(0, '')
    dvh.physician_roi.insert(0, '')
    dvh.roi_name.insert(0, select_reviewed_dvh.value)
    dvh.roi_type.insert(0, 'Review')
    dvh.rx_dose.insert(0, 'N/A')
    dvh.volume.insert(0, '')
    dvh.min_dose.insert(0, '')
    dvh.mean_dose.insert(0, '')
    dvh.max_dose.insert(0, '')
    dvh.eud.insert(0, 'N/A')
    dvh.eud_a_value.insert(0, 'N/A')
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
                   'min_dose': dvh.min_dose,
                   'mean_dose': dvh.mean_dose,
                   'max_dose': dvh.max_dose,
                   'eud': dvh.eud,
                   'eud_a_value': dvh.eud_a_value,
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

    update_beam_data(dvh.study_instance_uid)
    update_plan_data(dvh.study_instance_uid)
    update_rx_data(dvh.study_instance_uid)


# updates beam ColumnSourceData for a given list of uids
def update_beam_data(uids):

    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    beam_data = QuerySQL('Beams', cond_str)

    source_beams.data = {'mrn': beam_data.mrn,
                         'uid': beam_data.study_instance_uid,
                         'beam_dose': beam_data.beam_dose,
                         'beam_energy_min': beam_data.beam_energy_min,
                         'beam_energy_max': beam_data.beam_energy_max,
                         'beam_mu': beam_data.beam_mu,
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

    source_plans.data = {'mrn': plan_data.mrn,
                         'uid': plan_data.study_instance_uid,
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
                         'heterogeneity_correction': plan_data.heterogeneity_correction}


# updates rx ColumnSourceData for a given list of uids
def update_rx_data(uids):

    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    rx_data = QuerySQL('Rxs', cond_str)

    source_rxs.data = {'mrn': rx_data.mrn,
                       'uid': rx_data.study_instance_uid,
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
def update_endpoint_data(dvh):

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
    counter = 0
    for i in range(0, len(query_row)):
        if query_row_type[i] == 'endpoint' and counter < 8:
            output_unit = ['Gy', 'cc']
            x = float(query_row[i].text_input.value)
            x_for_text = x
            if query_row[i].units.active == 0:
                endpoint_input = 'relative'
                units = query_row[i].units.labels[0]
                x /= 100
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
            else:
                endpoint_columns[counter] = 'V_' + str(x_for_text) + units + ' (' + output_unit[1] + ')'
                endpoints_map[counter] = dvh.get_volume_of_dose(x, input=endpoint_input, output=endpoint_output)
            endpoints_map[counter].extend(calc_stats(endpoints_map[counter][0:dvh.count]))
            counter += 1
    for i in range(counter, 8):
        endpoints_map[i] = []
        for j in range(0, dvh.count + extra_rows):
            endpoints_map[i].append('')

    tuple_list = {}
    for i in range(0, 8):
        current_tuple_list = []
        for j in range(1, dvh.count + extra_rows + 1):
            current_tuple_list.append(tuple([j, endpoints_map[i][j-1]]))
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


def calculate_review_dvh():
    global temp_dvh_info, dvh_review_rois, x, y

    initial_button_type = calculate_review_dvh_button.button_type
    initial_button_label = calculate_review_dvh_button.label

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
            rx_dose = float(dicompyler_plan['rxdose']) / 100
            review_rx.value = str(round(rx_dose, 2))
        else:
            rx_dose = round(float(review_rx.value), 2)
        if not review_eud_a_value.value:
            eud_a_value = float(1)
        else:
            eud_a_value = float(review_eud_a_value.value)

        x = review_dvh.bincenters
        y = np.divide(review_dvh.counts, max(review_dvh.counts))

        eud = calc_eud(y, eud_a_value)

        if radio_group_dose.active == 1:
            f = 5000
            bin_count = len(x)
            new_bin_count = int(bin_count * f / (rx_dose * 100))

            x1 = np.linspace(0, bin_count, bin_count)
            x2 = np.multiply(np.linspace(0, new_bin_count, new_bin_count), rx_dose * float(100) / f)
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

        source.patch(patches)

    calculate_review_dvh_button.button_type = initial_button_type
    calculate_review_dvh_button.label = initial_button_label


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
data_table_title = Div(text="<b>DVHs</b>", width=1000)
columns = [TableColumn(field="mrn", title="MRN / Stat", width=175),
           TableColumn(field="roi_name", title="ROI Name"),
           TableColumn(field="roi_type", title="ROI Type", width=80),
           TableColumn(field="rx_dose", title="Rx Dose", width=100, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="volume", title="Volume", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="min_dose", title="Min Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="mean_dose", title="Mean Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="max_dose", title="Max Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="eud", title="EUD", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="eud_a_value", title="a", width=80)]
data_table = DataTable(source=source, columns=columns, width=1000)

# Set up EndPoint DataTable
endpoint_table_title = Div(text="<b>DVH Endpoints</b>", width=1000)
columns = [TableColumn(field="mrn", title="MRN", width=160),
           TableColumn(field="ep1", title=endpoint_columns[0], width=120),
           TableColumn(field="ep2", title=endpoint_columns[1], width=120),
           TableColumn(field="ep3", title=endpoint_columns[2], width=120),
           TableColumn(field="ep4", title=endpoint_columns[3], width=120),
           TableColumn(field="ep5", title=endpoint_columns[4], width=120),
           TableColumn(field="ep6", title=endpoint_columns[5], width=120),
           TableColumn(field="ep7", title=endpoint_columns[6], width=120),
           TableColumn(field="ep8", title=endpoint_columns[7], width=120)]
data_table_endpoints = DataTable(source=source, columns=columns, width=1000)

# Set up Beams DataTable
beam_table_title = Div(text="<b>Beams</b>", width=1500)
columns = [TableColumn(field="mrn", title="MRN", width=105),
           TableColumn(field="beam_number", title="Beam", width=50),
           TableColumn(field="fx_count", title="Fxs", width=50),
           TableColumn(field="fx_grp_beam_count", title="Beams", width=50),
           TableColumn(field="fx_grp_number", title="Rx Grp", width=60),
           TableColumn(field="beam_name", title="Name", width=150),
           TableColumn(field="beam_dose", title="Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="beam_energy_min", title="Energy Min", width=80),
           TableColumn(field="beam_energy_max", title="Energy Max", width=80),
           TableColumn(field="beam_mu", title="MU", width=100, formatter=NumberFormatter(format="0.0")),
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
           TableColumn(field="tx_site", title="Tx Site")]
data_table_plans = DataTable(source=source_plans, columns=columns, width=1200)

# Set up Rxs DataTable
rxs_table_title = Div(text="<b>Rxs</b>", width=1000)
columns = [TableColumn(field="mrn", title="MRN"),
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
data_table_rxs = DataTable(source=source_rxs, columns=columns, width=1000)

# Setup axis normalization radio buttons
radio_group_dose = RadioGroup(labels=["Absolute Dose", "Relative Dose (Rx)"], active=0, width=200)
radio_group_dose.on_change('active', radio_group_dose_ticker)
radio_group_volume = RadioGroup(labels=["Absolute Volume", "Relative Volume"], active=1, width=200)
radio_group_volume.on_change('active', radio_group_volume_ticker)

# Setup selectors for dvh review
select_reviewed_mrn = Select(title='MRN to review',
                             value=dvh_review_mrns[0],
                             options=dvh_review_mrns,
                             width=300)
select_reviewed_mrn.on_change('value', update_dvh_review_rois)

select_reviewed_dvh = Select(title='ROI to review',
                             value=dvh_review_rois[0],
                             options=dvh_review_rois,
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
download_button = Button(label="Download", button_type="default", width=100)
download_button.callback = CustomJS(args=dict(source=source,
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

# define main layout to pass to curdoc()
layout = column(row(radio_group_dose, radio_group_volume),
                row(select_reviewed_mrn, select_reviewed_dvh, review_rx, review_eud_a_value),
                dvh_plots,
                row(main_add_selector_button,
                    main_add_range_button,
                    main_add_endpoint_button,
                    update_button,
                    calculate_review_dvh_button,
                    download_button),
                data_table_title,
                data_table,
                endpoint_table_title,
                data_table_endpoints,
                rxs_table_title,
                data_table_rxs,
                plans_table_title,
                data_table_plans,
                beam_table_title,
                data_table_beams,
                beam_table_title2,
                data_table_beams2)

# go ahead and add a selector row for the user
button_add_selector_row()

# Create the document Bokeh server will use to generate the webpage
curdoc().add_root(layout)
curdoc().title = "DVH Analytics"
