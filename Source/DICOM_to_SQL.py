#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 22:15:52 2017

@author: nightowl
"""

from SQL_Tools import Insert_Values_DVHs, Insert_Values_Plans
from DICOM_to_Python import Create_ROI_PyTable, Create_Plan_Py


def DICOM_to_SQL(PlanFile, StructureFile, DoseFile):

    ROI_PyTable = Create_ROI_PyTable(StructureFile, DoseFile)
    Plan_Py = Create_Plan_Py(PlanFile, StructureFile)
    Insert_Values_Plans(Plan_Py)
    Insert_Values_DVHs(ROI_PyTable)


if __name__ == '__main__':
    DICOM_to_SQL()
