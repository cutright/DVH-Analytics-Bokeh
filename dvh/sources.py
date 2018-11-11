#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
All ColumnDataSource objects for the main DVH Analytics bokeh program
Created on Tue Oct 30 2018
@author: Dan Cutright, PhD
"""

from bokeh.models import ColumnDataSource

dvhs = ColumnDataSource(data=dict(color=[], x=[], y=[], mrn=[]))

selectors = ColumnDataSource(data=dict(row=[1], category1=[''], category2=[''],
                                       group=[''], group_label=[''], not_status=['']))

ranges = ColumnDataSource(data=dict(row=[], category=[], min=[], max=[], min_display=[], max_display=[],
                                    group=[], group_label=[], not_status=[]))

endpoint_defs = ColumnDataSource(data=dict(row=[], output_type=[], input_type=[], input_value=[],
                                           label=[], units_in=[], units_out=[]))

endpoint_view = ColumnDataSource(data=dict(mrn=[], group=[], roi_name=[], ep1=[], ep2=[], ep3=[], ep4=[],
                                           ep5=[], ep6=[], ep7=[], ep8=[], ep9=[], ep10=[]))

patch_1 = ColumnDataSource(data=dict(x_patch=[], y_patch=[]))
patch_2 = ColumnDataSource(data=dict(x_patch=[], y_patch=[]))

stats_1 = ColumnDataSource(data=dict(x=[], min=[], q1=[], mean=[], median=[], q3=[], max=[]))
stats_2 = ColumnDataSource(data=dict(x=[], min=[], q1=[], mean=[], median=[], q3=[], max=[]))

tv = ColumnDataSource(data=dict(x=[], y=[]))

rad_bio = ColumnDataSource(data=dict(mrn=[], uid=[], roi_name=[], ptv_overlap=[], roi_type=[], rx_dose=[],
                                     fxs=[], fx_dose=[], eud_a=[], gamma_50=[], td_tcp=[], eud=[],
                                     ntcp_tcp=[]))

time_1 = ColumnDataSource(data=dict(x=[], y=[], mrn=[]))
time_2 = ColumnDataSource(data=dict(x=[], y=[], mrn=[]))
time_csv = ColumnDataSource(data=dict(text=[]))

time_trend_1 = ColumnDataSource(data=dict(x=[], y=[], w=[], mrn=[]))
time_trend_2 = ColumnDataSource(data=dict(x=[], y=[], w=[], mrn=[]))

time_collapsed = ColumnDataSource(data=dict(x=[], y=[], w=[], mrn=[]))

time_bound_1 = ColumnDataSource(data=dict(x=[], upper=[], avg=[], lower=[], mrn=[]))
time_bound_2 = ColumnDataSource(data=dict(x=[], upper=[], avg=[], lower=[], mrn=[]))

time_patch_1 = ColumnDataSource(data=dict(x=[], y=[]))
time_patch_2 = ColumnDataSource(data=dict(x=[], y=[]))

histogram_1 = ColumnDataSource(data=dict(x=[], top=[], width=[]))
histogram_2 = ColumnDataSource(data=dict(x=[], top=[], width=[]))

corr_matrix_line = ColumnDataSource(data=dict(x=[], y=[]))
corr_chart_1 = ColumnDataSource(data=dict(x=[], y=[], mrn=[]))
corr_chart_2 = ColumnDataSource(data=dict(x=[], y=[], mrn=[]))
corr_trend_1 = ColumnDataSource(data=dict(x=[], y=[]))
corr_trend_2 = ColumnDataSource(data=dict(x=[], y=[]))

CORR_CHART_STATS_ROW_NAMES = ['slope', 'y-intercept', 'R-squared', 'p-value', 'std. err.', 'sample size']
corr_chart_stats = ColumnDataSource(data=dict(stat=CORR_CHART_STATS_ROW_NAMES,  group_1=[''] * 6, group_2=[''] * 6))

multi_var_include = ColumnDataSource(data=dict(var_name=[]))
multi_var_coeff_results_1 = ColumnDataSource(data=dict(var_name=[], coeff=[], coeff_str=[], p=[], p_str=[]))
multi_var_model_results_1 = ColumnDataSource(data=dict(model_p=[], model_p_str=[], r_sq=[], r_sq_str=[], y_var=[]))
multi_var_coeff_results_2 = ColumnDataSource(data=dict(var_name=[], coeff=[], coeff_str=[], p=[], p_str=[]))
multi_var_model_results_2 = ColumnDataSource(data=dict(model_p=[], model_p_str=[], r_sq=[], r_sq_str=[], y_var=[]))

mlc_viewer = ColumnDataSource(data=dict(top=[], bottom=[], left=[], right=[], color=[]))

residual_chart_1 = ColumnDataSource(data=dict(x=[], y=[], mrn=[], db_value=[]))
residual_chart_2 = ColumnDataSource(data=dict(x=[], y=[], mrn=[], db_value=[]))

emami = ColumnDataSource(data=dict(roi=['Brain', 'Brainstem', 'Optic Chiasm', 'Colon', 'Ear (mid/ext)',
                                        'Ear (mid/ext)', 'Esophagus', 'Heart', 'Kidney', 'Lens', 'Liver',
                                        'Lung', 'Optic Nerve', 'Retina'],
                                   ep=['Necrosis', 'Necrosis', 'Blindness', 'Obstruction/Perforation',
                                       'Acute serous otitus', 'Chronic serous otitus', 'Peforation',
                                       'Pericarditus', 'Nephritis', 'Cataract', 'Liver Failure',
                                       'Pneumonitis', 'Blindness', 'Blindness'],
                                   eud_a=[5, 7, 25, 6, 31, 31, 19, 3, 1, 3, 3, 1, 25, 15],
                                   gamma_50=[3, 3, 3, 4, 3, 4, 4, 3, 3, 1, 3, 2, 3, 2],
                                   td_tcd=[60, 65, 65, 55, 40, 65, 68, 50, 28, 18, 40, 24.5, 65, 65]))

endpoint_calcs = ColumnDataSource(data=dict())
beams = ColumnDataSource(data=dict())
plans = ColumnDataSource(data=dict())
rxs = ColumnDataSource(data=dict())
mlc_summary = ColumnDataSource(data=dict())

roi1_viewer = ColumnDataSource(data=dict(x=[], y=[]))
roi2_viewer = ColumnDataSource(data=dict(x=[], y=[]))
roi3_viewer = ColumnDataSource(data=dict(x=[], y=[]))
roi4_viewer = ColumnDataSource(data=dict(x=[], y=[]))
roi5_viewer = ColumnDataSource(data=dict(x=[], y=[]))

correlation_1_pos = ColumnDataSource(data=dict(x=[], y=[], x_name=[], y_name=[], color=[], alpha=[], r=[], p=[],
                                               group=[], size=[], x_normality=[], y_normality=[]))
correlation_1_neg = ColumnDataSource(data=dict(x=[], y=[], x_name=[], y_name=[], color=[], alpha=[], r=[], p=[],
                                               group=[], size=[], x_normality=[], y_normality=[]))
correlation_2_pos = ColumnDataSource(data=dict(x=[], y=[], x_name=[], y_name=[], color=[], alpha=[], r=[], p=[],
                                               group=[], size=[], x_normality=[], y_normality=[]))
correlation_2_neg = ColumnDataSource(data=dict(x=[], y=[], x_name=[], y_name=[], color=[], alpha=[], r=[], p=[],
                                               group=[], size=[], x_normality=[], y_normality=[]))
