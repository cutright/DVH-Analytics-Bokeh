#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# DICOM_to_Python.py
"""
Import DICOM RT Dose, Structure, and Plan files into Python objects
Created on Sun Feb 26 11:06:28 2017
@author: Dan Cutright, PhD
"""

import dicom  # PyDICOM
from dicompylercore import dicomparser, dvhcalc  # DICOMPyler.com
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ROI_Name_Manager import *


# Each ROI class object contains data to fill an entire row of the SQL table 'DVHs'
# This code will generate a list of ROI class objects
# There will be a ROI class per structure of a Plan
class DVHRow:
    def __init__(self, MRN, study_instance_uid, institutional_roi_name, physician_roi_name,
                 roi_name, roi_type, volume, min_dose, mean_dose, max_dose, dose_bin_size, dvh_str):
        self.MRN = MRN
        self.study_instance_uid = study_instance_uid
        self.institutional_roi_name = institutional_roi_name
        self.physician_roi_name = physician_roi_name
        self.roi_name = roi_name
        self.roi_type = roi_type
        self.volume = volume
        self.min_dose = min_dose
        self.mean_dose = mean_dose
        self.max_dose = max_dose
        self.dose_bin_size = dose_bin_size
        self.dvh_str = dvh_str


# Each BeamInfo class object contains data to fill an entire row of the SQL table 'Beams'
# This code will generate a list of BeamInfo class objects
# There will be a Beam class per beam of a Plan
class BeamRow:
    def __init__(self, MRN, study_instance_uid, beam_num, description,
                 fx_group, fxs, fx_group_beam_count, dose,
                 mu, radiation_type, energy, delivery_type, cp_count,
                 gantry_start, gantry_end, gantry_rot_dir, col_angle,
                 couch_ang, isocenter_coord, ssd):
        self.MRN = MRN
        self.study_instance_uid = study_instance_uid
        self.beam_num = beam_num
        self.description = description
        self.fx_group = fx_group
        self.fxs = fxs
        self.fx_group_beam_count = fx_group_beam_count
        self.dose = dose
        self.mu = mu
        self.radiation_type = radiation_type
        self.energy = energy
        self.delivery_type = delivery_type
        self.cp_count = cp_count
        self.gantry_start = gantry_start
        self.gantry_end = gantry_end
        self.gantry_rot_dir = gantry_rot_dir
        self.col_angle = col_angle
        self.couch_ang = couch_ang
        self.isocenter_coord = isocenter_coord
        self.ssd = ssd


