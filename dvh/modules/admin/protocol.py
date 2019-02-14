#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
protocol model for admin view
Created on Fri Jan 27 2019
@author: Dan Cutright, PhD
This module is to designed to update protocol information
"""

from __future__ import print_function
from bokeh.models.widgets import TextAreaInput, DataTable, Select, Button, TableColumn, TextInput, Div, DatePicker,\
    CheckboxGroup
from bokeh.models import ColumnDataSource, Spacer
from bokeh.layouts import row, column
from ..tools.io.database.sql_connector import DVH_SQL
from ..tools.utilities import parse_text_area_input_to_list


class Protocol:
    def __init__(self):
        note = Div(text="<b>NOTE</b>: Each plan may only have one protocol assigned. "
                        "Updating database will overwrite any existing data.", width=700)
        self.update_checkbox = CheckboxGroup(labels=["Only update plans in table."], active=[0])

        self.toxicity = []  # Will be used to link to Toxicity tab

        self.source = ColumnDataSource(data=dict(mrn=['']))
        self.source.selected.on_change('indices', self.source_listener)

        self.clear_source_selection_button = Button(label='Clear Selection', button_type='primary', width=150)
        self.clear_source_selection_button.on_click(self.clear_source_selection)

        self.protocol = Select(value='', options=[''], title='Protocols:')
        self.physician = Select(value='', options=[''], title='Physician:', width=150)

        self.date_filter_by = Select(value='None', options=['None', 'sim_study_date', 'import_time_stamp'],
                                     title='Date Filter Type:', width=150)
        self.date_filter_by.on_change('value', self.date_ticker)
        self.date_start = DatePicker(title='Start Date:', width=200)
        self.date_start.on_change('value', self.date_ticker)
        self.date_end = DatePicker(title='End Date:', width=200)
        self.date_end.on_change('value', self.date_ticker)

        self.update_protocol_options()
        self.update_physician_options()

        self.protocol_input = TextInput(value='', title='Protocol for MRN Input:')
        self.update_button = Button(label='Need MRNs to Update', button_type='default', width=150)
        self.update_button.on_click(self.update_db)

        self.mrn_input = TextAreaInput(value='', title='MRN Input:', rows=30, cols=25, max_length=2000)
        self.mrn_input.on_change('value', self.mrn_input_ticker)

        self.columns = ['mrn', 'protocol', 'physician', 'tx_site', 'sim_study_date', 'import_time_stamp',
                        'toxicity_grades']
        relative_widths = [1, 0.8, 0.5, 1, 0.75, 1, 0.8]
        column_widths = [int(250. * rw) for rw in relative_widths]
        table_columns = [TableColumn(field=c, title=c, width=column_widths[i]) for i, c in enumerate(self.columns)]
        self.table = DataTable(source=self.source, columns=table_columns, width=800, editable=True, height=600)

        self.protocol.on_change('value', self.protocol_ticker)
        self.physician.on_change('value', self.physician_ticker)
        self.update_source()

        self.layout = column(row(self.protocol, self.physician),
                             row(self.date_filter_by, Spacer(width=30), self.date_start, Spacer(width=30),
                                 self.date_end),
                             note,
                             row(self.table, Spacer(width=30), column(self.update_checkbox,
                                                                      row(self.protocol_input, self.update_button),
                                                                      self.clear_source_selection_button,
                                                                      self.mrn_input)))

    def source_listener(self, attr, old, new):
        mrns = [self.source.data['mrn'][x] for x in new]
        self.mrn_input.value = '\n'.join(mrns)

    def update_source(self):

        condition = []

        if self.protocol.value not in self.protocol.options[0:3]:
            condition.append("protocol = '%s'" % self.protocol.value)
        elif self.protocol.value == self.protocol.options[1]:
            condition.append("protocol != ''")
        elif self.protocol.value == self.protocol.options[2]:
            condition.append("protocol = ''")

        if self.physician.value != self.physician.options[0]:
            condition.append("physician = '%s'" % self.physician.value)

        if self.date_filter_by.value != 'None':
            if self.date_start.value:
                condition.append("%s >= '%s'::date" % (self.date_filter_by.value, self.date_start.value))
            if self.date_end.value:
                condition.append("%s >= '%s'::date" % (self.date_filter_by.value, self.date_end.value))

        condition = ' AND '.join(condition)

        columns = ', '.join(self.columns + ['study_instance_uid'])

        data = DVH_SQL().query('Plans', columns, condition, order_by='mrn', bokeh_cds=True)

        self.source.data = data

    def update_protocol_options(self):
        options = ['All Data', 'Any Protocol', 'No Protocol'] + self.get_protocols()
        self.protocol.options = options
        if self.protocol.value not in options:
            self.protocol.value = options[0]

    @property
    def mrns_to_add(self):
        return parse_text_area_input_to_list(self.mrn_input.value, delimeter=None)

    @staticmethod
    def get_protocols(condition=None):
        return DVH_SQL().get_unique_values('Plans', 'protocol', condition, ignore_null=True)

    def update_physician_options(self):
        physicians = ['Any'] + DVH_SQL().get_unique_values('Plans', 'physician')

        self.physician.options = physicians
        if self.physician.value not in physicians:
            self.physician.value = physicians[0]

    def protocol_ticker(self, attr, old, new):
        self.update_source()

    def physician_ticker(self, attr, old, new):
        self.update_source()

    def date_ticker(self, attr, old, new):
        self.update_source()

    def update_db(self):
        if 0 in self.update_checkbox.active:
            condition = "mrn in ('%s')" % "', '".join(self.mrns_to_add)
        else:
            uids = []
            for i, mrn in enumerate(self.mrns_to_add):
                if mrn in self.source.data['mrn']:
                    index = self.source.data['mrn'].index(mrn)
                    uids.append(self.source.data['study_instance_uid'][index])

            condition = "study_instance_uid in ('%s')" % "', '".join(uids)

        DVH_SQL().update('Plans', 'protocol',
                         self.protocol_input.value.replace("'", "").replace("\"", "").replace("\\", ""), condition)

        self.update_source()

        self.clear_source_selection()
        self.protocol_input.value = ''

        self.update_protocol_options()

        self.toxicity.update_protocol_options()
        self.toxicity.update_source()

    def clear_source_selection(self):
        self.source.selected.indices = []

    def add_toxicity_tab_link(self, toxicity):
        self.toxicity = toxicity

    def mrn_input_ticker(self, attr, old, new):
        self.update_update_button_status()

    def update_update_button_status(self):
        if self.mrns_to_add:
            self.update_button.label = 'Update'
            self.update_button.button_type = 'primary'
        else:
            self.update_button.label = 'Need MRNs to Update'
            self.update_button.button_type = 'default'
