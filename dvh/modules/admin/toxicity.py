#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
baseline plans model for admin view
Created on Sun Jan 20 2019
@author: Dan Cutright, PhD
This module is to designed to update toxicity and protocol information
"""

from __future__ import print_function
from bokeh.models.widgets import TextAreaInput, AutocompleteInput, DataTable, Select, Button, TableColumn
from bokeh.models import ColumnDataSource, Spacer
from bokeh.layouts import row, column
from ..tools.io.database.sql_connector import DVH_SQL
from ..tools.utilities import flatten_list_of_lists


class Toxicity:
    def __init__(self):
        self.source = ColumnDataSource(data=dict(mrn=[]))
        self.data = []  # This will keep all data from query, self.source may display a subset

        self.protocol = AutocompleteInput(value='', title='Protocol:', completions=self.get_all_protocols_in_db())
        self.protocol.on_change('value', self.protocol_ticker)

        self.physician = Select(value='', options=[''], title='Physician:')
        self.physician.on_change('value', self.physician_ticker)

        self.physician_roi = Select(value='', options=[''], title='Physician ROI:')
        self.physician_roi.on_change('value', self.physician_roi_ticker)

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

        self.layout = column(row(self.protocol, self.physician, self.physician_roi),
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

        self.data = cnx.query('DVHs', ', '.join(self.columns + ['study_instance_uid']), condition, bokeh_cds=True)
        cnx.close()

        self.clean_toxicity_grades()

        self.source.data = self.get_data_filtered_by_protocol()

    def get_data_filtered_by_protocol(self):
        protocols = self.get_protocols_in_source()
        new_data = {key: [] for key in list(self.data)}
        for i in range(len(self.data['mrn'])):
            if self.protocol.value in protocols[self.data['study_instance_uid'][i]]:
                for key in list(self.data):
                    new_data[key].append(self.data[key][i])
        return new_data

    def clean_toxicity_grades(self):
        # Replace any toxicity grade values of -1 to None. Stored in SQL as integer, but integer columns can't have NULL
        for i, value in enumerate(self.data['toxicity_grade']):
            if value == -1:
                self.data['toxicity_grade'][i] = None

    @staticmethod
    def get_all_protocols_in_db():
        db_values = DVH_SQL().get_unique_values('Plans', 'protocol')
        protocols = []
        for value in db_values:
            protocols.extend(value.split(','))
        protocols = list(set(protocols))
        protocols.sort()

        return protocols

    def get_protocols_in_source(self):
        return {uid: self.get_protocols_in_db_by_uid(uid) for uid in self.data['study_instance_uid']}

    @staticmethod
    def get_protocols_in_db_by_uid(study_instance_uid):
        data = DVH_SQL().get_unique_values('Plans', 'protocol', "study_instance_uid = '%s'" % study_instance_uid)
        protocols = [[v.replace('(NULL)', '') for v in line.split(',')] for line in data]
        return flatten_list_of_lists(protocols, remove_duplicates=True)

    def update_physicians(self):
        physicians = DVH_SQL().get_unique_values('Plans', 'physician')
        self.physician.options = physicians
        if self.physician.value not in physicians:
            self.physician.value = physicians[0]

    def protocol_ticker(self, attr, old, new):
        self.update_source()

    def physician_ticker(self, attr, old, new):
        self.update_source()
        self.update_physician_rois()

    def physician_roi_ticker(self, attr, old, new):
        self.update_source()

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
