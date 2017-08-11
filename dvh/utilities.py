#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
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


class Temp_DICOM_FileSet:
    def __init__(self, **kwargs):

        # Read SQL configuration file
        script_dir = os.path.dirname(__file__)
        if 'start_path' in kwargs:
            rel_path = kwargs['start_path']
            abs_file_path = os.path.join(script_dir, rel_path)
            start_path = abs_file_path
        else:
            rel_path = "preferences/import_settings.txt"
            abs_file_path = os.path.join(script_dir, rel_path)
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
        mrns = []

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
        for key in rt_structures:
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

    cnx.cnx.close()


def datetime_str_to_obj(datetime_str):

    year = int(datetime_str[0:4])
    month = int(datetime_str[4:6])
    day = int(datetime_str[6:8])
    hour = int(datetime_str[8:10])
    minute = int(datetime_str[10:12])
    second = int(datetime_str[12:14])

    datetime_obj = datetime(year, month, day, hour, minute, second)

    return datetime_obj


def date_str_to_obj(date_str):

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

    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/import_settings.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    if os.path.isfile(abs_file_path):
        return True
    else:
        return False


def is_sql_connection_defined():

    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/sql_connection.cnf"
    abs_file_path = os.path.join(script_dir, rel_path)

    if os.path.isfile(abs_file_path):
        return True
    else:
        return False


def write_import_settings(directories):

    import_text = ['inbox ' + directories['inbox'],
                   'imported ' + directories['imported'],
                   'review ' + directories['review']]
    import_text = '\n'.join(import_text)

    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/import_settings.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "w") as text_file:
        text_file.write(import_text)


def write_sql_connection_settings(config):

    text = []
    for key, value in config.iteritems():
        if value:
            text.append(key + ' ' + value)
    text = '\n'.join(text)

    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/sql_connection.cnf"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "w") as text_file:
        text_file.write(text)


def validate_import_settings():
    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/import_settings.txt"
    abs_file_path = os.path.join(script_dir, rel_path)

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
    for key, value in config.iteritems():
        if not os.path.isdir(value):
            print('invalid', key, 'path:', value, sep=" ")
            valid = False

    return valid


def validate_sql_connection(*config, **kwargs):

    if config:
        try:
            cnx = DVH_SQL(config[0])
            cnx.close()
            valid = True
        except:
            valid = False
    else:
        try:
            cnx = DVH_SQL()
            cnx.close()
            valid = True
        except:
            valid = False

    if not kwargs or ('verbose' in kwargs and kwargs['verbose']):
        if valid:
            print("SQL DB is alive!")
        else:
            print("Connection to SQL DB could not be established.")
            if not is_sql_connection_defined():
                print("ERROR: SQL settings are not yet defined.  Please run:\n",
                      "    $ dvh settings --sql", sep="")

    return valid


def change_angle_origin(angles, max_positive_angle):
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
    contours = []
    for z in coord:
        for plane in coord[z]:
            points = [z]
            for point in plane['data']:
                points.append(str(round(point[0], 3)))
                points.append(str(round(point[1], 3)))
            contours.append(','.join(points))
    return ':'.join(contours)


def surface_area_of_roi(coord):

    """

    :param coord: dicompyler structure coordinates from GetStructureCoordinates()
    :return: surface_area in cm^2
    :rtype: float
    """
    surface_area = 0.
    all_z_values = [round(float(z), 1) for z in coord.keys()]
    all_z_values = np.sort(all_z_values)
    thicknesses = np.abs(np.diff(all_z_values))
    thicknesses = np.append(thicknesses, np.min(thicknesses))
    first_slice = min(all_z_values)
    final_slice = max(all_z_values)
    all_z_values = all_z_values.tolist()

    for z in coord:
        # z in coord will not necessarily go in order of z, convert z to float to lookup thickness
        # also used to check for top and bottom slices, to add area of those contours
        z_value = round(float(z), 1)
        thickness = thicknesses[all_z_values.index(round(float(z), 1))]

        previous_contour = []
        for plane in coord[z]:

            points = [(point[0], point[1]) for point in plane['data']]

            # if structure is a point or contains only 2 points, assume zero surface area
            if points and len(points) > 2:

                # Explicitly connect the final point to the first
                points.append(points[0])

                contour = Polygon(points)
                perimeter = contour.length
                surface_area += perimeter * thickness

                # Account for top and bottom surfaces
                if z_value in {first_slice, final_slice}:
                    # if current contour is contained within the previous contour, then current contour is a subtraction
                    # this is how DICOM handles ring structures
                    if previous_contour and not Point((points[0][0], points[0][1])).disjoint(previous_contour):
                        surface_area -= contour.area
                        previous_contour = []
                    else:
                        surface_area += contour.area
                        previous_contour = contour
            else:
                previous_contour = []

    return round(surface_area / 100., 2)


