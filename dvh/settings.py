#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:43:28 2017

@author: nightowl
"""

from __future__ import print_function
from future.utils import listvalues
from utilities import is_import_settings_defined, is_sql_connection_defined,\
    write_import_settings, write_sql_connection_settings, validate_sql_connection
import os
import time
from sql_connector import DVH_SQL
from bokeh.models.widgets import Button, TextInput, Div, PasswordInput
from bokeh.models import Spacer
from bokeh.layouts import layout, row, column
from bokeh.io import curdoc
import auth
from options import *
from get_settings import get_settings, parse_settings_file

# This depends on a user defined function in dvh/auth.py.  By default, this returns True
# It is up to the user/installer to write their own function (e.g., using python-ldap)
# Proper execution of this requires placing Bokeh behind a reverse proxy with SSL setup (HTTPS)
# Please see Bokeh documentation for more information
ACCESS_GRANTED = not AUTH_USER_REQ


directories = {}
config = {}
save_needed = False


def load_directories():
    global directories
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Get Import settings
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if is_import_settings_defined():
        directories = parse_settings_file(get_settings('import'))
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
        config = parse_settings_file(get_settings('sql'))

        if 'user' not in list(config):
            config['user'] = ''
            config['password'] = ''

        if 'password' not in list(config):
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
    save_dir_button.button_type = 'success'
    save_dir_button.label = 'Save'


def reload_sql_settings():
    load_sql_settings()
    input_host.value = config['host']
    input_port.value = config['port']
    input_dbname.value = config['dbname']
    input_user.value = config['user']
    input_password.value = config['password']
    save_sql_settings_button.button_type = 'success'
    save_sql_settings_button.label = 'Save'


def save_directories():
    update_directories()
    write_import_settings(directories)
    reload_directories()


def save_sql_settings():
    update_sql_settings()
    write_sql_connection_settings(config)
    reload_sql_settings()
    save_sql_settings_button.button_type = 'success'
    save_sql_settings_button.label = 'Save'


def update_directories():
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


def update_directory_status(dir_label, input_widget):

    directory = directories[dir_label.lower()]

    if os.path.isdir(directory):
        input_widget.title = dir_label
        save_dir_button.button_type = 'success'
    elif not directory:
        input_widget.title = "%s --- Path Needed ---" % dir_label
        save_dir_button.button_type = 'warning'
    else:
        input_widget.title = "%s --- Invalid Path ---" % dir_label
        save_dir_button.button_type = 'warning'

    update_dir_save_status()


def update_inbox(attr, old, new):
    directories['inbox'] = new
    update_directory_status("Inbox", input_inbox)


def update_imported(attr, old, new):
    directories['imported'] = new
    update_directory_status("Imported", input_imported)


def update_review(attr, old, new):
    directories['review'] = new
    update_directory_status("Review", input_review)


def update_dir_save_status():

    dir_save_status = True

    for path in listvalues(directories):
        if not(os.path.isdir(path)):
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
    if validate_sql_connection(config=config, verbose=False):
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

        if all(table_result.values()):
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


def auth_button_click():
    global ACCESS_GRANTED

    if not ACCESS_GRANTED:
        ACCESS_GRANTED = auth.check_credentials(auth_user.value, auth_pass.value, 'admin')
        if ACCESS_GRANTED:
            auth_button.label = 'Access Granted'
            auth_button.button_type = 'success'
            curdoc().clear()
            curdoc().add_root(settings_layout)
        else:
            auth_button.label = 'Failed'
            auth_button.button_type = 'danger'
            time.sleep(3)
            auth_button.label = 'Authenticate'
            auth_button.button_type = 'warning'


######################################################
# Layout objects
######################################################
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Custom authorization
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
auth_user = TextInput(value='', title='User Name:', width=150)
auth_pass = PasswordInput(value='', title='Password:', width=150)
auth_button = Button(label="Authenticate", button_type="warning", width=100)
auth_button.on_click(auth_button_click)
auth_div = Div(text="<b>DVH Analytics Admin</b>", width=600)
layout_login = column(auth_div,
                      row(auth_user, Spacer(width=50), auth_pass, Spacer(width=50), auth_button))

div_import = Div(text="<b>DICOM Directories</b>")
div_import_note = Div(text="Please fill in existing directory locations below.")
div_horizontal_bar_settings = Div(text="<hr>", width=900)
input_inbox = TextInput(value=directories['inbox'], title="Inbox", width=600)
input_inbox.on_change('value', update_inbox)
input_imported = TextInput(value=directories['imported'], title="Imported", width=600)
input_imported.on_change('value', update_imported)
input_review = TextInput(value=directories['review'], title="Review", width=600)
input_review.on_change('value', update_review)

div_sql = Div(text="<b>SQL Settings</b>")
input_host = TextInput(value=config['host'], title="Host", width=300)
input_port = TextInput(value=config['port'], title="Port", width=300)
input_dbname = TextInput(value=config['dbname'], title="Database Name", width=300)
input_user = TextInput(value=config['user'], title="User (Leave blank for OS authentication)", width=300)
input_password = PasswordInput(value=config['password'], title="Password (Leave blank for OS authentication)", width=300)
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
                          [div_import_note],
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
# Create the document Bokeh server will use to generate the webpage
if ACCESS_GRANTED:
    curdoc().add_root(settings_layout)
else:
    curdoc().add_root(layout_login)
curdoc().title = "DVH Analytics"

# Update statuses based on the loaded import_settings.txt
update_directory_status("Inbox", input_inbox)
update_directory_status("Imported", input_imported)
update_directory_status("Review", input_review)


if __name__ == '__main__':
    pass
