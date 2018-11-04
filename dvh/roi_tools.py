from shapely.geometry import Polygon, Point
from shapely import speedups
from scipy.spatial.distance import cdist


# Enable shapely calculations using C, as opposed to the C++ default
if speedups.available:
    speedups.enable()


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
                for i in range(len(x_coord)):
                    points.append([x_coord[i], y_coord[i], round(float(z), 2)])
                new_roi[z].append(points)

                if hasattr(polygon, 'interiors'):
                    for interior in polygon.interiors:
                        xy = interior.coords.xy
                        x_coord, y_coord = xy[0], xy[1]
                        points = []
                        for i in range(len(x_coord)):
                            points.append([x_coord[i], y_coord[i], round(float(z), 2)])
                        new_roi[z].append(points)
        else:
            print('WARNING: no contour found for slice %s' % z)

    return new_roi


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


def calc_cross_section(roi):
    """
    :param roi: a "sets of points" formatted list
    :return: max and median cross-sectional area of all slices in cm^2
    :rtype: list
    """
    areas = []

    for z in list(roi):
        shapely_roi = points_to_shapely_polygon(roi[z])
        if shapely_roi and shapely_roi.area > 0:
            slice_centroid = shapely_roi.centroid
            polygon_count = len(slice_centroid.xy[0])
            for i in range(polygon_count):
                if polygon_count > 1:
                    areas.append(shapely_roi[i].area)
                else:
                    areas.append(shapely_roi.area)

    areas = np.array(areas)

    area = {'max': float(np.max(areas) / 100.),
            'median': float(np.median(areas) / 100.)}

    return area


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

    for i in range(slice_count):
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


def calc_roi_overlap(oar, tv):
    """
    :param oar: dict representing organ-at-risk, follows format of "sets of points" in dicompyler_roi_to_sets_of_points
    :param tv: dict representing treatment volume
    :return: volume (cm^3) of overlap between ROIs
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


def calc_centroid(roi):
    """
    :param roi: a "sets of points" formatted list
    :return: centroid dicom coordinate in mm
    :rtype: list
    """
    centroids = {'x': [], 'y': [], 'z': [], 'area': []}

    for z in list(roi):
        shapely_roi = points_to_shapely_polygon(roi[z])
        if shapely_roi and shapely_roi.area > 0:
            slice_centroid = shapely_roi.centroid
            polygon_count = len(slice_centroid.xy[0])
            for i in range(polygon_count):
                centroids['x'].append(slice_centroid.xy[0][i])
                centroids['y'].append(slice_centroid.xy[1][i])
                centroids['z'].append(float(z))
                if polygon_count > 1:
                    centroids['area'].append(shapely_roi[i].area)
                else:
                    centroids['area'].append(shapely_roi.area)

    x = np.array(centroids['x'])
    y = np.array(centroids['y'])
    z = np.array(centroids['z'])
    w = np.array(centroids['area'])
    w_sum = np.sum(w)

    centroid = [float(np.sum(x * w) / w_sum),
                float(np.sum(y * w) / w_sum),
                float(np.sum(z * w) / w_sum)]

    return centroid
