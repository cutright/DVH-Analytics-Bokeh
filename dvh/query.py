#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
All Query tab objects and functions for the main DVH Analytics bokeh program
Created on Sun Nov 4 2018
@author: Dan Cutright, PhD
"""
from __future__ import print_function
from sql_connector import DVH_SQL
from dateutil.parser import parse
from os.path import dirname, join
from bokeh.models.widgets import Select, Button, TextInput, CheckboxButtonGroup, Dropdown, CheckboxGroup, Div
from bokeh.models import CustomJS, Spacer
from utilities import get_study_instance_uids, clear_source_selection, clear_source_data,\
    group_constraint_count, calc_stats
from bokeh.layouts import column, row
from bokeh.palettes import Colorblind8 as palette
from sql_to_python import QuerySQL
from analysis_tools import DVH
from datetime import datetime
import itertools
import numpy as np
import options
from options import GROUP_LABELS
import time


class Query:
    def __init__(self, sources, categories, dvhs, rad_bio, roi_viewer, time_series,
                 correlation, regression, mlc_analyzer, custom_title, data_tables):
        self.sources = sources
        self.selector_categories = categories.selector
        self.range_categories = categories.range
        self.correlation_variables = categories.correlation_variables
        self.dvhs = dvhs
        self.rad_bio = rad_bio
        self.roi_viewer = roi_viewer
        self.time_series = time_series
        self.correlation = correlation
        self.regression = regression
        self.mlc_analyzer = mlc_analyzer

        self.uids = {n: [] for n in GROUP_LABELS}
        self.allow_source_update = True
        self.current_dvh = []
        self.anon_id_map = []
        self.colors = itertools.cycle(palette)

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Selection Filter UI objects
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!
        category_options = list(self.selector_categories)
        category_options.sort()

        # Add Current row to source
        self.add_selector_row_button = Button(label="Add Selection Filter", button_type="primary", width=200)
        self.add_selector_row_button.on_click(self.add_selector_row)

        # Row
        self.selector_row = Select(value='1', options=['1'], width=50, title="Row")
        self.selector_row.on_change('value', self.selector_row_ticker)

        # Category 1
        self.select_category1 = Select(value="ROI Institutional Category", options=category_options, width=300,
                                       title="Category 1")
        self.select_category1.on_change('value', self.select_category1_ticker)

        # Category 2
        cat_2_sql_table = self.selector_categories[self.select_category1.value]['table']
        cat_2_var_name = self.selector_categories[self.select_category1.value]['var_name']
        self.category2_values = DVH_SQL().get_unique_values(cat_2_sql_table, cat_2_var_name)
        self.select_category2 = Select(value=self.category2_values[0], options=self.category2_values, width=300,
                                       title="Category 2")
        self.select_category2.on_change('value', self.select_category2_ticker)

        # Misc
        self.delete_selector_row_button = Button(label="Delete", button_type="warning", width=100)
        self.delete_selector_row_button.on_click(self.delete_selector_row)
        self.group_selector = CheckboxButtonGroup(labels=["Group 1", "Group 2"], active=[0], width=180)
        self.group_selector.on_change('active', self.ensure_selector_group_is_assigned)
        self.selector_not_operator_checkbox = CheckboxGroup(labels=['Not'], active=[])
        self.selector_not_operator_checkbox.on_change('active', self.selector_not_operator_ticker)

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Range Filter UI objects
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!
        category_options = list(self.range_categories)
        category_options.sort()

        # Add Current row to source
        self.add_range_row_button = Button(label="Add Range Filter", button_type="primary", width=200)
        self.add_range_row_button.on_click(self.add_range_row)

        # Row
        self.range_row = Select(value='', options=[''], width=50, title="Row")
        self.range_row.on_change('value', self.range_row_ticker)

        # Category
        self.select_category = Select(value=options.SELECT_CATEGORY_DEFAULT, options=category_options, width=240, title="Category")
        self.select_category.on_change('value', self.select_category_ticker)

        # Min and max
        self.text_min = TextInput(value='', title='Min: ', width=150)
        self.text_min.on_change('value', self.min_text_ticker)
        self.text_max = TextInput(value='', title='Max: ', width=150)
        self.text_max.on_change('value', self.max_text_ticker)

        # Misc
        self.delete_range_row_button = Button(label="Delete", button_type="warning", width=100)
        self.delete_range_row_button.on_click(self.delete_range_row)
        self.group_range = CheckboxButtonGroup(labels=["Group 1", "Group 2"], active=[0], width=180)
        self.group_range.on_change('active', self.ensure_range_group_is_assigned)
        self.range_not_operator_checkbox = CheckboxGroup(labels=['Not'], active=[])
        self.range_not_operator_checkbox.on_change('active', self.range_not_operator_ticker)

        self.query_button = Button(label="Query", button_type="success", width=100)
        self.query_button.on_click(self.update_data)

        # define Download button and call download.js on click
        menu = [("All Data", "all"), ("Lite", "lite"), ("Only DVHs", "dvhs"), ("Anonymized DVHs", "anon_dvhs")]
        self.download_dropdown = Dropdown(label="Download", button_type="default", menu=menu, width=100)
        self.download_dropdown.callback = CustomJS(args=dict(source=sources.dvhs,
                                                             source_rxs=sources.rxs,
                                                             source_plans=sources.plans,
                                                             source_beams=sources.beams),
                                                   code=open(join(dirname(__file__), "download.js")).read())

        self.layout = column(Div(text="<b>DVH Analytics v%s</b>" % options.VERSION),
                             row(custom_title['1']['query'], Spacer(width=50), custom_title['2']['query'],
                                 Spacer(width=50), self.query_button, Spacer(width=50), self.download_dropdown),
                             Div(text="<b>Query by Categorical Data</b>", width=1000),
                             self.add_selector_row_button,
                             row(self.selector_row, Spacer(width=10), self.select_category1, self.select_category2,
                                 self.group_selector, self.delete_selector_row_button, Spacer(width=10),
                                 self.selector_not_operator_checkbox),
                             data_tables.selection_filter,
                             Div(text="<hr>", width=1050),
                             Div(text="<b>Query by Numerical Data</b>", width=1000),
                             self.add_range_row_button,
                             row(self.range_row, Spacer(width=10), self.select_category, self.text_min,
                                 Spacer(width=30),
                                 self.text_max, Spacer(width=30), self.group_range,
                                 self.delete_range_row_button, Spacer(width=10), self.range_not_operator_checkbox),
                             data_tables.range_filter)

    def get_query(self, group=None):

        if group:
            if group == 1:
                active_groups = [1]
            elif group == 2:
                active_groups = [2]
        else:
            active_groups = [1, 2]

        # Used to accumulate lists of query strings for each table
        # Will assume each item in list is complete query for that SQL column
        queries = {'Plans': [], 'Rxs': [], 'Beams': [], 'DVHs': []}

        # Used to group queries by variable, will combine all queries of same variable with an OR operator
        # e.g., queries_by_sql_column['Plans'][key] = list of strings, where key is sql column
        queries_by_sql_column = {'Plans': {}, 'Rxs': {}, 'Beams': {}, 'DVHs': {}}

        for active_group in active_groups:

            # Accumulate categorical query strings
            data = self.sources.selectors.data
            for r in data['row']:
                r = int(r)
                if data['group'][r - 1] in {active_group, 3}:
                    var_name = self.selector_categories[data['category1'][r - 1]]['var_name']
                    table = self.selector_categories[data['category1'][r - 1]]['table']
                    value = data['category2'][r - 1]
                    if data['not_status'][r - 1]:
                        operator = "!="
                    else:
                        operator = "="

                    query_str = "%s %s '%s'" % (var_name, operator, value)

                    # Append query_str in query_by_sql_column
                    if var_name not in queries_by_sql_column[table].keys():
                        queries_by_sql_column[table][var_name] = []
                    queries_by_sql_column[table][var_name].append(query_str)

            # Accumulate numerical query strings
            data = self.sources.ranges.data
            for r in data['row']:
                r = int(r)
                if data['group'][r - 1] in {active_group, 3}:
                    var_name = self.range_categories[data['category'][r - 1]]['var_name']
                    table = self.range_categories[data['category'][r - 1]]['table']

                    value_low, value_high = data['min'][r - 1], data['max'][r - 1]
                    if data['category'][r - 1] != 'Simulation Date':
                        value_low, value_high = float(value_low), float(value_high)

                    # Modify value_low and value_high so SQL interprets values as dates, if applicable
                    if var_name in {'sim_study_date', 'birth_date'}:
                        value_low = "'%s'" % value_low
                        value_high = "'%s'" % value_high

                    if data['not_status'][r - 1]:
                        query_str = var_name + " NOT BETWEEN " + str(value_low) + " AND " + str(value_high)
                    else:
                        query_str = var_name + " BETWEEN " + str(value_low) + " AND " + str(value_high)

                    # Append query_str in query_by_sql_column
                    if var_name not in queries_by_sql_column[table]:
                        queries_by_sql_column[table][var_name] = []
                    queries_by_sql_column[table][var_name].append(query_str)

        for table in queries:
            temp_str = []
            for v in queries_by_sql_column[table].keys():
                # collect all constraints for a given sql column into one list
                q_by_sql_col = [q for q in queries_by_sql_column[table][v]]

                # combine all constraints for a given sql column with 'or' operators
                temp_str.append("(%s)" % ' OR '.join(q_by_sql_col))

            queries[table] = ' AND '.join(temp_str)
            print(str(datetime.now()), '%s = %s' % (table, queries[table]), sep=' ')

        # Get a list of UIDs that fit the plan, rx, and beam query criteria.  DVH query criteria will not alter the
        # list of UIDs, therefore dvh_query is not needed to get the UID list
        print(str(datetime.now()), 'getting uids', sep=' ')
        uids = get_study_instance_uids(plans=queries['Plans'], rxs=queries['Rxs'], beams=queries['Beams'])['union']

        # uids: a unique list of all uids that satisfy the criteria
        # queries['DVHs']: the dvh query string for SQL
        return uids, queries['DVHs']

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Functions for Querying by categorical data
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def update_select_category2_values(self):
        new = self.select_category1.value
        table_new = self.selector_categories[new]['table']
        var_name_new = self.selector_categories[new]['var_name']
        new_options = DVH_SQL().get_unique_values(table_new, var_name_new)
        self.select_category2.options = new_options
        self.select_category2.value = new_options[0]

    def ensure_selector_group_is_assigned(self, attr, old, new):
        if not self.group_selector.active:
            self.group_selector.active = [-old[0] + 1]
        self.update_selector_source()

    def update_selector_source(self):
        if self.selector_row.value:
            r = int(self.selector_row.value) - 1
            group = sum([i + 1 for i in self.group_selector.active])
            group_labels = ['1', '2', '1 & 2']
            group_label = group_labels[group - 1]
            not_status = ['', 'Not'][len(self.selector_not_operator_checkbox.active)]

            patch = {'category1': [(r, self.select_category1.value)], 'category2': [(r, self.select_category2.value)],
                     'group': [(r, group)], 'group_label': [(r, group_label)], 'not_status': [(r, not_status)]}
            self.sources.selectors.patch(patch)

    def add_selector_row(self):
        if self.sources.selectors.data['row']:
            temp = self.sources.selectors.data

            for key in list(temp):
                temp[key].append('')
            temp['row'][-1] = len(temp['row'])

            self.sources.selectors.data = temp
            new_options = [str(x + 1) for x in range(len(temp['row']))]
            self.selector_row.options = new_options
            self.selector_row.value = new_options[-1]
            self.select_category1.value = options.SELECT_CATEGORY1_DEFAULT
            self.select_category2.value = self.select_category2.options[0]
            self.selector_not_operator_checkbox.active = []
        else:
            self.selector_row.options = ['1']
            self.selector_row.value = '1'
            self.sources.selectors.data = dict(row=[1], category1=[''], category2=[''],
                                               group=[], group_label=[''], not_status=[''])
        self.update_selector_source()

        clear_source_selection(self.sources, 'selectors')

    def select_category1_ticker(self, attr, old, new):
        self.update_select_category2_values()
        self.update_selector_source()

    def select_category2_ticker(self, attr, old, new):
        self.update_selector_source()

    def selector_not_operator_ticker(self, attr, old, new):
        self.update_selector_source()

    def selector_row_ticker(self, attr, old, new):
        if self.sources.selectors.data['category1'] and self.sources.selectors.data['category1'][-1]:
            r = int(self.selector_row.value) - 1
            category1 = self.sources.selectors.data['category1'][r]
            category2 = self.sources.selectors.data['category2'][r]
            group = self.sources.selectors.data['group'][r]
            not_status = self.sources.selectors.data['not_status'][r]

            self.select_category1.value = category1
            self.select_category2.value = category2
            self.group_selector.active = [[0], [1], [0, 1]][group - 1]
            if not_status:
                self.selector_not_operator_checkbox.active = [0]
            else:
                self.selector_not_operator_checkbox.active = []

    def update_selector_row_on_selection(self, attr, old, new):
        if new:
            self.selector_row.value = self.selector_row.options[min(new)]

    def delete_selector_row(self):
        if self.selector_row.value:
            new_selectors_source = self.sources.selectors.data
            index_to_delete = int(self.selector_row.value) - 1
            new_source_length = len(self.sources.selectors.data['category1']) - 1

            if new_source_length == 0:
                clear_source_data(self.sources, 'selector')
                self.selector_row.options = ['']
                self.selector_row.value = ''
                self.group_selector.active = [0]
                self.selector_not_operator_checkbox.active = []
                self.select_category1.value = options.SELECT_CATEGORY1_DEFAULT
                self.select_category2.value = self.select_category2.options[0]
            else:
                for key in list(new_selectors_source):
                    new_selectors_source[key].pop(index_to_delete)

                for i in range(index_to_delete, new_source_length):
                    new_selectors_source['row'][i] -= 1

                self.selector_row.options = [str(x + 1) for x in range(new_source_length)]
                if self.selector_row.value not in self.selector_row.options:
                    self.selector_row.value = self.selector_row.options[-1]
                self.sources.selectors.data = new_selectors_source

            clear_source_selection(self.sources, 'selectors')

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Functions for Querying by numerical data
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def add_range_row(self):
        if self.sources.ranges.data['row']:
            temp = self.sources.ranges.data

            for key in list(temp):
                temp[key].append('')
            temp['row'][-1] = len(temp['row'])
            self.sources.ranges.data = temp
            new_options = [str(x + 1) for x in range(len(temp['row']))]
            self.range_row.options = new_options
            self.range_row.value = new_options[-1]
            self.select_category.value = options.SELECT_CATEGORY_DEFAULT
            self.group_range.active = [0]
            self.range_not_operator_checkbox.active = []
        else:
            self.range_row.options = ['1']
            self.range_row.value = '1'
            self.sources.ranges.data = dict(row=['1'], category=[''], min=[''], max=[''], min_display=[''],
                                            max_display=[''],  group=[''], group_label=[''], not_status=[''])

        self.update_range_titles(reset_values=True)
        self.update_range_source()

        clear_source_selection(self.sources, 'ranges')

    def update_range_source(self):
        if self.range_row.value:
            table = self.range_categories[self.select_category.value]['table']
            var_name = self.range_categories[self.select_category.value]['var_name']

            r = int(self.range_row.value) - 1
            group = sum([i + 1 for i in self.group_range.active])  # a result of 3 means group 1 & 2
            group_labels = ['1', '2', '1 & 2']
            group_label = group_labels[group - 1]
            not_status = ['', 'Not'][len(self.range_not_operator_checkbox.active)]

            if self.select_category.value == 'Simulation Date':
                min_value = str(parse(self.text_min.value).date())
                min_display = min_value

                max_value = str(parse(self.text_max.value).date())
                max_display = max_value
            else:

                try:
                    min_value = float(self.text_min.value)
                except ValueError:
                    try:
                        min_value = float(DVH_SQL().get_min_value(table, var_name))
                    except TypeError:
                        min_value = ''

                try:
                    max_value = float(self.text_max.value)
                except ValueError:
                    try:
                        max_value = float(DVH_SQL().get_max_value(table, var_name))
                    except TypeError:
                        max_value = ''

                if min_value or min_value == 0.:
                    min_display = "%s %s" % (str(min_value), self.range_categories[self.select_category.value]['units'])
                else:
                    min_display = 'None'

                if max_value or max_value == 0.:
                    max_display = "%s %s" % (str(max_value), self.range_categories[self.select_category.value]['units'])
                else:
                    max_display = 'None'

            patch = {'category': [(r, self.select_category.value)], 'min': [(r, min_value)], 'max': [(r, max_value)],
                     'min_display': [(r, min_display)], 'max_display': [(r, max_display)],
                     'group': [(r, group)], 'group_label': [(r, group_label)], 'not_status': [(r, not_status)]}
            self.sources.ranges.patch(patch)

            self.group_range.active = [[0], [1], [0, 1]][group - 1]
            self.text_min.value = str(min_value)
            self.text_max.value = str(max_value)

    def update_range_titles(self, reset_values=False):
        table = self.range_categories[self.select_category.value]['table']
        var_name = self.range_categories[self.select_category.value]['var_name']
        min_value = DVH_SQL().get_min_value(table, var_name)
        self.text_min.title = 'Min: ' + str(min_value) + ' ' + self.range_categories[self.select_category.value]['units']
        max_value = DVH_SQL().get_max_value(table, var_name)
        self.text_max.title = 'Max: ' + str(max_value) + ' ' + self.range_categories[self.select_category.value]['units']

        if reset_values:
            self.text_min.value = str(min_value)
            self.text_max.value = str(max_value)

    def range_row_ticker(self, attr, old, new):
        if self.sources.ranges.data['category'] and self.sources.ranges.data['category'][-1]:
            r = int(new) - 1
            category = self.sources.ranges.data['category'][r]
            min_new = self.sources.ranges.data['min'][r]
            max_new = self.sources.ranges.data['max'][r]
            group = self.sources.ranges.data['group'][r]
            not_status = self.sources.ranges.data['not_status'][r]

            self.allow_source_update = False
            self.select_category.value = category
            self.text_min.value = str(min_new)
            self.text_max.value = str(max_new)
            self.update_range_titles()
            self.group_range.active = [[0], [1], [0, 1]][group - 1]
            self.allow_source_update = True
            if not_status:
                self.range_not_operator_checkbox.active = [0]
            else:
                self.range_not_operator_checkbox.active = []

    def select_category_ticker(self, attr, old, new):
        if self.allow_source_update:
            self.update_range_titles(reset_values=True)
            self.update_range_source()

    def min_text_ticker(self, attr, old, new):
        if self.allow_source_update:
            self.update_range_source()

    def max_text_ticker(self, attr, old, new):
        if self.allow_source_update:
            self.update_range_source()

    def range_not_operator_ticker(self, attr, old, new):
        if self.allow_source_update:
            self.update_range_source()

    def delete_range_row(self):
        if self.range_row.value:
            new_range_source = self.sources.ranges.data
            index_to_delete = int(self.range_row.value) - 1
            new_source_length = len(self.sources.ranges.data['category']) - 1

            if new_source_length == 0:
                clear_source_data(self.sources, 'ranges')
                self.range_row.options = ['']
                self.range_row.value = ''
                self.group_range.active = [0]
                self.range_not_operator_checkbox.active = []
                self.select_category.value = options.SELECT_CATEGORY_DEFAULT
                self.text_min.value = ''
                self.text_max.value = ''
            else:
                for key in list(new_range_source):
                    new_range_source[key].pop(index_to_delete)

                for i in range(index_to_delete, new_source_length):
                    new_range_source['row'][i] -= 1

                self.range_row.options = [str(x + 1) for x in range(new_source_length)]
                if self.range_row.value not in self.range_row.options:
                    self.range_row.value = self.range_row.options[-1]
                self.sources.ranges.data = new_range_source

            clear_source_selection(self.sources, 'ranges')

    def ensure_range_group_is_assigned(self, attr, old, new):
        if not self.group_range.active:
            self.group_range.active = [-old[0] + 1]
        self.update_range_source()

    def update_range_row_on_selection(self, attr, old, new):
        if new:
            self.range_row.value = self.range_row.options[min(new)]

    # main update function
    def update_data(self):
        global BAD_UID
        BAD_UID = {n: [] for n in GROUP_LABELS}
        old_update_button_label = self.query_button.label
        old_update_button_type = self.query_button.button_type
        self.query_button.label = 'Updating...'
        self.query_button.button_type = 'warning'
        print(str(datetime.now()), 'Constructing query for complete dataset', sep=' ')
        uids, dvh_query_str = self.get_query()
        print(str(datetime.now()), 'getting dvh data', sep=' ')
        self.current_dvh = DVH(uid=uids, dvh_condition=dvh_query_str)
        if self.current_dvh.count:
            print(str(datetime.now()), 'initializing source data ', self.current_dvh.query, sep=' ')
            self.time_series.update_current_dvh_group(self.update_dvh_data(self.current_dvh))
            if not options.LITE_VIEW:
                print(str(datetime.now()), 'updating correlation data')
                self.correlation.update_data(self.correlation_variables)
                print(str(datetime.now()), 'correlation data updated')
            self.dvhs.update_source_endpoint_calcs()
            if not options.LITE_VIEW:
                self.dvhs.calculate_review_dvh()
                self.rad_bio.initialize()
                self.time_series.y_axis.value = ''
                self.roi_viewer.update_mrn()
                self.mlc_analyzer.update_mrn()
        else:
            print(str(datetime.now()), 'empty dataset returned', sep=' ')
            self.query_button.label = 'No Data'
            self.query_button.button_type = 'danger'
            time.sleep(2.5)

        self.query_button.label = old_update_button_label
        self.query_button.button_type = old_update_button_type

    # updates beam ColumnSourceData for a given list of uids
    def update_beam_data(self, uids):

        cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
        beam_data = QuerySQL('Beams', cond_str)

        groups = self.get_group_list(beam_data.study_instance_uid)

        anon_id = [self.anon_id_map[beam_data.mrn[i]] for i in range(len(beam_data.mrn))]

        attributes = ['mrn', 'beam_dose', 'beam_energy_min', 'beam_energy_max', 'beam_mu', 'beam_mu_per_deg',
                      'beam_mu_per_cp', 'beam_name', 'beam_number', 'beam_type', 'scan_mode', 'scan_spot_count',
                      'control_point_count', 'fx_count', 'fx_grp_beam_count', 'fx_grp_number', 'gantry_start',
                      'gantry_end', 'gantry_rot_dir', 'gantry_range', 'gantry_min', 'gantry_max', 'collimator_start',
                      'collimator_end', 'collimator_rot_dir', 'collimator_range', 'collimator_min', 'collimator_max',
                      'couch_start', 'couch_end', 'couch_rot_dir', 'couch_range', 'couch_min', 'couch_max',
                      'radiation_type', 'ssd', 'treatment_machine']
        data = {attr: getattr(beam_data, attr) for attr in attributes}
        data['anon_id'] = anon_id
        data['group'] = groups
        data['uid'] = beam_data.study_instance_uid

        self.sources.beams.data = data

    # updates plan ColumnSourceData for a given list of uids
    def update_plan_data(self, uids):

        cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
        plan_data = QuerySQL('Plans', cond_str)

        # Determine Groups
        groups = self.get_group_list(plan_data.study_instance_uid)

        anon_id = [self.anon_id_map[plan_data.mrn[i]] for i in range(len(plan_data.mrn))]

        attributes = ['mrn', 'age', 'birth_date', 'dose_grid_res', 'fxs', 'patient_orientation', 'patient_sex',
                      'physician',
                      'rx_dose', 'sim_study_date', 'total_mu', 'tx_modality', 'tx_site', 'heterogeneity_correction',
                      'baseline']
        data = {attr: getattr(plan_data, attr) for attr in attributes}
        data['anon_id'] = anon_id
        data['group'] = groups
        data['uid'] = plan_data.study_instance_uid

        self.sources.plans.data = data

    # updates rx ColumnSourceData for a given list of uids
    def update_rx_data(self, uids):

        cond_str = "study_instance_uid in ('" + "', '".join(uids) + "')"
        rx_data = QuerySQL('Rxs', cond_str)

        groups = self.get_group_list(rx_data.study_instance_uid)

        anon_id = [self.anon_id_map[rx_data.mrn[i]] for i in range(len(rx_data.mrn))]

        attributes = ['mrn', 'plan_name', 'fx_dose', 'rx_percent', 'fxs', 'rx_dose', 'fx_grp_count', 'fx_grp_name',
                      'fx_grp_number', 'normalization_method', 'normalization_object']
        data = {attr: getattr(rx_data, attr) for attr in attributes}
        data['anon_id'] = anon_id
        data['group'] = groups
        data['uid'] = rx_data.study_instance_uid

        self.sources.rxs.data = data

    def get_group_list(self, uids):

        groups = []
        for r in range(len(uids)):
            if uids[r] in self.uids['1']:
                if uids[r] in self.uids['2']:
                    groups.append('Group 1 & 2')
                else:
                    groups.append('Group 1')
            else:
                groups.append('Group 2')

        return groups

    def update_dvh_data(self, dvh):

        dvh_group_1, dvh_group_2 = [], []
        group_1_constraint_count, group_2_constraint_count = group_constraint_count(self.sources)

        if group_1_constraint_count and group_2_constraint_count:
            extra_rows = 12
        elif group_1_constraint_count or group_2_constraint_count:
            extra_rows = 6
        else:
            extra_rows = 0

        print(str(datetime.now()), 'updating dvh data', sep=' ')
        line_colors = [color for j, color in itertools.izip(range(dvh.count + extra_rows), self.colors)]

        x_axis = np.round(np.add(np.linspace(0, dvh.bin_count, dvh.bin_count) / 100., 0.005), 3)

        print(str(datetime.now()), 'beginning stat calcs', sep=' ')

        if self.dvhs.radio_group_dose.active == 1:
            stat_dose_scale = 'relative'
            x_axis_stat = dvh.get_resampled_x_axis()
        else:
            stat_dose_scale = 'absolute'
            x_axis_stat = x_axis
        if self.dvhs.radio_group_volume.active == 0:
            stat_volume_scale = 'absolute'
        else:
            stat_volume_scale = 'relative'

        print(str(datetime.now()), 'calculating patches', sep=' ')

        if group_1_constraint_count == 0:
            self.uids['1'] = []
            clear_source_data(self.sources, 'patch_1')
            clear_source_data(self.sources, 'stats_1')
        else:
            print(str(datetime.now()), 'Constructing Group 1 query', sep=' ')
            self.uids['1'], dvh_query_str = self.get_query(group=1)
            dvh_group_1 = DVH(uid=self.uids['1'], dvh_condition=dvh_query_str)
            self.uids['1'] = dvh_group_1.study_instance_uid
            stat_dvhs_1 = dvh_group_1.get_standard_stat_dvh(dose_scale=stat_dose_scale,
                                                            volume_scale=stat_volume_scale)

            if self.dvhs.radio_group_dose.active == 1:
                x_axis_1 = dvh_group_1.get_resampled_x_axis()
            else:
                x_axis_1 = np.add(np.linspace(0, dvh_group_1.bin_count, dvh_group_1.bin_count) / 100., 0.005)

            self.sources.patch_1.data = {'x_patch': np.append(x_axis_1, x_axis_1[::-1]).tolist(),
                                         'y_patch': np.append(stat_dvhs_1['q3'], stat_dvhs_1['q1'][::-1]).tolist()}
            self.sources.stats_1.data = {'x': x_axis_1.tolist(),
                                         'min': stat_dvhs_1['min'].tolist(),
                                         'q1': stat_dvhs_1['q1'].tolist(),
                                         'mean': stat_dvhs_1['mean'].tolist(),
                                         'median': stat_dvhs_1['median'].tolist(),
                                         'q3': stat_dvhs_1['q3'].tolist(),
                                         'max': stat_dvhs_1['max'].tolist()}
        if group_2_constraint_count == 0:
            self.uids['2'] = []
            clear_source_data(self.sources, 'patch_2')
            clear_source_data(self.sources, 'stats_2')

        else:
            print(str(datetime.now()), 'Constructing Group 2 query', sep=' ')
            self.uids['2'], dvh_query_str = self.get_query(group=2)
            dvh_group_2 = DVH(uid=self.uids['2'], dvh_condition=dvh_query_str)
            self.uids['2'] = dvh_group_2.study_instance_uid
            stat_dvhs_2 = dvh_group_2.get_standard_stat_dvh(dose_scale=stat_dose_scale,
                                                            volume_scale=stat_volume_scale)

            if self.dvhs.radio_group_dose.active == 1:
                x_axis_2 = dvh_group_2.get_resampled_x_axis()
            else:
                x_axis_2 = np.add(np.linspace(0, dvh_group_2.bin_count, dvh_group_2.bin_count) / 100., 0.005)

            self.sources.patch_2.data = {'x_patch': np.append(x_axis_2, x_axis_2[::-1]).tolist(),
                                         'y_patch': np.append(stat_dvhs_2['q3'], stat_dvhs_2['q1'][::-1]).tolist()}
            self.sources.stats_2.data = {'x': x_axis_2.tolist(),
                                         'min': stat_dvhs_2['min'].tolist(),
                                         'q1': stat_dvhs_2['q1'].tolist(),
                                         'mean': stat_dvhs_2['mean'].tolist(),
                                         'median': stat_dvhs_2['median'].tolist(),
                                         'q3': stat_dvhs_2['q3'].tolist(),
                                         'max': stat_dvhs_2['max'].tolist()}

        print(str(datetime.now()), 'patches calculated', sep=' ')

        if self.dvhs.radio_group_dose.active == 0:
            x_scale = ['Gy'] * (dvh.count + extra_rows + 1)
            self.dvhs.plot.xaxis.axis_label = "Dose (Gy)"
        else:
            x_scale = ['%RxDose'] * (dvh.count + extra_rows + 1)
            self.dvhs.plot.xaxis.axis_label = "Relative Dose (to Rx)"
        if self.dvhs.radio_group_volume.active == 0:
            y_scale = ['cm^3'] * (dvh.count + extra_rows + 1)
            self.dvhs.plot.yaxis.axis_label = "Absolute Volume (cc)"
        else:
            y_scale = ['%Vol'] * (dvh.count + extra_rows + 1)
            self.dvhs.plot.yaxis.axis_label = "Relative Volume"

        # new_endpoint_columns = [''] * (dvh.count + extra_rows + 1)

        x_data, y_data = [], []
        for n in range(dvh.count):
            if self.dvhs.radio_group_dose.active == 0:
                x_data.append(x_axis.tolist())
            else:
                x_data.append(np.divide(x_axis, dvh.rx_dose[n]).tolist())
            if self.dvhs.radio_group_volume.active == 0:
                y_data.append(np.multiply(dvh.dvh[:, n], dvh.volume[n]).tolist())
            else:
                y_data.append(dvh.dvh[:, n].tolist())

        y_names = ['Max', 'Q3', 'Median', 'Mean', 'Q1', 'Min']

        # Determine Population group (blue (1) or red (2))
        dvh_groups = []
        for r in range(len(dvh.study_instance_uid)):

            current_uid = dvh.study_instance_uid[r]
            current_roi = dvh.roi_name[r]

            if dvh_group_1:
                for r1 in range(len(dvh_group_1.study_instance_uid)):
                    if dvh_group_1.study_instance_uid[r1] == current_uid and dvh_group_1.roi_name[r1] == current_roi:
                        dvh_groups.append('Group 1')

            if dvh_group_2:
                for r2 in range(len(dvh_group_2.study_instance_uid)):
                    if dvh_group_2.study_instance_uid[r2] == current_uid and dvh_group_2.roi_name[r2] == current_roi:
                        if len(dvh_groups) == r + 1:
                            dvh_groups[r] = 'Group 1 & 2'
                        else:
                            dvh_groups.append('Group 2')

            if len(dvh_groups) < r + 1:
                dvh_groups.append('error')

        dvh_groups.insert(0, 'Review')

        for n in range(6):
            if group_1_constraint_count > 0:
                dvh.mrn.append(y_names[n])
                dvh.roi_name.append('N/A')
                x_data.append(x_axis_stat.tolist())
                current = stat_dvhs_1[y_names[n].lower()].tolist()
                y_data.append(current)
                dvh_groups.append('Group 1')
            if group_2_constraint_count > 0:
                dvh.mrn.append(y_names[n])
                dvh.roi_name.append('N/A')
                x_data.append(x_axis_stat.tolist())
                current = stat_dvhs_2[y_names[n].lower()].tolist()
                y_data.append(current)
                dvh_groups.append('Group 2')

        # Adjust dvh object to include stats data
        attributes = ['rx_dose', 'volume', 'surface_area', 'min_dose', 'mean_dose', 'max_dose', 'dist_to_ptv_min',
                      'dist_to_ptv_median', 'dist_to_ptv_mean', 'dist_to_ptv_max', 'dist_to_ptv_centroids',
                      'ptv_overlap', 'cross_section_max', 'cross_section_median', 'spread_x', 'spread_y',
                      'spread_z']
        if extra_rows > 0:
            dvh.study_instance_uid.extend(['N/A'] * extra_rows)
            dvh.institutional_roi.extend(['N/A'] * extra_rows)
            dvh.physician_roi.extend(['N/A'] * extra_rows)
            dvh.roi_type.extend(['Stat'] * extra_rows)
        if group_1_constraint_count > 0:
            for attr in attributes:
                getattr(dvh, attr).extend(calc_stats(getattr(dvh_group_1, attr)))

        if group_2_constraint_count > 0:
            for attr in attributes:
                getattr(dvh, attr).extend(calc_stats(getattr(dvh_group_2, attr)))

        # Adjust dvh object for review dvh
        dvh.dvh = np.insert(dvh.dvh, 0, 0, 1)
        dvh.count += 1
        dvh.mrn.insert(0, self.dvhs.select_reviewed_mrn.value)
        dvh.study_instance_uid.insert(0, '')
        dvh.institutional_roi.insert(0, '')
        dvh.physician_roi.insert(0, '')
        dvh.roi_name.insert(0, self.dvhs.select_reviewed_dvh.value)
        dvh.roi_type.insert(0, 'Review')
        dvh.rx_dose.insert(0, 0)
        dvh.volume.insert(0, 0)
        dvh.surface_area.insert(0, '')
        dvh.min_dose.insert(0, '')
        dvh.mean_dose.insert(0, '')
        dvh.max_dose.insert(0, '')
        dvh.dist_to_ptv_min.insert(0, 'N/A')
        dvh.dist_to_ptv_mean.insert(0, 'N/A')
        dvh.dist_to_ptv_median.insert(0, 'N/A')
        dvh.dist_to_ptv_max.insert(0, 'N/A')
        dvh.dist_to_ptv_centroids.insert(0, 'N/A')
        dvh.ptv_overlap.insert(0, 'N/A')
        dvh.cross_section_max.insert(0, 'N/A')
        dvh.cross_section_median.insert(0, 'N/A')
        dvh.spread_x.insert(0, 'N/A')
        dvh.spread_y.insert(0, 'N/A')
        dvh.spread_z.insert(0, 'N/A')
        line_colors.insert(0, options.REVIEW_DVH_COLOR)
        x_data.insert(0, [0])
        y_data.insert(0, [0])

        # anonymize ids
        self.anon_id_map = {mrn: i for i, mrn in enumerate(list(set(dvh.mrn)))}
        anon_id = [self.anon_id_map[dvh.mrn[i]] for i in range(len(dvh.mrn))]

        print(str(datetime.now()), "writing sources.dvhs.data", sep=' ')
        self.sources.dvhs.data = {'mrn': dvh.mrn,
                                  'anon_id': anon_id,
                                  'group': dvh_groups,
                                  'uid': dvh.study_instance_uid,
                                  'roi_institutional': dvh.institutional_roi,
                                  'roi_physician': dvh.physician_roi,
                                  'roi_name': dvh.roi_name,
                                  'roi_type': dvh.roi_type,
                                  'rx_dose': dvh.rx_dose,
                                  'volume': dvh.volume,
                                  'surface_area': dvh.surface_area,
                                  'min_dose': dvh.min_dose,
                                  'mean_dose': dvh.mean_dose,
                                  'max_dose': dvh.max_dose,
                                  'dist_to_ptv_min': dvh.dist_to_ptv_min,
                                  'dist_to_ptv_mean': dvh.dist_to_ptv_mean,
                                  'dist_to_ptv_median': dvh.dist_to_ptv_median,
                                  'dist_to_ptv_max': dvh.dist_to_ptv_max,
                                  'dist_to_ptv_centroids': dvh.dist_to_ptv_centroids,
                                  'ptv_overlap': dvh.ptv_overlap,
                                  'cross_section_max': dvh.cross_section_max,
                                  'cross_section_median': dvh.cross_section_median,
                                  'spread_x': dvh.spread_x,
                                  'spread_y': dvh.spread_y,
                                  'spread_z': dvh.spread_z,
                                  'x': x_data,
                                  'y': y_data,
                                  'color': line_colors,
                                  'x_scale': x_scale,
                                  'y_scale': y_scale}

        print(str(datetime.now()), 'begin updating beam, plan, rx data sources', sep=' ')
        self.update_beam_data(dvh.study_instance_uid)
        self.update_plan_data(dvh.study_instance_uid)
        self.update_rx_data(dvh.study_instance_uid)
        print(str(datetime.now()), 'all sources set', sep=' ')

        return {'1': dvh_group_1, '2': dvh_group_2}