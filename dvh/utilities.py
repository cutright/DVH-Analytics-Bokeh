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
import dicom
import sys
from shapely.geometry import Polygon, Point
import numpy as np
from scipy.spatial.distance import cdist


SCRIPT_DIR = os.path.dirname(__file__)
PREFERENCE_PATHS = {''}
MIN_SLICE_THICKNESS = 2  # Update method to pull from DICOM


class Temp_DICOM_FileSet:
    def __init__(self, start_path=None):

        # Read SQL configuration file
        if start_path:
            abs_file_path = os.path.join(SCRIPT_DIR, start_path)
            start_path = abs_file_path
        else:
            start_path = "preferences/import_settings.txt"
            abs_file_path = os.path.join(SCRIPT_DIR, start_path)
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

        for x in range(0, len(f)):
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

        for a in range(0, self.count):
            self.plan.append(plan_files[a])
            self.mrn.append(dicom.read_file(plan_files[a]).PatientID)
            self.study_instance_uid.append(dicom.read_file(plan_files[a]).StudyInstanceUID)
            for b in range(0, len(structure_files)):
                if study_uid_plan[a] == study_uid_structure[b]:
                    self.structure.append(structure_files[b])
            for c in range(0, len(dose_files)):
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


def recalculate_ages(*custom_condition):

    if custom_condition:
        custom_condition = " AND " + custom_condition[0]
    else:
        custom_condition = ''

    dvh_data = QuerySQL('Plans', "mrn != ''" + custom_condition)
    cnx = DVH_SQL()

    for i in range(0, len(dvh_data.mrn)):
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
    for i in range(0, len(beam_data.study_instance_uid)):
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
    """
    Checks if import_settings.txt exists
    :rtype: bool
    """

    rel_path = "preferences/import_settings.txt"
    abs_file_path = os.path.join(SCRIPT_DIR, rel_path)

    if os.path.isfile(abs_file_path):
        return True
    else:
        return False


def is_sql_connection_defined():
    """
    Checks if sql_connection.cnf exists
    :rtype: bool
    """

    rel_path = "preferences/sql_connection.cnf"
    abs_file_path = os.path.join(SCRIPT_DIR, rel_path)

    if os.path.isfile(abs_file_path):
        return True
    else:
        return False


def write_import_settings(directories):

    import_text = ['inbox ' + directories['inbox'],
                   'imported ' + directories['imported'],
                   'review ' + directories['review']]
    import_text = '\n'.join(import_text)

    rel_path = "preferences/import_settings.txt"
    abs_file_path = os.path.join(SCRIPT_DIR, rel_path)

    with open(abs_file_path, "w") as text_file:
        text_file.write(import_text)


def write_sql_connection_settings(config):

    text = ["%s %s" % (key, value) for key, value in listitems(config) if value]
    text = '\n'.join(text)

    rel_path = "preferences/sql_connection.cnf"
    abs_file_path = os.path.join(SCRIPT_DIR, rel_path)

    with open(abs_file_path, "w") as text_file:
        text_file.write(text)


def validate_import_settings():
    rel_path = "preferences/import_settings.txt"
    abs_file_path = os.path.join(SCRIPT_DIR, rel_path)

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
    :param verbose: boolean indicating if cmd line printing should be performed
    :param config:
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


def dicompyler_roi_coord_to_db_string(coord):
    """
    :param coord: dicompyler structure coordinates from GetStructureCoordinates()
    :return: string representation of roi, <z1>: <x1 y1 x2 y2... xn yn>, <zn>: <x1 y1 x2 y2... xn yn>
    :rtype: str
    """
    contours = []
    for z in coord:
        for plane in coord[z]:
            points = [z]
            for point in plane['data']:
                points.append(str(round(point[0], 3)))
                points.append(str(round(point[1], 3)))
            contours.append(','.join(points))
    return ':'.join(contours)


