#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:48:19 2017

@author: nightowl
"""

import numpy as np
from DVH_SQL import *


class DVH:
    def __init__(self, *condition_str):

        eud_a_values = {}
        with open('EUD_a-values.txt', 'r') as document:
            for line in document:
                line = line.strip().split(',')
                eud_a_values[line[0]] = float(line[1])

        sqlcnx = DVH_SQL()
        columns = """MRN, StudyInstanceUID, InstitutionalROI, PhysicianROI,
        ROIName, Type, Volume, MinDose, MeanDose, MaxDose, DoseBinSize, VolumeString"""
        if condition_str:
            cursor_rtn = sqlcnx.query('DVHs', columns, condition_str[0])
            self.query = condition_str[0]
        else:
            cursor_rtn = sqlcnx.query('DVHs', columns)
            self.query = ''

        max_dvh_length = 0
        for row in cursor_rtn:
            current_dvh_str = np.array(str(row[11]).split(','))
            current_size = np.size(current_dvh_str)
            if current_size > max_dvh_length:
                max_dvh_length = current_size

        num_rows = len(cursor_rtn)
        MRNs = {}
        study_uids = {}
        roi_institutional = {}
        roi_physician = {}
        roi_names = {}
        roi_types = {}
        rx_doses = np.zeros(num_rows)
        roi_volumes = np.zeros(num_rows)
        min_doses = np.zeros(num_rows)
        mean_doses = np.zeros(num_rows)
        max_doses = np.zeros(num_rows)
        dose_bin_sizes = np.zeros(num_rows)
        dvhs = np.zeros([max_dvh_length, len(cursor_rtn)])
        euds = np.zeros(num_rows)
        a_values = np.zeros(num_rows)

        dvh_counter = 0
        for row in cursor_rtn:
            MRNs[dvh_counter] = str(row[0])
            study_uids[dvh_counter] = str(row[1])
            roi_institutional[dvh_counter] = str(row[2])
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

            if eud_a_values in [roi_physician[dvh_counter]]:
                current_a = eud_a_values[roi_physician[dvh_counter]]
            elif roi_types[dvh_counter].lower() in {'gtv', 'ctv', 'ptv'}:
                current_a = float(-10)
            else:
                current_a = float(1)
            euds[dvh_counter] = get_EUD(current_dvh, 0.01, current_a)
            a_values[dvh_counter] = current_a

            dvh_counter += 1

        self.mrn = MRNs
        self.study_uid = study_uids
        self.roi_institutional = roi_institutional
        self.roi_physician = roi_physician
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
        self.eud = euds
        self.eud_a_value = a_values
        self.bin_count = max_dvh_length

        # Initialize properties
        # Calculating all of these can be computationally expensive
        # so using @property method below only calculates these if called
        self._min_dvh = np.ones(max_dvh_length)
        self._q1_dvh = np.ones(max_dvh_length)
        self._mean_dvh = np.ones(max_dvh_length)
        self._median_dvh = np.ones(max_dvh_length)
        self._q3_dvh = np.ones(max_dvh_length)
        self._max_dvh = np.ones(max_dvh_length)
        self._std_dvh = np.ones(max_dvh_length)

        sqlcnx.cnx.close()

    def __repr__(self):
        if self.count > 1:
            plural = 's'
        else:
            plural = ''
        rtn_str = 'This object contains %d Plan%s' % (self.count, plural)
        if self.query:
            rtn_str += ' such that %s.' % (self.query)

        # Create empty class to speed up dir()
        empty_class = DVH("StudyInstanceUID = '*'")

        properties = []
        functions = []
        for attr in dir(empty_class):
            if not attr.startswith('_'):
                if callable(getattr(empty_class, attr)):
                    functions.append(attr)
                else:
                    properties.append(attr)

        num_properties = len(properties)
        num_rows_to_print = num_properties / 3 + 1
        final_row_len = num_properties % 3

        rtn_str += '\n\nAvailable properties:\n'
        for i in range(0, num_rows_to_print - 1):
            x = i * 3
            temp = properties[x] + ' ' * (30 - len(properties[x]))
            temp += properties[x + 1] + ' ' * (30 - len(properties[x + 1]))
            temp += properties[x + 2] + ' ' * (30 - len(properties[x + 2]))
            rtn_str += temp + '\n'
        temp = ''
        for j in range(0, final_row_len):
            x = (i * 3) + 1
            temp += properties[x + j] + ' ' * (30 - len(properties[x + j]))
        rtn_str += temp

        num_functions = len(functions)
        num_rows_to_print = num_functions / 3 + 1
        final_row_len = num_functions % 3

        rtn_str += '\n\nAvailable functions:\n'
        for i in range(0, num_rows_to_print - 1):
            x = i * 3
            temp = functions[x] + ' ' * (30 - len(functions[x]))
            temp += functions[x + 1] + ' ' * (30 - len(functions[x + 1]))
            temp += functions[x + 2] + ' ' * (30 - len(functions[x + 2]))
            rtn_str += temp + '\n'
        temp = ''
        for j in range(0, final_row_len):
            x = (i * 3) + 1
            temp += functions[x + j] + ' ' * (30 - len(functions[x + j]))
        rtn_str += temp

        return rtn_str

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

    def get_percentile_dvh(self, percentile):
        dvh = np.zeros(self.bin_count)
        for x in range(0, self.bin_count):
            dvh[x] = np.percentile(self.dvh[x, :], percentile)
        return dvh

    def sort(self, to_be_sorted, *order):
        sorted_indices = np.argsort(to_be_sorted)
        if order and order[0].lower() == 'descending':
            sorted_indices = sorted_indices[::-1]
        self.mrn = [self.mrn[x] for x in sorted_indices]
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

    def get_dose_to_volume(self, volume):

        doses = np.zeros(self.count)
        for x in range(0, self.count):
            dvh = np.zeros(len(self.dvh))
            for y in range(0, len(self.dvh)):
                dvh[y] = self.dvh[y][x]
                doses[x] = dose_to_volume(dvh, volume, self.dose_bin_size[x],
                                          self.volume[x])

        return doses

    def get_volume_of_dose(self, Dose):

        x = (np.ones(self.count) * Dose) / self.dose_bin_size
        roi_volume = {}
        for i in range(0, self.count):
            x_range = [np.floor(x[i]), np.ceil(x[i])]
            y_range = [self.dvh[int(np.floor(x[i]))][i], self.dvh[int(np.ceil(x[i]))][i]]
            roi_volume[i] = np.round(np.interp(x[i], x_range, y_range), 3)

        return roi_volume

    def coverage(self, rx_dose_fraction):

        answer = np.zeros(self.count)
        for x in range(0, self.count):
            answer[x] = self.get_volume_of_dose(float(self.rx_dose[x] * rx_dose_fraction))

        return answer


# Returns the isodose level outlining the given volume
def dose_to_volume(dvh, volume, dose_bin_size, *roi_volume):
    # if an roi_volume is not given, volume is assumed to be fractional
    if roi_volume:
        roi_volume = roi_volume[0]
    else:
        roi_volume = 1

    dose_high = np.argmax(dvh < (volume / roi_volume))
    y = volume / roi_volume
    x_range = [dose_high - 1, dose_high]
    y_range = [dvh[dose_high - 1], dvh[dose_high]]
    dose = np.interp(y, y_range, x_range) * dose_bin_size

    return dose


# EUD = sum[ v(i) * D(i)^a ] ^ [1/a]
def get_EUD(dvh, dose_bin_size, a):
    v = -np.gradient(dvh) * dose_bin_size

    D = np.linspace(1, np.size(dvh), np.size(dvh))
    D *= dose_bin_size
    D -= (dose_bin_size / 2)
    D = np.round(D, 3)
    D_raised_a = np.power(D, a)

    EUD = np.power(np.sum(np.multiply(v, D_raised_a)), 1 / float(a))
    EUD = np.round(EUD, 2)

    return EUD


if __name__ == '__main__':
    pass
