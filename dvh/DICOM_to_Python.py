#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# DICOM_to_Python.py
"""
Import DICOM RT Dose, Structure, and Plan files into Python objects
Created on Sun Feb 26 11:06:28 2017
@author: Dan Cutright, PhD
"""

import dicom  # PyDICOM
from dicompylercore import dicomparser, dvhcalc
import datetime
from dateutil.relativedelta import relativedelta
from ROI_Name_Manager import *


# Each ROI class object contains data to fill an entire row of the SQL table 'DVHs'
# This code will generate a list of ROI class objects
# There will be a ROI class per structure of a Plan
class DVHRow:
    def __init__(self, mrn, study_instance_uid, institutional_roi_name, physician_roi_name,
                 roi_name, roi_type, volume, min_dose, mean_dose, max_dose, dvh_str):
        self.mrn = mrn
        self.study_instance_uid = study_instance_uid
        self.institutional_roi_name = institutional_roi_name
        self.physician_roi_name = physician_roi_name
        self.roi_name = roi_name
        self.roi_type = roi_type
        self.volume = volume
        self.min_dose = min_dose
        self.mean_dose = mean_dose
        self.max_dose = max_dose
        self.dvh_str = dvh_str


# Each BeamInfo class object contains data to fill an entire row of the SQL table 'Beams'
# This code will generate a list of BeamInfo class objects
# There will be a Beam class per beam of a Plan
class BeamRow:
    def __init__(self, mrn, study_instance_uid, beam_number, beam_name,
                 fx_group, fxs, fx_grp_beam_count, beam_dose,
                 beam_mu, radiation_type, beam_energy, beam_type, control_point_count,
                 gantry_start, gantry_end, gantry_rot_dir, collimator_angle,
                 couch_angle, isocenter, ssd, treatment_machine):
        self.mrn = mrn
        self.study_instance_uid = study_instance_uid
        self.beam_number = beam_number
        self.beam_name = beam_name
        self.fx_group = fx_group
        self.fxs = fxs
        self.fx_grp_beam_count = fx_grp_beam_count
        self.beam_dose = beam_dose
        self.beam_mu = beam_mu
        self.radiation_type = radiation_type
        self.beam_energy = beam_energy
        self.beam_type = beam_type
        self.control_point_count = control_point_count
        self.gantry_start = gantry_start
        self.gantry_end = gantry_end
        self.gantry_rot_dir = gantry_rot_dir
        self.collimator_angle = collimator_angle
        self.couch_angle = couch_angle
        self.isocenter = isocenter
        self.ssd = ssd
        self.treatment_machine = treatment_machine


