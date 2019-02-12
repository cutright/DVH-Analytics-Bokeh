class Categories:
    def __init__(self, sources):

        # This is a maps categorical data type selections to SQL columns and SQL tables
        self.selector = {'ROI Institutional Category': {'var_name': 'institutional_roi', 'table': 'DVHs'},
                         'ROI Physician Category': {'var_name': 'physician_roi', 'table': 'DVHs'},
                         'ROI Type': {'var_name': 'roi_type', 'table': 'DVHs'},
                         'Beam Type': {'var_name': 'beam_type', 'table': 'Beams'},
                         'Collimator Rotation Direction': {'var_name': 'collimator_rot_dir', 'table': 'Beams'},
                         'Couch Rotation Direction': {'var_name': 'couch_rot_dir', 'table': 'Beams'},
                         'Dose Grid Resolution': {'var_name': 'dose_grid_res', 'table': 'Plans'},
                         'Gantry Rotation Direction': {'var_name': 'gantry_rot_dir', 'table': 'Beams'},
                         'Radiation Type': {'var_name': 'radiation_type', 'table': 'Beams'},
                         'Patient Orientation': {'var_name': 'patient_orientation', 'table': 'Plans'},
                         'Patient Sex': {'var_name': 'patient_sex', 'table': 'Plans'},
                         'Physician': {'var_name': 'physician', 'table': 'Plans'},
                         'Tx Modality': {'var_name': 'tx_modality', 'table': 'Plans'},
                         'Tx Site': {'var_name': 'tx_site', 'table': 'Plans'},
                         'Normalization': {'var_name': 'normalization_method', 'table': 'Rxs'},
                         'Treatment Machine': {'var_name': 'treatment_machine', 'table': 'Beams'},
                         'Heterogeneity Correction': {'var_name': 'heterogeneity_correction', 'table': 'Plans'},
                         'Scan Mode': {'var_name': 'scan_mode', 'table': 'Beams'},
                         'MRN': {'var_name': 'mrn', 'table': 'Plans'},
                         'UID': {'var_name': 'study_instance_uid', 'table': 'Plans'},
                         'Baseline': {'var_name': 'baseline', 'table': 'Plans'},
                         'Protocol': {'var_name': 'protocol', 'table': 'Plans'}}

        # This is a maps quantitative data type selections to SQL columns and SQL tables, and the bokeh source
        self.range = {'Age': {'var_name': 'age', 'table': 'Plans', 'units': '', 'source': sources.plans},
                      'Beam Energy Min': {'var_name': 'beam_energy_min', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'Beam Energy Max': {'var_name': 'beam_energy_max', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'Birth Date': {'var_name': 'birth_date', 'table': 'Plans', 'units': '', 'source': sources.plans},
                      'Planned Fractions': {'var_name': 'fxs', 'table': 'Plans', 'units': '', 'source': sources.plans},
                      'Rx Dose': {'var_name': 'rx_dose', 'table': 'Plans', 'units': 'Gy', 'source': sources.plans},
                      'Rx Isodose': {'var_name': 'rx_percent', 'table': 'Rxs', 'units': '%', 'source': sources.rxs},
                      'Simulation Date': {'var_name': 'sim_study_date', 'table': 'Plans', 'units': '', 'source': sources.plans},
                      'Total Plan MU': {'var_name': 'total_mu', 'table': 'Plans', 'units': 'MU', 'source': sources.plans},
                      'Fraction Dose': {'var_name': 'fx_dose', 'table': 'Rxs', 'units': 'Gy', 'source': sources.rxs},
                      'Beam Dose': {'var_name': 'beam_dose', 'table': 'Beams', 'units': 'Gy', 'source': sources.beams},
                      'Beam MU': {'var_name': 'beam_mu', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'Control Point Count': {'var_name': 'control_point_count', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'Collimator Start Angle': {'var_name': 'collimator_start', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Collimator End Angle': {'var_name': 'collimator_end', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Collimator Min Angle': {'var_name': 'collimator_min', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Collimator Max Angle': {'var_name': 'collimator_max', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Collimator Range': {'var_name': 'collimator_range', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Couch Start Angle': {'var_name': 'couch_start', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Couch End Angle': {'var_name': 'couch_end', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Couch Min Angle': {'var_name': 'couch_min', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Couch Max Angle': {'var_name': 'couch_max', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Couch Range': {'var_name': 'couch_range', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Gantry Start Angle': {'var_name': 'gantry_start', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Gantry End Angle': {'var_name': 'gantry_end', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Gantry Min Angle': {'var_name': 'gantry_min', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Gantry Max Angle': {'var_name': 'gantry_max', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'Gantry Range': {'var_name': 'gantry_range', 'table': 'Beams', 'units': 'deg', 'source': sources.beams},
                      'SSD': {'var_name': 'ssd', 'table': 'Beams', 'units': 'cm', 'source': sources.beams},
                      'ROI Min Dose': {'var_name': 'min_dose', 'table': 'DVHs', 'units': 'Gy', 'source': sources.dvhs},
                      'ROI Mean Dose': {'var_name': 'mean_dose', 'table': 'DVHs', 'units': 'Gy', 'source': sources.dvhs},
                      'ROI Max Dose': {'var_name': 'max_dose', 'table': 'DVHs', 'units': 'Gy', 'source': sources.dvhs},
                      'ROI Volume': {'var_name': 'volume', 'table': 'DVHs', 'units': 'cc', 'source': sources.dvhs},
                      'ROI Surface Area': {'var_name': 'surface_area', 'table': 'DVHs', 'units': 'cm^2', 'source': sources.dvhs},
                      'ROI Spread X': {'var_name': 'spread_x', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                      'ROI Spread Y': {'var_name': 'spread_y', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                      'ROI Spread Z': {'var_name': 'spread_z', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                      'PTV Distance (Min)': {'var_name': 'dist_to_ptv_min', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                      'PTV Distance (Mean)': {'var_name': 'dist_to_ptv_mean', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                      'PTV Distance (Median)': {'var_name': 'dist_to_ptv_median', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                      'PTV Distance (Max)': {'var_name': 'dist_to_ptv_max', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                      'PTV Distance (Centroids)': {'var_name': 'dist_to_ptv_centroids', 'table': 'DVHs', 'units': 'cm', 'source': sources.dvhs},
                      'PTV Overlap': {'var_name': 'ptv_overlap', 'table': 'DVHs', 'units': 'cc', 'source': sources.dvhs},
                      'Scan Spots': {'var_name': 'scan_spot_count', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'Beam MU per deg': {'var_name': 'beam_mu_per_deg', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'Beam MU per control point': {'var_name': 'beam_mu_per_cp', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'ROI Cross-Section Max': {'var_name': 'cross_section_max', 'table': 'DVHs', 'units': 'cm^2', 'source': sources.dvhs},
                      'ROI Cross-Section Median': {'var_name': 'cross_section_median', 'table': 'DVHs', 'units': 'cm^2', 'source': sources.dvhs},
                      'Toxicity Grade': {'var_name': 'toxicity_grade', 'table': 'DVHs', 'units': '', 'source': sources.dvhs},
                      'Plan Complexity': {'var_name': 'complexity', 'table': 'Plans', 'units': '', 'source': sources.plans},
                      'Beam Complexity (Min)': {'var_name': 'complexity_min', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'Beam Complexity (Mean)': {'var_name': 'complexity_mean', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'Beam Complexity (Median)': {'var_name': 'complexity_median', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'Beam Complexity (Max)': {'var_name': 'complexity_max', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'Beam Area (Min)': {'var_name': 'area_min', 'table': 'Beams', 'units': 'cm^2', 'source': sources.beams},
                      'Beam Area (Mean)': {'var_name': 'area_mean', 'table': 'Beams', 'units': 'cm^2', 'source': sources.beams},
                      'Beam Area (Median)': {'var_name': 'area_median', 'table': 'Beams', 'units': 'cm^2', 'source': sources.beams},
                      'Beam Area (Max)': {'var_name': 'area_max', 'table': 'Beams', 'units': 'cm^2', 'source': sources.beams},
                      'CP MU (Min)': {'var_name': 'cp_mu_min', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'CP MU (Mean)': {'var_name': 'cp_mu_mean', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'CP MU (Median)': {'var_name': 'cp_mu_median', 'table': 'Beams', 'units': '', 'source': sources.beams},
                      'CP MU (Max)': {'var_name': 'cp_mu_max', 'table': 'Beams', 'units': '', 'source': sources.beams}}

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Correlation and Regression variable names
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.correlation_variables = []
        self.correlation_names = []
        self.correlation_variables_beam = ['Beam Dose', 'Beam MU', 'Control Point Count', 'Gantry Range',
                                           'SSD', 'Beam MU per control point']
        for key in list(self.range):
            if key.startswith('ROI') or key.startswith('PTV') or 'Beam Complexity' in key or 'Beam Area' in key or \
                    'CP MU' in key or key in {'Total Plan MU', 'Rx Dose', 'Toxicity Grade', 'Plan Complexity'}:
                self.correlation_variables.append(key)
                self.correlation_names.append(key)
            if key in self.correlation_variables_beam:
                self.correlation_variables.append(key)
                for stat in ['Min', 'Mean', 'Median', 'Max']:
                    self.correlation_names.append("%s (%s)" % (key, stat))
        self.correlation_variables.sort()
        self.correlation_names.sort()
        self.multi_var_reg_var_names = self.correlation_names + ['EUD', 'NTCP/TCP']
