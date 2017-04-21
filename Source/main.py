from os.path import dirname, join

from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Slider, Button, DataTable, TableColumn, NumberFormatter
from bokeh.io import curdoc

from Analysis_Tools import *

source = ColumnDataSource(data=dict())


def update():
    condition = "institutional_roi = 'spinal cord' and max_dose > " + str(slider.value)
    current = DVH(dvh_condition=condition)
    current_mrn = []
    current_roi = []
    current_max_dose = []
    for i in range(0, current.count):
        current_mrn.append(current.mrn[i])
        current_roi.append(current.roi_name[i])
        current_max_dose.append(str(current.max_dose[i]))
    source.data = {
        'mrn'             : current_mrn,
        'roi_name'           : current_roi,
        'max_dose' : current_max_dose,
    }

slider = Slider(title="Max Dose", start=0, end=100, value=30, step=1)
slider.on_change('value', lambda attr, old, new: update())

button = Button(label="Download", button_type="success")
button.callback = CustomJS(args=dict(source=source), code=open(join(dirname(__file__), "download.js")).read())


columns = [
    TableColumn(field="mrn", title="MRN"),
    TableColumn(field="roi_name", title="ROI Name"),
    TableColumn(field="max_dose", title="Max ROI Dose")
]

data_table = DataTable(source=source, columns=columns, width=800)

controls = widgetbox(slider, button)
table = widgetbox(data_table)

curdoc().add_root(row(controls, table))
curdoc().title = "Export CSV"

update()
