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
from roi_name_manager import DatabaseROIs, clean_name
from sql_connector import DVH_SQL
from bokeh.models.widgets import Select, Button, Tabs, Panel, TextInput, RadioButtonGroup, Div
from bokeh.layouts import layout
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, LabelSet, Range1d


##################################
# Import settings and SQL settings
##################################

directories = {}
config = {}
categories = ["Institutional ROI", "Physician", "Physician ROI", "Variation"]
operators = ["Add", "Delete", "Rename"]
save_needed = False

data = {'name': [],
        'x': [],
        'y': [],
        'x0': [],
        'y0': [],
        'x1': [],
        'y1': []}


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
    if validate_sql_connection(config):
        echo_button.button_type = 'success'
        echo_button.label = 'Success'
        time.sleep(1.5)
        echo_button.button_type = 'primary'
        echo_button.label = 'Echo'
    else:
        echo_button.button_type = 'warning'
        echo_button.label = 'Fail'
        time.sleep(1.5)
        echo_button.button_type = 'primary'
        echo_button.label = 'Echo'


# Load Settings
load_directories()
load_sql_settings()

# Load ROI map
db = DatabaseROIs()


###############################
# Institutional roi functions
###############################
def delete_institutional_roi():
    db.delete_institutional_roi(select_institutional_roi.value)
    new_options = db.get_institutional_rois()
    select_institutional_roi.options = new_options
    select_institutional_roi.value = new_options[0]


def add_institutional_roi():
    new = clean_name(input_text.value)
    if len(new) > 50:
        new = new[0:50]
    if new and new not in db.get_institutional_rois():
        db.add_institutional_roi(new)
        select_institutional_roi.options = db.get_institutional_rois()
        select_institutional_roi.value = new
        input_text.value = ''
        update_select_unlinked_institutional_roi()


def select_institutional_roi_change(attr, old, new):
    update_input_text()


def update_institutional_roi_select():
    new_options = db.get_institutional_rois()
    select_institutional_roi.options = new_options
    select_institutional_roi.value = new_options[0]


def rename_institutional_roi():
    new = clean_name(input_text.value)
    db.set_institutional_roi(new, select_institutional_roi.value)
    update_institutional_roi_select()
    select_institutional_roi.value = new


##############################################
# Physician ROI functions
##############################################
def update_physician_roi(attr, old, new):
    select_physician_roi.options = db.get_physician_rois(new)
    try:
        select_physician_roi.value = select_physician_roi.options[0]
    except KeyError:
        pass


def add_physician_roi():
    new = clean_name(input_text.value)
    if len(new) > 50:
        new = new[0:50]
    if new and new not in db.get_physicians():
        db.add_physician_roi(select_physician.value, 'uncategorized', new)
        select_physician_roi.options = db.get_physician_rois(select_physician.value)
        select_physician_roi.value = new
        input_text.value = ''
    elif new in db.get_physicians():
        input_text.value = ''


def delete_physician_roi():
    if select_physician.value not in {'DEFAULT', ''}:
        db.delete_physician_roi(select_physician.value, select_physician_roi.value)
        select_physician_roi.options = db.get_physician_rois(select_physician.value)
        select_physician_roi.value = db.get_physician_rois(select_physician.value)[0]


def select_physician_roi_change(attr, old, new):
    update_variation()
    update_input_text()
    update_column_source_data()
    update_select_unlinked_institutional_roi()


def rename_physician_roi():
    new = clean_name(input_text.value)
    db.set_physician_roi(new, select_physician.value, select_physician_roi.value)
    update_physician_roi_select()
    select_physician_roi.value = new


##############################
# Physician functions
##############################
def update_physician_select():
    options = db.get_physicians()
    options.sort()
    select_physician.options = options
    select_physician.value = options[0]
    update_input_text()
    update_column_source_data()


