#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# DICOM_to_Python.py
"""
Import DICOM RT Dose, Structure, and Plan files into Python objects
Created on Sun Feb 26 11:06:28 2017
@author: Dan Cutright, PhD
"""

from __future__ import print_function
import dicom  # pydicom
from dicompylercore import dicomparser, dvhcalc
from datetime import datetime
from dateutil.relativedelta import relativedelta  # python-dateutil
from roi_name_manager import DatabaseROIs, clean_name
from utilities import datetime_str_to_obj


class DVHRow:
    def __init__(self, mrn, study_instance_uid, institutional_roi, physician_roi,
                 roi_name, roi_type, volume, min_dose, mean_dose, max_dose, dvh_str):

        for key, value in locals().iteritems():
            if key != 'self':
                setattr(self, key, value)


class BeamRow:
    def __init__(self, mrn, study_instance_uid, beam_number, beam_name,
                 fx_group, fxs, fx_grp_beam_count, beam_dose,
                 beam_mu, radiation_type, beam_energy, beam_type, control_point_count,
                 gantry_start, gantry_end, gantry_rot_dir,
                 collimator_start, collimator_end, collimator_rot_dir,
                 couch_start, couch_end, couch_rot_dir,
                 isocenter, ssd, treatment_machine):

        for key, value in locals().iteritems():
            if key != 'self':
                setattr(self, key, value)


class RxRow:
    def __init__(self, mrn, study_instance_uid, plan_name, fx_grp_name, fx_grp_number, fx_grp_count,
                 fx_dose, fxs, rx_dose, rx_percent, normalization_method, normalization_object):

        for key, value in locals().iteritems():
            if key != 'self':
                setattr(self, key, value)


