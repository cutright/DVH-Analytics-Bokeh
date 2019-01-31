#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
database editor model for admin view
Created on Tue Dec 25 2018
@author: Dan Cutright, PhD
"""

from __future__ import print_function
import os
from os.path import dirname, join
from datetime import datetime
from bokeh.models.widgets import Select, Button, TextInput, Div, MultiSelect, TableColumn, DataTable, CheckboxGroup
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, CustomJS, Spacer
from ..tools.utilities import get_csv, print_run_time
from ..tools.io.preferences.import_settings import load_directories
from ..tools.io.database.sql_connector import DVH_SQL
from ..tools.io.database.dicom.importer import dicom_to_sql, rebuild_database
from ..tools.io.database import update as db_update
from ..tools.io.database.recalculate import recalculate_ages


class DatabaseEditor:
    def __init__(self, roi_manager):

        column_width = 600

        self.roi_manager = roi_manager  # allows ROI Name manager updates after importing data

        self.source = ColumnDataSource(data=dict())
        self.source_csv = ColumnDataSource(data=dict(text=[]))

        self.import_inbox_button = Button(label='Import all from inbox', button_type='success', width=200)
        self.import_inbox_button.on_click(self.import_inbox)
        self.import_inbox_force = CheckboxGroup(labels=['Force Update', 'Import Latest Only', 'Move Files'],
                                                active=[1, 2])
        self.rebuild_db_button = Button(label='Rebuild database', button_type='warning', width=200)
        self.rebuild_db_button.on_click(self.rebuild_db_button_click)

        self.query_table = Select(value='Plans', options=['DVHs', 'Plans', 'Rxs', 'Beams', 'DICOM_Files'], width=200,
                                  title='Table:')
        self.query_columns = MultiSelect(title="Columns (Ctrl or Shift Click enabled):", width=250,
                                         options=[tuple(['', ''])], size=10)
        self.query_condition = TextInput(value='', title="Condition:", width=450)
        self.query_button = Button(label='Query', button_type='primary', width=100)

        self.query_table.on_change('value', self.update_query_columns_ticker)
        self.query_button.on_click(self.update_query_source)

        self.update_db_title = Div(text="<b>Update Database</b>", width=column_width)
        self.update_db_table = Select(value='DVHs', options=['DVHs', 'Plans', 'Rxs', 'Beams'], width=80,
                                      title='Table:')
        self.update_db_column = Select(value='', options=[''], width=175, title='Column')
        self.update_db_value = TextInput(value='', title="Value:", width=200)
        self.update_db_condition = TextInput(value='', title="Condition:", width=350)
        self.update_db_button = Button(label='Update DB', button_type='warning', width=100)

        self.update_db_table.on_change('value', self.update_update_db_columns_ticker)
        self.update_db_button.on_click(self.update_db)

        self.update_query_columns()
        self.update_update_db_column()

        self.reimport_title = Div(text="<b>Reimport from DICOM</b>", width=column_width)
        self.reimport_mrn_text = TextInput(value='', width=200, title='MRN:')
        self.reimport_study_date_select = Select(value='', options=[''], width=200, title='Sim Study Date:')
        self.reimport_uid_select = Select(value='', options=[''], width=425, title='Study Instance UID:')
        self.reimport_old_data_select = Select(value='Delete from DB', options=['Delete from DB', 'Keep in DB'],
                                               width=150, title='Current Data:')
        self.reimport_button = Button(label='Reimport', button_type='warning', width=100)

        self.reimport_mrn_text.on_change('value', self.reimport_mrn_ticker)
        self.reimport_study_date_select.on_change('value', self.reimport_study_date_ticker)
        self.reimport_button.on_click(self.reimport_button_click)

        self.query_data_table = DataTable(source=self.source, columns=[], width=column_width, editable=True, height=600)

        self.delete_from_db_title = Div(text="<b>Delete all data with mrn or study_instance_uid</b>",
                                        width=column_width)
        self.delete_from_db_column = Select(value='mrn', options=['mrn', 'study_instance_uid'], width=200,
                                            title='Patient Identifier:')
        self.delete_from_db_value = TextInput(value='', title="Value (required):", width=300)
        self.delete_from_db_button = Button(label='Delete', button_type='warning', width=100)
        self.delete_auth_text = TextInput(value='', title="Type 'delete' here to authorize:", width=300)
        self.delete_auth_text.on_change('value', self.delete_auth_text_ticker)
        self.delete_from_db_button.on_click(self.delete_from_db)

        self.change_mrn_uid_title = Div(text="<b>Change mrn or study_instance_uid in all tables</b>",
                                        width=column_width)
        self.change_mrn_uid_column = Select(value='mrn', options=['mrn', 'study_instance_uid'], width=200,
                                            title='Patient Identifier:')
        self.change_mrn_uid_old_value = TextInput(value='', title="Old:", width=300)
        self.change_mrn_uid_new_value = TextInput(value='', title="New:", width=300)
        self.change_mrn_uid_button = Button(label='Rename', button_type='warning', width=100)
        self.change_mrn_uid_button.on_click(self.change_mrn_uid)

        self.calculations_title = Div(text="<b>Post Import Calculations</b>", width=column_width)
        self.calculate_condition = TextInput(value='', title="Condition:", width=350)
        self.calculate_options = ['Default Post-Import', 'PTV Distances', 'PTV Overlap', 'ROI Centroid',
                                  'ROI Spread', 'ROI Cross-Section', 'OAR-PTV Centroid Dist', 'All (except age)',
                                  'Patient Ages']
        self.calculate_select = Select(value=self.calculate_options[0], options=self.calculate_options,
                                       title='Calculate:', width=150)
        self.calculate_missing_only = CheckboxGroup(labels=['Only Calculate Missing Values'], active=[0], width=280)
        self.calculate_exec_button = Button(label='Perform Calc', button_type='primary', width=150)
        self.calculate_exec_button.on_click(self.calculate_exec)

        self.download = Button(label="Download Table", button_type="default", width=150)
        self.download.callback = CustomJS(args=dict(source=self.source_csv),
                                          code=open(join(dirname(dirname(__file__)), 'download_new.js')).read())

        self.layout = row(column(row(self.import_inbox_button, Spacer(width=20), self.rebuild_db_button,
                                     Spacer(width=50), self.import_inbox_force),
                                 self.calculations_title,
                                 row(self.calculate_select, Spacer(width=20), self.calculate_missing_only,
                                     self.calculate_exec_button),
                                 self.calculate_condition,
                                 Div(text="<hr>", width=column_width),
                                 self.update_db_title,
                                 row(self.update_db_table, self.update_db_column, self.update_db_value,
                                     Spacer(width=45), self.update_db_button),
                                 self.update_db_condition,
                                 Div(text="<hr>", width=column_width),
                                 self.reimport_title,
                                 row(self.reimport_mrn_text, Spacer(width=10),
                                     self.reimport_old_data_select, Spacer(width=140), self.reimport_button),
                                 row(self.reimport_study_date_select, self.reimport_uid_select),
                                 Div(text="<hr>", width=column_width),
                                 row(self.delete_from_db_title),
                                 row(self.delete_from_db_column, Spacer(width=300), self.delete_from_db_button),
                                 row(self.delete_from_db_value, self.delete_auth_text),
                                 Div(text="<hr>", width=column_width),
                                 row(self.change_mrn_uid_title),
                                 row(self.change_mrn_uid_column, Spacer(width=300), self.change_mrn_uid_button),
                                 row(self.change_mrn_uid_old_value, self.change_mrn_uid_new_value)),
                          column(Div(text="<b>Query Database</b>", width=column_width),
                                 row(self.query_table, self.query_columns),
                                 self.query_condition,
                                 row(self.query_button, Spacer(width=25), self.download),
                                 self.query_data_table))

    def update_query_columns_ticker(self, attr, old, new):
        self.update_query_columns()

    def update_query_columns(self):
        new_options = DVH_SQL().get_column_names(self.query_table.value.lower())
        if self.query_table.value.lower() == 'dvhs':
            new_options.pop(new_options.index('dvh_string'))
            new_options.pop(new_options.index('roi_coord_string'))
            new_options.pop(new_options.index('dth_string'))
        options_tuples = [tuple([option, option]) for option in new_options]
        self.query_columns.options = options_tuples
        self.query_columns.value = ['']

    def update_update_db_columns_ticker(self, attr, old, new):
        self.update_update_db_column()

    def update_update_db_column(self):
        new_options = DVH_SQL().get_column_names(self.update_db_table.value.lower())
        new_options.pop(new_options.index('import_time_stamp'))
        if self.update_db_table.value.lower() == 'dvhs':
            new_options.pop(new_options.index('dvh_string'))
            new_options.pop(new_options.index('roi_coord_string'))

        self.update_db_column.options = new_options
        self.update_db_column.value = new_options[0]

    def update_query_source(self):
        columns = [v for v in self.query_columns.value if v]
        for i, key in enumerate(['mrn', 'study_instance_uid']):  # move/add mrn and study_instance_uid to the front
            if key in columns:
                columns.pop(columns.index(key))
            columns.insert(i, key)

        table_columns = [TableColumn(field=c, title=c) for c in columns]

        query_cursor = DVH_SQL().query(self.query_table.value, ','.join(columns).strip(),
                                       self.query_condition.value, order_by='mrn')
        new_data = {c: [str(line[i]) for line in query_cursor] for i, c in enumerate(columns)}

        if new_data:
            self.source.data = new_data
            self.query_data_table.columns = table_columns
            self.query_data_table.width = [700, 150*len(table_columns)][len(table_columns) > 5]
            self.update_csv()

    def update_db(self):
        if self.update_db_condition.value and self.update_db_value.value:
            self.update_db_button.label = 'Updating...'
            self.update_db_button.button_type = 'danger'
            update_value = self.update_db_value.value
            if self.update_db_column.value in {'birth_date', 'sim_study_date'}:
                update_value = update_value + "::date"
            DVH_SQL().update(self.update_db_table.value, self.update_db_column.value, update_value,
                             self.update_db_condition.value)
            self.update_query_source()
            self.update_db_button.label = 'Update'
            self.update_db_button.button_type = 'warning'

            self.roi_manager.update_uncategorized_variation_select()
            self.roi_manager.update_ignored_variations_select()

    def delete_from_db(self):
        if self.delete_from_db_value.value and self.delete_auth_text.value == 'delete':
            condition = self.delete_from_db_column.value + " = '" + self.delete_from_db_value.value + "'"
            DVH_SQL().delete_rows(condition)
            self.update_query_source()
            self.delete_from_db_value.value = ''
            self.delete_auth_text.value = ''

            self.roi_manager.update_uncategorized_variation_select()
            self.roi_manager.update_ignored_variations_select()

    def change_mrn_uid(self):
        self.change_mrn_uid_button.label = 'Updating...'
        self.change_mrn_uid_button.button_type = 'danger'
        old = self.change_mrn_uid_old_value.value
        new = self.change_mrn_uid_new_value.value
        if old and new and old != new:
            if self.change_mrn_uid_column.value == 'mrn':
                DVH_SQL().change_mrn(old, new)
            elif self.change_mrn_uid_column.value == 'study_instance_uid':
                DVH_SQL().change_uid(old, new)
        self.change_mrn_uid_old_value.value = ''
        self.change_mrn_uid_new_value.value = ''
        self.change_mrn_uid_button.label = 'Rename'
        self.change_mrn_uid_button.button_type = 'warning'
        self.update_query_source()

    def delete_auth_text_ticker(self, attr, old, new):
        self.delete_from_db_button.button_type = ['warning', 'danger'][new == 'delete']

    def import_inbox(self):
        if self.import_inbox_button.label in {'Cancel'}:
            self.rebuild_db_button.label = 'Rebuild database'
            self.rebuild_db_button.button_type = 'warning'
        else:
            self.import_inbox_button.button_type = 'warning'
            self.import_inbox_button.label = 'Importing...'

            force_update = 0 in self.import_inbox_force.active
            move_files = 2 in self.import_inbox_force.active
            import_latest_only = 1 in self.import_inbox_force.active

            dicom_to_sql(force_update=force_update, import_latest_only=import_latest_only, move_files=move_files)

        self.roi_manager.update_uncategorized_variation_select()

        self.import_inbox_button.button_type = 'success'
        self.import_inbox_button.label = 'Import all from inbox'

    def rebuild_db_button_click(self):
        if self.rebuild_db_button.button_type in {'warning'}:
            self.rebuild_db_button.label = 'Are you sure?'
            self.rebuild_db_button.button_type = 'danger'
            self.import_inbox_button.button_type = 'success'
            self.import_inbox_button.label = 'Cancel'

        else:
            directories = load_directories()
            self.rebuild_db_button.label = 'Rebuilding...'
            self.rebuild_db_button.button_type = 'danger'
            self.import_inbox_button.button_type = 'success'
            self.import_inbox_button.label = 'Import all from inbox'
            rebuild_database(directories['imported'])
            self.rebuild_db_button.label = 'Rebuild database'
            self.rebuild_db_button.button_type = 'warning'

    def update_all_min_distances_in_db(self, *condition):
        if condition and condition[0]:
            condition = " AND (" + condition[0] + ")"
        else:
            condition = ''
        condition = "(LOWER(roi_type) IN ('organ', 'ctv', 'gtv') AND (" \
                    "LOWER(roi_name) NOT IN ('external', 'skin') OR " \
                    "LOWER(physician_roi) NOT IN ('uncategorized', 'ignored', 'external', 'skin')))" + condition
        if 0 in self.calculate_missing_only.active:
            if condition:
                condition = "(%s) AND dist_to_ptv_min is NULL" % condition
            else:
                condition = "dist_to_ptv_min is NULL"
        rois = DVH_SQL().query('dvhs', 'study_instance_uid, roi_name, physician_roi', condition)

        total_rois = float(len(rois))
        for i, roi in enumerate(rois):
            self.calculate_exec_button.label = str(int((float(i) / total_rois) * 100)) + '%'
            if roi[1].lower() not in {'external', 'skin'} and \
                    roi[2].lower() not in {'uncategorized', 'ignored', 'external', 'skin'}:
                print('updating dist to ptv:', roi[1], sep=' ')
                db_update.min_distances(roi[0], roi[1])
            else:
                print('skipping dist to ptv:', roi[1], sep=' ')

    def update_all(self, variable, *condition):
        variable_function_map = {'ptv_overlap': db_update.treatment_volume_overlap,
                                 'centroid': db_update.centroid,
                                 'spread': db_update.spread,
                                 'cross_section': db_update.cross_section,
                                 'ptv_centroids': db_update.dist_to_ptv_centroids}
        null_variable = variable
        if variable == 'ptv_centroids':
            null_variable = 'dist_to_ptv_centroids'
        elif variable == 'spread':
            null_variable = 'spread_x'
        elif variable == 'cross_section':
            null_variable = 'cross_section_max'

        final_condition = {True: ["(%s is NULL)" % null_variable], False: []}[0 in self.calculate_missing_only.active]
        if condition and condition[0]:
            final_condition.append('(%s)' % condition[0])
        final_condition = ' AND '.join(final_condition)

        rois = DVH_SQL().query('dvhs', 'study_instance_uid, roi_name, physician_roi', final_condition)

        total_rois = float(len(rois))
        for i, roi in enumerate(rois):
            self.calculate_exec_button.label = str(int((float(i) / total_rois) * 100)) + '%'
            print('updating %s:' % variable, roi[1], sep=' ')
            variable_function_map[variable](roi[0], roi[1])

    def update_all_tv_overlaps_in_db(self, condition):
        self.update_all('ptv_overlap', condition)

    def update_all_centroids_in_db(self, condition):
        self.update_all('centroid', condition)

    def update_all_spreads_in_db(self, condition):
        self.update_all('spread', condition)

    def update_all_cross_sections_in_db(self, condition):
        self.update_all('cross_section', condition)

    def update_all_dist_to_ptv_centoids_in_db(self, condition):
        self.update_all('ptv_centroids', condition)

    def update_all_except_age_in_db(self, *condition):
        for f in self.calculate_select.options:
            if f not in {'Patient Ages', 'Default Post-Import'}:
                self.calculate_select.value = f
                self.calculate_exec()

    def update_default_post_import(self, *condition):
        for f in ['PTV Distances', 'PTV Overlap', 'OAR-PTV Centroid Dist']:
            self.calculate_select.value = f
            self.calculate_exec()
        self.calculate_select.value = 'Default Post-Import'

    # Calculates volumes using Shapely, not dicompyler
    # This function is not in the GUI
    @staticmethod
    def recalculate_roi_volumes(*condition):
        rois = DVH_SQL().query('dvhs', 'study_instance_uid, roi_name, physician_roi', condition[0])

        counter = 0.
        total_rois = float(len(rois))
        for roi in rois:
            counter += 1.
            print('updating volume:', roi[1], int(100. * counter / total_rois), sep=' ')
            db_update.volumes(roi[0], roi[1])

    # Calculates surface area using Shapely
    # This function is not in the GUI
    @staticmethod
    def recalculate_surface_areas(*condition):
        rois = DVH_SQL().query('dvhs', 'study_instance_uid, roi_name, physician_roi', condition[0])

        roi_count = float(len(rois))
        for i, roi in enumerate(rois):
            print('updating surface area:', roi[1], int(100. * float(i) / roi_count), sep=' ')
            db_update.surface_area(roi[0], roi[1])

    def reimport_mrn_ticker(self, attr, old, new):
        new_options = DVH_SQL().get_unique_values('Plans', 'sim_study_date', "mrn = '%s'" % new)
        if not new_options:
            new_options = ['MRN not found']
        self.reimport_study_date_select.options = new_options
        self.reimport_study_date_select.value = new_options[0]

    def reimport_study_date_ticker(self, attr, old, new):
        if new != 'MRN not found':
            if new == 'None':
                new_options = DVH_SQL().get_unique_values('Plans',
                                                          'study_instance_uid',
                                                          "mrn = '%s'" %
                                                          self.reimport_mrn_text.value)
            else:
                new_options = DVH_SQL().get_unique_values('Plans',
                                                          'study_instance_uid',
                                                          "mrn = '%s' and sim_study_date = '%s'" %
                                                          (self.reimport_mrn_text.value, new))
        else:
            new_options = ['Study Date not found']

        self.reimport_uid_select.options = new_options
        self.reimport_uid_select.value = new_options[0]

    def reimport_button_click(self):
        dicom_directory = DVH_SQL().query('DICOM_Files',
                                          "folder_path",
                                          "study_instance_uid = '%s'" % self.reimport_uid_select.value)[0][0]
        if os.path.isdir(dicom_directory):
            if not os.listdir(dicom_directory):
                print("WARNING: %s is empty." % dicom_directory)
                print("Aborting DICOM reimport.")
            else:
                self.reimport_button.label = "Updating..."
                self.reimport_button.button_type = 'danger'
                if self.reimport_old_data_select.value == "Delete from DB":
                    DVH_SQL().delete_rows("study_instance_uid = '%s'" % self.reimport_uid_select.value,
                                          ignore_table=['DICOM_Files'])

                dicom_to_sql(start_path=dicom_directory, force_update=True,
                             move_files=False, update_dicom_catalogue_table=False)
                self.reimport_button.label = "Reimport"
                self.reimport_button.button_type = 'warning'

                self.roi_manager.update_uncategorized_variation_select()
                self.roi_manager.update_ignored_variations_select()
        else:
            print("WARNING: %s does not exist" % dicom_directory)
            print("Aborting DICOM reimport.")

    def calculate_exec(self):
        calc_map = {'PTV Distances': self.update_all_min_distances_in_db,
                    'PTV Overlap': self.update_all_tv_overlaps_in_db,
                    'Patient Ages': recalculate_ages,
                    'ROI Centroid': self.update_all_centroids_in_db,
                    'ROI Spread': self.update_all_spreads_in_db,
                    'ROI Cross-Section': self.update_all_cross_sections_in_db,
                    'OAR-PTV Centroid Dist': self.update_all_dist_to_ptv_centoids_in_db,
                    'All (except age)': self.update_all_except_age_in_db,
                    'Default Post-Import': self.update_default_post_import}

        start_time = datetime.now()
        print(str(start_time), 'Beginning %s calculations' % self.calculate_select.value, sep=' ')

        self.calculate_exec_button.label = 'Calculating...'
        self.calculate_exec_button.button_type = 'warning'

        calc_map[self.calculate_select.value](self.calculate_condition.value)

        self.update_query_source()

        self.calculate_exec_button.label = 'Perform Calc'
        self.calculate_exec_button.button_type = 'primary'

        end_time = datetime.now()
        print(str(end_time), 'Calculations complete', sep=' ')

        print_run_time(start_time, end_time, "Calculations for %s" % self.calculate_select.value)

    def update_csv(self):
        src_data = [self.source.data]
        src_names = ['Queried Data']
        columns = list(src_data[0])
        columns.sort()

        for i, key in enumerate(['mrn', 'study_instance_uid']):  # move/add mrn and study_instance_uid to the front
            if key in columns:
                columns.pop(columns.index(key))
            columns.insert(i, key)

        csv_text = get_csv(src_data, src_names, columns)

        self.source_csv.data = {'text': [csv_text]}
