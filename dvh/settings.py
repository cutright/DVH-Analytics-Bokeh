#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
settings view
Created on Tue Dec 25 2018
@author: Dan Cutright, PhD
"""

from __future__ import print_function
import update_sys_path  # noqa
from dvh_bokeh_models.settings.dicom_directories import DicomDirectories
from dvh_bokeh_models.settings.custom_options import CustomOptions
from dvh_bokeh_models.settings.sql_config import SqlConfig
from tools import auth
from tools.utilities import initialize_directories_settings
from dvh import options
import time
from bokeh.models.widgets import Button, TextInput, Div, PasswordInput
from bokeh.models import Spacer
from bokeh.layouts import layout, row, column
from bokeh.io import curdoc


initialize_directories_settings()

dicom_directories = DicomDirectories()
sql_config = SqlConfig()
custom_options = CustomOptions()


# This depends on a user defined function in dvh/auth.py.  By default, this returns True
# It is up to the user/installer to write their own function (e.g., using python-ldap)
# Proper execution of this requires placing Bokeh behind a reverse proxy with SSL setup (HTTPS)
# Please see Bokeh documentation for more information
ACCESS_GRANTED = not options.AUTH_USER_REQ


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


settings_layout = layout(column(dicom_directories.layout,
                                sql_config.layout,
                                custom_options.layout))

# Create the document Bokeh server will use to generate the webpage
if ACCESS_GRANTED:
    curdoc().add_root(settings_layout)
else:
    curdoc().add_root(layout_login)
curdoc().title = "DVH Analytics"