def add_physician():
    new = clean_name(input_text.value).upper()
    if len(new) > 50:
        new = new[0:50]
    if new and new not in db.get_physicians():
        input_text.value = ''
        db.add_physician(new)
        select_physician.options = db.get_physicians()
        try:
            select_physician.value = new
        except KeyError:
            pass
    elif new in db.get_physicians():
        input_text.value = ''


def delete_physician():
    if select_physician.value != 'DEFAULT':
        db.delete_physician(select_physician.value)
        new_options = db.get_physicians()
        select_physician.options = new_options
        select_physician.value = new_options[0]


def select_physician_change(attr, old, new):
    update_physician_roi_select()
    update_input_text()
    update_select_unlinked_institutional_roi()
    update_uncategorized_variation_select()
    update_ignored_variations_select()


def rename_physician():
    new = clean_name(input_text.value)
    db.set_physician(new, select_physician.value)
    update_physician_select()
    select_physician.value = new


###################################
# Physician ROI Variation functions
###################################
def update_physician_roi_select():
    new_options = db.get_physician_rois(select_physician.value)
    select_physician_roi.options = new_options
    select_physician_roi.value = new_options[0]
    update_input_text()
    update_column_source_data()


def update_variation():
    select_variation.options = db.get_variations(select_physician.value,
                                                 select_physician_roi.value)
    select_variation.value = select_variation.options[0]


def add_variation():
    new = clean_name(input_text.value)
    if len(new) > 50:
        new = new[0:50]
    if new and new not in db.get_all_variations_of_physician(select_physician.value):
        db.add_variation(select_physician.value,
                         select_physician_roi.value,
                         new)
        select_variation.value = new
        input_text.value = ''
        update_variation()
        select_variation.value = new
    elif new in db.get_variations(select_physician.value,
                                  select_physician_roi.value):
        input_text.value = ''


def delete_variation():
    if select_variation.value != select_physician_roi.value:
        db.delete_variation(select_physician.value, select_physician_roi.value, select_variation.value)
        new_options = db.get_variations(select_physician.value, select_physician_roi.value)
        select_variation.options = new_options
        select_variation.value = new_options[0]


def select_variation_change(attr, old, new):
    update_input_text()


def rename_physician_roi():
    new = clean_name(input_text.value)
    db.set_physician_roi(new, select_physician.value, select_physician_roi.value)
    update_physician_roi_select()
    select_physician_roi.value = new


################
# Misc functions
################
def rename_variation():
    new = clean_name(input_text.value)
    db.set_variation(new, select_physician.value, select_physician_roi.value, select_variation.value)
    update_variation()
    select_variation.value = new


def update_input_text_title():
    input_text.title = operators[operator.active] + " " + categories[category.active] + ":"
    update_action_text()


def update_input_text_value():
    category_map = {0: select_institutional_roi.value,
                    1: select_physician.value,
                    2: select_physician_roi.value,
                    3: select_variation.value}
    if operator.active != 0:
        input_text.value = category_map[category.active]
    elif operator.active == 0 and category.active == 3:
        input_text.value = select_uncategorized_variation.value
    else:
        input_text.value = ''
    update_action_text()


def operator_change(attr, old, new):
    update_input_text()
    update_action_text()


def category_change(attr, old, new):
    update_input_text()
    update_action_text()


def update_input_text():
    update_input_text_title()
    update_input_text_value()


