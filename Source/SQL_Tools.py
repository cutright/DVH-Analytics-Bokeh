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
#    with open('SQL_Connection.cnf', 'r') as document:
#        config = {}
#        for line in document:
#            line = line.split()
#            if not line:  # empty line?
#                continue
#            config[line[0]] = line[1:]

    try:
        print('Connecting to MySQL database...')
        cnx = mysql.connector.connect(**config)

        if cnx.is_connected():
            print('Connection established.')
        else:
            print('Connection failed.')

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
    print('Connection closed.')


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
        print('Connection closed.')
        return True

    cnx.close()
    print('Connection closed.')
    return False


def Query_SQL(TableName, ReturnColStr, *ConditionStr):

    query = 'Select ' + ReturnColStr + ' from ' + TableName
    if ConditionStr:
        query += ' where ' + ConditionStr[0]
    query += ';'

    cnx = Connect_to_SQL()
    cursor = cnx.cursor()

    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    cnx.close()
    print('Connection closed.')

    return results


def GetPlanIDs(MRN):

    query = 'Select PlanID from Plans where MRN=\'' + MRN + '\';'
    cnx = Connect_to_SQL()
    cursor = cnx.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    cnx.close()
    print('Connection closed.')
    return results


def Create_Table_Plans():

    # Generate string to create table in SQL, write to output text file
    SQL_CreateTable = []
    SQL_CreateTable.append('CREATE TABLE')
    SQL_CreateTable.append('Plans')
    SQL_CreateTable.append('(MRN varchar(12),')
    SQL_CreateTable.append('PlanID tinyint(4) unsigned,')
    SQL_CreateTable.append('Birthdate date,')
    SQL_CreateTable.append('Age tinyint(3) unsigned,')
    SQL_CreateTable.append('Sex char(1),')
    SQL_CreateTable.append('SimStudyDate date,')
    SQL_CreateTable.append('RadOnc varchar(50),')
    SQL_CreateTable.append('TxSite varchar(50),')
    SQL_CreateTable.append('RxDose float,')
    SQL_CreateTable.append('Fractions tinyint(3) unsigned,')
    SQL_CreateTable.append('Energy varchar(30),')
    SQL_CreateTable.append('TxModality varchar(30),')
    SQL_CreateTable.append('MUs int(6) unsigned,')
    SQL_CreateTable.append('TxTime time,')
    SQL_CreateTable.append('StudyInstanceUID varchar(100),')
    SQL_CreateTable.append('PatientOrientation varchar(3),')
    SQL_CreateTable.append('PlanTimeStamp datetime,')
    SQL_CreateTable.append('StTimeStamp datetime,')
    SQL_CreateTable.append('DoseTimeStamp datetime,')
    SQL_CreateTable.append('TPSManufacturer varchar(50),')
    SQL_CreateTable.append('TPSSoftwareName varchar(50),')
    SQL_CreateTable.append('TPSSoftwareVersion varchar(30));')
    SQL_CreateTable = ' '.join(SQL_CreateTable)
    FilePath = 'Create_Table_Plans.sql'
    with open(FilePath, "w") as text_file:
            text_file.write(SQL_CreateTable)

    Send_to_SQL(FilePath)
    os.remove(FilePath)


def Create_Table_DVHs():

    # Generate string to create table in SQL, write to output text file
    SQL_CreateTable = []
    SQL_CreateTable.append('CREATE TABLE')
    SQL_CreateTable.append('DVHs')
    SQL_CreateTable.append('(MRN varchar(12),')
    SQL_CreateTable.append('PlanID tinyint(4) unsigned,')
    SQL_CreateTable.append('ROIName VARCHAR(50),')
    SQL_CreateTable.append('Type VARCHAR(20),')
    SQL_CreateTable.append('Volume DOUBLE,')
    SQL_CreateTable.append('MinDose DOUBLE,')
    SQL_CreateTable.append('MeanDose DOUBLE,')
    SQL_CreateTable.append('MaxDose DOUBLE,')
    SQL_CreateTable.append('DoseBinSize FLOAT,')
    SQL_CreateTable.append('VolumeString MEDIUMTEXT);')
    SQL_CreateTable = ' '.join(SQL_CreateTable)
    FilePath = 'Create_Table_DVHs.sql'
    with open(FilePath, "w") as text_file:
            text_file.write(SQL_CreateTable)

    Send_to_SQL(FilePath)
    os.remove(FilePath)


