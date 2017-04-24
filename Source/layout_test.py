from bokeh.layouts import layout
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Select, Paragraph, Button, Tabs, Panel, RangeSlider, PreText
from bokeh.plotting import figure
from bokeh.io import curdoc
from ROI_Name_Manager import *
from DVH_SQL import *

db_rois = DatabaseROIs()
source = ColumnDataSource(data=dict())
source_stat = ColumnDataSource(data=dict())
query_row_count = 0
query_row = {}
query_row_type = []

# Categories map of dropdown values, SQL column, and SQL table
selector_categories = {'Institutional ROI': {'var_name': 'institutional_roi', 'table': 'DVHs'},
                       'Physician ROI': {'var_name': 'physician_roi', 'table': 'DVHs'},
                       'ROI Type': {'var_name': 'roi_type', 'table': 'DVHs'},
                       'Beam Energy': {'var_name': 'beam_energy', 'table': 'Beams'},
                       'Beam Type': {'var_name': 'beam_type', 'table': 'Beams'},
                       'Gantry Rotation Direction': {'var_name': 'gantry_rot_dir', 'table': 'Beams'},
                       'Radiation Type': {'var_name': 'radiation_type', 'table': 'Beams'},
                       'Patient Orientation': {'var_name': 'patient_orientation', 'table': 'Plans'},
                       'Patient Sex': {'var_name': 'patient_sex', 'table': 'Plans'},
                       'Physician': {'var_name': 'physician', 'table': 'Plans'},
                       'Tx Modality': {'var_name': 'tx_modality', 'table': 'Plans'},
                       'Tx Site': {'var_name': 'tx_site', 'table': 'Plans'},
                       'Normalization': {'var_name': 'normalization_method', 'table': 'Rxs'}}

slider_categories = {'Age': {'var_name': 'age', 'table': 'Plans'},
                     'Birth Date': {'var_name': 'birth_date', 'table': 'Plans'},
                     'Planned Fractions': {'var_name': 'fxs', 'table': 'Plans'},
                     'Rx Dose': {'var_name': 'rx_dose', 'table': 'Plans'},
                     'Rx Isodose': {'var_name': 'rx_percent', 'table': 'Rxs'},
                     'Simulation Date': {'var_name': 'sim_study_date', 'table': 'Plans'},
                     'Total Plan MU': {'var_name': 'total_mu', 'table': 'Plans'},
                     'Fraction Dose': {'var_name': 'fx_dose', 'table': 'Rxs'},
                     'Beam Dose': {'var_name': 'beam_dose', 'table': 'Beams'},
                     'Beam MU': {'var_name': 'beam_mu', 'table': 'Beams'},
                     'Collimator Angle': {'var_name': 'collimator_angle', 'table': 'Beams'},
                     'Couch Angle': {'var_name': 'couch_angle', 'table': 'Beams'},
                     'Gantry Start Angle': {'var_name': 'gantry_start', 'table': 'Beams'},
                     'Gantry End Angle': {'var_name': 'gantry_end', 'table': 'Beams'},
                     'SSD': {'var_name': 'ssd', 'table': 'Beams'},
                     'ROI Min Dose': {'var_name': 'min_dose', 'table': 'DVHs'},
                     'ROI Mean Dose': {'var_name': 'mean_dose', 'table': 'DVHs'},
                     'ROI Max Dose': {'var_name': 'max_dose', 'table': 'DVHs'},
                     'ROI Volume': {'var_name': 'volume', 'table': 'DVHs'}}


def update():
    pass


def button_add_selector_row():
    global query_row_count, query_row_type
    query_row[query_row_count] = AddSelectorRow(query_row_count)
    layout_query.children.append(query_row[query_row_count].row)
    query_row_count += 1
    query_row_type.append('selector')


def button_add_slider_row():
    global query_row_count
    query_row[query_row_count] = AddSliderRow(query_row_count)
    layout_query.children.append(query_row[query_row_count].row)
    query_row_count += 1
    query_row_type.append('slider')


def button_del_row():
    global query_row_count
    del(layout_query.children[query_row_count])
    query_row_count -= 1
    query_row_type.pop()


def update_query_text():
    global query_row_count, query_row_type, query_row
    full_query = []
    for i in range(0, query_row_count):
        if query_row_type[i] == 'selector':
            var_name = selector_categories[query_row[i].select_category.value]['var_name']
            value = query_row[i].select_value.value
            full_query.append(var_name + " = '" + value + "'")
        else:
            print query_row[i].slider.range
            var_name = slider_categories[query_row[i].select_category.value]['var_name']
            full_query.append(var_name)
    full_query = ' and '.join(full_query)
    full_query += ';'
    query.text = full_query


