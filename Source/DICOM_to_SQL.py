#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 22:15:52 2017

@author: nightowl
"""

from DVH_SQL import DVH_SQL
from DICOM_to_Python import DVHTable, PlanRow, BeamTable, FxGrpTable
import os
import dicom


class DICOM_FileSet:
    def __init__(self, plan, structure, dose):
        self.plan = plan
        self.structure = structure
        self.dose = dose


def get_file_paths(start_path):

    f = []
    for root, dirs, files in os.walk(start_path, topdown=False):
        for name in files:
            f.append(os.path.join(root, name))

    plan_files = []
    study_uid_plan = []
    structure_files = []
    study_uid_structure = []
    dose_files = []
    study_uid_dose = []

    for x in range(0, len(f)):
        try:
            DICOM_File = dicom.read_file(f[x])
            if DICOM_File.Modality.lower() == 'rtplan':
                plan_files.append(f[x])
                study_uid_plan.append(DICOM_File.StudyInstanceUID)
            elif DICOM_File.Modality.lower() == 'rtstruct':
                structure_files.append(f[x])
                study_uid_structure.append(DICOM_File.StudyInstanceUID)
            elif DICOM_File.Modality.lower() == 'rtdose':
                dose_files.append(f[x])
                study_uid_dose.append(DICOM_File.StudyInstanceUID)
        except Exception:
            pass

    dicom_files = {}
    for a in range(0, len(plan_files)):
        rt_plan = plan_files[a]
        for b in range(0, len(structure_files)):
            if study_uid_plan[a] == study_uid_structure[b]:
                rt_structure = structure_files[b]
        for c in range(0, len(dose_files)):
            if study_uid_plan[a] == study_uid_dose[c]:
                rt_dose = dose_files[c]
        dicom_files[a] = DICOM_FileSet(rt_plan, rt_structure, rt_dose)

    return dicom_files


def dicom_to_sql(start_path):

    sqlcnx = DVH_SQL()
    f = get_file_paths(start_path)

    for n in range(0, len(f)):
        plan = PlanRow(f[n].plan, f[n].structure, f[n].dose)
        beams = BeamTable(f[n].plan)
        dvhs = DVHTable(f[n].structure, f[n].dose)
        rxs = FxGrpTable(f[n].plan, f[n].structure)

        sqlcnx.insert_plan(plan)
        sqlcnx.insert_beams(beams)
        sqlcnx.insert_dvhs(dvhs)
        sqlcnx.insert_rxs(rxs)

    sqlcnx.cnx.close()


def rebuild_database(start_path):

    sqlcnx = DVH_SQL()

    sqlcnx.reinitialize_database()
    dicom_to_sql(start_path)
    sqlcnx.cnx.close()


if __name__ == '__main__':
    dicom_to_sql()
