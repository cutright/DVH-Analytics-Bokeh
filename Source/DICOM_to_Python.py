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
    def __init__(self, Plan_UID, ROI_Name, Type, Volume, MinDose, MeanDose,
                 MaxDose, DoseBinSize, DoseUnits, VolumeString, VolumeUnits):
        self.Plan_UID = Plan_UID
        self.ROI_Name = ROI_Name
        self.Type = Type
        self.Volume = Volume
        self.MinDose = MinDose
        self.MeanDose = MeanDose
        self.MaxDose = MaxDose
        self.DoseBinSize = DoseBinSize
        self.DoseUnits = DoseUnits
        self.VolumeString = VolumeString
        self.VolumeUnits = VolumeUnits


class Plan:
    def __init__(self, MRN, PlanID, Birthdate, Age, Sex, PlanDate,
                 RadOnc, TxSite, RxDose, Fractions, Modality, MUs,
                 Plan_UID):
        self.MRN = MRN
        self.PlanID = PlanID
        self.Birthdate = Birthdate
        self.Age = Age
        self.Sex = Sex
        self.PlanDate = PlanDate
        self.RadOnc = RadOnc
        self.TxSite = TxSite
        self.RxDose = RxDose
        self.Fractions = Fractions
        self.Modality = Modality
        self.MUs = MUs
        self.Plan_UID = Plan_UID


def Create_ROI_PyTable(StructureFile, DoseFile):
    # Import RT Structure and RT Dose files using dicompyler
    RT_St = dicomparser.DicomParser(StructureFile)
    Structures = RT_St.GetStructures()
    ROI_Count = len(Structures)
    # ROI_Count = 10

    DICOM_RT_St = dicom.read_file(StructureFile)
    MRN = DICOM_RT_St.PatientID
    Plan_UID = MRN

    ROI_List = {}

    ROI_List_Counter = 1

    for ROI_Counter in range(1, ROI_Count):
        # Import DVH from RT Structure and RT Dose files
        if Structures[ROI_Counter]['type'] != 'MARKER':
            Current_DVH = dvhcalc.get_dvh(StructureFile, DoseFile, ROI_Counter)
            if Current_DVH.volume > 0:
                print('Importing ' + Current_DVH.name)
                Current_ROI = ROI(Plan_UID,
                                  Structures[ROI_Counter]['name'],
                                  Structures[ROI_Counter]['type'],
                                  Current_DVH.volume,
                                  Current_DVH.min,
                                  Current_DVH.mean,
                                  Current_DVH.max,
                                  Current_DVH.bins[1],
                                  Current_DVH.dose_units,
                                  ','.join(['%.2f' % num for num in Current_DVH.counts]),
                                  Current_DVH.volume_units)
                ROI_List[ROI_List_Counter] = Current_ROI
                ROI_List_Counter += 1
    return ROI_List


def Create_Plan_Py(PlanFile, StructureFile):
    # Import RT Dose files using dicompyler
    RT_Plan = dicom.read_file(PlanFile)
    RT_Plan_dicompyler = dicomparser.DicomParser(PlanFile)
    RT_St = dicom.read_file(StructureFile)

    MRN = RT_Plan.PatientID

    # Will require a yet to be named function to determine this by
    # querying the SQL database
    PlanID = 1

    BirthDate = RT_Plan.PatientBirthDate
    if not BirthDate:
        BirthDate = '18000101'
    BirthYear = int(BirthDate[0:4])
    BirthMonth = int(BirthDate[4:6])
    BirthDay = int(BirthDate[6:8])
    BirthDateObj = datetime(BirthYear, BirthMonth, BirthDay)

    Sex = RT_Plan.PatientSex
    if Sex == 'M':
        pass
    elif Sex == 'F':
        pass
    else:
        Sex = '-'

    PlanDate = RT_Plan.StudyDate
    PlanYear = int(PlanDate[0:4])
    PlanMonth = int(PlanDate[4:6])
    PlanDay = int(PlanDate[6:8])
    PlanDateObj = datetime(PlanYear, PlanMonth, PlanDay)

    Age = relativedelta(PlanDateObj, BirthDateObj).years

    RadOnc = RT_Plan.ReferringPhysicianName

    TxSite = RT_Plan.RTPlanLabel

    Fractions = 0
    MUs = 0
    for FxGroup in range(0, len(RT_Plan.FractionGroupSequence)):
        Fractions += RT_Plan.FractionGroupSequence[FxGroup].NumberOfFractionsPlanned
        for BeamNum in range(0, RT_Plan.FractionGroupSequence[FxGroup].NumberOfBeams):
            MUs += RT_Plan.FractionGroupSequence[FxGroup].ReferencedBeamSequence[BeamNum].BeamMeterset

    # Because DICOM does not contain Rx's explicitly, the user must create
    # a point in the RT Structure file called 'rx [total dose]'
    RxFound = 0
    ROI_Counter = 0
    ROI_Count = len(RT_St.StructureSetROISequence) - 1
    RxString = ''
    ROI_Seq = RT_St.StructureSetROISequence
    while (not RxFound) and (ROI_Counter < ROI_Count):
        if len(ROI_Seq[ROI_Counter].ROIName) > 2:
            if ROI_Seq[ROI_Counter].ROIName[0:2].lower() == 'rx':
                RxString = ROI_Seq[ROI_Counter].ROIName
                RxFound = 1
            else:
                ROI_Counter += 1
        else:
            ROI_Counter += 1
    if not RxString:
        RxDose = RT_Plan_dicompyler.GetPlan()['rxdose']/100
    else:
        RxString = RxString.lower()
        RxString = RxString[3:RxString.rfind('gy')]
        while RxString[len(RxString)-1] == ' ':
            RxString = RxString[0:len(RxString)-1]
        RxDose = float(RxString[RxString.rfind(' '):len(RxString)])
        if RxString.find('x') == -1:
            RxDose = float(RxString[RxString.rfind(' '):len(RxString)])
        else:
            RxDose = float(RxString[RxString.rfind(' '):len(RxString)]) * Fractions

    # This assumes that Plans are either 100% Arc plans or 100% Static Angle
    FirstCP = RT_Plan.BeamSequence[0].ControlPointSequence[0]
    if FirstCP.GantryRotationDirection in {'CW', 'CC'}:
        Modality = 'Arc'
    else:
        Modality = '3D'

    # Will require a yet to be named function to determine this by
    # querying the SQL database
    ROI_UID = 1

    Plan_Py = Plan(MRN, PlanID, BirthDate, Age, Sex, PlanDate,
                   RadOnc, TxSite, RxDose, Fractions, Modality, MUs, ROI_UID)

    return Plan_Py

if __name__ == '__main__':
    pass
