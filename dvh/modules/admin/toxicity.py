#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
baseline plans model for admin view
Created on Sun Jan 20 2019
@author: Dan Cutright, PhD
This module is to designed to update toxicity and protocol information
"""

from bokeh.models.widgets import TextAreaInput, AutocompleteInput, DataTable, Select, Button, TableColumn
from bokeh.models import ColumnDataSource, Spacer
from bokeh.layouts import row, column
from ..tools.io.database.sql_connector import DVH_SQL


class Toxicity:
    def __init__(self):
        self.source = ColumnDataSource(data=dict(mrn=[]))

        self.protocol = AutocompleteInput(value='', title='Protocol:', completions=['test1', 'test2', 'ohyeah'])
        self.physician = Select(value='', options=[''], title='Physician:')
        self.physician.on_change('value', self.physician_ticker)

        self.physician_roi = Select(value='', options=[''], title='Physician ROI:')
        self.query_button = Button(label='Query', button_type='primary', width=100)
        self.query_button.on_click(self.update_source)

        self.mrn_input = TextAreaInput(value='', title="MRN Input:", rows=10, cols=25, max_length=2000)
        self.toxicity_grade_input = TextAreaInput(value='', title="Toxicity Grade Input:",
                                                  rows=10, cols=5, max_length=500)
        self.update_button = Button(label='Update', button_type='primary', width=425)

        self.columns = ['mrn', 'roi_name', 'toxicity_scale', 'toxicity_grade']
        relative_widths = [1, 1, 1, 1]
        column_widths = [int(250. * rw) for rw in relative_widths]
        table_columns = [TableColumn(field=c, title=c, width=column_widths[i]) for i, c in enumerate(self.columns)]
        self.table = DataTable(source=self.source, columns=table_columns, width=800, editable=True, height=600)

        self.update_physicians()

        self.layout = column(row(self.protocol, self.physician, self.physician_roi, self.query_button),
                             row(self.table, Spacer(width=50), column(self.update_button,
                                                                      row(self.mrn_input, self.toxicity_grade_input))))

    def update_source(self):
        cnx = DVH_SQL()
        uids_physician = cnx.get_unique_values('Plans', 'study_instance_uid',
                                               "physician = '%s'" % self.physician.value)

        condition = ["physician_roi = '%s'" % self.physician_roi.value]
        if uids_physician:
            condition.append("study_instance_uid in ('%s')" % "', '".join(uids_physician))
        condition = ' AND '.join(condition)

        data = cnx.query('DVHs', ', '.join(self.columns), condition, bokeh_cds=True)
        cnx.close()

        self.source.data = data

    def update_protocol_completions(self):
        self.protocol.completions = self.get_protocols()

    @staticmethod
    def get_protocols():
        db_values = DVH_SQL().get_unique_values('Plans', 'protocol')
        protocols = []
        for value in db_values:
            protocols.extend(value.split(','))
        protocols = list(set(protocols))
        protocols.sort()

        return protocols

    def update_physicians(self):
        physicians = DVH_SQL().get_unique_values('Plans', 'physician')
        self.physician.options = physicians
        if self.physician.value not in physicians:
            self.physician.value = physicians[0]

    def physician_ticker(self, attr, old, new):
        self.update_physician_rois()

    def update_physician_rois(self):
        cnx = DVH_SQL()
        uids_physician = cnx.get_unique_values('Plans', 'study_instance_uid',
                                               "physician = '%s'" % self.physician.value)
        condition = "study_instance_uid in ('%s')" % "', '".join(uids_physician)
        physician_rois = cnx.get_unique_values('DVHs', 'physician_roi', condition)
        cnx.close()
        self.physician_roi.options = physician_rois
        if self.physician_roi.value not in physician_rois:
            self.physician_roi.value = physician_rois[0]
