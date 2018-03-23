#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Input an rt_plan from pydicom into the Plan class to parse MLC data
Created on Wed, Feb 28 2018
@author: Dan Cutright, PhD
"""

import numpy as np
from shapely.geometry import Polygon

MAX_FIELD_SIZE_X = 400  # in mm
MAX_FIELD_SIZE_Y = 400  # in mm


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
                lb = bld_seq.LeafPositionBoundaries
                lb.sort(reverse=True)  # Ensure descending order, not sure if a mlcy defaults to that in DICOM
                self.leaf_boundaries = lb

        self.aperture_shape = [get_shapely_from_cp(self.leaf_boundaries, cp) for cp in self.control_point]

        self.control_point_meter_set = np.append([0], np.diff(np.array([cp.cum_mu for cp in self.control_point])))

        self.name = beam_seq.BeamDescription

        self.aperture_x = []
        self.aperture_y = []
        for ap in self.aperture_shape:
            x, y = [], []
            if ap.geom_type in {'MultiPolygon'}:
                for shape in ap:
                    x.append(shape.exterior.coords.xy[0].tolist())
                    y.append(shape.exterior.coords.xy[1].tolist())
            else:
                x.append(ap.exterior.coords.xy[0].tolist())
                y.append(ap.exterior.coords.xy[1].tolist())

            self.aperture_x.append(x)
            self.aperture_y.append(y)


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
    lb = leaf_boundaries  # NOTE: this is in DESCENDING order
    cp = control_point

    # Determine jaw opening
    if hasattr(cp, 'asymy'):
        y_min = min(cp.asymy)
        y_max = max(cp.asymy)
    else:
        y_min = np.float(-MAX_FIELD_SIZE_Y / 2)
        y_max = np.float(MAX_FIELD_SIZE_Y / 2)
    if hasattr(cp, 'asymx'):
        x_min = min(cp.asymx)
        x_max = max(cp.asymx)
    else:
        x_min = np.float(-MAX_FIELD_SIZE_X / 2)
        x_max = np.float(MAX_FIELD_SIZE_X / 2)

    # Get mlc positions and start/end indices based on jaws
    if hasattr(cp, 'mlcx'):
        mlc = cp.mlcx
        order = 1
    elif hasattr(cp, 'mlcy'):
        mlc = cp.mlcy
        order = -1
    else:
        return False

    v_max = [x_max, y_max][int((order+1)/2)]
    v_min = [x_min, y_min][int((order+1)/2)]

    # These indices are selected to ignore MLCs under the jaws
    # Needs validation, definitely lb_end_index is not tight enough
    lb_start_index = int(np.argmax(lb < v_max)) - 1
    lb_end_index = int(np.argmax(lb < v_min)) - 1

    # Get list of points defining MLC open area
    # To avoid using the intersection function for MLC and Jaw openings
    points = []

    # Accumulate points representing top and bottom positions of A side MLCs
    # First MLC may be split by Jaw
    points.append((mlc[0][lb_start_index], v_max)[::order])
    points.append((mlc[0][lb_start_index], lb[lb_start_index + 1])[::order])
    # The MLCs excluding first and last
    for i in range(lb_start_index+1, lb_end_index):
        points.append((mlc[0][i], lb[i])[::order])
        points.append((mlc[0][i], lb[i+1])[::order])
    # Last MLC may be split by Jaw
    points.append((mlc[0][lb_end_index], lb[lb_end_index])[::order])
    points.append((mlc[0][lb_end_index], v_min)[::order])

    # Accumulate points representing top and bottom positions of B side MLCs, in reverse order
    points.append((mlc[1][lb_end_index], v_min)[::order])
    points.append((mlc[1][lb_end_index], lb[lb_end_index])[::order])
    for i in range(lb_start_index+1, lb_end_index)[::-1]:
        points.append((mlc[1][i], lb[i+1])[::order])
        points.append((mlc[1][i], lb[i])[::order])
    points.append((mlc[1][lb_start_index], lb[lb_start_index + 1])[::order])
    points.append((mlc[1][lb_start_index], v_max)[::order])

    points.append(points[0])  # explicitly close polygon

    aperture = Polygon(points).buffer(0)  # may turn into MultiPolygon

    return aperture
