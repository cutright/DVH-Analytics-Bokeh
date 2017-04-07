from DVH_SQL import *


def cursor_to_list(cursor):
    rtn_list = {}
    i = 0
    for row in cursor:
        rtn_list[i] = str(row[0])
        i += 1

    inverted = dict()
    rtn_list_unique = dict()
    i = 0
    for (a, b) in rtn_list.iteritems():
        if b not in inverted:
            inverted[b] = a
    for c in inverted.iterkeys():
        rtn_list_unique[i] = c
        i += 1

    return rtn_list_unique


class BeamQuery:
    def __init__(self, condition_str):
        self.condition_str = condition_str
        self.cnx = DVH_SQL()

        beam_dict = {'name': 'BeamDescription',
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

        for key, value in beam_dict.iteritems():
            setattr(self, key, self.rtn_list(value))

    def rtn_list(self, column):
        cursor = self.cnx.query('Beams', column, self.condition_str)
        return cursor_to_list(cursor)


class DVHQuery:
    def __init__(self, condition_str):
        self.condition_str = condition_str
        self.cnx = DVH_SQL()

        dvh_dict = {'institutional_roi': 'InstitutionalROI',
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

        for key, value in dvh_dict.iteritems():
            setattr(self, key, self.rtn_list(value))

    def rtn_list(self, column):
        cursor = self.cnx.query('DVHs', column, self.condition_str)
        return cursor_to_list(cursor)


class PlanQuery:
    def __init__(self, condition_str):
        self.condition_str = condition_str
        self.cnx = DVH_SQL()

        plan_dict = {'age': 'Age',
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

        for key, value in plan_dict.iteritems():
            setattr(self, key, self.rtn_list(value))

    def rtn_list(self, column):
        cursor = self.cnx.query('Plans', column, self.condition_str)
        return cursor_to_list(cursor)


class RxQuery:
    def __init__(self, condition_str):
        self.condition_str = condition_str
        self.cnx = DVH_SQL()

        rx_dict = {'fx_dose': 'FxDose',
                   'fx_grp_name': 'FxGrpName',
                   'fx_grp_num': 'FxGrpNum'
                   'fx_grp_count:' 'FxGrps',
                   'fx_count': 'Fxs',
                   'mrn': 'MRN',
                   'normalization_method': 'NormMethod',
                   'normalization_object': 'NormObject',
                   'plan_name': 'PlanName',
                   'rx_dose': 'RxDose',
                   'rx_percent': 'RxPercent',
                   'study_instance_uid': 'StudyInstanceUID'}

        for key, value in rx_dict.iteritems():
            setattr(self, key, self.rtn_list(value))

    def rtn_list(self, column):
        cursor = self.cnx.query('Rxs', column, self.condition_str)
        return cursor_to_list(cursor)
