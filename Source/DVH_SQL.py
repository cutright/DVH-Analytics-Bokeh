#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Tools used to interact with SQL database
Created on Sat Mar  4 11:33:10 2017
@author: Dan Cutright, PhD
"""

# code currently only supports MySQL by Oracle
import mysql.connector
from mysql.connector import Error
import os


class DVH_SQL:
    def __init__(self):
        # Read SQL configuration file
        with open('SQL_Connection.cnf', 'r') as document:
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

        try:
            cnx = mysql.connector.connect(**config)

        except Error as error:
            print(error)

        finally:
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
        if condition_str:
            query += ' where ' + condition_str[0]
        query += ';'

        self.cursor.execute(query)
        results = self.cursor.fetchall()

        return results

    def get_study_uid(self, MRN):

        query = 'Select StudyInstanceUID from Plans where MRN=\'' + MRN + '\';'
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        return results

    def insert_dvhs(self, dvh_table):

        file_path = 'insert_values_DVHs.sql'

        # Import each ROI from ROI_PyTable, append to output text file
        sql_input = []
        for x in range(0, dvh_table.count):
            sql_input.append(str(dvh_table.MRN[x]))
            sql_input.append(str(dvh_table.study_instance_uid[x]))
            sql_input.append(dvh_table.institutional_roi_name[x])
            sql_input.append(dvh_table.physician_roi_name[x])
            sql_input.append(dvh_table.roi_name[x])
            sql_input.append(dvh_table.roi_type[x])
            sql_input.append(str(round(dvh_table.volume[x], 3)))
            sql_input.append(str(round(dvh_table.min_dose[x], 2)))
            sql_input.append(str(round(dvh_table.mean_dose[x], 2)))
            sql_input.append(str(round(dvh_table.max_dose[x], 2)))
            sql_input.append(str(dvh_table.dose_bin_size[x]))
            sql_input.append(dvh_table.dvh_str[x])
            sql_input = '\',\''.join(sql_input)
            sql_input += '\');'
            Prepend = 'INSERT INTO DVHs VALUES (\''
            sql_input = Prepend + str(sql_input)
            sql_input += '\n'
            with open(file_path, "a") as text_file:
                text_file.write(sql_input)
            sql_input = []

        self.execute_file(file_path)
        os.remove(file_path)
        print('DVHs Imported.')

    def insert_plan(self, plan):

        file_path = 'insert_plan_' + plan.MRN + '.sql'

        # Import each ROI from ROI_PyTable, append to output text file
        sql_input = []
        sql_input.append(str(plan.MRN))
        sql_input.append(str(plan.birthdate))
        sql_input.append(str(plan.age))
        sql_input.append(plan.sex)
        sql_input.append(plan.sim_study_date)
        sql_input.append(plan.rad_onc)
        sql_input.append(plan.tx_site)
        sql_input.append(str(plan.rx_dose))
        sql_input.append(str(plan.fxs))
        sql_input.append(plan.energies)
        sql_input.append(plan.study_instance_uid)
        sql_input.append(plan.patient_orientation)
        sql_input.append(str(plan.plan_time_stamp))
        sql_input.append(str(plan.roi_time_stamp))
        sql_input.append(str(plan.dose_time_stamp))
        sql_input.append(plan.tps_manufacturer)
        sql_input.append(plan.tps_software_name)
        sql_input.append(str(plan.tps_software_version))
        sql_input.append(plan.tx_modality)
        sql_input.append(str(plan.tx_time))
        sql_input.append(str(plan.total_mu))
        sql_input.append(plan.dose_grid_resolution)
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
        sql_input = []
        for x in range(0, beams.count):
            sql_input.append(str(beams.MRN[x]))
            sql_input.append(str(beams.study_instance_uid[x]))
            sql_input.append(str(beams.beam_num[x]))
            sql_input.append(beams.description[x])
            sql_input.append(str(beams.fx_group[x]))
            sql_input.append(str(beams.fxs[x]))
            sql_input.append(str(beams.fx_group_beam_count[x]))
            sql_input.append(str(round(beams.dose[x], 3)))
            sql_input.append(str(beams.mu[x]))
            sql_input.append(beams.radiation_type[x])
            sql_input.append(str(beams.energy[x]))
            sql_input.append(beams.delivery_type[x])
            sql_input.append(str(beams.cp_count[x]))
            sql_input.append(str(beams.gantry_start[x]))
            sql_input.append(str(beams.gantry_end[x]))
            sql_input.append(beams.gantry_rot_dir[x])
            sql_input.append(str(beams.col_angle[x]))
            sql_input.append(str(beams.couch_ang[x]))
            sql_input.append(beams.isocenter_coord[x])
            sql_input.append(str(round(beams.ssd[x], 2)))
            sql_input = '\',\''.join(sql_input)
            sql_input += '\');'
            prepend = 'INSERT INTO Beams VALUES (\''
            sql_input = prepend + str(sql_input)
            sql_input += '\n'
            with open(file_path, "a") as text_file:
                text_file.write(sql_input)
            sql_input = []

        self.execute_file(file_path)
        os.remove(file_path)
        print('Beams Imported.')

    def insert_rxs(self, rx_table):

        file_path = 'insert_fx_grps_' + plan.MRN + '.sql'

        sql_input = []
        sql_input.append(str(rx_table.MRN))
        sql_input.append(str(rx_table.study_instance_uid))
        sql_input.append(str(rx_table.fx_grp_name))
        sql_input.append(str(rx_table.fx_grp_num))
        sql_input.append(str(rx_table.fx_grps))
        sql_input.append(str(round(rx_table.fx_dose, 2)))
        sql_input.append(str(rx_table.fxs))
        sql_input.append(str(round(rx_table.rx_dose, 2)))
        sql_input.append(str(round(rx_table.rx_percent, 1)))
        sql_input.append(str(rx_table.norm_method))
        sql_input.append(str(rx_table.norm_object))
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

        cmd = 'DELETE FROM Plans WHERE ' + condition_str + ';\n'
        cmd += 'DELETE FROM DVHs WHERE ' + condition_str + ';\n'
        cmd += 'DELETE FROM Rxs WHERE ' + condition_str + ';\n'
        cmd += 'DELETE FROM Beams WHERE ' + condition_str + ';'
        self.cursor.execute(cmd, multi=True)
        self.cnx.commit()

    def reinitialize_database(self):

        if self.check_table_exists('Plans'):
            self.cursor.execute('DROP TABLE Plans;')
        if self.check_table_exists('DVHs'):
            self.cursor.execute('DROP TABLE DVHs;')
        if self.check_table_exists('Beams'):
            self.cursor.execute('DROP TABLE Beams;')
        if self.check_table_exists('Rxs'):
            self.cursor.execute('DROP TABLE Rxs;')
        self.cnx.commit()
        self.execute_file("create_tables.sql")


if __name__ == '__main__':
    pass