def surface_area_of_roi(coord, coord_type='dicompyler'):
    """
    :param coord: dicompyler structure coordinates from GetStructureCoordinates() or sets_of_points
    :param coord_type: either 'dicompyler' or 'sets_of_points'
    :return: surface_area in cm^2
    :rtype: float
    """

    if coord_type == "sets_of_points":
        sets_of_points = coord
    else:
        sets_of_points = dicompyler_roi_to_sets_of_points(coord)

    shapely_roi = get_shapely_from_sets_of_points(sets_of_points)

    slice_count = len(shapely_roi['z'])

    area = 0.
    polygon = shapely_roi['polygon']
    z = shapely_roi['z']
    thickness = min(shapely_roi['thickness'])

    for i in range(0, slice_count):
        for j in [-1, 1]:  # -1 for bottom area and 1 for top area
            # ensure bottom of first slice and top of last slice are fully added
            # if prev/next slice is not adjacent, assume non-contiguous ROI
            if (i == 0 and j == -1) or (i == slice_count-1 and j == 1) or abs(z[i] - z[i+j]) > 2*thickness:
                area += polygon[i].area
            else:
                area += polygon[i].difference(polygon[i+j]).area

        area += polygon[i].length * thickness

    return round(area/100, 3)


def get_shapely_from_sets_of_points(sets_of_points):
    """
    :param sets_of_points: a dictionary of slices with key being a str representation of z value, value is a list
    of points defining a polygon in the slice.  point[0] is x and point[1] is y
    :return: roi_slice which is a dictionary of lists of z, thickness, and a Shapely Polygon class object
    :rtype: list
    """

    roi_slice = {'z': [], 'thickness': [], 'polygon': []}

    sets_of_points_keys = list(sets_of_points)
    sets_of_points_keys.sort()

    all_z_values = [round(float(z), 2) for z in sets_of_points_keys]
    thicknesses = np.abs(np.diff(all_z_values))
    if len(thicknesses):
        thicknesses = np.append(thicknesses, np.min(thicknesses))
    else:
        thicknesses = np.array([MIN_SLICE_THICKNESS])

    for z in sets_of_points:
        thickness = thicknesses[all_z_values.index(round(float(z), 2))]
        shapely_roi = points_to_shapely_polygon(sets_of_points[z])
        if shapely_roi:
            roi_slice['z'].append(round(float(z), 2))
            roi_slice['thickness'].append(thickness)
            roi_slice['polygon'].append(shapely_roi)

    return roi_slice


def dicompyler_roi_to_sets_of_points(coord):
    """
    :param coord: dicompyler structure coordinates from GetStructureCoordinates()
    :return: a dictionary of lists of points that define contours in each slice z
    :rtype: dict
    """
    all_points = {}
    for z in coord:
        all_points[z] = []
        for plane in coord[z]:
            plane_points = [[float(point[0]), float(point[1])] for point in plane['data']]
            for point in plane['data']:
                plane_points.append([float(point[0]), float(point[1])])
            if len(plane_points) > 2:
                all_points[z].append(plane_points)
    return all_points


def points_to_shapely_polygon(sets_of_points):
    """
    :param sets_of_points: sets of points is a dictionary of lists using str(z) as keys
    :return: a composite polygon as a shapely object (eith polygon or multipolygon)
    """
    # sets of points are lists using str(z) as keys
    # each item is an ordered list of points representing a polygon, each point is a 3-item list [x, y, z]
    # polygon n is inside polygon n-1, then the current accumulated polygon is
    #    polygon n subtracted from the accumulated polygon up to and including polygon n-1
    #    Same method DICOM uses to handle rings and islands

    composite_polygon = []
    for set_of_points in sets_of_points:
        if len(set_of_points) > 3:
            points = [(point[0], point[1]) for point in set_of_points]
            points.append(points[0])  # Explicitly connect the final point to the first

            # if there are multiple sets of points in a slice, each set is a polygon,
            # interior polygons are subtractions, exterior are addition
            # Only need to check one point for interior vs exterior
            current_polygon = Polygon(points).buffer(0)  # clean stray points
            if composite_polygon:
                if Point((points[0][0], points[0][1])).disjoint(composite_polygon):
                    composite_polygon = composite_polygon.union(current_polygon)
                else:
                    composite_polygon = composite_polygon.symmetric_difference(current_polygon)
            else:
                composite_polygon = current_polygon

    return composite_polygon