def update_action_text():
    category_map = {0: select_institutional_roi.value,
                    1: select_physician.value,
                    2: select_physician_roi.value,
                    3: select_variation.value}

    current = {0: db.get_institutional_rois(),
               1: db.get_physicians(),
               2: db.get_physician_rois(select_physician.value),
               3: db.get_variations(select_physician.value, select_physician_roi.value)}

    in_value = category_map[category.active]

    input_text_value = clean_name(input_text.value)
    if category.active == 1:
        input_text_value = input_text_value.upper()

    if input_text_value == '' or \
            (select_physician.value == 'DEFAULT' and category.active != 0) or \
            (operator.active == 1 and input_text_value not in current[category.active]) or \
            (operator.active == 2 and input_text_value in current[category.active]) or \
            (operator.active != 0 and category.active == 3 and select_variation.value == select_physician_roi.value):
        text = "<b>No Action</b>"

    else:

        text = "<b>" + input_text.title[:-1] + " </b><i>"
        if operator.active == 0:
            text += input_text_value
        else:
            text += in_value
        text += "</i>"
        output = input_text_value

        if operator.active == 0:
            if category.active == 2:
                text += " linked to Institutional ROI <i>uncategorized</i>"
            if category.active == 3:
                text += " linked to Physician ROI <i>" + select_physician_roi.value + "</i>"

        elif operator.active == 2:
            text += " to <i>" + output + "</i>"

    div_action.text = text
    action_button.label = input_text.title[:-1]


def input_text_change(attr, old, new):
    update_action_text()


def reload_db():
    global db, category, operator

    db = DatabaseROIs()

    category.active = 0
    operator.active = 0

    input_text.value = ''

    new_options = db.get_institutional_rois()
    select_institutional_roi.options = new_options
    select_institutional_roi.value = new_options[0]

    new_options = db.get_physicians()
    if len(new_options) > 1:
        new_value = new_options[1]
    else:
        new_value = new_options[0]
    select_physician.options = new_options
    select_physician.value = new_value


def save_db():
    db.write_to_file()
    save_button_roi.button_type = 'success'
    save_button_roi.label = 'Map Saved'


def update_column_source_data():
    source.data = db.get_physician_roi_visual_coordinates(select_physician.value,
                                                          select_physician_roi.value)

function_map = {'Add Institutional ROI': add_institutional_roi,
                'Add Physician': add_physician,
                'Add Physician ROI': add_physician_roi,
                'Add Variation': add_variation,
                'Delete Institutional ROI': delete_institutional_roi,
                'Delete Physician': delete_physician,
                'Delete Physician ROI': delete_physician_roi,
                'Delete Variation': delete_variation,
                'Rename Institutional ROI': rename_institutional_roi,
                'Rename Physician': rename_physician,
                'Rename Physician ROI': rename_physician_roi,
                'Rename Variation': rename_variation}


def execute_button_click():
    function_map[input_text.title.strip(':')]()
    update_column_source_data()
    update_uncategorized_variation_select()
    update_save_button_status()


def unlinked_institutional_roi_change(attr, old, new):
    if select_physician.value != 'DEFAULT':
        db.set_linked_institutional_roi(new, select_physician.value, select_physician_roi.value)
        update_action_text()
        update_column_source_data()


def update_select_unlinked_institutional_roi():
    new_options = db.get_unused_institutional_rois(select_physician.value)
    new_value = db.get_institutional_roi(select_physician.value, select_physician_roi.value)
    if new_value not in new_options:
        new_options.append(new_value)
        new_options.sort()
    select_unlinked_institutional_roi.options = new_options
    select_unlinked_institutional_roi.value = new_value


def update_uncategorized_variation_change(attr, old, new):
    update_input_text()


def update_uncategorized_variation_select():
    global uncategorized_variations
    uncategorized_variations = get_uncategorized_variations(select_physician.value)
    new_options = uncategorized_variations.keys()
    new_options.sort()
    old_value_index = select_uncategorized_variation.options.index(select_uncategorized_variation.value)
    select_uncategorized_variation.options = new_options
    if old_value_index < len(new_options) - 1:
        select_uncategorized_variation.value = new_options[old_value_index]
    else:
        try:
            select_uncategorized_variation.value = new_options[old_value_index - 1]
        except IndexError:
            select_uncategorized_variation.value = new_options[0]
    update_input_text()


def update_ignored_variations_select():
    new_options = get_ignored_variations(select_physician.value).keys()
    new_options.sort()
    select_ignored_variation.options = new_options
    select_ignored_variation.value = new_options[0]


