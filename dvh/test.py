#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 11:18 2017
@author: Dan Cutright, PhD
This is a test script to verify a successful installation.
"""

from dicom_to_sql import dicom_to_sql
from analysis_tools import DVH
from sql_to_python import DVH_SQL
from utilities import Temp_DICOM_FileSet


def test_dvh_code():

    print "importing test files with dicom_to_sql.py"
    dicom_to_sql(start_path="test_files/example_dicom_files",
                 organize_files=False,
                 move_files=False)

    print "reading data from SQL DB with analysis_tools.py"
    test = DVH()

    print "reading dicom information from test files with utilities.py"
    test_files = Temp_DICOM_FileSet(start_path="test_files/example_dicom_files")

    print "deleting test data from SQL database"
    for i in range(0, test_files.count):
        cond_str = "mrn = '" + test_files.mrn[i] + "'"
        print 'removing mrn = ' + test_files.mrn[i]
        DVH_SQL().delete_rows(cond_str)

    print "tests successful!"
