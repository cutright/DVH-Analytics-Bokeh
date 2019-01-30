#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
protocol model for admin view
Created on Fri Jan 27 2019
@author: Dan Cutright, PhD
This module is to designed to update protocol information
"""

from __future__ import print_function
from bokeh.models.widgets import TextAreaInput, DataTable, Select, Button, TableColumn, TextInput, Div
from bokeh.models import ColumnDataSource, Spacer
from bokeh.layouts import row, column
from ..tools.io.database.sql_connector import DVH_SQL
from ..tools.utilities import parse_text_area_input_to_list


class Protocol:
    def __init__(self):
        note = Div(text="<b>NOTE</b>: Each plan may only have one protocol assigned. "
                        "Updating database will over-write any existing data.")

        self.toxicity = []  # Will be used to link to Toxicity tab

        self.source = ColumnDataSource(data=dict(mrn=['']))
        self.source.selected.on_change('indices', self.source_listener)

        self.clear_source_selection_button = Button(label='Clear Selection', button_type='primary', width=150)
        self.clear_source_selection_button.on_click(self.clear_source_selection)

        self.protocol = Select(value='', options=[''], title='Protocols:')
        self.physician = Select(value='', options=[''], title='Physician:', width=150)

        self.update_protocol_options()
        self.update_physician_options()

        self.delete_protocol_button = Button(label='Delete', button_type='warning')

        self.protocol_input = TextInput(value='', title='Protocol for MRN Input:')
        self.update_button = Button(label='Update', button_type='primary', width=150)
        self.update_button.on_click(self.update_db)

        self.mrn_input = TextAreaInput(value='', title='MRN Input:', rows=30, cols=25, max_length=2000)

        self.columns = ['mrn', 'protocol', 'physician', 'tx_site', 'sim_study_date', 'import_time_stamp', 'toxicity_grades']
        relative_widths = [1, 0.8, 0.5, 1, 0.75, 1, 0.8]
        column_widths = [int(250. * rw) for rw in relative_widths]
        table_columns = [TableColumn(field=c, title=c, width=column_widths[i]) for i, c in enumerate(self.columns)]
        self.table = DataTable(source=self.source, columns=table_columns, width=800, editable=True, height=600)

        self.protocol.on_change('value', self.protocol_ticker)
        self.physician.on_change('value', self.physician_ticker)
        self.update_source()

        self.layout = column(row(self.protocol, self.physician),
                             row(self.table, Spacer(width=30), column(note,
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

        condition = ' AND '.join(condition)

        columns = ', '.join(self.columns + ['study_instance_uid'])

        data = DVH_SQL().query('Plans', columns, condition, order_by='mrn', bokeh_cds=True)
        data['toxicity_grades'] = [[x, ''][x == '-1'] for x in data['toxicity_grades']]

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

    def update_db(self):
        cnx = DVH_SQL()
        for i, mrn in enumerate(self.mrns_to_add):
            if mrn in self.source.data['mrn']:
                index = self.source.data['mrn'].index(mrn)
                uid = self.source.data['study_instance_uid'][index]
                cnx.update('Plans', 'protocol', self.protocol_input.value,
                           "study_instance_uid = '%s'" % uid)
        cnx.close()
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
