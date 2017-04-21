from bokeh.layouts import column, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, DataTable, TableColumn, TextInput
from bokeh.io import curdoc

from Analysis_Tools import *

source = ColumnDataSource(data=dict())
cnx = DVH_SQL()


def update():
    condition = "institutional_roi = 'brain' and max_dose > " + str(slider.value)
    current = DVH(cnx, dvh_condition=condition)
    mrn = []
    institutional_roi = []
    roi_name = []
    max_dose = []
    for i in range(0, current.count):
        mrn.append(current.mrn[i])
        roi_name.append(current.roi_name[i])
        institutional_roi.append(current.roi_institutional[i])
        max_dose.append(current.max_dose[i])
    source.data = {
        'mrn'             : mrn,
        'institutional_roi': institutional_roi,
        'roi_name'           : roi_name,
        'max_dose' : max_dose,
    }


def update_text():
    condition = query_text.value
    print condition
    current = DVH(cnx, dvh_condition=condition)
    mrn = []
    institutional_roi = []
    roi_name = []
    max_dose = []
    for i in range(0, current.count):
        mrn.append(current.mrn[i])
        roi_name.append(current.roi_name[i])
        institutional_roi.append(current.roi_institutional[i])
        max_dose.append(current.max_dose[i])
    source.data = {
        'mrn'             : mrn,
        'institutional_roi': institutional_roi,
        'roi_name'           : roi_name,
        'max_dose' : max_dose,
    }


slider = Slider(title="Max Dose", start=0, end=100, value=30, step=1)
slider.on_change('value', lambda attr, old, new: update())

query_text = TextInput(placeholder="e.g., institutional_roi = 'spinal_cord'")
query_text.on_change('value', lambda attr, old, new: update_text())

columns = [
    TableColumn(field="mrn", title="MRN"),
    TableColumn(field="roi_name", title="ROI Name"),
    TableColumn(field="max_dose", title="Max ROI Dose")
]

data_table = DataTable(source=source, columns=columns, width=800)

controls = widgetbox(slider)
text_in = widgetbox(query_text)
table = widgetbox(data_table)

curdoc().add_root(column(controls, text_in, table))
curdoc().title = "Export CSV"

update()
