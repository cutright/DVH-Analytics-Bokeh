#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
toxicity model for admin view
Created on Sun Jan 20 2019
@author: Dan Cutright, PhD
This module is to designed to update toxicity information
"""

from __future__ import print_function
from bokeh.models.widgets import TextAreaInput, DataTable, Select, Button, TableColumn, RadioGroup
from bokeh.models import ColumnDataSource, Spacer
from bokeh.layouts import row, column
from ..tools.io.database.sql_connector import DVH_SQL


class Toxicity:
    def __init__(self):
        self.source = ColumnDataSource(data=dict(mrn=[]))
        self.data = []  # This will keep all data from query, self.source may display a subset

        self.protocol = Select(value='All Data', options=['All Data', 'None'], title='Protocol:')
        self.protocol.on_change('value', self.protocol_ticker)
        self.update_protocol_options()

        self.display_by = RadioGroup(labels=['Display by Institutional ROI', 'Display by Physician ROI'], active=0)
        self.display_by.on_change('active', self.display_by_ticker)

        self.physician = Select(value='', options=[''], title='Physician:', width=150)
        self.physician.on_change('value', self.physician_ticker)

        self.roi = Select(value='', options=[''], title='Institutional ROI:')
        self.roi.on_change('value', self.roi_ticker)

        self.mrn_input = TextAreaInput(value='', title="MRN Input:", rows=30, cols=25, max_length=2000)
        self.toxicity_grade_input = TextAreaInput(value='', title="Toxicity Grade Input:",
                                                  rows=30, cols=5, max_length=500)
        self.update_button = Button(label='Update', button_type='primary', width=425)

        self.columns = ['mrn', 'roi_name', 'toxicity_grade']
        relative_widths = [1, 1, 1, 1]
        column_widths = [int(250. * rw) for rw in relative_widths]
        table_columns = [TableColumn(field=c, title=c, width=column_widths[i]) for i, c in enumerate(self.columns)]
        table_columns.insert(1, TableColumn(field='protocol', title='protocol', width=column_widths[0]))
        table_columns.insert(1, TableColumn(field='physician', title='physician', width=column_widths[0]/3))
        self.table = DataTable(source=self.source, columns=table_columns, width=800, editable=True, height=600)

        self.update_physicians()

        self.layout = column(self.protocol,
                             row(self.display_by, self.physician, self.roi),
                             row(self.table, Spacer(width=50), column(self.update_button,
                                                                      row(self.mrn_input, self.toxicity_grade_input))))

    def update_source(self):
        cnx = DVH_SQL()
        if self.display_by.active == 1:  # Display by Physician ROI
            uids_physician = cnx.get_unique_values('Plans', 'study_instance_uid',
                                                   "physician = '%s'" % self.physician.value)

            condition = ["physician_roi = '%s'" % self.roi.value]
            if uids_physician:
                condition.append("study_instance_uid in ('%s')" % "', '".join(uids_physician))

        else:  # Display by Institutional ROI
            condition = ["institutional_roi = '%s'" % self.roi.value]

            if self.physician.value != 'Any':
                uids_physician = cnx.get_unique_values('Plans', 'study_instance_uid',
                                                       "physician = '%s'" % self.physician.value)
                if uids_physician:
                    condition.append("study_instance_uid in ('%s')" % "', '".join(uids_physician))

        condition = ' AND '.join(condition)

        self.data = cnx.query('DVHs', ', '.join(self.columns + ['study_instance_uid']), condition, bokeh_cds=True)
        cnx.close()

        for col in ['protocol', 'physician']:
            self.data[col] = self.get_sql_values_based_on_source('Plans', col, return_list=True)

        self.clean_toxicity_grades()

        if self.protocol.value == 'All Data':
            self.source.data = self.data
        else:
            self.source.data = self.get_data_filtered_by_protocol()

    def get_data_filtered_by_protocol(self):
        selected_protocol = self.protocol.value
        if selected_protocol == 'No Protocol':
            selected_protocol = ''
        protocols = self.get_sql_values_based_on_source('Plans', 'protocol')
        if not protocols:
            return self.data
        new_data = {key: [] for key in list(self.data)}
        for i in range(len(self.data['mrn'])):
            if (selected_protocol == 'Any Protocol' and protocols[self.data['study_instance_uid'][i]]) or \
                    (not selected_protocol and not protocols[self.data['study_instance_uid'][i]]) or\
                    (selected_protocol and selected_protocol in protocols[self.data['study_instance_uid'][i]]):
                for key in list(self.data):
                    new_data[key].append(self.data[key][i])
        return new_data

    def clean_toxicity_grades(self):
        # Replace any toxicity grade values of -1 to None. Stored in SQL as integer, but integer columns can't have NULL
        for i, value in enumerate(self.data['toxicity_grade']):
            if value == -1:
                self.data['toxicity_grade'][i] = None

    def update_protocol_options(self):
        options = ['All Data', 'Any Protocol', 'No Protocol'] + self.get_protocols()
        self.protocol.options = options
        if self.protocol.value not in options:
            self.protocol.value = options[0]

    def get_sql_values_based_on_source(self, sql_table, sql_column, return_list=False):
        cnx = DVH_SQL()
        uids = self.data['study_instance_uid']
        data = cnx.query(sql_table, 'study_instance_uid, %s' % sql_column,
                         "study_instance_uid in ('%s')" % "', '".join(uids))

        if data:
            return_data = {line[0]: line[1] for line in data}
            if return_list:
                return [return_data[uid] for uid in self.data['study_instance_uid']]
            else:
                return return_data
        return []

    @staticmethod
    def get_protocols(condition=None):
        return DVH_SQL().get_unique_values('Plans', 'protocol', condition, ignore_null=True)

    def update_physicians(self):
        physicians = DVH_SQL().get_unique_values('Plans', 'physician')
        if self.display_by.active == 0:
            physicians.insert(0, 'Any')

        self.physician.options = physicians
        if self.physician.value not in physicians:
            self.physician.value = physicians[0]

    def protocol_ticker(self, attr, old, new):
        self.update_source()

    def physician_ticker(self, attr, old, new):
        self.update_source()
        self.update_rois()

    def roi_ticker(self, attr, old, new):
        self.update_source()

    def update_rois(self):
        cnx = DVH_SQL()
        if self.display_by.active == 1:  # Display by Physician ROI
            uids_physician = cnx.get_unique_values('Plans', 'study_instance_uid',
                                                   "physician = '%s'" % self.physician.value)
            condition = "study_instance_uid in ('%s')" % "', '".join(uids_physician)
            rois = cnx.get_unique_values('DVHs', 'physician_roi', condition)
        else:  # Display by Institutional ROI
            rois = cnx.get_unique_values('DVHs', 'institutional_roi')
        cnx.close()
        self.roi.options = rois
        if self.roi.value not in rois:
            self.roi.value = rois[0]

    @staticmethod
    def update_plan_toxicity_grades_in_db(study_instance_uid):
        cnx = DVH_SQL()
        toxicities = cnx.get_unique_values('DVHs', 'toxicity', "study_instance_uid = '%s'" % study_instance_uid)
        toxicities_str = ','.join(toxicities)
        cnx.update('Plans', 'toxicity_grades', toxicities_str, "study_instance_uid = '%s'" % study_instance_uid)
        cnx.close()

    def display_by_ticker(self, attr, old, new):
        self.roi.title = ['Institutional ROI:', 'Physician ROI:'][new]
        self.update_physicians()
        self.update_rois()