def get_uncategorized_variations(physician):
    global config
    if validate_sql_connection(config, verbose=False):
        physician = clean_name(physician).upper()
        condition = "physician_roi = 'uncategorized'"
        cursor_rtn = DVH_SQL().query('dvhs', 'roi_name, study_instance_uid', condition)
        new_uncategorized_variations = {}
        cnx = DVH_SQL()
        for row in cursor_rtn:
            variation = clean_name(str(row[0]))
            study_instance_uid = str(row[1])
            physician_db = cnx.query('plans', 'physician', "study_instance_uid = '" + study_instance_uid + "'")[0][0]
            if physician == physician_db and variation not in new_uncategorized_variations.keys():
                new_uncategorized_variations[variation] = {'roi_name': str(row[0]), 'study_instance_uid': str(row[1])}
        if new_uncategorized_variations:
            return new_uncategorized_variations
        else:
            return {' ': ''}
    else:
        return ['Could not connect to SQL']


def get_ignored_variations(physician):
    global config
    if validate_sql_connection(config, verbose=False):
        physician = clean_name(physician).upper()
        condition = "physician_roi = 'ignored'"
        cursor_rtn = DVH_SQL().query('dvhs', 'roi_name, study_instance_uid', condition)
        variations = db.get_all_variations_of_physician(physician)
        new_ignored_variations = {}
        for row in cursor_rtn:
            variation = clean_name(str(row[0]))
            study_instance_uid = str(row[1])
            if variation not in variations and variation not in new_ignored_variations.keys():
                new_ignored_variations[variation] = {'roi_name': str(row[0]),
                                                     'study_instance_uid': study_instance_uid}
        if new_ignored_variations:
            return new_ignored_variations
        else:
            return {' ': ''}
    else:
        return {'Could not connect to SQL': ''}


def delete_uncategorized_dvh():
    if delete_uncategorized_button_roi.button_type == 'warning':
        delete_uncategorized_button_roi.button_type = 'danger'
        delete_uncategorized_button_roi.label = 'Are you sure?'
        ignore_button_roi.button_type = 'success'
        ignore_button_roi.label = 'Cancel Delete DVH'
    else:
        roi_info = uncategorized_variations[select_uncategorized_variation.value]
        DVH_SQL().delete_dvh(roi_info['roi_name'], roi_info['study_instance_uid'])
        update_uncategorized_variation_select()
        delete_uncategorized_button_roi.button_type = 'warning'
        delete_uncategorized_button_roi.label = 'Delete DVH'


def delete_ignored_dvh():
    if delete_ignored_button_roi.button_type == 'warning':
        delete_ignored_button_roi.button_type = 'danger'
        delete_ignored_button_roi.label = 'Are you sure?'
        unignore_button_roi.button_type = 'success'
        unignore_button_roi.label = 'Cancel Delete DVH'
    else:
        roi_info = ignored_variations[select_ignored_variation.value]
        DVH_SQL().delete_dvh(roi_info['roi_name'], roi_info['study_instance_uid'])
        update_ignored_variations_select()
        delete_ignored_button_roi.button_type = 'warning'
        delete_ignored_button_roi.label = 'Delete DVH?'


def ignore_dvh():
    global config
    if ignore_button_roi.label == 'Cancel Delete DVH':
        ignore_button_roi.button_type = 'primary'
        ignore_button_roi.label = 'Ignore'
        delete_uncategorized_button_roi.button_type = 'warning'
        delete_uncategorized_button_roi.label = 'Delete DVH'
    else:
        cnx = DVH_SQL()
        if validate_sql_connection(config, verbose=False):
            condition = "physician_roi = 'uncategorized'"
            cursor_rtn = DVH_SQL().query('dvhs', 'roi_name, study_instance_uid', condition)
            for row in cursor_rtn:
                variation = str(row[0])
                study_instance_uid = str(row[1])
                if clean_name(variation) == select_uncategorized_variation.value:
                    cnx.update('dvhs', 'physician_roi', 'ignored', "roi_name = '" + variation +
                               "' and study_instance_uid = '" + study_instance_uid + "'")
        cnx.close()
        to_be_ignored = select_uncategorized_variation.value
        update_uncategorized_variation_select()
        update_ignored_variations_select()
        select_ignored_variation.value = to_be_ignored


