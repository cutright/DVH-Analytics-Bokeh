#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
All ROI Viewer tab objects and functions for the main DVH Analytics bokeh program
Created on Sun Nov 4 2018
@author: Dan Cutright, PhD
"""
import matplotlib.colors as plot_colors
from bokeh.models.widgets import Select, Button, CheckboxGroup, Div
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.models import Spacer
from bokeh_components.utilities import clear_source_data
import options
from bokeh import events
from sql_connector import DVH_SQL
from roi_tools import get_planes_from_string, get_union


class RoiViewerRoiColorTicker:
    def __init__(self, roi_number, roi_viewer_patch):
        self.roi_number = str(roi_number)
        self.roi_viewer_patch = roi_viewer_patch

    def ticker(self, attr, old, new):
        self.roi_viewer_patch[self.roi_number].glyph.fill_color = new
        self.roi_viewer_patch[self.roi_number].glyph.line_color = new


class RoiViewerRoiTicker:
    def __init__(self, sources, roi_viewer_data, roi_number, roi_select, uid_select, slice_select):

        self.sources = sources
        self.roi_number = str(roi_number)
        self.roi_select = roi_select[self.roi_number]
        self.roi_viewer_data = roi_viewer_data
        self.uid_select = uid_select
        self.slice_select = slice_select

    def ticker(self, attr, old, new):
        self.update_roi_viewer_data()
        if self.roi_number == '1':
            self.update_slice()
        else:
            z = self.slice_select.value
            if z in list(self.roi_viewer_data[self.roi_number]):
                getattr(self.sources, 'roi%s_viewer' % self.roi_number).data = self.roi_viewer_data[self.roi_number][z]
            else:
                clear_source_data(self.sources, 'roi%s_viewer' % self.roi_number)

    def update_roi_viewer_data(self):

        # if roi_name is an empty string (default selection), return an empty data set
        if not self.roi_select.value:
            return {'0': {'x': [], 'y': [], 'z': []}}

        roi_data = {}
        roi_coord_string = DVH_SQL().query('dvhs',
                                           'roi_coord_string',
                                           "study_instance_uid = '%s' and roi_name = '%s'" % (self.uid_select.value,
                                                                                              self.roi_select.value))
        roi_planes = get_planes_from_string(roi_coord_string[0][0])
        for z_plane in list(roi_planes):
            x, y, z = [], [], []
            for polygon in roi_planes[z_plane]:
                initial_polygon_index = len(x)
                for point in polygon:
                    x.append(point[0])
                    y.append(point[1])
                    z.append(point[2])
                x.append(x[initial_polygon_index])
                y.append(y[initial_polygon_index])
                z.append(z[initial_polygon_index])
                x.append(float('nan'))
                y.append(float('nan'))
                z.append(float('nan'))
            roi_data[z_plane] = {'x': x, 'y': y, 'z': z}

        self.roi_viewer_data[self.roi_number] = roi_data

    def update_slice(self):
        new_options = list(self.roi_viewer_data['1'])
        new_options.sort()
        self.slice_select.options = new_options
        self.slice_select.value = new_options[len(new_options) / 2]  # default to the middle slice


class ROI_Viewer:
    def __init__(self, sources, custom_title):
        self.sources = sources

        self.data = {str(i): {} for i in range(1, 6)}
        self.tv_data = {}

        roi_colors = plot_colors.cnames.keys()
        roi_colors.sort()
        roi_viewer_options = [''] + sources.dvhs.data['mrn']
        self.mrn_select = Select(value='', options=roi_viewer_options, width=200, title='MRN')
        self.study_date_select = Select(value='', options=[''], width=200, title='Sim Study Date')
        self.uid_select = Select(value='', options=[''], width=400, title='Study Instance UID')
        self.roi_select = {str(i): Select(value='', options=[''], width=200, title='ROI %s Name' % i) for i in range(1, 6)}

        colors = ['blue', 'green', 'red', 'orange', 'lightgreen']
        self.roi_select_color = {str(i): Select(value=colors[i-1], options=roi_colors, width=150, title='ROI %s Color' % i) for i in range(1, 6)}
        self.slice_select = Select(value='', options=[''], width=200, title='Slice: z = ')
        self.previous_slice = Button(label="<", button_type="primary", width=50)
        self.next_slice = Button(label=">", button_type="primary", width=50)
        self.flip_x_axis_button = Button(label='Flip X-Axis', button_type='primary', width=100)
        self.flip_y_axis_button = Button(label='Flip Y-Axis', button_type='primary', width=100)
        self.plot_tv_button = Button(label='Plot TV', button_type='primary', width=100)

        self.mrn_select.on_change('value', self.mrn_ticker)
        self.study_date_select.on_change('value', self.study_date_ticker)
        self.uid_select.on_change('value', self.uid_ticker)
        self.slice_select.on_change('value', self.slice_ticker)

        self.previous_slice.on_click(self.go_to_previous_slice)
        self.next_slice.on_click(self.go_to_next_slice)
        self.flip_x_axis_button.on_click(self.flip_x_axis)
        self.flip_y_axis_button.on_click(self.flip_y_axis)
        self.plot_tv_button.on_click(self.plot_tv)

        self.fig = figure(plot_width=825, plot_height=600, logo=None, match_aspect=True,
                          tools="pan,wheel_zoom,reset,crosshair,save")
        self.fig.xaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.fig.yaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.fig.xaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.fig.yaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.fig.min_border_left = options.MIN_BORDER
        self.fig.min_border_bottom = options.MIN_BORDER
        self.fig.y_range.flipped = True
        self.patch = {str(i): self.fig.patch('x', 'y', source=getattr(self.sources, 'roi%s_viewer' % i),
                                             color=colors[i - 1], alpha=0.5) for i in range(1, 6)}

        self.fig.patch('x', 'y', source=self.sources.tv, color='black', alpha=0.5)
        self.fig.xaxis.axis_label = "Lateral DICOM Coordinate (mm)"
        self.fig.yaxis.axis_label = "Anterior/Posterior DICOM Coordinate (mm)"
        self.fig.on_event(events.MouseWheel, self.wheel_event)
        self.scrolling = CheckboxGroup(labels=["Enable Slice Scrolling with Mouse Wheel"], active=[])

        self.roi_ticker = {str(i): RoiViewerRoiTicker(self.sources, self.data, i, self.roi_select, self.uid_select, self.slice_select) for i in range(1, 6)}
        for i in range(1, 6):
            self.roi_select[str(i)].on_change('value', self.roi_ticker[str(i)].ticker)

        self.roi_color_ticker = {str(i): RoiViewerRoiColorTicker(i, self.patch) for i in range(1, 6)}
        for i in range(1, 6):
            self.roi_select_color[str(i)].on_change('value', self.roi_color_ticker[str(i)].ticker)

        self.layout = column(row(custom_title['1']['roi_viewer'], Spacer(width=50), custom_title['2']['roi_viewer']),
                             row(self.mrn_select, self.study_date_select, self.uid_select),
                             Div(text="<hr>", width=800),
                             row(self.roi_select['1'], self.roi_select_color['1'], self.slice_select,
                                 self.previous_slice, self.next_slice),
                             Div(text="<hr>", width=800),
                             row(self.roi_select['2'], self.roi_select['3'],
                                 self.roi_select['4'], self.roi_select['5']),
                             row(self.roi_select_color['2'], self.roi_select_color['3'],
                                 self.roi_select_color['4'], self.roi_select_color['5']),
                             row(Div(text="<b>NOTE:</b> Axis flipping requires a figure reset "
                                          "(Click the circular double-arrow)", width=1025)),
                             row(self.flip_x_axis_button, self.flip_y_axis_button,
                                 self.plot_tv_button),
                             row(self.scrolling),
                             row(self.fig),
                             row(Spacer(width=1000, height=100)))

    def update_mrn(self):
        new_options = [mrn for mrn in self.sources.plans.data['mrn']]
        if new_options:
            new_options.sort()
            self.mrn_select.options = new_options
            self.mrn_select.value = new_options[0]
        else:
            self.mrn_select.options = ['']
            self.mrn_select.value = ''

    def mrn_ticker(self, attr, old, new):

        if new == '':
            self.study_date_select.options = ['']
            self.study_date_select.value = ''
            self.uid_select.options = ['']
            self.uid_select.value = ''
            for i in range(1, 6):
                self.roi_select[str(i)].options = []
                self.roi_select[str(i)].value = ''

        else:
            # Clear out additional ROIs since current values may not exist in new patient set
            for i in range(2, 6):
                self.roi_select[str(i)].value = ''

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

    def update_uid(self):
        if self.mrn_select.value != '':
            new_options = []
            for i in range(len(self.sources.plans.data['mrn'])):
                if self.sources.plans.data['mrn'][i] == self.mrn_select.value and \
                                self.sources.plans.data['sim_study_date'][i] == self.study_date_select.value:
                    new_options.append(self.sources.plans.data['uid'][i])
            self.uid_select.options = new_options
            self.uid_select.value = new_options[0]

    def uid_ticker(self, attr, old, new):
        self.update_rois()

    def slice_ticker(self, attr, old, new):
        for i in range(1, 6):
            roi_number = str(i)
            z = self.slice_select.value
            if z in list(self.data[roi_number]):
                getattr(self.sources, 'roi%s_viewer' % roi_number).data = self.data[roi_number][z]
            else:
                clear_source_data(self.sources, 'roi%s_viewer' % roi_number)
        clear_source_data(self.sources, 'tv')

    def go_to_previous_slice(self):
        index = self.slice_select.options.index(self.slice_select.value)
        self.slice_select.value = self.slice_select.options[index - 1]

    def go_to_next_slice(self):
        index = self.slice_select.options.index(self.slice_select.value)
        if index + 1 == len(self.slice_select.options):
            index = -1
        self.slice_select.value = self.slice_select.options[index + 1]

    def update_rois(self):

        new_options = DVH_SQL().get_unique_values('DVHs', 'roi_name', "study_instance_uid = '%s'" % self.uid_select.value)
        new_options.sort()

        self.roi_select['1'].options = new_options
        # default to an external like ROI if found
        if 'external' in new_options:
            self.roi_select['1'].value = 'external'
        elif 'ext' in new_options:
            self.roi_select['1'].value = 'ext'
        elif 'body' in new_options:
            self.roi_select['1'].value = 'body'
        elif 'skin' in new_options:
            self.roi_select['1'].value = 'skin'
        else:
            self.roi_select['1'].value = new_options[0]

        for i in range(2, 6):
            self.roi_select[str(i)].options = [''] + new_options
            self.roi_select[str(i)].value = ''

    def update_tv_data(self):
        self.tv_data = {}

        uid = self.uid_select.value
        ptv_coordinates_strings = DVH_SQL().query('dvhs',
                                                  'roi_coord_string',
                                                  "study_instance_uid = '%s' and roi_type like 'PTV%%'"
                                                  % uid)

        if ptv_coordinates_strings:

            ptvs = [get_planes_from_string(ptv[0]) for ptv in ptv_coordinates_strings]
            tv_planes = get_union(ptvs)

        for z_plane in list(tv_planes):
            x, y, z = [], [], []
            for polygon in tv_planes[z_plane]:
                initial_polygon_index = len(x)
                for point in polygon:
                    x.append(point[0])
                    y.append(point[1])
                    z.append(point[2])
                x.append(x[initial_polygon_index])
                y.append(y[initial_polygon_index])
                z.append(z[initial_polygon_index])
                x.append(float('nan'))
                y.append(float('nan'))
                z.append(float('nan'))
                self.tv_data[z_plane] = {'x': x, 'y': y, 'z': z}

    def flip_y_axis(self):
        if self.fig.y_range.flipped:
            self.fig.y_range.flipped = False
        else:
            self.fig.y_range.flipped = True

    def flip_x_axis(self):
        if self.fig.x_range.flipped:
            self.fig.x_range.flipped = False
        else:
            self.fig.x_range.flipped = True

    def plot_tv(self):
        self.update_tv_data()
        z = self.slice_select.value
        if z in list(self.tv_data) and not self.sources.tv.data['x']:
            self.sources.tv.data = self.tv_data[z]
        else:
            clear_source_data(self.sources, 'tv')

    def wheel_event(self, event):
        if self.scrolling.active:
            if event.delta > 0:
                self.go_to_next_slice()
            elif event.delta < 0:
                self.go_to_previous_slice()
