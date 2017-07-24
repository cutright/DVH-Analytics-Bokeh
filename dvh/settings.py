#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:43:28 2017

@author: nightowl
"""

from __future__ import print_function
from utilities import is_import_settings_defined, is_sql_connection_defined,\
    write_import_settings, write_sql_connection_settings, validate_sql_connection
import os
import time
from sql_connector import DVH_SQL
from bokeh.models.widgets import Button, TextInput, Div
from bokeh.layouts import layout
from bokeh.io import curdoc


if is_sql_connection_defined():
    DVH_SQL().initialize_database()

directories = {}
config = {}
save_needed = False


def load_directories():
    global directories
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Get Import settings
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if is_import_settings_defined():
        script_dir = os.path.dirname(__file__)
        rel_path = "preferences/import_settings.txt"
        abs_file_path = os.path.join(script_dir, rel_path)

        with open(abs_file_path, 'r') as document:
            directories = {}
            for line in document:
                line = line.split()
                if not line:
                    continue
                try:
                    directories[line[0]] = line[1:][0]
                except:
                    directories[line[0]] = ''
    else:
        directories = {'inbox': '',
                       'imported': '',
                       'review': ''}


def load_sql_settings():
    global config
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Get SQL settings
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if is_sql_connection_defined():
        script_dir = os.path.dirname(__file__)
        rel_path = "preferences/sql_connection.cnf"
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

        if 'user' not in config.keys():
            config['user'] = ''
            config['password'] = ''

    else:
        config = {'host': 'localhost',
                  'dbname': 'dvh',
                  'port': '5432',
                  'user': '',
                  'password': ''}


def reload_directories():
    load_directories()
    input_inbox.value = directories['inbox']
    input_imported.value = directories['imported']
    input_review.value = directories['review']


def reload_sql_settings():
    load_sql_settings()
    input_host.value = config['host']
    input_port.value = config['port']
    input_dbname.value = config['dbname']
    input_user.value = config['user']
    input_password.value = config['password']


def save_directories():
    global directories
    update_direcories()
    write_import_settings(directories)
    reload_directories()


def save_sql_settings():
    global config
    update_sql_settings()
    write_sql_connection_settings(config)
    reload_sql_settings()
    save_sql_settings_button.button_type = 'success'
    save_sql_settings_button.label = 'Save'


def update_direcories():
    global directories
    directories['inbox'] = input_inbox.value
    directories['imported'] = input_imported.value
    directories['review'] = input_review.value


def update_sql_settings():
    global config
    config['host'] = input_host.value
    config['port'] = input_port.value
    config['dbname'] = input_dbname.value
    config['user'] = input_user.value
    config['password'] = input_password.value


def update_inbox_status(attr, old, new):
    directories['inbox'] = new

    script_dir = os.path.dirname(__file__)
    rel_path = new[2:len(new)]
    abs_dir_path = os.path.join(script_dir, rel_path)

    if os.path.isdir(new) or (os.path.isdir(abs_dir_path) and new[0:2] == './'):
        input_inbox.title = "Inbox"
        save_dir_button.button_type = 'success'
    elif not new:
        input_inbox.title = "Inbox --- Path Needed ---"
        save_dir_button.button_type = 'warning'
    else:
        input_inbox.title = "Inbox --- Invalid Path ---"
        save_dir_button.button_type = 'warning'

    update_dir_save_status()


def update_imported_status(attr, old, new):
    directories['imported'] = new

    script_dir = os.path.dirname(__file__)
    rel_path = new[2:len(new)]
    abs_dir_path = os.path.join(script_dir, rel_path)

    if os.path.isdir(new) or (os.path.isdir(abs_dir_path) and new[0:2] == './'):
        input_imported.title = "Imported"
        save_dir_button.button_type = 'success'
    elif not new:
        input_imported.title = "Imported --- Path Needed ---"
        save_dir_button.button_type = 'warning'
    else:
        input_imported.title = "Imported --- Invalid Path ---"
        save_dir_button.button_type = 'warning'

    update_dir_save_status()


def update_review_status(attr, old, new):

    directories['review'] = new

    script_dir = os.path.dirname(__file__)
    rel_path = new[2:len(new)]
    abs_dir_path = os.path.join(script_dir, rel_path)

    if os.path.isdir(new) or (os.path.isdir(abs_dir_path) and new[0:2] == './'):
        input_review.title = "Review"
        save_dir_button.button_type = 'success'
    elif not new:
        input_review.title = "Review --- Path Needed ---"
        save_dir_button.button_type = 'warning'
    else:
        input_review.title = "Review --- Invalid Path ---"
        save_dir_button.button_type = 'warning'

    update_dir_save_status()


def update_dir_save_status():

    dir_save_status = True

    script_dir = os.path.dirname(__file__)

    for path in directories.itervalues():
        rel_path = path[2:len(path)]
        abs_dir_path = os.path.join(script_dir, rel_path)
        if not(os.path.isdir(path) or (os.path.isdir(abs_dir_path) and path[0:2] == './')):
            dir_save_status = False

    if dir_save_status:
        save_dir_button.button_type = 'success'
    else:
        save_dir_button.button_type = 'warning'


def echo():
    global config
    update_sql_settings()
    initial_button_type = echo_button.button_type
    initial_label = echo_button.label
    if validate_sql_connection(config):
        echo_button.button_type = 'success'
        echo_button.label = 'Success'
    else:
        echo_button.button_type = 'warning'
        echo_button.label = 'Fail'

    time.sleep(1.5)
    echo_button.button_type = initial_button_type
    echo_button.label = initial_label


# Load Settings
load_directories()
load_sql_settings()


def check_tables():

    initial_label = check_tables_button.label
    initial_button_type = check_tables_button.button_type

    try:
        tables = ['dvhs', 'plans', 'beams', 'rxs']
        table_result = {}
        for table in tables:
            table_result[table] = DVH_SQL().check_table_exists(table)

        if all(table_result.itervalues()):
            check_tables_button.button_type = 'success'
            check_tables_button.label = 'Success'
        else:
            check_tables_button.button_type = 'warning'
            check_tables_button.label = 'Fail'

        time.sleep(1.5)
        check_tables_button.button_type = initial_button_type
        check_tables_button.label = initial_label
    except:
        check_tables_button.button_type = 'warning'
        check_tables_button.label = 'No Connection'
        time.sleep(1.5)
        check_tables_button.button_type = initial_button_type
        check_tables_button.label = initial_label


def create_tables():
    initial_label = create_tables_button.label
    initial_button_type = create_tables_button.button_type
    if initial_label == 'Cancel':
        create_tables_button.button_type = 'primary'
        create_tables_button.label = 'Create Tables'
        clear_tables_button.button_type = 'primary'
        clear_tables_button.label = 'Clear Tables'
    else:
        try:
            DVH_SQL().initialize_database()
        except:
            create_tables_button.button_type = 'warning'
            create_tables_button.label = 'No Connection'
            time.sleep(1.5)
            create_tables_button.button_type = initial_button_type
            create_tables_button.label = initial_label


def clear_tables():

    if clear_tables_button.button_type == 'danger':
        try:
            DVH_SQL().reinitialize_database()
        except:
            clear_tables_button.button_type = 'warning'
            clear_tables_button.label = 'No Connection'
            time.sleep(1.5)
            clear_tables_button.button_type = 'primary'
            clear_tables_button.label = 'Clear Tables'
        create_tables_button.button_type = 'primary'
        create_tables_button.label = 'Create Tables'
        clear_tables_button.button_type = 'primary'
        clear_tables_button.label = 'Clear Tables'
    elif clear_tables_button.button_type == 'primary':
        clear_tables_button.button_type = 'danger'
        clear_tables_button.label = 'Are you sure?'
        create_tables_button.button_type = 'success'
        create_tables_button.label = 'Cancel'


def save_needed_sql(attr, old, new):
    save_sql_settings_button.label = 'Save Needed'
    save_sql_settings_button.button_type = 'warning'


######################################################
# Layout objects
######################################################
div_import = Div(text="<b>DICOM Directories</b>")
div_horizontal_bar_settings = Div(text="<hr>", width=900)
input_inbox = TextInput(value=directories['inbox'], title="Inbox", width=300)
input_inbox.on_change('value', update_inbox_status)
input_imported = TextInput(value=directories['imported'], title="Imported", width=300)
input_imported.on_change('value', update_imported_status)
input_review = TextInput(value=directories['review'], title="Review", width=300)
input_review.on_change('value', update_review_status)

div_sql = Div(text="<b>SQL Settings</b>")
input_host = TextInput(value=config['host'], title="Host", width=300)
input_port = TextInput(value=config['port'], title="Port", width=300)
input_dbname = TextInput(value=config['dbname'], title="Database Name", width=300)
input_user = TextInput(value=config['user'], title="User (Leave blank for OS authentication)", width=300)
input_password = TextInput(value=config['password'], title="Password (Leave blank for OS authentication)", width=300)
input_host.on_change('value', save_needed_sql)
input_port.on_change('value', save_needed_sql)
input_dbname.on_change('value', save_needed_sql)
input_user.on_change('value', save_needed_sql)
input_password.on_change('value', save_needed_sql)

# Reload and Save objects
reload_dir_button = Button(label='Reload', button_type='primary', width=100)
reload_dir_button.on_click(reload_directories)
save_dir_button = Button(label='Save', button_type='success', width=100)
save_dir_button.on_click(save_directories)
update_dir_save_status()

# SQL Table check/create/reinitialize objects
check_tables_button = Button(label='Check Tables', button_type='primary', width=100)
check_tables_button.on_click(check_tables)
create_tables_button = Button(label='Create Tables', button_type='primary', width=100)
create_tables_button.on_click(create_tables)
clear_tables_button = Button(label='Clear Tables', button_type='primary', width=100)
clear_tables_button.on_click(clear_tables)

reload_sql_settings_button = Button(label='Reload', button_type='primary', width=100)
reload_sql_settings_button.on_click(reload_sql_settings)
save_sql_settings_button = Button(label='Save', button_type='success', width=100)
save_sql_settings_button.on_click(save_sql_settings)
echo_button = Button(label="Echo", button_type='primary', width=100)
echo_button.on_click(echo)

settings_layout = layout([[div_import],
                          [input_inbox],
                          [input_imported],
                          [input_review],
                          [reload_dir_button, save_dir_button],
                          [div_horizontal_bar_settings],
                          [div_sql],
                          [input_host, input_port],
                          [input_user, input_password],
                          [input_dbname],
                          [reload_sql_settings_button, echo_button, save_sql_settings_button],
                          [check_tables_button, create_tables_button, clear_tables_button]])

# Create the document Bokeh server will use to generate the webpage
curdoc().add_root(settings_layout)
curdoc().title = "DVH Analytics"


if __name__ == '__main__':
    pass