def unignore_dvh():
    global config
    if ignore_button_roi.label == 'Cancel Delete DVH':
        unignore_button_roi.button_type = 'primary'
        unignore_button_roi.label = 'Ignore'
        delete_ignored_button_roi.button_type = 'warning'
        delete_ignored_button_roi.label = 'Delete DVH'
    else:
        cnx = DVH_SQL()
        if validate_sql_connection(config, verbose=False):
            condition = "physician_roi = 'ignored'"
            cursor_rtn = DVH_SQL().query('dvhs', 'roi_name, study_instance_uid', condition)
            for row in cursor_rtn:
                variation = str(row[0])
                study_instance_uid = str(row[1])
                if clean_name(variation) == select_ignored_variation.value:
                    cnx.update('dvhs', 'physician_roi', 'uncategorized', "roi_name = '" + variation +
                               "' and study_instance_uid = '" + study_instance_uid + "'")
        cnx.close()
        to_be_unignored = select_ignored_variation.value
        update_uncategorized_variation_select()
        update_ignored_variations_select()
        select_uncategorized_variation.value = to_be_unignored


def update_uncategorized_rois_in_db():
    cnx = DVH_SQL()

    cursor_rtn = cnx.query('dvhs', 'roi_name, study_instance_uid', "physician_roi = 'uncategorized'")
    progress = 0
    complete = len(cursor_rtn)
    initial_label = update_uncategorized_rois_button.label
    for row in cursor_rtn:
        progress += 1
        variation = str(row[0])
        study_instance_uid = str(row[1])
        physician = cnx.query('plans', 'physician', "study_instance_uid = '" + study_instance_uid + "'")[0][0]

        new_physician_roi = db.get_physician_roi(physician, variation)

        if new_physician_roi == 'uncategorized':
            if clean_name(variation) in db.get_institutional_rois():
                new_institutional_roi = clean_name(variation)
            else:
                new_institutional_roi = 'uncategorized'
        else:
            new_institutional_roi = db.get_institutional_roi(physician, new_physician_roi)

        condition_str = "roi_name = '" + variation + "' and study_instance_uid = '" + study_instance_uid + "'"
        cnx.update('dvhs', 'physician_roi', new_physician_roi, condition_str)
        cnx.update('dvhs', 'institutional_roi', new_institutional_roi, condition_str)

        percent = int(float(100) * (float(progress) / float(complete)))
        update_uncategorized_rois_button.label = "Remap progress: " + str(percent) + "%"

    update_uncategorized_rois_button.label = initial_label
    cnx.close()
    db.write_to_file()
    update_uncategorized_variation_select()
    update_ignored_variations_select()


def remap_all_rois_in_db():
    cnx = DVH_SQL()

    cursor_rtn = cnx.query('dvhs', 'roi_name, study_instance_uid')
    progress = 0
    complete = len(cursor_rtn)
    initial_label = remap_all_rois_button.label
    for row in cursor_rtn:
        progress += 1
        variation = str(row[0])
        study_instance_uid = str(row[1])
        physician = cnx.query('plans', 'physician', "study_instance_uid = '" + study_instance_uid + "'")[0][0]

        new_physician_roi = db.get_physician_roi(physician, variation)

        if new_physician_roi == 'uncategorized':
            if clean_name(variation) in db.get_institutional_rois():
                new_institutional_roi = clean_name(variation)
            else:
                new_institutional_roi = 'uncategorized'
        else:
            new_institutional_roi = db.get_institutional_roi(physician, new_physician_roi)

        condition_str = "roi_name = '" + variation + "' and study_instance_uid = '" + study_instance_uid + "'"
        cnx.update('dvhs', 'physician_roi', new_physician_roi, condition_str)
        cnx.update('dvhs', 'institutional_roi', new_institutional_roi, condition_str)

        percent = int(float(100) * (float(progress) / float(complete)))
        remap_all_rois_button.label = "Remap progress: " + str(percent) + "%"

    remap_all_rois_button.label = initial_label
    cnx.close()
    db.write_to_file()
    update_uncategorized_variation_select()
    update_ignored_variations_select()


