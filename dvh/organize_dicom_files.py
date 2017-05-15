#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 15 15:19 2017

@author: Dan Cutright, Ph.D.
"""

import dicom
import os
import sys


class DICOM_FileSet:
    def __init__(self, plan, structure, dose, name):
        self.plan = plan
        self.structure = structure
        self.dose = dose
        self.name = name


def organize_dicom_files(path):
    initial_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path)
    files = [f for f in os.listdir('.') if os.path.isfile(os.path.join('.', f))]

    for i in range(0, len(files)):
        try:
            name = dicom.read_file(files[i]).PatientName.replace(' ', '_').replace('^', '_')
            os.mkdir(name)
        except:
            pass

        file_name = files[i].split('/')[-1]

        old = files[i]
        new = '/'.join([path, name, file_name])
        print old, new
        os.rename(old, new)

    os.chdir(initial_path)


if __name__ == '__main__':
    organize_dicom_files(sys.argv[1])
