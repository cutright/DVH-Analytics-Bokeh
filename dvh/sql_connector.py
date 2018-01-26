#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Tools used to interact with SQL database
Created on Sat Mar  4 11:33:10 2017
@author: Dan Cutright, PhD
"""

from __future__ import print_function
import psycopg2
import os


class DVH_SQL:
    def __init__(self, *config):
        if config:
            config = config[0]
        else:
            # Read SQL configuration file
            script_dir = os.path.dirname(__file__)
            rel_path = "preferences/sql_connection.cnf"
            abs_file_path = os.path.join(script_dir, rel_path)
            with open(abs_file_path, 'r') as document:
                config = {}
                for line in document:
                    line = line.split()
                    if not line:
                        continue
                    config[line[0]] = line[1:][0]

        self.dbname = config['dbname']

        cnx = psycopg2.connect(**config)

        self.cnx = cnx
        self.cursor = cnx.cursor()
        self.tables = ['DVHs', 'Plans', 'Rxs', 'Beams', 'DICOM_Files']

    def close(self):
        self.cnx.close()

    # Executes lines within text file named 'sql_file_name' to SQL
    def execute_file(self, sql_file_name):

        for line in open(sql_file_name):
            self.cursor.execute(line)
        self.cnx.commit()

    def check_table_exists(self, table_name):

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(table_name.replace('\'', '\'\'')))
        if self.cursor.fetchone()[0] == 1:
            return True
        else:
            return False

    def query(self, table_name, return_col_str, *condition_str):
        query = "Select %s from %s;" % (return_col_str, table_name)
        if condition_str and condition_str[0]:
            query = "Select %s from %s where %s;" % (return_col_str, table_name, condition_str[0])

        self.cursor.execute(query)
        results = self.cursor.fetchall()

        return results

    def query_generic(self, query_str):
        self.cursor.execute(query_str)
        return self.cursor.fetchall()

    def update(self, table_name, column, value, condition_str):

        try:
            temp = float(value)
            value_is_numeric = True
        except ValueError:
            value_is_numeric = False

        if '::date' in str(value):
            value = "'%s'::date" % value.strip('::date')  # augment value string for postgresql date formatting
        elif value_is_numeric:
            value = str(value)
        else:
            value = "'%s'" % str(value)  # need quotes to input a string

        update = "Update %s SET %s = %s WHERE %s" % (table_name, column, value, condition_str)
        self.cursor.execute(update)
        self.cnx.commit()

    def is_study_instance_uid_in_table(self, table_name, study_instance_uid):
        query = "Select study_instance_uid from %s where study_instance_uid = '%s';" % (table_name, study_instance_uid)
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return bool(results)

    def insert_dvhs(self, dvh_table):
        file_path = 'insert_values_DVHs.sql'

        if os.path.isfile(file_path):
            os.remove(file_path)

        # Import each ROI from ROI_PyTable, append to output text file
        if max(dvh_table.ptv_number) > 1:
            multi_ptv = True
        else:
            multi_ptv = False
        for x in range(0, dvh_table.count):
            if multi_ptv and dvh_table.ptv_number[x] > 0:
                dvh_table.roi_type[x] = 'PTV' + str(dvh_table.ptv_number[x])
            sql_input = [str(dvh_table.mrn[x]),
                         str(dvh_table.study_instance_uid[x]),
                         dvh_table.institutional_roi[x],
                         dvh_table.physician_roi[x],
                         dvh_table.roi_name[x].replace("'", "`"),
                         dvh_table.roi_type[x],
                         str(round(dvh_table.volume[x], 3)),
                         str(round(dvh_table.min_dose[x], 2)),
                         str(round(dvh_table.mean_dose[x], 2)),
                         str(round(dvh_table.max_dose[x], 2)),
                         dvh_table.dvh_str[x],
                         dvh_table.roi_coord[x],
                         '(NULL)',
                         '(NULL)',
                         '(NULL)',
                         '(NULL)',
                         str(round(dvh_table.surface_area[x], 2)),
                         '(NULL)',
                         'NOW()']
            sql_input = '\',\''.join(sql_input)
            sql_input += '\');'
            sql_input = sql_input.replace("'(NULL)'", "(NULL)")
            prepend = 'INSERT INTO DVHs VALUES (\''
            sql_input = prepend + str(sql_input)
            sql_input += '\n'
            with open(file_path, "a") as text_file:
                text_file.write(sql_input)

        self.execute_file(file_path)
        os.remove(file_path)
        print('DVHs imported')

    def insert_plan(self, plan):
        file_path = 'insert_plan_' + plan.mrn + '.sql'

        if os.path.isfile(file_path):
            os.remove(file_path)

        # Import each ROI from ROI_PyTable, append to output text file
        sql_input = [str(plan.mrn),
                     plan.study_instance_uid,
                     str(plan.birth_date),
                     str(plan.age),
                     plan.patient_sex,
                     str(plan.sim_study_date),
                     plan.physician,
                     plan.tx_site,
                     str(plan.rx_dose),
                     str(plan.fxs),
                     plan.patient_orientation,
                     str(plan.plan_time_stamp),
                     str(plan.struct_time_stamp),
                     str(plan.dose_time_stamp),
                     plan.tps_manufacturer,
                     plan.tps_software_name,
                     str(plan.tps_software_version),
                     plan.tx_modality,
                     str(plan.tx_time),
                     str(plan.total_mu),
                     plan.dose_grid_resolution,
                     plan.heterogeneity_correction,
                     'false',
                     'NOW()']
        sql_input = '\',\''.join(sql_input)
        sql_input += '\');'
        sql_input = sql_input.replace("'(NULL)'", "(NULL)")
        prepend = 'INSERT INTO Plans VALUES (\''
        sql_input = prepend + str(sql_input)
        sql_input += '\n'
        with open(file_path, "a") as text_file:
            text_file.write(sql_input)

        self.execute_file(file_path)
        os.remove(file_path)
        print('Plan imported')

    def insert_beams(self, beams):

        file_path = 'insert_values_beams.sql'

        if os.path.isfile(file_path):
            os.remove(file_path)

        # Import each ROI from ROI_PyTable, append to output text file
        for x in range(0, beams.count):

            if beams.beam_mu[x] > 0:
                sql_input = [str(beams.mrn[x]),
                             str(beams.study_instance_uid[x]),
                             str(beams.beam_number[x]),
                             beams.beam_name[x].replace("'", "`"),
                             str(beams.fx_group[x]),
                             str(beams.fxs[x]),
                             str(beams.fx_grp_beam_count[x]),
                             str(round(beams.beam_dose[x], 3)),
                             str(beams.beam_mu[x]),
                             beams.radiation_type[x],
                             str(round(beams.beam_energy_min[x], 2)),
                             str(round(beams.beam_energy_max[x], 2)),
                             beams.beam_type[x],
                             str(beams.control_point_count[x]),
                             str(beams.gantry_start[x]),
                             str(beams.gantry_end[x]),
                             beams.gantry_rot_dir[x],
                             str(beams.gantry_range[x]),
                             str(beams.gantry_min[x]),
                             str(beams.gantry_max[x]),
                             str(beams.collimator_start[x]),
                             str(beams.collimator_end[x]),
                             beams.collimator_rot_dir[x],
                             str(beams.collimator_range[x]),
                             str(beams.collimator_min[x]),
                             str(beams.collimator_max[x]),
                             str(beams.couch_start[x]),
                             str(beams.couch_end[x]),
                             beams.couch_rot_dir[x],
                             str(beams.couch_range[x]),
                             str(beams.couch_min[x]),
                             str(beams.couch_max[x]),
                             beams.beam_dose_pt[x],
                             beams.isocenter[x],
                             str(beams.ssd[x]),
                             beams.treatment_machine[x],
                             beams.scan_mode[x],
                             str(beams.scan_spot_count[x]),
                             str(beams.beam_mu_per_deg[x]),
                             str(beams.beam_mu_per_cp[x]),
                             'NOW()']
                sql_input = '\',\''.join(sql_input)
                sql_input += '\');'
                sql_input = sql_input.replace("'(NULL)'", "(NULL)")
                prepend = 'INSERT INTO Beams VALUES (\''
                sql_input = prepend + str(sql_input)
                sql_input += '\n'
                with open(file_path, "a") as text_file:
                    text_file.write(sql_input)

        self.execute_file(file_path)
        os.remove(file_path)
        print('Beams imported')

    def insert_rxs(self, rx_table):

        file_path = 'insert_values_rxs.sql'

        if os.path.isfile(file_path):
            os.remove(file_path)

        for x in range(0, rx_table.count):
            sql_input = [str(rx_table.mrn[x]),
                         str(rx_table.study_instance_uid[x]),
                         str(rx_table.plan_name[x]).replace("'", "`"),
                         str(rx_table.fx_grp_name[x]),
                         str(rx_table.fx_grp_number[x]),
                         str(rx_table.fx_grp_count[x]),
                         str(round(rx_table.fx_dose[x], 2)),
                         str(rx_table.fxs[x]),
                         str(round(rx_table.rx_dose[x], 2)),
                         str(round(rx_table.rx_percent[x], 1)),
                         str(rx_table.normalization_method[x]),
                         str(rx_table.normalization_object[x]).replace("'", "`"),
                         'NOW()']
            sql_input = '\',\''.join(sql_input)
            sql_input += '\');'
            prepend = 'INSERT INTO Rxs VALUES (\''
            sql_input = prepend + str(sql_input)
            sql_input += '\n'
            with open(file_path, "a") as text_file:
                text_file.write(sql_input)

        self.execute_file(file_path)
        os.remove(file_path)
        print('Rxs imported')

    def insert_dicom_file_row(self, mrn, uid, dir_name, plan_file, struct_file, dose_file):

        sql_cmd = "INSERT INTO DICOM_Files VALUES ('%s', '%s', '%s', '%s', '%s', '%s', NOW());\n" % \
                  (mrn, uid, dir_name, plan_file, struct_file, dose_file)
        sql_cmd.replace("'(NULL)'", "(NULL)")
        self.cursor.execute(sql_cmd)
        self.cnx.commit()

    def delete_rows(self, condition_str):

        for table in self.tables:
            self.cursor.execute("DELETE FROM %s WHERE %s;" % (table, condition_str))
            self.cnx.commit()

    def change_mrn(self, old, new):
        condition = "mrn = '%s'" % old
        for table in self.tables:
            self.update(table, 'mrn', new, condition)

    def change_uid(self, old, new):
        condition = "study_instance_uid = '%s'" % old
        for table in self.tables:
            self.update(table, 'study_instance_uid', new, condition)

    def delete_dvh(self, roi_name, study_instance_uid):
        self.cursor.execute("DELETE FROM DVHs WHERE roi_name = '%s' and study_instance_uid = '%s';"
                            % (roi_name, study_instance_uid))
        self.cnx.commit()

    def drop_tables(self):
        print('Dropping tables')
        for table in self.tables:
            self.cursor.execute("DROP TABLE IF EXISTS %s;" % table)
            self.cnx.commit()

    def drop_table(self, table):
        print("Dropping table: %s" % table)
        self.cursor.execute("DROP TABLE IF EXISTS %s;" % table)
        self.cnx.commit()

    def initialize_database(self):
        script_dir = os.path.dirname(__file__)
        rel_path = "preferences/create_tables.sql"
        abs_file_path = os.path.join(script_dir, rel_path)
        self.execute_file(abs_file_path)

    def reinitialize_database(self):
        self.drop_tables()
        self.initialize_database()

    def does_db_exist(self):
        # Check if database exists
        line = "SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower('%s');" % self.dbname
        self.cursor.execute(line)

        return bool(len(self.cursor.fetchone()))

    def is_sql_table_empty(self, table):
        line = "SELECT COUNT(*) FROM %s;" % table
        self.cursor.execute(line)
        count = self.cursor.fetchone()[0]
        return not(bool(count))

    def get_unique_values(self, table, column, *condition):
        if condition:
            query = "select distinct %s from %s where %s;" % (column, table, str(condition[0]))
        else:
            query = "select distinct %s from %s;" % (column, table)
        self.cursor.execute(query)
        cursor_return = self.cursor.fetchall()
        unique_values = [str(uv[0]) for uv in cursor_return]
        unique_values.sort()
        return unique_values

    def get_column_names(self, table_name):
        query = "select column_name from information_schema.columns where table_name = '%s';" % table_name.lower()
        self.cursor.execute(query)
        cursor_return = self.cursor.fetchall()
        columns = [str(c[0]) for c in cursor_return]
        columns.sort()
        return columns

    def get_min_value(self, table, column):
        query = "SELECT MIN(%s) FROM %s;" % (column, table)
        self.cursor.execute(query)
        cursor_return = self.cursor.fetchone()
        return cursor_return[0]

    def get_max_value(self, table, column):
        query = "SELECT MAX(%s) FROM %s;" % (column, table)
        self.cursor.execute(query)
        cursor_return = self.cursor.fetchone()
        return cursor_return[0]

    def get_roi_count_from_query(self, **kwargs):
        if 'uid' in kwargs:
            condition = "study_instance_uid in ('%s')" % "', '".join(kwargs['uid'])
            if 'dvh_condition' in kwargs and kwargs['dvh_condition']:
                condition = " and " + condition
        else:
            condition = ''

        if 'dvh_condition' in kwargs and kwargs['dvh_condition']:
            condition = kwargs['dvh_condition'] + condition

        return len(self.query('DVHs', 'mrn', condition))


if __name__ == '__main__':
    pass
