#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
dicom directories for settings view
Created on Tue Dec 25 2018
@author: Dan Cutright, PhD
"""

from __future__ import print_function
from os.path import isdir
from future.utils import listvalues
from bokeh.models.widgets import Button, TextInput, Div
from bokeh.layouts import row, column
import time
from ..tools.io.preferences.import_settings import is_import_settings_defined, write_import_settings
from ..tools.get_settings import get_settings, parse_settings_file
from ..paths import INBOX_DIR, IMPORTED_DIR, REVIEW_DIR


class DicomDirectories:
    def __init__(self):

        self.directories = {}
        self.directory_types = ['inbox', 'imported', 'review']
        self.load(update_widgets=False)

        self.input = {key: TextInput(value=self.directories[key], title=key, width=600) for key in self.directory_types}
        for key in self.directory_types:
            self.input[key].on_change('value', self.input_change)

        self.reload_button = Button(label='Reload', button_type='primary', width=100)
        self.reload_button.on_click(self.load)

        self.save_button = Button(label='Saved', button_type='success', width=100)
        self.save_button.on_click(self.save)

        self.update_all_directory_statuses()

        div_import = Div(text="<b>DICOM Directories</b>")
        div_import_note = Div(text="Please fill in existing directory locations below.")
        div_horizontal_bar_settings = Div(text="<hr>", width=900)
        self.layout = column(div_import,
                             div_import_note,
                             self.input['inbox'],
                             self.input['imported'],
                             self.input['review'],
                             row(self.reload_button, self.save_button),
                             div_horizontal_bar_settings)

    def update_directories(self):
        for key in self.directory_types:
            self.directories[key] = self.input[key].value

    def load(self, update_widgets=True):
        if is_import_settings_defined():
            self.directories = parse_settings_file(get_settings('import'))
        else:
            self.directories = {'inbox': INBOX_DIR,
                                'imported': IMPORTED_DIR,
                                'review': REVIEW_DIR}
            write_import_settings(self.directories)

        if update_widgets:
            for key in self.directory_types:
                self.input[key] = self.directories[key]

            self.save_button.label = 'Saved'
            self.save_button.button_type = 'default'

    def save(self):
        write_import_settings(self.directories)
        self.update_directories()
        self.load()

        # Save button animation
        self.save_button.button_type = 'success'
        self.save_button.label = 'Saved'
        time.sleep(2)
        self.save_button.button_type = 'default'

    def update_status(self, dir_key):

        directory = self.directories[dir_key]

        if isdir(directory):
            self.input[dir_key].title = dir_key
        elif not directory:
            self.input[dir_key].title = "%s --- Path Needed ---" % dir_key
        else:
            self.input[dir_key].title = "%s --- Invalid Path ---" % dir_key

        # if any paths are invalid, return False
        dir_save_status = all([isdir(path) for path in listvalues(self.directories)])
        self.save_button.button_type = {True: 'default', False: 'warning'}[dir_save_status]

    def update_all_directory_statuses(self):
        for key in self.directory_types:
            self.update_status(key)

    def input_change(self, attr, old, new):
        self.save_button.label = 'Save Needed'
        self.save_button.button_type = 'primary'
        self.update_directories()
        self.update_all_directory_statuses()
