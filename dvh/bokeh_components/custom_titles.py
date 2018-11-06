#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
custom group title widgets for DVH Analytics
Created on Tue Oct 30 2018
@author: Dan Cutright, PhD
"""

from options import GROUP_1_COLOR, GROUP_2_COLOR, GROUP_LABELS
from bokeh.models.widgets import TextInput

TITLE_TYPES = ['query', 'dvhs', 'rad_bio', 'roi_viewer', 'planning', 'time_series',
               'correlation', 'regression', 'mlc_analyzer']

group_1_title = 'Group 1 (%s) Custom Title:' % GROUP_1_COLOR.capitalize()
group_2_title = 'Group 2 (%s) Custom Title:' % GROUP_2_COLOR.capitalize()
title = {'1': group_1_title, '2': group_2_title}


def custom_title_1_ticker(attr, old, new):
    for t in TITLE_TYPES:
        custom_title['1'][t].value = new


def custom_title_2_ticker(attr, old, new):
    for t in TITLE_TYPES:
        custom_title['2'][t].value = new


custom_title = {n: {t: TextInput(value='', title=title[n], width=300) for t in TITLE_TYPES} for n in GROUP_LABELS}

for t in TITLE_TYPES:
    custom_title['1'][t].on_change('value', custom_title_1_ticker)
    custom_title['2'][t].on_change('value', custom_title_2_ticker)
