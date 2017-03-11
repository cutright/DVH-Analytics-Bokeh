#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:48:19 2017

@author: nightowl
"""

import numpy as np
from SQL_Tools import Query_SQL


class DVH:
    def __init__(self, MRN, PlanID, ROI_Name, Type, Volume, DoseBinSize, DVH):
        self.MRN = MRN
        self.PlanID = PlanID
        self.ROI_Name = ROI_Name
        self.Type = Type
        self.Volume = Volume
        self.DoseBinSize = DoseBinSize
        self.DVH = DVH


def SQL_DVH_to_Py(*ConditionStr):

    Columns = 'MRN, PlanID, ROIName, Type, Volume, DoseBinSize, VolumeString'
    if ConditionStr:
        Cursor = Query_SQL('DVHs', Columns, ConditionStr[0])
    else:
        Cursor = Query_SQL('DVHs', Columns)

    MaxDVH_Length = 0
    for row in Cursor:
        CurrentDVH_Str = np.array(str(row[6]).split(','))
        CurrentSize = np.size(CurrentDVH_Str)
        if CurrentSize > MaxDVH_Length:
            MaxDVH_Length = CurrentSize

    NumRows = len(Cursor)
    MRNs = {}
    PlanIDs = np.zeros(NumRows)
    ROI_Names = {}
    Types = {}
    Volumes = np.zeros(NumRows)
    DoseBinSizes = np.zeros(NumRows)
    DVHs = np.zeros([MaxDVH_Length, len(Cursor)])

    DVH_Counter = 0
    for row in Cursor:

        MRNs[DVH_Counter] = str(row[0])
        PlanIDs[DVH_Counter] = row[1]
        ROI_Names[DVH_Counter] = str(row[2])
        Types[DVH_Counter] = str(row[3])
        Volumes[DVH_Counter] = row[4]
        DoseBinSizes[DVH_Counter] = row[5]

        # Process VolumeString to numpy array
        CurrentDVH_Str = np.array(str(row[6]).split(','))
        CurrentDVH = CurrentDVH_Str.astype(np.float)
        if max(CurrentDVH) > 0:
            CurrentDVH /= max(CurrentDVH)
        DVHs[:, DVH_Counter] = np.concatenate((CurrentDVH,np.zeros(MaxDVH_Length - np.size(CurrentDVH))))
        DVH_Counter += 1

    AllDVHs = DVH(MRNs, PlanIDs, ROI_Names, Types, Volumes, DoseBinSizes, DVHs)

    return AllDVHs


def AvgDVH(DVHs):

    NumDVHs = np.size(DVHs, 1)
    AvgDVH = np.zeros([np.size(DVHs, 0)])
    for x in range(0, NumDVHs - 1):
        AvgDVH += DVHs[:, x] / np.max(DVHs[:, x])
    AvgDVH /= NumDVHs
    AvgDVH /= max(AvgDVH)

    return AvgDVH


if __name__ == '__main__':
    pass
