#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))  # for abs imports to script path
from future.utils import listitems
from sql_to_python import QuerySQL
from sql_connector import DVH_SQL
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dicompylercore import dicomparser
import numpy as np
from get_settings import get_settings, parse_settings_file
import pickle
from math import ceil
from shapely import speedups
import roi_tools
try:
    import pydicom as dicom  # for pydicom >= 1.0
except:
    import dicom
from paths import APPS_DIR, APP_DIR, PREF_DIR, DATA_DIR, INBOX_DIR, IMPORTED_DIR, REVIEW_DIR, BACKUP_DIR
import types


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
    abs_file_path = os.path.join(PREF_DIR, 'options')

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
    abs_file_path = os.path.join(PREF_DIR, 'options')

    if os.path.isfile(abs_file_path):

        try:
            infile = open(abs_file_path, 'rb')
            new_dict = pickle.load(infile)

            new_options = Object()
            for key, value in listitems(new_dict):
                setattr(new_options, key, value)

            infile.close()

            return new_options
        except EOFError:
            print('Corrupt options file, loading defaults.')

    out_options = Object()
    for i in options.__dict__:
        if not i.startswith('_'):
            value = getattr(options, i)
            if not isinstance(value, types.ModuleType):  # ignore imports in options.py
                setattr(out_options, i, value)
    return out_options


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
    def __init__(self):

        # Read SQL configuration file
        abs_file_path = get_settings('import')

        with open(abs_file_path, 'r') as document:
            for line in document:
                line = line.split()
                if not line:
                    continue
                if line[0] == 'review' and len(line) > 1:
                    start_path = line[1:][0]

        self.plan = []
        self.structure = []
        self.dose = []
        self.mrn = []
        self.study_instance_uid = []

        f = []
        if start_path:
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


def get_csv(data_dict_list, data_dict_names, columns):

    text = []
    for s, data_dict in enumerate(data_dict_list):
        text.append(data_dict_names[s])
        text.append(','.join(columns))  # Column headers
        row_count = len(data_dict[columns[0]])
        for r in range(row_count):
            line = [str(data_dict[c][r]).replace(',', '^') for c in columns]
            text.append(','.join(line))
        text.append('')

    return '\n'.join(text)


def initialize_directories_settings():
    directories = [APPS_DIR, APP_DIR, PREF_DIR, DATA_DIR, INBOX_DIR, IMPORTED_DIR, REVIEW_DIR, BACKUP_DIR]
    for directory in directories:
        if not os.path.isdir(directory):
            os.mkdir(directory)


def load_sql_settings():
    if is_sql_connection_defined():
        config = parse_settings_file(get_settings('sql'))
        config = validate_config(config)

    else:
        config = {'host': 'localhost',
                  'port': '5432',
                  'dbname': 'dvh',
                  'user': '',
                  'password': ''}

    return config


def validate_config(config):
    if 'user' not in list(config):
        config['user'] = ''
        config['password'] = ''

    if 'password' not in list(config):
        config['password'] = ''

    return config


def load_directories():
    if is_import_settings_defined():
        return parse_settings_file(get_settings('import'))
    else:
        return {'inbox': INBOX_DIR,
                'imported': IMPORTED_DIR,
                'review': REVIEW_DIR}