def update_save_button_status():
    save_button_roi.button_type = 'primary'
    save_button_roi.label = 'Map Save Needed'


######################################################
# Layout objects
######################################################

# !!!!!!!!!!!!!!!!!!!!!!!
# ROI Name Manger objects
# !!!!!!!!!!!!!!!!!!!!!!!
div_warning = Div(text="<b>WARNING:</b> Buttons in red or orange cannot be easily undone.", width=600)

# Selectors
options = db.get_institutional_rois()
select_institutional_roi = Select(value=options[0],
                                  options=options,
                                  width=300,
                                  title='All Institutional ROIs')

options = db.get_physicians()
if len(options) > 1:
    value = options[1]
else:
    value = options[0]
select_physician = Select(value=value,
                          options=options,
                          width=300,
                          title='Physician')

options = db.get_physician_rois(select_physician.value)
select_physician_roi = Select(value=options[0],
                              options=options,
                              width=300,
                              title='Physician ROIs')

options = db.get_variations(select_physician.value, select_physician_roi.value)
select_variation = Select(value=options[0],
                          options=options,
                          width=300,
                          title='Variations')

options = db.get_unused_institutional_rois(select_physician.value)
value = db.get_institutional_roi(select_physician.value, select_physician_roi.value)
if value not in options:
    options.append(value)
    options.sort()
select_unlinked_institutional_roi = Select(value=value,
                                           options=options,
                                           width=300,
                                           title='Linked Institutional ROI')
uncategorized_variations = get_uncategorized_variations(select_physician.value)
options = uncategorized_variations.keys()
options.sort()
select_uncategorized_variation = Select(value=options[0],
                                        options=options,
                                        width=300,
                                        title='Uncategorized Variations')
ignored_variations = get_ignored_variations(select_physician.value)
options = ignored_variations.keys()
if not options:
    options = ['']
else:
    options.sort()
select_ignored_variation = Select(value=options[0],
                                  options=options,
                                  width=300,
                                  title='Ignored Variations')

div_horizontal_bar1 = Div(text="<hr>", width=900)
div_horizontal_bar2 = Div(text="<hr>", width=900)

div_action = Div(text="<b>No Action</b>", width=600)

input_text = TextInput(value='',
                       title='Add Institutional ROI:',
                       width=300)

# RadioButtonGroups
category = RadioButtonGroup(labels=categories,
                            active=0,
                            width=400)
operator = RadioButtonGroup(labels=operators,
                            active=0,
                            width=200)

# Ticker calls
select_institutional_roi.on_change('value', select_institutional_roi_change)
select_physician.on_change('value', select_physician_change)
select_physician_roi.on_change('value', select_physician_roi_change)
select_variation.on_change('value', select_variation_change)
category.on_change('active', category_change)
operator.on_change('active', operator_change)
input_text.on_change('value', input_text_change)
select_unlinked_institutional_roi.on_change('value', unlinked_institutional_roi_change)
select_uncategorized_variation.on_change('value', update_uncategorized_variation_change)

