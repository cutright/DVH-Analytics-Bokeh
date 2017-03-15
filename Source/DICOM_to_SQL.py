#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 22:15:52 2017

@author: nightowl
"""

from SQL_Tools import Insert_Values_DVHs, Insert_Values_Plans, Insert_Values_Beams
from DICOM_to_Python import Create_ROI_PyTable, Create_Plan_Py, Create_Beams_Py
import os
import dicom


class DICOM_FileSet:
    def __init__(self, RTPlan, RTStructure, RTDose):
        self.RTPlan = RTPlan
        self.RTStructure = RTStructure
        self.RTDose = RTDose


def GetFilePaths(StartPath):

    FilePaths = []
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            FilePaths.append(os.path.join(root, name))

    RTPlanFiles = []
    RTPlanStudyUID = []
    RTStructureFiles = []
    RTStructureStudyUID = []
    RTDoseFiles = []
    RTDoseStudyUID = []

    for x in range(0, len(FilePaths) - 1):
        try:
            DICOM_File = dicom.read_file(FilePaths[x])
            if DICOM_File.Modality.lower() == 'rtplan':
                RTPlanFiles.append(FilePaths[x])
                RTPlanStudyUID.append(DICOM_File.StudyInstanceUID)
            elif DICOM_File.Modality.lower() == 'rtstruct':
                RTStructureFiles.append(FilePaths[x])
                RTStructureStudyUID.append(DICOM_File.StudyInstanceUID)
            elif DICOM_File.Modality.lower() == 'rtdose':
                RTDoseFiles.append(FilePaths[x])
                RTDoseStudyUID.append(DICOM_File.StudyInstanceUID)
        except Exception:
            pass

    DICOM_Files = {}
    for a in range(0, len(RTPlanFiles)):
        RTPlan = RTPlanFiles[a]
        for b in range(0, len(RTStructureFiles)):
            if RTPlanStudyUID[a] == RTStructureStudyUID[b]:
                RTStructure = RTStructureFiles[b]
        for c in range(0, len(RTDoseFiles)):
            if RTPlanStudyUID[a] == RTDoseStudyUID[c]:
                RTDose = RTDoseFiles[c]
        CurrentFileSet = DICOM_FileSet(RTPlan, RTStructure, RTDose)
        DICOM_Files[a] = CurrentFileSet

    return DICOM_Files


def DICOM_to_SQL(StartPath):

    FP = GetFilePaths(StartPath)

    for n in range(0, len(FP)):
        Plan_Py = Create_Plan_Py(FP[n].RTPlan, FP[n].RTStructure, FP[n].RTDose)
        Insert_Values_Plans(Plan_Py)
        Beam_PyTable = Create_Beams_Py(FP[n].RTPlan)
        Insert_Values_Beams(Beam_PyTable)
        ROI_PyTable = Create_ROI_PyTable(FP[n].RTStructure, FP[n].RTDose)
        Insert_Values_DVHs(ROI_PyTable)


if __name__ == '__main__':
    DICOM_to_SQL()
