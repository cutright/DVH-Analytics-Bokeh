#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
main program for Bokeh server
Created on Sun Apr 21 2017
@author: Dan Cutright, PhD
"""

import numpy as np
import itertools
from bokeh.layouts import layout, column, row
from bokeh.models import ColumnDataSource, Legend, CustomJS, HoverTool
from bokeh.models.widgets import Select, Button, PreText, TableColumn, DataTable, NumberFormatter, RadioButtonGroup, TextInput, RadioGroup
from bokeh.plotting import figure
from bokeh.io import curdoc
from ROI_Name_Manager import DatabaseROIs
from Analysis_Tools import DVH, get_study_instance_uids
from DVH_SQL import DVH_SQL
from SQL_to_Python import QuerySQL
from bokeh.palettes import Category20_9 as palette
from datetime import datetime
from os.path import dirname, join

db_rois = DatabaseROIs()
colors = itertools.cycle(palette)
current_dvh = []
update_warning = True

# Initialize variables
source = ColumnDataSource(data=dict(color=[], x=[], y=[], mrn=[],
                                    ep1=[], ep2=[], ep3=[], ep4=[], ep5=[], ep6=[], ep7=[], ep8=[]))
source_patch = ColumnDataSource(data=dict(x_patch=[], y_patch=[]))
source_stats = ColumnDataSource(data=dict(x=[], min=[], q1=[], mean=[], median=[], q3=[], max=[]))
source_beams = ColumnDataSource(data=dict())
source_plans = ColumnDataSource(data=dict())
source_rxs = ColumnDataSource(data=dict())
source_endpoint_names = ColumnDataSource(data=dict(ep1=[], ep2=[], ep3=[], ep4=[], ep5=[], ep6=[], ep7=[], ep8=[]))
source_endpoints = ColumnDataSource(data=dict())
endpoint_columns = {}
for i in range(0, 10):
    endpoint_columns[i] = ''

query_row = []
query_row_type = []

# Get ROI maps
db_rois = DatabaseROIs()

# Categories map of dropdown values, SQL column, and SQL table
selector_categories = {'Institutional ROI': {'var_name': 'institutional_roi', 'table': 'DVHs'},
                       'Physician ROI': {'var_name': 'physician_roi', 'table': 'DVHs'},
                       'ROI Type': {'var_name': 'roi_type', 'table': 'DVHs'},
                       'Beam Energy': {'var_name': 'beam_energy', 'table': 'Beams'},
                       'Beam Type': {'var_name': 'beam_type', 'table': 'Beams'},
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
range_categories = {'Age': {'var_name': 'age', 'table': 'Plans', 'units': '', 'source': source_plans},
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
                    'Collimator Angle': {'var_name': 'collimator_angle', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Couch Angle': {'var_name': 'couch_angle', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Gantry Start Angle': {'var_name': 'gantry_start', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'Gantry End Angle': {'var_name': 'gantry_end', 'table': 'Beams', 'units': 'deg', 'source': source_beams},
                    'SSD': {'var_name': 'ssd', 'table': 'Beams', 'units': 'cm', 'source': source_beams},
                    'ROI Min Dose': {'var_name': 'min_dose', 'table': 'DVHs', 'units': 'Gy', 'source': source},
                    'ROI Mean Dose': {'var_name': 'mean_dose', 'table': 'DVHs', 'units': 'Gy', 'source': source},
                    'ROI Max Dose': {'var_name': 'max_dose', 'table': 'DVHs', 'units': 'Gy', 'source': source},
                    'ROI Volume': {'var_name': 'volume', 'table': 'DVHs', 'units': 'cc', 'source': source}}


def button_add_selector_row():
    global query_row_type
    query_row.append(AddSelectorRow())
    layout.children.insert(2 + len(query_row_type), query_row[-1].row)
    query_row_type.append('selector')


def button_add_range_row():
    global query_row_type
    query_row.append(AddRangeRow())
    layout.children.insert(2 + len(query_row_type), query_row[-1].row)
    query_row_type.append('range')


def button_add_endpoint_row():
    global query_row_type
    query_row.append(AddEndPointRow())
    layout.children.insert(2 + len(query_row_type), query_row[-1].row)
    query_row_type.append('endpoint')


def update_query_row_ids():
    global query_row
    for i in range(1, len(query_row)):
        query_row[i].id = i


def update_all_range_endpoints():
    global query_row, query_row_type
    for i in range(1, len(query_row)):
        if query_row_type[i] == 'range':
            query_row[i].update_range_values(query_row[i].select_category.value)


def is_physician_set():
    global query_row, query_row_type
    for i in range(1, len(query_row)):
        if query_row_type[i] == 'selector':
            if query_row[i].select_category.value == "Physician":
                return True
    return False


def get_physician():
    global query_row, query_row_type
    for i in range(1, len(query_row)):
        if query_row_type[i] == 'selector':
            if query_row[i].select_category.value == "Physician":
                return query_row[i].select_value.value
    return None


def update_data():
    global query_row_type, query_row, current_dvh
    uids, dvh_query_str = get_query()
    print str(datetime.now()), 'getting dvh data'
    current_dvh = DVH(uid=uids, dvh_condition=dvh_query_str)
    print str(datetime.now()), 'initializing source data', current_dvh.query
    update_dvh_data(current_dvh)
    update_all_range_endpoints()
    update_endpoint_data(current_dvh)


def update_update_button_status():
    uids, dvh_query_str = get_query()
    count = DVH_SQL().get_roi_count_from_query(dvh_condition=dvh_query_str, uid=uids)
    if count > 50:
        update_button.button_type = "warning"
        update_button.label = "Large Update (" + str(count) + ")"
    else:
        update_button.button_type = "success"
        update_button.label = "Update"


def radio_group_dose_ticker(attr, old, new):
    if source.data['x'] != '':
        update_data()


def radio_group_volume_ticker(attr, old, new):
    if source.data['x'] != '':
        update_data()


def get_query():
    global query_row_type, query_row, current_dvh
    plan_query_str = []
    rx_query_str = []
    beam_query_str = []
    dvh_query_str = []
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
                plan_query_str.append(query_str)
            elif table == 'Rxs':
                rx_query_str.append(query_str)
            elif table == 'Beams':
                beam_query_str.append(query_str)
            elif table == 'DVHs':
                dvh_query_str.append(query_str)

    plan_query_str = ' and '.join(plan_query_str)
    rx_query_str = ' and '.join(rx_query_str)
    beam_query_str = ' and '.join(beam_query_str)
    dvh_query_str = ' and '.join(dvh_query_str)

    print str(datetime.now()), 'getting uids'
    uids = get_study_instance_uids(Plans=plan_query_str, Rxs=rx_query_str, Beams=beam_query_str)['union']

    return uids, dvh_query_str


class AddSelectorRow:
    def __init__(self):
        # Plans Tab Widgets
        # Category Dropdown
        self.id = len(query_row)
        self.category_options = selector_categories.keys()
        self.category_options.sort()
        self.select_category = Select(value="Institutional ROI", options=self.category_options, width=450)
        self.select_category.on_change('value', self.update_selector_values)

        # Value Dropdown
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
        del (layout.children[2 + self.id])
        query_row_type.pop(self.id)
        query_row.pop(self.id)
        update_query_row_ids()
        update_update_button_status()


class AddRangeRow:
    def __init__(self):
        self.id = len(query_row)
        # Plans Tab Widgets
        # Category Dropdown
        self.category_options = range_categories.keys()
        self.category_options.sort()
        self.select_category = Select(value=self.category_options[-1], options=self.category_options, width=450)
        self.select_category.on_change('value', self.update_range_values_ticker)

        # Range slider
        self.sql_table = range_categories[self.select_category.value]['table']
        self.var_name = range_categories[self.select_category.value]['var_name']
        self.min_value = []
        self.max_value = []
        self.text_min = TextInput(value='', title='', width=225)
        self.text_max = TextInput(value='', title='', width=225)
        self.text_min.on_change('value', self.update_range_values_ticker)
        self.text_max.on_change('value', self.update_range_values_ticker)
        self.update_range_values(self.select_category.value)

        self.delete_last_row = Button(label="Delete", button_type="warning", width=100)
        self.delete_last_row.on_click(self.delete_row)

        self.row = row([self.select_category,
                        self.text_min,
                        self.text_max,
                        self.delete_last_row])

    def update_range_values_ticker(self, attrname, old, new):
        self.update_range_values(new)
        update_update_button_status()

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
        del (layout.children[2 + self.id])
        query_row_type.pop(self.id)
        query_row.pop(self.id)
        update_query_row_ids()
        update_update_button_status()


class AddEndPointRow:
    def __init__(self):
        # Plans Tab Widgets
        # Category RadioButtonGroup
        self.id = len(query_row)
        self.options = ["Dose to Vol", "Vol of Dose"]
        self.select_category = RadioButtonGroup(labels=self.options, active=0, width=225)
        self.select_category.on_change('active', self.endpoint_category_ticker)

        self.unit_labels = [["%", "cc"], ["%", "Gy"]]

        self.units_out = RadioButtonGroup(labels=self.unit_labels[1], active=1, width=225)
        self.units_out.on_change('active', self.endpoint_units_out_ticker)

        # Value Dropdown
        self.text_input = TextInput(value='', title="Volume (%):", width=225)
        self.text_input.on_change('value', self.endpoint_calc_ticker)

        self.units = RadioButtonGroup(labels=self.unit_labels[0], active=0, width=225)
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
        del (layout.children[2 + self.id])
        query_row_type.pop(self.id)
        query_row.pop(self.id)
        update_query_row_ids()
        update_endpoint_data(current_dvh)

    def update_text_input_title(self):
        if self.select_category.active == 0:
            self.text_input.title = 'Volume (' + self.unit_labels[0][self.units.active] + '):'
        elif self.select_category.active == 1:
            self.text_input.title = 'Dose (' + self.unit_labels[1][self.units.active] + '):'


def update_dvh_data(dvh):

    line_colors = []
    for i, color in itertools.izip(range(0, dvh.count), colors):
        line_colors.append(color)

    x_axis = np.add(np.linspace(0, dvh.bin_count, dvh.bin_count) / float(100), 0.005)
    mrn = []
    uid = []
    roi_institutional = []
    roi_physician = []
    roi_name = []
    roi_type = []
    rx_dose = []
    volume = []
    min_dose = []
    mean_dose = []
    max_dose = []
    eud = []
    eud_a_value = []
    x_data = []
    y_data = []
    endpoint_columns = []
    x_scale = []
    y_scale = []
    for i in range(0, dvh.count):
        mrn.append(dvh.mrn[i])
        uid.append(dvh.study_instance_uid[i])
        roi_institutional.append(dvh.institutional_roi[i])
        roi_physician.append(dvh.physician_roi[i])
        roi_name.append(dvh.roi_name[i])
        roi_type.append(dvh.roi_type[i])
        rx_dose.append(dvh.rx_dose[i])
        volume.append(dvh.volume[i])
        min_dose.append(dvh.min_dose[i])
        mean_dose.append(dvh.mean_dose[i])
        max_dose.append(dvh.max_dose[i])
        eud.append(dvh.eud[i].tolist())
        eud_a_value.append(dvh.eud_a_value[i])
        endpoint_columns.append('')
        if radio_group_dose.active == 0:
            x_data.append(x_axis.tolist())
            x_scale.append('Gy')
        else:
            x_data.append(np.divide(x_axis, rx_dose[i]).tolist())
            x_scale.append('%RxDose')
        if radio_group_volume.active == 0:
            y_data.append(np.multiply(dvh.dvh[:, i], volume[i]).tolist())
            y_scale.append('%Vol')
        else:
            y_data.append(dvh.dvh[:, i].tolist())
            y_scale.append('cm^3')

    source.data = {'mrn': mrn,
                   'uid': uid,
                   'roi_institutional': roi_institutional,
                   'roi_physician': roi_physician,
                   'roi_name': roi_name,
                   'roi_type': roi_type,
                   'rx_dose': rx_dose,
                   'volume': volume,
                   'min_dose': min_dose,
                   'mean_dose': mean_dose,
                   'max_dose': max_dose,
                   'eud': eud,
                   'eud_a_value': eud_a_value,
                   'x': x_data,
                   'y': y_data,
                   'color': line_colors,
                   'ep1': endpoint_columns,
                   'ep2': endpoint_columns,
                   'ep3': endpoint_columns,
                   'ep4': endpoint_columns,
                   'ep5': endpoint_columns,
                   'ep6': endpoint_columns,
                   'ep7': endpoint_columns,
                   'ep8': endpoint_columns,
                   'x_scale': x_scale,
                   'y_scale': y_scale}

    if radio_group_dose.active == 0 and radio_group_volume.active == 1:
        source_patch.data = {'x_patch': np.append(x_axis, x_axis[::-1]).tolist(),
                             'y_patch': np.append(dvh.q3_dvh, dvh.q1_dvh[::-1]).tolist()}
        source_stats.data = {'x': x_axis.tolist(),
                             'min': dvh.min_dvh.tolist(),
                             'q1': dvh.q1_dvh.tolist(),
                             'mean': dvh.mean_dvh.tolist(),
                             'median': dvh.median_dvh.tolist(),
                             'q3': dvh.q3_dvh.tolist(),
                             'max': dvh.max_dvh.tolist()}
    else:
        source_patch.data = {'x_patch': [],
                             'y_patch': []}
        source_stats.data = {'x': [],
                             'min': [],
                             'q1': [],
                             'mean': [],
                             'median': [],
                             'q3': [],
                             'max': []}

    if radio_group_dose.active == 0:
        dvh_plots.xaxis.axis_label = "Dose (Gy)"
    else:
        dvh_plots.xaxis.axis_label = "Relative Dose (to Rx)"
    if radio_group_volume.active == 0:
        dvh_plots.yaxis.axis_label = "Absolute Volume (cc)"
    else:
        dvh_plots.yaxis.axis_label = "Relative Volume"

    update_beam_data(dvh.study_instance_uid)
    update_plan_data(dvh.study_instance_uid)
    update_rx_data(dvh.study_instance_uid)


def update_beam_data(uids):
    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    beam_data = QuerySQL('Beams', cond_str)

    source_beams.data = {'mrn': beam_data.mrn,
                         'uid': beam_data.study_instance_uid,
                         'beam_dose': beam_data.beam_dose,
                         'beam_energy': beam_data.beam_energy,
                         'beam_mu': beam_data.beam_mu,
                         'beam_name': beam_data.beam_name,
                         'beam_number': beam_data.beam_number,
                         'beam_type': beam_data.beam_type,
                         'collimator_angle': beam_data.collimator_angle,
                         'control_point_count': beam_data.control_point_count,
                         'couch_angle': beam_data.couch_angle,
                         'fx_count': beam_data.fx_count,
                         'fx_grp_beam_count': beam_data.fx_grp_beam_count,
                         'fx_grp_number': beam_data.fx_grp_number,
                         'gantry_end': beam_data.gantry_end,
                         'gantry_rot_dir': beam_data.gantry_rot_dir,
                         'gantry_start': beam_data.gantry_start,
                         'radiation_type': beam_data.radiation_type,
                         'ssd': beam_data.ssd,
                         'treatment_machine': beam_data.treatment_machine}


def update_plan_data(uids):

    cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
    plan_data = QuerySQL('Plans', cond_str)

    source_plans.data = {'mrn': plan_data.mrn,
                         'uid': plan_data.study_instance_uid,
                         'age': plan_data.age,
                         'birth_date': plan_data.birth_date,
                         'dose_grid_resolution': plan_data.dose_grid_res,
                         'fxs': plan_data.fxs,
                         'patient_orientation': plan_data.patient_orientation,
                         'patient_sex': plan_data.patient_sex,
                         'physician': plan_data.physician,
                         'rx_dose': plan_data.rx_dose,
                         'sim_study_date': plan_data.sim_study_date,
                         'total_mu': plan_data.total_mu,
                         'tx_energies': plan_data.tx_energies,
                         'tx_modality': plan_data.tx_modality,
                         'tx_site': plan_data.tx_site,
                         'heterogeneity_correction': plan_data.heterogeneity_correction}


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


def update_endpoint_data(dvh):
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
        for j in range(0, dvh.count):
            endpoints_map[i].append('')

    tuple_list = {}
    for i in range(0, 8):
        current_tuple_list = []
        for j in range(0, dvh.count):
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

    for i in range(0, counter):
        data_table_endpoints.columns[i+1] = TableColumn(field=str('ep' + str(i+1)),
                                                        title=endpoint_columns[i],
                                                        width=100,
                                                        formatter=NumberFormatter(format="0.00"))


# set up layout
tools = "pan,wheel_zoom,box_zoom,reset,crosshair,hover"
dvh_plots = figure(plot_width=1000, plot_height=400, tools=tools, logo=None)

stats_min = dvh_plots.line('x', 'min', source=source_stats, line_width=2, color='black', line_dash='dotted', alpha=0.2)
stats_q1 = dvh_plots.line('x', 'q1', source=source_stats, line_width=0.5, color='black', alpha=0.2)
stats_median = dvh_plots.line('x', 'median', source=source_stats, line_width=2, color='lightpink', line_dash='dashed', alpha=0.75)
stats_mean = dvh_plots.line('x', 'mean', source=source_stats, line_width=2, color='lightseagreen', line_dash='dashed', alpha=0.5)
stats_q3 = dvh_plots.line('x', 'q3', source=source_stats, line_width=0.5, color='black', alpha=0.2)
stats_max = dvh_plots.line('x', 'max', source=source_stats, line_width=2, color='black', line_dash='dotted', alpha=0.2)

dvh_plots.multi_line('x', 'y', source=source, selection_color='color', line_width=2, alpha=0, nonselection_alpha=0, selection_alpha=1)
dvh_plots.patch('x_patch', 'y_patch', source=source_patch, alpha=0.15)
dvh_plots.xaxis.axis_label = "Dose (Gy)"
dvh_plots.yaxis.axis_label = "Normalized Volume"

legend_stats = Legend(items=[
        ("Max", [stats_max]),
        ("Q3", [stats_q3]),
        ("Median", [stats_median]),
        ("Mean", [stats_mean]),
        ("Q1", [stats_q1]),
        ("Min", [stats_min])
    ], location=(0, 45))

dvh_plots.add_layout(legend_stats, 'right')
dvh_plots.legend.click_policy = "hide"

# Set up DataTable
data_table_title = PreText(text="DVHs", width=1000)
columns = [TableColumn(field="mrn", title="MRN", width=175),
           TableColumn(field="roi_name", title="ROI Name"),
           TableColumn(field="roi_type", title="ROI Type", width=80),
           TableColumn(field="rx_dose", title="Rx Dose", width=100, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="volume", title="Volume", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="min_dose", title="Min Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="mean_dose", title="Mean Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="max_dose", title="Max Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="eud", title="EUD", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="eud_a_value", title="a", width=80)]
data_table = DataTable(source=source, columns=columns, width=1000, selectable=True)

# Set up EndPoint DataTable
endpoint_table_title = PreText(text="DVH Endpoints", width=1000)
columns = [TableColumn(field="mrn", title="MRN", width=175),
           TableColumn(field="ep1", title=endpoint_columns[0], width=120),
           TableColumn(field="ep2", title=endpoint_columns[1], width=120),
           TableColumn(field="ep3", title=endpoint_columns[2], width=120),
           TableColumn(field="ep4", title=endpoint_columns[3], width=120),
           TableColumn(field="ep5", title=endpoint_columns[4], width=120),
           TableColumn(field="ep6", title=endpoint_columns[5], width=120),
           TableColumn(field="ep7", title=endpoint_columns[6], width=120),
           TableColumn(field="ep8", title=endpoint_columns[7], width=120)]
data_table_endpoints = DataTable(source=source, columns=columns, width=1000, selectable=True)

beam_table_title = PreText(text="Beams", width=1500)
columns = [TableColumn(field="mrn", title="MRN", width=175),
           TableColumn(field="beam_number", title="Beam", width=50),
           TableColumn(field="fx_grp_beam_count", title="Beams", width=50),
           TableColumn(field="fx_grp_number", title="Rx Grp", width=60),
           TableColumn(field="fx_count", title="Fxs", width=50),
           TableColumn(field="beam_name", title="Name", width=150),
           TableColumn(field="beam_dose", title="Dose", width=80, formatter=NumberFormatter(format="0.00")),
           TableColumn(field="beam_energy", title="Energy", width=80),
           TableColumn(field="beam_mu", title="MU", width=100, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="beam_type", title="Type", width=100),
           TableColumn(field="collimator_angle", title="Col Ang", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="control_point_count", title="CPs", width=80),
           TableColumn(field="couch_angle", title="Couch Ang", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="gantry_start", title="Gant Start", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="gantry_rot_dir", title="Gant Dir", width=80),
           TableColumn(field="gantry_end", title="Gant End", width=80, formatter=NumberFormatter(format="0.0")),
           TableColumn(field="radiation_type", title="Rad. Type", width=80),
           TableColumn(field="ssd", title="SSD", width=80),
           TableColumn(field="treatment_machine", title="Tx Machine", width=80)]
data_table_beams = DataTable(source=source_beams, columns=columns, width=1500)

plans_table_title = PreText(text="Plans", width=1000)
columns = [TableColumn(field="mrn", title="MRN"),
           TableColumn(field="age", title="Age"),
           TableColumn(field="birth_date", title="Birth Date"),
           TableColumn(field="dose_grid_res", title="Dose Grid Res"),
           TableColumn(field="fxs", title="Fxs"),
           TableColumn(field="patient_orientation", title="Orientation"),
           TableColumn(field="patient_sex", title="Gender"),
           TableColumn(field="physician", title="Rad Onc"),
           TableColumn(field="rx_dose", title="Rx Dose", formatter=NumberFormatter(format="0.00")),
           TableColumn(field="sim_study_date", title="Sim Study Date"),
           TableColumn(field="total_mu", title="Total MU", formatter=NumberFormatter(format="0.0")),
           TableColumn(field="tx_energies", title="Tx Energies"),
           TableColumn(field="tx_modality", title="Tx Modality"),
           TableColumn(field="tx_site", title="Tx Site")]
data_table_plans = DataTable(source=source_plans, columns=columns, width=1200)

rxs_table_title = PreText(text="Rxs", width=1000)
columns = [TableColumn(field="mrn", title="MRN"),
           TableColumn(field="plan_name", title="Plan Name"),
           TableColumn(field="fx_dose", title="Fx Dose", formatter=NumberFormatter(format="0.00")),
           TableColumn(field="rx_percent", title="Rx Isodose", formatter=NumberFormatter(format="0.0")),
           TableColumn(field="rx_dose", title="Rx Dose", formatter=NumberFormatter(format="0.00")),
           TableColumn(field="fx_grp_number", title="Fx Grp"),
           TableColumn(field="fx_grp_count", title="Fx Groups"),
           TableColumn(field="fx_grp_name", title="Fx Grp Name"),
           TableColumn(field="normalization_method", title="Norm Method"),
           TableColumn(field="normalization_object", title="Norm Object")]
data_table_rxs = DataTable(source=source_rxs, columns=columns, width=1000)

# Setup axis normalization radio buttons
radio_group_dose = RadioGroup(labels=["Absolute Dose", "Relative Dose (Rx)"], active=0)
radio_group_dose.on_change('active', radio_group_dose_ticker)
radio_group_volume = RadioGroup(labels=["Absolute Volume", "Relative Volume"], active=1)
radio_group_volume.on_change('active', radio_group_volume_ticker)

update_button = Button(label="Update", button_type="success", width=200)
update_button.on_click(update_data)

download_button = Button(label="Download", button_type="default", width=200)
download_button.callback = CustomJS(args=dict(source=source,
                                              source_rxs=source_rxs,
                                              source_plans=source_plans,
                                              source_beams=source_beams,
                                              source_endpoint_names=source_endpoint_names),
                                    code=open(join(dirname(__file__), "download.js")).read())

main_add_selector_button = Button(label="Add Selection Filter", button_type="primary", width=200)
main_add_selector_button.on_click(button_add_selector_row)
main_add_range_button = Button(label="Add Range Filter", button_type="primary", width=200)
main_add_range_button.on_click(button_add_range_row)
main_add_endpoint_button = Button(label="Add Endpoint", button_type="primary", width=200)
main_add_endpoint_button.on_click(button_add_endpoint_row)
query_row.append(row(update_button, main_add_selector_button, main_add_range_button))
query_row_type.append('main')

layout = column(row(radio_group_dose, radio_group_volume),
                dvh_plots,
                row(main_add_selector_button,
                    main_add_range_button,
                    main_add_endpoint_button,
                    update_button,
                    download_button),
                data_table_title,
                data_table,
                endpoint_table_title,
                data_table_endpoints,
                rxs_table_title,
                data_table_rxs,
                beam_table_title,
                data_table_beams,
                plans_table_title,
                data_table_plans)

button_add_selector_row()

curdoc().add_root(layout)
curdoc().title = "Live Free or DICOM"
