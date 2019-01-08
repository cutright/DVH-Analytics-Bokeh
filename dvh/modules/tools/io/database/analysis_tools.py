#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:48:19 2017
@author: nightowl
"""

from __future__ import print_function
import numpy as np
from sql_connector import DVH_SQL
from sql_to_python import QuerySQL
from ..preferences.options import load_options


# This class retrieves DVH data from the SQL database and calculates statistical DVHs (min, max, quartiles)
# It also provides some inspection tools of the retrieved data
class DVH:
    def __init__(self, uid=None, dvh_condition=None):
        """
        This class will retrieve DVHs and other data in the DVH SQL table meeting the given constraints,
        it will also parse the DVH_string into python lists and retrieve the associated Rx dose
        :param uid: a list of allowed study_instance_uids in data set
        :param dvh_condition: a string in SQL syntax applied to a DVH Table query
        """

        if uid:
            constraints_str = "study_instance_uid in ('%s')" % "', '".join(uid)
            if dvh_condition:
                constraints_str = " and " + constraints_str
        else:
            constraints_str = ''

        if dvh_condition:
            constraints_str = "(%s)%s" % (dvh_condition, constraints_str)
            self.query = dvh_condition
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

        self.dth = []

        # Get needed values not in DVHs table
        for i in range(self.count):
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

            # Process dth_string to numpy array
            try:
                self.dth.append(np.array(self.dth_string[i].split(','), dtype='|S4').astype(np.float))
            except:
                self.dth.append(np.array([0]))

    def get_percentile_dvh(self, percentile):
        """
        :param percentile: the percentile to calculate for each dose-bin
        :return: a single DVH such that each bin is the given percentile of each bin over the whole sample
        :rtype: numpy 1D array
        """
        return np.percentile(self.dvh, percentile, 1)

    def get_dose_to_volume(self, volume, volume_scale='absolute', dose_scale='absolute'):
        """
        :param volume: the specified volume in cm^3
        :param volume_scale: either 'relative' or 'absolute'
        :param dose_scale: either 'relative' or 'absolute'
        :return: the dose in Gy to the specified volume
        :rtype: list
        """
        doses = np.zeros(self.count)
        for x in range(self.count):
            dvh = np.zeros(len(self.dvh))
            for y in range(len(self.dvh)):
                dvh[y] = self.dvh[y][x]
            if volume_scale == 'relative':
                doses[x] = dose_to_volume(dvh, volume)
            else:
                if self.volume[x]:
                    doses[x] = dose_to_volume(dvh, volume/self.volume[x])
                else:
                    doses[x] = 0
        if dose_scale == 'relative':
            if self.rx_dose[0]:
                doses = np.divide(doses * 100, self.rx_dose[0:self.count])
            else:
                self.rx_dose[0] = 1  # if review dvh isn't defined, the following line would crash
                doses = np.divide(doses * 100, self.rx_dose[0:self.count])
                self.rx_dose[0] = 0
                doses[0] = 0

        return doses.tolist()

    def get_volume_of_dose(self, dose, dose_scale='absolute', volume_scale='absolute'):
        """
        :param dose: input dose use to calculate a volume of dose for entire sample
        :param dose_scale: either 'absolute' or 'relative'
        :param volume_scale: either 'absolute' or 'relative'
        :return: a list of V_dose
        :rtype: list
        """
        volumes = np.zeros(self.count)
        for x in range(self.count):

            dvh = np.zeros(len(self.dvh))
            for y in range(len(self.dvh)):
                dvh[y] = self.dvh[y][x]
            if dose_scale == 'relative':
                if isinstance(self.rx_dose[x], basestring):
                    volumes[x] = 0
                else:
                    volumes[x] = volume_of_dose(dvh, dose * self.rx_dose[x])
            else:
                volumes[x] = volume_of_dose(dvh, dose)

        if volume_scale == 'absolute':
            volumes = np.multiply(volumes, self.volume[0:self.count])
        else:
            volumes = np.multiply(volumes, 100.)

        return volumes.tolist()

    def coverage(self, rx_dose_fraction):
        """
        :param rx_dose_fraction: relative rx dose to calculate fractional coverage
        :return: fractional coverage
        :rtype: list
        """

        answer = np.zeros(self.count)
        for x in range(self.count):
            answer[x] = self.get_volume_of_dose(float(self.rx_dose[x] * rx_dose_fraction))

        return answer

    def get_resampled_x_axis(self):
        """
        :return: the x axis of a resampled dvh
        """
        x_axis, dvhs = self.resample_dvh()
        return x_axis

    def get_stat_dvh(self, stat_type='mean', dose_scale='absolute', volume_scale='relative'):
        """
        :param stat_type: either min, mean, median, max, or std
        :param dose_scale: either 'absolute' or 'relative'
        :param volume_scale: either 'absolute' or 'relative'
        :return: a single dvh where each bin is the stat_type of each bin for the entire sample
        :rtype: numpy 1D array
        """
        if dose_scale == 'relative':
            x_axis, dvhs = self.resample_dvh()
        else:
            dvhs = self.dvh

        if volume_scale == 'absolute':
            dvhs = self.dvhs_to_abs_vol(dvhs)

        stat_function = {'min': np.min,
                         'mean': np.mean,
                         'median': np.median,
                         'max': np.max,
                         'std': np.std}
        dvh = stat_function[stat_type](dvhs, 1)

        return dvh

    def get_standard_stat_dvh(self, dose_scale='absolute', volume_scale='relative'):
        """
        :param dose_scale: either 'absolute' or 'relative'
        :param volume_scale: either 'absolute' or 'relative'
        :return: a standard set of statistical dvhs (min, q1, mean, median, q1, and max)
        :rtype: dict
        """
        if dose_scale == 'relative':
            x_axis, dvhs = self.resample_dvh()
        else:
            dvhs = self.dvh

        if volume_scale == 'absolute':
            dvhs = self.dvhs_to_abs_vol(dvhs)

        standard_stat_dvh = {'min': np.min(dvhs, 1),
                             'q1': np.percentile(dvhs, 25, 1),
                             'mean': np.mean(dvhs, 1),
                             'median': np.median(dvhs, 1),
                             'q3': np.percentile(dvhs, 75, 1),
                             'max': np.max(dvhs, 1)}

        return standard_stat_dvh

    def dvhs_to_abs_vol(self, dvhs):
        """
        :param dvhs: relative DVHs (dvh[bin, roi_index])
        :return: absolute DVHs
        :rtype: numpy 2D array
        """
        return np.multiply(dvhs, self.volume)

    def resample_dvh(self):
        """
        :return: x-axis, y-axis of resampled DVHs
        """

        resampled_bin_count = load_options(return_attr='RESAMPLED_DVH_BIN_COUNT')

        min_rx_dose = np.min(self.rx_dose) * 100.
        new_bin_count = int(np.divide(float(self.bin_count), min_rx_dose) * resampled_bin_count)

        x1 = np.linspace(0, self.bin_count, self.bin_count)
        y2 = np.zeros([new_bin_count, self.count])
        for i in range(self.count):
            x2 = np.multiply(np.linspace(0, new_bin_count, new_bin_count),
                             self.rx_dose[i] * 100. / resampled_bin_count)
            y2[:, i] = np.interp(x2, x1, self.dvh[:, i])
        x2 = np.divide(np.linspace(0, new_bin_count, new_bin_count), resampled_bin_count)
        return x2, y2


# Returns the isodose level outlining the given volume
def dose_to_volume(dvh, rel_volume):
    """
    :param dvh: a single dvh
    :param rel_volume: fractional volume
    :return: minimum dose in Gy of specified volume
    """

    # Return the maximum dose instead of extrapolating
    if rel_volume < dvh[-1]:
        return len(dvh) * 0.01

    dose_high = np.argmax(dvh < rel_volume)
    y = rel_volume
    x_range = [dose_high - 1, dose_high]
    y_range = [dvh[dose_high - 1], dvh[dose_high]]
    dose = np.interp(y, y_range, x_range) * 0.01

    return dose


def volume_of_dose(dvh, dose):
    """
    :param dvh: a single dvh
    :param dose: dose in cGy
    :return: volume in cm^3 of roi receiving at least the specified dose
    """

    x = [int(np.floor(dose * 100)), int(np.ceil(dose * 100))]
    if len(dvh) < x[1]:
        return dvh[-1]
    y = [dvh[x[0]], dvh[x[1]]]
    roi_volume = np.interp(float(dose), x, y)

    return roi_volume


def calc_eud(dvh, a):
    """
    EUD = sum[ v(i) * D(i)^a ] ^ [1/a]
    :param dvh: a single DVH as a list of numpy 1D array with 1cGy bins
    :param a: standard a-value for EUD calculations, organ and dose fractionation specific
    :return: equivalent uniform dose
    """
    v = -np.gradient(dvh)

    dose_bins = np.linspace(1, np.size(dvh), np.size(dvh))
    dose_bins = np.round(dose_bins, 3)
    bin_centers = dose_bins - 0.5
    eud = np.power(np.sum(np.multiply(v, np.power(bin_centers, a))), 1. / float(a))
    eud = np.round(eud, 2) * 0.01

    return eud
