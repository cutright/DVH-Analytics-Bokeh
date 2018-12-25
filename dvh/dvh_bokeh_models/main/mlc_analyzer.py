#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
All MLC Analyzer tab objects and functions for the main DVH Analytics bokeh program
Created on Sat Nov 3 2018
@author: Dan Cutright, PhD
"""

from __future__ import print_function
from tools import mlc_analyzer as mlca
from tools.sql_connector import DVH_SQL
from bokeh.models.widgets import Select, Button, Div, DataTable
from bokeh.plotting import figure
from bokeh.models import Range1d, Spacer
from bokeh.layouts import row, column
import os
from tools.get_settings import get_settings, parse_settings_file
import numpy as np
import options
import time
from dvh_bokeh_models.main.columns import mlc_viewer as mlc_viewer_columns


class MLC_Analyzer:
    def __init__(self, sources, custom_title, data_tables):
        self.sources = sources

        self.mlc_data = []

        mlc_analyzer_options = [''] + sources.dvhs.data['mrn']

        self.options = [''] + sources.dvhs.data['mrn']
        self.mrn_select = Select(value='', options=mlc_analyzer_options, width=200, title='MRN')
        self.study_date_select = Select(value='', options=[''], width=200, title='Sim Study Date')
        self.uid_select = Select(value='', options=[''], width=400, title='Study Instance UID')
        self.plan_select = Select(value='', options=[''], width=200, title='Plan')
        self.fx_grp_select = Select(value='', options=[''], width=200, title='Fx Group')
        self.beam_select = Select(value='', options=[''], width=200, title='Beam')
        self.cp_select = Select(value='', options=[''], width=50, title='CP')

        self.mrn_select.on_change('value', self.mrn_ticker)
        self.study_date_select.on_change('value', self.study_date_ticker)
        self.uid_select.on_change('value', self.uid_ticker)
        self.plan_select.on_change('value', self.plan_ticker)
        self.fx_grp_select.on_change('value', self.fx_grp_ticker)
        self.beam_select.on_change('value', self.beam_ticker)
        self.cp_select.on_change('value', self.cp_ticker)

        self.mlc_viewer = figure(plot_width=500, plot_height=500, logo=None, match_aspect=True,
                                 tools="crosshair,save")
        self.mlc_viewer.xaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.mlc_viewer.yaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.mlc_viewer.xaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.mlc_viewer.yaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.mlc_viewer.min_border_left = options.MIN_BORDER
        self.mlc_viewer.min_border_bottom = options.MIN_BORDER
        self.mlc_viewer.xaxis.axis_label = "X-Axis (mm)"
        self.mlc_viewer.yaxis.axis_label = "Y-Axis (mm)"
        self.mlc_viewer.quad(top='top', bottom='bottom', left='left', right='right',
                             source=self.sources.mlc_viewer, alpha=0.25, color='color')
        self.mlc_viewer_previous_cp = Button(label="<", button_type="primary", width=50)
        self.mlc_viewer_next_cp = Button(label=">", button_type="primary", width=50)
        self.mlc_viewer_play_button = Button(label="Play", button_type="success", width=100)
        self.mlc_viewer_beam_score = Div(text="<b>Beam Complexity Score: </b>", width=300)

        self.mlc_viewer_data_table = DataTable(source=self.sources.mlc_summary, columns=mlc_viewer_columns,
                                               editable=False, width=700, height=425, index_position=None)

        self.mlc_viewer_previous_cp.on_click(self.mlc_viewer_go_to_previous_cp)
        self.mlc_viewer_next_cp.on_click(self.mlc_viewer_go_to_next_cp)
        self.mlc_viewer_play_button.on_click(self.mlc_viewer_play)
        self.sources.mlc_summary.selected.on_change('indices', self.update_cp_on_selection)

        self.mlc_viewer.x_range = Range1d(-options.MAX_FIELD_SIZE_X / 2, options.MAX_FIELD_SIZE_X / 2)
        self.mlc_viewer.y_range = Range1d(-options.MAX_FIELD_SIZE_Y / 2, options.MAX_FIELD_SIZE_Y / 2)
        self.mlc_viewer.xgrid.grid_line_color = None
        self.mlc_viewer.ygrid.grid_line_color = None

        self.layout = column(Div(text="<b>DVH Analytics v%s</b>" % options.VERSION),
                             row(custom_title['1']['mlc_analyzer'], Spacer(width=50),
                                 custom_title['2']['mlc_analyzer']),
                             row(self.mrn_select, self.study_date_select,
                                 self.uid_select),
                             row(self.plan_select),
                             Div(text="<hr>", width=800),
                             row(self.fx_grp_select, self.beam_select,
                                 self.mlc_viewer_previous_cp, self.mlc_viewer_next_cp,
                                 Spacer(width=10), self.mlc_viewer_play_button, Spacer(width=10),
                                 self.mlc_viewer_beam_score),
                             row(self.mlc_viewer, data_tables.mlc_viewer))

    def mrn_ticker(self, attr, old, new):
        if new == '':
            self.study_date_select.options = ['']
            self.study_date_select.value = ''
            self.uid_select.options = ['']
            self.uid_select.value = ''

        else:
            new_options = []
            for i in range(len(self.sources.plans.data['mrn'])):
                if self.sources.plans.data['mrn'][i] == new:
                    new_options.append(self.sources.plans.data['sim_study_date'][i])
                    new_options.sort()
            old_sim_date = self.study_date_select.value
            self.study_date_select.options = new_options
            self.study_date_select.value = new_options[0]
            if old_sim_date == new_options[0]:
                self.update_uid()

    def study_date_ticker(self, attr, old, new):
        self.update_uid()

    def uid_ticker(self, attr, old, new):
        rt_plan = DVH_SQL().query('DICOM_Files', 'folder_path, plan_file', "study_instance_uid = '%s'" % new)[0]
        folder_path = rt_plan[0]
        if not os.path.isdir(folder_path):
            folder_path = os.path.join(parse_settings_file(get_settings('import'))['imported'],
                                       os.path.split(folder_path)[-1])
        plan_files = [os.path.join(folder_path, file_path) for file_path in rt_plan[1].split(', ')]

        self.plan_select.options = plan_files
        self.plan_select.value = plan_files[0]

    def plan_ticker(self, attr, old, new):
        if os.path.isfile(new):
            try:
                self.mlc_data = mlca.Plan(new)
                self.fx_grp_select.options = [str(i + 1) for i in range(len(self.mlc_data.fx_group))]
                if self.fx_grp_select.value == self.fx_grp_select.options[0]:
                    self.update_beam()
                else:
                    self.fx_grp_select.value = '1'
            except:
                self.mlc_data = []
                print('MLC import failure: %s' % new)
        else:
            self.mlc_data = []
            self.fx_grp_select.options = ['']
            self.fx_grp_select.value = ''
            self.mlc_viewer_beam_score.text = 'DICOM plan file not found!!!'

    def fx_grp_ticker(self, attr, old, new):
        self.update_fx_grp()
        if old == new:
            self.update_beam()

    def beam_ticker(self, attr, old, new):
        self.update_beam()

        # update beam score
        scores = self.sources.mlc_summary.data['cmp_score']
        mu = self.sources.mlc_summary.data['cum_mu'][-1]
        score = np.sum(scores) / float(mu)
        self.mlc_viewer_beam_score.text = "<b>Beam Complexity Score: </b>%s" % round(score, 3)

    def cp_ticker(self, attr, old, new):
        self.update_mlc_viewer()
        self.sources.mlc_summary.selected.indices = [int(new) - 1]

    def update_mrn(self):
        new_options = [mrn for mrn in self.sources.plans.data['mrn']]
        if new_options:
            new_options.sort()
            self.mrn_select.options = new_options
            self.mrn_select.value = new_options[0]
        else:
            self.mrn_select.options = ['']
            self.mrn_select.value = ''

    def update_uid(self):
        if self.mrn_select.value != '':
            new_options = []
            for i in range(len(self.sources.plans.data['mrn'])):
                if self.sources.plans.data['mrn'][i] == self.mrn_select.value and \
                                self.sources.plans.data['sim_study_date'][i] == self.study_date_select.value:
                    new_options.append(self.sources.plans.data['uid'][i])
            self.uid_select.options = new_options
            self.uid_select.value = new_options[0]

        self.update_fx_grp()

    def update_fx_grp(self):
        if self.mlc_data:
            fx_grp = self.mlc_data.fx_group[int(self.fx_grp_select.value) - 1]
            beam_options = ["%s: %s" % (i+1, j) for i, j in enumerate(fx_grp.beam_names)]
            self.beam_select.options = beam_options
            if self.beam_select.value == self.beam_select.options[0]:
                self.update_beam()
            else:
                self.beam_select.value = beam_options[0]

    def update_beam(self):
        if self.mlc_data:
            fx_grp = self.mlc_data.fx_group[int(self.fx_grp_select.value) - 1]
            beam_number = int(self.beam_select.value.split(':')[0])
            beam = fx_grp.beam[beam_number-1]
            cp_count = beam.control_point_count
            cp_numbers = [str(i + 1) for i in range(cp_count)]
            self.cp_select.options = cp_numbers
            if self.cp_select.value == self.cp_select.options[0]:
                self.update_mlc_viewer()
            else:
                self.cp_select.value = cp_numbers[0]
            self.sources.mlc_summary.data = beam.summary

    def update_mlc_viewer(self):
        if self.mlc_data:
            fx_grp = self.mlc_data.fx_group[int(self.fx_grp_select.value) - 1]
            beam_number = int(self.beam_select.value.split(':')[0])
            beam = fx_grp.beam[beam_number - 1]
            cp_index = int(self.cp_select.value) - 1

            x_min, x_max = -options.MAX_FIELD_SIZE_X / 2, options.MAX_FIELD_SIZE_X / 2
            y_min, y_max = -options.MAX_FIELD_SIZE_Y / 2, options.MAX_FIELD_SIZE_Y / 2

            borders = {'top': [y_max, y_max, y_max, beam.jaws[cp_index]['y_min']],
                       'bottom': [y_min, y_min, beam.jaws[cp_index]['y_max'], y_min],
                       'left': [x_min, beam.jaws[cp_index]['x_max'], x_min, x_min],
                       'right': [beam.jaws[cp_index]['x_min'], x_max, x_max, x_max]}
            for edge in list(borders):
                borders[edge].extend(beam.mlc_borders[cp_index][edge])
            borders['color'] = [options.JAW_COLOR] * 4 + [options.MLC_COLOR] * len(beam.mlc_borders[cp_index]['top'])

        self.sources.mlc_viewer.data = borders

    def mlc_viewer_go_to_previous_cp(self):
        index = self.cp_select.options.index(self.cp_select.value)
        self.cp_select.value = self.cp_select.options[index - 1]

    def mlc_viewer_go_to_next_cp(self):
        index = self.cp_select.options.index(self.cp_select.value)
        if index + 1 == len(self.cp_select.options):
            index = -1
        self.cp_select.value = self.cp_select.options[index + 1]

    def mlc_viewer_play(self):
        if self.cp_select.value == self.cp_select.options[-1]:
            self.cp_select.value = self.cp_select.options[0]
        start = self.cp_select.options.index(self.cp_select.value)
        end = len(self.cp_select.options) - 1

        for i in range(start, end):
            self.mlc_viewer_go_to_next_cp()
            time.sleep(options.CP_TIME_SPACING)

    def update_cp_on_selection(self, attr, old, new):
        if new:
            self.cp_select.value = self.cp_select.options[min(new)]
