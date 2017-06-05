#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
main program for Bokeh server for Plan Review
Created on Sun Apr 21 2017
@author: Dan Cutright, PhD
This module is still under development
"""

from __future__ import print_function
import numpy as np
import itertools
from bokeh.layouts import layout, column, row
from bokeh.models import ColumnDataSource, Legend, CustomJS, HoverTool
from bokeh.models.widgets import Select, Button, PreText, TableColumn, DataTable, \
    NumberFormatter, RadioButtonGroup, TextInput, RadioGroup
from bokeh.plotting import figure
from bokeh.io import curdoc
from roi_name_manager import DatabaseROIs
from analysis_tools import DVH, get_study_instance_uids
from sql_connector import DVH_SQL
from sql_to_python import QuerySQL
from bokeh.palettes import Category20_9 as palette
from datetime import datetime
from utilities import Temp_DICOM_FileSet
from dicompylercore import dvhcalc, dicomparser

# Declare variables
widget_row_origin = 2
db_rois = DatabaseROIs()
colors = itertools.cycle(palette)
query_row = []
query_row_type = []
endpoint_columns = {}
temp_dvh_info = Temp_DICOM_FileSet()
for i in range(0, 10):
    endpoint_columns[i] = ''
dvh_review_mrns = temp_dvh_info.mrn
if dvh_review_mrns[0] != '':
    dvh_review_rois = temp_dvh_info.get_roi_names(dvh_review_mrns[0]).values()
else:
    dvh_review_rois = ['']
x = []
y = []

# Initialize ColumnDataSource variables
temp = []
temp_vec = []
temp_null = []
for i in range(0, 6):
    temp.append(0)
    temp_vec.append([''])
    temp_null.append('')
source = ColumnDataSource(data=dict(x=temp_vec,
                                    y=temp_vec,
                                    roi_name=temp_null,
                                    volume=temp,
                                    min_dose=temp,
                                    mean_dose=temp,
                                    max_dose=temp,
                                    eud=temp,
                                    eud_a_value=temp,
                                    ep1=temp_null,
                                    ep2=temp_null,
                                    ep3=temp_null,
                                    ep4=temp_null,
                                    ep5=temp_null,
                                    ep6=temp_null,
                                    ep7=temp_null,
                                    ep8=temp_null))
source_patch = ColumnDataSource(data=dict(x_patch=[], y_patch=[]))
source_stats = ColumnDataSource(data=dict(x=[], min=[], q1=[], mean=[], median=[], q3=[], max=[]))
source_endpoint_names = ColumnDataSource(data=dict(ep1=[''], ep2=[''], ep3=[''], ep4=[''], ep5=[''],
                                                   ep6=[''], ep7=[''], ep8=['']))
source_endpoints = ColumnDataSource(data=dict())


# Categories map of dropdown values, SQL column, and SQL table (and data source for range_categories)
selector_categories = {'ROI Institutional Category': {'var_name': 'institutional_roi', 'table': 'DVHs'},
                       'ROI Physician Category': {'var_name': 'physician_roi', 'table': 'DVHs'},
                       'ROI Type': {'var_name': 'roi_type', 'table': 'DVHs'},
                       'Beam Energy': {'var_name': 'beam_energy', 'table': 'Beams'},
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
                       'Heterogeneity Correction': {'var_name': 'heterogeneity_correction', 'table': 'Plans'}}
range_categories = {'Age': {'var_name': 'age', 'table': 'Plans', 'units': ''},
                    'Birth Date': {'var_name': 'birth_date', 'table': 'Plans', 'units': ''},
                    'Planned Fractions': {'var_name': 'fxs', 'table': 'Plans', 'units': ''},
                    'Rx Dose': {'var_name': 'rx_dose', 'table': 'Plans', 'units': 'Gy'},
                    'Rx Isodose': {'var_name': 'rx_percent', 'table': 'Rxs', 'units': '%'},
                    'Simulation Date': {'var_name': 'sim_study_date', 'table': 'Plans', 'units': ''},
                    'Total Plan MU': {'var_name': 'total_mu', 'table': 'Plans', 'units': ''},
                    'Fraction Dose': {'var_name': 'fx_dose', 'table': 'Rxs', 'units': 'Gy'},
                    'Beam Dose': {'var_name': 'beam_dose', 'table': 'Beams', 'units': 'Gy'},
                    'Beam MU': {'var_name': 'beam_mu', 'table': 'Beams', 'units': ''},
                    'Control Point Count': {'var_name': 'control_point_count', 'table': 'Beams', 'units': ''},
                    'Collimator Angle': {'var_name': 'collimator_angle', 'table': 'Beams', 'units': 'deg'},
                    'Couch Angle': {'var_name': 'couch_angle', 'table': 'Beams', 'units': 'deg'},
                    'Gantry Start Angle': {'var_name': 'gantry_start', 'table': 'Beams', 'units': 'deg'},
                    'Gantry End Angle': {'var_name': 'gantry_end', 'table': 'Beams', 'units': 'deg'},
                    'SSD': {'var_name': 'ssd', 'table': 'Beams', 'units': 'cm'},
                    'ROI Min Dose': {'var_name': 'min_dose', 'table': 'DVHs', 'units': 'Gy'},
                    'ROI Mean Dose': {'var_name': 'mean_dose', 'table': 'DVHs', 'units': 'Gy'},
                    'ROI Max Dose': {'var_name': 'max_dose', 'table': 'DVHs', 'units': 'Gy'},
                    'ROI Volume': {'var_name': 'volume', 'table': 'DVHs', 'units': 'cc'}}


# Functions that add widget rows
def button_add_selector_row():
    global query_row_type
    old_label = main_add_selector_button.label
    old_type = main_add_selector_button.button_type
    main_add_selector_button.label = 'Updating Layout...'
    main_add_selector_button.button_type = 'warning'
    query_row.append(AddSelectorRow())
    layout.children.insert(widget_row_origin + len(query_row_type), query_row[-1].row)
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
    query_row.append(AddRangeRow())
    layout.children.insert(widget_row_origin + len(query_row_type), query_row[-1].row)
    query_row_type.append('range')
    update_update_button_status()
    main_add_range_button.label = old_label
    main_add_range_button.button_type = old_type


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


# main update function
def update_data():
    global query_row_type, query_row
    old_update_button_label = update_button.label
    old_update_button_type = update_button.button_type
    update_button.label = 'Updating...'
    update_button.button_type = 'warning'
    uids, dvh_query_str = get_query()
    print(str(datetime.now()), 'getting dvh data', sep=' ')
    current_dvhs = DVH(uid=uids, dvh_condition=dvh_query_str)
    print(str(datetime.now()), 'initializing source data', current_dvhs.query, sep=' ')
    update_dvh_data(current_dvhs)
    update_all_range_endpoints()
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
        update_button.label = "Update Stats"


# This function retuns the list of information needed to execute QuerySQL from
# SQL_to_Python.py (i.e., uids and dvh_condition
def get_query():
    global query_row_type, query_row
    plan_query_map = {}
    rx_query_map = {}
    beam_query_map = {}
    dvh_query_map = {}
    for i in range(1, len(query_row)):
        if query_row_type[i] in {'selector', 'range'}:
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
class AddSelectorRow:
    def __init__(self):

        self.id = len(query_row)
        self.category_options = selector_categories.keys()
        self.category_options.sort()
        self.select_category = Select(value="ROI Institutional Category", options=self.category_options, width=450)
        self.select_category.on_change('value', self.update_selector_values)

        self.sql_table = selector_categories[self.select_category.value]['table']
        self.var_name = selector_categories[self.select_category.value]['var_name']
        self.values = DVH_SQL().get_unique_values(self.sql_table, self.var_name)
        self.select_value = Select(value=self.values[0], options=self.values, width=450)
        self.select_value.on_change('value', self.selector_values_ticker)

        self.delete_last_row = Button(label="Delete", button_type="warning", width=100)
        self.delete_last_row.on_click(self.delete_row)

        self.row = row(self.select_category,
                       self.select_value,
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
        del (layout.children[widget_row_origin + self.id])
        query_row_type.pop(self.id)
        query_row.pop(self.id)
        update_query_row_ids()
        update_update_button_status()


# This class adds a row suitable to filter continuous data from the SQL database
class AddRangeRow:
    def __init__(self):
        self.id = len(query_row)
        self.category_options = range_categories.keys()
        self.category_options.sort()
        self.select_category = Select(value=self.category_options[-1], options=self.category_options, width=450)
        self.select_category.on_change('value', self.update_range_values_ticker)

        self.sql_table = range_categories[self.select_category.value]['table']
        self.var_name = range_categories[self.select_category.value]['var_name']
        self.min_value = []
        self.max_value = []
        self.text_min = TextInput(value='', title='', width=225)
        self.text_min.on_change('value', self.check_for_start_date_ticker)
        self.text_max = TextInput(value='', title='', width=225)
        self.text_max.on_change('value', self.check_for_end_date_ticker)
        self.update_range_values(self.select_category.value)

        self.delete_last_row = Button(label="Delete", button_type="warning", width=100)
        self.delete_last_row.on_click(self.delete_row)

        self.row = row([self.select_category,
                        self.text_min,
                        self.text_max,
                        self.delete_last_row])

    def check_for_start_date_ticker(self, attrname, old, new):
        if self.select_category.value.lower().find("date") > -1:
            self.text_min.value = date_str_to_SQL_format(new, type='start')

    def check_for_end_date_ticker(self, attrname, old, new):
        if self.select_category.value.lower().find("date") > -1:
            self.text_max.value = date_str_to_SQL_format(new, type='end')

    def update_range_values_ticker(self, attrname, old, new):
        self.update_range_values(new)

    def update_range_values(self, new):
        table_new = range_categories[new]['table']
        var_name_new = range_categories[new]['var_name']
        self.min_value = DVH_SQL().get_min_value(table_new, var_name_new)
        self.max_value = DVH_SQL().get_max_value(table_new, var_name_new)
        self.text_min.title = 'Min: ' + str(self.min_value) + ' ' + range_categories[new]['units']
        self.text_max.title = 'Max: ' + str(self.max_value) + ' ' + range_categories[new]['units']
        update_update_button_status()

    def delete_row(self):
        del (layout.children[widget_row_origin + self.id])
        query_row_type.pop(self.id)
        query_row.pop(self.id)
        update_query_row_ids()
        update_update_button_status()


# This class adds a row to calculate specified DVH endpoints
class AddEndPointRow:
    def __init__(self, instance):

        self.id = len(query_row)
        self.options = ["Dose to Vol", "Vol of Dose"]
        self.select_category = RadioButtonGroup(labels=self.options, active=0, width=225)
        self.select_category.on_change('active', self.endpoint_category_ticker)

        self.unit_labels = [["%", "cc"], ["%", "Gy"]]

        self.units_out = RadioButtonGroup(labels=self.unit_labels[1], active=1, width=225)
        self.units_out.on_change('active', self.endpoint_units_out_ticker)

        self.text_input = TextInput(value='', title="Volume (%):", width=300)
        self.text_input.on_change('value', self.endpoint_calc_ticker)

        self.units = RadioButtonGroup(labels=self.unit_labels[0], active=0, width=225)
        self.units.on_change('active', self.endpoint_units_ticker)

        self.label = PreText(text='Column ' + str(instance), width=100)

        self.row = row(self.label,
                       self.select_category,
                       self.units_out,
                       self.text_input,
                       self.units)

    def endpoint_category_ticker(self, attrname, old, new):
        self.update_text_input_title()
        self.units.labels = self.unit_labels[new]
        self.units_out.labels = self.unit_labels[old]
        if self.text_input.value != '':
            update_endpoint_data()

    def endpoint_calc_ticker(self, attrname, old, new):
        if self.text_input.value != '':
            update_endpoint_data()

    def endpoint_units_ticker(self, attrname, old, new):
        self.update_text_input_title()
        if self.text_input.value != '':
            update_endpoint_data()

    def endpoint_units_out_ticker(self, attrname, old, new):
        if self.text_input.value != '':
            update_endpoint_data()

    def update_text_input_title(self):
        if self.select_category.active == 0:
            self.text_input.title = 'Volume (' + self.unit_labels[0][self.units.active] + '):'
        elif self.select_category.active == 1:
            self.text_input.title = 'Dose (' + self.unit_labels[1][self.units.active] + '):'


# input is a DVH class from Analysis_Tools.py
# This function creates a new ColumnSourceData and calls
# the functions to update beam, rx, and plans ColumnSourceData variables
def update_dvh_data(dvh):

    update_button.label = 'Getting DVH data...'
    print(str(datetime.now()), 'updating dvh data', sep=' ')
    line_colors = []
    for i, color in itertools.izip(range(0, dvh.count), colors):
        line_colors.append(color)

    x_axis = np.add(np.linspace(0, dvh.bin_count, dvh.bin_count) / float(100), 0.005)

    x_data = []
    y_data = []
    endpoint_columns = []
    x_scale = []
    y_scale = []
    for i in range(0, dvh.count):
        endpoint_columns.append('')
        x_data.append(x_axis.tolist())
        y_data.append(dvh.dvh[:, i].tolist())

    print(str(datetime.now()), 'beginning stat calcs', sep=' ')
    update_button.label = 'Calculating stats...'

    print(str(datetime.now()), 'calculating patches', sep=' ')
    stat_dvhs = dvh.get_standard_stat_dvh(dose='absolute', volume='relative')

    print(str(datetime.now()), 'patches calculated', sep=' ')

    source_patch.data = {'x_patch': np.append(x_axis, x_axis[::-1]).tolist(),
                         'y_patch': np.append(stat_dvhs['q3'], stat_dvhs['q1'][::-1]).tolist()}
    print(str(datetime.now()), 'patches set', sep=' ')
    source_stats.data = {'x': x_axis.tolist(),
                         'min': stat_dvhs['min'].tolist(),
                         'q1': stat_dvhs['q1'].tolist(),
                         'mean': stat_dvhs['mean'].tolist(),
                         'median': stat_dvhs['median'].tolist(),
                         'q3': stat_dvhs['q3'].tolist(),
                         'max': stat_dvhs['max'].tolist()}

    print(str(datetime.now()), 'stats set', sep=' ')

    update_beam_data(dvh.study_instance_uid)
    update_plan_data(dvh.study_instance_uid)
    update_rx_data(dvh.study_instance_uid)


# updates beam ColumnSourceData for a given list of uids
def update_beam_data(uids):
    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    beam_data = QuerySQL('Beams', cond_str)


# updates plan ColumnSourceData for a given list of uids
def update_plan_data(uids):

    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    plan_data = QuerySQL('Plans', cond_str)


# updates rx ColumnSourceData for a given list of uids
def update_rx_data(uids):

    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    rx_data = QuerySQL('Rxs', cond_str)


# updates endpoint ColumnSourceData for a given DVH class from Analysis_Tools.py
# note that endpoint ColumnSourceData exits in dvh data ColumnSourceData (i.e.,
# the main ColumnSourceData variable, or 'source')
def update_endpoint_data():
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
            counter += 1
    for i in range(counter, 8):
        endpoints_map[i] = []
        for j in range(0, 1):
            endpoints_map[i].append('')

    tuple_list = {}
    for i in range(0, 8):
        current_tuple_list = []
        for j in range(0, 1):
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


def update_dvh_review_mrns():
    global temp_dvh_info, dvh_review_mrns
    temp_dvh_info = Temp_DICOM_FileSet()
    dvh_review_mrns = temp_dvh_info.mrn
    select_reviewed_mrn.options = dvh_review_mrns


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
    calculate_review_dvh_button.button_type = 'warning'
    calculate_review_dvh_button.label = 'Calculating...'

    file_index = temp_dvh_info.mrn.index(select_reviewed_mrn.value)
    roi_index = dvh_review_rois.index(select_reviewed_dvh.value)
    structure_file = temp_dvh_info.structure[file_index]
    dose_file = temp_dvh_info.dose[file_index]
    key = temp_dvh_info.get_roi_names(select_reviewed_mrn.value).keys()[roi_index]

    rt_st = dicomparser.DicomParser(structure_file)
    rt_structures = rt_st.GetStructures()
    review_dvh = dvhcalc.get_dvh(structure_file, dose_file, key)

    roi_name = rt_structures[key]['name']
    volume = review_dvh.volume
    min_dose = review_dvh.min
    mean_dose = review_dvh.mean
    max_dose = review_dvh.max
    eud = 0
    eud_a_value = 0
    x = review_dvh.bincenters
    y = np.divide(review_dvh.counts, max(review_dvh.counts)).tolist()

    patches = {'x': [(0, x)],
               'y': [(0, y)],
               'roi_name': [(0, roi_name)],
               'volume': [(0, volume)],
               'min_dose': [(0, min_dose)],
               'mean_dose': [(0, mean_dose)],
               'max_dose': [(0, max_dose)],
               'eud': [(0, eud)],
               'eud_a_value': [(0, eud_a_value)]}

    source.patch(patches)

    calculate_review_dvh_button.button_type = initial_button_type
    calculate_review_dvh_button.label = initial_button_label


def date_str_to_SQL_format(date, **kwargs):

    if kwargs['type'] == 'start':
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


# set up layout
tools = "pan,wheel_zoom,box_zoom,reset,crosshair,save,hover"
dvh_plots = figure(plot_width=1000, plot_height=400, tools=tools, logo=None, active_drag="box_zoom")

# Add statistical plots to figure
stats_min = dvh_plots.line('x', 'min',
                           source=source_stats,
                           line_width=2,
                           color='black',
                           line_dash='dotted',
                           alpha=0.2)
stats_q1 = dvh_plots.line('x', 'q1',
                          source=source_stats,
                          line_width=0.5,
                          color='black',
                          alpha=0.2)
stats_median = dvh_plots.line('x', 'median',
                              source=source_stats,
                              line_width=2,
                              color='lightpink',
                              line_dash='dashed',
                              alpha=0.75)
stats_mean = dvh_plots.line('x', 'mean',
                            source=source_stats,
                            line_width=2,
                            color='lightseagreen',
                            line_dash='dashed',
                            alpha=0.5)
stats_q3 = dvh_plots.line('x', 'q3',
                          source=source_stats,
                          line_width=0.5,
                          color='black',
                          alpha=0.2)
stats_max = dvh_plots.line('x', 'max',
                           source=source_stats,
                           line_width=2,
                           color='black',
                           line_dash='dotted',
                           alpha=0.2)

# Add all DVHs, but hide them until selected
dvh_plots.multi_line('x', 'y', source=source, line_width=2)

# Shaded region between Q1 and Q3
dvh_plots.patch('x_patch', 'y_patch',
                source=source_patch,
                alpha=0.15)

# Set x and y axis labels
dvh_plots.xaxis.axis_label = "Dose (Gy)"
dvh_plots.yaxis.axis_label = "Normalized Volume"

# Set the legend (for stat dvhs only)
legend_stats = Legend(items=[
        ("Max", [stats_max]),
        ("Q3", [stats_q3]),
        ("Median", [stats_median]),
        ("Mean", [stats_mean]),
        ("Q1", [stats_q1]),
        ("Min", [stats_min])
    ], location=(0, 30))

# Add the layout outside the plot, clicking legend item hides the line
dvh_plots.add_layout(legend_stats, 'right')
dvh_plots.legend.click_policy = "hide"

# Set up DataTable for dvhs
data_table_title = PreText(text="DVHs", width=1000)
columns = [TableColumn(field="roi_name", title="ROI Name"),
           TableColumn(field="volume", title="Volume", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="min_dose", title="Min Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="mean_dose", title="Mean Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="max_dose", title="Max Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="eud", title="EUD", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="eud_a_value", title="a", width=80)]
data_table = DataTable(source=source, columns=columns, width=1000, height=60)

# Set up EndPoint DataTable
endpoint_table_title = PreText(text="DVH Endpoints", width=1000)
columns = [TableColumn(field="ep1", title=endpoint_columns[0], width=120),
           TableColumn(field="ep2", title=endpoint_columns[1], width=120),
           TableColumn(field="ep3", title=endpoint_columns[2], width=120),
           TableColumn(field="ep4", title=endpoint_columns[3], width=120),
           TableColumn(field="ep5", title=endpoint_columns[4], width=120),
           TableColumn(field="ep6", title=endpoint_columns[5], width=120),
           TableColumn(field="ep7", title=endpoint_columns[6], width=120),
           TableColumn(field="ep8", title=endpoint_columns[7], width=120)]
data_table_endpoints = DataTable(source=source, columns=columns, width=1000, height=75)

# Setup selectors for dvh review
select_reviewed_mrn = Select(title='MRN to review',
                             value=dvh_review_mrns[0],
                             options=dvh_review_mrns,
                             width=200)
select_reviewed_mrn.on_change('value', update_dvh_review_rois)

select_reviewed_dvh = Select(title='ROI',
                             value=dvh_review_rois[0],
                             options=dvh_review_rois,
                             width=500)

calculate_review_dvh_button = Button(label="Calculate Review DVH",
                                     button_type="success",
                                     width=200)
calculate_review_dvh_button.on_click(calculate_review_dvh)

update_dvh_review_mrns()

# Begin defining main row of widgets below figure

# define Update button
update_button = Button(label="Update Stats", button_type="success", width=200)
update_button.on_click(update_data)

# define button to widget row for discrete data filtering
main_add_selector_button = Button(label="Add Selection Filter", button_type="primary", width=200)
main_add_selector_button.on_click(button_add_selector_row)

# define button to widget row for continuous data filtering
main_add_range_button = Button(label="Add Range Filter", button_type="primary", width=200)
main_add_range_button.on_click(button_add_range_row)

# not for display, but add these buttons to query_row
# query row is simply used to keep track of pointers to query rows
# allows code to dynamically add widgets and keep button functionality contained
query_row.append(row(update_button, main_add_selector_button, main_add_range_button))
query_row_type.append('main')

# define main layout to pass to curdoc()
layout = column(dvh_plots,
                row(select_reviewed_mrn, select_reviewed_dvh),
                row(main_add_selector_button,
                    main_add_range_button,
                    update_button,
                    calculate_review_dvh_button),
                data_table_title,
                data_table,
                endpoint_table_title,
                data_table_endpoints,
                AddEndPointRow(1).row,
                AddEndPointRow(2).row,
                AddEndPointRow(3).row,
                AddEndPointRow(4).row,
                AddEndPointRow(5).row,
                AddEndPointRow(6).row,
                AddEndPointRow(7).row,
                AddEndPointRow(8).row,)

# go ahead and add a selector row for the user
button_add_selector_row()

# Create the document Bokeh server will use to generate the webpage
curdoc().add_root(layout)
curdoc().title = "DVH Analytics: Plan Review"
