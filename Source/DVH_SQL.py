#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 11:33:10 2017

@author: nightowl
"""

import mysql.connector
from mysql.connector import Error
import os


class DVH_SQL:
    def __init__(self):
        with open('SQL_Connection.cnf', 'r') as document:
            config = {}
            for line in document:
                line = line.split()
                if not line:
                    continue
                config[line[0]] = line[1:][0]
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

    def send(self, sql_file_name):

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

    def insert_dvhs(self, roi_table):

        file_path = 'insert_values_DVHs.sql'

        # Import each ROI from ROI_PyTable, append to output text file
        sql_input = []
        for x in range(1, len(roi_table)):
            sql_input.append(str(roi_table[x].MRN))
            sql_input.append(str(roi_table[x].study_instance_uid))
            sql_input.append(roi_table[x].roi_name)
            sql_input.append(roi_table[x].roi_type)
            sql_input.append(str(round(roi_table[x].volume, 3)))
            sql_input.append(str(round(roi_table[x].min_dose, 2)))
            sql_input.append(str(round(roi_table[x].mean_dose, 2)))
            sql_input.append(str(round(roi_table[x].max_dose, 2)))
            sql_input.append(str(roi_table[x].dose_bin_size))
            sql_input.append(roi_table[x].dvh_str)
            sql_input = '\',\''.join(sql_input)
            sql_input += '\');'
            Prepend = 'INSERT INTO DVHs VALUES (\''
            sql_input = Prepend + str(sql_input)
            sql_input += '\n'
            with open(file_path, "a") as text_file:
                text_file.write(sql_input)
            sql_input = []

        self.send(file_path)
        os.remove(file_path)
        print('DVHs Imported.')

    def insert_plans(self, plan):

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
        sql_input = '\',\''.join(sql_input)
        sql_input += '\');'
        sql_input = sql_input.replace("'(NULL)'", "(NULL)")
        Prepend = 'INSERT INTO Plans VALUES (\''
        sql_input = Prepend + str(sql_input)
        sql_input += '\n'
        with open(file_path, "a") as text_file:
            text_file.write(sql_input)

        self.send(file_path)
        os.remove(file_path)
        print('Plan Imported.')

    def insert_beams(self, beam_table):

        file_path = 'insert_values_beams.sql'

        # Import each ROI from ROI_PyTable, append to output text file
        sql_input = []
        for x in range(0, len(beam_table)):
            sql_input.append(str(beam_table[x].MRN))
            sql_input.append(str(beam_table[x].study_instance_uid))
            sql_input.append(str(beam_table[x].beam_num))
            sql_input.append(beam_table[x].description)
            sql_input.append(str(beam_table[x].fx_group))
            sql_input.append(str(beam_table[x].fxs))
            sql_input.append(str(beam_table[x].fx_group_beam_count))
            sql_input.append(str(round(beam_table[x].beam_dose, 3)))
            sql_input.append(str(beam_table[x].mu))
            sql_input.append(beam_table[x].radiation_type)
            sql_input.append(str(beam_table[x].energy))
            sql_input.append(beam_table[x].delivery_type)
            sql_input.append(str(beam_table[x].cp_count))
            sql_input.append(str(beam_table[x].gantry_start))
            sql_input.append(str(beam_table[x].gantry_end))
            sql_input.append(beam_table[x].gantry_rot_dir)
            sql_input.append(str(beam_table[x].col_angle))
            sql_input.append(str(beam_table[x].couch_ang))
            sql_input.append(beam_table[x].isocenter_coord)
            sql_input.append(str(round(beam_table[x].ssd, 2)))
            sql_input = '\',\''.join(sql_input)
            sql_input += '\');'
            Prepend = 'INSERT INTO Beams VALUES (\''
            sql_input = Prepend + str(sql_input)
            sql_input += '\n'
            with open(file_path, "a") as text_file:
                text_file.write(sql_input)
            sql_input = []

        self.send(file_path)
        os.remove(file_path)
        print('Beams Imported.')

    def delete_rows(self, condition_str):

        cmd = 'DELETE FROM Plans WHERE ' + condition_str + ';\n'
        cmd += 'DELETE FROM DVHs WHERE ' + condition_str + ';\n'
        cmd += 'DELETE FROM Beams WHERE ' + condition_str + ';'
        self.cursor.execute(cmd, multi=True)
        self.cnx.commit()

    def reinitialize_database(self):

        self.cursor.execute('DROP TABLE Plans;')
        self.cursor.execute('DROP TABLE DVHs;')
        self.cursor.execute('DROP TABLE Beams;')
        self.cnx.commit()
        self.send("create_tables.sql")


if __name__ == '__main__':
    pass
