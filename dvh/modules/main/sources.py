#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
All ColumnDataSource objects for the main DVH Analytics bokeh program
Created on Tue Oct 30 2018
@author: Dan Cutright, PhD
"""

from bokeh.models import ColumnDataSource


class Sources:
    def __init__(self):
        self.dvhs = ColumnDataSource(data=dict(color=[], x=[], y=[], mrn=[]))
        self.query_csv_anon_dvhs = ColumnDataSource(data=dict(text=[]))
        self.query_csv_all = ColumnDataSource(data=dict(text=[]))
        self.query_csv_lite = ColumnDataSource(data=dict(text=[]))
        self.query_csv_dvhs = ColumnDataSource(data=dict(text=[]))

        self.selectors = ColumnDataSource(data=dict(row=[1], category1=[''], category2=[''],
                                               group=[''], group_label=[''], not_status=['']))

        self.ranges = ColumnDataSource(data=dict(row=[], category=[], min=[], max=[], min_display=[], max_display=[],
                                            group=[], group_label=[], not_status=[]))

        self.endpoint_defs = ColumnDataSource(data=dict(row=[], output_type=[], input_type=[], input_value=[],
                                                   label=[], units_in=[], units_out=[]))

        self.endpoint_view = ColumnDataSource(data=dict(mrn=[], group=[], roi_name=[], ep1=[], ep2=[], ep3=[], ep4=[],
                                                   ep5=[], ep6=[], ep7=[], ep8=[], ep9=[], ep10=[]))
        self.endpoints_csv = ColumnDataSource(data=dict(text=[]))

        self.patch_1 = ColumnDataSource(data=dict(x_patch=[], y_patch=[]))
        self.patch_2 = ColumnDataSource(data=dict(x_patch=[], y_patch=[]))

        self.stats_1 = ColumnDataSource(data=dict(x=[], min=[], q1=[], mean=[], median=[], q3=[], max=[]))
        self.stats_2 = ColumnDataSource(data=dict(x=[], min=[], q1=[], mean=[], median=[], q3=[], max=[]))

        self.tv = ColumnDataSource(data=dict(x=[], y=[]))

        self.rad_bio = ColumnDataSource(data=dict(mrn=[], uid=[], roi_name=[], ptv_overlap=[], roi_type=[], rx_dose=[],
                                             fxs=[], fx_dose=[], eud_a=[], gamma_50=[], td_tcp=[], eud=[],
                                             ntcp_tcp=[]))

        self.time_1 = ColumnDataSource(data=dict(x=[], y=[], mrn=[]))
        self.time_2 = ColumnDataSource(data=dict(x=[], y=[], mrn=[]))
        self.time_csv = ColumnDataSource(data=dict(text=[]))

        self.time_trend_1 = ColumnDataSource(data=dict(x=[], y=[], w=[], mrn=[]))
        self.time_trend_2 = ColumnDataSource(data=dict(x=[], y=[], w=[], mrn=[]))

        self.time_collapsed = ColumnDataSource(data=dict(x=[], y=[], w=[], mrn=[]))

        self.time_bound_1 = ColumnDataSource(data=dict(x=[], upper=[], avg=[], lower=[], mrn=[]))
        self.time_bound_2 = ColumnDataSource(data=dict(x=[], upper=[], avg=[], lower=[], mrn=[]))

        self.time_patch_1 = ColumnDataSource(data=dict(x=[], y=[]))
        self.time_patch_2 = ColumnDataSource(data=dict(x=[], y=[]))

        self.histogram_1 = ColumnDataSource(data=dict(x=[], top=[], width=[]))
        self.histogram_2 = ColumnDataSource(data=dict(x=[], top=[], width=[]))

        self.corr_matrix_line = ColumnDataSource(data=dict(x=[], y=[]))
        self.corr_chart_1 = ColumnDataSource(data=dict(x=[], y=[], mrn=[]))
        self.corr_chart_2 = ColumnDataSource(data=dict(x=[], y=[], mrn=[]))
        self.corr_trend_1 = ColumnDataSource(data=dict(x=[], y=[]))
        self.corr_trend_2 = ColumnDataSource(data=dict(x=[], y=[]))

        self.CORR_CHART_STATS_ROW_NAMES = ['slope', 'y-intercept', 'R-squared', 'p-value', 'std. err.', 'sample size']
        self.corr_chart_stats = ColumnDataSource(data=dict(stat=self.CORR_CHART_STATS_ROW_NAMES,  group_1=[''] * 6, group_2=[''] * 6))

        self.multi_var_include = ColumnDataSource(data=dict(var_name=[]))
        self.multi_var_coeff_results_1 = ColumnDataSource(data=dict(var_name=[], coeff=[], coeff_str=[], p=[], p_str=[]))
        self.multi_var_model_results_1 = ColumnDataSource(data=dict(model_p=[], model_p_str=[], r_sq=[], r_sq_str=[], y_var=[]))
        self.multi_var_coeff_results_2 = ColumnDataSource(data=dict(var_name=[], coeff=[], coeff_str=[], p=[], p_str=[]))
        self.multi_var_model_results_2 = ColumnDataSource(data=dict(model_p=[], model_p_str=[], r_sq=[], r_sq_str=[], y_var=[]))

        self.mlc_viewer = ColumnDataSource(data=dict(top=[], bottom=[], left=[], right=[], color=[]))

        self.residual_chart_1 = ColumnDataSource(data=dict(x=[], y=[], mrn=[], db_value=[]))
        self.residual_chart_2 = ColumnDataSource(data=dict(x=[], y=[], mrn=[], db_value=[]))

        self.emami = ColumnDataSource(data=dict(roi=['Brain', 'Brainstem', 'Optic Chiasm', 'Colon', 'Ear (mid/ext)',
                                                'Ear (mid/ext)', 'Esophagus', 'Heart', 'Kidney', 'Lens', 'Liver',
                                                'Lung', 'Optic Nerve', 'Retina'],
                                           ep=['Necrosis', 'Necrosis', 'Blindness', 'Obstruction/Perforation',
                                               'Acute serous otitus', 'Chronic serous otitus', 'Peforation',
                                               'Pericarditus', 'Nephritis', 'Cataract', 'Liver Failure',
                                               'Pneumonitis', 'Blindness', 'Blindness'],
                                           eud_a=[5, 7, 25, 6, 31, 31, 19, 3, 1, 3, 3, 1, 25, 15],
                                           gamma_50=[3, 3, 3, 4, 3, 4, 4, 3, 3, 1, 3, 2, 3, 2],
                                           td_tcd=[60, 65, 65, 55, 40, 65, 68, 50, 28, 18, 40, 24.5, 65, 65]))

        self.endpoint_calcs = ColumnDataSource(data=dict())
        self.beams = ColumnDataSource(data=dict())
        self.plans = ColumnDataSource(data=dict())
        self.rxs = ColumnDataSource(data=dict())
        self.mlc_summary = ColumnDataSource(data=dict())

        self.roi1_viewer = ColumnDataSource(data=dict(x=[], y=[]))
        self.roi2_viewer = ColumnDataSource(data=dict(x=[], y=[]))
        self.roi3_viewer = ColumnDataSource(data=dict(x=[], y=[]))
        self.roi4_viewer = ColumnDataSource(data=dict(x=[], y=[]))
        self.roi5_viewer = ColumnDataSource(data=dict(x=[], y=[]))

        self.correlation_1_pos = ColumnDataSource(data=dict(x=[], y=[], x_name=[], y_name=[], color=[], alpha=[], r=[], p=[],
                                                       group=[], size=[], x_normality=[], y_normality=[]))
        self.correlation_1_neg = ColumnDataSource(data=dict(x=[], y=[], x_name=[], y_name=[], color=[], alpha=[], r=[], p=[],
                                                       group=[], size=[], x_normality=[], y_normality=[]))
        self.correlation_2_pos = ColumnDataSource(data=dict(x=[], y=[], x_name=[], y_name=[], color=[], alpha=[], r=[], p=[],
                                                       group=[], size=[], x_normality=[], y_normality=[]))
        self.correlation_2_neg = ColumnDataSource(data=dict(x=[], y=[], x_name=[], y_name=[], color=[], alpha=[], r=[], p=[],
                                                       group=[], size=[], x_normality=[], y_normality=[]))
        self.correlation_csv = ColumnDataSource(data=dict(text=[]))
