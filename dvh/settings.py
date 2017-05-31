#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:43:28 2017

@author: nightowl
"""

from utilities import is_import_settings_defined, is_sql_connection_defined,\
    write_import_settings, write_sql_connection_settings, validate_sql_connection
import os
import time
from roi_name_manager import DatabaseROIs, clean_name
from sql_to_python import QuerySQL
from sql_connector import DVH_SQL
from bokeh.models.widgets import Select, Button, Tabs, Panel, TextInput, RadioGroup, Div
from bokeh.layouts import layout, column, row
from bokeh.plotting import figure
from bokeh.io import curdoc
import re


##################################
# Import settings and SQL settings
##################################

directories = {}
config = {}


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
        echo_button.button_type = 'danger'
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
    select_institutional_roi.options = db.get_institutional_rois()
    select_institutional_roi.value = db.get_institutional_rois()[0]
    update_linked_institutional_roi()


def add_institutional_roi():
    new = clean_name(re.sub(r'\W+', '', input_institutional_roi.value.replace(' ', '_')))
    if len(new) > 50:
        new = new[0:50]
    if new and new not in db.get_institutional_rois():
        db.add_institutional_roi(new)
        update_institutional_roi_select()
        select_institutional_roi.value = new
        input_institutional_roi.value = ''
    elif new in db.get_institutional_rois():
        input_institutional_roi.value = ''


def update_institutional_roi_select():
    select_institutional_roi.options = db.get_institutional_rois()


def update_linked_institutional_roi():
    roi = db.get_institutional_roi(select_physician.value, select_physician_roi.value)
    if not roi:
        roi = 'uncategorized'
    div_linked_institutional_roi.text = "Linked to Institutional ROI: <i>" + roi + "</i>"


##############################################
# Physician ROI functions
##############################################
def update_physician_roi(attr, old, new):
    select_physician_roi.options = db.get_physician_rois(new)
    try:
        select_physician_roi.value = select_physician_roi.options[0]
    except KeyError:
        pass
    update_select_linked_physician_roi()


def update_select_linked_physician_roi():
    options = db.get_unused_institutional_rois(select_physician.value)
    select_linked_institutional_roi.options = options
    try:
        select_linked_institutional_roi.options = options[0]
    except ValueError:
        pass


def add_physician_roi():
    new = clean_name(re.sub(r'\W+', '', input_physician_roi.value.replace(' ', '_'))).lower()
    if len(new) > 50:
        new = new[0:50]
    if new and new not in db.get_physicians():
        db.add_physician_roi(select_physician.value, select_linked_institutional_roi.value, new)
        select_physician_roi.options = db.get_physician_rois(select_physician.value)
        select_physician_roi.value = new
        input_physician_roi.value = ''
        update_linked_institutional_roi()
        select_linked_institutional_roi.value = ''
    elif new in db.get_physicians():
        input_physician_roi.value = ''


def delete_physician_roi():
    if select_physician.value not in {'DEFAULT', ''}:
        db.delete_physician_roi(select_physician.value, select_physician_roi.value)
        select_physician_roi.options = db.get_physician_rois(select_physician.value)
        select_physician_roi.value = db.get_physician_rois(select_physician.value)[0]


def select_physician_roi_change(attr, old, new):
    update_variation()
    update_linked_institutional_roi()


##############################
# Physician functions
##############################
def update_physician_select():
    options = db.get_physicians()
    options.sort()
    select_physician.options = options
    select_physician.value = options[0]


def add_physician():
    new = str(clean_name(re.sub(r'\W+', '', input_physician.value.replace(' ', '_'))).upper())
    if len(new) > 50:
        new = new[0:50]
    if new and new not in db.get_physicians():
        input_physician.value = ''
        db.add_physician(new)
        select_physician.options = db.get_physicians()
        try:
            select_physician.value = new
        except KeyError:
            pass
    elif new in db.get_physicians():
        input_physician.value = ''


def delete_physician():
    if select_physician.value != 'DEFAULT':
        db.delete_physician(select_physician.value)
        select_physician.options = db.get_physicians()
        select_physician.value = db.get_physicians()[0]


###################################
# Physician ROI Variation functions
###################################
def update_physician_roi_select():
    select_physician_roi.options = db.get_physician_rois(select_physician.value)
    select_physician_roi.value = db.get_physician_rois(select_physician.value)[0]


def update_variation():
    select_variation.options = db.get_variations(select_physician.value,
                                                 select_physician_roi.value)


def add_variation():
    new = clean_name(re.sub(r'\W+', '', input_variation.value.replace(' ', '_'))).lower()
    if len(new) > 50:
        new = new[0:50]
    if new and new not in db.get_all_variations_of_physician(select_physician.value):
        db.add_variation(select_physician.value,
                         select_physician_roi.value,
                         new)
        select_variation.value = new
        input_variation.value = ''
        update_variation()
        select_variation.value = new
    elif new in db.get_variations(select_physician.value,
                                  select_physician_roi.value):
        input_variation.value = ''


def delete_variation():
    if select_variation.value != select_physician_roi.value:
        db.delete_variation(select_physician.value, select_physician_roi.value, select_variation.value)
        select_variation.options = db.get_variations(select_physician.value, select_physician_roi.value)
        select_variation.value = db.get_variations(select_physician.value, select_physician_roi.value)[0]


################
# Misc functions
################
def reload_db():
    global db
    db = DatabaseROIs()

    update_physician_select()
    update_physician_roi_select()
    update_institutional_roi_select()
    select_institutional_roi.value = db.get_institutional_rois()[0]
    select_linked_institutional_roi.value = ''
    update_variation()
    update_linked_institutional_roi()


######################################################
# Layout objects
###########################################

empty_plot = figure()
empty_tab = Panel(child=empty_plot, title='Empty')

# !!!!!!!!!!!!!!!!!!!!!!!
# ROI Name Manger objects
# !!!!!!!!!!!!!!!!!!!!!!!
div_default_roi = Div(text="<b>Institutional ROI</b>")
div_physician = Div(text="<b>Physician</b>")
div_physician_roi = Div(text="<b>Physician ROI</b>")
div_variation = Div(text="<b>Physician ROI Variation</b>")
div_horizontal_bar = Div(text="<hr>", width=1000)
div_horizontal_bar2 = Div(text="<hr>", width=1000)
div_horizontal_bar3 = Div(text="<hr>", width=1000)
div_horizontal_bar4 = Div(text="<hr>", width=1000)

# Institutional ROI objects
select_institutional_roi = Select(value=db.get_institutional_rois()[0],
                                  options=db.get_institutional_rois(),
                                  width=300,
                                  title='Current Institutional ROIs')
delete_institutional_roi_button = Button(label="Delete", button_type="warning", width=100)
delete_institutional_roi_button.on_click(delete_institutional_roi)
input_institutional_roi = TextInput(value='', title="Add new Institutional ROI", width=300)
add_institutional_roi_button = Button(label="Add", button_type="success", width=100)
add_institutional_roi_button.on_click(add_institutional_roi)

# Reload and Save objects
reload_button_institutional = Button(label='Reload', button_type='primary', width=100)
reload_button_institutional.on_click(reload_db)
save_button_institutional = Button(label='Save', button_type='success', width=100)

institutional_roi_layout = layout([[div_default_roi],
                                   [select_institutional_roi, delete_institutional_roi_button],
                                   [input_institutional_roi, add_institutional_roi_button],
                                   [reload_button_institutional, save_button_institutional]])

# Physician objects
select_physician = Select(value=db.get_physicians()[0],
                          options=db.get_physicians(),
                          width=300,
                          title='Physician')
select_physician.on_change('value', update_physician_roi)
delete_physician_button = Button(label="Delete", button_type="warning", width=100)
delete_physician_button.on_click(delete_physician)
input_physician = TextInput(value='', title="Add new physician", width=300)
add_physician_button = Button(label="Add", button_type="success", width=100)
add_physician_button.on_click(add_physician)

# Physician ROI objects
select_physician_roi = Select(value=db.get_physician_rois(select_physician.value)[0],
                              options=db.get_physician_rois(select_physician.value),
                              width=300,
                              title='Physician ROI')
select_physician_roi.on_change('value', select_physician_roi_change)
select_linked_institutional_roi = Select(value=db.get_unused_institutional_rois(select_physician.value)[0],
                                         options=db.get_unused_institutional_rois(select_physician.value),
                                         width=300,
                                         title='Linked Institutional ROI')
div_linked_institutional_roi = Div(text="", width=500)
update_linked_institutional_roi()
delete_physician_roi_button = Button(label="Delete", button_type="warning", width=100)
delete_physician_roi_button.on_click(delete_physician_roi)
input_physician_roi = TextInput(value='', title="Add new physician ROI", width=300)
add_physician_roi_button = Button(label="Add", button_type="success", width=100)
add_physician_roi_button.on_click(add_physician_roi)

reload_button_physician = Button(label='Reload', button_type='primary', width=100)
reload_button_physician.on_click(reload_db)
save_button_physician = Button(label='Save', button_type='success', width=100)

# Physician ROI Variation objects
select_variation = Select(value=db.get_variations(select_physician.value,
                                                  select_physician_roi.value)[0],
                          options=db.get_variations(select_physician.value,
                                                    select_physician_roi.value),
                          width=300,
                          title='Physician ROI Variation')
delete_variation_button = Button(label="Delete", button_type="warning", width=100)
delete_variation_button.on_click(delete_variation)
input_variation = TextInput(value='', title="Add new variation", width=300)
add_variation_button = Button(label="Add", button_type="success", width=100)
add_variation_button.on_click(add_variation)

physician_layout = layout([[div_physician],
                           [select_physician, delete_physician_button],
                           [input_physician, add_physician_button],
                           [div_horizontal_bar],
                           [div_physician_roi],
                           [select_physician_roi, delete_physician_roi_button],
                           [div_linked_institutional_roi],
                           [div_horizontal_bar2],
                           [input_physician_roi],
                           [select_linked_institutional_roi, add_physician_roi_button],
                           [div_horizontal_bar3],
                           [div_variation],
                           [select_variation, delete_variation_button],
                           [input_variation, add_variation_button],
                           [reload_button_physician, save_button_physician]])

# !!!!!!!!!!!!!!!!!!!!!!!
# Import and SQL objects
# !!!!!!!!!!!!!!!!!!!!!!!
div_import = Div(text="<b>DICOM Directories</b>")
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
                          [div_horizontal_bar4],
                          [div_sql],
                          [input_host, input_port],
                          [input_user, input_password],
                          [input_dbname],
                          [reload_sql_settings_button, echo_button, save_sql_settings_button]])

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Tabs and document
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
settings_tab = Panel(child=settings_layout, title='Directories & SQL Settings')
institutional_tab = Panel(child=institutional_roi_layout, title='Institutional ROIs')
physician_tab = Panel(child=physician_layout, title='Physician ROIs')

tabs = Tabs(tabs=[settings_tab, institutional_tab, physician_tab, empty_tab])

# Create the document Bokeh server will use to generate the webpage
curdoc().add_root(tabs)
curdoc().title = "DVH Analytics Settings"


if __name__ == '__main__':
    pass
