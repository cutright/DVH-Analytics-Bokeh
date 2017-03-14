#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:48:19 2017

@author: nightowl
"""

import numpy as np
from SQL_Tools import Query_SQL


class DVH:
    def __init__(self, MRN, StudyUID, ROI_Name, Type, Volume, MinDose,
                 MeanDose, MaxDose, DVH):
        self.MRN = MRN
        self.StudyUID = StudyUID
        self.ROI_Name = ROI_Name
        self.Type = Type
        self.Volume = Volume
        self.MinDose = MinDose
        self.MeanDose = MeanDose
        self.MaxDose = MaxDose
        self.DVH = DVH


def SQL_DVH_to_Py(*ConditionStr):

    Columns = """MRN, StudyInstanceUID, ROIName, Type, Volume, MinDose,
    MeanDose, MaxDose, VolumeString"""
    if ConditionStr:
        Cursor = Query_SQL('DVHs', Columns, ConditionStr[0])
    else:
        Cursor = Query_SQL('DVHs', Columns)

    MaxDVH_Length = 0
    for row in Cursor:
        CurrentDVH_Str = np.array(str(row[8]).split(','))
        CurrentSize = np.size(CurrentDVH_Str)
        if CurrentSize > MaxDVH_Length:
            MaxDVH_Length = CurrentSize

    NumRows = len(Cursor)
    MRNs = {}
    StudyUIDs = {}
    ROI_Names = {}
    Types = {}
    Volumes = np.zeros(NumRows)
    MinDoses = np.zeros(NumRows)
    MeanDoses = np.zeros(NumRows)
    MaxDoses = np.zeros(NumRows)
    DVHs = np.zeros([MaxDVH_Length, len(Cursor)])

    DVH_Counter = 0
    for row in Cursor:
        MRNs[DVH_Counter] = str(row[0])
        StudyUIDs[DVH_Counter] = str(row[1])
        ROI_Names[DVH_Counter] = str(row[2])
        Types[DVH_Counter] = str(row[3])
        Volumes[DVH_Counter] = row[4]
        MinDoses[DVH_Counter] = row[5]
        MeanDoses[DVH_Counter] = row[6]
        MaxDoses[DVH_Counter] = row[7]

        # Process VolumeString to numpy array
        CurrentDVH_Str = np.array(str(row[8]).split(','))
        CurrentDVH = CurrentDVH_Str.astype(np.float)
        if max(CurrentDVH) > 0:
            CurrentDVH /= max(CurrentDVH)
        ZeroFill = np.zeros(MaxDVH_Length - np.size(CurrentDVH))
        DVHs[:, DVH_Counter] = np.concatenate((CurrentDVH, ZeroFill))
        DVH_Counter += 1

    AllDVHs = DVH(MRNs, StudyUIDs, ROI_Names, Types, Volumes, MinDoses,
                  MeanDoses, MaxDoses, DVHs)

    return AllDVHs


# input equals 2D numpy array, output: 1D numpy array
def AvgDVH(DVHs):

    NumDVHs = np.size(DVHs, 1)
    AvgDVH = np.zeros([np.size(DVHs, 0)])
    for x in range(0, NumDVHs - 1):
        AvgDVH += DVHs[:, x] / np.max(DVHs[:, x])
    AvgDVH /= NumDVHs
    AvgDVH /= max(AvgDVH)

    return AvgDVH


# DVH as 1D numpy array, Dose (Gy)
def VolumeOfDose(DVH, Dose):

    DoseBinSize = 0.01
    x = Dose / DoseBinSize
    xRange = [np.floor(x), np.ceil(x)]
    yRange = [DVH[int(np.floor(x))], DVH[int(np.ceil(x))]]
    Vol = np.interp(x, xRange, yRange)

    return Vol


# DVH as 1D numpy array, Volume (cm^3), ROI_Volume (cm^3)
def DoseToVolume(DVH, Volume, ROI_Volume):

    DoseBinSize = 0.01
    DoseHigh = np.argmax(DVH < Volume / ROI_Volume)
    y = Volume / ROI_Volume
    xRange = [DoseHigh - 1, DoseHigh]
    yRange = [DVH[DoseHigh - 1], DVH[DoseHigh]]
    Dose = np.interp(y, yRange, xRange) * DoseBinSize

    return Dose


def SortDVH(DVHs, SortedBy, *Order):

    Sorted = []

    SortedBy = SortedBy.lower()
    if SortedBy == 'mindose':
        Sorted = np.argsort(DVHs.MinDose)
    elif SortedBy == 'meandose':
        Sorted = np.argsort(DVHs.MeanDose)
    elif SortedBy == 'maxdose':
        Sorted = np.argsort(DVHs.MaxDose)
    elif SortedBy == 'volume':
        Sorted = np.argsort(DVHs.Volume)

    if len(Sorted) > 0:
        if Order and Order[0] == 1:
            Sorted = Sorted[::-1]
        DVHs.MRN = [DVHs.MRN[x] for x in Sorted]
        DVHs.StudyUID = [int(DVHs.StudyUID[x]) for x in Sorted]
        DVHs.ROI_Name = [DVHs.ROI_Name[x] for x in Sorted]
        DVHs.Type = [DVHs.Type[x] for x in Sorted]
        DVHs.Volume = [round(DVHs.Volume[x], 2) for x in Sorted]
        DVHs.MinDose = [round(DVHs.MinDose[x], 2) for x in Sorted]
        DVHs.MeanDose = [round(DVHs.MeanDose[x], 2) for x in Sorted]
        DVHs.MaxDose = [round(DVHs.MaxDose[x], 2) for x in Sorted]

        DVH_Temp = np.empty_like(DVHs.DVH)
        for x in range(0, np.size(DVHs.DVH, 1)):
            np.copyto(DVH_Temp[:, x], DVHs.DVH[:, Sorted[x]])
        np.copyto(DVHs.DVH, DVH_Temp)


if __name__ == '__main__':
    pass
