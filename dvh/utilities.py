#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
from sql_to_python import QuerySQL
from sql_connector import DVH_SQL
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dicompylercore import dicomparser
import os
import dicom
import sys


class Temp_DICOM_FileSet:
    def __init__(self, **kwargs):

        # Read SQL configuration file
        script_dir = os.path.dirname(__file__)
        if 'start_path' in kwargs:
            rel_path = kwargs['start_path']
            abs_file_path = os.path.join(script_dir, rel_path)
            start_path = abs_file_path
        else:
            rel_path = "preferences/import_settings.txt"
            abs_file_path = os.path.join(script_dir, rel_path)
            with open(abs_file_path, 'r') as document:
                for line in document:
                    line = line.split()
                    if not line:
                        continue
                    if line[0] == 'review':
                        start_path = line[1:][0]

        self.plan = []
        self.structure = []
        self.dose = []
        self.mrn = []
        self.study_instance_uid = []

        f = []

        for root, dirs, files in os.walk(start_path, topdown=False):
            for name in files:
                f.append(os.path.join(root, name))

        plan_files = []
        study_uid_plan = []
        structure_files = []
        study_uid_structure = []
        dose_files = []
        study_uid_dose = []
        mrns = []

        for x in range(0, len(f)):
            try:
                dicom_file = dicom.read_file(f[x])
                if dicom_file.Modality.lower() == 'rtplan':
                    plan_files.append(f[x])
                    study_uid_plan.append(dicom_file.StudyInstanceUID)
                elif dicom_file.Modality.lower() == 'rtstruct':
                    structure_files.append(f[x])
                    study_uid_structure.append(dicom_file.StudyInstanceUID)
                elif dicom_file.Modality.lower() == 'rtdose':
                    dose_files.append(f[x])
                    study_uid_dose.append(dicom_file.StudyInstanceUID)
            except Exception:
                pass

        self.count = len(plan_files)

        for a in range(0, self.count):
            self.plan.append(plan_files[a])
            self.mrn.append(dicom.read_file(plan_files[a]).PatientID)
            self.study_instance_uid.append(dicom.read_file(plan_files[a]).StudyInstanceUID)
            for b in range(0, len(structure_files)):
                if study_uid_plan[a] == study_uid_structure[b]:
                    self.structure.append(structure_files[b])
            for c in range(0, len(dose_files)):
                if study_uid_plan[a] == study_uid_dose[c]:
                    self.dose.append(dose_files[c])

        if self.count == 0:
            self.plan.append('')
            self.mrn.append('')
            self.structure.append('')
            self.dose.append('')

    def get_roi_names(self, mrn):

        structure_file = self.structure[self.mrn.index(mrn)]
        rt_st = dicomparser.DicomParser(structure_file)
        rt_structures = rt_st.GetStructures()

        roi = {}
        for key in rt_structures:
            if rt_structures[key]['type'].upper() not in {'MARKER', 'REGISTRATION', 'ISOCENTER'}:
                roi[key] = rt_structures[key]['name']

        return roi


def recalculate_ages():

    dvh_data = QuerySQL('Plans', "mrn != ''")
    cnx = DVH_SQL()

    for i in range(0, len(dvh_data.mrn)):
        uid = dvh_data.study_instance_uid[i]
        sim_study_date = dvh_data.sim_study_date[i].split('-')
        birth_date = dvh_data.birth_date[i].split('-')

        birth_year = int(birth_date[0])
        birth_month = int(birth_date[1])
        birth_day = int(birth_date[2])
        birth_date_obj = datetime(birth_year, birth_month, birth_day)

        sim_study_year = int(sim_study_date[0])
        sim_study_month = int(sim_study_date[1])
        sim_study_day = int(sim_study_date[2])
        sim_study_date_obj = datetime(sim_study_year,
                                               sim_study_month,
                                               sim_study_day)

        if sim_study_date == '1800-01-01':
            age = '(NULL)'
        else:
            age = relativedelta(sim_study_date_obj, birth_date_obj).years

        condition = "study_instance_uid = '" + uid + "'"
        cnx.update('Plans', 'age', str(age), condition)

    cnx.cnx.close()


def datetime_str_to_obj(datetime_str):

    year = int(datetime_str[0:4])
    month = int(datetime_str[4:6])
    day = int(datetime_str[6:8])
    hour = int(datetime_str[8:10])
    minute = int(datetime_str[10:12])
    second = int(datetime_str[12:14])

    datetime_obj = datetime(year, month, day, hour, minute, second)

    return datetime_obj


def date_str_to_obj(date_str):

    year = int(date_str[0:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])

    return datetime(year, month, day)


def platform():
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('darwin'):
        return 'mac'
    return 'linux'


def is_import_settings_defined():

    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/import_settings.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    if os.path.isfile(abs_file_path):
        return True
    else:
        return False


def is_sql_connection_defined():

    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/sql_connection.cnf"
    abs_file_path = os.path.join(script_dir, rel_path)

    if os.path.isfile(abs_file_path):
        return True
    else:
        return False


def write_import_settings(directories):

    import_text = ['inbox ' + directories['inbox'],
                   'imported ' + directories['imported'],
                   'review ' + directories['review']]
    import_text = '\n'.join(import_text)

    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/import_settings.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "w") as text_file:
        text_file.write(import_text)


def write_sql_connection_settings(config):

    text = []
    for key, value in config.iteritems():
        if value:
            text.append(key + ' ' + value)
    text = '\n'.join(text)

    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/sql_connection.cnf"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "w") as text_file:
        text_file.write(text)


def validate_import_settings():
    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/import_settings.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, 'r') as document:
        config = {}
        for line in document:
            line = line.split()
            if not line:
                continue
            try:
                config[line[0]] = line[1:][0]
            except:
                config[line[0]] = ''

    valid = True
    for key, value in config.iteritems():
        if not os.path.isdir(value):
            print('invalid', key, 'path:', value, sep=" ")
            valid = False

    return valid


def validate_sql_connection(*config, **kwargs):

    if config:
        try:
            cnx = DVH_SQL(config[0])
            cnx.close()
            valid = True
        except:
            valid = False
    else:
        try:
            cnx = DVH_SQL()
            cnx.close()
            valid = True
        except:
            valid = False

    if not kwargs or ('verbose' in kwargs and kwargs['verbose']):
        if valid:
            print("SQL DB is alive!")
        else:
            print("Connection to SQL DB could not be established.")
            if not is_sql_connection_defined():
                print("ERROR: SQL settings are not yet defined.  Please run:\n",
                      "    $ dvh settings --sql", sep="")

    return valid


def change_angle_origin(angles, max_positive_angle):
    if len(angles) == 1:
        if angles[0] > max_positive_angle:
            return [angles[0] - 360]
        else:
            return angles
    new_angles = []
    for angle in angles:
        if angle > max_positive_angle:
            new_angles.append(angle - 360)
        elif angle == max_positive_angle:
            if angle == angles[0] and angles[1] > max_positive_angle:
                new_angles.append(angle - 360)
            elif angle == angles[-1] and angles[-2] > max_positive_angle:
                new_angles.append(angle - 360)
            else:
                new_angles.append(angle)
        else:
            new_angles.append(angle)
    return new_angles


def dicompyler_roi_coord_to_db_string(coord):
    contours = []
    for z in coord:
        for plane in coord[z]:
            points = [z]
            for point in plane['data']:
                points.append(str(point[0]))
                points.append(str(point[1]))
            contours.append(','.join(points))
    return ':'.join(contours)
