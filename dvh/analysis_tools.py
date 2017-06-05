#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:48:19 2017
@author: nightowl
"""

from __future__ import print_function
import numpy as np
from sql_connector import DVH_SQL
from sql_to_python import QuerySQL, get_unique_list
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
        rel_path = "preferences/eud_a-values.txt"
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
            elif self.roi_type[i].lower()[0:3] in {'gtv', 'ctv', 'ptv'}:
                current_a = float(-10)
            else:
                current_a = float(1)
            self.eud.append(calc_eud(current_dvh, current_a))
            self.eud_a_value.append(current_a)

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

    def get_stat_dvh(self, **kwargs):
        f = 5000

        if 'type' in kwargs:
            bin_count = self.bin_count
            if 'dose' in kwargs and kwargs['dose'] == 'relative':
                x_axis, dvhs = self.resample_dvh(f)
                bin_count = np.size(x_axis)
                if not kwargs['type']:
                    return x_axis
            else:
                dvhs = self.dvh

            dvh = np.zeros(bin_count)

            if 'volume' in kwargs and kwargs['volume'] == 'absolute':
                print('converting dvh to abs volume')
                dvhs = self.dvhs_to_abs_vol(dvhs)

            if kwargs['type'] == 'min':
                for x in range(0, bin_count):
                    dvh[x] = np.min(dvhs[x, :])

            elif kwargs['type'] == 'mean':
                for x in range(0, bin_count):
                    dvh[x] = np.mean(dvhs[x, :])

            elif kwargs['type'] == 'median':
                for x in range(0, bin_count):
                    dvh[x] = np.median(dvhs[x, :])

            elif kwargs['type'] == 'max':
                for x in range(0, bin_count):
                    dvh[x] = np.max(dvhs[x, :])

            elif kwargs['type'] == 'percentile':
                if 'percent' in kwargs and kwargs['percent']:
                    for x in range(0, bin_count):
                        dvh[x] = np.percentile(dvhs[x, :], kwargs['percent'])

            elif kwargs['type'] == 'std':
                for x in range(0, bin_count):
                    dvh[x] = np.std(dvhs[x, :])

            return dvh
        else:
            print("keyword argument of 'type=': min, mean, median, max, percentile, or std required")
            return False

    def get_standard_stat_dvh(self, **kwargs):
        f = 5000

        bin_count = self.bin_count
        if 'dose' in kwargs and kwargs['dose'] == 'relative':
            x_axis, dvhs = self.resample_dvh(f)
            bin_count = np.size(x_axis)
        else:
            dvhs = self.dvh

        if 'volume' in kwargs and kwargs['volume'] == 'absolute':
            print('converting dvh to abs volume')
            dvhs = self.dvhs_to_abs_vol(dvhs)

        dvh_min = np.zeros(bin_count)
        dvh_q1 = np.zeros(bin_count)
        dvh_mean = np.zeros(bin_count)
        dvh_median = np.zeros(bin_count)
        dvh_q3 = np.zeros(bin_count)
        dvh_max = np.zeros(bin_count)

        for x in range(0, bin_count):
            dvh_min[x] = np.min(dvhs[x, :])
            dvh_mean[x] = np.mean(dvhs[x, :])
            dvh_median[x] = np.median(dvhs[x, :])
            dvh_max[x] = np.max(dvhs[x, :])
            dvh_q1[x] = np.percentile(dvhs[x, :], 25)
            dvh_q3[x] = np.percentile(dvhs[x, :], 75)

        standard_stat_dvh = {'min': dvh_min,
                             'q1': dvh_q1,
                             'mean': dvh_mean,
                             'median': dvh_median,
                             'q3': dvh_q3,
                             'max': dvh_max}

        return standard_stat_dvh

    def dvhs_to_abs_vol(self, dvhs):
        new_dvhs = np.zeros_like(dvhs)
        for i in range(0, self.count):
            new_dvhs[:, i] = np.multiply(dvhs[:, i], self.volume[i])
        return new_dvhs

    def resample_dvh(self, f):
        min_rx_dose = np.min(self.rx_dose) * float(100)
        new_bin_count = int(np.divide(float(self.bin_count), min_rx_dose) * f)

        x1 = np.linspace(0, self.bin_count, self.bin_count)
        y2 = np.zeros([new_bin_count, self.count])
        for i in range(0, self.count):
            x2 = np.multiply(np.linspace(0, new_bin_count, new_bin_count), self.rx_dose[i] * float(100) / f)
            y2[:, i] = np.interp(x2, x1, self.dvh[:, i])
        x2 = np.divide(np.linspace(0, new_bin_count, new_bin_count), f)
        return x2, y2


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
            print(key, ' is not a valid table name\nSelect from Plans, DVHs, Beams, or Rxs.', sep=' ')
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
