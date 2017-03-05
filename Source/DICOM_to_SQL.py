#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 22:15:52 2017

@author: nightowl
"""

from SQL_Tools import Check_Table_Exists, Insert_Values_ROI, Create_Table_ROI
from Create_ROI_PyTable import Create_ROI_PyTable


def DICOM_to_SQL(ROI_UID, StructureFile, DoseFile):

    ROI_PyTable = Create_ROI_PyTable(StructureFile, DoseFile)
    if Check_Table_Exists(ROI_UID) is 'False':
        Create_Table_ROI(ROI_UID)
    Insert_Values_ROI(ROI_UID, ROI_PyTable)

if __name__ == '__main__':
    DICOM_to_SQL()
