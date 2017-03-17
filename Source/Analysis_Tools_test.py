#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:48:19 2017

@author: nightowl
"""

import numpy as np
from SQL_Tools import Query_SQL


class DVH:
    def __init__(self, *ConditionStr):
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
        RxDoses = np.zeros(NumRows)
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

            Condition = "MRN = '" + str(row[0])
            Condition += "' and StudyInstanceUID = '"
            Condition += str(StudyUIDs[DVH_Counter]) + "'"
            RxDoseCursor = Query_SQL('Plans', 'RxDose', Condition)
            RxDoses[DVH_Counter] = RxDoseCursor[0][0]

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

        self.MRN = MRNs
        self.StudyUID = StudyUIDs
        self.ROI_Name = ROI_Names
        self.Type = Types
        self.RxDose = RxDoses
        self.Volume = Volumes
        self.MinDose = MinDoses
        self.MeanDose = MeanDoses
        self.MaxDose = MaxDoses
        self.DVH = DVHs

        def Sort(self, SortedIndices):
            self.MRN = [self.MRN[x] for x in SortedIndices]
            self.StudyUID = [self.StudyUID[x] for x in SortedIndices]
            self.ROI_Name = [self.ROI_Name[x] for x in SortedIndices]
            self.Type = [self.Type[x] for x in SortedIndices]
            self.Volume = [round(self.Volume[x], 2) for x in SortedIndices]
            self.MinDose = [round(self.MinDose[x], 2) for x in SortedIndices]
            self.MeanDose = [round(self.MeanDose[x], 2) for x in SortedIndices]
            self.MaxDose = [round(self.MaxDose[x], 2) for x in SortedIndices]

            DVH_Temp = np.empty_like(self.DVH)
            for x in range(0, np.size(self.DVH, 1)):
                np.copyto(DVH_Temp[:, x], self.DVH[:, SortedIndices[x]])
            np.copyto(self.DVH, DVH_Temp)


class DVH_Spread:
    def __init__(self, DVHs):
        DVH_Len = np.size(DVHs, 0)

        Min = np.zeros(DVH_Len)
        Q1 = np.zeros(DVH_Len)
        Mean = np.zeros(DVH_Len)
        Median = np.zeros(DVH_Len)
        Q3 = np.zeros(DVH_Len)
        Max = np.zeros(DVH_Len)
        Std = np.zeros(DVH_Len)
        Low2Std = np.zeros(DVH_Len)
        Low1Std = np.zeros(DVH_Len)
        High1Std = np.zeros(DVH_Len)
        High2Std = np.zeros(DVH_Len)

        for x in range(0, DVH_Len - 1):
            Min[x] = np.min(DVHs[x, :])
            Q1[x] = np.percentile(DVHs[x, :], 25)
            Mean[x] = np.mean(DVHs[x, :])
            Median[x] = np.median(DVHs[x, :])
            Q3[x] = np.percentile(DVHs[x, :], 75)
            Max[x] = np.max(DVHs[x, :])
            Std[x] = np.std(DVHs[x, :])

        Low2Std = np.subtract(Mean, np.multiply(2, Std))
        Low1Std = np.subtract(Mean, Std)
        High1Std = np.add(Mean, Std)
        High2Std = np.add(Mean, np.multiply(2, Std))

        self.Min = Min
        self.Low2Std = Low2Std
        self.Low1Std = Low1Std
        self.Q1 = Q1
        self.Mean = Mean
        self.Median = Median
        self.Q3 = Q3
        self.High1Std = High1Std
        self.High2Std = High2Std
        self.Max = Max


# input equals 2D numpy array, output: 1D numpy array
def AvgDVH(DVHs):

    NumDVHs = np.size(DVHs, 1)
    AvgDVH = np.zeros([np.size(DVHs, 0)])
    for x in range(0, NumDVHs - 1):
        AvgDVH += DVHs[:, x] / np.max(DVHs[:, x])
    AvgDVH /= NumDVHs
    AvgDVH /= max(AvgDVH)

    return AvgDVH


def PercentCoverage(DVHs, Doses):

    if np.size(Doses) == 1:
        Doses = np.multiply(np.ones(np.size(DVHs, 0)), Doses)

    NumDVHs = np.size(DVHs, 1)
    Coverage = np.zeros(NumDVHs)
    for x in range(0, NumDVHs):
        Coverage[x] = VolumeOfDose(DVHs[:, x], Doses[x]) * 100

    return Coverage


def DosesToVolume(DVHs, Volume, ROI_Volumes):

    NumDVHs = np.size(DVHs, 1)
    Doses = np.zeros(NumDVHs)
    for x in range(0, NumDVHs):
        Doses[x] = DoseToVolume(DVHs[:, x], Volume, ROI_Volumes[x])

    return Doses


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


def GetSortedIndices(ToBeSorted, *Order):

    Sorted = np.argsort(ToBeSorted)

    if Order and Order[0].lower() == 'descend':
        Sorted = Sorted[::-1]

    return Sorted


if __name__ == '__main__':
    pass