# Each Plan class object contains data to fill an entire row of the SQL table 'Plans'
# There will be a Plan class per structure of a Plan
class PlanRow:
    def __init__(self, plan_file, structure_file, dose_file):
        # Read DICOM files
        rt_plan = dicom.read_file(plan_file)
        rt_plan_dicompyler = dicomparser.DicomParser(plan_file)
        rt_plan_obj = rt_plan_dicompyler.GetPlan()
        rt_structure = dicom.read_file(structure_file)
        rt_dose = dicom.read_file(dose_file)

        # Heterogeneity
        if hasattr(rt_dose, 'TissueHeterogeneityCorrection'):
            if isinstance(rt_dose.TissueHeterogeneityCorrection, basestring):
                heterogeneity_correction = rt_dose.TissueHeterogeneityCorrection
            else:
                heterogeneity_correction = ','.join(rt_dose.TissueHeterogeneityCorrection)
        else:
            heterogeneity_correction = 'IMAGE'

        # Record Medical Record Number
        mrn = rt_plan.PatientID

        # Record gender
        patient_sex = rt_plan.PatientSex.upper()
        if not (patient_sex == 'M' or patient_sex == 'F'):
            patient_sex = '-'

        # Parse and record sim date
        sim_study_date = rt_plan.StudyDate
        if sim_study_date:
            sim_study_year = int(sim_study_date[0:4])
            sim_study_month = int(sim_study_date[4:6])
            sim_study_day = int(sim_study_date[6:8])
            sim_study_date_obj = datetime(sim_study_year, sim_study_month, sim_study_day)
        else:
            sim_study_date = '(NULL)'

        # Calculate patient age at time of sim
        # Set to NULL birthday is not in DICOM file
        birth_date = rt_plan.PatientBirthDate
        if not birth_date:
            birth_date = '(NULL)'
            age = '(NULL)'
        else:
            birth_year = int(birth_date[0:4])
            birth_month = int(birth_date[4:6])
            birth_day = int(birth_date[6:8])
            birth_date_obj = datetime(birth_year, birth_month, birth_day)
            if sim_study_date == '(NULL)':
                age = '(NULL)'
            else:
                age = relativedelta(sim_study_date_obj, birth_date_obj).years
                if age <= 0:
                    age = '(NULL)'

        # Record physician initials
        # In Pinnacle, PhysiciansOfRecord refers to the Radiation Oncologist field
        if hasattr(rt_plan, 'PhysiciansOfRecord'):
            physician = rt_plan.PhysiciansOfRecord.upper()
        else:
            physician = rt_plan.ReferringPhysicianName.upper()

        # Initialize fx and MU counters, iterate over all rx's
        fxs = 0
        total_mu = 0
        fx_grp_seq = rt_plan.FractionGroupSequence  # just to limit characters for later reference
        # Count number of fxs and total MUs
        # Note these are total fxs, not treatment days
        for fx_grp in fx_grp_seq:
            fxs += fx_grp.NumberOfFractionsPlanned
            for Beam in range(0, fx_grp.NumberOfBeams):
                total_mu += fx_grp.ReferencedBeamSequence[Beam].BeamMeterset
        total_mu = round(total_mu, 1)

        # This UID must be in all DICOM files associated with this sim study
        study_instance_uid = rt_plan.StudyInstanceUID

        # Record patient position (e.g., HFS, HFP, FFS, or FFP)
        patient_orientation = rt_plan.PatientSetupSequence[0].PatientPosition

        # Context self-evident, their utility is not (yet)
        plan_time_stamp = datetime_str_to_obj(rt_plan.RTPlanDate + rt_plan.RTPlanTime)
        struct_time_stamp = datetime_str_to_obj(rt_structure.StructureSetDate + rt_structure.StructureSetTime)
        dose_time_stamp = datetime_str_to_obj(rt_dose.InstanceCreationDate +
                                              rt_dose.InstanceCreationTime.split('.')[0])

        # Record treatment planning system vendor, name, and version
        tps_manufacturer = rt_plan.Manufacturer
        tps_software_name = rt_plan.ManufacturerModelName
        tps_software_version = rt_plan.SoftwareVersions[0]

        # Because DICOM does not contain Rx's explicitly, the user must create
        # a point in the RT Structure file called 'rx: '
        # If multiple Rx found, sum will be reported
        # Record tx site from 'tx:' point or RTPlanLabel if no point
        tx_site = rt_plan.RTPlanLabel  # tx_site defaults to plan name if tx in a tx point
        tx_found = False
        rx_dose = 0
        roi_counter = 0
        roi_count = len(rt_structure.StructureSetROISequence)
        roi_seq = rt_structure.StructureSetROISequence  # just limit num characters in code
        fx_reset = False
        while (not tx_found) and (roi_counter < roi_count):
            roi_name = roi_seq[roi_counter].ROIName.lower()
            if len(roi_name) > 2:
                temp = roi_name.split(' ')
                if temp[0][0:2] == 'rx':
                    if not fx_reset:
                        fxs = 0
                        fx_reset = True
                    fx_dose = float(temp[temp.index('cgy')-1]) / 100
                    fxs += int(temp[temp.index('x') + 1])
                    rx_dose += fx_dose * float((temp[temp.index('x') + 1]))
                elif temp[0] == 'tx:':
                    temp.remove('tx:')
                    tx_site = ' '.join(temp)
                    tx_found = True
            roi_counter += 1

        # if rx_dose point not found, use dose in DICOM file
        if rx_dose == 0:
            rx_dose = float(rt_plan_obj['rxdose']) / 100

        # This assumes that Plans are either 100% Arc plans or 100% Static Angle
        # Note that the beams class will have this information on a per beam basis
        tx_modality = ''
        tx_energies = ' '
        temp = ''

        # Brachytherapy
        if rt_plan_obj['brachy']:
            tx_modality = 'Brachy '

        # Protons
        elif hasattr(rt_plan, 'IonBeamSequence'):
            beam_seq = rt_plan.IonBeamSequence
            for beam in beam_seq:
                temp += beam.RadiationType + ' '
                first_cp = beam.IonControlPointSequence[0]
                if first_cp.GantryRotationDirection in {'CW', 'CC'}:
                    temp += 'Arc '
                else:
                    temp += '3D '
                energy_str = str(round(float(first_cp.NominalBeamEnergy))).split('.')[0]
                energy_temp = ' ' + energy_str + 'MeV '
                if energy_temp not in tx_energies:
                    tx_energies += energy_temp

            tx_energies = tx_energies[1:-1]
            tx_modality += 'Proton '

        # Photons and electrons
        elif hasattr(rt_plan, 'BeamSequence'):
            beam_seq = rt_plan.BeamSequence
            for beam in beam_seq:
                temp += beam.RadiationType + ' '
                first_cp = beam.ControlPointSequence[0]
                if first_cp.GantryRotationDirection in {'CW', 'CC'}:
                    temp += 'Arc '
                else:
                    temp += '3D '
                energy_temp = ' ' + str(first_cp.NominalBeamEnergy)
                if beam.RadiationType.lower() == 'photon':
                    energy_temp += 'MV '
                elif beam.RadiationType.lower() == 'electron':
                    energy_temp += 'MeV '
                if tx_energies.find(energy_temp) < 0:
                    tx_energies += energy_temp

            tx_energies = tx_energies.strip()
            temp = temp.lower()
            if 'photon' in temp:
                if 'photon arc' in temp:
                    tx_modality += 'Photon Arc '
                else:
                    tx_modality += 'Photon 3D '
            if 'electron' in temp:
                if 'electron arc' in temp:
                    tx_modality += 'Electron Arc '
                else:
                    tx_modality += 'Electron 3D '

        tx_modality = tx_modality.strip()

        # Will require a yet to be named function to determine this
        # Applicable for brachy and Gamma Knife, not yet supported
        tx_time = '00:00:00'

        # Record resolution of dose grid
        dose_grid_resolution = [str(round(float(rt_dose.PixelSpacing[0]), 1)),
                                str(round(float(rt_dose.PixelSpacing[1]), 1)),
                                str(round(float(rt_dose.SliceThickness), 1))]
        dose_grid_resolution = ', '.join(dose_grid_resolution)

        # Set object values
        self.mrn = mrn
        self.birth_date = birth_date
        self.age = age
        self.patient_sex = patient_sex
        self.sim_study_date = sim_study_date
        self.physician = physician
        self.tx_site = tx_site
        self.rx_dose = rx_dose
        self.fxs = fxs
        self.tx_energies = tx_energies
        self.study_instance_uid = study_instance_uid
        self.patient_orientation = patient_orientation
        self.plan_time_stamp = plan_time_stamp
        self.struct_time_stamp = struct_time_stamp
        self.dose_time_stamp = dose_time_stamp
        self.tps_manufacturer = tps_manufacturer
        self.tps_software_name = tps_software_name
        self.tps_software_version = tps_software_version
        self.tx_modality = tx_modality
        self.tx_time = tx_time
        self.total_mu = total_mu
        self.dose_grid_resolution = dose_grid_resolution
        self.heterogeneity_correction = heterogeneity_correction