# Button objects
action_button = Button(label='Add Institutional ROI', button_type='primary', width=200)
reload_button_roi = Button(label='Reload Map', button_type='primary', width=300)
save_button_roi = Button(label='Save Map', button_type='success', width=300)
ignore_button_roi = Button(label='Ignore', button_type='primary', width=150)
delete_uncategorized_button_roi = Button(label='Delete DVH', button_type='warning', width=150)
unignore_button_roi = Button(label='UnIgnore', button_type='primary', width=150)
delete_ignored_button_roi = Button(label='Delete DVH', button_type='warning', width=150)
update_uncategorized_rois_button = Button(label='Update Uncategorized ROIs in DB', button_type='warning', width=300)
remap_all_rois_button = Button(label='Remap all ROIs in DB', button_type='warning', width=300)

# Button calls
action_button.on_click(execute_button_click)
reload_button_roi.on_click(reload_db)
save_button_roi.on_click(save_db)
delete_uncategorized_button_roi.on_click(delete_uncategorized_dvh)
ignore_button_roi.on_click(ignore_dvh)
delete_ignored_button_roi.on_click(delete_ignored_dvh)
unignore_button_roi.on_click(unignore_dvh)
update_uncategorized_rois_button.on_click(update_uncategorized_rois_in_db)
remap_all_rois_button.on_click(remap_all_rois_in_db)

# Plot
p = figure(plot_width=1000, plot_height=500,
           x_range=["Institutional ROI", "Physician ROI", "Variations"],
           x_axis_location="above",
           title="(Linked by Physician and Physician ROI dropdowns)",
           tools="pan, ywheel_zoom",
           logo=None)
p.toolbar.active_scroll = "auto"
p.title.align = 'center'
p.title.text_font_style = "italic"
p.xaxis.axis_line_color = None
p.xaxis.major_tick_line_color = None
p.xaxis.minor_tick_line_color = None
p.xaxis.major_label_text_font_size = "15pt"
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.yaxis.visible = False
p.outline_line_color = None
p.y_range = Range1d(-5, 5)

source = ColumnDataSource(data=data)
p.circle("x", "y", size=12, source=source, line_color="black", fill_alpha=0.8)
labels = LabelSet(x="x", y="y", text="name", y_offset=8,
                  text_font_size="15pt", text_color="#555555",
                  source=source, text_align='center')
p.add_layout(labels)
p.segment(x0='x0', y0='y0', x1='x1', y1='y1', source=source, alpha=0.5)
update_column_source_data()

roi_layout = layout([[select_institutional_roi],
                     [div_horizontal_bar1],
                     [select_physician],
                     [select_physician_roi, select_variation, select_unlinked_institutional_roi],
                     [select_uncategorized_variation, select_ignored_variation],
                     [ignore_button_roi, delete_uncategorized_button_roi, unignore_button_roi,
                      delete_ignored_button_roi],
                     [reload_button_roi, save_button_roi],
                     [update_uncategorized_rois_button, remap_all_rois_button],
                     [div_warning],
                     [div_horizontal_bar2],
                     [input_text, operator, category],
                     [div_action],
                     [action_button],
                     [p]])

# !!!!!!!!!!!!!!!!!!!!!!!
# Import and SQL objects
# !!!!!!!!!!!!!!!!!!!!!!!
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

# Reload and Save objects
reload_dir_button = Button(label='Reload', button_type='primary', width=100)
reload_dir_button.on_click(reload_directories)
save_dir_button = Button(label='Save', button_type='success', width=100)
save_dir_button.on_click(save_directories)
update_dir_save_status()

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
                          [reload_sql_settings_button, echo_button, save_sql_settings_button]])

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Tabs and document
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
settings_tab = Panel(child=settings_layout, title='Directories & SQL Settings')
roi_tab = Panel(child=roi_layout, title='ROI Name Manager')

tabs = Tabs(tabs=[settings_tab, roi_tab])

# Create the document Bokeh server will use to generate the webpage
curdoc().add_root(tabs)
curdoc().title = "DVH Analytics: Settings"


if __name__ == '__main__':
    pass