def calc_roi_overlap(oar, tv):
    """
    :param oar: dict representing organ-at-risk, follows format of "sets of points" in dicompyler_roi_to_sets_of_points
    :param tv: dict representing tumor volume
    :return: volume of overlap between ROIs
    :rtype: float
    """

    intersection_volume = 0.
    all_z_values = [round(float(z), 2) for z in list(tv)]
    all_z_values = np.sort(all_z_values)
    thicknesses = np.abs(np.diff(all_z_values))
    thicknesses = np.append(thicknesses, np.min(thicknesses))
    all_z_values = all_z_values.tolist()

    for z in list(tv):
        # z in coord will not necessarily go in order of z, convert z to float to lookup thickness
        # also used to check for top and bottom slices, to add area of those contours

        if z in list(oar):
            thickness = thicknesses[all_z_values.index(round(float(z), 2))]
            shapely_tv = points_to_shapely_polygon(tv[z])
            shapely_oar = points_to_shapely_polygon(oar[z])
            if shapely_oar and shapely_tv:
                intersection_volume += shapely_tv.intersection(shapely_oar).area * thickness

    return round(intersection_volume / 1000., 2)


def get_union(rois):
    """
    :param rois: a list of "sets of points"
    :return: a "sets of points" representing the union of the rois, each item in "sets of points" is a plane
    :rtype: list
    """

    new_roi = {}

    all_z_values = []
    for roi in rois:
        for z in list(roi):
            if z not in all_z_values:
                all_z_values.append(z)

    for z in all_z_values:

        if z not in list(new_roi):
            new_roi[z] = []

        current_slice = []
        for roi in rois:
            # Make sure current roi has at least 3 points in z plane
            if z in list(roi) and len(roi[z][0]) > 2:
                if not current_slice:
                    current_slice = points_to_shapely_polygon(roi[z])
                else:
                    current_slice = current_slice.union(points_to_shapely_polygon(roi[z]))

        if current_slice:
            if current_slice.type != 'MultiPolygon':
                current_slice = [current_slice]

            for polygon in current_slice:
                xy = polygon.exterior.xy
                x_coord, y_coord = xy[0], xy[1]
                points = []
                for i in range(0, len(x_coord)):
                    points.append([x_coord[i], y_coord[i], round(float(z), 2)])
                new_roi[z].append(points)

                if hasattr(polygon, 'interiors'):
                    for interior in polygon.interiors:
                        xy = interior.coords.xy
                        x_coord, y_coord = xy[0], xy[1]
                        points = []
                        for i in range(0, len(x_coord)):
                            points.append([x_coord[i], y_coord[i], round(float(z), 2)])
                        new_roi[z].append(points)
        else:
            print('WARNING: no contour found for slice %s' % z)

    return new_roi


def calc_volume(roi):
    """
    :param roi: a "sets of points" formatted list
    :return: volume in cm^3 of roi
    :rtype: float
    """

    # oar and ptv are lists using str(z) as keys
    # each item is an ordered list of points representing a polygon
    # polygon n is inside polygon n-1, then the current accumulated polygon is
    #    polygon n subtracted from the accumulated polygon up to and including polygon n-1
    #    Same method DICOM uses to handle rings and islands

    volume = 0.
    all_z_values = [round(float(z), 2) for z in list(roi)]
    all_z_values = np.sort(all_z_values)
    thicknesses = np.abs(np.diff(all_z_values))
    thicknesses = np.append(thicknesses, np.min(thicknesses))
    all_z_values = all_z_values.tolist()

    for z in list(roi):
        # z in coord will not necessarily go in order of z, convert z to float to lookup thickness
        # also used to check for top and bottom slices, to add area of those contours

        thickness = thicknesses[all_z_values.index(round(float(z), 2))]
        shapely_roi = points_to_shapely_polygon(roi[z])
        if shapely_roi:
            volume += shapely_roi.area * thickness

    return round(volume / 1000., 2)


