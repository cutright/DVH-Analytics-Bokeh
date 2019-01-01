#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
backup model for admin view
Created on Tue Dec 25 2018
@author: Dan Cutright, PhD
"""

from __future__ import print_function
from os import remove, listdir, system, mkdir, rmdir
from os.path import isfile, isdir, join
from datetime import datetime
from tools.io.database.sql_connector import DVH_SQL
from bokeh.models.widgets import Select, Button, Div
from bokeh.layouts import row, column
from shutil import copyfile
from paths import BACKUP_DIR, PREF_DIR
from tools.io.preferences.sql import load_sql_settings


class Backup:
    def __init__(self):

        self.config = load_sql_settings()

        self.backup_select = Select(value='', options=[''], title="Available SQL Backups", width=450)
        self.delete_backup_button = Button(label='Delete', button_type='warning', width=100)
        self.restore_db_button = Button(label='Restore', button_type='primary', width=100)
        self.backup_db_button = Button(label='Backup', button_type='success', width=100)

        self.backup_pref_select = Select(value='', options=[''], title="Available Preferences Backups", width=450)
        self.delete_backup_button_pref = Button(label='Delete', button_type='warning', width=100)
        self.restore_pref_button = Button(label='Restore', button_type='primary', width=100)
        self.backup_pref_button = Button(label='Backup', button_type='success', width=100)

        warning_div = Div(text="<b>WARNING for Non-Docker Users:</b> Restore requires your OS user name to be both a"
                               " PostgreSQL super user and have ALL PRIVILEGES WITH GRANT OPTIONS. Do NOT attempt otherwise."
                               " It's possible you have multiple PostgreSQL servers installed, so be sure your backup"
                               " file isn't empty. Validate by typing 'psql' in a terminal/command prompt, then"
                               " <i>SELECT * FROM pg_settings WHERE name = 'port';</i> "
                               " The resulting port should match the port below"
                               " (i.e., make sure you're backing up the correct database).", width=650)
        host_div = Div(text="<b>Host</b>: %s" % self.config['host'])
        port_div = Div(text="<b>Port</b>: %s" % self.config['port'])
        db_div = Div(text="<b>Database</b>: %s" % self.config['dbname'])

        self.delete_backup_button.on_click(self.delete_backup)
        self.backup_db_button.on_click(self.backup_db)
        self.restore_db_button.on_click(self.restore_db)

        self.delete_backup_button_pref.on_click(self.delete_backup_pref)
        self.backup_pref_button.on_click(self.backup_pref)
        self.restore_pref_button.on_click(self.restore_preferences)

        self.update_backup_select()

        self.layout = column(row(self.backup_select, self.delete_backup_button, self.restore_db_button,
                                 self.backup_db_button),
                             row(self.backup_pref_select, self.delete_backup_button_pref, self.restore_pref_button,
                                 self.backup_pref_button),
                             warning_div,
                             host_div,
                             port_div,
                             db_div)

    def update_backup_select(self):

        # SQL Backups
        backups = [f for f in listdir(BACKUP_DIR) if isfile(join(BACKUP_DIR, f)) and '.sql' in f]
        if not backups:
            backups = ['']
        backups.sort(reverse=True)
        self.backup_select.options = backups
        self.backup_select.value = backups[0]

        # Preferences backups
        backups = [d for d in listdir(BACKUP_DIR) if isdir(join(BACKUP_DIR, d)) and d.startswith('preferences')]
        if not backups:
            backups = ['']
        backups.sort(reverse=True)
        self.backup_pref_select.options = backups
        self.backup_pref_select.value = backups[0]

    def delete_backup(self):
        abs_file = join(BACKUP_DIR, self.backup_select.value)
        if isfile(abs_file):
            remove(abs_file)

        self.update_backup_select()

    def backup_db(self):
        self.backup_db_button.button_type = 'warning'
        self.backup_db_button.label = 'Backing up...'

        time_id = str(datetime.now()).split('.')[0].replace(':', '-').replace(' ', '_')
        new_file = "%s_%s_%s_%s.sql" % (self.config['dbname'], self.config['host'], self.config['port'], time_id)
        abs_file_path = join(BACKUP_DIR, new_file)

        if isfile('/this_is_running_in_docker'):
            system("pg_dump -U %s -h %s %s > %s" % (self.config['user'], self.config['host'], self.config['dbname'],
                                                    abs_file_path))
        else:
            system("pg_dumpall >" + abs_file_path)

        self.backup_db_button.button_type = 'success'
        self.backup_db_button.label = 'Backup'

        self.update_backup_select()

    def restore_db(self):
        self.restore_db_button.label = 'Restoring...'
        self.restore_db_button.button_type = 'warning'

        DVH_SQL().drop_tables()

        abs_file_path = join(BACKUP_DIR, self.backup_select.value)

        back_up_command = "psql " + self.config['dbname'] + " < " + abs_file_path
        system(back_up_command)

        self.restore_db_button.label = 'Restore'
        self.restore_db_button.button_type = 'primary'

        self.update_backup_select()

    def backup_pref(self):
        self.backup_pref_button.button_type = 'warning'
        self.backup_pref_button.label = 'Backing up...'

        time_id = str(datetime.now()).split('.')[0].replace(':', '-').replace(' ', '_')
        backup_path_pref = join(BACKUP_DIR, "preferences_" + time_id)
        if not isdir(backup_path_pref):
            mkdir(backup_path_pref)

        files_to_backup = [f for f in listdir(PREF_DIR) if isfile(join(PREF_DIR, f))]
        for f in files_to_backup:
            copyfile(join(PREF_DIR, f), join(backup_path_pref, f))

        self.backup_pref_button.button_type = 'success'
        self.backup_pref_button.label = 'Backup'

        self.update_backup_select()

    def restore_preferences(self):
        self.restore_pref_button.label = 'Restoring...'
        self.restore_pref_button.button_type = 'warning'

        src_path = join(BACKUP_DIR, self.backup_pref_select.value)

        for f in listdir(PREF_DIR):
            remove(join(PREF_DIR, f))

        files_to_restore = [f for f in listdir(src_path) if isfile(join(src_path, f))]
        for f in files_to_restore:
            copyfile(join(src_path, f), join(PREF_DIR, f))

        self.update_backup_select()

        self.restore_pref_button.label = 'Restore'
        self.restore_pref_button.button_type = 'primary'

    def delete_backup_pref(self):

        src_path = join(BACKUP_DIR, self.backup_pref_select.value)

        for f in listdir(src_path):
            remove(join(src_path, f))
        rmdir(src_path)

        self.update_backup_select()
