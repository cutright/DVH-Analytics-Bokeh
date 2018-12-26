#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
sql settings for settings view
Created on Tue Dec 25 2018
@author: Dan Cutright, PhD
"""

from __future__ import print_function
from tools.utilities import write_sql_connection_settings, validate_sql_connection, load_sql_settings
from tools.sql_connector import DVH_SQL
import time
from bokeh.models.widgets import Button, TextInput, Div, PasswordInput
from bokeh.layouts import row, column


class SqlConfig:
    def __init__(self):
        self.config = {}
        self.load(update_widgets=False)
        self.input_types = ['host', 'port', 'dbname', 'user', 'password']
        self.input_widget = {key: TextInput for key in self.input_types}
        self.input_widget['password'] = PasswordInput

        div_sql = Div(text="<b>SQL Settings</b>")

        title = {'host': 'Host',
                 'port': 'Port',
                 'dbname': 'Database Name',
                 'user': 'User (Leave blank for OS authentication)',
                 'password': 'Password (Leave blank for OS authentication)'}

        self.input = {key: self.input_widget[key](value=self.config[key], title=title[key], width=300) for key in
                      self.input_types}
        for key in self.input_types:
            self.input[key].on_change('value', self.save_needed)

        self.check_tables_button = Button(label='Check Tables', button_type='primary', width=100)
        self.check_tables_button.on_click(self.check_tables)

        self.create_tables_button = Button(label='Create Tables', button_type='primary', width=100)
        self.create_tables_button.on_click(self.create_tables)

        self.clear_tables_button = Button(label='Clear Tables', button_type='primary', width=100)
        self.clear_tables_button.on_click(self.clear_tables)

        self.reload_button = Button(label='Reload', button_type='primary', width=100)
        self.reload_button.on_click(self.load)

        self.save_button = Button(label='Save', button_type='default', width=100)
        self.save_button.on_click(self.save)

        self.echo_button = Button(label="Echo", button_type='primary', width=100)
        self.echo_button.on_click(self.echo)

        self.layout = column(div_sql,
                             row(self.input['host'], self.input['port']),
                             row(self.input['user'], self.input['password']),
                             self.input['dbname'],
                             row(self.reload_button, self.echo_button, self.save_button),
                             row(self.check_tables_button, self.create_tables_button, self.clear_tables_button))

    def load(self, update_widgets=True):
        self.config = load_sql_settings()

        if update_widgets:
            for key in self.input_types:
                self.input[key].value = self.config[key]

            self.save_button.button_type = 'default'
            self.save_button.label = 'Save'

    def save(self):
        self.update_config()
        write_sql_connection_settings(self.config)
        self.load()
        self.save_button.button_type = 'default'
        self.save_button.label = 'Save'

    def update_config(self):
        for key in self.input_types:
            self.config[key] = self.input[key].value

    def echo(self):
        self.update_config()
        initial_button_type = self.echo_button.button_type
        initial_label = self.echo_button.label
        if validate_sql_connection(config=self.config, verbose=False):
            self.echo_button.button_type = 'success'
            self.echo_button.label = 'Success'
        else:
            self.echo_button.button_type = 'warning'
            self.echo_button.label = 'Fail'

        time.sleep(1.5)
        self.echo_button.button_type = initial_button_type
        self.echo_button.label = initial_label

    def check_tables(self):

        initial_label = self.check_tables_button.label
        initial_button_type = self.check_tables_button.button_type

        try:
            table_result = {table: DVH_SQL().check_table_exists(table) for table in ['dvhs', 'plans', 'beams', 'rxs']}

            if all(table_result.values()):
                self.check_tables_button.button_type = 'success'
                self.check_tables_button.label = 'Success'
            else:
                self.check_tables_button.button_type = 'warning'
                self.check_tables_button.label = 'Fail'

        except:
            self.check_tables_button.button_type = 'warning'
            self.check_tables_button.label = 'No Connection'

        time.sleep(1.5)
        self.check_tables_button.button_type = initial_button_type
        self.check_tables_button.label = initial_label

    def create_tables(self):
        initial_label = self.create_tables_button.label
        initial_button_type = self.create_tables_button.button_type
        if initial_label == 'Cancel':
            self.create_tables_button.button_type = 'primary'
            self.create_tables_button.label = 'Create Tables'
            self.clear_tables_button.button_type = 'primary'
            self.clear_tables_button.label = 'Clear Tables'
        else:
            try:
                DVH_SQL().initialize_database()
            except:
                self.create_tables_button.button_type = 'warning'
                self.create_tables_button.label = 'No Connection'
                time.sleep(1.5)
                self.create_tables_button.button_type = initial_button_type
                self.create_tables_button.label = initial_label

    def clear_tables(self):

        if self.clear_tables_button.button_type == 'danger':
            try:
                DVH_SQL().reinitialize_database()
            except:
                self.clear_tables_button.button_type = 'warning'
                self.clear_tables_button.label = 'No Connection'
                time.sleep(1.5)
                self.clear_tables_button.button_type = 'primary'
                self.clear_tables_button.label = 'Clear Tables'
            self.create_tables_button.button_type = 'primary'
            self.create_tables_button.label = 'Create Tables'
            self.clear_tables_button.button_type = 'primary'
            self.clear_tables_button.label = 'Clear Tables'
        elif self.clear_tables_button.button_type == 'primary':
            self.clear_tables_button.button_type = 'danger'
            self.clear_tables_button.label = 'Are you sure?'
            self.create_tables_button.button_type = 'success'
            self.create_tables_button.label = 'Cancel'

    def save_needed(self, attr, old, new):
        self.save_button.label = 'Save Needed'
        self.save_button.button_type = 'warning'
