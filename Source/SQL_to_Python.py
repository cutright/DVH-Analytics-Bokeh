from DVH_SQL import *


class QuerySQL:
    def __init__(self, table_name, condition_str):
        create_properties = True

        if table_name == 'Beams':
            query_dict = {'name': 'BeamDescription',
                          'dose': 'BeamDose',
                          'energy': 'BeamEnergy',
                          'mus': 'BeamMUs',
                          'type': 'BeamType',
                          'collimator_angle': 'ColAngle',
                          'control_point_count': 'ControlPoints',
                          'couch_angle': 'CouchAngle',
                          'fx_count': 'Fractions',
                          'fx_grp_num': 'FxGroup',
                          'gantry_end': 'GantryEnd',
                          'gantry_rot_dir': 'GantryRotDir',
                          'gantry_start': 'GantryStart',
                          'isocenter': 'IsocenterCoord',
                          'mrn': 'MRN',
                          'fx_grp_beam_count': 'NumFxGrpBeams',
                          'radiation_type': 'RadiationType',
                          'ssd': 'SSD',
                          'study_instance_uid': 'StudyInstanceUID'}
        elif table_name == 'DVHs':
            query_dict = {'institutional_roi': 'InstitutionalROI',
                          'mrn': 'MRN',
                          'max_dose': 'MaxDose',
                          'mean_dose': 'MeanDose',
                          'min_dose': 'MinDose',
                          'physician_roi': 'PhysicianROI',
                          'roi_name': 'ROIName',
                          'study_instance_uid': 'StudyInstanceUID',
                          'roi_type': 'Type',
                          'volume': 'Volume',
                          'dvh_string': 'VolumeString'}
        elif table_name == 'Plans':
            query_dict = {'age': 'Age',
                          'birth_date': 'Birthdate',
                          'dose_grid_res': 'DoseGridRes',
                          'dose_time_stamp': 'DoseTimeStamp',
                          'energy': 'Energy',
                          'fxs': 'Fractions',
                          'mrn': 'MRN',
                          'mu': 'MUs',
                          'patient_orientation': 'PatientOrientation',
                          'plan_time_stamp': 'PlanTimeStamp',
                          'physician': 'RadOnc',
                          'rx_dose': 'RxDose',
                          'patient_sex': 'Sex',
                          'sim_study_date': 'SimStudyDate',
                          'struct_time_stamp': 'StTimeStamp',
                          'study_instance_uid': 'StudyInstanceUID',
                          'tps_manufacturer': 'TPSManufacturer',
                          'tps_software_name': 'TPSSoftwareName',
                          'tps_software_version': 'TPSSoftwareVersion',
                          'tx_modality': 'TxModality',
                          'tx_site': 'TxSite',
                          'tx_time': 'TxTime'}
        elif table_name == 'Rxs':
            query_dict = {'fx_dose': 'FxDose',
                          'fx_grp_name': 'FxGrpName',
                          'fx_grp_num': 'FxGrpNum',
                          'fx_grp_count': 'FxGrps',
                          'fx_count': 'Fxs',
                          'mrn': 'MRN',
                          'normalization_method': 'NormMethod',
                          'normalization_object': 'NormObject',
                          'plan_name': 'PlanName',
                          'rx_dose': 'RxDose',
                          'rx_percent': 'RxPercent',
                          'study_instance_uid': 'StudyInstanceUID'}
        else:
            create_properties = False

        if create_properties:
            self.table_name = table_name
            self.condition_str = condition_str
            self.cnx = DVH_SQL()
            for key, value in query_dict.iteritems():
                self.cursor = self.cnx.query(self.table_name,
                                             value,
                                             self.condition_str)
                rtn_list = self.cursor_to_list()
                rtn_list[0] = query_dict[key]
                setattr(self, key, rtn_list)
        else:
            print 'Table name in valid. Please select from Beams, DVHs, Plans, or Rxs.'

    def cursor_to_list(self):
        rtn_list = {}
        i = 0
        for row in self.cursor:
            rtn_list[i] = str(row[0])
            i += 1

        inverted = dict()
        rtn_list_unique = dict()
        i = 1
        for (a, b) in rtn_list.iteritems():
            if b not in inverted:
                inverted[b] = a
        for c in inverted.iterkeys():
            rtn_list_unique[i] = c
            i += 1

        return rtn_list_unique
