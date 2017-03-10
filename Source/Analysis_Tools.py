#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:48:19 2017

@author: nightowl
"""

import numpy as np
from SQL_Tools import Query_SQL


def SQL_DVH_to_Py(Cursor):

    MaxDVH_Length = 0
    for row in Cursor:
        CurrentDVH_Str = np.array(str(row[0]).split(','), dtype='|S4')
        CurrentSize = np.size(CurrentDVH_Str)
        if CurrentSize > MaxDVH_Length:
            MaxDVH_Length = CurrentSize

    DVHs = np.zeros([MaxDVH_Length, len(Cursor)])

    DVH_Counter = 0
    for row in Cursor:
        CurrentDVH_Str = np.array(str(row[0]).split(','), dtype='|S4')
        CurrentDVH = CurrentDVH_Str.astype(np.float)
        if max(CurrentDVH) > 0:
            CurrentDVH /= max(CurrentDVH)
        DVHs[:, DVH_Counter] = np.concatenate((CurrentDVH,np.zeros(MaxDVH_Length - np.size(CurrentDVH))))
        DVH_Counter += 1

    return DVHs


def GetDVHsFromSQL(*ConditionStr):

    if ConditionStr:
        DVHs = Query_SQL('DVHs', 'VolumeString', ConditionStr[0])
    else:
        DVHs = Query_SQL('DVHs', 'VolumeString')
    DVHs = SQL_DVH_to_Py(DVHs)

    return DVHs


def AvgDVH(DVHs):

    NumDVHs = np.size(DVHs, 1)
    AvgDVH = np.zeros([np.size(DVHs, 0)])
    for x in range(0, NumDVHs - 1):
        AvgDVH += DVHs[:, x]
    AvgDVH /= NumDVHs
    AvgDVH /= max(AvgDVH)

    return AvgDVH


if __name__ == '__main__':
    pass
