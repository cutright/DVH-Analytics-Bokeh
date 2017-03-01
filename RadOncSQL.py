#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 14:47:25 2017

@author: nightowl
"""

from dicompylercore import dicomparser, dvh, dvhcalc
import dicom
import mysql.connector


class ROI:
    def __init__(self, ROI_UID, PatientID, PlanID, Name, Type, Volume,
                 MinDose, MeanDose, MaxDose, DoseString, VolString):
        self.ROI_UID = ROI_UID
        self.PatientID = PatientID
        self.PlanID = PlanID
        self.Name = Name
        self.Type = Type
        self.Volume = Volume
        self.MinDose = MinDose
        self.MeanDose = MeanDose
        self.MaxDose = MaxDose
        self.DoseString = DoseString
        self.VolString = VolString


class Plan_Info:
    def __init__(self, PatientID, PatientPlanID, Age, Sex, TxStartDate,
                 RadOnc, TxSite, RxDose, Fractions, Modality, MUs, ROI_UID):
        self.PatientID = PatientID
        self.PatientPlanID = PatientPlanID
        self.Age = Age
        self.Sex = Sex
        self.TxStartDate = TxStartDate
        self.RadOnc = RadOnc
        self.TxSite = TxSite
        self.RxDose = RxDose
        self.Fractions = Fractions
        self.Modality = Modality
        self.MUs = MUs
        self.ROI_UID = ROI_UID



def import_dicom_to_RadOncSQL(PlanFile, StructureFile, DoseFile):

    # Import pertinent dicom files using dicompyler code
    RT_Plan = dicomparser.DicomParser(PlanFile)
    RT_St = dicomparser.DicomParser(StructureFile)
    RT_Dose = dicomparser.DicomParser(DoseFile)
    
    # Calculate the DVH of a specific structure
    dvh = dvhcalc.get_dvh(StructureFile, DoseFile, 6)
    
    # Import RT Plan file for DICOM header information using pydicom
    Dicom_RT_Plan = dicom.read_file(PlanFile)
    
    # Get Patient Data to be sent to SQL database
    Plan_to_Import = Patient(Dicom_RT_Plan.PatientID,
                             Dicom_RT_Plan.PatientName,
                             Dicom_RT_Plan.PatientBirthDate,
                             Dicom_RT_Plan.PatientSex,
                             Dicom_RT_Plan.RTPlanDate)
