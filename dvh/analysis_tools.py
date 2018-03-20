#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:48:19 2017
@author: nightowl
"""

from __future__ import print_function
from future.utils import listitems
import numpy as np
from sql_connector import DVH_SQL
from sql_to_python import QuerySQL, get_unique_list
from options import RESAMPLED_DVH_BIN_COUNT


# This class retrieves DVH data from the SQL database and calculates statistical DVHs (min, max, quartiles)
# It also provides some inspection tools of the retrieved data
class DVH:
    def __init__(self, **kwargs):

        if 'uid' in kwargs:
            constraints_str = "study_instance_uid in ('%s')" % "', '".join(kwargs['uid'])
            if 'dvh_condition' in kwargs and kwargs['dvh_condition']:
                constraints_str = " and " + constraints_str
        else:
            constraints_str = ''

        if 'dvh_condition' in kwargs and kwargs['dvh_condition']:
            constraints_str = "(%s)%s" % (kwargs['dvh_condition'], constraints_str)
            self.query = kwargs['dvh_condition']
        else:
            self.query = ''

        cnx = DVH_SQL()

        # Get DVH data from SQL
        dvh_data = QuerySQL('DVHs', constraints_str)
        for key, value in dvh_data.__dict__.items():
            if not key.startswith("__"):
                setattr(self, key, value)

        # Add these properties to dvh_data since they aren't in the DVHs SQL table
        self.count = len(self.mrn)
        self.rx_dose = []

        self.bin_count = 0
        for value in self.dvh_string:
            current_dvh_str = np.array(str(value).split(','))
            current_size = np.size(current_dvh_str)
            if current_size > self.bin_count:
                self.bin_count = current_size
        self.dvh = np.zeros([self.bin_count, self.count])

        # Get needed values not in DVHs table
        for i in range(0, self.count):
            # Get Rx Doses
            condition = "mrn = '%s' and study_instance_uid = '%s'" % (self.mrn[i], self.study_instance_uid[i])
            rx_dose_cursor = cnx.query('Plans', 'rx_dose', condition)
            self.rx_dose.append(rx_dose_cursor[0][0])

            # Process dvh_string to numpy array, and pad with zeros at the end
            # so that all dvhs are the same length
            current_dvh = np.array(self.dvh_string[i].split(','), dtype='|S4').astype(np.float)
            current_dvh_max = np.max(current_dvh)
            if current_dvh_max > 0:
                current_dvh = np.divide(current_dvh, current_dvh_max)
            zero_fill = np.zeros(self.bin_count - len(current_dvh))
            self.dvh[:, i] = np.concatenate((current_dvh, zero_fill))

    def get_percentile_dvh(self, percentile):
        return np.percentile(self.dvh, percentile, 1)

    def get_dose_to_volume(self, volume, **kwargs):
        doses = np.zeros(self.count)
        for x in range(0, self.count):
            dvh = np.zeros(len(self.dvh))
            for y in range(0, len(self.dvh)):
                dvh[y] = self.dvh[y][x]
            if 'input' in kwargs and kwargs['input'] == 'relative':
                doses[x] = dose_to_volume(dvh, volume)
            else:
                # if self.volume[x] is zero, dose_to_volume encounters a divide / 0 error
                if self.volume[x]:
                    doses[x] = dose_to_volume(dvh, volume, self.volume[x])
                else:
                    doses[x] = 0
        if 'output' in kwargs and kwargs['output'] == 'relative':
            if self.rx_dose[0]:
                doses = np.divide(doses * 100, self.rx_dose[0:self.count])
            else:
                self.rx_dose[0] = 1  # if review dvh isn't defined, the following line would crash
                doses = np.divide(doses * 100, self.rx_dose[0:self.count])
                self.rx_dose[0] = 0
                doses[0] = 0

        return doses.tolist()

    def get_volume_of_dose(self, dose, **kwargs):
        volumes = np.zeros(self.count)
        for x in range(0, self.count):

            dvh = np.zeros(len(self.dvh))
            for y in range(0, len(self.dvh)):
                dvh[y] = self.dvh[y][x]
            if 'input' in kwargs and kwargs['input'] == 'relative':
                if isinstance(self.rx_dose[x], basestring):
                    volumes[x] = 0
                else:
                    volumes[x] = volume_of_dose(dvh, dose * self.rx_dose[x])
            else:
                volumes[x] = volume_of_dose(dvh, dose)

        if 'output' in kwargs and kwargs['output'] == 'absolute':
            volumes = np.multiply(volumes, self.volume[0:self.count])
        else:
            volumes = np.multiply(volumes, 100.)

        return volumes.tolist()

    def coverage(self, rx_dose_fraction):

        answer = np.zeros(self.count)
        for x in range(0, self.count):
            answer[x] = self.get_volume_of_dose(float(self.rx_dose[x] * rx_dose_fraction))

        return answer

    def get_resampled_x_axis(self):
        x_axis, dvhs = self.resample_dvh()
        return x_axis

    def get_stat_dvh(self, **kwargs):
        if 'type' in kwargs:
            stat_type = kwargs['type']
            if 'dose' in kwargs and kwargs['dose'] == 'relative':
                x_axis, dvhs = self.resample_dvh()
            else:
                dvhs = self.dvh

            if 'volume' in kwargs and kwargs['volume'] == 'absolute':
                dvhs = self.dvhs_to_abs_vol(dvhs)

            stat_function = {'min': np.min,
                             'mean': np.mean,
                             'median': np.median,
                             'max': np.max,
                             'std': np.std}
            dvh = stat_function[stat_type](dvhs, 1)

            return dvh
        else:
            print("keyword argument of 'type=': min, mean, median, max, percentile, or std required")
            return False

    def get_standard_stat_dvh(self, **kwargs):
        if 'dose' in kwargs and kwargs['dose'] == 'relative':
            x_axis, dvhs = self.resample_dvh()
        else:
            dvhs = self.dvh

        if 'volume' in kwargs and kwargs['volume'] == 'absolute':
            dvhs = self.dvhs_to_abs_vol(dvhs)

        standard_stat_dvh = {'min': np.min(dvhs, 1),
                             'q1': np.percentile(dvhs, 25, 1),
                             'mean': np.mean(dvhs, 1),
                             'median': np.median(dvhs, 1),
                             'q3': np.percentile(dvhs, 75, 1),
                             'max': np.max(dvhs, 1)}

        return standard_stat_dvh

    def dvhs_to_abs_vol(self, dvhs):
        return np.multiply(dvhs, self.volume)

    def resample_dvh(self):
        min_rx_dose = np.min(self.rx_dose) * 100.
        new_bin_count = int(np.divide(float(self.bin_count), min_rx_dose) * RESAMPLED_DVH_BIN_COUNT)

        x1 = np.linspace(0, self.bin_count, self.bin_count)
        y2 = np.zeros([new_bin_count, self.count])
        for i in range(0, self.count):
            x2 = np.multiply(np.linspace(0, new_bin_count, new_bin_count),
                             self.rx_dose[i] * 100. / RESAMPLED_DVH_BIN_COUNT)
            y2[:, i] = np.interp(x2, x1, self.dvh[:, i])
        x2 = np.divide(np.linspace(0, new_bin_count, new_bin_count), RESAMPLED_DVH_BIN_COUNT)
        return x2, y2


# Returns the isodose level outlining the given volume
def dose_to_volume(dvh, volume, *roi_volume):

    # if an roi_volume is not given, volume is assumed to be fractional
    if roi_volume:
        if isinstance(roi_volume[0], basestring):
            return 0
        roi_volume = roi_volume[0]
    else:
        roi_volume = 1

    dose_high = np.argmax(dvh < (volume / roi_volume))
    y = volume / roi_volume
    x_range = [dose_high - 1, dose_high]
    y_range = [dvh[dose_high - 1], dvh[dose_high]]
    dose = np.interp(y, y_range, x_range) * 0.01

    return dose


def volume_of_dose(dvh, dose):

    x = [int(np.floor(dose * 100)), int(np.ceil(dose * 100))]
    if len(dvh) < x[1]:
        return dvh[-1]
    y = [dvh[x[0]], dvh[x[1]]]
    roi_volume = np.interp(float(dose), x, y)

    return roi_volume


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
    uids = {}
    complete_list = []
    for key, value in listitems(kwargs):
        uids[key] = QuerySQL(key, value).study_instance_uid
        complete_list.extend(uids[key])

    uids['unique'] = get_unique_list(complete_list)
    uids['union'] = [value for value in uids['unique'] if is_uid_in_all_keys(value, uids)]

    return uids


def is_uid_in_all_keys(uid, uid_kwlist):
    key_answer = {}
    # Initialize a False value for each key
    for key in list(uid_kwlist):
        key_answer[key] = False
    # search for uid in each keyword fof uid_kwlist
    for key, value in listitems(uid_kwlist):
        if uid in value:
            key_answer[key] = True

    final_answer = True
    # Product of all answer[key] values (except 'unique')
    for key, value in listitems(key_answer):
        if key not in 'unique':
            final_answer *= value
    return final_answer


if __name__ == '__main__':
    pass
