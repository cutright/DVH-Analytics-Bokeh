#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
custom group title widgets for DVH Analytics
Created on Tue Oct 30 2018
@author: Dan Cutright, PhD
"""

from ..tools.io.preferences.options import load_options
from bokeh.models.widgets import TextInput


options = load_options()


class CustomTitles:
    def __init__(self):

        self.TITLE_TYPES = ['query', 'dvhs', 'rad_bio', 'roi_viewer', 'planning', 'time_series',
                            'correlation', 'regression', 'mlc_analyzer']

        self.group_1_title = 'Group 1 (%s) Custom Title:' % options.GROUP_1_COLOR.capitalize()
        self.group_2_title = 'Group 2 (%s) Custom Title:' % options.GROUP_2_COLOR.capitalize()
        self.title = {'1': self.group_1_title, '2': self.group_2_title}

        self.custom_title = {n: {t: TextInput(value='', title=self.title[n], width=300) for t in self.TITLE_TYPES}
                             for n in options.GROUP_LABELS}

        for t in self.TITLE_TYPES:
            self.custom_title['1'][t].on_change('value', self.custom_title_1_ticker)
            self.custom_title['2'][t].on_change('value', self.custom_title_2_ticker)

    def custom_title_1_ticker(self, attr, old, new):
        for t in self.TITLE_TYPES:
            self.custom_title['1'][t].value = new

    def custom_title_2_ticker(self, attr, old, new):
        for t in self.TITLE_TYPES:
            self.custom_title['2'][t].value = new
