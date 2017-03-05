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
    def __init__(self, Name, Type, Volume, MinDose, MeanDose, MaxDose,
                 DoseBinSize, DoseUnits, VolumeString, VolumeUnits):
        self.Name = Name
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
                 ROITableUID):
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
        self.ROITableUID = ROITableUID


def Create_ROI_PyTable(StructureFile, DoseFile):
    # Import RT Structure and RT Dose files using dicompyler
    RT_St = dicomparser.DicomParser(StructureFile)
    Structures = RT_St.GetStructures()
    # ROI_Count = len(Structures)
    ROI_Count = 10

    ROI_List = {}

    ROI_List_Counter = 1

    for ROI_Counter in range(1, ROI_Count):
        # Import DVH from RT Structure and RT Dose files
        if Structures[ROI_Counter]['type'] != 'MARKER':
            Current_DVH = dvhcalc.get_dvh(StructureFile, DoseFile, ROI_Counter)
            if Current_DVH.volume > 0:
                print('Importing ' + Current_DVH.name)
                Current_ROI = ROI(Structures[ROI_Counter]['name'],
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


def Create_Plan_Py(PlanFile):
    # Import RT Dose files using dicompyler
    RT_Plan = dicom.read_file(PlanFile)

    MRN = RT_Plan.PatientID

    # Will require a yet to be named function to determine this by
    # querying the SQL database
    PlanID = 1

    BirthDate = RT_Plan.PatientBirthDate
    BirthYear = int(BirthDate[0:4])
    BirthMonth = int(BirthDate[4:6])
    BirthDay = int(BirthDate[6:8])
    BirthDateObj = datetime(BirthYear, BirthMonth, BirthDay)

    Sex = RT_Plan.PatientSex
    if Sex is not 'M' or 'F':
        Sex = '-'

    PlanDate = RT_Plan.StudyDate
    PlanYear = int(PlanDate[0:4])
    PlanMonth = int(PlanDate[4:6])
    PlanDay = int(PlanDate[6:8])
    PlanDateObj = datetime(PlanYear, PlanMonth, PlanDay)

    Age = relativedelta(BirthDateObj, PlanDateObj).years

    RadOnc = RT_Plan.ReferringPhysicianName

    # StudyDescription from RT Plan DICOM is required to be named
    # [TxSite] [fractions] x [RxDose]Gy
    # The following code parses the StudyDescription (or plan name)
    StudyName = RT_Plan.StudyDescription
    FinalSpaceIndex = StudyName.rfind(' ')
    TxSite_Fx = StudyName[0:StudyName.find(' x ')]

    TxSite = StudyName[0:TxSite_Fx.rfind(' ') - 1]
    RxDose = float(StudyName[FinalSpaceIndex + 1:len(StudyName) - 2])
    Fractions = int(TxSite_Fx[TxSite_Fx.rfind(' ') + 1:len(TxSite_Fx)])

    # This assumes that Plans are either 100% Arc plans or 100% Static Angle
    FirstCP = RT_Plan.BeamSequence[0].ControlPointSequence[0]
    if FirstCP.GantryRotationDirection is not 'NONE':
        Modality = '3D'
    else:
        Modality = 'Arc'

    # Replace with code to extract MU Meterset from dicom
    MUs = 3000

    # Will require a yet to be named function to determine this by
    # querying the SQL database
    ROI_UID = 1

    Plan_Py = Plan(MRN, PlanID, BirthDate, Age, Sex, PlanDate,
                   RadOnc, TxSite, RxDose, Fractions, Modality, MUs, ROI_UID)

    return Plan_Py

if __name__ == '__main__':
    pass
