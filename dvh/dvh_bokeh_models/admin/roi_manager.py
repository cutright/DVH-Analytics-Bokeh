#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
roi manager model for admin view
Created on Tue Dec 25 2018
@author: Dan Cutright, PhD
"""

from __future__ import print_function
from tools.io.preferences.sql import validate_sql_connection, load_sql_settings
from tools.roi.name_manager import DatabaseROIs, clean_name
from tools.io.database.sql_connector import DVH_SQL
from bokeh.models.widgets import Select, Button, TextInput, RadioButtonGroup, Div
from bokeh.layouts import row, column
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LabelSet, Range1d, Spacer


class RoiManager:
    def __init__(self):

        widget_width = 200

        # Create empty Bokeh data sources
        self.source_table = ColumnDataSource(data=dict(institutional_roi=[], physician_roi=[], variation=[]))

        self.categories = ["Institutional ROI", "Physician", "Physician ROI", "Variation"]
        self.operators = ["Add", "Delete", "Rename"]

        # Load ROI map
        self.db = DatabaseROIs()

        self.function_map = {'Add Institutional ROI': self.add_institutional_roi,
                             'Add Physician': self.add_physician,
                             'Add Physician ROI': self.add_physician_roi,
                             'Add Variation': self.add_variation,
                             'Delete Institutional ROI': self.delete_institutional_roi,
                             'Delete Physician': self.delete_physician,
                             'Delete Physician ROI': self.delete_physician_roi,
                             'Delete Variation': self.delete_variation,
                             'Rename Institutional ROI': self.rename_institutional_roi,
                             'Rename Physician': self.rename_physician,
                             'Rename Physician ROI': self.rename_physician_roi,
                             'Rename Variation': self.rename_variation}

        # Selectors
        roi_options = self.db.get_institutional_rois()
        self.select_institutional_roi = Select(value=roi_options[0],
                                               options=roi_options,
                                               width=widget_width,
                                               title='All Institutional ROIs')

        physician_options = self.db.get_physicians()
        if len(physician_options) > 1:
            value = physician_options[1]
        else:
            value = physician_options[0]
        self.select_physician = Select(value=value,
                                       options=physician_options,
                                       width=widget_width,
                                       title='Physician')

        phys_roi_options = self.db.get_physician_rois(self.select_physician.value)
        self.select_physician_roi = Select(value=phys_roi_options[0],
                                           options=phys_roi_options,
                                           width=widget_width,
                                           title='Physician ROIs')

        variations_options = self.db.get_variations(self.select_physician.value, self.select_physician_roi.value)
        self.select_variation = Select(value=variations_options[0],
                                       options=variations_options,
                                       width=widget_width,
                                       title='Variations')

        unused_roi_options = self.db.get_unused_institutional_rois(self.select_physician.value)
        value = self.db.get_institutional_roi(self.select_physician.value, self.select_physician_roi.value)
        if value not in unused_roi_options:
            unused_roi_options.append(value)
            unused_roi_options.sort()
        self.select_unlinked_institutional_roi = Select(value=value,
                                                        options=unused_roi_options,
                                                        width=widget_width,
                                                        title='Linked Institutional ROI')
        self.uncategorized_variations = self.get_uncategorized_variations(self.select_physician.value)
        try:
            uncat_var_options = list(self.uncategorized_variations)
        except:
            uncat_var_options = ['']
        uncat_var_options.sort()
        self.select_uncategorized_variation = Select(value=uncat_var_options[0],
                                                     options=uncat_var_options,
                                                     width=widget_width,
                                                     title='Uncategorized Variations')
        ignored_variations = self.get_ignored_variations(self.select_physician.value)
        try:
            ignored_var_options = list(ignored_variations)
        except:
            ignored_var_options = ['']
        if not ignored_var_options:
            ignored_var_options = ['']
        else:
            ignored_var_options.sort()
        self.select_ignored_variation = Select(value=ignored_var_options[0],
                                               options=ignored_var_options,
                                               width=widget_width,
                                               title='Ignored Variations')

        self.div_action = Div(text="<b>No Action</b>", width=widget_width*2)

        self.input_text = TextInput(value='', title='Add Institutional ROI:', width=widget_width)

        # RadioButtonGroups
        self.category = RadioButtonGroup(labels=self.categories, active=0, width=400)
        self.operator = RadioButtonGroup(labels=self.operators, active=0, width=200)

        # Ticker calls
        self.select_institutional_roi.on_change('value', self.select_institutional_roi_change)
        self.select_physician.on_change('value', self.select_physician_change)
        self.select_physician_roi.on_change('value', self.select_physician_roi_change)
        self.select_variation.on_change('value', self.select_variation_change)
        self.category.on_change('active', self.category_change)
        self.operator.on_change('active', self.operator_change)
        self.input_text.on_change('value', self.input_text_change)
        self.select_unlinked_institutional_roi.on_change('value', self.unlinked_institutional_roi_change)
        self.select_uncategorized_variation.on_change('value', self.update_uncategorized_variation_change)

        # Button objects
        self.action_button = Button(label='Add Institutional ROI', button_type='primary',
                                    width=int(widget_width*(2./3)))
        self.reload_button_roi = Button(label='Reload Map', button_type='primary', width=widget_width)
        self.save_button_roi = Button(label='Map Saved', button_type='primary', width=widget_width)
        self.ignore_button_roi = Button(label='Ignore', button_type='primary', width=widget_width/2)
        self.delete_uncategorized_button_roi = Button(label='Delete DVH', button_type='warning', width=widget_width/2)
        self.unignore_button_roi = Button(label='UnIgnore', button_type='primary', width=widget_width/2)
        self.delete_ignored_button_roi = Button(label='Delete DVH', button_type='warning', width=widget_width/2)
        self.update_uncategorized_rois_button = Button(label='Update Uncategorized ROIs in DB', button_type='warning',
                                                       width=widget_width)
        self.remap_all_rois_for_selected_physician_button = Button(label='Remap all ROIs for Physician',
                                                                   button_type='warning', width=widget_width)
        self.remap_all_rois_button = Button(label='Remap all ROIs in DB', button_type='warning', width=widget_width)

        # Button calls
        self.action_button.on_click(self.execute_button_click)
        self.reload_button_roi.on_click(self.reload_db)
        self.save_button_roi.on_click(self.save_db)
        self.delete_uncategorized_button_roi.on_click(self.delete_uncategorized_dvh)
        self.ignore_button_roi.on_click(self.ignore_dvh)
        self.delete_ignored_button_roi.on_click(self.delete_ignored_dvh)
        self.unignore_button_roi.on_click(self.unignore_dvh)
        self.update_uncategorized_rois_button.on_click(self.update_uncategorized_rois_in_db)
        self.remap_all_rois_for_selected_physician_button.on_click(self.remap_all_rois_for_selected_physician)
        self.remap_all_rois_button.on_click(self.remap_all_rois_in_db)

        # Plot
        self.select_plot_display = Select(value='All', width=widget_width, title='Institutional Data to Display:',
                                          options=['All', 'Linked', 'Unlinked', 'Branched'])
        self.select_plot_display.on_change('value', self.select_plot_display_ticker)
        self.select_merge_physician_roi = {'a': Select(value='', options=[''], width=widget_width,
                                                       title='Merge Physician ROI A:'),
                                           'b': Select(value='', options=[''], width=widget_width,
                                                       title='Into Physician ROI B:'),
                                           'button': Button(label='Merge', button_type='primary', width=widget_width/2)}
        self.select_merge_physician_roi['button'].on_click(self.merge_click)

        self.roi_map_plot = figure(plot_width=800, plot_height=800,
                                   x_range=["Institutional ROI", "Physician ROI", "Variations"],
                                   x_axis_location="above",
                                   title="(Linked by Physician dropdowns)",
                                   tools="reset, ywheel_zoom, ywheel_pan",
                                   active_scroll='ywheel_pan',
                                   logo=None)
        self.roi_map_plot.title.align = 'center'
        # self.roi_map_plot.title.text_font_style = "italic"
        self.roi_map_plot.title.text_font_size = "15pt"
        self.roi_map_plot.xaxis.axis_line_color = None
        self.roi_map_plot.xaxis.major_tick_line_color = None
        self.roi_map_plot.xaxis.minor_tick_line_color = None
        self.roi_map_plot.xaxis.major_label_text_font_size = "12pt"
        self.roi_map_plot.xgrid.grid_line_color = None
        self.roi_map_plot.ygrid.grid_line_color = None
        self.roi_map_plot.yaxis.visible = False
        self.roi_map_plot.outline_line_color = None
        self.roi_map_plot.y_range = Range1d(-25, 0)
        self.roi_map_plot.border_fill_color = "whitesmoke"
        self.roi_map_plot.min_border_left = 50
        self.roi_map_plot.min_border_bottom = 30
        # self.roi_map_plot.toolbar.autohide = True  # bokeh > than 0.13?

        self.source_map = ColumnDataSource(data={'name': [], 'color': [], 'x': [], 'y': [],
                                                 'x0': [], 'y0': [], 'x1': [], 'y1': []})
        self.roi_map_plot.circle("x", "y", size=12, source=self.source_map, line_color="black", fill_alpha=0.8,
                                 color='color')
        labels = LabelSet(x="x", y="y", text="name", y_offset=8, text_color="#555555",
                          source=self.source_map, text_align='center')
        self.roi_map_plot.add_layout(labels)
        self.roi_map_plot.segment(x0='x0', y0='y0', x1='x1', y1='y1', source=self.source_map, alpha=0.5)
        self.update_roi_map_source_data()
        # self.div_roi_map_table = Div(text='')
        # self.update_roi_map_table_source()

        # columns = [TableColumn(field="institutional_roi", title="Institutional", width=150),
        #            TableColumn(field="physician_roi", title="Physician", width=150),
        #            TableColumn(field="variation_roi", title="Variations", width=500)]
        # self.roi_map_table = DataTable(source=self.source_table, columns=columns, index_position=None, width=1000,
        #                                editable=True)

        self.category_map = {0: self.select_institutional_roi.value,
                             1: self.select_physician.value,
                             2: self.select_physician_roi.value,
                             3: self.select_variation.value}

        self.layout = row(column(self.select_institutional_roi,
                                 Div(text="<hr>", width=widget_width*3),
                                 self.select_physician,
                                 row(self.select_physician_roi, self.select_variation,
                                     self.select_unlinked_institutional_roi),
                                 row(self.select_uncategorized_variation, self.select_ignored_variation),
                                 row(self.ignore_button_roi, self.delete_uncategorized_button_roi,
                                     self.unignore_button_roi, self.delete_ignored_button_roi),
                                 row(self.reload_button_roi, self.save_button_roi),
                                 row(self.update_uncategorized_rois_button,
                                     self.remap_all_rois_for_selected_physician_button, self.remap_all_rois_button),
                                 Div(text="<b>WARNING:</b> Buttons in orange cannot be easily undone.",
                                     width=widget_width*3+100),
                                 Div(text="<hr>", width=widget_width*3),
                                 self.input_text,
                                 row(self.operator, self.category),
                                 self.div_action,
                                 self.action_button),
                          column(row(self.select_plot_display, Spacer(width=75), self.select_merge_physician_roi['a'],
                                     self.select_merge_physician_roi['b'], self.select_merge_physician_roi['button']),
                                 self.roi_map_plot,
                                 Spacer(width=1000, height=100)))

    ###############################
    # Institutional roi functions
    ###############################
    def delete_institutional_roi(self):
        self.db.delete_institutional_roi(self.select_institutional_roi.value)
        new_options = self.db.get_institutional_rois()
        self.select_institutional_roi.options = new_options
        self.select_institutional_roi.value = new_options[0]

    def add_institutional_roi(self):
        new = clean_name(self.input_text.value)
        if len(new) > 50:
            new = new[0:50]
        if new and new not in self.db.get_institutional_rois():
            self.db.add_institutional_roi(new)
            self.select_institutional_roi.options = self.db.get_institutional_rois()
            self.select_institutional_roi.value = new
            self.input_text.value = ''
            self.update_select_unlinked_institutional_roi()

    def select_institutional_roi_change(self, attr, old, new):
        self.update_input_text()

    def update_institutional_roi_select(self):
        new_options = self.db.get_institutional_rois()
        self.select_institutional_roi.options = new_options
        self.select_institutional_roi.value = new_options[0]

    def rename_institutional_roi(self):
        new = clean_name(self.input_text.value)
        self.db.set_institutional_roi(new, self.select_institutional_roi.value)
        self.update_institutional_roi_select()
        self.select_institutional_roi.value = new

    ##############################################
    # Physician ROI functions
    ##############################################
    def update_physician_roi(self, attr, old, new):
        self.select_physician_roi.options = self.db.get_physician_rois(new)
        try:
            self.select_physician_roi.value = self.select_physician_roi.options[0]
        except KeyError:
            pass

    def add_physician_roi(self):
        new = clean_name(self.input_text.value)
        if len(new) > 50:
            new = new[0:50]
        if new and new not in self.db.get_physicians():
            self.db.add_physician_roi(self.select_physician.value, 'uncategorized', new)
            self.select_physician_roi.options = self.db.get_physician_rois(self.select_physician.value)
            self.select_physician_roi.value = new
            self.input_text.value = ''
        elif new in self.db.get_physicians():
            self.input_text.value = ''

    def delete_physician_roi(self):
        if self.select_physician.value not in {'DEFAULT', ''}:
            self.db.delete_physician_roi(self.select_physician.value, self.select_physician_roi.value)
            self.select_physician_roi.options = self.db.get_physician_rois(self.select_physician.value)
            self.select_physician_roi.value = self.db.get_physician_rois(self.select_physician.value)[0]

    def select_physician_roi_change(self, attr, old, new):
        self.update_variation()
        self.update_input_text()
        self.update_roi_map_source_data()
        self.update_select_unlinked_institutional_roi()

    def rename_physician_roi(self):
        new = clean_name(self.input_text.value)
        self.db.set_physician_roi(new, self.select_physician.value, self.select_physician_roi.value)
        self.update_physician_roi_select()
        self.select_physician_roi.value = new

    ##############################
    # Physician functions
    ##############################
    def update_physician_select(self):
        new_options = self.db.get_physicians()
        new_options.sort()
        self.select_physician.options = new_options
        self.select_physician.value = new_options[0]
        self.update_input_text()
        self.update_roi_map_source_data()

    def add_physician(self):
        new = clean_name(self.input_text.value).upper()
        if len(new) > 50:
            new = new[0:50]
        if new and new not in self.db.get_physicians():
            self.input_text.value = ''
            self.db.add_physician(new)
            self.select_physician.options = self.db.get_physicians()
            try:
                self.select_physician.value = new
            except KeyError:
                pass
        elif new in self.db.get_physicians():
            self.input_text.value = ''

    def delete_physician(self):
        if self.select_physician.value != 'DEFAULT':
            self.db.delete_physician(self.select_physician.value)
            new_options = self.db.get_physicians()
            self.select_physician.options = new_options
            self.select_physician.value = new_options[0]

    def select_physician_change(self, attr, old, new):
        self.update_physician_roi_select()
        self.update_input_text()
        self.update_select_unlinked_institutional_roi()
        self.update_uncategorized_variation_select()
        self.update_ignored_variations_select()
        self.update_roi_map_source_data()

    def rename_physician(self):
        new = clean_name(self.input_text.value)
        self.db.set_physician(new, self.select_physician.value)
        self.update_physician_select()
        self.select_physician.value = new

    ###################################
    # Physician ROI Variation functions
    ###################################
    def update_physician_roi_select(self):
        new_options = self.db.get_physician_rois(self.select_physician.value)
        self.select_physician_roi.options = new_options
        self.select_physician_roi.value = new_options[0]
        self.update_input_text()
        self.update_roi_map_source_data()

    def update_variation(self):
        self.select_variation.options = self.db.get_variations(self.select_physician.value,
                                                               self.select_physician_roi.value)
        self.select_variation.value = self.select_variation.options[0]

    def add_variation(self):
        new = clean_name(self.input_text.value)
        if len(new) > 50:
            new = new[0:50]
        if new and new not in self.db.get_all_variations_of_physician(self.select_physician.value):
            self.db.add_variation(self.select_physician.value,
                                  self.select_physician_roi.value,
                                  new)
            self.select_variation.value = new
            self.input_text.value = ''
            self.update_variation()
            self.select_variation.value = new
        elif new in self.db.get_variations(self.select_physician.value,
                                           self.select_physician_roi.value):
            self.input_text.value = ''

    def delete_variation(self):
        if self.select_variation.value != self.select_physician_roi.value:
            self.db.delete_variation(self.select_physician.value, self.select_physician_roi.value,
                                     self.select_variation.value)
            new_options = self.db.get_variations(self.select_physician.value, self.select_physician_roi.value)
            self.select_variation.options = new_options
            self.select_variation.value = new_options[0]

    def select_variation_change(self, attr, old, new):
        self.update_input_text()

    ################
    # Merge functions
    ################
    def update_merge(self):
        physician = self.select_physician.value
        if physician and physician != 'DEFAULT':
            new_options = self.db.get_physician_rois(physician)

            for key in ['a', 'b']:
                self.select_merge_physician_roi[key].options = new_options
                self.select_merge_physician_roi[key].value = new_options[0]

        else:
            for key in ['a', 'b']:
                self.select_merge_physician_roi[key].options = ['']
                self.select_merge_physician_roi[key].value = ''

    def merge_click(self):
        physician = self.select_physician.value
        physician_rois = [self.select_merge_physician_roi[key].value for key in ['a', 'b']]
        final_physician_roi = physician_rois[1]

        if physician_rois[0] != physician_rois[1]:
            self.db.merge_physician_rois(physician, physician_rois, final_physician_roi)

        self.update_roi_map_source_data()
        self.update_save_button_status()

    ################
    # Misc functions
    ################
    def rename_variation(self):
        new = clean_name(self.input_text.value)
        self.db.set_variation(new, self.select_physician.value, self.select_physician_roi.value,
                              self.select_variation.value)
        self.update_variation()
        self.select_variation.value = new

    def update_input_text_title(self):
        self.input_text.title = self.operators[self.operator.active] + " " + self.categories[self.category.active] + ":"
        self.update_action_text()

    def update_input_text_value(self):
        if self.operator.active != 0:
            self.input_text.value = self.category_map[self.category.active]
        elif self.operator.active == 0 and self.category.active == 3:
            self.input_text.value = self.select_uncategorized_variation.value
        else:
            self.input_text.value = ''
            self.update_action_text()

    def operator_change(self, attr, old, new):
        self.update_input_text()
        self.update_action_text()

    def category_change(self, attr, old, new):
        self.update_input_text()
        self.update_action_text()

    def update_input_text(self):
        self.update_input_text_title()
        self.update_input_text_value()

    def update_action_text(self):
        current = {0: self.db.get_institutional_rois(),
                   1: self.db.get_physicians(),
                   2: self.db.get_physician_rois(self.select_physician.value),
                   3: self.db.get_variations(self.select_physician.value, self.select_physician_roi.value)}

        in_value = self.category_map[self.category.active]

        input_text_value = clean_name(self.input_text.value)
        if self.category.active == 1:
            input_text_value = input_text_value.upper()

        if input_text_value == '' or \
                (self.select_physician.value == 'DEFAULT' and self.category.active != 0) or \
                (self.operator.active == 1 and input_text_value not in current[self.category.active]) or \
                (self.operator.active == 2 and input_text_value in current[self.category.active]) or \
                (self.operator.active != 0 and self.category.active == 3 and
                 self.select_variation.value == self.select_physician_roi.value):
            text = "<b>No Action</b>"

        else:

            text = "<b>" + self.input_text.title[:-1] + " </b><i>"
            if self.operator.active == 0:
                text += input_text_value
            else:
                text += in_value
            text += "</i>"
            output = input_text_value

            if self.operator.active == 0:
                if self.category.active == 2:
                    text += " linked to Institutional ROI <i>uncategorized</i>"
                if self.category.active == 3:
                    text += " linked to Physician ROI <i>" + self.select_physician_roi.value + "</i>"

            elif self.operator.active == 2:
                text += " to <i>" + output + "</i>"

        self.div_action.text = text
        self.action_button.label = self.input_text.title[:-1]

    def input_text_change(self, attr, old, new):
        self.update_action_text()

    def reload_db(self):

        self.db = DatabaseROIs()

        self.category.active = 0
        self.operator.active = 0

        self.input_text.value = ''

        new_options = self.db.get_institutional_rois()
        self.select_institutional_roi.options = new_options
        self.select_institutional_roi.value = new_options[0]

        new_options = self.db.get_physicians()
        if len(new_options) > 1:
            new_value = new_options[1]
        else:
            new_value = new_options[0]
        self.select_physician.options = new_options
        self.select_physician.value = new_value

        self.save_button_roi.button_type = 'primary'
        self.save_button_roi.label = 'Map Saved'

        self.update_roi_map_source_data()

    def save_db(self):
        self.db.write_to_file()
        self.save_button_roi.button_type = 'primary'
        self.save_button_roi.label = 'Map Saved'
        # self.update_roi_map_table_source()
        self.update_roi_map_source_data()

    def update_roi_map_source_data(self):
        new_data = self.db.get_all_institutional_roi_visual_coordinates(self.select_physician.value)

        i_roi = new_data['institutional_roi']
        p_roi = new_data['physician_roi']
        b_roi = self.db.branched_institutional_rois[self.select_physician.value]
        if self.select_plot_display.value == 'Linked':
            ignored_roi = [p_roi[i] for i in range(len(i_roi)) if i_roi[i] == 'uncategorized']
        elif self.select_plot_display.value == 'Unlinked':
            ignored_roi = [p_roi[i] for i in range(len(i_roi)) if i_roi[i] != 'uncategorized']
        elif self.select_plot_display.value == 'Branched':
            ignored_roi = [p_roi[i] for i in range(len(i_roi)) if i_roi[i] not in b_roi]
        else:
            ignored_roi = []

        new_data = self.db.get_all_institutional_roi_visual_coordinates(self.select_physician.value,
                                                                        ignored_physician_rois=ignored_roi)

        self.source_map.data = new_data
        self.roi_map_plot.title.text = 'ROI Map for %s' % self.select_physician.value
        self.roi_map_plot.yaxis.bounds = (min(self.source_map.data['y']), max(self.source_map.data['y']))

        self.update_merge()

    def select_plot_display_ticker(self, attr, old, new):
        self.update_roi_map_source_data()

    def execute_button_click(self):
        self.function_map[self.input_text.title.strip(':')]()
        self.update_roi_map_source_data()
        self.update_uncategorized_variation_select()
        self.update_save_button_status()

    def unlinked_institutional_roi_change(self, attr, old, new):
        if self.select_physician.value != 'DEFAULT':
            self.db.set_linked_institutional_roi(new, self.select_physician.value, self.select_physician_roi.value)
            self.update_action_text()
            self.update_roi_map_source_data()

    def update_select_unlinked_institutional_roi(self):
        new_options = self.db.get_unused_institutional_rois(self.select_physician.value)
        new_value = self.db.get_institutional_roi(self.select_physician.value, self.select_physician_roi.value)
        if new_value not in new_options:
            new_options.append(new_value)
            new_options.sort()
        self.select_unlinked_institutional_roi.options = new_options
        self.select_unlinked_institutional_roi.value = new_value

    def update_uncategorized_variation_change(self, attr, old, new):
        self.update_input_text()

    def update_uncategorized_variation_select(self):
        self.uncategorized_variations = self.get_uncategorized_variations(self.select_physician.value)
        new_options = list(self.uncategorized_variations)
        new_options.sort()
        old_value_index = self.select_uncategorized_variation.options.index(self.select_uncategorized_variation.value)
        self.select_uncategorized_variation.options = new_options
        if old_value_index < len(new_options) - 1:
            self.select_uncategorized_variation.value = new_options[old_value_index]
        else:
            try:
                self.select_uncategorized_variation.value = new_options[old_value_index - 1]
            except IndexError:
                self.select_uncategorized_variation.value = new_options[0]
        self.update_input_text()

    def update_ignored_variations_select(self):
        new_options = list(self.get_ignored_variations(self.select_physician.value))
        new_options.sort()
        self.select_ignored_variation.options = new_options
        self.select_ignored_variation.value = new_options[0]

    @staticmethod
    def get_uncategorized_variations(physician):
        if validate_sql_connection(config=load_sql_settings(), verbose=False):
            physician = clean_name(physician).upper()
            condition = "physician_roi = 'uncategorized'"
            cursor_rtn = DVH_SQL().query('dvhs', 'roi_name, study_instance_uid', condition)
            new_uncategorized_variations = {}
            cnx = DVH_SQL()
            for row in cursor_rtn:
                variation = clean_name(str(row[0]))
                study_instance_uid = str(row[1])
                physician_db = cnx.query('plans', 'physician', "study_instance_uid = '" + study_instance_uid + "'")
                if physician_db:
                    physician_db = physician_db[0][0]
                new_uncategorized_variations_keys = list(new_uncategorized_variations)
                if physician == physician_db and variation not in new_uncategorized_variations_keys:
                    new_uncategorized_variations[variation] = {'roi_name': str(row[0]), 'study_instance_uid': str(row[1])}
            if new_uncategorized_variations:
                return new_uncategorized_variations
            else:
                return {' ': ''}
        else:
            return ['Could not connect to SQL']

    @staticmethod
    def get_ignored_variations(physician):
        if validate_sql_connection(config=load_sql_settings(), verbose=False):
            physician = clean_name(physician).upper()
            condition = "physician_roi = 'ignored'"
            cursor_rtn = DVH_SQL().query('dvhs', 'roi_name, study_instance_uid', condition)
            new_ignored_variations = {}
            cnx = DVH_SQL()
            for row in cursor_rtn:
                variation = clean_name(str(row[0]))
                study_instance_uid = str(row[1])
                physician_db = cnx.query('plans', 'physician', "study_instance_uid = '" + study_instance_uid + "'")[0][0]
                new_ignored_variations_keys = list(new_ignored_variations)
                if physician == physician_db and variation not in new_ignored_variations_keys:
                    new_ignored_variations[variation] = {'roi_name': str(row[0]), 'study_instance_uid': str(row[1])}
            if new_ignored_variations:
                return new_ignored_variations
            else:
                return {' ': ''}
        else:
            return ['Could not connect to SQL']

    def delete_uncategorized_dvh(self):
        if self.delete_uncategorized_button_roi.button_type == 'warning':
            if self.select_uncategorized_variation.value != ' ':
                self.delete_uncategorized_button_roi.button_type = 'danger'
                self.delete_uncategorized_button_roi.label = 'Are you sure?'
                self.ignore_button_roi.button_type = 'success'
                self.ignore_button_roi.label = 'Cancel Delete DVH'
        else:
            physician_uids = DVH_SQL().query('Plans', 'study_instance_uid', "physician = '%s'" % self.select_physician.value)
            physician_uids = [uid[0] for uid in physician_uids]
            uids = DVH_SQL().query('DVHs', 'study_instance_uid', "roi_name = '%s'" % self.select_uncategorized_variation.value)
            for uid in uids:
                if uid[0] in physician_uids:
                    DVH_SQL().delete_dvh(self.select_uncategorized_variation.value, uid[0])
            self.update_uncategorized_variation_select()
            self.update_ignored_variations_select()
            self.delete_uncategorized_button_roi.button_type = 'warning'
            self.delete_uncategorized_button_roi.label = 'Delete DVH'
            self.ignore_button_roi.button_type = 'primary'
            self.ignore_button_roi.label = 'Ignore'

    def delete_ignored_dvh(self):
        if self.delete_ignored_button_roi.button_type == 'warning':
            if self.select_ignored_variation.value != ' ':
                self.delete_ignored_button_roi.button_type = 'danger'
                self.delete_ignored_button_roi.label = 'Are you sure?'
                self.unignore_button_roi.button_type = 'success'
                self.unignore_button_roi.label = 'Cancel Delete DVH'
        else:
            physician_uids = DVH_SQL().query('Plans', 'study_instance_uid', "physician = '%s'" % self.select_physician.value)
            physician_uids = [uid[0] for uid in physician_uids]
            uids = DVH_SQL().query('DVHs', 'study_instance_uid', "roi_name = '%s'" % self.select_ignored_variation.value)
            for uid in uids:
                if uid[0] in physician_uids:
                    DVH_SQL().delete_dvh(self.select_ignored_variation.value, uid[0])
            self.update_uncategorized_variation_select()
            self.update_ignored_variations_select()
            self.delete_ignored_button_roi.button_type = 'warning'
            self.delete_ignored_button_roi.label = 'Delete DVH'
            self.unignore_button_roi.button_type = 'primary'
            self.unignore_button_roi.label = 'Unignore'

    def ignore_dvh(self):
        if self.ignore_button_roi.label == 'Cancel Delete DVH':
            self.ignore_button_roi.button_type = 'primary'
            self.ignore_button_roi.label = 'Ignore'
            self.delete_uncategorized_button_roi.button_type = 'warning'
            self.delete_uncategorized_button_roi.label = 'Delete DVH'
        else:
            cnx = DVH_SQL()
            if validate_sql_connection(config=load_sql_settings(), verbose=False):
                condition = "physician_roi = 'uncategorized'"
                cursor_rtn = DVH_SQL().query('dvhs', 'roi_name, study_instance_uid', condition)
                for row in cursor_rtn:
                    variation = str(row[0])
                    study_instance_uid = str(row[1])
                    if clean_name(variation) == self.select_uncategorized_variation.value:
                        cnx.update('dvhs', 'physician_roi', 'ignored', "roi_name = '" + variation +
                                   "' and study_instance_uid = '" + study_instance_uid + "'")
            cnx.close()
            to_be_ignored = self.select_uncategorized_variation.value
            self.update_uncategorized_variation_select()
            self.update_ignored_variations_select()
            self.select_ignored_variation.value = to_be_ignored

    def unignore_dvh(self):
        if self.unignore_button_roi.label == 'Cancel Delete DVH':
            self.unignore_button_roi.button_type = 'primary'
            self.unignore_button_roi.label = 'Ignore'
            self.delete_ignored_button_roi.button_type = 'warning'
            self.delete_ignored_button_roi.label = 'Delete DVH'
        else:
            cnx = DVH_SQL()
            if validate_sql_connection(config=load_sql_settings(), verbose=False):
                condition = "physician_roi = 'ignored'"
                cursor_rtn = DVH_SQL().query('dvhs', 'roi_name, study_instance_uid', condition)
                for row in cursor_rtn:
                    variation = str(row[0])
                    study_instance_uid = str(row[1])
                    if clean_name(variation) == self.select_ignored_variation.value:
                        cnx.update('dvhs', 'physician_roi', 'uncategorized', "roi_name = '" + variation +
                                   "' and study_instance_uid = '" + study_instance_uid + "'")
            cnx.close()
            to_be_unignored = self.select_ignored_variation.value
            self.update_uncategorized_variation_select()
            self.update_ignored_variations_select()
            self.select_uncategorized_variation.value = to_be_unignored

    def remap_rois(self, cursor_rtn, button, *physician):
        if physician:
            physician = physician[0]
        else:
            physician = False

        initial_label = button.label
        cnx = DVH_SQL()
        progress = 0
        complete = len(cursor_rtn)
        for row in cursor_rtn:
            progress += 1
            variation = str(row[0])
            study_instance_uid = str(row[1])
            current_physician = cnx.query('plans', 'physician', "study_instance_uid = '" + study_instance_uid + "'")[0][0]

            if not physician or physician == current_physician:

                new_physician_roi = self.db.get_physician_roi(current_physician, variation)

                if new_physician_roi == 'uncategorized':
                    if clean_name(variation) in self.db.get_institutional_rois():
                        new_institutional_roi = clean_name(variation)
                    else:
                        new_institutional_roi = 'uncategorized'
                else:
                    new_institutional_roi = self.db.get_institutional_roi(current_physician, new_physician_roi)

                condition_str = "roi_name = '" + variation + "' and study_instance_uid = '" + study_instance_uid + "'"
                cnx.update('dvhs', 'physician_roi', new_physician_roi, condition_str)
                cnx.update('dvhs', 'institutional_roi', new_institutional_roi, condition_str)

                percent = int(float(100) * (float(progress) / float(complete)))
                button.label = "Remap progress: " + str(percent) + "%"
        button.label = initial_label

        self.db.write_to_file()
        self.update_uncategorized_variation_select()
        self.update_ignored_variations_select()

    def update_uncategorized_rois_in_db(self):
        cursor_rtn = DVH_SQL().query('dvhs', 'roi_name, study_instance_uid', "physician_roi = 'uncategorized'")
        self.remap_rois(cursor_rtn, self.update_uncategorized_rois_button)

    def remap_all_rois_in_db(self):
        cursor_rtn = DVH_SQL().query('dvhs', 'roi_name, study_instance_uid')
        self.remap_rois(cursor_rtn, self.remap_all_rois_button)

    def remap_all_rois_for_selected_physician(self):
        cursor_rtn = DVH_SQL().query('dvhs', 'roi_name, study_instance_uid')
        self.remap_rois(cursor_rtn, self.remap_all_rois_for_selected_physician_button, self.select_physician.value)

    def update_save_button_status(self):
        self.save_button_roi.button_type = 'success'
        self.save_button_roi.label = 'Map Save Needed'

    # def update_roi_map_table_source(self):
    #     phys_roi = self.db.get_physician_rois(self.select_physician.value)
    #     inst_roi = [self.db.get_institutional_roi(self.select_physician.value, roi) for roi in phys_roi]
    #     vari_roi = [', '.join(self.db.get_variations(self.select_physician.value, roi)) for roi in phys_roi]
    #     self.source_table.data = {'institutional_roi': inst_roi,
    #                               'physician_roi': phys_roi,
    #                               'variation_roi': vari_roi}
    #     self.div_roi_map_table.text = "<b>Currently Saved ROI Map for %s" % self.select_physician.value
