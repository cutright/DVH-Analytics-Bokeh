#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Tools used to interact with SQL database
Created on Sat Mar  4 11:33:10 2017
@author: Dan Cutright, PhD
"""

# code currently only supports MySQL by Oracle
import psycopg2
import os
from datetime import datetime


class DVH_SQL:
    def __init__(self):
        # Read SQL configuration file
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "preferences/sql_connection.cnf"
        abs_file_path = os.path.join(script_dir, rel_path)
        with open(abs_file_path, 'r') as document:
            config = {}
            for line in document:
                line = line.split()
                if not line:
                    continue
                config[line[0]] = line[1:][0]
                # Convert strings to boolean
                if line[1:][0].lower() == 'true':
                    config[line[0]] = True
                elif line[1:][0].lower() == 'false':
                    config[line[0]] = False

        self.dbname = config['dbname']

        cnx = psycopg2.connect(**config)

        self.cnx = cnx
        self.cursor = cnx.cursor()

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
        query = 'Select ' + return_col_str + ' from ' + table_name
        if condition_str and condition_str[0]:
            query += ' where ' + condition_str[0]
        query += ';'

        self.cursor.execute(query)
        results = self.cursor.fetchall()

        return results

    def update(self, table_name, column, value, condition_str):
        update = "Update " + table_name + " SET " + column + " = '" \
                 + str(value) \
                 + "' WHERE " + condition_str

        self.cursor.execute(update)
        self.cnx.commit()

    def is_study_instance_uid_in_table(self, table_name, study_instance_uid):
        query = 'Select study_instance_uid from ' + table_name
        query += " where study_instance_uid = '" + study_instance_uid + "';"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        if results:
            return True
        else:
            return False

    def insert_dvhs(self, dvh_table):

        file_path = 'insert_values_DVHs.sql'

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
                         dvh_table.institutional_roi_name[x],
                         dvh_table.physician_roi_name[x],
                         dvh_table.roi_name[x],
                         dvh_table.roi_type[x],
                         str(round(dvh_table.volume[x], 3)),
                         str(round(dvh_table.min_dose[x], 2)),
                         str(round(dvh_table.mean_dose[x], 2)),
                         str(round(dvh_table.max_dose[x], 2)),
                         dvh_table.dvh_str[x]]
            sql_input = '\',\''.join(sql_input)
            sql_input += '\');'
            prepend = 'INSERT INTO DVHs VALUES (\''
            sql_input = prepend + str(sql_input)
            sql_input += '\n'
            with open(file_path, "a") as text_file:
                text_file.write(sql_input)

        self.execute_file(file_path)
        os.remove(file_path)
        print('DVHs Imported.')

    def insert_plan(self, plan):

        file_path = 'insert_plan_' + plan.mrn + '.sql'

        # Import each ROI from ROI_PyTable, append to output text file
        sql_input = [str(plan.mrn),
                     str(plan.birth_date),
                     str(plan.age),
                     plan.patient_sex,
                     str(plan.sim_study_date),
                     plan.physician,
                     plan.tx_site,
                     str(plan.rx_dose),
                     str(plan.fxs),
                     plan.tx_energies,
                     plan.study_instance_uid,
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
                     plan.heterogeneity_correction]
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
        print('Plan Imported.')

    def insert_beams(self, beams):

        file_path = 'insert_values_beams.sql'

        # Import each ROI from ROI_PyTable, append to output text file
        for x in range(0, beams.count):
            sql_input = [str(beams.mrn[x]),
                         str(beams.study_instance_uid[x]),
                         str(beams.beam_number[x]),
                         beams.beam_name[x],
                         str(beams.fx_group[x]),
                         str(beams.fxs[x]),
                         str(beams.fx_grp_beam_count[x]),
                         str(round(beams.beam_dose[x], 3)),
                         str(beams.beam_mu[x]),
                         beams.radiation_type[x],
                         str(beams.beam_energy[x]),
                         beams.beam_type[x],
                         str(beams.control_point_count[x]),
                         str(beams.gantry_start[x]),
                         str(beams.gantry_end[x]),
                         beams.gantry_rot_dir[x],
                         str(beams.collimator_angle[x]),
                         str(beams.couch_angle[x]),
                         beams.isocenter[x],
                         str(round(beams.ssd[x], 2)),
                         beams.treatment_machine[x]]
            sql_input = '\',\''.join(sql_input)
            sql_input += '\');'
            prepend = 'INSERT INTO Beams VALUES (\''
            sql_input = prepend + str(sql_input)
            sql_input += '\n'
            with open(file_path, "a") as text_file:
                text_file.write(sql_input)

        self.execute_file(file_path)
        os.remove(file_path)
        print('Beams Imported.')

    def insert_rxs(self, rx_table):

        file_path = 'insert_values_rxs.sql'

        for x in range(0, rx_table.count):
            sql_input = [str(rx_table.mrn[x]),
                         str(rx_table.study_instance_uid[x]),
                         str(rx_table.plan_name[x]),
                         str(rx_table.fx_grp_name[x]),
                         str(rx_table.fx_grp_number[x]),
                         str(rx_table.fx_grp_count[x]),
                         str(round(rx_table.fx_dose[x], 2)),
                         str(rx_table.fxs[x]),
                         str(round(rx_table.rx_dose[x], 2)),
                         str(round(rx_table.rx_percent[x], 1)),
                         str(rx_table.normalization_method[x]),
                         str(rx_table.normalization_object[x])]
            sql_input = '\',\''.join(sql_input)
            sql_input += '\');'
            prepend = 'INSERT INTO Rxs VALUES (\''
            sql_input = prepend + str(sql_input)
            sql_input += '\n'
            with open(file_path, "a") as text_file:
                text_file.write(sql_input)

        self.execute_file(file_path)
        os.remove(file_path)
        print('Rxs Imported.')

    def delete_rows(self, condition_str):

        self.cursor.execute('DELETE FROM Plans WHERE ' + condition_str + ';')
        self.cnx.commit()
        self.cursor.execute('DELETE FROM DVHs WHERE ' + condition_str + ';')
        self.cnx.commit()
        self.cursor.execute('DELETE FROM Rxs WHERE ' + condition_str + ';')
        self.cnx.commit()
        self.cursor.execute('DELETE FROM Beams WHERE ' + condition_str + ';')
        self.cnx.commit()

    def reinitialize_database(self):

        print str(datetime.now()), 'Dropping tables'
        self.cursor.execute('DROP TABLE IF EXISTS Plans;')
        self.cursor.execute('DROP TABLE IF EXISTS DVHs;')
        self.cursor.execute('DROP TABLE IF EXISTS Beams;')
        self.cursor.execute('DROP TABLE IF EXISTS Rxs;')
        self.cnx.commit()
        print str(datetime.now()), 'Loading create_tables.sql'
        script_dir = os.path.dirname(__file__)
        rel_path = "preferences/create_tables.sql"
        abs_file_path = os.path.join(script_dir, rel_path)
        print str(datetime.now()), 'Executing create_tables.sql'
        self.execute_file(abs_file_path)
        print str(datetime.now()), 'Tables created'

    def does_db_exist(self):
        # Check if database exists
        line = "SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower('"
        line += self.dbname + "');"
        self.cursor.execute(line)

        if len(self.cursor.fetchone()) > 0:
            return True
        else:
            return False

    def get_unique_values(self, table, column):
        query = "select distinct " + column + " from " + table + ";"
        self.cursor.execute(query)
        cursor_return = self.cursor.fetchall()
        unique_values = []
        for i in range(0, len(cursor_return)):
            unique_values.append(str(cursor_return[i][0]))
        unique_values.sort()
        return unique_values

    def get_column_names(self, table_name):
        query = "select column_name from information_schema.columns where table_name = '"
        query += table_name
        query += "';"
        self.cursor.execute(query)
        cursor_return = self.cursor.fetchall()
        columns = []
        for i in range(0, len(cursor_return)):
            columns.append(str(cursor_return[i][0]))
        columns.sort()
        return columns

    def get_min_value(self, table, column):
        query = 'SELECT ' + column + ' FROM ' + table + ' ORDER BY ' + column + ' ASC LIMIT 1;'
        self.cursor.execute(query)
        cursor_return = self.cursor.fetchone()
        return cursor_return[0]

    def get_max_value(self, table, column):
        query = 'SELECT ' + column + ' FROM ' + table + ' ORDER BY ' + column + ' DESC LIMIT 1;'
        self.cursor.execute(query)
        cursor_return = self.cursor.fetchone()
        return cursor_return[0]

    def get_roi_count_from_query(self, **kwargs):
        if 'uid' in kwargs:
            study_instance_uid = kwargs['uid']
            db_constraints_list = []
            for i in range(0, len(study_instance_uid)):
                db_constraints_list.append(study_instance_uid[i])
            condition = "study_instance_uid in ('"
            condition += "', '".join(db_constraints_list)
            condition += "')"
            if 'dvh_condition' in kwargs and kwargs['dvh_condition']:
                condition = " and " + condition
        else:
            condition = ''

        if 'dvh_condition' in kwargs and kwargs['dvh_condition']:
            condition = kwargs['dvh_condition'] + condition

        return len(self.query('DVHs', 'mrn', condition))


if __name__ == '__main__':
    pass
