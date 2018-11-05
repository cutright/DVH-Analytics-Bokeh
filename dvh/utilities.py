#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
from future.utils import listitems
from sql_to_python import QuerySQL
from sql_connector import DVH_SQL
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dicompylercore import dicomparser
import os
import sys
import numpy as np
from get_settings import get_settings
import pickle
from math import ceil
from shapely import speedups
import roi_tools
try:
    import pydicom as dicom  # for pydicom >= 1.0
except:
    import dicom


# Enable shapely calculations using C, as opposed to the C++ default
if speedups.available:
    speedups.enable()

PREFERENCE_PATHS = {''}
MIN_SLICE_THICKNESS = 2  # Update method to pull from DICOM


def recalculate_ages(*custom_condition):

    if custom_condition:
        custom_condition = " AND " + custom_condition[0]
    else:
        custom_condition = ''

    dvh_data = QuerySQL('Plans', "mrn != ''" + custom_condition)
    cnx = DVH_SQL()

    for i in range(len(dvh_data.mrn)):
        mrn = dvh_data.mrn[i]
        uid = dvh_data.study_instance_uid[i]
        sim_study_date = dvh_data.sim_study_date[i].split('-')
        birth_date = dvh_data.birth_date[i].split('-')

        try:
            birth_year = int(birth_date[0])
            birth_month = int(birth_date[1])
            birth_day = int(birth_date[2])
            birth_date_obj = datetime(birth_year, birth_month, birth_day)

            sim_study_year = int(sim_study_date[0])
            sim_study_month = int(sim_study_date[1])
            sim_study_day = int(sim_study_date[2])
            sim_study_date_obj = datetime(sim_study_year, sim_study_month, sim_study_day)

            if sim_study_date == '1800-01-01':
                age = '(NULL)'
            else:
                age = relativedelta(sim_study_date_obj, birth_date_obj).years

            condition = "study_instance_uid = '" + uid + "'"
            cnx.update('Plans', 'age', str(age), condition)
        except:
            print("Update Failed for", mrn, "sim date:", sim_study_date, "birthdate", birth_date, sep=' ')

    cnx.close()


def recalculate_total_mu(*custom_condition):

    if custom_condition:
        custom_condition = " AND " + custom_condition[0]
    else:
        custom_condition = ''

    # Get entire table
    beam_data = QuerySQL('Beams', "mrn != ''" + custom_condition)
    cnx = DVH_SQL()

    plan_mus = {}
    for i in range(len(beam_data.study_instance_uid)):
        uid = beam_data.study_instance_uid[i]
        beam_mu = beam_data.beam_mu[i]
        fxs = float(beam_data.fx_count[i])
        if uid not in list(plan_mus):
            plan_mus[uid] = 0.

        plan_mus[uid] += beam_mu * fxs

    for uid in list(plan_mus):
        cnx.update('Plans', 'total_mu', str(round(plan_mus[uid], 1)), "study_instance_uid = '%s'" % uid)

    cnx.close()


def datetime_str_to_obj(datetime_str):
    """
    :param datetime_str: a string representation of a datetime as formatted in DICOM (YYYYMMDDHHMMSS)
    :return: a datetime object
    :rtype: datetime
    """

    year = int(datetime_str[0:4])
    month = int(datetime_str[4:6])
    day = int(datetime_str[6:8])
    hour = int(datetime_str[8:10])
    minute = int(datetime_str[10:12])
    second = int(datetime_str[12:14])

    datetime_obj = datetime(year, month, day, hour, minute, second)

    return datetime_obj


def date_str_to_obj(date_str):
    """
    :param date_str: a string representation of a date as formatted in DICOM (YYYYMMDD)
    :return: a datetime object
    :rtype: datetime
    """

    year = int(date_str[0:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])

    return datetime(year, month, day)


def platform():
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('darwin'):
        return 'mac'
    return 'linux'


def is_import_settings_defined():
    abs_file_path = get_settings('import')
    if os.path.isfile(abs_file_path):
        return True
    else:
        return False


def is_sql_connection_defined():
    """
    Checks if sql_connection.cnf exists
    :rtype: bool
    """
    abs_file_path = get_settings('sql')
    if os.path.isfile(abs_file_path):
        return True
    else:
        return False


def write_import_settings(directories):

    import_text = ['inbox ' + directories['inbox'],
                   'imported ' + directories['imported'],
                   'review ' + directories['review']]
    import_text = '\n'.join(import_text)

    abs_file_path = get_settings('import')

    with open(abs_file_path, "w") as text_file:
        text_file.write(import_text)


def write_sql_connection_settings(config):
    """
    :param config: a dict with keys 'host', 'dbname', 'port' and optionally 'user' and 'password'
    """

    text = ["%s %s" % (key, value) for key, value in listitems(config) if value]
    text = '\n'.join(text)

    abs_file_path = get_settings('sql')

    with open(abs_file_path, "w") as text_file:
        text_file.write(text)


