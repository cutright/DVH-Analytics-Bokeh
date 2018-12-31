#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
database editor model for admin view
Created on Tue Dec 25 2018
@author: Dan Cutright, PhD
"""

from __future__ import print_function
from tools.utilities import get_csv
from tools.io.preferences.import_settings import load_directories
import os
from os.path import dirname, join
from datetime import datetime
from tools.io.database.sql_connector import DVH_SQL
from tools.io.database.dicom.importer import dicom_to_sql, rebuild_database
from tools.io.database import update as db_update
from bokeh.models.widgets import Select, Button, TextInput, Div, MultiSelect, TableColumn, DataTable, CheckboxGroup
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Slider, CustomJS, Spacer


class DatabaseEditor:
    def __init__(self, roi_manager):

        self.roi_manager = roi_manager  # allows ROI Name manager updates after importing data

        self.source = ColumnDataSource(data=dict())
        self.source_csv = ColumnDataSource(data=dict(text=[]))

        self.import_inbox_button = Button(label='Import all from inbox', button_type='success', width=200)
        self.import_inbox_button.on_click(self.import_inbox)
        self.import_inbox_force = CheckboxGroup(labels=['Force Update', 'Import Latest Only', 'Move Files'],
                                                active=[1, 2])
        self.rebuild_db_button = Button(label='Rebuild database', button_type='warning', width=200)
        self.rebuild_db_button.on_click(self.rebuild_db_button_click)

        self.query_table = Select(value='DVHs', options=['DVHs', 'Plans', 'Rxs', 'Beams', 'DICOM_Files'], width=200,
                                  title='Table')
        self.query_columns = MultiSelect(title="Columns (Ctrl or Shift Click enabled)", width=250,
                                         options=[tuple(['', ''])])
        self.query_condition = TextInput(value='', title="Condition", width=300)
        self.query_button = Button(label='Query', button_type='primary', width=100)
        self.table_slider = Slider(start=300, end=2000, value=1000, step=10, title="Table Width")

        self.query_table.on_change('value', self.update_query_columns_ticker)
        self.query_button.on_click(self.update_query_source)

        self.update_db_title = Div(text="<b>Update Database</b>", width=1000)
        self.update_db_table = Select(value='DVHs', options=['DVHs', 'Plans', 'Rxs', 'Beams'], width=200, height=100,
                                      title='Table')
        self.update_db_column = Select(value='', options=[''], width=250, title='Column')
        self.update_db_value = TextInput(value='', title="Value", width=300)
        self.update_db_condition = TextInput(value='', title="Condition", width=300)
        self.update_db_button = Button(label='Update DB', button_type='warning', width=100)

        self.update_db_table.on_change('value', self.update_update_db_columns_ticker)
        self.update_db_button.on_click(self.update_db)

        self.update_query_columns()
        self.update_update_db_column()

        self.reimport_title = Div(text="<b>Reimport from DICOM</b>", width=1025)
        self.reimport_mrn_text = TextInput(value='', width=200, title='MRN')
        self.reimport_study_date_select = Select(value='', options=[''], width=200, height=100, title='Sim Study Date')
        self.reimport_uid_select = Select(value='', options=[''], width=425, height=100, title='Study Instance UID')
        self.reimport_old_data_select = Select(value='Delete from DB', options=['Delete from DB', 'Keep in DB'],
                                               width=150, height=100, title='Current Data')
        self.reimport_button = Button(label='Reimport', button_type='warning', width=100)

        self.reimport_mrn_text.on_change('value', self.reimport_mrn_ticker)
        self.reimport_study_date_select.on_change('value', self.reimport_study_date_ticker)
        self.reimport_button.on_click(self.reimport_button_click)

        self.query_data_table = DataTable(source=self.source, columns=[], width=1000)

        self.delete_from_db_title = Div(text="<b>Delete all data with mrn or study_instance_uid</b>", width=1000)
        self.delete_from_db_column = Select(value='mrn', options=['mrn', 'study_instance_uid'], width=200, height=100,
                                            title='Patient Identifier')
        self.delete_from_db_value = TextInput(value='', title="Value (required)", width=300)
        self.delete_from_db_button = Button(label='Delete', button_type='warning', width=100)
        self.delete_auth_text = TextInput(value='', title="Type 'delete' here to authorize", width=300)
        self.delete_auth_text.on_change('value', self.delete_auth_text_ticker)
        self.delete_from_db_button.on_click(self.delete_from_db)

        self.change_mrn_uid_title = Div(text="<b>Change mrn or study_instance_uid in all tables</b>", width=1000)
        self.change_mrn_uid_column = Select(value='mrn', options=['mrn', 'study_instance_uid'], width=200, height=100,
                                            title='Patient Identifier')
        self.change_mrn_uid_old_value = TextInput(value='', title="Old", width=300)
        self.change_mrn_uid_new_value = TextInput(value='', title="New", width=300)
        self.change_mrn_uid_button = Button(label='Rename', button_type='warning', width=100)
        self.change_mrn_uid_button.on_click(self.change_mrn_uid)

        self.calculations_title = Div(text="<b>Post Import Calculations</b>", width=1000)
        self.calculate_condition = TextInput(value='', title="Condition", width=300)
        self.calculate_options = ['Default Post-Import', 'PTV Distances', 'PTV Overlap', 'ROI Centroid',
                                  'ROI Spread', 'ROI Cross-Section', 'OAR-PTV Centroid Dist', 'All (except age)',
                                  'Patient Ages']
        self.calculate_select = Select(value=self.calculate_options[0], options=self.calculate_options,
                                       title='Calculate:')
        self.calculate_exec_button = Button(label='Perform Calc', button_type='primary', width=150)
        self.calculate_exec_button.on_click(self.calculate_exec)

        self.download = Button(label="Download Table", button_type="default", width=150)
        self.download.callback = CustomJS(args=dict(source=self.source_csv),
                                          code=open(join(dirname(dirname(__file__)), 'download_new.js')).read())

        self.layout = column(row(self.import_inbox_button, self.rebuild_db_button),
                             self.import_inbox_force,
                             Div(text="<b>Query Database</b>", width=1000),
                             row(self.query_table, self.query_columns, self.query_condition, self.table_slider,
                                 self.query_button),
                             self.update_db_title,
                             row(self.update_db_table, self.update_db_column, self.update_db_condition,
                                 self.update_db_value, self.update_db_button),
                             self.reimport_title,
                             row(self.reimport_mrn_text, Spacer(width=10), self.reimport_study_date_select,
                                 self.reimport_uid_select,
                                 self.reimport_old_data_select, Spacer(width=10), self.reimport_button),
                             row(self.delete_from_db_title),
                             row(self.delete_from_db_column, self.delete_from_db_value, self.delete_auth_text,
                                 self.delete_from_db_button),
                             row(self.change_mrn_uid_title),
                             row(self.change_mrn_uid_column, self.change_mrn_uid_old_value,
                                 self.change_mrn_uid_new_value, self.change_mrn_uid_button),
                             self.calculations_title,
                             row(self.calculate_condition, self.calculate_select, self.calculate_exec_button),
                             self.download,
                             self.query_data_table)

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
        columns = [v for v in self.query_columns.value]
        if 'mrn' not in columns:
            columns.insert(0, 'mrn')
        if 'study_instance_uid' not in columns:
            columns.insert(1, 'study_instance_uid')
        new_data = {}
        table_columns = []
        if not columns[-1]:
            columns.pop()
        for c in columns:
            new_data[c] = []
            table_columns.append(TableColumn(field=c, title=c))
        columns_str = ','.join(columns).strip()
        if self.query_condition.value:
            query_cursor = DVH_SQL().query(self.query_table.value, columns_str, self.query_condition.value)
        else:
            query_cursor = DVH_SQL().query(self.query_table.value, columns_str)

        for row in query_cursor:
            for i in range(len(columns)):
                new_data[columns[i]].append(str(row[i]))

        if new_data:
            self.source.data = new_data

            data_table_new = DataTable(source=self.source, columns=table_columns,
                                       width=int(self.table_slider.value), editable=True)
            self.layout.children.pop()
            self.layout.children.append(data_table_new)

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
        if new == 'delete':
            self.delete_from_db_button.button_type = 'danger'
        else:
            self.delete_from_db_button.button_type = 'warning'

    def import_inbox(self):
        if self.import_inbox_button.label in {'Cancel'}:
            self.rebuild_db_button.label = 'Rebuild database'
            self.rebuild_db_button.button_type = 'warning'
        else:
            self.import_inbox_button.button_type = 'warning'
            self.import_inbox_button.label = 'Importing...'
            if 0 in self.import_inbox_force.active:
                force_update = True
            else:
                force_update = False

            if 2 in self.import_inbox_force.active:
                move_files = True
            else:
                move_files = False

            if 1 in self.import_inbox_force.active:
                import_latest_only = True
            else:
                import_latest_only = False
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
        if condition:
            condition = " AND (" + condition[0] + ")"
        else:
            condition = ''
        condition = "(LOWER(roi_type) IN ('organ', 'ctv', 'gtv') AND (" \
                    "LOWER(roi_name) NOT IN ('external', 'skin') OR " \
                    "LOWER(physician_roi) NOT IN ('uncategorized', 'ignored', 'external', 'skin')))" + condition
        rois = DVH_SQL().query('dvhs', 'study_instance_uid, roi_name, physician_roi', condition)
        counter = 0.
        total_rois = float(len(rois))
        for roi in rois:
            self.calculate_exec_button.label = str(int((counter / total_rois) * 100)) + '%'
            counter += 1.
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
        if condition:
            rois = DVH_SQL().query('dvhs', 'study_instance_uid, roi_name, physician_roi', condition[0])
        else:
            rois = DVH_SQL().query('dvhs', 'study_instance_uid, roi_name, physician_roi')
        counter = 0.
        total_rois = float(len(rois))
        for roi in rois:
            self.calculate_exec_button.label = str(int((counter / total_rois) * 100)) + '%'
            counter += 1.
            print('updating %s:' % variable, roi[1], sep=' ')
            variable_function_map[variable](roi[0], roi[1])

    def update_all_tv_overlaps_in_db(self, *condition):
        self.update_all('ptv_overlap', condition)

    def update_all_centroids_in_db(self, *condition):
        self.update_all('centroid', condition)

    def update_all_spreads_in_db(self, *condition):
        self.update_all('spread', condition)

    def update_all_cross_sections_in_db(self, *condition):
        self.update_all('cross_section', condition)

    def update_all_dist_to_ptv_centoids_in_db(self, *condition):
        self.update_all('ptv_centroids', condition)

    def update_all_except_age_in_db(self):
        for f in self.calculate_select.options:
            if f not in {'Patient Ages', 'Default Post-Import'}:
                self.calculate_select.value = f
                self.calculate_exec()

    def update_default_post_import(self):
        for f in ['PTV Distances', 'PTV Overlap', 'OAR-PTV Centroid Dist']:
            self.calculate_select.value = f
            self.calculate_exec()
        self.calculate_select.value = 'Default Post-Import'

    # Calculates volumes using Shapely, not dicompyler
    # This function is not in the GUI
    @staticmethod
    def recalculate_roi_volumes(*condition):
        if condition:
            rois = DVH_SQL().query('dvhs', 'study_instance_uid, roi_name, physician_roi', condition[0])
        else:
            rois = DVH_SQL().query('dvhs', 'study_instance_uid, roi_name, physician_roi')
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
        if condition:
            rois = DVH_SQL().query('dvhs', 'study_instance_uid, roi_name, physician_roi', condition[0])
        else:
            rois = DVH_SQL().query('dvhs', 'study_instance_uid, roi_name, physician_roi')
        counter = 0.
        total_rois = float(len(rois))
        for roi in rois:
            counter += 1.
            print('updating surface area:', roi[1], int(100. * counter / total_rois), sep=' ')
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
                    'Patient Ages': db_update.recalculate_ages,
                    'ROI Centroid': self.update_all_centroids_in_db,
                    'ROI Spread': self.update_all_spreads_in_db,
                    'ROI Cross-Section': self.update_all_cross_sections_in_db,
                    'OAR-PTV Centroid Dist': self.update_all_dist_to_ptv_centoids_in_db,
                    'All (except age)': self.update_all_except_age_in_db,
                    'Default Post-Import': self.update_default_post_import}

        if self.calculate_select.value not in {'All (except age)', 'Default Post-Import'}:

            start_time = datetime.now()
            print(str(start_time), 'Beginning %s calculations' % self.calculate_condition.value, sep=' ')

            self.calculate_exec_button.label = 'Calculating...'
            self.calculate_exec_button.button_type = 'warning'

            if self.calculate_condition.value:
                calc_map[self.calculate_select.value](self.calculate_condition.value)
            else:
                calc_map[self.calculate_select.value]()

            self.update_query_source()

            self.calculate_exec_button.label = 'Perform Calc'
            self.calculate_exec_button.button_type = 'primary'

            end_time = datetime.now()
            print(str(end_time), 'Calculations complete', sep=' ')

            total_time = end_time - start_time
            seconds = total_time.seconds
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            if h:
                print("These calculations took %dhrs %02dmin %02dsec to complete" % (h, m, s))
            elif m:
                print("These calculations took %02dmin %02dsec to complete" % (m, s))
            else:
                print("These calculations took %02dsec to complete" % s)
        else:
            if self.calculate_condition.value:
                calc_map[self.calculate_select.value](self.calculate_condition.value)
            else:
                calc_map[self.calculate_select.value]()

    def update_csv(self):
        src_data = [self.source.data]
        src_names = ['Queried Data']
        columns = list(src_data[0])

        mrn_index, uid_index = None, None
        for i, c in enumerate(columns):
            if c == 'mrn':
                mrn_index = i
            if c == 'study_instance_uid':
                uid_index = i

        if uid_index is not None:
            columns.pop(uid_index)
            columns.insert(0, 'study_instance_uid')
        if mrn_index is not None:
            columns.pop(mrn_index)
            columns.insert(0, 'mrn')

        csv_text = get_csv(src_data, src_names, columns)

        self.source_csv.data = {'text': [csv_text]}
