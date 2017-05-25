#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 22:15:52 2017

@author: nightowl
"""

from sql_connector import DVH_SQL
from dicom_to_python import DVHTable, PlanRow, BeamTable, RxTable
import os
import dicom
from datetime import datetime


class DICOM_FileSet:
    def __init__(self, plan, structure, dose):
        self.plan = plan
        self.structure = structure
        self.dose = dose


def dicom_to_sql(**kwargs):
    # Read SQL configuration file
    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/import_settings.txt"
    abs_file_path = os.path.join(script_dir, rel_path)
    with open(abs_file_path, 'r') as document:
        import_settings = {}
        for line in document:
            line = line.split()
            if not line:
                continue
            import_settings[line[0]] = line[1:][0]
            # Convert strings to boolean
            if line[1:][0].lower() == 'true':
                import_settings[line[0]] = True
            elif line[1:][0].lower() == 'false':
                import_settings[line[0]] = False

    if 'start_path' in kwargs and kwargs['start_path']:
        rel_path = kwargs['start_path']
        abs_file_path = os.path.join(script_dir, rel_path)
        import_settings['inbox'] = abs_file_path

    sqlcnx = DVH_SQL()
    force_update = False
    if 'force_update' in kwargs and kwargs['force_update']:
        force_update = True
    f = get_file_paths(import_settings['inbox'], force_update=force_update)

    for n in range(0, len(f)):
        print f[n].structure
        print f[n].plan
        print f[n].dose

        plan = PlanRow(f[n].plan, f[n].structure, f[n].dose)
        beams = BeamTable(f[n].plan)
        dvhs = DVHTable(f[n].structure, f[n].dose)
        rxs = RxTable(f[n].plan, f[n].structure)

        setattr(dvhs, 'ptv_number', rank_ptvs_by_D95(dvhs))

        sqlcnx.insert_plan(plan)
        sqlcnx.insert_beams(beams)
        sqlcnx.insert_dvhs(dvhs)
        sqlcnx.insert_rxs(rxs)

        # Default behavior is to move files from inbox to imported
        # Only way to prevent moving files is to set move_files = False in kwargs
        if 'move_files' not in kwargs:
            move_files_to_imported_path(f[n], import_settings['imported'])
        elif kwargs['move_files']:
            move_files_to_imported_path(f[n], import_settings['imported'])

    # Default behavior is to organize files in the imported folder
    # Only way to prevent organizing files is to set organize_files = False in kwargs
    if 'organize_files' not in kwargs:
        organize_dicom_files(import_settings['imported'])
    elif kwargs['organize_files']:
        organize_dicom_files(import_settings['imported'])

    sqlcnx.cnx.close()


def get_file_paths(start_path, **kwargs):

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

    if 'force_update' in kwargs and kwargs['force_update']:
        print 'WARNING: Forcing all dicom to be imported (i.e., not checking DB for potential duplicates)'

    db_entry_found = False
    for x in range(0, len(f)):
        if 'force_update' in kwargs and kwargs['force_update']:
            try:
                dicom_file = dicom.read_file(f[x])
                if dicom_file.Modality.lower() == 'rtplan':
                    plan_files.append(f[x])
                    study_uid_plan.append(dicom_file.StudyInstanceUID)
                elif dicom_file.Modality.lower() == 'rtstruct':
                    structure_files.append(f[x])
                    study_uid_structure.append(dicom_file.StudyInstanceUID)
                elif dicom_file.Modality.lower() == 'rtdose':
                    dose_files.append(f[x])
                    study_uid_dose.append(dicom_file.StudyInstanceUID)
            except Exception:
                pass
        else:
            try:
                if not is_file_imported(f[x]):
                    dicom_file = dicom.read_file(f[x])
                    if dicom_file.Modality.lower() == 'rtplan':
                        plan_files.append(f[x])
                        study_uid_plan.append(dicom_file.StudyInstanceUID)
                    elif dicom_file.Modality.lower() == 'rtstruct':
                        structure_files.append(f[x])
                        study_uid_structure.append(dicom_file.StudyInstanceUID)
                    elif dicom_file.Modality.lower() == 'rtdose':
                        dose_files.append(f[x])
                        study_uid_dose.append(dicom_file.StudyInstanceUID)
                else:
                    if not db_entry_found:
                        print "The following files are already imported. Must delete from database before reimporting."
                        db_entry_found = True
                    print f[x]
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


def rebuild_database(start_path):
    print 'connecting to SQL DB'
    sqlcnx = DVH_SQL()
    print 'connection established'

    sqlcnx.reinitialize_database()
    print 'DB reinitialized with no data'
    dicom_to_sql(start_path=start_path,
                 force_update=True,
                 move_files=False,
                 organize_files=False)
    sqlcnx.cnx.close()


def is_file_imported(file_path):

    try:
        dicom_data = dicom.read_file(file_path)
        uid = dicom_data.StudyInstanceUID
    except Exception:
        return False

    if dicom_data.Modality.lower() == 'rtplan':
        table_name = 'Plans'
    elif dicom_data.Modality.lower() == 'rtstruct':
        table_name = 'DVHs'
    elif dicom_data.Modality.lower() == 'rtdose':
        table_name = 'DVHs'
    else:
        return False

    if DVH_SQL().is_study_instance_uid_in_table(table_name, uid):
        return True
    else:
        return False


def rank_ptvs_by_D95(dvhs):
    ptv_number_list = []
    ptv_index = []

    for i in range(0, dvhs.count):
        ptv_number_list.append(0)
        if dvhs.roi_type[i] == 'PTV':
            ptv_index.append(i)

    ptv_count = len(ptv_index)

    # Calculate D95 for each PTV
    doses_to_rank = get_dose_to_volume(dvhs, ptv_index, 0.95)
    order_index = sorted(range(ptv_count), key=lambda k: doses_to_rank[k])
    final_order = sorted(range(ptv_count), key=lambda k: order_index[k])

    for i in range(0, ptv_count):
        ptv_number_list[ptv_index[i]] = final_order[i] + 1

    return ptv_number_list


def get_dose_to_volume(dvhs, indices, roi_fraction):
    # Not precise (i.e., no interpolation) but good enough for sorting PTVs
    doses = []
    for x in indices:
        abs_volume = dvhs.volume[x] * roi_fraction
        dvh = dvhs.dvhs[x]
        dose = next(x[0] for x in enumerate(dvh) if x[1] < abs_volume)
        doses.append(dose)

    return doses


def move_files_to_imported_path(file_paths, imported_path):
    for file_type in file_paths.__dict__:
        file_path = getattr(file_paths, file_type)
        file_name = file_path.split('/')[-1]
        new = '/'.join([imported_path, file_name])
        try:
            os.rename(file_path, new)
        except:
            os.mkdir(imported_path)
            os.rename(file_path, new)


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
    DVH_SQL().reinitialize_database()
    dicom_to_sql()