def points_to_shapely_polygon(sets_of_points):
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

    # oar and ptv are lists using str(z) as keys
    # each item is an ordered list of points representing a polygon
    # polygon n is inside polygon n-1, then the current accumulated polygon is
    #    polygon n subtracted from the accumulated polygon up to and including polygon n-1
    #    Same method DICOM uses to handle rings and islands

    intersection_volume = 0.
    all_z_values = [round(float(z), 2) for z in tv.keys()]
    all_z_values = np.sort(all_z_values)
    thicknesses = np.abs(np.diff(all_z_values))
    thicknesses = np.append(thicknesses, np.min(thicknesses))
    all_z_values = all_z_values.tolist()

    for z in tv.keys():
        # z in coord will not necessarily go in order of z, convert z to float to lookup thickness
        # also used to check for top and bottom slices, to add area of those contours

        if z in oar.keys():
            thickness = thicknesses[all_z_values.index(round(float(z), 2))]
            shapely_tv = points_to_shapely_polygon(tv[z])
            shapely_oar = points_to_shapely_polygon(oar[z])
            if shapely_oar and shapely_tv:
                intersection_volume += shapely_tv.intersection(shapely_oar).area * thickness

    return round(intersection_volume / 1000., 2)


def get_union(rois):

    new_roi = {}

    all_z_values = []
    for roi in rois:
        for z in roi.keys():
            if z not in all_z_values:
                all_z_values.append(z)

    for z in all_z_values:

        if z not in new_roi.keys():
            new_roi[z] = []

        current_slice = []
        for roi in rois:
            if z in roi.keys() and len(roi[z]) > 2:
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

    # oar and ptv are lists using str(z) as keys
    # each item is an ordered list of points representing a polygon
    # polygon n is inside polygon n-1, then the current accumulated polygon is
    #    polygon n subtracted from the accumulated polygon up to and including polygon n-1
    #    Same method DICOM uses to handle rings and islands

    volume = 0.
    all_z_values = [round(float(z), 2) for z in roi.keys()]
    all_z_values = np.sort(all_z_values)
    thicknesses = np.abs(np.diff(all_z_values))
    thicknesses = np.append(thicknesses, np.min(thicknesses))
    all_z_values = all_z_values.tolist()

    for z in roi.keys():
        # z in coord will not necessarily go in order of z, convert z to float to lookup thickness
        # also used to check for top and bottom slices, to add area of those contours

        thickness = thicknesses[all_z_values.index(round(float(z), 2))]
        shapely_roi = points_to_shapely_polygon(roi[z])
        if shapely_roi:
            volume += shapely_roi.area * thickness

    return round(volume / 1000., 2)


def get_roi_coordinates_from_string(roi_coord_string):
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
    roi_coordinates = []

    for z in planes.keys():
        for polygon in planes[z]:
            for point in polygon:
                roi_coordinates.append(np.array((point[0], point[1], point[2])))
    return roi_coordinates


def get_planes_from_string(roi_coord_string):
    planes = {}
    contours = roi_coord_string.split(':')

    for contour in contours:
        contour = contour.split(',')
        z = contour.pop(0)
        z = round(float(z), 2)
        z_str = str(z)

        if z_str not in planes.keys():
            planes[z_str] = []

        i, points = 0, []
        while i < len(contour):
            point = [float(contour[i]), float(contour[i+1]), z]
            points.append(point)
            i += 2
        planes[z_str].append(points)

    return planes


def get_min_distances_to_target(oar_coordinates, target_coordinates):
    # type: ([np.array], [np.array]) -> [float]
    """

    :param oar_coordinates: list of numpy arrays of 3D points defining the surface of the OAR
    :param target_coordinates: list of numpy arrays of 3D points defining the surface of the PTV
    :return: min_distances: list of numpy arrays of 3D points defining the surface of the OAR
    :rtype: [float]
    """
    min_distances = []
    print(oar_coordinates)
    print(target_coordinates)
    all_distances = cdist(oar_coordinates, target_coordinates, 'euclidean')
    for oar_point in all_distances:
        min_distances.append(float(np.min(oar_point)/10.))

    return min_distances


def update_min_distances_in_db(study_instance_uid, roi_name):

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

        ptvs = []
        for ptv in ptv_coordinates_strings:
            ptvs.append(get_planes_from_string(ptv[0]))
        tv_planes = get_union(ptvs)
        tv_coordinates = get_roi_coordinates_from_planes(tv_planes)

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
            pass


def update_treatment_volume_overlap_in_db(study_instance_uid, roi_name):

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

        ptvs = []
        for ptv in ptv_coordinates_strings:
            ptvs.append(get_planes_from_string(ptv[0]))

        tv = get_union(ptvs)
        overlap = calc_roi_overlap(oar, tv)

        DVH_SQL().update('dvhs',
                         'ptv_overlap',
                         round(float(overlap), 2),
                         "study_instance_uid = '%s' and roi_name = '%s'"
                         % (study_instance_uid, roi_name))


def update_volumes_in_db(study_instance_uid, roi_name):

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
