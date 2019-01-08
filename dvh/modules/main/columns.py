#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
All lists of TableColumn objects for DVH Analytics main Bokeh program
Created on Tue Oct 30 2018
@author: Dan Cutright, PhD
"""

from bokeh.models.widgets import TableColumn, NumberFormatter
from ..tools.io.preferences.options import load_options


class Columns:
    def __init__(self):
        self.selection_filter = [TableColumn(field="row", title="Row", width=60),
                                 TableColumn(field="category1", title="Selection Category 1", width=280),
                                 TableColumn(field="category2", title="Selection Category 2", width=280),
                                 TableColumn(field="group_label", title="Group", width=170),
                                 TableColumn(field="not_status", title="Apply Not Operator", width=150)]

        self.range_filter = [TableColumn(field="row", title="Row", width=60),
                             TableColumn(field="category", title="Range Category", width=230),
                             TableColumn(field="min_display", title="Min", width=170),
                             TableColumn(field="max_display", title="Max", width=170),
                             TableColumn(field="group_label", title="Group", width=180),
                             TableColumn(field="not_status", title="Apply Not Operator", width=150)]

        self.dvhs = [TableColumn(field="mrn", title="MRN / Stat", width=175),
                     TableColumn(field="group", title="Group", width=175),
                     TableColumn(field="roi_name", title="ROI Name"),
                     TableColumn(field="roi_type", title="ROI Type", width=80),
                     TableColumn(field="rx_dose", title="Rx Dose", width=100, formatter=NumberFormatter(format="0.00")),
                     TableColumn(field="volume", title="Volume", width=80, formatter=NumberFormatter(format="0.00")),
                     TableColumn(field="min_dose", title="Min Dose", width=80, formatter=NumberFormatter(format="0.00")),
                     TableColumn(field="mean_dose", title="Mean Dose", width=80, formatter=NumberFormatter(format="0.00")),
                     TableColumn(field="max_dose", title="Max Dose", width=80, formatter=NumberFormatter(format="0.00")),
                     TableColumn(field="dist_to_ptv_min", title="Dist to PTV", width=80, formatter=NumberFormatter(format="0.0")),
                     TableColumn(field="ptv_overlap", title="PTV Overlap", width=80, formatter=NumberFormatter(format="0.0"))]

        self.endpoints = [TableColumn(field="mrn", title="MRN / Stat", width=175),
                          TableColumn(field="group", title="Group", width=175),
                          TableColumn(field="roi_name", title="ROI Name")]
        for i in range(load_options(return_attr='ENDPOINT_COUNT')):
            self.endpoints.append(TableColumn(field="ep%s" % (i+1), title="ep%s" % (i+1), width=80,
                                              formatter=NumberFormatter(format="0.00")))

        self.ep_data = [TableColumn(field="row", title="Row", width=60),
                        TableColumn(field="label", title="Endpoint", width=180),
                        TableColumn(field="units_out", title="Units", width=60)]

        self.rad_bio = [TableColumn(field="mrn", title="MRN", width=150),
                        TableColumn(field="group", title="Group", width=100),
                        TableColumn(field="roi_name", title="ROI Name", width=250),
                        TableColumn(field="ptv_overlap", title="PTV Overlap",  width=150),
                        TableColumn(field="roi_type", title="ROI Type", width=100),
                        TableColumn(field="rx_dose", title="Rx Dose", width=100, formatter=NumberFormatter(format="0.00")),
                        TableColumn(field="fxs", title="Total Fxs", width=100),
                        TableColumn(field="fx_dose", title="Fx Dose", width=100, formatter=NumberFormatter(format="0.00")),
                        TableColumn(field="eud_a", title="a", width=50),
                        TableColumn(field="gamma_50", title=u"\u03b3_50", width=75),
                        TableColumn(field="td_tcd", title="TD or TCD", width=150),
                        TableColumn(field="eud", title="EUD", width=75, formatter=NumberFormatter(format="0.00")),
                        TableColumn(field="ntcp_tcp", title="NTCP or TCP", width=150, formatter=NumberFormatter(format="0.000"))]

        self.emami = [TableColumn(field="roi", title="Structure", width=150),
                      TableColumn(field="ep", title="Endpoint", width=250),
                      TableColumn(field="eud_a", title="a", width=75),
                      TableColumn(field="gamma_50", title=u"\u03b3_50", width=75),
                      TableColumn(field="td_tcd", title="TD_50", width=150)]

        self.beams = [TableColumn(field="mrn", title="MRN", width=105),
                      TableColumn(field="group", title="Group", width=230),
                      TableColumn(field="beam_number", title="Beam", width=50),
                      TableColumn(field="fx_count", title="Fxs", width=50),
                      TableColumn(field="fx_grp_beam_count", title="Beams", width=50),
                      TableColumn(field="fx_grp_number", title="Rx Grp", width=60),
                      TableColumn(field="beam_name", title="Name", width=150),
                      TableColumn(field="beam_dose", title="Dose", width=80, formatter=NumberFormatter(format="0.00")),
                      TableColumn(field="beam_energy_min", title="Energy Min", width=80),
                      TableColumn(field="beam_energy_max", title="Energy Max", width=80),
                      TableColumn(field="beam_mu", title="MU", width=100, formatter=NumberFormatter(format="0.0")),
                      TableColumn(field="beam_mu_per_deg", title="MU/deg", width=100, formatter=NumberFormatter(format="0.0")),
                      TableColumn(field="beam_mu_per_cp", title="MU/CP", width=100, formatter=NumberFormatter(format="0.0")),
                      TableColumn(field="beam_type", title="Type", width=100),
                      TableColumn(field="scan_mode", title="Scan Mode", width=100),
                      TableColumn(field="scan_spot_count", title="Scan Spots", width=100),
                      TableColumn(field="control_point_count", title="CPs", width=80),
                      TableColumn(field="radiation_type", title="Rad. Type", width=80),
                      TableColumn(field="ssd", title="SSD", width=80, formatter=NumberFormatter(format="0.0")),
                      TableColumn(field="treatment_machine", title="Tx Machine", width=80)]

        self.beams2 = [TableColumn(field="mrn", title="MRN", width=105),
                       TableColumn(field="group", title="Group", width=230),
                       TableColumn(field="beam_name", title="Name", width=150),
                       TableColumn(field="gantry_start", title="Gan Start", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="gantry_end", title="End", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="gantry_rot_dir", title="Rot Dir", width=80),
                       TableColumn(field="gantry_range", title="Range", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="gantry_min", title="Min", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="gantry_max", title="Max", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="collimator_start", title="Col Start", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="collimator_end", title="End", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="collimator_rot_dir", title="Rot Dir", width=80),
                       TableColumn(field="collimator_range", title="Range", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="collimator_min", title="Min", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="collimator_max", title="Max", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="couch_start", title="Couch Start", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="couch_end", title="End", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="couch_rot_dir", title="Rot Dir", width=80),
                       TableColumn(field="couch_range", title="Range", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="couch_min", title="Min", width=80, formatter=NumberFormatter(format="0.0")),
                       TableColumn(field="couch_max", title="Max", width=80, formatter=NumberFormatter(format="0.0"))]

        self.plans = [TableColumn(field="mrn", title="MRN", width=420),
                      TableColumn(field="group", title="Group", width=230),
                      TableColumn(field="age", title="Age", width=80),
                      TableColumn(field="birth_date", title="Birth Date"),
                      TableColumn(field="dose_grid_res", title="Dose Grid Res"),
                      TableColumn(field="heterogeneity_correction", title="Heterogeneity"),
                      TableColumn(field="fxs", title="Fxs", width=80),
                      TableColumn(field="patient_orientation", title="Orientation"),
                      TableColumn(field="patient_sex", title="Sex", width=80),
                      TableColumn(field="physician", title="Rad Onc"),
                      TableColumn(field="rx_dose", title="Rx Dose", formatter=NumberFormatter(format="0.00")),
                      TableColumn(field="sim_study_date", title="Sim Study Date"),
                      TableColumn(field="total_mu", title="Total MU", formatter=NumberFormatter(format="0.0")),
                      TableColumn(field="tx_modality", title="Tx Modality"),
                      TableColumn(field="tx_site", title="Tx Site"),
                      TableColumn(field="baseline", title="Baseline")]

        self.rxs = [TableColumn(field="mrn", title="MRN"),
                    TableColumn(field="group", title="Group", width=230),
                    TableColumn(field="plan_name", title="Plan Name"),
                    TableColumn(field="fx_dose", title="Fx Dose", formatter=NumberFormatter(format="0.00")),
                    TableColumn(field="rx_percent", title="Rx Isodose", formatter=NumberFormatter(format="0.0")),
                    TableColumn(field="fxs", title="Fxs", width=80),
                    TableColumn(field="rx_dose", title="Rx Dose", formatter=NumberFormatter(format="0.00")),
                    TableColumn(field="fx_grp_number", title="Fx Grp"),
                    TableColumn(field="fx_grp_count", title="Fx Groups"),
                    TableColumn(field="fx_grp_name", title="Fx Grp Name"),
                    TableColumn(field="normalization_method", title="Norm Method"),
                    TableColumn(field="normalization_object", title="Norm Object")]

        self.corr_chart = [TableColumn(field="stat", title="Single-Var Regression", width=100),
                           TableColumn(field="group_1", title="Group 1", width=60),
                           TableColumn(field="group_2", title="Group 2", width=60)]

        self.multi_var_include = [TableColumn(field="var_name", title="Variables for Multi-Var Regression", width=100)]

        self.multi_var_model_1 = [TableColumn(field="var_name", title="Independent Variable", width=300),
                                  TableColumn(field="coeff_str", title="coefficient",  width=150),
                                  TableColumn(field="p_str", title="p-value", width=150)]

        self.multi_var_model_2 = [TableColumn(field="var_name", title="Independent Variable", width=300),
                                  TableColumn(field="coeff_str", title="coefficient",  width=150),
                                  TableColumn(field="p_str", title="p-value", width=150)]

        self.multi_var_coeff_1 = [TableColumn(field="y_var", title="Dependent Variable", width=150),
                                  TableColumn(field="r_sq_str", title="R-squared", width=150),
                                  TableColumn(field="model_p_str", title="Prob for F-statistic", width=150)]

        self.multi_var_coeff_2 = [TableColumn(field="y_var", title="Dependent Variable", width=150),
                                  TableColumn(field="r_sq_str", title="R-squared", width=150),
                                  TableColumn(field="model_p_str", title="Prob for F-statistic", width=150)]

        self.mlc_viewer = [TableColumn(field="cp", title="CP"),
                           TableColumn(field="cum_mu_frac", title="Rel MU", formatter=NumberFormatter(format="0.000")),
                           TableColumn(field="cum_mu", title="MU", formatter=NumberFormatter(format="0.0")),
                           TableColumn(field="cp_mu", title="CP MU", formatter=NumberFormatter(format="0.0")),
                           TableColumn(field="gantry", title="Gantry", formatter=NumberFormatter(format="0.0")),
                           TableColumn(field="collimator", title="Col", formatter=NumberFormatter(format="0.0")),
                           TableColumn(field="couch", title="Couch", formatter=NumberFormatter(format="0.0")),
                           TableColumn(field="jaw_x1", title="X1", formatter=NumberFormatter(format="0.0")),
                           TableColumn(field="jaw_x2", title="X2", formatter=NumberFormatter(format="0.0")),
                           TableColumn(field="jaw_y1", title="Y1", formatter=NumberFormatter(format="0.0")),
                           TableColumn(field="jaw_y2", title="Y2", formatter=NumberFormatter(format="0.0")),
                           TableColumn(field="area", title="Area", formatter=NumberFormatter(format="0.0")),
                           TableColumn(field="x_perim", title="X Path", formatter=NumberFormatter(format="0.00")),
                           TableColumn(field="y_perim", title="Y Path", formatter=NumberFormatter(format="0.00")),
                           TableColumn(field="cmp_score", title="Score", formatter=NumberFormatter(format="0.000"))]