class AddSelectorRow:
    def __init__(self, current_row):
        # Plans Tab Widgets
        # Category Dropdown
        self.category_options = selector_categories.keys()
        self.category_options.sort()
        self.select_category = Select(value=self.category_options[0], options=self.category_options)
        self.select_category.on_change('value', self.update_selector_values)

        # Value Dropdown
        self.sql_table = selector_categories[self.select_category.value]['table']
        self.var_name = selector_categories[self.select_category.value]['var_name']
        self.values = DVH_SQL().get_unique_values(self.sql_table, self.var_name)
        self.select_value = Select(value=self.values[0], options=self.values)

        self.add_selector_button = Button(label="Add Selector", button_type="default", width=100)
        self.add_selector_button.on_click(button_add_selector_row)
        self.add_slider_button = Button(label="Add Slider", button_type="primary", width=100)
        self.add_slider_button.on_click(button_add_slider_row)
        self.delete_last_row = Button(label="Delete", button_type="warning", width=100)
        self.delete_last_row.on_click(button_del_row)

        self.row = layout([[self.select_category,
                            self.select_value,
                            self.add_selector_button,
                            self.add_slider_button,
                            self.delete_last_row]])

    def update_selector_values(self, attrname, old, new):
        table_new = selector_categories[self.select_category.value]['table']
        var_name_new = selector_categories[new]['var_name']
        self.select_value.options = DVH_SQL().get_unique_values(table_new, var_name_new)


class AddSliderRow:
    def __init__(self, current_row):
        # Plans Tab Widgets
        # Category Dropdown
        self.category_options = slider_categories.keys()
        self.category_options.sort()
        self.select_category = Select(value=self.category_options[0], options=self.category_options)
        self.select_category.on_change('value', self.update_slider_values)

        # Range slider
        self.sql_table = slider_categories[self.select_category.value]['table']
        self.var_name = slider_categories[self.select_category.value]['var_name']
        self.min_value = DVH_SQL().get_min_value(self.sql_table, self.var_name)
        if not self.min_value:
            self.min_value = 0
        self.max_value = DVH_SQL().get_max_value(self.sql_table, self.var_name)
        if not self.max_value:
            self.max_value = 100
        self.slider = RangeSlider(start=round(self.min_value, 1),
                                  end=round(self.max_value, 1),
                                  range=(self.min_value, self.max_value),
                                  step=0.1)

        self.add_selector_button = Button(label="Add Selector", button_type="default", width=100)
        self.add_selector_button.on_click(button_add_selector_row)
        self.add_slider_button = Button(label="Add Slider", button_type="primary", width=100)
        self.add_slider_button.on_click(button_add_slider_row)
        self.delete_last_row = Button(label="Delete", button_type="warning", width=100)
        self.delete_last_row.on_click(button_del_row)

        self.row = layout([[self.select_category,
                            self.slider,
                            self.add_selector_button,
                            self.add_slider_button,
                            self.delete_last_row]])

    def update_slider_values(self, attrname, old, new):
        table_new = slider_categories[new]['table']
        var_name_new = slider_categories[new]['var_name']
        min_value_new = DVH_SQL().get_min_value(table_new, var_name_new)
        print min_value_new
        if not min_value_new:
            min_value_new = 0
        max_value_new = DVH_SQL().get_max_value(table_new, var_name_new)
        if not max_value_new:
            max_value_new = 100
        self.slider.start = round(min_value_new, 1)
        self.slider.end = round(max_value_new, 1)
        self.slider.value = round(min_value_new, 1)


# set up layout
dvh_plots = figure(plot_width=700, plot_height=400)
update_query_button = Button(label="Update", button_type="success", width=100)
update_query_button.on_click(update_query_text)
query = Paragraph(text="This will contain the final SQL Query", width=1000)
layout_data = layout([[query], [update_query_button], [dvh_plots]])

main_pre_text = PreText(text="Add selectors and sliders to design your query", width=500)
main_add_selector_button = Button(label="Add Selector", button_type="default", width=200)
main_add_selector_button.on_click(button_add_selector_row)
main_add_slider_button = Button(label="Add Slider", button_type="primary", width=200)
main_add_slider_button.on_click(button_add_slider_row)
layout_query = layout([[main_pre_text, main_add_selector_button, main_add_slider_button]])

tab_query = Panel(child=layout_query, title="Query")
tab_data = Panel(child=layout_data, title="Data")
tabs = Tabs(tabs=[tab_query, tab_data])

curdoc().add_root(tabs)
curdoc().title = "Live Free or DICOM"

update()
