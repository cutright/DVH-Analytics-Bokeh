#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 16:57 2017
@author: Dan Cutright, PhD
This is the main python file for command line implementation.
"""

from dicom_to_sql import dicom_to_sql
from utilities import recalculate_ages, Temp_DICOM_FileSet
from sql_connector import DVH_SQL
from analysis_tools import DVH
import os
from getpass import getpass
import argparse
from subprocess import call


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
            print "ERROR: SQL settings are not yet defined.  Please run:\n    $ dvh" \
                  " settings --sql"

    return valid


def settings(**kwargs):
    if not kwargs:
        set_import_settings()
        set_sql_connection_parameters()
    else:
        if 'dir' in kwargs and kwargs['dir']:
            set_import_settings()
        if 'sql' in kwargs and kwargs['sql']:
            set_sql_connection_parameters()


def test_dvh_code():

    if not is_import_settings_defined() and not is_sql_connection_defined():
        print "ERROR: Import and SQL settings are not yet defined.  Please run:\n    $ dvh" \
              " settings"
    elif not is_import_settings_defined():
        print "ERROR: Import settings are not yet defined.  Please run:\n    $ dvh" \
              " settings --dir"
    elif not is_sql_connection_defined():
        print "ERROR: SQL settings are not yet defined.  Please run:\n    $ dvh" \
              " settings --sql"
    else:
        is_import_valid = validate_import_settings()
        is_sql_connection_valid = validate_sql_connection()
        if not is_import_valid and not is_sql_connection_valid:
            print("ERROR: Create the directories listed above or input valid directories.")
            print("ERROR: Cannot connect to SQL.")
            print("Please run:")
            print("    $ dvh"
                  " settings")
        elif not is_import_valid:
            print("ERROR: Create the directories listed above or input valid directories by running:")
            print("    $ dvh"
                  " settings --dir")
        elif not is_sql_connection_valid:
            print("ERROR: Cannot connect to SQL.")
            print("Verify database is active and/or update SQL connection information with:")
            print("    $ dvh"
                  " settings --sql")

        else:
            print "Importing test files"
            dicom_to_sql(start_path="test_files/",
                         organize_files=False,
                         move_files=False,
                         force_update=False)

            print "Reading data from SQL DB with analysis_tools.py"
            test = DVH()

            print "Reading dicom information from test files with utilities.py (for plan review module)"
            test_files = Temp_DICOM_FileSet(start_path="test_files/")

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
    rel_path = "preferences/import_settings.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "w") as text_file:
        text_file.write(import_text)


def write_sql_connection_settings(config):

    text = []
    for key, value in config.iteritems():
        text.append(key + ' ' + value)
    text = '\n'.join(text)

    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/sql_connection.cnf"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "w") as text_file:
        text_file.write(text)


def set_import_settings():
    config = get_import_settings_from_user()
    write_import_settings(config)


def set_sql_connection_parameters():
    config = get_sql_connection_parameters_from_user()
    write_sql_connection_settings(config)


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


def main():
    parser = argparse.ArgumentParser(description='Command line interface for DVH Analytics')
    parser.add_argument('--sql',
                        help='Modify SQL connection settings',
                        default=False,
                        action='store_true')
    parser.add_argument('--dir',
                        help='Modify import directory settings',
                        default=False,
                        action='store_true')
    parser.add_argument('--start-path',
                        dest='start_path',
                        help='modify the start path for dicom import',
                        default=None)
    parser.add_argument('--do-not-organize',
                        help='Import will organize files by default. Set to False to leave files in the same hierarchy',
                        default=False,
                        action='store_true')
    parser.add_argument('--do-not-move',
                        help='Import will move files by default.  Set to False to leave files where they are',
                        default=False,
                        action='store_true')
    parser.add_argument('--force-update',
                        help='Import will add to SQL DB even if DB already contains data from dicom files',
                        default=False,
                        action='store_true')
    parser.add_argument('--allow-websocket-origin',
                        dest='allow_websocket_origin',
                        help='Allows Bokeh server to accept a non-default origin',
                        default=None)
    parser.add_argument('--port',
                        dest='port',
                        help='Initializes Bokeh server on a non-default port',
                        default=None)
    parser.add_argument('command', nargs='+', help='bar help')
    args = parser.parse_args()

    if args.command:

        if args.command[0] == 'settings':
            if not args.sql and not args.dir:
                settings()
            else:
                if args.sql:
                    settings(sql=True)
                if args.dir:
                    settings(dir=True)

        elif args.command[0] == 'test':
            test_dvh_code()

        elif args.command[0] == 'echo':
            validate_sql_connection()

        elif args.command[0] == 'print_mrns':
            print_mrns()

        elif args.command[0] == 'recalculate_ages':
            recalculate_ages()

        elif args.command[0] == 'import':

            # Set defaults
            start_path = False
            organize_files = True
            move_files = True
            force_update = False

            if args.start_path:
                if os.path.isdir(args.start_path):
                    start_path = str(args.start_path)
                else:
                    print args.start_path, 'is not a valid path'
            if args.do_not_organize:
                organize_files = False
            if args.do_not_move:
                move_files = False
            if args.force_update:
                force_update = True

            dicom_to_sql(start_path=start_path,
                         organize_files=organize_files,
                         move_files=move_files,
                         force_update=force_update)
        elif args.command[0] == 'run':

            command = ["bokeh", "serve"]

            script_dir = os.path.dirname(__file__)

            if args.allow_websocket_origin:
                command.append("--allow-websocket-origin")
                command.append(args.allow_websocket_origin)
            if args.port:
                command.append("--port")
                command.append(args.port)
            if not args.allow_websocket_origin and not args.port:
                command.append("--show")

            command.append(script_dir)

            call(command)


if __name__ == '__main__':
    main()