def validate_import_settings():

    abs_file_path = get_settings('import')

    with open(abs_file_path, 'r') as document:
        config = {}
        for line in document:
            line = line.split()
            if not line:
                continue
            try:
                config[line[0]] = line[1:][0]
            except:
                config[line[0]] = ''

    valid = True
    for key, value in listitems(config):
        if not os.path.isdir(value):
            print('invalid', key, 'path:', value, sep=" ")
            valid = False

    return valid


def validate_sql_connection(config=None, verbose=False):
    """
    :param config: a dict with keys 'host', 'dbname', 'port' and optionally 'user' and 'password'
    :param verbose: boolean indicating if cmd line printing should be performed
    :return:
    """

    valid = True
    if config:
        try:
            cnx = DVH_SQL(config)
            cnx.close()
        except:
            valid = False
    else:
        try:
            cnx = DVH_SQL()
            cnx.close()
        except:
            valid = False

    if verbose:
        if valid:
            print("SQL DB is alive!")
        else:
            print("Connection to SQL DB could not be established.")
            if not is_sql_connection_defined():
                print("ERROR: SQL settings are not yet defined.  Please run:\n",
                      "    $ dvh settings --sql", sep="")

    return valid


def change_angle_origin(angles, max_positive_angle):
    """
    :param angles: a list of angles
    :param max_positive_angle: the maximum positive angle, angles greater than this will be shifted to negative angles
    :return: list of the same angles, but none exceed the max
    :rtype: list
    """
    if len(angles) == 1:
        if angles[0] > max_positive_angle:
            return [angles[0] - 360]
        else:
            return angles
    new_angles = []
    for angle in angles:
        if angle > max_positive_angle:
            new_angles.append(angle - 360)
        elif angle == max_positive_angle:
            if angle == angles[0] and angles[1] > max_positive_angle:
                new_angles.append(angle - 360)
            elif angle == angles[-1] and angles[-2] > max_positive_angle:
                new_angles.append(angle - 360)
            else:
                new_angles.append(angle)
        else:
            new_angles.append(angle)
    return new_angles


def update_centroid_in_db(study_instance_uid, roi_name):
    """
    This function will recalculate the centroid of an roi based on data in the SQL DB.
    :param study_instance_uid: uid as specified in SQL DB
    :param roi_name: roi_name as specified in SQL DB
    """

    coordinates_string = DVH_SQL().query('dvhs',
                                         'roi_coord_string',
                                         "study_instance_uid = '%s' and roi_name = '%s'"
                                         % (study_instance_uid, roi_name))

    roi = roi_tools.get_planes_from_string(coordinates_string[0][0])
    centroid = roi_tools.calc_centroid(roi)

    centroid = [str(round(v, 3)) for v in centroid]

    DVH_SQL().update('dvhs',
                     'centroid',
                     ','.join(centroid),
                     "study_instance_uid = '%s' and roi_name = '%s'"
                     % (study_instance_uid, roi_name))


def update_cross_section_in_db(study_instance_uid, roi_name):
    """
    This function will recalculate the centoid of an roi based on data in the SQL DB.
    :param study_instance_uid: uid as specified in SQL DB
    :param roi_name: roi_name as specified in SQL DB
    """

    coordinates_string = DVH_SQL().query('dvhs',
                                         'roi_coord_string',
                                         "study_instance_uid = '%s' and roi_name = '%s'"
                                         % (study_instance_uid, roi_name))

    roi = roi_tools.get_planes_from_string(coordinates_string[0][0])
    area = roi_tools.calc_cross_section(roi)

    DVH_SQL().update('dvhs',
                     'cross_section_max',
                     area['max'],
                     "study_instance_uid = '%s' and roi_name = '%s'"
                     % (study_instance_uid, roi_name))

    DVH_SQL().update('dvhs',
                     'cross_section_median',
                     area['median'],
                     "study_instance_uid = '%s' and roi_name = '%s'"
                     % (study_instance_uid, roi_name))


def calc_spread(roi):
    """
    :param roi: a "sets of points" formatted list
    :return: x, y, z dimensions of a rectangular prism encompassing roi
    :rtype: list
    """
    all_points = {'x': [], 'y': [], 'z': []}

    for z in list(roi):
        for polygon in roi[z]:
            for point in polygon:
                all_points['x'].append(point[0])
                all_points['y'].append(point[1])
                all_points['z'].append(point[2])

    all_points = {'x': np.array(all_points['x']),
                  'y': np.array(all_points['y']),
                  'z': np.array(all_points['z'])}

    if len(all_points['x'] > 1):
        spread = [abs(float(np.max(all_points[dim]) - np.min(all_points[dim]))) for dim in ['x', 'y', 'z']]
    else:
        spread = [0, 0, 0]

    return spread


