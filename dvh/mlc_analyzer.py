#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Input an rt_plan from pydicom into the Plan class to parse MLC data
Created on Wed, Feb 28 2018
@author: Dan Cutright, PhD
"""

import numpy as np
from shapely.geometry import Polygon
from utilities import flatten_list_of_lists as flatten
from options import MAX_FIELD_SIZE_X, MAX_FIELD_SIZE_Y


class Plan:
    def __init__(self, rt_plan):
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

        self.meter_set = meter_set

        self.control_point = [ControlPoint(cp_seq) for cp_seq in beam_seq.ControlPointSequence]
        self.control_point_count = len(self.control_point)

        for bld_seq in beam_seq.BeamLimitingDeviceSequence:
            if hasattr(bld_seq, 'LeafPositionBoundaries'):
                self.leaf_boundaries = bld_seq.LeafPositionBoundaries

        self.mlc = [get_shapely_from_cp(self.leaf_boundaries, cp) for cp in self.control_point]
        self.jaws = [get_jaws(cp) for cp in self.control_point]

        self.control_point_meter_set = np.append([0], np.diff(np.array([cp.cum_mu for cp in self.control_point])))

        self.name = beam_seq.BeamDescription

        self.aperture = [get_apertures(self.leaf_boundaries, cp) for cp in self.control_point]


class ControlPoint:
    def __init__(self, cp_seq):
        cp = {'cum_mu': float(cp_seq.CumulativeMetersetWeight)}
        for device_position_seq in cp_seq.BeamLimitingDevicePositionSequence:
            leaf_jaw_type = str(device_position_seq.RTBeamLimitingDeviceType).lower()

            positions = np.array(map(float, device_position_seq.LeafJawPositions))

            pos_count = len(positions)
            cp[leaf_jaw_type] = [positions[0:pos_count / 2],
                                 positions[pos_count / 2:pos_count]]

        for key in cp:
            setattr(self, key, cp[key])


def get_shapely_from_cp(leaf_boundaries, control_point):
    """
    This function will return the outline of MLCs regardless of jaws
    :param leaf_boundaries: an ordered list of leaf boundaries
    :param control_point: a ControlPoint class object
    :return: a shapely Polygon of the complete MLC aperture as one shape (including MLC overlap)
    """
    lb = leaf_boundaries  # NOTE: this is in DESCENDING order
    cp = control_point

    # Get mlc positions and start/end indices based on jaws
    if hasattr(cp, 'mlcx'):
        mlc = cp.mlcx
    elif hasattr(cp, 'mlcy'):
        mlc = cp.mlcy
    else:
        return False

    a = flatten([[(m, lb[i]), (m, lb[i+1])] for i, m in enumerate(mlc[0])])
    b = flatten([[(m, lb[i]), (m, lb[i+1])] for i, m in enumerate(mlc[1])])
    points = a + b[::-1] + [a[0]]  # concatenate a and reverse(b), then explicitly close polygon

    aperture = Polygon(points)

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

    jaws = {'x_min': x_min,
            'x_max': x_max,
            'y_min': y_min,
            'y_max': y_max}

    return jaws


def get_apertures(leaf_boundaries, control_point):
    """
    It is significantly slower to calculate the union of the jaws and full MLC shape than it is to recalculate a new
    shape ignoring positions beyond the jaws.
    :param leaf_boundaries: an ordered list of leaf boundaries
    :param control_point: a ControlPoint class object
    :return: shapely MultiPolygon (or a [Polygon] so return is always iterable)
    """
    lb = leaf_boundaries  # NOTE: this is in DESCENDING order
    cp = control_point

    jaws = get_jaws(control_point)
    x_min, x_max = jaws['x_min'], jaws['x_max']
    y_min, y_max = jaws['y_min'], jaws['y_max']

    # Get mlc positions and start/end indices based on jaws
    if hasattr(cp, 'mlcx'):
        mlc = cp.mlcx
        v_min, v_max = y_min, y_max
    elif hasattr(cp, 'mlcy'):
        mlc = cp.mlcy
        v_min, v_max = x_min, x_max
    else:
        return False

    # These indices are selected to ignore MLCs under the jaws
    # Needs validation, definitely lb_end_index is not tight enough
    lb_start_index = int(np.argmax(lb < v_max)) - 1
    lb_end_index = int(np.argmax(lb < v_min)) - 1

    # Get list of points defining MLC open area
    # To avoid using the intersection function for MLC and Jaw openings
    points = []

    # Accumulate points representing top and bottom positions of A side MLCs
    # First MLC may be split by Jaw
    points.append((mlc[0][lb_start_index], v_max))
    points.append((mlc[0][lb_start_index], lb[lb_start_index + 1]))
    # The MLCs excluding first and last
    for i in range(lb_start_index + 1, lb_end_index):
        points.append((mlc[0][i], lb[i]))
        points.append((mlc[0][i], lb[i + 1]))
    # Last MLC may be split by Jaw
    points.append((mlc[0][lb_end_index], lb[lb_end_index]))
    points.append((mlc[0][lb_end_index], v_min))

    # Accumulate points representing top and bottom positions of B side MLCs, in reverse order
    points.append((mlc[1][lb_end_index], v_min))
    points.append((mlc[1][lb_end_index], lb[lb_end_index]))
    for i in range(lb_start_index + 1, lb_end_index)[::-1]:
        points.append((mlc[1][i], lb[i + 1]))
        points.append((mlc[1][i], lb[i]))
    points.append((mlc[1][lb_start_index], lb[lb_start_index + 1]))
    points.append((mlc[1][lb_start_index], v_max))

    points.append(points[0])  # explicitly close polygon

    aperture = Polygon(points).buffer(0)  # may turn into MultiPolygon

    # Ensure an iterable is returned for ease of code later
    if aperture.geom_type in {'MultiPolygon'}:
        return aperture
    else:
        return [aperture]