class DVHTable:
    def __init__(self, structure_file, dose_file):
        # Get ROI Category Map
        database_rois = DatabaseROIs()

        # Import RT Structure and RT Dose files using dicompyler
        rt_structure_dicom = dicom.read_file(structure_file)
        mrn = rt_structure_dicom.PatientID
        study_instance_uid = rt_structure_dicom.StudyInstanceUID

        rt_structure = dicomparser.DicomParser(structure_file)
        rt_structures = rt_structure.GetStructures()

        if hasattr(rt_structure_dicom, 'PhysiciansOfRecord'):
            physician = rt_structure_dicom.PhysiciansOfRecord.upper()
        else:
            physician = rt_structure_dicom.ReferringPhysicianName.upper()

        values = {}
        row_counter = 0
        self.dvhs = {}
        for key in rt_structures:
            # Import DVH from RT Structure and RT Dose files
            if rt_structures[key]['type'] != 'MARKER':

                current_dvh_calc = dvhcalc.get_dvh(structure_file, dose_file, key)
                self.dvhs[row_counter] = current_dvh_calc.counts
                if current_dvh_calc.volume > 0:
                    print('Importing', current_dvh_calc.name, sep=' ')
                    if rt_structures[key]['name'].lower().find('itv') == 0:
                        roi_type = 'ITV'
                    else:
                        roi_type = rt_structures[key]['type']
                    current_roi_name = clean_name(rt_structures[key]['name'])

                    if database_rois.is_roi(current_roi_name):
                        if database_rois.is_physician(physician):
                            physician_roi = database_rois.get_physician_roi(physician, current_roi_name)
                            institutional_roi = database_rois.get_institutional_roi(physician, physician_roi)
                        else:
                            if current_roi_name in database_rois.institutional_rois:
                                institutional_roi = current_roi_name
                            else:
                                institutional_roi = 'uncategorized'
                            physician_roi = 'uncategorized'
                    else:
                        institutional_roi = 'uncategorized'
                        physician_roi = 'uncategorized'

                    current_dvh_row = DVHRow(mrn,
                                             study_instance_uid,
                                             institutional_roi,
                                             physician_roi,
                                             current_roi_name,
                                             roi_type,
                                             current_dvh_calc.volume,
                                             current_dvh_calc.min,
                                             current_dvh_calc.mean,
                                             current_dvh_calc.max,
                                             ','.join(['%.2f' % num for num in current_dvh_calc.counts]))
                    values[row_counter] = current_dvh_row
                    row_counter += 1

        self.count = row_counter
        dvh_range = range(0, self.count)

        for attr in dir(values[0]):
            if not attr.startswith('_'):
                new_list = []
                for x in dvh_range:
                    new_list.append(getattr(values[x], attr))
                setattr(self, attr, new_list)


