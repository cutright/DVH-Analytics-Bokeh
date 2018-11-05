from sql_to_python import QuerySQL
from future.utils import listitems
from dateutil.relativedelta import relativedelta
import numpy as np
import os
from get_settings import get_settings
from dicompylercore import dicomparser
try:
    import pydicom as dicom
except ImportError:
    import dicom


def calc_stats(data):
    """
    :param data: a list or numpy 1D array of numbers
    :return: a standard list of stats (max, 75%, median, mean, 25%, and min)
    :rtype: list
    """
    data = [x for x in data if x != 'None']
    try:
        data_np = np.array(data)
        rtn_data = [np.max(data_np),
                    np.percentile(data_np, 75),
                    np.median(data_np),
                    np.mean(data_np),
                    np.percentile(data_np, 25),
                    np.min(data_np)]
    except:
        rtn_data = [0, 0, 0, 0, 0, 0]
        print("calc_stats() received non-numerical data")
    return rtn_data


def collapse_into_single_dates(x, y):
    """
    :param x: a list of dates in ascending order
    :param y: a list of values as a function of date
    :return: a unique list of dates, sum of y for that date, and number of original points for that date
    :rtype: dict
    """

    # average daily data and keep track of points per day
    x_collapsed = [x[0]]
    y_collapsed = [y[0]]
    w_collapsed = [1]
    for n in range(1, len(x)):
        if x[n] == x_collapsed[-1]:
            y_collapsed[-1] = (y_collapsed[-1] + y[n])
            w_collapsed[-1] += 1
        else:
            x_collapsed.append(x[n])
            y_collapsed.append(y[n])
            w_collapsed.append(1)

    return {'x': x_collapsed, 'y': y_collapsed, 'w': w_collapsed}


def moving_avg(xyw, avg_len):
    """
    :param xyw: a dictionary of of lists x, y, w: x, y being coordinates and w being the weight
    :param avg_len: average of these number of points, i.e., look-back window
    :return: list of x values, list of y values
    """
    cumsum, moving_aves, x_final = [0], [], []

    for i, y in enumerate(xyw['y'], 1):
        cumsum.append(cumsum[i - 1] + y / xyw['w'][i - 1])
        if i >= avg_len:
            moving_ave = (cumsum[i] - cumsum[i - avg_len]) / avg_len
            moving_aves.append(moving_ave)
    x_final = [xyw['x'][i] for i in range(avg_len - 1, len(xyw['x']))]

    return x_final, moving_aves


def moving_avg_by_calendar_day(xyw, avg_days):
    """
    :param xyw: a dictionary of of lists x, y, w: x, y being coordinates and w being the weight
    :param avg_days: number of calendar days in look-back window
    :return: list of x values, list of y values
    """
    cumsum, moving_aves, x_final = [0], [], []

    for i, y in enumerate(xyw['y'], 1):
        cumsum.append(cumsum[i - 1] + y / xyw['w'][i - 1])

        first_date_index = i - 1
        for j, x in enumerate(xyw['x']):
            delta_x = relativedelta(xyw['x'][i-1], x)
            delta_x_days = delta_x.years * 365.25 + delta_x.days
            if delta_x_days <= avg_days:
                first_date_index = j
                break
        moving_ave = (cumsum[i] - cumsum[first_date_index]) / (i - first_date_index)
        moving_aves.append(moving_ave)
        x_final.append(xyw['x'][i-1])

    return x_final, moving_aves


def group_constraint_count(sources):
    data = sources.selectors.data
    g1a = len([r for r in data['row'] if data['group'][int(r)-1] in {1, 3}])
    g2a = len([r for r in data['row'] if data['group'][int(r)-1] in {2, 3}])

    data = sources.ranges.data
    g1b = len([r for r in data['row'] if data['group'][int(r)-1] in {1, 3}])
    g2b = len([r for r in data['row'] if data['group'][int(r)-1] in {2, 3}])

    return g1a + g1b, g2a + g2b


def get_include_map(sources):
    # remove review and stats from source
    group_1_constraint_count, group_2_constraint_count = group_constraint_count(sources)
    if group_1_constraint_count > 0 and group_2_constraint_count > 0:
        extra_rows = 12
    elif group_1_constraint_count > 0 or group_2_constraint_count > 0:
        extra_rows = 6
    else:
        extra_rows = 0
    include = [True] * (len(sources.dvhs.data['uid']) - extra_rows)
    include[0] = False
    include.extend([False] * extra_rows)

    return include


def clear_source_data(sources, key):
    src = getattr(sources, key)
    src.data = {k: [] for k in list(src.data)}


def clear_source_selection(sources, key):
    getattr(sources, key).selected.indices = []


def get_group_list(uids, all_uids):

    groups = []
    for r in range(len(uids)):
        if uids[r] in all_uids['1']:
            if uids[r] in all_uids['2']:
                groups.append('Group 1 & 2')
            else:
                groups.append('Group 1')
        else:
            groups.append('Group 2')

    return groups


def get_study_instance_uids(**kwargs):
    uids = {}
    complete_list = []
    for key, value in listitems(kwargs):
        uids[key] = QuerySQL(key, value).study_instance_uid
        complete_list.extend(uids[key])

    uids['unique'] = list(set(complete_list))
    uids['union'] = [uid for uid in uids['unique'] if is_uid_in_all_keys(uid, uids)]

    return uids


def is_uid_in_all_keys(uid, uids):
    key_answer = {}
    # Initialize a False value for each key
    for key in list(uids):
        key_answer[key] = False
    # search for uid in each keyword fof uid_kwlist
    for key, value in listitems(uids):
        if uid in value:
            key_answer[key] = True

    final_answer = True
    # Product of all answer[key] values (except 'unique')
    for key, value in listitems(key_answer):
        if key not in 'unique':
            final_answer *= value
    return final_answer


class Temp_DICOM_FileSet:
    def __init__(self, start_path=None):

        # Read SQL configuration file
        if start_path:
            abs_file_path = os.path.join(os.path.dirname(__file__), start_path)
            start_path = abs_file_path
        else:
            abs_file_path = get_settings('import')

            with open(abs_file_path, 'r') as document:
                for line in document:
                    line = line.split()
                    if not line:
                        continue
                    if line[0] == 'review':
                        start_path = line[1:][0]

        self.plan = []
        self.structure = []
        self.dose = []
        self.mrn = []
        self.study_instance_uid = []

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

        for x in range(len(f)):
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

        self.count = len(plan_files)

        for a in range(self.count):
            self.plan.append(plan_files[a])
            self.mrn.append(dicom.read_file(plan_files[a]).PatientID)
            self.study_instance_uid.append(dicom.read_file(plan_files[a]).StudyInstanceUID)
            for b in range(len(structure_files)):
                if study_uid_plan[a] == study_uid_structure[b]:
                    self.structure.append(structure_files[b])
            for c in range(len(dose_files)):
                if study_uid_plan[a] == study_uid_dose[c]:
                    self.dose.append(dose_files[c])

        if self.count == 0:
            self.plan.append('')
            self.mrn.append('')
            self.structure.append('')
            self.dose.append('')

    def get_roi_names(self, mrn):

        structure_file = self.structure[self.mrn.index(mrn)]
        rt_st = dicomparser.DicomParser(structure_file)
        rt_structures = rt_st.GetStructures()

        roi = {}
        for key in list(rt_structures):
            if rt_structures[key]['type'].upper() not in {'MARKER', 'REGISTRATION', 'ISOCENTER'}:
                roi[key] = rt_structures[key]['name']

        return roi