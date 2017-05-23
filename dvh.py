#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 16:57 2017
@author: Dan Cutright, PhD
This is the main python file for command line implementation.
"""

import sys
from dvh.test import test_dvh_code
from dvh.dicom_to_sql import dicom_to_sql
from dvh.utilities import recalculate_ages
from dvh.sql_connector import DVH_SQL


def import_dicom(flags):

    if 'force-update' in flags:
        force_update = True
    else:
        force_update = False

    if 'do-not-organize-files' in flags:
        organize_files = False
    else:
        organize_files = True

    if 'do-not-move-files' in flags:
        move_files = False
    else:
        move_files = True

    dicom_to_sql(force_update=force_update, organize_files=organize_files, move_files=move_files)


def print_patient_ids():
    mrns = DVH_SQL().get_unique_values('plans', 'mrn')
    if len(mrns) == 0:
        print "No plans have been imported"
    else:
        for i in range(0, len(mrns)):
            print mrns[i]


def print_patient_ids_with_no_ages():

    mrns = DVH_SQL().query('plans', 'mrn', 'age is NULL');
    if len(mrns) == 0:
        print "No plans found with no age"
    else:
        for i in range(0, len(mrns)):
            print str(mrns[i][0])


if __name__ == '__main__':

    arg_count = len(sys.argv)
    call = sys.argv[1]

    flags = []
    for i in range(0, arg_count):
        if sys.argv[i][0:2] == '--':
            flags.append(sys.argv[i][2:len(sys.argv[i])])

    if arg_count == 1:
        print "argument required, for example 'python dvh-analytics.py test"

    else:
        if call == 'test':
            test_dvh_code()

        elif call == 'import':
            import_dicom(flags)

        elif call == 'recalculate-ages':
            recalculate_ages()

        elif call == 'print-patient-ids':
            print_patient_ids()

        elif call == 'print-patient-ids-with-no-age':
            print_patient_ids_with_no_ages()

        elif call == 'initialize':
            # create script with user input to create import_settings.txt and sql_connection.cnf
            pass

        elif call == 'ping':
            cnx = DVH_SQL()
            cnx.close()
            print "SQL DB is alive!"

        else:
            print call + " is not a valid call"
