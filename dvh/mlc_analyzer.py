#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Input an rt_plan file path into the Plan class to parse MLC data and calculate metrics
Created on Wed, Feb 28 2018
@author: Dan Cutright, PhD
"""

from dicompylercore import dicomparser
import numpy as np
from shapely.geometry import Polygon
from utilities import flatten_list_of_lists as flatten
from options import MAX_FIELD_SIZE_X, MAX_FIELD_SIZE_Y, COMPLEXITY_SCORE_X_WEIGHT, COMPLEXITY_SCORE_Y_WEIGHT


class Plan:
    def __init__(self, rt_plan_file):
        """
        :param rt_plan_file: absolute file path of an rt_plan_file)
        """
        rt_plan = dicomparser.read_file(rt_plan_file)
        self.fx_group = [FxGroup(fx_grp_seq, rt_plan.BeamSequence) for fx_grp_seq in rt_plan.FractionGroupSequence]
        self.name = rt_plan.RTPlanLabel


class FxGroup:
    def __init__(self, fx_grp_seq, plan_beam_sequences):
        self.fxs = fx_grp_seq.NumberOfFractionsPlanned

        meter_set = {}
        for ref_beam in fx_grp_seq.ReferencedBeamSequence:
            ref_beam_num = str(ref_beam.ReferencedBeamNumber)
            meter_set[ref_beam_num] = float(ref_beam.BeamMeterset)

        self.beam = []
        for beam_seq in plan_beam_sequences:
            beam_num = str(beam_seq.BeamNumber)
            if beam_num in meter_set:
                self.beam.append(Beam(beam_seq, meter_set[beam_num]))
        self.beam_count = len(self.beam)
        self.beam_names = [b.name for b in self.beam]


class Beam:
    def __init__(self, beam_seq, meter_set):

        cp_seq = beam_seq.ControlPointSequence
        self.control_point = [ControlPoint(cp) for cp in cp_seq]
        self.control_point_count = len(self.control_point)

        for bld_seq in beam_seq.BeamLimitingDeviceSequence:
            if hasattr(bld_seq, 'LeafPositionBoundaries'):
                self.leaf_boundaries = bld_seq.LeafPositionBoundaries

        self.jaws = [get_jaws(cp) for cp in self.control_point]
        self.aperture = [get_shapely_from_cp(self.leaf_boundaries, cp) for cp in self.control_point]
        self.mlc_borders = [get_mlc_borders(cp, self.leaf_boundaries) for cp in self.control_point]

        self.gantry_angle = [float(cp.GantryAngle) for cp in cp_seq if hasattr(cp, 'GantryAngle')]
        self.collimator_angle = [float(cp.BeamLimitingDeviceAngle) for cp in cp_seq if hasattr(cp, 'BeamLimitingDeviceAngle')]
        self.couch_angle = [float(cp.PatientSupportAngle) for cp in cp_seq if hasattr(cp, 'PatientSupportAngle')]

        self.meter_set = meter_set
        self.control_point_meter_set = np.append([0], np.diff(np.array([cp.cum_mu for cp in self.control_point])))

        if hasattr(beam_seq, 'BeamDescription'):
            self.name = beam_seq.BeamDescription
        else:
            self.name = beam_seq.BeamName

        cum_mu = [cp.cum_mu * self.meter_set for cp in self.control_point]
        cp_mu = np.diff(np.array(cum_mu)).tolist() + [0]
        x_paths = np.array([get_xy_path_lengths(cp)[0] for cp in self.aperture])
        y_paths = np.array([get_xy_path_lengths(cp)[1] for cp in self.aperture])
        area = [cp.area for cp in self.aperture]
        c1, c2 = COMPLEXITY_SCORE_X_WEIGHT, COMPLEXITY_SCORE_Y_WEIGHT
        complexity_scores = np.divide(np.multiply(np.add(c1*x_paths, c2*y_paths), cp_mu), area)
        # Complexity score based on:
        # Younge KC, Matuszak MM, Moran JM, McShan DL, Fraass BA, Roberts DA. Penalization of aperture
        # complexity in inversely planned volumetric modulated arc therapy. Med Phys. 2012;39(11):7160–70.

        self.summary = {'cp': range(1, len(self.control_point)+1),
                        'cum_mu_frac': [cp.cum_mu for cp in self.control_point],
                        'cum_mu': cum_mu,
                        'cp_mu': cp_mu,
                        'gantry': self.gantry_angle,
                        'collimator': self.collimator_angle,
                        'couch': self.couch_angle,
                        'jaw_x1': [j['x_min']/10 for j in self.jaws],
                        'jaw_x2': [j['x_max']/10 for j in self.jaws],
                        'jaw_y1': [j['y_min']/10 for j in self.jaws],
                        'jaw_y2': [j['y_max']/10 for j in self.jaws],
                        'area': np.divide(area, 100.).tolist(),
                        'x_perim': np.divide(x_paths, 10.).tolist(),
                        'y_perim': np.divide(y_paths, 10.).tolist(),
                        'cmp_score': complexity_scores.tolist()}

        for key in self.summary:
            if len(self.summary[key]) == 1:
                self.summary[key] = self.summary[key] * len(self.summary['cp'])


class ControlPoint:
    def __init__(self, cp_seq):
        cp = {'cum_mu': float(cp_seq.CumulativeMetersetWeight)}
        for device_position_seq in cp_seq.BeamLimitingDevicePositionSequence:
            leaf_jaw_type = str(device_position_seq.RTBeamLimitingDeviceType).lower()
            if leaf_jaw_type.startswith('mlc'):
                cp['leaf_type'] = leaf_jaw_type
                leaf_jaw_type = 'mlc'

            positions = np.array(map(float, device_position_seq.LeafJawPositions))

            pos_count = len(positions)
            cp[leaf_jaw_type] = [positions[0:pos_count / 2],
                                 positions[pos_count / 2:pos_count]]

        if 'leaf_type' not in list(cp):
            cp['leaf_type'] = False

        for key in cp:
            setattr(self, key, cp[key])


def get_mlc_borders(control_point, leaf_boundaries):
    """
    This function returns the boundaries of each MLC leaf for purposes of displaying a beam's eye view using
    bokeh's quad() glyph
    :param control_point: a ControlPoint class object
    :param leaf_boundaries: the leaf boundaries as stored in the Beam class object
    :return: the boundaries of each leaf within the control point
    """
    top = leaf_boundaries[0:-1] + leaf_boundaries[0:-1]
    top = [float(i) for i in top]
    bottom = leaf_boundaries[1::] + leaf_boundaries[1::]
    bottom = [float(i) for i in bottom]
    left = [- MAX_FIELD_SIZE_X / 2] * len(control_point.mlc[0])
    left.extend(control_point.mlc[1])
    right = control_point.mlc[0].tolist()
    right.extend([MAX_FIELD_SIZE_X / 2] * len(control_point.mlc[1]))

    return {'top': top,
            'bottom': bottom,
            'left': left,
            'right': right}


def get_shapely_from_cp(leaf_boundaries, control_point):
    """
    This function will return the outline of MLCs within jaws
    :param leaf_boundaries: an ordered list of leaf boundaries
    :param control_point: a ControlPoint class object
    :return: a shapely object of the complete MLC aperture as one shape (including MLC overlap)
    """
    lb = leaf_boundaries
    mlc = control_point.mlc
    jaws = get_jaws(control_point)
    x_min, x_max = jaws['x_min'], jaws['x_max']
    y_min, y_max = jaws['y_min'], jaws['y_max']

    jaw_points = [(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)]
    jaw_shapely = Polygon(jaw_points)

    if control_point.leaf_type == 'mlcx':
        a = flatten([[(m, lb[i]), (m, lb[i+1])] for i, m in enumerate(mlc[0])])
        b = flatten([[(m, lb[i]), (m, lb[i+1])] for i, m in enumerate(mlc[1])])
    elif control_point.leaf_type == 'mlcy':
        a = flatten([[(lb[i], m), (lb[i + 1], m)] for i, m in enumerate(mlc[0])])
        b = flatten([[(lb[i], m), (lb[i + 1], m)] for i, m in enumerate(mlc[1])])
    else:
        return jaw_shapely

    mlc_points = a + b[::-1]  # concatenate a and reverse(b)
    mlc_aperture = Polygon(mlc_points).buffer(0)

    aperture = mlc_aperture.intersection(jaw_shapely)

    return aperture


def get_jaws(control_point):
    """
    :param control_point: a ControlPoint class object
    :return: jaw positions (or max field size in lieu of a jaw)
    :rtype: dict
    """

    cp = control_point

    # Determine jaw opening
    if hasattr(cp, 'asymy'):
        y_min = min(cp.asymy)
        y_max = max(cp.asymy)
    else:
        y_min = -MAX_FIELD_SIZE_Y / 2.
        y_max = MAX_FIELD_SIZE_Y / 2.
    if hasattr(cp, 'asymx'):
        x_min = min(cp.asymx)
        x_max = max(cp.asymx)
    else:
        x_min = -MAX_FIELD_SIZE_X / 2.
        x_max = MAX_FIELD_SIZE_X / 2.

    jaws = {'x_min': float(x_min),
            'x_max': float(x_max),
            'y_min': float(y_min),
            'y_max': float(y_max)}

    return jaws


def get_xy_path_lengths(shapely_object):
    """
    :param shapely_object: either 'GeometryCollection', 'MultiPolygon', or 'Polygon'
    :return: pathl engths in the x and y directions
    :rtype: list
    """
    path = np.array([0., 0.])
    if shapely_object.type == 'GeometryCollection':
        for geometry in shapely_object.geoms:
            if geometry.type in {'MultiPolygon', 'Polygon'}:
                path = np.add(path, get_xy_path_lengths(geometry))
    elif shapely_object.type == 'MultiPolygon':
        for shape in shapely_object:
            path = np.add(path, get_xy_path_lengths(shape))
    elif shapely_object.type == 'Polygon':
        x, y = np.array(shapely_object.exterior.xy[0]), np.array(shapely_object.exterior.xy[1])
        path = np.array([np.sum(np.abs(np.diff(x))), np.sum(np.abs(np.diff(y)))])

    return path.tolist()

