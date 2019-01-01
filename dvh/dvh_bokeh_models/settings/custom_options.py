#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
custom options for settings view
Created on Tue Dec 25 2018
@author: Dan Cutright, PhD
"""

from __future__ import print_function
import os
from tools.io.preferences.options import save_options, load_options
from bokeh.models.widgets import Button, TextInput, Div, RadioButtonGroup, CheckboxGroup, Select
from bokeh.layouts import row, column
import matplotlib.colors as plot_colors
from paths import PREF_DIR


class CustomOptions:
    def __init__(self):

        self.options = load_options()
        self.option_types = ['AUTH_USER_REQ', 'DISABLE_BACKUP_TAB', 'OPTIONAL_TABS', 'LITE_VIEW', 'COLORS', 'SIZE',
                             'LINE_WIDTH', 'LINE_DASH', 'ALPHA', 'ENDPOINT_COUNT', 'RESAMPLED_DVH_BIN_COUNT']
        div = {key: Div(text=key) for key in self.option_types}

        self.input = {}

        self.input['AUTH_USER_REQ'] = RadioButtonGroup(labels=["True", "False"], active=1-int(self.options.AUTH_USER_REQ))
        self.input['AUTH_USER_REQ'].on_change('active', self.update_auth_user_req)

        self.input['DISABLE_BACKUP_TAB'] = RadioButtonGroup(labels=["True", "False"], active=1-int(self.options.DISABLE_BACKUP_TAB))
        self.input['DISABLE_BACKUP_TAB'].on_change('active', self.update_disable_backup_tab)

        labels = ['ROI Viewer', 'Planning Data', 'Time-Series', 'Correlation', 'Regression', 'MLC Analyzer']
        active = [l for l in range(0, len(labels)) if self.options.OPTIONAL_TABS[labels[l]]]
        self.input['OPTIONAL_TABS'] = CheckboxGroup(labels=labels, active=active)
        self.input['OPTIONAL_TABS'].on_change('active', self.update_options_tabs)

        self.input['LITE_VIEW'] = RadioButtonGroup(labels=["True", "False"], active=1 - int(self.options.LITE_VIEW))
        self.input['LITE_VIEW'].on_change('active', self.update_lite_view)

        color_variables = [c for c in self.options.__dict__ if c.find('COLOR') > -1]
        color_variables.sort()
        colors = plot_colors.cnames.keys()
        colors.sort()
        self.input['COLORS_var'] = Select(value=color_variables[0], options=color_variables)
        self.input['COLORS_var'].on_change('value', self.update_input_colors_var)
        self.input['COLORS_val'] = Select(value=getattr(self.options, color_variables[0]), options=colors)
        self.input['COLORS_val'].on_change('value', self.update_input_colors_val)

        size_variables = [s for s in self.options.__dict__ if s.find('SIZE') > -1]
        size_variables.sort()
        self.input['SIZE_var'] = Select(value=size_variables[0], options=size_variables)
        self.input['SIZE_var'].on_change('value', self.update_size_var)
        self.input['SIZE_val'] = TextInput(value=str(getattr(self.options, size_variables[0])).replace('pt', ''))
        self.input['SIZE_val'].on_change('value', self.update_size_val)

        width_variables = [l for l in self.options.__dict__ if l.find('LINE_WIDTH') > -1]
        width_variables.sort()
        self.input['LINE_WIDTH_var'] = Select(value=width_variables[0], options=width_variables)
        self.input['LINE_WIDTH_var'].on_change('value', self.update_line_width_var)
        self.input['LINE_WIDTH_val'] = TextInput(value=str(getattr(self.options, width_variables[0])))
        self.input['LINE_WIDTH_val'].on_change('value', self.update_line_width_val)

        line_dash_variables = [d for d in self.options.__dict__ if d.find('LINE_DASH') > -1]
        line_dash_variables.sort()
        self.input['LINE_DASH_var'] = Select(value=line_dash_variables[0], options=line_dash_variables)
        self.input['LINE_DASH_var'].on_change('value', self.update_line_dash_var)
        line_dash_options = ['solid', 'dashed', 'dotted', 'dotdash', 'dashdot']
        self.input['LINE_DASH_val'] = Select(value=getattr(self.options, line_dash_variables[0]),
                                             options=line_dash_options)
        self.input['LINE_DASH_val'].on_change('value', self.update_line_dash_val)

        alpha_variables = [a for a in self.options.__dict__ if a.find('ALPHA') > -1]
        alpha_variables.sort()
        self.input['ALPHA_var'] = Select(value=alpha_variables[0], options=alpha_variables)
        self.input['ALPHA_var'].on_change('value', self.update_alpha_var)
        self.input['ALPHA_val'] = TextInput(value=str(getattr(self.options, alpha_variables[0])))
        self.input['ALPHA_val'].on_change('value', self.update_alpha_val)

        self.input['ENDPOINT_COUNT'] = TextInput(value=str(self.options.ENDPOINT_COUNT))
        self.input['ENDPOINT_COUNT'].on_change('value', self.update_endpoint_count)

        self.input['RESAMPLED_DVH_BIN_COUNT'] = TextInput(value=str(self.options.RESAMPLED_DVH_BIN_COUNT))
        self.input['RESAMPLED_DVH_BIN_COUNT'].on_change('value', self.update_resampled_dvh_bin_count)

        self.default_options_button = Button(label="Restore Default Options", button_type='warning')
        self.default_options_button.on_click(self.restore_default_options)

        self.layout = column(Div(text="<hr>", width=900),
                             Div(text="<b>Options</b>"),
                             row(div['AUTH_USER_REQ'], self.input['AUTH_USER_REQ']),
                             row(div['DISABLE_BACKUP_TAB'], self.input['DISABLE_BACKUP_TAB']),
                             row(div['OPTIONAL_TABS'], self.input['OPTIONAL_TABS']),
                             row(div['LITE_VIEW'], self.input['LITE_VIEW']),
                             row(div['COLORS'], self.input['COLORS_var'], self.input['COLORS_val']),
                             row(div['SIZE'], self.input['SIZE_var'], self.input['SIZE_val']),
                             row(div['LINE_WIDTH'], self.input['LINE_WIDTH_var'], self.input['LINE_WIDTH_val']),
                             row(div['LINE_DASH'], self.input['LINE_DASH_var'], self.input['LINE_DASH_val']),
                             row(div['ALPHA'], self.input['ALPHA_var'], self.input['ALPHA_val']),
                             row(div['ENDPOINT_COUNT'], self.input['ENDPOINT_COUNT']),
                             row(div['RESAMPLED_DVH_BIN_COUNT'], self.input['RESAMPLED_DVH_BIN_COUNT']),
                             row(self.default_options_button,
                                 Div(text="Must restart Settings server to take effect after click")))

    def save_options(self):
        save_options(self.options)

    def update_auth_user_req(self, attr, old, new):
        self.options.AUTH_USER_REQ = bool(1-new)
        self.save_options()

    def update_disable_backup_tab(self, attr, old, new):
        self.options.DISABLE_BACKUP_TAB = bool(1-new)
        self.save_options()

    def update_options_tabs(self, attr, old, new):
        for i in range(len(self.input['OPTIONAL_TABS'].labels)):
            key = self.input['OPTIONAL_TABS'].labels[i]
            if i in new:
                self.options.OPTIONAL_TABS[key] = True
            else:
                self.options.OPTIONAL_TABS[key] = False
        self.save_options()

    def update_lite_view(self, attr, old, new):
        self.options.LITE_VIEW = bool(1-new)
        self.save_options()

    def update_input_colors_var(self, attr, old, new):
        self.input['COLORS_val'].value = getattr(self.options, new)

    def update_input_colors_val(self, attr, old, new):
        setattr(self.options, self.input['COLORS_var'].value, new)
        self.save_options()

    def update_size_var(self, attr, old, new):
        try:
            self.input['SIZE_val'].value = getattr(self.options, new).replace('pt', '')
        except AttributeError:
            self.input['SIZE_val'].value = str(getattr(self.options, new))

    def update_size_val(self, attr, old, new):
        if 'FONT' in self.input['SIZE_var'].value:
            try:
                size = str(int(new)) + 'pt'
            except ValueError:
                size = '10pt'
        else:
            try:
                size = float(new)
            except ValueError:
                size = 1.

        setattr(self.options, self.input['SIZE_val'].value, size)
        self.save_options()

    def update_line_width_var(self, attr, old, new):
        self.input['LINE_WIDTH_val'].value = str(getattr(self.options, new))

    def update_line_width_val(self, attr, old, new):
        try:
            line_width = float(new)
        except ValueError:
            line_width = 1.
        setattr(self.options, self.input['LINE_WIDTH_var'].value, line_width)
        self.save_options()

    def update_line_dash_var(self, attr, old, new):
        self.input['LINE_DASH_val'].value = getattr(self.options, new)

    def update_line_dash_val(self, attr, old, new):
        setattr(self.options, self.input['LINE_DASH_var'].value, new)
        self.save_options()

    def update_alpha_var(self, attr, old, new):
        self.input['ALPHA_val'].value = str(getattr(self.options, new))

    def update_alpha_val(self, attr, old, new):
        try:
            alpha = float(new)
        except ValueError:
            alpha = 1.
        setattr(self.options, self.input['ALPHA_var'].value, alpha)
        self.save_options()

    def update_endpoint_count(self, attr, old, new):
        try:
            ep_count = int(new)
        except ValueError:
            ep_count = 10
        self.options.ENDPOINT_COUNT = ep_count
        self.save_options()

    def update_resampled_dvh_bin_count(self, attr, old, new):
        try:
            bin_count = int(new)
        except ValueError:
            bin_count = 10
        self.options.RESAMPLED_DVH_BIN_COUNT = bin_count
        self.save_options()

    def restore_default_options(self):
        abs_file_path = os.path.join(PREF_DIR, options)
        if os.path.isfile(abs_file_path):
            os.remove(abs_file_path)
            self.default_options_button.button_type = 'danger'
            self.default_options_button.label = 'Web server restart needed'
