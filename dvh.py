#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 16:57 2017
@author: Dan Cutright, PhD
This is the main python file for command line implementation.
"""

import sys
from dvh.dicom_to_sql import dicom_to_sql
from dvh.utilities import recalculate_ages, Temp_DICOM_FileSet
from dvh.sql_connector import DVH_SQL
from dvh.analysis_tools import DVH
import os
from getpass import getpass


def is_import_settings_defined():

    script_dir = os.path.dirname(__file__)
    rel_path = "dvh-analytics/preferences/import_settings.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    if os.path.isfile(abs_file_path):
        return True
    else:
        return False


def is_sql_connection_defined():

    script_dir = os.path.dirname(__file__)
    rel_path = "dvh-analytics/preferences/sql_connection.cnf"
    abs_file_path = os.path.join(script_dir, rel_path)

    if os.path.isfile(abs_file_path):
        return True
    else:
        return False


def validate_import_settings():
    script_dir = os.path.dirname(__file__)
    rel_path = "dvh-analytics/preferences/import_settings.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, 'r') as document:
        config = {}
        for line in document:
            line = line.split()
            if not line:
                continue
            config[line[0]] = line[1:][0]

    valid = True
    for key, value in config.iteritems():
        if not os.path.isdir(value):
            print 'invalid', key, 'path: ', value
            valid = False

    return valid


def validate_sql_connection():

    try:
        cnx = DVH_SQL()
        cnx.close()
        valid = True
    except:
        valid = False

    if valid:
        print "SQL DB is alive!"
    else:
        print "Connection to SQL DB could not be established."
        if not is_sql_connection_defined():
            print "ERROR: SQL settings are not yet defined.  Please run:\n    $ python dvh.py settings --sql"

    return valid


def settings(*flags):
    if flags:
        flags = flags[0]
    if not flags or 'import' in flags:
        set_import_settings()
    if not flags or 'sql' in flags:
        set_sql_connection_parameters()


def test_dvh_code():

    if not is_import_settings_defined() and not is_sql_connection_defined():
        print "ERROR: Import and SQL settings are not yet defined.  Please run:\n    $ python dvh.py settings"
    elif not is_import_settings_defined():
        print "ERROR: Import settings are not yet defined.  Please run:\n    $ python dvh.py settings --import"
    elif not is_sql_connection_defined():
        print "ERROR: SQL settings are not yet defined.  Please run:\n    $ python dvh.py settings --sql"
    else:
        is_import_valid = validate_import_settings()
        is_sql_connection_valid = validate_sql_connection()
        if not is_import_valid and not is_sql_connection_valid:
            print("ERROR: Create the directories listed above or input valid directories.")
            print("ERROR: Cannot connect to SQL.")
            print("Please run:")
            print("    $ python dvh.py settings")
        elif not is_import_valid:
            print("ERROR: Create the directories listed above or input valid directories by running:")
            print("    $ python dvh.py settings --import")
        elif not is_sql_connection_valid:
            print("ERROR: Cannot connect to SQL.")
            print("Verify database is active and/or update SQL connection information with:")
            print("    $ python dvh.py settings --sql")

        else:
            print "Importing test files"
            dicom_to_sql(start_path="test_files/example_dicom_files",
                         organize_files=False,
                         move_files=False,
                         force_update=False)

            print "Reading data from SQL DB with analysis_tools.py"
            test = DVH()

            print "Reading dicom information from test files with utilities.py (for plan review module)"
            test_files = Temp_DICOM_FileSet(start_path="test_files/example_dicom_files")

            print "Deleting test data from SQL database"
            for i in range(0, test_files.count):
                cond_str = "mrn = '" + test_files.mrn[i]
                cond_str += "' and study_instance_uid = '" + test_files.study_instance_uid[i] + "'"
                DVH_SQL().delete_rows(cond_str)

            print "Tests successful!"


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
    rel_path = "dvh-analytics/preferences/import_settings.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "w") as text_file:
        text_file.write(import_text)


def write_sql_connection_settings(config):

    text = []
    for key, value in config.iteritems():
        text.append(key + ' ' + value)
    text = '\n'.join(text)

    script_dir = os.path.dirname(__file__)
    rel_path = "dvh-analytics/preferences/sql_connection.cnf"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "w") as text_file:
        text_file.write(text)


def set_import_settings():
    config = get_import_settings_from_user()
    write_import_settings(config)


def set_sql_connection_parameters():
    config = get_sql_connection_parameters_from_user()
    write_sql_connection_settings(config)


def import_dicom(*flags):

    if flags:
        flags = flags[0]
    else:
        flags = []

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

    dicom_to_sql(force_update=force_update,
                 organize_files=organize_files,
                 move_files=move_files)


def print_mrns():
    mrns = DVH_SQL().get_unique_values('plans', 'mrn')
    if len(mrns) == 0:
        print "No plans have been imported"

    printed_mrns = []
    for i in range(0, len(mrns)):
        current_mrn = mrns[i]
        if current_mrn not in printed_mrns:
            printed_mrns.append(current_mrn)
            print current_mrn


def get_flags_modifier():
    bad_command = False
    flags = []
    modifier = []
    i = 1
    while i < arg_count:
        if sys.argv[i][0:2] == '--':
            current_flag = sys.argv[i][2:len(sys.argv[i])]

            if current_flag in call_map[call]['flags']:
                flags.append(current_flag)
                try:
                    if sys.argv[i + 1][0:2] != '--':
                        if call_map[call]['modifier']:
                            for j in range(i, arg_count):
                                modifier.append(sys.argv[j+1])
                            i = arg_count
                        else:
                            print "ERROR: Modifiers not allowed for --" + flags[-1]
                            bad_command = True
                            i += 1
                except:
                    pass
            else:
                print "ERROR: " + current_flag + " is not a valid flag"
                bad_command = True
        else:
            if i > 1:
                if not call_map[call]['modifier']:
                    print "ERROR: multiple calls given"
                    bad_command = True
        i += 1

    return flags, modifier, bad_command


call_map = {'test': {'function': test_dvh_code,
                     'flags': {},
                     'modifier': False},
            'echo': {'function': validate_sql_connection,
                     'flags': {},
                     'modifier': False},
            'import': {'function': import_dicom,
                       'flags': {'start_path', 'organize_files', 'move_files', 'force_update'},
                       'modifier': False},
            'print-mrns': {'function': print_mrns,
                           'flags': {},
                           'modifier': False},
            'settings': {'function': settings,
                         'flags': {'sql', 'import'},
                         'modifier': False},
            'recalculate-ages': {'function': recalculate_ages,
                                 'flags': {},
                                 'modifier': False}}


if __name__ == '__main__':

    arg_count = len(sys.argv)

    if arg_count == 1:
        print "Argument required: python dvh.py <call>"
        print "Call options are:"
        for key in call_map.keys():
            print key
    else:
        call = sys.argv[1]

        if call not in call_map:
            print call, "is not a valid call"

        else:
            flags, modifier, bad_command = get_flags_modifier()

            if not bad_command:
                if not flags or len(flags) == 0:
                    call_map[call]['function']()
                elif flags and not modifier:
                    call_map[call]['function'](flags)
                elif flags and modifier:
                    call_map[call]['function'](flags, modifier)
            else:
                print "Command not understood"
