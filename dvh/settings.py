#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:43:28 2017

@author: nightowl
"""

import os
from roi_name_manager import DatabaseROIs, clean_name
from sql_to_python import QuerySQL
from sql_connector import DVH_SQL
from bokeh.layouts import layout, column, row
from bokeh.models import ColumnDataSource, Legend, CustomJS, HoverTool
from bokeh.models.widgets import Select, Button, PreText, TableColumn, DataTable, \
    NumberFormatter, RadioButtonGroup, TextInput, RadioGroup, Div
from bokeh.plotting import figure
from bokeh.io import curdoc
import re


db = DatabaseROIs()


###############################
# Institutional roi functions
###############################
def delete_institutional_roi():
    db.delete_institutional_roi(select_institutional_roi.value)
    select_institutional_roi.options = db.get_institutional_rois()
    select_institutional_roi.value = db.get_institutional_rois()[0]


def add_institutional_roi():
    new = clean_name(re.sub(r'\W+', '', input_institutional_roi.value))
    if len(new) > 50:
        new = new[0:50]
    if new and new not in db.get_institutional_rois():
        print new
        db.add_institutional_roi(new)
        update_institutional_roi_select()
        select_institutional_roi.value = new
        input_institutional_roi.value = ''
    elif new in db.get_institutional_rois():
        input_institutional_roi.value = ''


def update_institutional_roi_select():
    select_institutional_roi.options = db.get_institutional_rois()


##############################################
# Physician ROI functions
##############################################
def update_physician_roi(attr, old, new):
    select_physician_roi.options = db.get_physician_rois(new)
    physician_roi = db.get_physician_roi(new, select_institutional_roi.value)
    select_physician_roi.value = db.get_physician_rois(new)[0]


def add_physician_roi():
    new = clean_name(re.sub(r'\W+', '', input_physician.value)).upper()
    if len(new) > 50:
        new = new[0:50]
    if new and new not in db.get_physicians():
        db.add_physician(new)
        update_physician_select()
        select_physician.value = new
        input_physician.value = ''
    elif new in db.get_physicians():
        input_physician.value = ''


def delete_physician_roi():
    if select_physician.value != 'DEFAULT':
        db.delete_physician(select_physician.value)
        select_physician.options = db.get_physicians()
        select_physician.value = db.get_physicians()[0]


##############################
# Physician functions
##############################
def update_physician_select():
    select_physician.options = db.get_physicians()


def add_physician():
    new = clean_name(re.sub(r'\W+', '', input_physician.value)).upper()
    if len(new) > 50:
        new = new[0:50]
    if new and new not in db.get_physicians():
        db.add_physician(new)
        update_physician_select()
        select_physician.value = new
        input_physician.value = ''
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
def update_variation(attr, old, new):
    select_variation.options = db.get_variations(select_physician.value,
                                                 select_physician_roi.value)


def add_variation():
    new = clean_name(re.sub(r'\W+', '', input_variation.value))
    if len(new) > 50:
        new = new[0:50]
    if new and new not in db.get_variations(select_physician.value,
                                            select_physician_roi.value):
        db.add_variation(select_physician.value,
                         select_physician_roi.value,
                         new)
        select_variation.value = new
        input_variation.value = ''
    elif new in db.get_variations(select_physician.value,
                                  select_physician_roi.value):
        input_variation.value = ''


def delete_variation():
    if select_physician.value != 'DEFAULT':
        db.delete_physician(select_physician.value)
        select_physician.options = db.get_physicians()
        select_physician.value = db.get_physicians()[0]


################
# Misc functions
################
def reload_db():
    global db
    db = DatabaseROIs()

    select_physician.options = db.get_physicians()
    select_institutional_roi.options = db.get_institutional_rois()


######################################################
# Layout objects
######################################################
div_default_roi = Div(text="<b>Institutional ROI</b>")
div_physician = Div(text="<b>Physician</b>")
div_physician_roi = Div(text="<b>Physician ROI</b>")
div_variation = Div(text="<b>Physician ROI Variation</b>")
div_horizontal_bar = Div(text="<hr>")
div_horizontal_bar2 = Div(text="<hr>")
div_horizontal_bar3 = Div(text="<hr>")

# Institutional ROI objects
select_institutional_roi = Select(value=db.get_institutional_rois()[0],
                                  options=db.get_institutional_rois(),
                                  width=225,
                                  title='Current Institutional ROIs')
delete_institutional_roi_button = Button(label="Delete", button_type="warning", width=100)
delete_institutional_roi_button.on_click(delete_institutional_roi)
input_institutional_roi = TextInput(value='', title="Add new ROI", width=225)
add_institutional_roi_button = Button(label="Add", button_type="success", width=100)
add_institutional_roi_button.on_click(add_institutional_roi)

# Physician objects
select_physician = Select(value=db.get_physicians()[0],
                          options=db.get_physicians(),
                          width=225,
                          title='Physician')
select_physician.on_change('value', update_physician_roi)
delete_physician_button = Button(label="Delete", button_type="warning", width=100)
delete_physician_button.on_click(delete_physician)
input_physician = TextInput(value='', title="Add new physician", width=225)
add_physician_button = Button(label="Add", button_type="success", width=100)
add_physician_button.on_click(add_physician)

# Physician ROI objects
select_physician_roi = Select(value=db.get_physician_rois(select_physician.value)[0],
                              options=db.get_physician_rois(select_physician.value),
                              width=225,
                              title='\nPhysician ROI')
select_physician_roi.on_change('value', update_variation)
delete_physician_roi_button = Button(label="Delete", button_type="warning", width=100)
input_physician_roi = TextInput(value='', title="Add new physician roi", width=225)
add_physician_roi_button = Button(label="Add", button_type="success", width=100)
add_physician_roi_button.on_click(add_physician_roi)

# Physician ROI Variation objects
select_variation = Select(value=db.get_variations(select_physician.value,
                                                  select_physician_roi.value)[0],
                          options=db.get_variations(select_physician.value,
                                                    select_physician_roi.value),
                          width=225,
                          title='\nPhysician ROI Variation')
delete_variation_button = Button(label="Delete", button_type="warning", width=100)
input_variation = TextInput(value='', title="Add new variation", width=225)
add_variation_button = Button(label="Add", button_type="success", width=100)
add_variation_button.on_click(add_physician_roi)

# Reload and Save objects
reload_button = Button(label='Reload', button_type='primary', width=100)
reload_button.on_click(reload_db)
save_button = Button(label='Save', button_type='success', width=100)

layout = column(row(div_default_roi),
                row(select_institutional_roi, delete_institutional_roi_button),
                row(input_institutional_roi, add_institutional_roi_button),
                row(div_horizontal_bar),
                row(div_physician),
                row(select_physician, delete_physician_button),
                row(input_physician, add_physician_button),
                row(div_horizontal_bar2),
                row(div_physician_roi),
                row(select_physician_roi, delete_physician_roi_button),
                row(input_physician_roi, add_physician_roi_button),
                row(div_horizontal_bar3),
                row(div_variation),
                row(select_variation, delete_variation_button),
                row(input_variation, add_variation_button),
                row(reload_button, save_button))

# Create the document Bokeh server will use to generate the webpage
curdoc().add_root(layout)
curdoc().title = "ROI Name Manager"


if __name__ == '__main__':
    pass
