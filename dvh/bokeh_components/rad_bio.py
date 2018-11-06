#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
All Rad Bio tab objects and functions for the main DVH Analytics bokeh program
Created on Sun Nov 4 2018
@author: Dan Cutright, PhD
"""
from bokeh.models.widgets import Button, TextInput, CheckboxButtonGroup, Div
from bokeh.models import Spacer
from bokeh.layouts import column, row
from bokeh_components.utilities import get_include_map
from analysis_tools import calc_eud
import options
from options import GROUP_LABELS


class RadBio:
    def __init__(self, sources, time_series, correlation, regression, custom_title, data_tables):
        self.sources = sources
        self.time_series = time_series
        self.correlation = correlation
        self.regression = regression

        self.eud_a_input = TextInput(value='', title='EUD a-value:', width=150)
        self.gamma_50_input = TextInput(value='', title=u"\u03b3_50:", width=150)
        self.td_tcd_input = TextInput(value='', title='TD_50 or TCD_50:', width=150)
        self.apply_button = Button(label="Apply parameters", button_type="primary", width=150)
        self.apply_filter = CheckboxButtonGroup(labels=["Group 1", "Group 2", "Selected"], active=[0], width=300)

        self.apply_button.on_click(self.apply_rad_bio_parameters)

        self.layout = column(Div(text="<b>DVH Analytics v%s</b>" % options.VERSION),
                             row(custom_title['1']['rad_bio'], Spacer(width=50), custom_title['2']['rad_bio']),
                             Div(text="<b>Published EUD Parameters from Emami"
                                      " et. al. for 1.8-2.0Gy fractions</b> (Click to apply)",
                                 width=600),
                             data_tables.emami,
                             Div(text="<b>Applied Parameters:</b>", width=150),
                             row(self.eud_a_input, Spacer(width=50),
                                 self.gamma_50_input, Spacer(width=50), self.td_tcd_input, Spacer(width=50),
                                 self.apply_filter, Spacer(width=50), self.apply_button),
                             Div(text="<b>EUD Calculations for Query</b>", width=500),
                             data_tables.rad_bio,
                             Spacer(width=1000, height=100))

    def initialize(self):
        include = get_include_map(self.sources)

        # Get data from DVH Table
        vars = ['mrn', 'uid', 'group', 'roi_name', 'ptv_overlap', 'roi_type', 'rx_dose']
        data = {v: [j for i, j in enumerate(self.sources.dvhs.data[v]) if include[i]] for v in vars}

        # Get data from beam table
        data['fxs'], data['fx_dose'] = [], []
        for eud_uid in data['uid']:
            plan_index = self.sources.plans.data['uid'].index(eud_uid)
            data['fxs'].append(self.sources.plans.data['fxs'][plan_index])

            rx_uids, rx_fxs = self.sources.rxs.data['uid'], self.sources.rxs.data['fxs']
            rx_indices = [i for i, rx_uid in enumerate(rx_uids) if rx_uid == eud_uid]
            max_rx_fxs = max([self.sources.rxs.data['fxs'][i] for i in rx_indices])
            rx_index = [i for i, rx_uid in enumerate(rx_uids) if rx_uid == eud_uid and rx_fxs[i] == max_rx_fxs][0]
            data['fx_dose'].append(self.sources.rxs.data['fx_dose'][rx_index])

        for v in ['eud_a', 'gamma_50', 'td_tcd', 'eud', 'ntcp_tcp']:
            data[v] = [0] * len(data['uid'])

        self.sources.rad_bio.data = data

    def apply_rad_bio_parameters(self):
        row_count = len(self.sources.rad_bio.data['uid'])
        data = {}

        group_data = self.sources.rad_bio.data['group']
        if self.apply_filter.active == [0, 1]:
            include = [i for i in range(row_count)]
        elif 0 in self.apply_filter.active:
            include = [i for i in range(row_count) if group_data[i] in {'Group 1', 'Group 1 & 2'}]
        elif 1 in self.apply_filter.active:
            include = [i for i in range(row_count) if group_data[i] in {'Group 2', 'Group 1 & 2'}]
        else:
            include = []

        if 2 in self.apply_filter.active:
            include.extend([i for i in range(row_count) if i in self.sources.rad_bio.selected.indices])

        try:
            data['eud_a'] = float(self.eud_a_input.value)
        except:
            data['eud_a'] = 1.
        try:
            data['gamma_50'] = float(self.gamma_50_input.value)
        except:
            data['gamma_50'] = 1.
        try:
            data['td_tcd'] = float(self.td_tcd_input.value)
        except:
            data['td_tcd'] = 1.

        patch = {v: [(i, data[v]) for i in range(row_count) if i in include] for v in list(data)}

        self.sources.rad_bio.patch(patch)

        self.update_eud()

    def update_eud(self):
        uids = self.sources.dvhs.data['uid']
        roi_names = self.sources.dvhs.data['roi_name']
        uid_roi_list = ["%s_%s" % (uid, roi_names[i]) for i, uid in enumerate(uids)]

        eud, ntcp_tcp = [], []
        for i, uid in enumerate(self.sources.rad_bio.data['uid']):
            uid_roi = "%s_%s" % (uid, self.sources.rad_bio.data['roi_name'][i])
            source_index = uid_roi_list.index(uid_roi)
            dvh = self.sources.dvhs.data['y'][source_index]
            a = self.sources.rad_bio.data['eud_a'][i]
            try:
                eud.append(round(calc_eud(dvh, a), 2))
            except:
                eud.append(0)
            td_tcd = self.sources.rad_bio.data['td_tcd'][i]
            gamma_50 = self.sources.rad_bio.data['gamma_50'][i]
            if eud[-1] > 0:
                ntcp_tcp.append(1 / (1 + (td_tcd / eud[-1]) ** (4. * gamma_50)))
            else:
                ntcp_tcp.append(0)

        self.sources.rad_bio.patch({'eud': [(i, j) for i, j in enumerate(eud)],
                                    'ntcp_tcp': [(i, j) for i, j in enumerate(ntcp_tcp)]})

        self.correlation.update_eud_in_correlation()
        categories = list(self.correlation.data[GROUP_LABELS[0]])
        categories.sort()
        self.regression.x.options = [''] + categories
        self.regression.y.options = [''] + categories
        self.regression.update_data()
        if self.time_series.y_axis.value in {'EUD', 'NTCP/TCP'}:
            self.time_series.update_plot()

    def emami_selection(self, attr, old, new):
        if new:
            row_index = min(new)
            self.eud_a_input.value = str(self.sources.emami.data['eud_a'][row_index])
            self.gamma_50_input.value = str(self.sources.emami.data['gamma_50'][row_index])
            self.td_tcd_input.value = str(self.sources.emami.data['td_tcd'][row_index])
