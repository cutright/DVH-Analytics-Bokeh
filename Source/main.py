from bokeh.layouts import column, row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, DataTable, TableColumn, TextInput, Select
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


slider = Slider(title="Max Dose", start=0, end=100, value=30, step=1)
slider.on_change('value', lambda attr, old, new: update())

select1 = Select(title="Category", options=["mrn", "institutional_roi", "max_dose"])
select2 = Select(title="Operator", options=["=", "<", ">", "like"])
query_text = TextInput(title="condition", placeholder="enter condition")

columns = [
    TableColumn(field="mrn", title="MRN"),
    TableColumn(field="roi_name", title="ROI Name"),
    TableColumn(field="max_dose", title="Max ROI Dose")
]

data_table = DataTable(source=source, columns=columns, width=800)

controls = widgetbox(slider)
table = widgetbox(data_table)
query = widgetbox(select1, select2, query_text)

curdoc().add_root(column(query, controls, table))
curdoc().title = "Live Free or DICOM"

update()
