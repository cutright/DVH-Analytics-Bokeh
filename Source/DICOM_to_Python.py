#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 11:06:28 2017

@author: nightowl
"""

import dicom
from dicompylercore import dicomparser, dvhcalc
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ROI:
    def __init__(self, MRN, study_instance_uid, roi_name, roi_type, volume,
                 min_dose, mean_dose, max_dose, dose_bin_size, dvh_str):
        self.MRN = MRN
        self.study_instance_uid = study_instance_uid
        self.roi_name = roi_name
        self.roi_type = roi_type
        self.volume = volume
        self.min_dose = min_dose
        self.mean_dose = mean_dose
        self.max_dose = max_dose
        self.dose_bin_size = dose_bin_size
        self.dvh_str = dvh_str


class Plan:
    def __init__(self, MRN, birthdate, age, sex, sim_study_date, rad_onc,
                 tx_site, rx_dose, fxs, energies, study_instance_uid,
                 patient_orientation, plan_time_stamp, roi_time_stamp,
                 dose_time_stamp, tps_manufacturer, tps_software_name,
                 tps_software_version, tx_modality, tx_time, total_mu):
        self.MRN = MRN
        self.birthdate = birthdate
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
        self.total_mu = total_mu


class BeamInfo:
    def __init__(self, MRN, study_instance_uid, beam_num, description,
                 fx_group, fxs, fx_group_beam_count, beam_dose,
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
        self.beam_dose = beam_dose
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


def get_roi_table(structure_file, dose_file):
    # Import RT Structure and RT Dose files using dicompyler
    rt_structure = dicomparser.DicomParser(structure_file)
    rt_structure_dicom = dicom.read_file(structure_file)
    Structures = rt_structure.GetStructures()

    MRN = rt_structure_dicom.PatientID
    StudyInstanceUID = rt_structure_dicom.StudyInstanceUID

    ROI_PyTable = {}
    ROI_PyTable_Counter = 1
    for key in Structures:
        # Import DVH from RT Structure and RT Dose files
        if Structures[key]['type'] != 'MARKER':
            Current_DVH = dvhcalc.get_dvh(structure_file, dose_file, key)
            if Current_DVH.volume > 0:
                print('Importing ' + Current_DVH.name)
                if Structures[key]['name'].lower().find('itv') == 0:
                    StType = 'ITV'
                else:
                    StType = Structures[key]['type']
                Current_ROI = ROI(MRN,
                                  StudyInstanceUID,
                                  Structures[key]['name'],
                                  StType,
                                  Current_DVH.volume,
                                  Current_DVH.min,
                                  Current_DVH.mean,
                                  Current_DVH.max,
                                  Current_DVH.bins[1],
                                  ','.join(['%.2f' % num for num in
                                            Current_DVH.counts]))
                ROI_PyTable[ROI_PyTable_Counter] = Current_ROI
                ROI_PyTable_Counter += 1
    return ROI_PyTable


def get_plan_table(plan_file, structure_file, dose_file):
    # Import RT Dose files using dicompyler
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
        rx_dose = float(rt_plan_obj['rxdose'])/100
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
        energies = energies[1:len(energies)-1]
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
    tx_modality = tx_modality[0:len(tx_modality)-1]

    # Will require a yet to be named function to determine this
    tx_time = 0

    Plan_Py = Plan(MRN, birth_date, age, sex, sim_study_date, rad_onc, tx_site,
                   rx_dose, fxs, energies, study_instance_uid,
                   patient_orientation, plan_time_stamp, roi_time_stamp,
                   dose_time_stamp, tps_manufacturer, tps_software_name,
                   tps_software_version, tx_modality, tx_time, mus)

    return Plan_Py


def get_beam_table(plan_file):
    beam_table = {}
    beam_num = 0
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
            if gantry_rot_dir in {'CW', 'CC'}:
                ssd = 0
                for CP in range(0, cp_count - 1):
                    ssd += round(float(beam_seq.ControlPointSequence[CP].SourceToSurfaceDistance)/10, 2)
                ssd /= cp_count
            else:
                gantry_rot_dir = '-'
                ssd = float(first_cp.SourceToSurfaceDistance)/10

            CurrentBeam = BeamInfo(MRN, study_instance_uid, beam_num + 1,
                                   description, fx_grp + 1, fxs,
                                   fx_grp_beam_count, dose, mu, radiation_type,
                                   energy, delivery_type, cp_count,
                                   gantry_start, gantry_end, gantry_rot_dir,
                                   col_angle, couch_ang, iso_coord, ssd)

            beam_table[beam_num] = CurrentBeam
            beam_num += 1

    return beam_table


if __name__ == '__main__':
    pass
