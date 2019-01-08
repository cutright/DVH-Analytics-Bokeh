#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
All DataTable objects and functions for the main DVH Analytics bokeh program
Created on Sun Nov 4 2018
@author: Dan Cutright, PhD
"""

from bokeh.models.widgets import DataTable
from .columns import Columns


class DataTables:
    def __init__(self, sources):

        columns = Columns()

        self.selection_filter = DataTable(source=sources.selectors,
                                          columns=columns.selection_filter, width=1000, height=150)

        self.range_filter = DataTable(source=sources.ranges,
                                      columns=columns.range_filter, width=1000, height=150)

        self.ep = DataTable(source=sources.endpoint_defs, columns=columns.ep_data, width=300, height=150)

        self.dvhs = DataTable(source=sources.dvhs, columns=columns.dvhs, width=1200, editable=True)
        self.beams = DataTable(source=sources.beams, columns=columns.beams, width=1300, editable=True)
        self.beams2 = DataTable(source=sources.beams, columns=columns.beams2, width=1300, editable=True)
        self.plans = DataTable(source=sources.plans, columns=columns.plans, width=1300, editable=True)
        self.rxs = DataTable(source=sources.rxs, columns=columns.rxs, width=1300, editable=True)
        self.endpoints = DataTable(source=sources.endpoint_view, columns=columns.endpoints, width=1200, editable=True)

        self.corr_chart = DataTable(source=sources.corr_chart_stats, columns=columns.corr_chart, editable=True,
                                    height=180, width=300)

        self.multi_var_include = DataTable(source=sources.multi_var_include, columns=columns.multi_var_include,
                                           height=175, width=275)

        self.multi_var_model_1 = DataTable(source=sources.multi_var_coeff_results_1, columns=columns.multi_var_model_1,
                                           editable=True, height=200)

        self.multi_var_coeff_1 = DataTable(source=sources.multi_var_model_results_1, columns=columns.multi_var_coeff_1,
                                           editable=True, height=60)

        self.multi_var_model_2 = DataTable(source=sources.multi_var_coeff_results_2, columns=columns.multi_var_model_2,
                                           editable=True, height=200)

        self.multi_var_coeff_2 = DataTable(source=sources.multi_var_model_results_2, columns=columns.multi_var_coeff_2,
                                           editable=True, height=60)

        self.rad_bio = DataTable(source=sources.rad_bio, columns=columns.rad_bio, editable=False, width=1100)

        self.emami = DataTable(source=sources.emami, columns=columns.emami, editable=False, width=1100)

        self.mlc_viewer = DataTable(source=sources.mlc_summary, columns=columns.mlc_viewer, editable=False,
                                    width=700, height=425)

        for key, value in self.__dict__.items():
            getattr(self, key).index_position = None
