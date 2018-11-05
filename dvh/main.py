#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
main program for Bokeh server (re-write for new query UI)
Created on Sun Apr 21 2017
@author: Dan Cutright, PhD
"""

from __future__ import print_function
from utilities import load_options
import auth
from bokeh.layouts import row
from bokeh.models import Spacer
from bokeh.io import curdoc
from bokeh.models.widgets import Button, Panel, Tabs, TextInput, PasswordInput
import time
import options
from bokeh_components import sources
from bokeh_components.custom_titles import custom_title
from bokeh_components.mlc_analyzer import MLC_Analyzer
from bokeh_components.time_series import TimeSeries
from bokeh_components.correlation import Correlation
from bokeh_components.roi_viewer import ROI_Viewer
from bokeh_components.rad_bio import RadBio
from bokeh_components.regression import Regression
from bokeh_components.query import Query
from bokeh_components.dvhs import DVHs
from bokeh_components.data_tables import DataTables
from bokeh_components.categories import Categories
from bokeh_components.planning_data import PlanningData

options = load_options(options)


# This depends on a user defined function in dvh/auth.py.  By default, this returns True
# It is up to the user/installer to write their own function (e.g., using python-ldap)
# Proper execution of this requires placing Bokeh behind a reverse proxy with SSL setup (HTTPS)
# Please see Bokeh documentation for more information
ACCESS_GRANTED = not options.AUTH_USER_REQ

# Categories map of dropdown values, SQL column, and SQL table (and data source for range_categories)
categories = Categories(sources)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Correlation and Regression variable names
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
correlation_variables, correlation_names = [], []
correlation_variables_beam = ['Beam Dose', 'Beam MU', 'Control Point Count', 'Gantry Range',
                              'SSD', 'Beam MU per control point']
for key in list(categories.range):
    if key.startswith('ROI') or key.startswith('PTV') or key in {'Total Plan MU', 'Rx Dose'}:
        correlation_variables.append(key)
        correlation_names.append(key)
    if key in correlation_variables_beam:
        correlation_variables.append(key)
        for stat in ['Min', 'Mean', 'Median', 'Max']:
            correlation_names.append("%s (%s)" % (key, stat))
correlation_variables.sort()
correlation_names.sort()
multi_var_reg_var_names = correlation_names + ['EUD', 'NTCP/TCP']

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Bokeh component classes
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
data_tables = DataTables(sources)

planning_data = PlanningData(custom_title, data_tables)
roi_viewer = ROI_Viewer(sources, custom_title)
mlc_analyzer = MLC_Analyzer(sources, custom_title, data_tables)
time_series = TimeSeries(sources, categories.range, custom_title, data_tables)
correlation = Correlation(sources, correlation_names, categories.range, custom_title)
regression = Regression(sources, time_series, correlation, multi_var_reg_var_names, custom_title, data_tables)
correlation.add_regression_link(regression)
rad_bio = RadBio(sources, time_series, correlation, regression, custom_title, data_tables)
dvhs = DVHs(sources, time_series, correlation, regression, custom_title, data_tables)
query = Query(sources, categories, correlation_variables,
              dvhs, rad_bio, roi_viewer, time_series, correlation, regression, mlc_analyzer, custom_title, data_tables)
dvhs.add_query_link(query)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Listen for changes to sources
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
class SourceSelection:
    def __init__(self, table):
        self.table = table

    def ticker(self, attr, old, new):
        if query.allow_source_update:
            src = getattr(sources, self.table)
            uids = list(set([src.data['uid'][i] for i in new]))
            self.update_planning_data_selections(uids)

    @staticmethod
    def update_planning_data_selections(uids):

        query.allow_source_update = False
        for k in ['rxs', 'plans', 'beams']:
            src = getattr(sources, k)
            src.selected.indices = [i for i, j in enumerate(src.data['uid']) if j in uids]

        query.allow_source_update = True


sources.selectors.selected.on_change('indices', query.update_selector_row_on_selection)
query.update_selector_source()

sources.ranges.selected.on_change('indices', query.update_range_row_on_selection)
sources.endpoint_defs.selected.on_change('indices', dvhs.update_ep_row_on_selection)

source_selection = {s: SourceSelection(s) for s in ['rxs', 'plans', 'beams']}
for s in ['rxs', 'plans', 'beams']:
    getattr(sources, s).selected.on_change('indices', source_selection[s].ticker)
sources.dvhs.selected.on_change('indices', dvhs.update_source_endpoint_view_selection)
sources.endpoint_view.selected.on_change('indices', dvhs.update_dvh_table_selection)
sources.emami.selected.on_change('indices', rad_bio.emami_selection)
sources.multi_var_include.selected.on_change('indices', regression.multi_var_include_selection)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Layout objects
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
