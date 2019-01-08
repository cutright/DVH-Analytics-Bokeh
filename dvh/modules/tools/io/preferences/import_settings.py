#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
from future.utils import listitems
try:
    import pydicom as dicom  # for pydicom >= 1.0
except ImportError:
    import dicom
from ....paths import APPS_DIR, APP_DIR, PREF_DIR, DATA_DIR, INBOX_DIR, IMPORTED_DIR, REVIEW_DIR, BACKUP_DIR
from ...get_settings import get_settings, parse_settings_file


def is_import_settings_defined():
    abs_file_path = get_settings('import')
    if os.path.isfile(abs_file_path):
        return True
    else:
        return False


def write_import_settings(directories):

    import_text = ['inbox ' + directories['inbox'],
                   'imported ' + directories['imported'],
                   'review ' + directories['review']]
    import_text = '\n'.join(import_text)

    abs_file_path = get_settings('import')

    with open(abs_file_path, "w") as text_file:
        text_file.write(import_text)


def validate_import_settings():

    abs_file_path = get_settings('import')

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
    for key, value in listitems(config):
        if not os.path.isdir(value):
            print('invalid', key, 'path:', value, sep=' ')
            valid = False

    return valid


def load_directories():
    if is_import_settings_defined():
        return parse_settings_file(get_settings('import'))
    else:
        return {'inbox': INBOX_DIR,
                'imported': IMPORTED_DIR,
                'review': REVIEW_DIR}


def initialize_directories_settings():
    directories = [APPS_DIR, APP_DIR, PREF_DIR, DATA_DIR, INBOX_DIR, IMPORTED_DIR, REVIEW_DIR, BACKUP_DIR]
    for directory in directories:
        if not os.path.isdir(directory):
            os.mkdir(directory)