class RxRow:
    def __init__(self, mrn, study_instance_uid, plan_name, fx_grp_name, fx_grp_number, fx_grp_count,
                 fx_dose, fxs, rx_dose, rx_percent, normalization_method, normalization_object):
        self.mrn = mrn
        self.study_instance_uid = study_instance_uid
        self.plan_name = plan_name
        self.fx_grp_name = fx_grp_name
        self.fx_grp_number = fx_grp_number
        self.fx_grp_count = fx_grp_count
        self.fx_dose = fx_dose
        self.fxs = fxs
        self.rx_dose = rx_dose
        self.rx_percent = rx_percent
        self.normalization_method = normalization_method
        self.normalization_object = normalization_object


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

        if isinstance(rt_dose.TissueHeterogeneityCorrection, basestring):
            heterogeneity_correction = rt_dose.TissueHeterogeneityCorrection
        else:
            heterogeneity_correction = ','.join(rt_dose.TissueHeterogeneityCorrection)

        # Record Medical Record Number
        MRN = rt_plan.PatientID

        # Record gender
        patient_sex = rt_plan.PatientSex.upper()
        if not (patient_sex == 'M' or patient_sex == 'F'):
            patient_sex = '-'

        # Parse and record sim date
        sim_study_date = rt_plan.StudyDate
        sim_study_year = int(sim_study_date[0:4])
        sim_study_month = int(sim_study_date[4:6])
        sim_study_day = int(sim_study_date[6:8])
        sim_study_date_obj = datetime.datetime(sim_study_year, sim_study_month,
                                               sim_study_day)

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
            birth_date_obj = datetime.datetime(birth_year, birth_month, birth_day)
            age = relativedelta(sim_study_date_obj, birth_date_obj).years

        # Record physician initials from ReferringPhysicianName tag
        physician = rt_plan.ReferringPhysicianName.upper()
        if hasattr(rt_plan, 'PhysiciansOfRecord') and not physician:
            physician = rt_plan.PhysiciansOfRecord.upper()

        # Initialize fx and MU counters, iterate over all rx's
        fxs = 0
        total_mu = 0
        fx_grp_seq = rt_plan.FractionGroupSequence  # just to limit characters for later reference
        # Count number of fxs and total MUs
        # Note these are total fxs, not treatment days
        for fxgrp in range(0, len(fx_grp_seq)):
            fxs += fx_grp_seq[fxgrp].NumberOfFractionsPlanned
            for Beam in range(0, fx_grp_seq[fxgrp].NumberOfBeams):
                total_mu += fx_grp_seq[fxgrp].ReferencedBeamSequence[Beam].BeamMeterset

        # This UID must be in all DICOM files associated with this sim study
        study_instance_uid = rt_plan.StudyInstanceUID

        # Record patient position (e.g., HFS, HFP, FFS, or FFP)
        patient_orientation = rt_plan.PatientSetupSequence[0].PatientPosition

        # Contest self-evident, their utility is not (yet)
        plan_time_stamp = rt_plan.RTPlanDate + rt_plan.RTPlanTime
        struct_time_stamp = rt_structure.StructureSetDate + rt_structure.StructureSetTime
        dose_time_stamp = rt_dose.ContentDate + rt_dose.ContentTime

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
                    rx_dose += fx_dose * fxs
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
        if rt_plan_obj['brachy']:
            tx_modality = 'Brachy '
        else:
            beam_seq = rt_plan.BeamSequence
            for beam_num in range(0, len(beam_seq) - 1):
                temp += beam_seq[beam_num].RadiationType + ' '
                first_cp = beam_seq[beam_num].ControlPointSequence[0]
                if first_cp.GantryRotationDirection in {'CW', 'CC'}:
                    temp += 'Arc '
                else:
                    temp += '3D '
                energy_temp = ' ' + str(first_cp.NominalBeamEnergy)
                if beam_seq[beam_num].RadiationType.lower() == 'photon':
                    energy_temp += 'MV '
                elif beam_seq[beam_num].RadiationType.lower() == 'proton':
                    energy_temp += 'MeV '
                elif beam_seq[beam_num].RadiationType.lower() == 'electron':
                    energy_temp += 'MeV '
                if tx_energies.find(energy_temp) < 0:
                    tx_energies += energy_temp
            tx_energies = tx_energies[1:len(tx_energies) - 1]
            if temp.lower().find('photon') > -1:
                if temp.lower().find('photon arc') > -1:
                    tx_modality += 'Photon Arc '
                else:
                    tx_modality += 'Photon 3D '
            if temp.lower().find('electron') > -1:
                if temp.lower().find('electron arc') > -1:
                    tx_modality += 'Electron Arc '
                else:
                    tx_modality += 'Electron 3D '
            elif temp.lower().find('proton') > -1:
                tx_modality += 'Proton '
        tx_modality = tx_modality[0:len(tx_modality) - 1]

        # Will require a yet to be named function to determine this
        # Applicable for brachy and Gamma Knife, not yet supported
        tx_time = 0

        # Record resolution of dose grid
        dose_grid_resolution = [str(round(float(rt_dose.PixelSpacing[0]), 1)),
                                str(round(float(rt_dose.PixelSpacing[1]), 1)),
                                str(round(float(rt_dose.SliceThickness), 1))]
        dose_grid_resolution = ', '.join(dose_grid_resolution)

        # Set object values
        self.mrn = MRN
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
                    print('Importing ' + current_dvh_calc.name)
                    if rt_structures[key]['name'].lower().find('itv') == 0:
                        roi_type = 'ITV'
                    else:
                        roi_type = rt_structures[key]['type']
                    current_roi_name = rt_structures[key]['name']
                    institutional_roi_name = database_rois.get_institutional_roi(current_roi_name, physician)
                    physician_roi_name = database_rois.get_physician_roi(current_roi_name, physician)
                    current_dvh_row = DVHRow(mrn,
                                             study_instance_uid,
                                             institutional_roi_name,
                                             physician_roi_name,
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

        self.mrn = [values[x].mrn for x in dvh_range]
        self.study_instance_uid = [values[x].study_instance_uid for x in dvh_range]
        self.institutional_roi_name = [values[x].institutional_roi_name for x in dvh_range]
        self.physician_roi_name = [values[x].physician_roi_name for x in dvh_range]
        self.roi_name = [values[x].roi_name for x in dvh_range]
        self.roi_type = [values[x].roi_type for x in dvh_range]
        self.volume = [values[x].volume for x in dvh_range]
        self.min_dose = [values[x].min_dose for x in dvh_range]
        self.mean_dose = [values[x].mean_dose for x in dvh_range]
        self.max_dose = [values[x].max_dose for x in dvh_range]
        self.dvh_str = [values[x].dvh_str for x in dvh_range]


class BeamTable:
    def __init__(self, plan_file):

        beam_num = 0
        values = {}
        # Import RT Dose files using dicompyler
        rt_plan = dicom.read_file(plan_file)

        mrn = rt_plan.PatientID
        study_instance_uid = rt_plan.StudyInstanceUID

        for fx_grp in range(0, len(rt_plan.FractionGroupSequence)):
            fx_grp_seq = rt_plan.FractionGroupSequence[fx_grp]
            fxs = int(fx_grp_seq.NumberOfFractionsPlanned)
            fx_grp_beam_count = int(fx_grp_seq.NumberOfBeams)

            for fx_grp_beam in range(0, fx_grp_beam_count):
                beam_seq = rt_plan.BeamSequence[beam_num]
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
                beam_energy = beam_seq.ControlPointSequence[0].NominalBeamEnergy
                beam_type = beam_seq.BeamType

                control_point_count = beam_seq.NumberOfControlPoints
                first_cp = beam_seq.ControlPointSequence[0]
                if beam_seq.BeamType == 'STATIC':
                    final_cp = first_cp
                else:
                    final_cp = beam_seq.ControlPointSequence[control_point_count - 1]
                gantry_start = float(first_cp.GantryAngle)
                gantry_rot_dir = first_cp.GantryRotationDirection
                gantry_end = float(final_cp.GantryAngle)
                collimator_angle = float(first_cp.BeamLimitingDeviceAngle)
                if collimator_angle > 180:
                    collimator_angle -= 360
                couch_angle = float(first_cp.PatientSupportAngle)
                if couch_angle > 180:
                    couch_angle -= 360

                # If beam is an arc, return average SSD, otherwise
                if gantry_rot_dir in {'CW', 'CC'}:
                    ssd = 0
                    for CP in range(0, control_point_count):
                        ssd += round(float(beam_seq.ControlPointSequence[CP].SourceToSurfaceDistance) / 10, 2)
                    ssd /= control_point_count
                    if gantry_rot_dir == 'CW':
                        if gantry_start > 176:
                            gantry_start -= float(360)
                        if gantry_end > 180:
                            gantry_end -= float(360)
                    elif gantry_rot_dir == 'CC':
                        if gantry_start > 184:
                            gantry_start -= float(360)
                        if gantry_end > 180:
                            gantry_end -= float(360)
                else:
                    gantry_rot_dir = '-'
                    ssd = float(first_cp.SourceToSurfaceDistance) / 10

                current_beam = BeamRow(mrn, study_instance_uid, beam_num + 1,
                                       beam_name, fx_grp + 1, fxs,
                                       fx_grp_beam_count, beam_dose, beam_mu, radiation_type,
                                       beam_energy, beam_type, control_point_count,
                                       gantry_start, gantry_end, gantry_rot_dir,
                                       collimator_angle, couch_angle, isocenter, ssd, treatment_machine)

                values[beam_num] = current_beam
                beam_num += 1

        self.count = beam_num
        beam_range = range(0, self.count)

        # Rearrange values into separate variables
        self.mrn = [values[x].mrn for x in beam_range]
        self.study_instance_uid = [values[x].study_instance_uid for x in beam_range]
        self.beam_number = [values[x].beam_number for x in beam_range]
        self.beam_name = [values[x].beam_name for x in beam_range]
        self.fx_group = [values[x].fx_group for x in beam_range]
        self.fxs = [values[x].fxs for x in beam_range]
        self.fx_grp_beam_count = [values[x].fx_grp_beam_count for x in beam_range]
        self.beam_dose = [values[x].beam_dose for x in beam_range]
        self.beam_mu = [values[x].beam_mu for x in beam_range]
        self.radiation_type = [values[x].radiation_type for x in beam_range]
        self.beam_energy = [values[x].beam_energy for x in beam_range]
        self.beam_type = [values[x].beam_type for x in beam_range]
        self.control_point_count = [values[x].control_point_count for x in beam_range]
        self.gantry_start = [values[x].gantry_start for x in beam_range]
        self.gantry_end = [values[x].gantry_end for x in beam_range]
        self.gantry_rot_dir = [values[x].gantry_rot_dir for x in beam_range]
        self.collimator_angle = [values[x].collimator_angle for x in beam_range]
        self.couch_angle = [values[x].couch_angle for x in beam_range]
        self.isocenter = [values[x].isocenter for x in beam_range]
        self.ssd = [values[x].ssd for x in beam_range]
        self.treatment_machine = [values[x].treatment_machine for x in beam_range]


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
            fx_grp_number = i + 1
            fx_dose = 0
            fx_grp_name = 'default'
            plan_name = rt_plan.RTPlanLabel

            for j in range(0, fx_grp_seq[i].NumberOfBeams):
                fx_dose += fx_grp_seq[i].ReferencedBeamSequence[j].BeamDose

            fxs = fx_grp_seq[i].NumberOfFractionsPlanned
            rx_percent = float(100)
            normalization_method = 'point'
            normalization_object = 'calc point'

            # Because DICOM does not contain Rx's explicitly, the user must create
            # a point in the RT Structure file called 'rx[#]: ' per rx
            roi_counter = 0
            roi_seq = rt_structure.StructureSetROISequence  # just limit num characters in code
            roi_count = len(roi_seq)
            # set defaults in case rx and tx points are not found

            rx_pt_found = False
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
        # Rearrange values into separate variables
        self.mrn = [values[x].mrn for x in fx_group_range]
        self.study_instance_uid = [values[x].study_instance_uid for x in fx_group_range]
        self.plan_name = [values[x].plan_name for x in fx_group_range]
        self.fx_grp_name = [values[x].fx_grp_name for x in fx_group_range]
        self.fx_grp_number = [values[x].fx_grp_number for x in fx_group_range]
        self.fx_grp_count = [values[x].fx_grp_count for x in fx_group_range]
        self.fx_dose = [values[x].fx_dose for x in fx_group_range]
        self.fxs = [values[x].fxs for x in fx_group_range]
        self.rx_dose = [values[x].rx_dose for x in fx_group_range]
        self.rx_percent = [values[x].rx_percent for x in fx_group_range]
        self.normalization_method = [values[x].normalization_method for x in fx_group_range]
        self.normalization_object = [values[x].normalization_object for x in fx_group_range]
        self.count = fx_group_count


if __name__ == '__main__':
    pass
