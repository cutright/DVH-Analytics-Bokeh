#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 11:33:10 2017

@author: nightowl
"""

import mysql.connector
from mysql.connector import Error
import os


def Connect_to_SQL():

    config = {'user': 'nightowl',
              'password': 'DVH123',
              'host': 'localhost',
              'database': 'DVH',
              'raise_on_warnings': True
              }

    try:
        print('Connecting to MySQL database...')
        cnx = mysql.connector.connect(**config)

        if cnx.is_connected():
            print('connection established.')
        else:
            print('connection failed.')

    except Error as error:
        print(error)

    finally:
        return cnx


def Send_to_SQL(SQL_File_Name):
    cnx = Connect_to_SQL()
    cursor = cnx.cursor()
    for line in open(SQL_File_Name):
        cursor.execute(line)
        cnx.commit()
    cnx.close()


def Check_Table_Exists(cnx, TableName):
    cnx = Connect_to_SQL()
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(TableName.replace('\'', '\'\'')))
    if cursor.fetchone()[0] == 1:
        cursor.close()
        cnx.close()
        return True

    cnx.close()
    return False


def Create_Table_PatientPlans(TableName):

    # Generate string to create table in SQL, write to output text file
    SQL_CreateTable = []
    SQL_CreateTable.append('CREATE TABLE')
    SQL_CreateTable.append(TableName)
    SQL_CreateTable.append('(MRN varchar(12),')
    SQL_CreateTable.append('PlanID tinyint(4) unsigned zerofill,')
    SQL_CreateTable.append('Birthdate date,')
    SQL_CreateTable.append('Age tinint(3) unsigned,')
    SQL_CreateTable.append('Sex char(1),')
    SQL_CreateTable.append('PlanDate date,')
    SQL_CreateTable.append('RadOnc varchar(3),')
    SQL_CreateTable.append('TxSite varchar(100),')
    SQL_CreateTable.append('RxDose float,')
    SQL_CreateTable.append('Fractions tinyint(3) unsigned,')
    SQL_CreateTable.append('Modality varchar(20),')
    SQL_CreateTable.append('MUs int(6) unsigned,')
    SQL_CreateTable.append('ROITableUID varchar(19));')
    SQL_CreateTable = ' '.join(SQL_CreateTable)
    FilePath = 'Create_Table_' + TableName + '.sql'
    with open(FilePath, "w") as text_file:
            text_file.write(SQL_CreateTable)

    Send_to_SQL(FilePath)
    os.remove(FilePath)


def Create_Table_ROI(ROI_UID):

    # Generate string to create table in SQL, write to output text file
    SQL_CreateTable = []
    SQL_CreateTable.append('CREATE TABLE')
    SQL_CreateTable.append(ROI_UID)
    SQL_CreateTable.append('(Name VARCHAR(20),')
    SQL_CreateTable.append('Type VARCHAR(20),')
    SQL_CreateTable.append('Volume DOUBLE,')
    SQL_CreateTable.append('MinDose DOUBLE,')
    SQL_CreateTable.append('MeanDose DOUBLE,')
    SQL_CreateTable.append('MaxDose DOUBLE,')
    SQL_CreateTable.append('DoseBinSize FLOAT,')
    SQL_CreateTable.append('VolumeString MEDIUMTEXT,')
    SQL_CreateTable.append('VolumeUnits VARCHAR(20));')
    SQL_CreateTable = ' '.join(SQL_CreateTable)
    FilePath = 'Create_Table_' + ROI_UID + '.sql'
    with open(FilePath, "w") as text_file:
            text_file.write(SQL_CreateTable)

    Send_to_SQL(FilePath)
    os.remove(FilePath)


def Insert_Values_ROI(ROI_UID, ROI_PyTable):

    FilePath = 'Insert_Values_' + ROI_UID + '.sql'

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
        SQL_Values_Line = '\',\''.join(SQL_Values_Line)
        SQL_Values_Line += '\');'
        Prepend = 'INSERT INTO ' + ROI_UID + ' VALUES (\''
        SQL_Values_Line = Prepend + str(SQL_Values_Line)
        SQL_Values_Line += '\n'
        with open(FilePath, "a") as text_file:
            text_file.write(SQL_Values_Line)
        SQL_Values_Line = []

    Send_to_SQL(FilePath)
    os.remove(FilePath)


def Insert_Values_PatientPlan(Table_Name, Plan_Py):

    FilePath = 'Insert_Plan_' + Plan_Py.MRN + '.sql'

    # Import each ROI from ROI_PyTable, append to output text file
    SQL_Values_Line = []
    SQL_Values_Line.append(str(Plan_Py.Patient_UID))
    SQL_Values_Line.append(str(Plan_Py.MRN))
    SQL_Values_Line.append(str(Plan_Py.PlanID))
    SQL_Values_Line.append(str(Plan_Py.Age))
    SQL_Values_Line.append(Plan_Py.Sex)
    SQL_Values_Line.append(Plan_Py.PlanDate)
    SQL_Values_Line.append(Plan_Py.RadOnc)
    SQL_Values_Line.append(Plan_Py.TxSite)
    SQL_Values_Line.append(str(Plan_Py.RxDose))
    SQL_Values_Line.append(str(Plan_Py.Fractions))
    SQL_Values_Line.append(Plan_Py.Modality)
    SQL_Values_Line.append(str(Plan_Py.MUs))
    SQL_Values_Line.append(str(Plan_Py.ROITableUID))
    SQL_Values_Line = '\',\''.join(SQL_Values_Line)
    SQL_Values_Line += '\');'
    Prepend = 'INSERT INTO ' + Table_Name + ' VALUES (\''
    SQL_Values_Line = Prepend + str(SQL_Values_Line)
    SQL_Values_Line += '\n'
    with open(FilePath, "a") as text_file:
        text_file.write(SQL_Values_Line)

    Send_to_SQL(FilePath)
    os.remove(FilePath)


# Functions yet to be defined
#
# def Get_PlanID(cnx, Table_Name, Patient_UID):
# def Get_ROI_UID(cnx, Table_Name, Patient_UID, PlanID):


if __name__ == '__main__':
    pass
