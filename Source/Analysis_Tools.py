#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:48:19 2017

@author: nightowl
"""

import numpy as np
from DVH_SQL import DVH_SQL


class DVH:
    def __init__(self, *condition_str):

        sqlcnx = DVH_SQL()
        columns = """MRN, StudyInstanceUID, ROIName, Type, Volume, MinDose,
        MeanDose, MaxDose, DoseBinSize, VolumeString"""
        if condition_str:
            cursor_rtn = sqlcnx.query('DVHs', columns, condition_str[0])
        else:
            cursor_rtn = sqlcnx.query('DVHs', columns)

        max_dvh_length = 0
        for row in cursor_rtn:
            current_dvh_str = np.array(str(row[9]).split(','))
            current_size = np.size(current_dvh_str)
            if current_size > max_dvh_length:
                max_dvh_length = current_size

        num_rows = len(cursor_rtn)
        MRNs = {}
        study_uids = {}
        roi_institutional = {}
        roi_names = {}
        roi_types = {}
        rx_doses = np.zeros(num_rows)
        roi_volumes = np.zeros(num_rows)
        min_doses = np.zeros(num_rows)
        mean_doses = np.zeros(num_rows)
        max_doses = np.zeros(num_rows)
        dose_bin_sizes = np.zeros(num_rows)
        dvhs = np.zeros([max_dvh_length, len(cursor_rtn)])

        dvh_counter = 0
        for row in cursor_rtn:
            MRNs[dvh_counter] = str(row[0])
            study_uids[dvh_counter] = str(row[1])
            roi_institutional[dvh_counter]= str(row[2])
            roi_physician[dvh_counter] = str(row[3])
            roi_names[dvh_counter] = str(row[4])
            roi_types[dvh_counter] = str(row[5])

            condition = "MRN = '" + str(row[0])
            condition += "' and StudyInstanceUID = '"
            condition += str(study_uids[dvh_counter]) + "'"
            rx_dose_cursor = sqlcnx.query('Plans', 'RxDose', condition)
            rx_doses[dvh_counter] = rx_dose_cursor[0][0]

            roi_volumes[dvh_counter] = row[6]
            min_doses[dvh_counter] = row[7]
            mean_doses[dvh_counter] = row[8]
            max_doses[dvh_counter] = row[9]
            dose_bin_sizes[dvh_counter] = row[10]

            # Process volumeString to numpy array
            current_dvh_str = np.array(str(row[11]).split(','))
            current_dvh = current_dvh_str.astype(np.float)
            if max(current_dvh) > 0:
                current_dvh /= max(current_dvh)
            zero_fill = np.zeros(max_dvh_length - np.size(current_dvh))
            dvhs[:, dvh_counter] = np.concatenate((current_dvh, zero_fill))
            dvh_counter += 1

        self.MRN = MRNs
        self.study_uid = study_uids
        self.roi_name = roi_names
        self.roi_type = roi_types
        self.rx_dose = rx_doses
        self.volume = roi_volumes
        self.min_dose = min_doses
        self.mean_dose = mean_doses
        self.max_dose = max_doses
        self.dose_bin_size = dose_bin_sizes
        self.dvh = dvhs
        self.count = dvh_counter
        sqlcnx.cnx.close()

    def sort(self, sorted_indices):
        self.MRN = [self.MRN[x] for x in sorted_indices]
        self.study_uid = [self.study_uid[x] for x in sorted_indices]
        self.roi_name = [self.roi_name[x] for x in sorted_indices]
        self.roi_type = [self.roi_type[x] for x in sorted_indices]
        self.volume = [round(self.volume[x], 2) for x in sorted_indices]
        self.min_dose = [round(self.min_dose[x], 2) for x in sorted_indices]
        self.mean_dose = [round(self.mean_dose[x], 2) for x in sorted_indices]
        self.max_dose = [round(self.max_dose[x], 2) for x in sorted_indices]

        dvh_temp = np.empty_like(self.dvh)
        for x in range(0, np.size(self.dvh, 1)):
            np.copyto(dvh_temp[:, x], self.dvh[:, sorted_indices[x]])
        np.copyto(self.dvh, dvh_temp)

    def get_avg_dvh(self):

        avg_dvh = np.zeros([np.size(self.dvh, 0)])
        for x in range(0, self.count):
            avg_dvh += self.dvh[:, x] / np.max(self.dvh[:, x])
        avg_dvh /= self.count
        avg_dvh /= max(avg_dvh)

        return avg_dvh

    def get_dose_to_volume(self, volume):

        doses = np.zeros(self.count)
        for x in range(0, self.count):
            doses[x] = dose_to_volume(self.dvh[:, x], volume,
                                      self.volume[x], self.dose_bin_size[x])

        return doses

    def get_volume_of_dose(self, Dose):

        x = (np.ones(self.count) * Dose) / self.dose_bin_size
        x_range = [np.floor(x), np.ceil(x)]
        y_range = [self.dvh[int(np.floor(x))], self.dvh[int(np.ceil(x))]]
        roi_volume = np.interp(x, x_range, y_range)

        return roi_volume

    def coverage(self, rx_dose_fraction):

        answer = np.zeros(self.count)
        for x in range(0, self.count):
            answer[x] = self.get_volume_of_dose(float(self.rx_dose[x] * rx_dose_fraction))

        return answer


class DVH_Spread:
    def __init__(self, dvhs):
        dvh_len = np.size(dvhs, 0)

        minimum = np.zeros(dvh_len)
        q1 = np.zeros(dvh_len)
        mean = np.zeros(dvh_len)
        median = np.zeros(dvh_len)
        q3 = np.zeros(dvh_len)
        maximum = np.zeros(dvh_len)
        std = np.zeros(dvh_len)

        for x in range(0, dvh_len):
            minimum[x] = np.min(dvhs[x, :])
            q1[x] = np.percentile(dvhs[x, :], 25)
            mean[x] = np.mean(dvhs[x, :])
            median[x] = np.median(dvhs[x, :])
            q3[x] = np.percentile(dvhs[x, :], 75)
            maximum[x] = np.max(dvhs[x, :])
            std[x] = np.std(dvhs[x, :])

        # if std[x] < 0, std[x] = 0
        std = np.multiply(std, np.greater(std, np.zeros_like(std)))

        self.x = range(0, dvh_len)
        self.min = minimum
        self.q1 = q1
        self.mean = mean
        self.median = median
        self.q3 = q3
        self.max = maximum
        self.std = std


# Returns the isodose level outlining the given volume
def dose_to_volume(dvh, volume, dose_bin_size, *roi_volume):

    # if an roi_volume is not given, volume is assumed to be fractional
    if roi_volume:
        roi_volume = roi_volume[0]
    else:
        roi_volume = 1

    dose_high = np.argmax(dvh < volume / roi_volume)
    y = volume / roi_volume
    x_range = [dose_high - 1, dose_high]
    y_range = [dvh[dose_high - 1], dvh[dose_high]]
    dose = np.interp(y, y_range, x_range) * dose_bin_size

    return dose


# Just np.argsort with an order argument
def get_sorted_indices(to_be_sorted, *order):

    sorted_indicies = np.argsort(to_be_sorted)
    if order and order[0].lower() == 'descend':
        sorted_indicies = sorted_indicies[::-1]

    return sorted_indicies


# EUD = sum[ v(i) * D(i)^a ] ^ [1/a]
def get_EUD(dvh, dose_bin_size, a):

    v = -np.gradient(dvh) * dose_bin_size

    D = np.linspace(1, np.size(dvh), np.size(dvh))
    D *= dose_bin_size
    D -= (dose_bin_size / 2)
    D = np.round(D, 3)
    D_raised_a = np.power(D, a)

    EUD = np.power(np.sum(np.multiply(v, D_raised_a)), 1 / float(a))

    return EUD


if __name__ == '__main__':
    pass