def update_spread_in_db(study_instance_uid, roi_name):
    """
    This function will recalculate the spread of an roi based on data in the SQL DB.
    :param study_instance_uid: uid as specified in SQL DB
    :param roi_name: roi_name as specified in SQL DB
    """

    coordinates_string = DVH_SQL().query('dvhs',
                                         'roi_coord_string',
                                         "study_instance_uid = '%s' and roi_name = '%s'"
                                         % (study_instance_uid, roi_name))

    roi = roi_tools.get_planes_from_string(coordinates_string[0][0])
    spread = calc_spread(roi)

    spread = [str(round(v/10., 3)) for v in spread]

    DVH_SQL().update('dvhs',
                     'spread_x',
                     spread[0],
                     "study_instance_uid = '%s' and roi_name = '%s'"
                     % (study_instance_uid, roi_name))
    DVH_SQL().update('dvhs',
                     'spread_y',
                     spread[1],
                     "study_instance_uid = '%s' and roi_name = '%s'"
                     % (study_instance_uid, roi_name))
    DVH_SQL().update('dvhs',
                     'spread_z',
                     spread[2],
                     "study_instance_uid = '%s' and roi_name = '%s'"
                     % (study_instance_uid, roi_name))


def calc_dth(min_distances):
    """
    :param min_distances:
    :return: histogram of distances in 0.1mm bin widths
    """

    bin_count = int(ceil(np.max(min_distances) * 10.))
    dst, bins = np.histogram(min_distances, bins=bin_count)

    return dst


def update_min_distances_in_db(study_instance_uid, roi_name):
    """
    This function will recalculate the min, mean, median, and max PTV distances an roi based on data in the SQL DB.
    :param study_instance_uid: uid as specified in SQL DB
    :param roi_name: roi_name as specified in SQL DB
    """

    oar_coordinates_string = DVH_SQL().query('dvhs',
                                             'roi_coord_string',
                                             "study_instance_uid = '%s' and roi_name = '%s'"
                                             % (study_instance_uid, roi_name))

    ptv_coordinates_strings = DVH_SQL().query('dvhs',
                                              'roi_coord_string',
                                              "study_instance_uid = '%s' and roi_type like 'PTV%%'"
                                              % study_instance_uid)

    if ptv_coordinates_strings:

        oar_coordinates = roi_tools.get_roi_coordinates_from_string(oar_coordinates_string[0][0])

        ptvs = [roi_tools.get_planes_from_string(ptv[0]) for ptv in ptv_coordinates_strings]
        tv_coordinates = roi_tools.get_roi_coordinates_from_planes(roi_tools.get_union(ptvs))

        try:
            min_distances = roi_tools.get_min_distances_to_target(oar_coordinates, tv_coordinates)
            dth = calc_dth(min_distances)
            dth_string = ','.join(['%.3f' % num for num in dth])

            DVH_SQL().update('dvhs',
                             'dist_to_ptv_min',
                             round(float(np.min(min_distances)), 2),
                             "study_instance_uid = '%s' and roi_name = '%s'"
                             % (study_instance_uid, roi_name))

            DVH_SQL().update('dvhs',
                             'dist_to_ptv_mean',
                             round(float(np.mean(min_distances)), 2),
                             "study_instance_uid = '%s' and roi_name = '%s'"
                             % (study_instance_uid, roi_name))

            DVH_SQL().update('dvhs',
                             'dist_to_ptv_median',
                             round(float(np.median(min_distances)), 2),
                             "study_instance_uid = '%s' and roi_name = '%s'"
                             % (study_instance_uid, roi_name))

            DVH_SQL().update('dvhs',
                             'dist_to_ptv_max',
                             round(float(np.max(min_distances)), 2),
                             "study_instance_uid = '%s' and roi_name = '%s'"
                             % (study_instance_uid, roi_name))

            DVH_SQL().update('dvhs',
                             'dth_string',
                             dth_string,
                             "study_instance_uid = '%s' and roi_name = '%s'"
                             % (study_instance_uid, roi_name))
        except:
            print('dist_to_ptv calculation failure, skipping')