# Each Plan class object contains data to fill an entire row of the SQL table 'Plans'
# There will be a Plan class per structure of a Plan
class PlanRow:
    def __init__(self, plan_file, structure_file, dose_file):
        rt_plan = dicom.read_file(plan_file)
        rt_plan_dicompyler = dicomparser.DicomParser(plan_file)
        rt_plan_obj = rt_plan_dicompyler.GetPlan()
        rt_structure = dicom.read_file(structure_file)
        rt_dose = dicom.read_file(dose_file)

        MRN = rt_plan.PatientID

        sex = rt_plan.PatientSex.upper()
        if not (sex == 'M' or sex == 'F'):
            sex = '-'

        sim_study_date = rt_plan.StudyDate
        sim_study_year = int(sim_study_date[0:4])
        sim_study_month = int(sim_study_date[4:6])
        sim_study_day = int(sim_study_date[6:8])
        sim_study_date_obj = datetime(sim_study_year, sim_study_month,
                                      sim_study_day)

        birth_date = rt_plan.PatientBirthDate
        if not birth_date:
            birth_date = '(NULL)'
            age = '(NULL)'
        else:
            birth_year = int(birth_date[0:4])
            birth_month = int(birth_date[4:6])
            birth_day = int(birth_date[6:8])
            birth_date_obj = datetime(birth_year, birth_month, birth_day)
            age = relativedelta(sim_study_date_obj, birth_date_obj).years

        rad_onc = rt_plan.ReferringPhysicianName

        tx_site = rt_plan.RTPlanLabel

        fxs = 0
        mus = 0
        fx_grp_seq = rt_plan.FractionGroupSequence
        for fxgrp in range(0, len(fx_grp_seq)):
            fxs += fx_grp_seq[fxgrp].NumberOfFractionsPlanned
            for Beam in range(0, fx_grp_seq[fxgrp].NumberOfBeams):
                mus += fx_grp_seq[fxgrp].ReferencedBeamSequence[Beam].BeamMeterset

        study_instance_uid = rt_plan.StudyInstanceUID
        patient_orientation = rt_plan.PatientSetupSequence[0].PatientPosition

        plan_time_stamp = rt_plan.RTPlanDate + rt_plan.RTPlanTime
        roi_time_stamp = rt_structure.StructureSetDate + rt_structure.StructureSetTime
        dose_time_stamp = rt_dose.ContentDate + rt_dose.ContentTime

        tps_manufacturer = rt_plan.Manufacturer
        tps_software_name = rt_plan.ManufacturerModelName
        tps_software_version = rt_plan.SoftwareVersions[0]

        # Because DICOM does not contain Rx's explicitly, the user must create
        # a point in the RT Structure file called 'rx [total dose]'
        rx_found = 0
        roi_counter = 0
        roi_count = len(rt_structure.StructureSetROISequence) - 1
        rx_str = ''
        roi_seq = rt_structure.StructureSetROISequence
        while (not rx_found) and (roi_counter < roi_count):
            if len(roi_seq[roi_counter].ROIName) > 2:
                if roi_seq[roi_counter].ROIName.lower().find('rx') == -1:
                    roi_counter += 1
                else:
                    rx_str = roi_seq[roi_counter].ROIName
                    rx_found = 1
            else:
                roi_counter += 1
        if not rx_str:
            rx_dose = float(rt_plan_obj['rxdose']) / 100
        else:
            rx_str = rx_str.lower().strip('rx').strip(':').strip('gy').strip()
            x = rx_str.find('x')
            if x == -1:
                rx_dose = float(rx_str)
            else:
                fx_from_str = float(rx_str[0:x - 1])
                fx_dose = float(rx_str[x + 1:len(rx_str)])
                rx_dose = fx_dose * fx_from_str

        # This assumes that Plans are either 100% Arc plans or 100% Static Angle
        # Note that the beams class will have this information on a per beam basis
        tx_modality = ''
        energies = ' '
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
                if energies.find(energy_temp) < 0:
                    energies += energy_temp
            energies = energies[1:len(energies) - 1]
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
        tx_time = 0

        dose_grid_resolution = []
        dose_grid_resolution.append(str(round(float(rt_dose.PixelSpacing[0]), 1)))
        dose_grid_resolution.append(str(round(float(rt_dose.PixelSpacing[1]), 1)))
        dose_grid_resolution.append(str(round(float(rt_dose.SliceThickness), 1)))
        dose_grid_resolution = ', '.join(dose_grid_resolution)

        self.MRN = MRN
        self.birthdate = birth_date
        self.age = age
        self.sex = sex
        self.sim_study_date = sim_study_date
        self.rad_onc = rad_onc
        self.tx_site = tx_site
        self.rx_dose = rx_dose
        self.fxs = fxs
        self.energies = energies
        self.study_instance_uid = study_instance_uid
        self.patient_orientation = patient_orientation
        self.plan_time_stamp = plan_time_stamp
        self.roi_time_stamp = roi_time_stamp
        self.dose_time_stamp = dose_time_stamp
        self.tps_manufacturer = tps_manufacturer
        self.tps_software_name = tps_software_name
        self.tps_software_version = tps_software_version
        self.tx_modality = tx_modality
        self.tx_time = tx_time
        self.total_mu = mus
        self.dose_grid_resolution = dose_grid_resolution


class DVHTable:
    def __init__(self, structure_file, dose_file):
        # Get ROI Category Map
        database_rois = DatabaseROIs()

        # Import RT Structure and RT Dose files using dicompyler
        rt_structure_dicom = dicom.read_file(structure_file)
        MRN = rt_structure_dicom.PatientID
        study_uid = rt_structure_dicom.StudyInstanceUID

        rt_structure = dicomparser.DicomParser(structure_file)
        rt_structures = rt_structure.GetStructures()

        physician = rt_structure_dicom.ReferringPhysicianName.upper()

        values = {}
        row_counter = 0
        for key in rt_structures:
            # Import DVH from RT Structure and RT Dose files
            if rt_structures[key]['type'] != 'MARKER':
                current_dvh_calc = dvhcalc.get_dvh(structure_file, dose_file, key)
                if current_dvh_calc.volume > 0:
                    print('Importing ' + current_dvh_calc.name)
                    if rt_structures[key]['name'].lower().find('itv') == 0:
                        st_type = 'ITV'
                    else:
                        st_type = rt_structures[key]['type']
                    current_roi_name = rt_structures[key]['name'].lower()
                    inst_roi = database_rois.get_institutional_roi(current_roi_name,
                                                                   physician)
                    phys_roi = database_rois.get_physician_roi(current_roi_name,
                                                               physician)
                    current_dvh_row = DVHRow(MRN,
                                             study_uid,
                                             inst_roi,
                                             phys_roi,
                                             current_roi_name,
                                             st_type,
                                             current_dvh_calc.volume,
                                             current_dvh_calc.min,
                                             current_dvh_calc.mean,
                                             current_dvh_calc.max,
                                             current_dvh_calc.bins[1],
                                             ','.join(['%.2f' % num for num in current_dvh_calc.counts]))
                    values[row_counter] = current_dvh_row
                    row_counter += 1

        self.count = row_counter
        dvh_range = range(0, self.count)

        self.MRN = [values[x].MRN for x in dvh_range]
        self.study_instance_uid = [values[x].study_instance_uid for x in dvh_range]
        self.institutional_roi_name = [values[x].institutional_roi_name for x in dvh_range]
        self.physician_roi_name = [values[x].physician_roi_name for x in dvh_range]
        self.roi_name = [values[x].roi_name for x in dvh_range]
        self.roi_type = [values[x].roi_type for x in dvh_range]
        self.volume = [values[x].volume for x in dvh_range]
        self.min_dose = [values[x].min_dose for x in dvh_range]
        self.mean_dose = [values[x].mean_dose for x in dvh_range]
        self.max_dose = [values[x].max_dose for x in dvh_range]
        self.dose_bin_size = [values[x].dose_bin_size for x in dvh_range]
        self.dvh_str = [values[x].dvh_str for x in dvh_range]