def get_roi_coordinates_from_string(roi_coord_string):
    """
    :param roi_coord_string: the string reprentation of an roi in the SQL database
    :return: a list of numpy arrays, each array is the x, y, z coordinates of the given point
    :rtype: list
    """
    roi_coordinates = []
    contours = roi_coord_string.split(':')

    for contour in contours:
        contour = contour.split(',')
        z = contour.pop(0)
        z = float(z)
        i = 0
        while i < len(contour):
            roi_coordinates.append(np.array((float(contour[i]), float(contour[i + 1]), z)))
            i += 2

    return roi_coordinates


def get_roi_coordinates_from_planes(planes):
    """
    :param planes: a "sets of points" formatted list
    :return: a list of numpy arrays, each array is the x, y, z coordinates of the given point
    :rtype: list
    """
    roi_coordinates = []

    for z in list(planes):
        for polygon in planes[z]:
            for point in polygon:
                roi_coordinates.append(np.array((point[0], point[1], point[2])))
    return roi_coordinates


def get_planes_from_string(roi_coord_string):
    """
    :param roi_coord_string: roi string represntation of an roi as formatted in the SQL database
    :return: a "sets of points" formatted list
    :rtype: list
    """
    planes = {}
    contours = roi_coord_string.split(':')

    for contour in contours:
        contour = contour.split(',')
        z = contour.pop(0)
        z = round(float(z), 2)
        z_str = str(z)

        if z_str not in list(planes):
            planes[z_str] = []

        i, points = 0, []
        while i < len(contour):
            point = [float(contour[i]), float(contour[i+1]), z]
            points.append(point)
            i += 2
        planes[z_str].append(points)

    return planes


def get_min_distances_to_target(oar_coordinates, target_coordinates):
    """
    :param oar_coordinates: list of numpy arrays of 3D points defining the surface of the OAR
    :param target_coordinates: list of numpy arrays of 3D points defining the surface of the PTV
    :return: min_distances: list of numpy arrays of 3D points defining the surface of the OAR
    :rtype: [float]
    """
    min_distances = []
    all_distances = cdist(oar_coordinates, target_coordinates, 'euclidean')
    for oar_point in all_distances:
        min_distances.append(float(np.min(oar_point)/10.))

    return min_distances


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

        oar_coordinates = get_roi_coordinates_from_string(oar_coordinates_string[0][0])

        ptvs = [get_planes_from_string(ptv[0]) for ptv in ptv_coordinates_strings]
        tv_coordinates = get_roi_coordinates_from_planes(get_union(ptvs))

        try:
            min_distances = get_min_distances_to_target(oar_coordinates, tv_coordinates)

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
        oar = get_planes_from_string(oar_coordinates_string[0][0])

        ptvs = [get_planes_from_string(ptv[0]) for ptv in ptv_coordinates_strings]

        tv = get_union(ptvs)
        overlap = calc_roi_overlap(oar, tv)

        DVH_SQL().update('dvhs',
                         'ptv_overlap',
                         round(float(overlap), 2),
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

    roi = get_planes_from_string(coordinates_string[0][0])

    volume = calc_volume(roi)

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

    roi = get_planes_from_string(coordinates_string[0][0])

    surface_area = surface_area_of_roi(roi, coord_type="sets_of_points")

    DVH_SQL().update('dvhs',
                     'surface_area',
                     round(float(surface_area), 2),
                     "study_instance_uid = '%s' and roi_name = '%s'"
                     % (study_instance_uid, roi_name))


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
    x, y, w = xyw['x'], xyw['y'], xyw['w']
    cumsum, moving_aves = [0], []

    for i, y in enumerate(y, 1):
        cumsum.append(cumsum[i - 1] + y / w[i - 1])
        if i >= avg_len:
            moving_ave = (cumsum[i] - cumsum[i - avg_len]) / avg_len
            moving_aves.append(moving_ave)
    x_final = [x[i] for i in range(avg_len - 1, len(x))]

    return x_final, moving_aves


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


def get_study_instance_uids(**kwargs):
    uids = {}
    complete_list = []
    for key, value in listitems(kwargs):
        uids[key] = QuerySQL(key, value).study_instance_uid
        complete_list.extend(uids[key])

    uids['unique'] = list(set(complete_list))
    uids['union'] = [uid for uid in uids['unique'] if is_uid_in_all_keys(value, uids)]

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