def update_treatment_volume_overlap_in_db(study_instance_uid, roi_name):
    """
    This function will recalculate the PTV overlap of an roi based on data in the SQL DB.
    :param study_instance_uid: uid as specified in SQL DB
    :param roi_name: roi_name as specified in SQL DB
    """

    oar_coordinates_string = DVH_SQL().query('dvhs',
                                             'roi_coord_string',
                                             "study_instance_uid = '%s' and roi_name = '%s'"
                                             % (study_instance_uid, roi_name))

    ptv_coordinates_strings = DVH_SQL().query('dvhs',
                                              'roi_coord_string',
                                              "study_instance_uid = '%s' and roi_type like 'PTV%%'"
                                              % study_instance_uid)

    if ptv_coordinates_strings:
        oar = roi_tools.get_planes_from_string(oar_coordinates_string[0][0])

        ptvs = [roi_tools.get_planes_from_string(ptv[0]) for ptv in ptv_coordinates_strings]

        tv = roi_tools.get_union(ptvs)
        overlap = roi_tools.calc_roi_overlap(oar, tv)

        DVH_SQL().update('dvhs',
                         'ptv_overlap',
                         round(float(overlap), 2),
                         "study_instance_uid = '%s' and roi_name = '%s'"
                         % (study_instance_uid, roi_name))


def update_dist_to_ptv_centroids_in_db(study_instance_uid, roi_name):
    """
    This function will recalculate the OARtoPTV centroid distance based on data in the SQL DB.
    :param study_instance_uid: uid as specified in SQL DB
    :param roi_name: roi_name as specified in SQL DB
    """

    oar_centroid_string = DVH_SQL().query('dvhs',
                                          'centroid',
                                          "study_instance_uid = '%s' and roi_name = '%s'"
                                          % (study_instance_uid, roi_name))
    oar_centroid = np.array([float(i) for i in oar_centroid_string[0][0].split(',')])

    ptv_coordinates_strings = DVH_SQL().query('dvhs',
                                              'roi_coord_string',
                                              "study_instance_uid = '%s' and roi_type like 'PTV%%'"
                                              % study_instance_uid)

    if ptv_coordinates_strings:

        ptvs = [roi_tools.get_planes_from_string(ptv[0]) for ptv in ptv_coordinates_strings]
        tv = roi_tools.get_union(ptvs)
        ptv_centroid = np.array(roi_tools.calc_centroid(tv))

        dist_to_ptv_centroids = float(np.linalg.norm(ptv_centroid - oar_centroid)) / 10.

        DVH_SQL().update('dvhs',
                         'dist_to_ptv_centroids',
                         round(dist_to_ptv_centroids, 3),
                         "study_instance_uid = '%s' and roi_name = '%s'"
                         % (study_instance_uid, roi_name))


def update_volumes_in_db(study_instance_uid, roi_name):
    """
    This function will recalculate the volume of an roi based on data in the SQL DB.
    :param study_instance_uid: uid as specified in SQL DB
    :param roi_name: roi_name as specified in SQL DB
    """

    coordinates_string = DVH_SQL().query('dvhs',
                                         'roi_coord_string',
                                         "study_instance_uid = '%s' and roi_name = '%s'"
                                         % (study_instance_uid, roi_name))

    roi = roi_tools.get_planes_from_string(coordinates_string[0][0])

    volume = roi_tools.calc_volume(roi)

    DVH_SQL().update('dvhs',
                     'volume',
                     round(float(volume), 2),
                     "study_instance_uid = '%s' and roi_name = '%s'"
                     % (study_instance_uid, roi_name))


def update_surface_area_in_db(study_instance_uid, roi_name):
    """
    This function will recalculate the surface area of an roi based on data in the SQL DB.
    :param study_instance_uid: uid as specified in SQL DB
    :param roi_name: roi_name as specified in SQL DB
    """

    coordinates_string = DVH_SQL().query('dvhs',
                                         'roi_coord_string',
                                         "study_instance_uid = '%s' and roi_name = '%s'"
                                         % (study_instance_uid, roi_name))

    roi = roi_tools.get_planes_from_string(coordinates_string[0][0])

    surface_area = roi_tools.surface_area_of_roi(roi, coord_type="sets_of_points")

    DVH_SQL().update('dvhs',
                     'surface_area',
                     round(float(surface_area), 2),
                     "study_instance_uid = '%s' and roi_name = '%s'"
                     % (study_instance_uid, roi_name))


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


def flatten_list_of_lists(some_list):
    return [item for sublist in some_list for item in sublist]


def save_options(options):
    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/options"
    abs_file_path = os.path.join(script_dir, rel_path)

    out_options = {}
    for i in options.__dict__:
        if not i.startswith('_'):
            out_options[i] = getattr(options, i)

    outfile = open(abs_file_path, 'wb')
    pickle.dump(out_options, outfile)
    outfile.close()


class Object():
    pass


def load_options(options):
    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/options"
    abs_file_path = os.path.join(script_dir, rel_path)

    if os.path.isfile(abs_file_path):

        infile = open(abs_file_path, 'rb')
        new_dict = pickle.load(infile)

        new_options = Object()
        for key, value in listitems(new_dict):
            setattr(new_options, key, value)

        infile.close()

        return new_options
    else:
        return options
