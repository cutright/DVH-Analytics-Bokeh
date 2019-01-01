#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
main program for Bokeh server (re-write for new query UI)
Created on Sun Apr 21 2017
@author: Dan Cutright, PhD
"""

from __future__ import print_function
import update_sys_path
from tools import auth
from bokeh.layouts import row
from bokeh.models import Spacer
from bokeh.io import curdoc
from bokeh.models.widgets import Button, Panel, Tabs, TextInput, PasswordInput
import time
from tools.io.preferences.options import load_options
from dvh_bokeh_models.main.sources import Sources
from dvh_bokeh_models.main.custom_titles import CustomTitles
from dvh_bokeh_models.main.mlc_analyzer import MLC_Analyzer
from dvh_bokeh_models.main.time_series import TimeSeries
from dvh_bokeh_models.main.correlation import Correlation
from dvh_bokeh_models.main.roi_viewer import ROI_Viewer
from dvh_bokeh_models.main.rad_bio import RadBio
from dvh_bokeh_models.main.regression import Regression
from dvh_bokeh_models.main.query import Query
from dvh_bokeh_models.main.dvhs import DVHs
from dvh_bokeh_models.main.data_tables import DataTables
from dvh_bokeh_models.main.categories import Categories
from dvh_bokeh_models.main.planning_data import PlanningData
from dvh_bokeh_models.main.source_listener import SourceListener


options = load_options()
custom_title = CustomTitles().custom_title


# This depends on a user defined function in dvh/auth.py.  By default, this returns True
# It is up to the user/installer to write their own function (e.g., using python-ldap)
# Proper execution of this requires placing Bokeh behind a reverse proxy with SSL setup (HTTPS)
# Please see Bokeh documentation for more information
ACCESS_GRANTED = not options.AUTH_USER_REQ


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Bokeh component classes
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ColumnDataSource objects
sources = Sources()

# Categories map of dropdown values, SQL column, and SQL table (and data source for range_categories)
categories = Categories(sources)

# Bokeh table objects
data_tables = DataTables(sources)

# Bokeh objects for each tab layout
planning_data = PlanningData(custom_title, data_tables)
roi_viewer = ROI_Viewer(sources, custom_title)
mlc_analyzer = MLC_Analyzer(sources, custom_title, data_tables)
time_series = TimeSeries(sources, categories.range, custom_title)
correlation = Correlation(sources, categories, custom_title)
regression = Regression(sources, time_series, correlation, categories.multi_var_reg_var_names, custom_title, data_tables)
correlation.add_regression_link(regression)
rad_bio = RadBio(sources, time_series, correlation, regression, custom_title, data_tables)
dvhs = DVHs(sources, time_series, correlation, regression, custom_title, data_tables)
query = Query(sources, categories, dvhs, rad_bio, roi_viewer, time_series, correlation, regression, mlc_analyzer,
              custom_title, data_tables)
dvhs.add_query_link(query)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Listen for changes to sources
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
source_listener = SourceListener(sources, query, dvhs, rad_bio, regression)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Layout
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

query_tab = Panel(child=query.layout, title='Query')
dvh_tab = Panel(child=dvhs.layout, title='DVHs')
rad_bio_tab = Panel(child=rad_bio.layout, title='Rad Bio')
optional_tabs = [('ROI Viewer', Panel(child=roi_viewer.layout, title='ROI Viewer')),
                 ('Planning Data', Panel(child=planning_data.layout, title='Planning Data')),
                 ('Time-Series', Panel(child=time_series.layout, title='Time-Series')),
                 ('Correlation', Panel(child=correlation.layout, title='Correlation')),
                 ('Regression', Panel(child=regression.layout, title='Regression')),
                 ('MLC Analyzer', Panel(child=mlc_analyzer.layout, title='MLC Analyzer'))]

if options.LITE_VIEW:
    rendered_tabs = [query_tab, dvh_tab]
else:
    rendered_tabs = [query_tab, dvh_tab, rad_bio_tab] + \
                    [tab for (title, tab) in optional_tabs if options.OPTIONAL_TABS[title]]

tabs = Tabs(tabs=rendered_tabs)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Custom authorization
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def auth_button_click():
    global ACCESS_GRANTED

    if not ACCESS_GRANTED:
        ACCESS_GRANTED = auth.check_credentials(auth_user.value, auth_pass.value, 'generic')
        if ACCESS_GRANTED:
            auth_button.label = 'Access Granted'
            auth_button.button_type = 'success'
            curdoc().clear()
            curdoc().add_root(tabs)
        else:
            auth_button.label = 'Failed'
            auth_button.button_type = 'danger'
            time.sleep(3)
            auth_button.label = 'Authenticate'
            auth_button.button_type = 'warning'


auth_user = TextInput(value='', title='User Name:', width=150)
auth_pass = PasswordInput(value='', title='Password:', width=150)
auth_button = Button(label="Authenticate", button_type="warning", width=100)
auth_button.on_click(auth_button_click)
layout_login = row(auth_user, Spacer(width=50), auth_pass, Spacer(width=50), auth_button)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Create the document Bokeh server will use to generate the web page
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
if ACCESS_GRANTED:
    curdoc().add_root(tabs)
else:
    curdoc().add_root(layout_login)

curdoc().title = "DVH Analytics"
