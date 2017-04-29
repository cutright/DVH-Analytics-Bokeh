#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:48:19 2017
@author: nightowl
"""

import numpy as np
from prettytable import PrettyTable
from SQL_to_Python import *
import os


class DVH:
    def __init__(self, **kwargs):

        if 'uid' in kwargs:
            study_instance_uid = kwargs['uid']
            db_constraints_list = []
            for i in range(0, len(study_instance_uid)):
                db_constraints_list.append(study_instance_uid[i])
            uid_constraints_str = "study_instance_uid in ('"
            uid_constraints_str += "', '".join(db_constraints_list)
            uid_constraints_str += "')"
            if 'dvh_condition' in kwargs and kwargs['dvh_condition']:
                uid_constraints_str = " and " + uid_constraints_str
        else:
            uid_constraints_str = ''

        if 'dvh_condition' in kwargs and kwargs['dvh_condition']:
            uid_constraints_str = kwargs['dvh_condition'] + uid_constraints_str
            self.query = kwargs['dvh_condition']
        else:
            self.query = ''

        if 'uncategorized' in kwargs:
            if kwargs['uncategorized']:
                self.uncategorized = True
            else:
                self.uncategorized = False
        else:
            self.uncategorized = False

        cnx = DVH_SQL()

        # Get DVH data from SQL
        dvh_data = QuerySQL('DVHs', uid_constraints_str)
        for key, value in dvh_data.__dict__.items():
            if not key.startswith("__"):
                setattr(self, key, value)

        # Add this properties to dvh_data since they aren't in teh DVHs SQL table
        self.count = len(self.mrn)
        setattr(self, 'rx_dose', [])
        setattr(self, 'eud', [])
        setattr(self, 'eud_a_value', [])

        self.bin_count = 0
        for value in self.dvh_string:
            current_dvh_str = np.array(str(value).split(','))
            current_size = np.size(current_dvh_str)
            if current_size > self.bin_count:
                self.bin_count = current_size
        setattr(self, 'dvh', np.zeros([self.bin_count, self.count]))

        # get EUD a values from a preference file
        eud_a_values = {}
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "preferences/EUD_a-values.txt"
        abs_file_path = os.path.join(script_dir, rel_path)
        with open(abs_file_path, 'r') as document:
            for line in document:
                line = line.strip().split(',')
                eud_a_values[line[0]] = float(line[1])

        # Get needed values not in DVHs table
        for i in range(0, self.count):
            # Get Rx Doses
            condition = "mrn = '" + self.mrn[i]
            condition += "' and study_instance_uid = '"
            condition += str(self.study_instance_uid[i]) + "'"
            rx_dose_cursor = cnx.query('Plans', 'rx_dose', condition)
            self.rx_dose.append(rx_dose_cursor[0][0])

            # Process dvh_string to numpy array, and pad with zeros at the end
            # so that all dvhs are the same length
            current_dvh = np.array(self.dvh_string[i].split(','), dtype='|S4').astype(np.float)
            if np.max(current_dvh) > 0:
                current_dvh = np.divide(current_dvh, np.max(current_dvh))
            zero_fill = np.zeros(self.bin_count - len(current_dvh))
            self.dvh[:, i] = np.concatenate((current_dvh, zero_fill))

            # Lookup the EUD a value for current roi
            if self.physician_roi[i] in eud_a_values:
                current_a = eud_a_values[self.physician_roi[i]]
            elif self.roi_type[i].lower() in {'gtv', 'ctv', 'ptv'}:
                current_a = float(-10)
            else:
                current_a = float(1)
            self.eud.append(calc_eud(current_dvh, current_a))
            self.eud_a_value.append(current_a)

        # Initialize properties
        # Calculating all of these can be computationally expensive
        # so using @property method below only calculates these if called
        self._min_dvh = np.ones(self.bin_count)
        self._q1_dvh = np.ones(self.bin_count)
        self._mean_dvh = np.ones(self.bin_count)
        self._median_dvh = np.ones(self.bin_count)
        self._q3_dvh = np.ones(self.bin_count)
        self._max_dvh = np.ones(self.bin_count)
        self._std_dvh = np.ones(self.bin_count)

    def __repr__(self):
        return self.roi_statistics()

    @property
    def min_dvh(self):
        dvh = np.zeros(self.bin_count)
        for x in range(0, self.bin_count):
            dvh[x] = np.min(self.dvh[x, :])
        return dvh

    @property
    def q1_dvh(self):
        dvh = np.zeros(self.bin_count)
        for x in range(0, self.bin_count):
            dvh[x] = np.percentile(self.dvh[x, :], 25)
        return dvh

    @property
    def mean_dvh(self):
        dvh = np.zeros(self.bin_count)
        for x in range(0, self.bin_count):
            dvh[x] = np.mean(self.dvh[x, :])
        return dvh

    @property
    def median_dvh(self):
        dvh = np.zeros(self.bin_count)
        for x in range(0, self.bin_count):
            dvh[x] = np.median(self.dvh[x, :])
        return dvh

    @property
    def q3_dvh(self):
        dvh = np.zeros(self.bin_count)
        for x in range(0, self.bin_count):
            dvh[x] = np.percentile(self.dvh[x, :], 75)
        return dvh

    @property
    def max_dvh(self):
        dvh = np.zeros(self.bin_count)
        for x in range(0, self.bin_count):
            dvh[x] = np.max(self.dvh[x, :])
        return dvh

    @property
    def std_dvh(self):
        dvh = np.zeros(self.bin_count)
        for x in range(0, self.bin_count):
            dvh[x] = np.std(self.dvh[x, :])
        return dvh

    def write_roi_statistics(self, file_path):
        document = open(file_path[0], 'w')
        document.write(self.roi_statistics())
        document.close()

    def roi_statistics(self):
        # Only use if running code in a python console
        # Print 'Pretty Table' of data
        roi_table = PrettyTable()
        roi_table.field_names = ['MRN', 'InstitutionalROI', 'PhysicianROI', 'ROIName', 'Volume',
                                 'Min Dose', 'Mean Dose', 'Max Dose', 'EUD', 'a']
        for i in range(0, self.count):
            roi_table.add_row([self.mrn[i],
                               self.roi_institutional[i],
                               self.roi_physician[i],
                               self.roi_name[i],
                               np.round(self.volume[i], 2),
                               self.min_dose[i],
                               self.mean_dose[i],
                               self.max_dose[i],
                               np.round(self.eud[i], 2),
                               self.eud_a_value[i]])

        return roi_table.get_string()

    def get_percentile_dvh(self, percentile):
        dvh = np.zeros(self.bin_count)
        for x in range(0, self.bin_count):
            dvh[x] = np.percentile(self.dvh[x, :], percentile)
        return dvh

    def get_dose_to_volume(self, volume, **kwargs):
        # if no kwargs, input and output assumed to be in Gy and cm^3
        doses = np.zeros(self.count)
        for x in range(0, self.count):
            dvh = np.zeros(len(self.dvh))
            for y in range(0, len(self.dvh)):
                dvh[y] = self.dvh[y][x]
                if 'input' in kwargs and kwargs['input'] == 'relative':
                    doses[x] = dose_to_volume(dvh, volume)
                else:
                    doses[x] = dose_to_volume(dvh, volume, self.volume[x])
        if 'output' in kwargs and kwargs['output'] == 'relative':
            doses = np.divide(doses, self.rx_dose)

        return doses.tolist()

    def get_volume_of_dose(self, dose, **kwargs):
        # dose input is assumed to be in Gy
        # output will be either fractional (relative) or in cc's
        roi_volume = []
        dose = np.ones(self.count) * dose
        if 'input' in kwargs and kwargs['input'] == 'relative':
            dose = np.multiply(dose, self.rx_dose)
        for i in range(0, self.count):
            x = [int(np.floor(dose[i] * 100)), int(np.ceil(dose[i] * 100))]
            y = [self.dvh[x[0], i], self.dvh[x[1], i]]
            if 'output' in kwargs and kwargs['output'] == 'relative':
                roi_volume.append(np.interp(float(dose[i]), x, y))
            else:
                roi_volume.append(np.interp(float(dose[i]), x, y) * self.volume[i])

        return roi_volume

    def coverage(self, rx_dose_fraction):

        answer = np.zeros(self.count)
        for x in range(0, self.count):
            answer[x] = self.get_volume_of_dose(float(self.rx_dose[x] * rx_dose_fraction))

        return answer


# Returns the isodose level outlining the given volume
def dose_to_volume(dvh, volume, *roi_volume):
    # if an roi_volume is not given, volume is assumed to be fractional
    if roi_volume:
        roi_volume = roi_volume[0]
    else:
        roi_volume = 1

    dose_high = np.argmax(dvh < (volume / roi_volume))
    y = volume / roi_volume
    x_range = [dose_high - 1, dose_high]
    y_range = [dvh[dose_high - 1], dvh[dose_high]]
    dose = np.interp(y, y_range, x_range) * 0.01

    return dose


# EUD = sum[ v(i) * D(i)^a ] ^ [1/a]
def calc_eud(dvh, a):
    v = -np.gradient(dvh)

    dose_bins = np.linspace(1, np.size(dvh), np.size(dvh))
    dose_bins = np.round(dose_bins, 3)
    bin_centers = dose_bins - 0.5
    eud = np.power(np.sum(np.multiply(v, np.power(bin_centers, a))), 1 / float(a))
    eud = np.round(eud, 2) * 0.01

    return eud


def get_study_instance_uids(**kwargs):
    study_instance_uids = {}
    complete_list = []
    for key, value in kwargs.iteritems():
        if key not in {'Plans', 'DVHs', 'Beams', 'Rxs'}:
            print key + ' is not a valid table name\nSelect from Plans, DVHs, Beams, or Rxs.'
            return
        study_instance_uids[key] = QuerySQL(key, value).study_instance_uid
        for sub_value in study_instance_uids[key]:
            complete_list.append(sub_value)
    study_instance_uids['unique'] = get_unique_list(complete_list)
    union_list = []
    for value in study_instance_uids['unique']:
        if is_uid_in_all_keys(value, study_instance_uids):
            union_list.append(value)
    study_instance_uids['union'] = union_list

    return study_instance_uids


def is_uid_in_all_keys(uid, uid_kwlist):
    key_answer = {}
    # Initialize a False value for each key
    for key in uid_kwlist.iterkeys():
        key_answer[key] = False
    # search for uid in each keyword fof uid_kwlist
    for key, value in uid_kwlist.iteritems():
        if uid in value:
            key_answer[key] = True

    final_answer = True
    # Product of all answer[key] values (except 'unique')
    for key, value in key_answer.iteritems():
        if key not in 'unique':
            final_answer *= value
    return final_answer


if __name__ == '__main__':
    pass
