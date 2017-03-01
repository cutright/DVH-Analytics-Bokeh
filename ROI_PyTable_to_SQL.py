#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 08:08:55 2017

@author: nightowl
"""


def ROI_PyTable_to_SQL(ROI_UID, ROI_PyTable):

    # Generate string to create table in SQL, write to output text file
    SQL_CreateTable = []
    SQL_CreateTable.append('CREATE TABLE')
    SQL_CreateTable.append(ROI_UID)
    SQL_CreateTable.append('(\n\tName VARCHAR(20),')
    SQL_CreateTable.append('\n\tType VARCHAR(20),')
    SQL_CreateTable.append('\n\tVolume DOUBLE,')
    SQL_CreateTable.append('\n\tMinDose DOUBLE,')
    SQL_CreateTable.append('\n\tMeanDose DOUBLE,')
    SQL_CreateTable.append('\n\tMaxDose DOUBLE,')
    SQL_CreateTable.append('\n\tDoseBinSize FLOAT,')
    SQL_CreateTable.append('\n\tVolumeString MEDIUMTEXT,')
    SQL_CreateTable.append('\n\tVolumeUnits VARCHAR(20));')
    SQL_CreateTable = ' '.join(SQL_CreateTable)
    SQL_CreateTable += '\n'
    with open("Output.txt", "w") as text_file:
            text_file.write(SQL_CreateTable)

    # Import each ROI from ROI_PyTable, append to output text file
    SQL_Values_Line = []
    for ROI_Counter in range(1, len(ROI_PyTable)+1):
        SQL_Values_Line.append(ROI_PyTable[ROI_Counter].Name)
        SQL_Values_Line.append(ROI_PyTable[ROI_Counter].Type)
        SQL_Values_Line.append(str(ROI_PyTable[ROI_Counter].Volume))
        SQL_Values_Line.append(str(ROI_PyTable[ROI_Counter].MinDose))
        SQL_Values_Line.append(str(ROI_PyTable[ROI_Counter].MeanDose))
        SQL_Values_Line.append(str(ROI_PyTable[ROI_Counter].MaxDose))
        SQL_Values_Line.append(str(ROI_PyTable[ROI_Counter].DoseBinSize))
        SQL_Values_Line.append(ROI_PyTable[ROI_Counter].VolumeString)
        SQL_Values_Line.append(ROI_PyTable[ROI_Counter].VolumeUnits)
        SQL_Values_Line = '\',\n\t\''.join(SQL_Values_Line)
        SQL_Values_Line += '\');\n'
        SQL_Values_Line = 'INSERT INTO ' + ROI_UID + '\nVALUES (\n\t\'' + str(SQL_Values_Line)
        with open("Output.txt", "a") as text_file:
            text_file.write(SQL_Values_Line)
        SQL_Values_Line = []

if __name__ == '__main__':
    ROI_PyTable_to_SQL()
