from bokeh.layouts import column, row
from bokeh.models import Spacer
from bokeh.models.widgets import Div
from ..tools.io.preferences.options import load_options


class PlanningData:
    def __init__(self, custom_title, data_tables):
        self.layout = column(Div(text="<b>DVH Analytics v%s</b>" % load_options(return_attr='VERSION')),
                             row(custom_title['1']['planning'], Spacer(width=50), custom_title['2']['planning']),
                             Div(text="<b>Rxs</b>", width=1000), data_tables.rxs,
                             Div(text="<b>Plans</b>", width=1200), data_tables.plans,
                             Div(text="<b>Beams</b>", width=1500), data_tables.beams,
                             Div(text="<b>Beams Continued</b>", width=1500), data_tables.beams2)
