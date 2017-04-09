#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 18:48:19 2017
@author: nightowl
"""

import numpy as np
from DVH_SQL import *
from prettytable import PrettyTable
import matplotlib.pyplot as plt


class DVH:
    def __init__(self, db_constraints, *condition_str):

        cnx = DVH_SQL()
        columns = """MRN, StudyInstanceUID, InstitutionalROI, PhysicianROI,
        ROIName, Type, Volume, MinDose, MeanDose, MaxDose, VolumeString"""

        if db_constraints == 'all':
            db_constraints_str = ''
        else:
            key = db_constraints[0]
            db_constraints_list = []
            for i in range(1, len(db_constraints)):
                db_constraints_list.append(db_constraints[i])
            db_constraints_str = key + " in ('"
            db_constraints_str += "', '".join(db_constraints_list)
            db_constraints_str += "')"

        if condition_str:
            condition_str_final = condition_str[0] + " and " + db_constraints_str
            cursor_rtn = cnx.query('DVHs', columns, condition_str_final)
            self.query = condition_str[0]
        else:
            cursor_rtn = cnx.query('DVHs', columns, db_constraints_str)
            self.query = ''

        max_dvh_length = 0
        for row in cursor_rtn:
            current_dvh_str = np.array(str(row[10]).split(','))
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
        dvhs = np.zeros([max_dvh_length, len(cursor_rtn)])
        euds = np.zeros(num_rows)
        a_values = np.zeros(num_rows)

        eud_a_values = {}
        with open('EUD_a-values.txt', 'r') as document:
            for line in document:
                line = line.strip().split(',')
                eud_a_values[line[0]] = float(line[1])

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
            rx_dose_cursor = cnx.query('Plans', 'RxDose', condition)
            rx_doses[dvh_counter] = rx_dose_cursor[0][0]

            roi_volumes[dvh_counter] = row[6]
            min_doses[dvh_counter] = row[7]
            mean_doses[dvh_counter] = row[8]
            max_doses[dvh_counter] = row[9]

            # Process volumeString to numpy array
            current_dvh_str = np.array(str(row[10]).split(','))
            current_dvh = current_dvh_str.astype(np.float)
            if max(current_dvh) > 0:
                current_dvh /= max(current_dvh)
            zero_fill = np.zeros(max_dvh_length - np.size(current_dvh))
            dvhs[:, dvh_counter] = np.concatenate((current_dvh, zero_fill))

            if roi_physician[dvh_counter] in eud_a_values:
                current_a = eud_a_values[roi_physician[dvh_counter]]
            elif roi_types[dvh_counter].lower() in {'gtv', 'ctv', 'ptv'}:
                current_a = float(-10)
            else:
                current_a = float(1)
            euds[dvh_counter] = calc_eud(current_dvh, current_a)
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

        cnx.cnx.close()

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
        document.close().t

    def roi_statistics(self):
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
                doses[x] = dose_to_volume(dvh, volume, self.volume[x])

        return doses

    def get_volume_of_dose(self, dose):

        x = (np.ones(self.count) * dose)
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

    def plot_dvh(self):
        x_axis = range(0, self.bin_count)
        for i in range(0, self.count):
            plt.plot(x_axis, self.dvh[:, i], label=self.mrn[i])
        plt.legend(loc='best')
        plt.xlabel('Dose (cGy)')
        plt.ylabel('Relative Volume')
        plt.title(self.query)

    def plot_dvh_spread(self):
        x_axis = range(0, self.bin_count)
        plt.plot(x_axis, self.min_dvh, label='Min', linestyle=":", color='black')
        plt.plot(x_axis, self.q1_dvh, label='Q1', linestyle="--", color='navy', linewidth=1.5)
        plt.plot(x_axis, self.median_dvh, label='Median', color='crimson', linewidth=2)
        plt.plot(x_axis, self.mean_dvh, label='Mean', color='deepskyblue', linewidth=2)
        plt.plot(x_axis, self.q3_dvh, label='Q3', linestyle="--", color='navy', linewidth=1.5)
        plt.plot(x_axis, self.max_dvh, label='Max', linestyle=":", color='black')
        plt.legend(loc='best')
        plt.xlabel('Dose (cGy)')
        plt.ylabel('Relative Volume')
        title = 'DVH Spread of ' + self.query
        plt.title(title)


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


if __name__ == '__main__':
    pass