def Insert_Values_DVHs(ROI_PyTable):

    FilePath = 'Insert_Values_DVHs.sql'

    # Import each ROI from ROI_PyTable, append to output text file
    SQL_Input = []
    for x in range(1, len(ROI_PyTable)+1):
        SQL_Input.append(str(ROI_PyTable[x].MRN))
        SQL_Input.append(str(ROI_PyTable[x].PlanID))
        SQL_Input.append(ROI_PyTable[x].ROI_Name)
        SQL_Input.append(ROI_PyTable[x].Type)
        SQL_Input.append(str(round(ROI_PyTable[x].Volume, 3)))
        SQL_Input.append(str(round(ROI_PyTable[x].MinDose, 2)))
        SQL_Input.append(str(round(ROI_PyTable[x].MeanDose, 2)))
        SQL_Input.append(str(round(ROI_PyTable[x].MaxDose, 2)))
        SQL_Input.append(str(ROI_PyTable[x].DoseBinSize))
        SQL_Input.append(ROI_PyTable[x].VolumeString)
        SQL_Input = '\',\''.join(SQL_Input)
        SQL_Input += '\');'
        Prepend = 'INSERT INTO DVHs VALUES (\''
        SQL_Input = Prepend + str(SQL_Input)
        SQL_Input += '\n'
        with open(FilePath, "a") as text_file:
            text_file.write(SQL_Input)
        SQL_Input = []

    Send_to_SQL(FilePath)
    os.remove(FilePath)
    print('DVHs Imported.')


def Insert_Values_Plans(Plan_Py):

    FilePath = 'Insert_Plan_' + Plan_Py.MRN + '.sql'

    # Import each ROI from ROI_PyTable, append to output text file
    SQL_Input = []
    SQL_Input.append(str(Plan_Py.MRN))
    SQL_Input.append(str(Plan_Py.PlanID))
    SQL_Input.append(str(Plan_Py.Birthdate))
    SQL_Input.append(str(Plan_Py.Age))
    SQL_Input.append(Plan_Py.Sex)
    SQL_Input.append(Plan_Py.SimStudyDate)
    SQL_Input.append(Plan_Py.RadOnc)
    SQL_Input.append(Plan_Py.TxSite)
    SQL_Input.append(str(Plan_Py.RxDose))
    SQL_Input.append(str(Plan_Py.Fractions))
    SQL_Input.append(Plan_Py.Energy)
    SQL_Input.append(Plan_Py.TxModality)
    SQL_Input.append(str(Plan_Py.MUs))
    SQL_Input.append(str(Plan_Py.TxTime))
    SQL_Input.append(Plan_Py.StudyInstanceUID)
    SQL_Input.append(Plan_Py.PatientOrientation)
    SQL_Input.append(str(Plan_Py.PlanTimeStamp))
    SQL_Input.append(str(Plan_Py.StTimeStamp))
    SQL_Input.append(str(Plan_Py.DoseTimeStamp))
    SQL_Input.append(Plan_Py.TPSManufacturer)
    SQL_Input.append(Plan_Py.TPSSoftwareName)
    SQL_Input.append(str(Plan_Py.TPSSoftwareVersion))
    SQL_Input = '\',\''.join(SQL_Input)
    SQL_Input += '\');'
    SQL_Input = SQL_Input.replace("'(NULL)'", "(NULL)")
    Prepend = 'INSERT INTO Plans VALUES (\''
    SQL_Input = Prepend + str(SQL_Input)
    SQL_Input += '\n'
    with open(FilePath, "a") as text_file:
        text_file.write(SQL_Input)

    Send_to_SQL(FilePath)
    os.remove(FilePath)
    print('Plan Imported.')


# Functions yet to be defined
#
# def Get_PlanID(cnx, Table_Name, Patient_UID):
# def Get_ROI_UID(cnx, Table_Name, Patient_UID, PlanID):


if __name__ == '__main__':
    pass
