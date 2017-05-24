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
import os
from getpass import getpass


def get_import_settings_from_user():
    print "Please enter the full directory path for each category"

    print "\nThis is where dicom files live before import."
    inbox_file_path = raw_input('Inbox: ')

    print "\nThis is where dicom files move to after import."
    imported_file_path = raw_input('Imported: ')

    print "\nThis is where dicom files to be reviewed live, but will not be imported."
    review_file_path = raw_input('DVH Review: ')

    import_settings = {'inbox': str(inbox_file_path),
                       'imported': str(imported_file_path),
                       'review': str(review_file_path)}

    return import_settings


def get_sql_connection_parameters_from_user():

    print "\nPlease enter the host address\n(defaults to 'localhost' if left empty)"
    host = raw_input('Host: ')
    if not host:
        host = 'localhost'

    print "\nPlease enter the user name\n(leave empty for OS authentication)"
    user = raw_input('User: ')

    if user:
        print "\nPlease enter the password, if any\n(will not display key strokes)"
        password = getpass('Password: ')

    print "\nPlease enter the database name\n(defaults to dvh if empty)"
    dbname = raw_input('Database name: ')
    if not dbname:
        dbname = 'dvh'

    print "\nPlease enter the database port\n(defaults to PostgreSQL default: 5432)"
    port = raw_input('Port: ')
    if not port:
        port = '5432'

    sql_connection_parameters = {'host': str(host),
                                 'dbname': str(dbname),
                                 'port': str(port)}

    if user:
        sql_connection_parameters['user'] = str(user)
        sql_connection_parameters['password'] = str(password)

    return sql_connection_parameters


def write_import_settings(settings):

    import_text = ['inbox ' + settings['inbox'],
                   'imported ' + settings['imported'],
                   'review ' + settings['review']]
    import_text = '\n'.join(import_text)

    script_dir = os.path.dirname(__file__)
    rel_path = "dvh/preferences/import_settings.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "w") as text_file:
        text_file.write(import_text)


def write_sql_connection_settings(config):

    text = []
    for key, value in config.iteritems():
        text.append(key + ' ' + value)
    text = '\n'.join(text)

    script_dir = os.path.dirname(__file__)
    rel_path = "dvh/preferences/sql_connection.cnf"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "w") as text_file:
        text_file.write(text)


def set_import_settings():
    config = get_import_settings_from_user()
    write_import_settings(config)


def set_sql_connection_parameters():
    config = get_sql_connection_parameters_from_user()
    write_sql_connection_settings(config)


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

        elif call == 'settings':
            if not flags or 'import' in flags:
                set_import_settings()
            if not flags or 'sql' in flags:
                set_sql_connection_parameters()

        elif call == 'echo':
            cnx = DVH_SQL()
            cnx.close()
            print "SQL DB is alive!"

        else:
            print call + " is not a valid call"