class BeamTable:
    def __init__(self, plan_file):

        beam_num = 0
        values = {}
        # Import RT Dose files using dicompyler
        rt_plan = dicom.read_file(plan_file)

        mrn = rt_plan.PatientID
        study_instance_uid = rt_plan.StudyInstanceUID

        fx_grp = 0
        for fx_grp_seq in rt_plan.FractionGroupSequence:
            fx_grp += 1
            fxs = int(fx_grp_seq.NumberOfFractionsPlanned)
            fx_grp_beam_count = int(fx_grp_seq.NumberOfBeams)

            for fx_grp_beam in range(0, fx_grp_beam_count):
                if hasattr(rt_plan, 'BeamSequence'):
                    beam_seq = rt_plan.BeamSequence[beam_num]  # Photons and electrons
                else:
                    beam_seq = rt_plan.IonBeamSequence[beam_num]  # Protons

                if 'BeamDescription' in beam_seq:
                    beam_name = beam_seq.BeamDescription
                else:
                    beam_name = beam_seq.BeamName

                ref_beam_seq = fx_grp_seq.ReferencedBeamSequence[fx_grp_beam]

                treatment_machine = beam_seq.TreatmentMachineName

                beam_dose = float(ref_beam_seq.BeamDose)
                beam_mu = float(ref_beam_seq.BeamMeterset)

                isocenter = [str(round(ref_beam_seq.BeamDoseSpecificationPoint[0], 4)),
                             str(round(ref_beam_seq.BeamDoseSpecificationPoint[1], 4)),
                             str(round(ref_beam_seq.BeamDoseSpecificationPoint[2], 4))]
                isocenter = ','.join(isocenter)

                radiation_type = beam_seq.RadiationType
                if hasattr(beam_seq, 'ControlPointSequence'):
                    cp_seq = beam_seq.ControlPointSequence
                else:
                    cp_seq = beam_seq.IonControlPointSequence

                beam_energy = cp_seq[0].NominalBeamEnergy
                beam_type = beam_seq.BeamType

                control_point_count = beam_seq.NumberOfControlPoints
                first_cp = cp_seq[0]
                if beam_seq.BeamType == 'STATIC':
                    final_cp = first_cp
                else:
                    final_cp = cp_seq[-1]

                max_angle = 180

                gantry_rot_dir = first_cp.GantryRotationDirection
                gantry_start, gantry_end = change_angle_range(float(first_cp.GantryAngle),
                                                              float(final_cp.GantryAngle),
                                                              gantry_rot_dir,
                                                              max_angle)

                collimator_rot_dir = first_cp.BeamLimitingDeviceRotationDirection
                collimator_start = float(first_cp.BeamLimitingDeviceAngle)
                try:
                    collimator_end = float(final_cp.BeamLimitingDeviceAngle)
                except:
                    collimator_end = collimator_start
                collimator_start, collimator_end = change_angle_range(collimator_start,
                                                                      collimator_end,
                                                                      collimator_rot_dir,
                                                                      max_angle)

                couch_rot_dir = first_cp.PatientSupportRotationDirection
                couch_start = float(first_cp.PatientSupportAngle)
                try:
                    couch_end = float(final_cp.PatientSupportAngle)
                except:
                    couch_end = couch_start
                couch_start, couch_end = change_angle_range(couch_start,
                                                            couch_end,
                                                            couch_rot_dir,
                                                            max_angle)

                # If beam is an arc, return average SSD, otherwise
                if hasattr(first_cp, 'SourceToSurfaceDistance'):
                    if gantry_rot_dir in {'CW', 'CC'}:
                        ssd = 0
                        for cp in beam_seq.ControlPointSequence:
                            ssd += round(float(cp.SourceToSurfaceDistance) / 10, 2)
                        ssd /= control_point_count

                    else:
                        ssd = float(first_cp.SourceToSurfaceDistance) / 10
                else:
                    ssd = float(0)

                current_beam = BeamRow(mrn, study_instance_uid, beam_num + 1,
                                       beam_name, fx_grp + 1, fxs,
                                       fx_grp_beam_count, beam_dose, beam_mu, radiation_type,
                                       beam_energy, beam_type, control_point_count,
                                       gantry_start, gantry_end, gantry_rot_dir,
                                       collimator_start, collimator_end, collimator_rot_dir,
                                       couch_start, couch_end, couch_rot_dir,
                                       isocenter, ssd, treatment_machine)

                values[beam_num] = current_beam
                beam_num += 1

        self.count = beam_num
        beam_range = range(0, self.count)

        # Rearrange values into separate attributes
        for attr in dir(values[0]):
            if not attr.startswith('_'):
                new_list = []
                for x in beam_range:
                    new_list.append(getattr(values[x], attr))
                setattr(self, attr, new_list)