class BeamTable:
    def __init__(self, plan_file):

        beam_num = 0
        values = {}
        # Import RT Dose files using dicompyler
        rt_plan = dicom.read_file(plan_file)

        MRN = rt_plan.PatientID
        study_instance_uid = rt_plan.StudyInstanceUID

        for fx_grp in range(0, len(rt_plan.FractionGroupSequence)):
            FxGrpSeq = rt_plan.FractionGroupSequence[fx_grp]
            fxs = int(FxGrpSeq.NumberOfFractionsPlanned)
            fx_grp_beam_count = int(FxGrpSeq.NumberOfBeams)

            for fx_grp_beam in range(0, fx_grp_beam_count):
                beam_seq = rt_plan.BeamSequence[beam_num]
                description = beam_seq.BeamDescription
                ref_beam_seq = FxGrpSeq.ReferencedBeamSequence[fx_grp_beam]

                dose = float(ref_beam_seq.BeamDose)
                mu = float(ref_beam_seq.BeamMeterset)

                iso_coord = []
                iso_coord.append(str(ref_beam_seq.BeamDoseSpecificationPoint[0]))
                iso_coord.append(str(ref_beam_seq.BeamDoseSpecificationPoint[1]))
                iso_coord.append(str(ref_beam_seq.BeamDoseSpecificationPoint[2]))
                iso_coord = ','.join(iso_coord)

                radiation_type = beam_seq.RadiationType
                energy = beam_seq.ControlPointSequence[0].NominalBeamEnergy
                delivery_type = beam_seq.BeamType

                cp_count = beam_seq.NumberOfControlPoints
                first_cp = beam_seq.ControlPointSequence[0]
                final_cp = beam_seq.ControlPointSequence[cp_count - 1]
                gantry_start = float(first_cp.GantryAngle)
                gantry_rot_dir = first_cp.GantryRotationDirection
                gantry_end = float(final_cp.GantryAngle)
                col_angle = float(first_cp.BeamLimitingDeviceAngle)
                couch_ang = float(first_cp.PatientSupportAngle)

                # If beam is an arc, return average SSD, otherwise
                if gantry_rot_dir in {'CW', 'CC'}:
                    ssd = 0
                    for CP in range(0, cp_count - 1):
                        ssd += round(float(beam_seq.ControlPointSequence[CP].SourceToSurfaceDistance) / 10, 2)
                    ssd /= cp_count
                else:
                    gantry_rot_dir = '-'
                    ssd = float(first_cp.SourceToSurfaceDistance) / 10

                current_beam = BeamRow(MRN, study_instance_uid, beam_num + 1,
                                      description, fx_grp + 1, fxs,
                                      fx_grp_beam_count, dose, mu, radiation_type,
                                      energy, delivery_type, cp_count,
                                      gantry_start, gantry_end, gantry_rot_dir,
                                      col_angle, couch_ang, iso_coord, ssd)

                values[beam_num] = current_beam
                beam_num += 1

        self.count = beam_num
        beam_range = range(0, self.count)

        # Rearrange values into separate variables
        self.MRN = [values[x].MRN for x in beam_range]
        self.study_instance_uid = [values[x].study_instance_uid for x in beam_range]
        self.beam_num = [values[x].beam_num for x in beam_range]
        self.description = [values[x].description for x in beam_range]
        self.fx_group = [values[x].fx_group for x in beam_range]
        self.fxs = [values[x].fxs for x in beam_range]
        self.fx_group_beam_count = [values[x].fx_group_beam_count for x in beam_range]
        self.dose = [values[x].dose for x in beam_range]
        self.mu = [values[x].mu for x in beam_range]
        self.radiation_type = [values[x].radiation_type for x in beam_range]
        self.energy = [values[x].energy for x in beam_range]
        self.delivery_type = [values[x].delivery_type for x in beam_range]
        self.cp_count = [values[x].cp_count for x in beam_range]
        self.gantry_start = [values[x].gantry_start for x in beam_range]
        self.gantry_end = [values[x].gantry_end for x in beam_range]
        self.gantry_rot_dir = [values[x].gantry_rot_dir for x in beam_range]
        self.col_angle = [values[x].col_angle for x in beam_range]
        self.couch_ang = [values[x].couch_ang for x in beam_range]
        self.isocenter_coord = [values[x].isocenter_coord for x in beam_range]
        self.ssd = [values[x].ssd for x in beam_range]


if __name__ == '__main__':
    pass
