#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
All DVHs tab objects and functions for the main DVH Analytics bokeh program
Created on Sun Nov 4 2018
@author: Dan Cutright, PhD
"""
from bokeh.models.widgets import Select, Button, TableColumn, NumberFormatter, RadioButtonGroup, TextInput,\
    RadioGroup, Div
from bokeh.models import Legend, CustomJS, HoverTool, Spacer
from bokeh.plotting import figure
from bokeh.layouts import column, row
import options
from options import GROUP_LABELS
from os.path import dirname, join
from utilities import clear_source_selection, clear_source_data, group_constraint_count, calc_stats,\
    Temp_DICOM_FileSet, get_csv
from analysis_tools import dose_to_volume, volume_of_dose
import numpy as np
from dicompylercore import dicomparser, dvhcalc


class DVHs:
    def __init__(self, sources, time_series, correlation, regression, custom_title, data_tables):
        self.sources = sources
        self.time_series = time_series
        self.correlation = correlation
        self.regression = regression

        self.dvh_review_rois = []
        self.query = None

        self.temp_dvh_info = Temp_DICOM_FileSet()
        self.dvh_review_mrns = self.temp_dvh_info.mrn
        if self.dvh_review_mrns[0] != '':
            self.dvh_review_rois = self.temp_dvh_info.get_roi_names(self.dvh_review_mrns[0]).values()
            self.dvh_review_mrns.append('')
        else:
            self.dvh_review_rois = ['']

        # Add Current row to source
        self.add_endpoint_row_button = Button(label="Add Endpoint", button_type="primary", width=200)
        self.add_endpoint_row_button.on_click(self.add_endpoint)

        self.ep_row = Select(value='', options=[''], width=50, title="Row")
        self.ep_options = ["Dose (Gy)", "Dose (%)", "Volume (cc)", "Volume (%)"]
        self.select_ep_type = Select(value=self.ep_options[0], options=self.ep_options, width=180, title="Output")
        self.select_ep_type.on_change('value', self.select_ep_type_ticker)
        self.ep_text_input = TextInput(value='', title="Input Volume (cc):", width=180)
        self.ep_text_input.on_change('value', self.ep_text_input_ticker)
        self.ep_units_in = RadioButtonGroup(labels=["cc", "%"], active=0, width=100)
        self.ep_units_in.on_change('active', self.ep_units_in_ticker)
        self.delete_ep_row_button = Button(label="Delete", button_type="warning", width=100)
        self.delete_ep_row_button.on_click(self.delete_ep_row)

        tools = "pan,wheel_zoom,box_zoom,reset,crosshair,save"
        self.plot = figure(plot_width=1050, plot_height=500, tools=tools, logo=None, active_drag="box_zoom")
        self.plot.min_border_left = options.MIN_BORDER
        self.plot.min_border_bottom = options.MIN_BORDER
        self.plot.add_tools(HoverTool(show_arrow=False, line_policy='next',
                                      tooltips=[('Label', '@mrn @roi_name'),
                                                ('Dose', '$x'),
                                                ('Volume', '$y')]))
        self.plot.xaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.plot.yaxis.axis_label_text_font_size = options.PLOT_AXIS_LABEL_FONT_SIZE
        self.plot.xaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.plot.yaxis.major_label_text_font_size = options.PLOT_AXIS_MAJOR_LABEL_FONT_SIZE
        self.plot.yaxis.axis_label_text_baseline = "bottom"
        self.plot.lod_factor = options.LOD_FACTOR  # level of detail during interactive plot events

        # Add statistical plots to figure
        stats_median_1 = self.plot.line('x', 'median', source=sources.stats_1,
                                        line_width=options.STATS_1_MEDIAN_LINE_WIDTH, color=options.GROUP_1_COLOR,
                                        line_dash=options.STATS_1_MEDIAN_LINE_DASH, alpha=options.STATS_1_MEDIAN_ALPHA)
        stats_mean_1 = self.plot.line('x', 'mean', source=sources.stats_1,
                                      line_width=options.STATS_1_MEAN_LINE_WIDTH, color=options.GROUP_1_COLOR,
                                      line_dash=options.STATS_1_MEAN_LINE_DASH, alpha=options.STATS_1_MEAN_ALPHA)
        stats_median_2 = self.plot.line('x', 'median', source=sources.stats_2,
                                        line_width=options.STATS_2_MEDIAN_LINE_WIDTH, color=options.GROUP_2_COLOR,
                                        line_dash=options.STATS_2_MEDIAN_LINE_DASH, alpha=options.STATS_2_MEDIAN_ALPHA)
        stats_mean_2 = self.plot.line('x', 'mean', source=sources.stats_2,
                                      line_width=options.STATS_2_MEAN_LINE_WIDTH, color=options.GROUP_2_COLOR,
                                      line_dash=options.STATS_2_MEAN_LINE_DASH, alpha=options.STATS_2_MEAN_ALPHA)

        # Add all DVHs, but hide them until selected
        self.plot.multi_line('x', 'y', source=sources.dvhs,
                             selection_color='color', line_width=options.DVH_LINE_WIDTH, alpha=0,
                             line_dash=options.DVH_LINE_DASH, nonselection_alpha=0, selection_alpha=1)

        # Shaded region between Q1 and Q3
        iqr_1 = self.plot.patch('x_patch', 'y_patch', source=sources.patch_1, alpha=options.IQR_1_ALPHA,
                                color=options.GROUP_1_COLOR)
        iqr_2 = self.plot.patch('x_patch', 'y_patch', source=sources.patch_2, alpha=options.IQR_2_ALPHA,
                                color=options.GROUP_2_COLOR)

        # Set x and y axis labels
        self.plot.xaxis.axis_label = "Dose (Gy)"
        self.plot.yaxis.axis_label = "Normalized Volume"

        # Set the legend (for stat dvhs only)
        legend_stats = Legend(items=[("Median", [stats_median_1]),
                                     ("Mean", [stats_mean_1]),
                                     ("IQR", [iqr_1]),
                                     ("Median", [stats_median_2]),
                                     ("Mean", [stats_mean_2]),
                                     ("IQR", [iqr_2])],
                              location=(25, 0))

        # Add the layout outside the plot, clicking legend item hides the line
        self.plot.add_layout(legend_stats, 'right')
        self.plot.legend.click_policy = "hide"

        self.download_endpoints_button = Button(label="Download Endpoints", button_type="default", width=150)
        self.download_endpoints_button.callback = CustomJS(args=dict(source=self.sources.endpoints_csv),
                                                           code=open(join(dirname(__file__),
                                                                          "download_new.js")).read())

        # Setup axis normalization radio buttons
        self.radio_group_dose = RadioGroup(labels=["Absolute Dose", "Relative Dose (Rx)"], active=0, width=200)
        self.radio_group_dose.on_change('active', self.radio_group_ticker)
        self.radio_group_volume = RadioGroup(labels=["Absolute Volume", "Relative Volume"], active=1, width=200)
        self.radio_group_volume.on_change('active', self.radio_group_ticker)

        # Setup selectors for dvh review
        self.select_reviewed_mrn = Select(title='MRN to review', value='', options=self.dvh_review_mrns, width=300)
        self.select_reviewed_mrn.on_change('value', self.update_dvh_review_rois)

        self.select_reviewed_dvh = Select(title='ROI to review', value='', options=[''], width=360)
        self.select_reviewed_dvh.on_change('value', self.select_reviewed_dvh_ticker)

        self.review_rx = TextInput(value='', title="Rx Dose (Gy):", width=170)
        self.review_rx.on_change('value', self.review_rx_ticker)

        if options.LITE_VIEW:
            self.layout = column(Div(text="<b>DVH Analytics v%s</b>" % options.VERSION),
                                 row(self.radio_group_dose, self.radio_group_volume),
                                 self.add_endpoint_row_button,
                                 row(self.ep_row, Spacer(width=10), self.select_ep_type, self.ep_text_input,
                                     Spacer(width=20),
                                     self.ep_units_in, self.delete_ep_row_button, Spacer(width=50),
                                     self.download_endpoints_button),
                                 data_tables.ep)
        else:
            self.layout = column(Div(text="<b>DVH Analytics v%s</b>" % options.VERSION),
                                 row(custom_title['1']['dvhs'], Spacer(width=50), custom_title['2']['dvhs']),
                                 row(self.radio_group_dose, self.radio_group_volume),
                                 row(self.select_reviewed_mrn, self.select_reviewed_dvh, self.review_rx),
                                 self.plot,
                                 Div(text="<b>DVHs</b>", width=1200),
                                 data_tables.dvhs,
                                 Div(text="<hr>", width=1050),
                                 Div(text="<b>Define Endpoints</b>", width=1000),
                                 self.add_endpoint_row_button,
                                 row(self.ep_row, Spacer(width=10), self.select_ep_type, self.ep_text_input,
                                     Spacer(width=20),
                                     self.ep_units_in, self.delete_ep_row_button, Spacer(width=50),
                                     self.download_endpoints_button),
                                 data_tables.ep,
                                 Div(text="<b>DVH Endpoints</b>", width=1200),
                                 data_tables.endpoints)

    def add_endpoint(self):
        if self.sources.endpoint_defs.data['row']:
            temp = self.sources.endpoint_defs.data

            for key in list(temp):
                temp[key].append('')
            temp['row'][-1] = len(temp['row'])
            self.sources.endpoint_defs.data = temp

            new_options = [str(x + 1) for x in range(len(temp['row']))]
            self.ep_row.options = new_options
            self.ep_row.value = new_options[-1]
        else:
            self.ep_row.options = ['1']
            self.ep_row.value = '1'
            self.sources.endpoint_defs.data = dict(row=['1'], output_type=[''], input_type=[''], input_value=[''],
                                                   label=[''], units_in=[''], units_out=[''])
            if not self.ep_text_input.value:
                self.ep_text_input.value = '1'

        self.update_ep_source()

        clear_source_selection(self.sources, 'endpoint_defs')

    def update_ep_source(self):
        if self.ep_row.value:

            r = int(self.ep_row.value) - 1

            if 'Dose' in self.select_ep_type.value:
                input_type, output_type = 'Volume', 'Dose'
                if '%' in self.select_ep_type.value:
                    units_out = '%'
                else:
                    units_out = 'Gy'
                units_in = ['cc', '%'][self.ep_units_in.active]
                label = "D_%s%s" % (self.ep_text_input.value, units_in)
            else:
                input_type, output_type = 'Dose', 'Volume'
                if '%' in self.select_ep_type.value:
                    units_out = '%'
                else:
                    units_out = 'cc'
                units_in = ['Gy', '%'][self.ep_units_in.active]
                label = "V_%s%s" % (self.ep_text_input.value, units_in)

            try:
                input_value = float(self.ep_text_input.value)
            except:
                input_value = 1

            patch = {'output_type': [(r, output_type)], 'input_type': [(r, input_type)],
                     'input_value': [(r, input_value)], 'label': [(r, label)],
                     'units_in': [(r, units_in)], 'units_out': [(r, units_out)]}

            self.sources.endpoint_defs.patch(patch)
            self.update_source_endpoint_calcs()

    def ep_units_in_ticker(self, attr, old, new):
        if self.query.allow_source_update:
            self.update_ep_text_input_title()
            self.update_ep_source()

    def update_ep_text_input_title(self):
        if 'Dose' in self.select_ep_type.value:
            self.ep_text_input.title = "Input Volume (%s):" % ['cc', '%'][self.ep_units_in.active]
        else:
            self.ep_text_input.title = "Input Dose (%s):" % ['Gy', '%'][self.ep_units_in.active]

    def select_ep_type_ticker(self, attr, old, new):
        if self.query.allow_source_update:
            if 'Dose' in new:
                self.ep_units_in.labels = ['cc', '%']
            else:
                self.ep_units_in.labels = ['Gy', '%']

            self.update_ep_text_input_title()
            self.update_ep_source()

    def ep_text_input_ticker(self, attr, old, new):
        if self.query.allow_source_update:
            self.update_ep_source()

    def delete_ep_row(self):
        if self.ep_row.value:
            new_ep_source = self.sources.endpoint_defs.data
            index_to_delete = int(self.ep_row.value) - 1
            new_source_length = len(self.sources.endpoint_defs.data['output_type']) - 1

            if new_source_length == 0:
                clear_source_data(self.sources, 'endpoint_defs')
                self.ep_row.options = ['']
                self.ep_row.value = ''
            else:
                for key in list(new_ep_source):
                    new_ep_source[key].pop(index_to_delete)

                for i in range(index_to_delete, new_source_length):
                    new_ep_source['row'][i] -= 1

                self.ep_row.options = [str(x + 1) for x in range(new_source_length)]
                if self.ep_row.value not in self.ep_row.options:
                    self.ep_row.value = self.ep_row.options[-1]
                self.sources.endpoint_defs.data = new_ep_source

            self.update_source_endpoint_calcs()  # not efficient, but still relatively quick
            clear_source_selection(self.sources, 'endpoint_defs')

    def update_ep_row_on_selection(self, attr, old, new):
        self.query.allow_source_update = False

        if new:
            data = self.sources.endpoint_defs.data
            r = min(new)

            # update row
            self.ep_row.value = self.ep_row.options[r]

            # update input value
            self.ep_text_input.value = str(data['input_value'][r])

            # update input units radio button
            if '%' in data['units_in'][r]:
                self.ep_units_in.active = 1
            else:
                self.ep_units_in.active = 0

            # update output
            if 'Dose' in data['output_type'][r]:
                if '%' in data['units_in'][r]:
                    self.select_ep_type.value = self.ep_options[1]
                else:
                    self.select_ep_type.value = self.ep_options[0]
            else:
                if '%' in data['units_in'][r]:
                    self.select_ep_type.value = self.ep_options[3]
                else:
                    self.select_ep_type.value = self.ep_options[2]

        self.query.allow_source_update = True

    def update_source_endpoint_calcs(self):

        if self.query.current_dvh:
            group_1_constraint_count, group_2_constraint_count = group_constraint_count(self.sources)

            ep = {'mrn': ['']}
            ep_group = {'1': {}, '2': {}}

            table_columns = []

            ep['mrn'] = self.query.current_dvh.mrn
            ep['uid'] = self.query.current_dvh.study_instance_uid
            ep['group'] = self.sources.dvhs.data['group']
            ep['roi_name'] = self.sources.dvhs.data['roi_name']

            table_columns.append(TableColumn(field='mrn', title='MRN'))
            table_columns.append(TableColumn(field='group', title='Group'))
            table_columns.append(TableColumn(field='roi_name', title='ROI Name'))

            data = self.sources.endpoint_defs.data
            for r in range(len(data['row'])):
                ep_name = str(data['label'][r])
                table_columns.append(
                    TableColumn(field=ep_name, title=ep_name, formatter=NumberFormatter(format="0.00")))
                x = data['input_value'][r]

                if '%' in data['units_in'][r]:
                    endpoint_input = 'relative'
                    x /= 100.
                else:
                    endpoint_input = 'absolute'

                if '%' in data['units_out'][r]:
                    endpoint_output = 'relative'
                else:
                    endpoint_output = 'absolute'

                if 'Dose' in data['output_type'][r]:
                    ep[ep_name] = self.query.current_dvh.get_dose_to_volume(x, volume_scale=endpoint_input,
                                                                 dose_scale=endpoint_output)
                    for g in GROUP_LABELS:
                        if self.time_series.current_dvh_group[g]:
                            ep_group[g][ep_name] = self.time_series.current_dvh_group[g].get_dose_to_volume(x,
                                                                                                       volume_scale=endpoint_input,
                                                                                                       dose_scale=endpoint_output)

                else:
                    ep[ep_name] = self.query.current_dvh.get_volume_of_dose(x, dose_scale=endpoint_input,
                                                                 volume_scale=endpoint_output)
                    for g in GROUP_LABELS:
                        if self.time_series.current_dvh_group[g]:
                            ep_group[g][ep_name] = self.time_series.current_dvh_group[g].get_volume_of_dose(x,
                                                                                                       dose_scale=endpoint_input,
                                                                                                       volume_scale=endpoint_output)

                if group_1_constraint_count and group_2_constraint_count:
                    ep_1_stats = calc_stats(ep_group['1'][ep_name])
                    ep_2_stats = calc_stats(ep_group['2'][ep_name])
                    stats = []
                    for i in range(len(ep_1_stats)):
                        stats.append(ep_1_stats[i])
                        stats.append(ep_2_stats[i])
                    ep[ep_name].extend(stats)
                else:
                    ep[ep_name].extend(calc_stats(ep[ep_name]))

            self.sources.endpoint_calcs.data = ep

            # Update endpoint calc from review_dvh, if available
            if self.sources.dvhs.data['y'][0] != []:
                review_ep = {}
                rx = float(self.sources.dvhs.data['rx_dose'][0])
                volume = float(self.sources.dvhs.data['volume'][0])
                data = self.sources.endpoint_defs.data
                for r in range(len(data['row'])):
                    ep_name = str(data['label'][r])
                    x = data['input_value'][r]

                    if '%' in data['units_in'][r]:
                        endpoint_input = 'relative'
                        x /= 100.
                    else:
                        endpoint_input = 'absolute'

                    if '%' in data['units_out'][r]:
                        endpoint_output = 'relative'
                    else:
                        endpoint_output = 'absolute'

                    if 'Dose' in data['output_type'][r]:
                        if endpoint_input == 'relative':
                            current_ep = dose_to_volume(y, x)
                        else:
                            current_ep = dose_to_volume(y, x / volume)
                        if endpoint_output == 'relative' and rx != 0:
                            current_ep = current_ep / rx

                    else:
                        if endpoint_input == 'relative':
                            current_ep = volume_of_dose(y, x * rx)
                        else:
                            current_ep = volume_of_dose(y, x)
                        if endpoint_output == 'absolute' and volume != 0:
                            current_ep = current_ep * volume

                    review_ep[ep_name] = [(0, current_ep)]

                review_ep['mrn'] = [(0, self.select_reviewed_mrn.value)]
                self.sources.endpoint_calcs.patch(review_ep)

            self.update_endpoint_view()
            self.update_endpoint_csv()

        if not options.LITE_VIEW:
            self.time_series.update_options()

    def update_endpoint_view(self):
        if self.query.current_dvh:
            rows = len(self.sources.endpoint_calcs.data['mrn'])
            ep_view = {'mrn': self.sources.endpoint_calcs.data['mrn'],
                       'group': self.sources.endpoint_calcs.data['group'],
                       'roi_name': self.sources.endpoint_calcs.data['roi_name']}
            for i in range(1, options.ENDPOINT_COUNT + 1):
                ep_view["ep%s" % i] = [''] * rows  # filling table with empty strings

            for r in range(len(self.sources.endpoint_defs.data['row'])):
                if r < options.ENDPOINT_COUNT:  # limiting UI to ENDPOINT_COUNT for efficiency
                    key = self.sources.endpoint_defs.data['label'][r]
                    ep_view["ep%s" % (r + 1)] = self.sources.endpoint_calcs.data[key]

            self.sources.endpoint_view.data = ep_view

            if not options.LITE_VIEW:
                self.correlation.update_or_add_endpoints_to_correlation()
                categories = list(self.correlation.data['1'])
                categories.sort()

                self.regression.x.options = [''] + categories
                self.regression.y.options = [''] + categories

                self.correlation.validate_data()
                self.correlation.update_correlation_matrix()
                self.regression.update_data()

    def update_source_endpoint_view_selection(self, attr, old, new):
        if new:
            self.sources.endpoint_view.selected.indices = new

    def update_dvh_table_selection(self, attr, old, new):
        if new:
            self.sources.dvhs.selected.indices = new

    def update_dvh_review_rois(self, attr, old, new):
        if self.select_reviewed_mrn.value:
            if new != '':
                self.dvh_review_rois = self.temp_dvh_info.get_roi_names(new).values()
                self.select_reviewed_dvh.options = self.dvh_review_rois
                self.select_reviewed_dvh.value = self.dvh_review_rois[0]
            else:
                self.select_reviewed_dvh.options = ['']
                self.select_reviewed_dvh.value = ['']

        else:
            self.select_reviewed_dvh.options = ['']
            self.select_reviewed_dvh.value = ''
            patches = {'x': [(0, [])],
                       'y': [(0, [])],
                       'roi_name': [(0, '')],
                       'volume': [(0, '')],
                       'min_dose': [(0, '')],
                       'mean_dose': [(0, '')],
                       'max_dose': [(0, '')],
                       'mrn': [(0, '')],
                       'rx_dose': [(0, '')]}
            self.sources.dvhs.patch(patches)

    def calculate_review_dvh(self):
        global x, y

        patches = {'x': [(0, [])],
                   'y': [(0, [])],
                   'roi_name': [(0, '')],
                   'volume': [(0, 1)],
                   'min_dose': [(0, '')],
                   'mean_dose': [(0, '')],
                   'max_dose': [(0, '')],
                   'mrn': [(0, '')],
                   'rx_dose': [(0, 1)]}

        try:
            if not self.sources.dvhs.data['x']:
                self.query.update_data()

            else:
                file_index = self.temp_dvh_info.mrn.index(self.select_reviewed_mrn.value)
                roi_index = self.dvh_review_rois.index(self.select_reviewed_dvh.value)
                structure_file = self.temp_dvh_info.structure[file_index]
                plan_file = self.temp_dvh_info.plan[file_index]
                dose_file = self.temp_dvh_info.dose[file_index]
                key = list(self.temp_dvh_info.get_roi_names(self.select_reviewed_mrn.value))[roi_index]

                rt_st = dicomparser.DicomParser(structure_file)
                rt_structures = rt_st.GetStructures()
                review_dvh = dvhcalc.get_dvh(structure_file, dose_file, key)
                dicompyler_plan = dicomparser.DicomParser(plan_file).GetPlan()

                roi_name = rt_structures[key]['name']
                volume = review_dvh.volume
                min_dose = review_dvh.min
                mean_dose = review_dvh.mean
                max_dose = review_dvh.max
                if not self.review_rx.value:
                    rx_dose = float(dicompyler_plan['rxdose']) / 100.
                    self.review_rx.value = str(round(rx_dose, 2))
                else:
                    rx_dose = round(float(self.review_rx.value), 2)

                x = review_dvh.bincenters
                if max(review_dvh.counts):
                    y = np.divide(review_dvh.counts, max(review_dvh.counts))
                else:
                    y = review_dvh.counts

                if self.radio_group_dose.active == 1:
                    f = 5000
                    bin_count = len(x)
                    new_bin_count = int(bin_count * f / (rx_dose * 100.))

                    x1 = np.linspace(0, bin_count, bin_count)
                    x2 = np.multiply(np.linspace(0, new_bin_count, new_bin_count), rx_dose * 100. / f)
                    y = np.interp(x2, x1, review_dvh.counts)
                    y = np.divide(y, np.max(y))
                    x = np.divide(np.linspace(0, new_bin_count, new_bin_count), f)

                if self.radio_group_volume.active == 0:
                    y = np.multiply(y, volume)

                patches = {'x': [(0, x)],
                           'y': [(0, y)],
                           'roi_name': [(0, roi_name)],
                           'volume': [(0, volume)],
                           'min_dose': [(0, min_dose)],
                           'mean_dose': [(0, mean_dose)],
                           'max_dose': [(0, max_dose)],
                           'mrn': [(0, self.select_reviewed_mrn.value)],
                           'rx_dose': [(0, rx_dose)]}

        except:
            pass

        self.sources.dvhs.patch(patches)

        self.update_source_endpoint_calcs()

    def select_reviewed_dvh_ticker(self, attr, old, new):
        self.calculate_review_dvh()

    def review_rx_ticker(self, attr, old, new):
        if self.radio_group_dose.active == 0:
            self.sources.dvhs.patch({'rx_dose': [(0, round(float(self.review_rx.value), 2))]})
        else:
            self.calculate_review_dvh()

    def radio_group_ticker(self, attr, old, new):
        if self.sources.dvhs.data['x'] != '':
            self.query.update_data()
            self.calculate_review_dvh()

    def add_query_link(self, query):
        self.query = query

    def update_endpoint_csv(self):

        src_data = [self.sources.endpoint_calcs.data]
        columns = ['mrn', 'uid', 'group', 'roi_name']
        eps = [key for key in list(src_data[0]) if key not in columns]
        eps.sort()
        columns.extend(eps)
        csv_text = get_csv(src_data, ['Endpoint Calcs'], columns)

        self.sources.endpoints_csv.data = {'text': [csv_text]}