class RxTable:
    def __init__(self, plan_file, structure_file):
        values = {}
        rt_plan = dicom.read_file(plan_file)
        rt_structure = dicom.read_file(structure_file)
        fx_grp_seq = rt_plan.FractionGroupSequence

        # Record Medical Record Number
        mrn = rt_plan.PatientID

        # This UID must be in all DICOM files associated with this sim study
        study_instance_uid = rt_plan.StudyInstanceUID

        fx_group_count = len(fx_grp_seq)

        for i in range(0, fx_group_count):
            rx_dose = 0
            rx_pt_found = False
            normalization_method = 'default'
            normalization_object = 'unknown'
            rx_percent = float(100)
            fx_grp_number = i + 1
            fx_dose = 0
            fx_grp_name = "FxGrp " + str(i + 1)
            plan_name = rt_plan.RTPlanLabel

            if hasattr(rt_plan, 'DoseReferenceSequence'):
                rx_dose = rt_plan.DoseReferenceSequence[i].TargetPrescriptionDose
                normalization_method = rt_plan.DoseReferenceSequence[i].DoseReferenceStructureType
                ref_roi_num = rt_plan.DoseReferenceSequence[i].ReferencedROINumber
                normalization_object_found = False
                j = 0
                while not normalization_object_found:
                    if rt_structure.ROIContourSequence[j].ReferencedROINumber == ref_roi_num:
                            normalization_object = rt_structure.StructureSetROISequence[j].ROIName
                            normalization_object_found = True
                    j += 1

                rx_pt_found = True

            for RefBeamSeq in fx_grp_seq[i].ReferencedBeamSequence:
                fx_dose += RefBeamSeq.BeamDose

            fxs = fx_grp_seq[i].NumberOfFractionsPlanned

            # Because DICOM does not contain Rx's explicitly, the user must create
            # a point in the RT Structure file called 'rx [#]: ' per rx
            roi_counter = 0
            roi_seq = rt_structure.StructureSetROISequence  # just limit num characters in code
            roi_count = len(roi_seq)
            # set defaults in case rx and tx points are not found

            while roi_counter < roi_count and not rx_pt_found:
                roi_name = roi_seq[roi_counter].ROIName.lower()
                if len(roi_name) > 2:
                    temp = roi_name.split(':')

                    if temp[0][0:3] == 'rx ' and int(temp[0].strip('rx ')) == i + 1:
                        fx_grp_number = int(temp[0].strip('rx '))

                        fx_grp_name = temp[1].strip()

                        fx_dose = float(temp[2].split('cgy')[0]) / float(100)
                        fxs = int(temp[2].split('x ')[1].split(' to')[0])
                        rx_dose = fx_dose * float(fxs)

                        rx_percent = float(temp[2].strip().split(' ')[5].strip('%'))
                        normalization_method = temp[3].strip()

                        if normalization_method != 'plan_max':
                            normalization_object = temp[4].strip()
                        else:
                            normalization_object = 'plan_max'
                        rx_pt_found = True

                roi_counter += 1

            current_fx_grp_row = RxRow(mrn, study_instance_uid, plan_name, fx_grp_name, fx_grp_number,
                                       fx_group_count, fx_dose, fxs, rx_dose, rx_percent, normalization_method,
                                       normalization_object)
            values[i] = current_fx_grp_row

        fx_group_range = range(0, fx_group_count)
        self.count = fx_group_count
        # Rearrange values into separate attributes
        for attr in dir(values[0]):
            if not attr.startswith('_'):
                new_list = []
                for x in fx_group_range:
                    new_list.append(getattr(values[x], attr))
                setattr(self, attr, new_list)


# Used to edit angle range from 0 to 360 to -180 to 180 (for example)
def change_angle_range(start, end, direction, max_positive_angle):
    if start >= max_positive_angle or \
            (start == float(max_positive_angle) and direction == 'CW'):
        start -= float(360)
    if end >= max_positive_angle or \
            (end == float(max_positive_angle) and direction == 'CC'):
        end -= float(360)

    return start, end


if __name__ == '__main__':
    pass
