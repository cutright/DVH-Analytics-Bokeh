#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Input an rt_plan from pydicom into the Plan class to parse MLC data
Created on Wed, Feb 28 2018
@author: Dan Cutright, PhD
"""

import numpy as np
from shapely.geometry import Polygon

MAX_FIELD_SIZE_X = 40  # in cm
MAX_FIELD_SIZE_Y = 40  # in cm


class Plan:
    def __init__(self, rt_plan):
        self.fx_group = [FxGroup(fx_grp_seq, rt_plan) for fx_grp_seq in rt_plan.FractionGroupSequence]


class FxGroup:
    def __init__(self, fx_grp_seq, rt_plan):
        self.fxs = fx_grp_seq.NumberOfFractionsPlanned

        meter_set = {}
        for ref_beam in fx_grp_seq.ReferencedBeamSequence:
            ref_beam_num = str(ref_beam.ReferencedBeamNumber)
            meter_set[ref_beam_num] = float(ref_beam.BeamMeterset)

        self.beam = []
        for beam_seq in rt_plan.BeamSequence:
            beam_num = str(beam_seq.BeamNumber)
            if beam_num in meter_set:
                self.beam.append(Beam(beam_seq, meter_set[beam_num]))
        self.beam_count = len(self.beam)


class Beam:
    def __init__(self, beam_seq, meter_set):

        self.meter_set = meter_set

        self.control_point = [ControlPoint(cp_seq) for cp_seq in beam_seq.ControlPointSequence]
        self.control_point_count = len(self.control_point)

        for bld_seq in beam_seq.BeamLimitingDeviceSequence:
            if hasattr(bld_seq, 'LeafPositionBoundaries'):
                self.leaf_boundaries = np.array(map(float, bld_seq.LeafPositionBoundaries))

        self.aperture = [self.get_shapely_from_cp(cp) for cp in self.control_point]

        self.control_point_meter_set = np.append([0], np.diff(np.array([cp.cum_mu for cp in self.control_point])))

    def get_shapely_from_cp(self, cp):
        lb = self.leaf_boundaries

        if hasattr(cp, 'mlcx'):
            mlc = cp.mlcx
            order = 1
        elif hasattr(cp, 'mlcy'):
            mlc = cp.mlcy
            order = -1
        else:
            return False

        # Get list of points defining MLC open area
        leaf_pair_count = len(lb) - 1
        points = []
        for i in range(0, leaf_pair_count - 1):
            points.append((mlc[0][i], lb[i])[::order])
            points.append((mlc[0][i], lb[i + 1])[::order])
        for i in range(0, leaf_pair_count - 1)[::-1]:
            points.append((mlc[1][i], lb[i])[::order])
            points.append((mlc[1][i], lb[i + 1])[::order])
        points.append(points[0])  # explicitly close polygon
        open_polygon_mlc = Polygon(points).buffer(0)  # may turn into MultiPolygon

        # Get list of points defining Jaw open area
        if hasattr(cp, 'asymy'):
            y_min = cp.asymy[0]
            y_max = cp.asymy[1]
        else:
            y_min = np.float(-MAX_FIELD_SIZE_Y/2)
            y_max = np.float(MAX_FIELD_SIZE_Y/2)
        if hasattr(cp, 'asymx'):
            x_min = cp.asymx[0]
            x_max = cp.asymx[1]
        else:
            x_min = np.float(-MAX_FIELD_SIZE_X/2)
            x_max = np.float(MAX_FIELD_SIZE_X/2)
        points = [(x_min, y_min), (x_max, y_min),
                  (x_max, y_max), (x_min, y_max),
                  (x_min, y_min)]
        open_polygon_jaw = Polygon(points)

        aperture = open_polygon_mlc.intersection(open_polygon_jaw)

        return aperture


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


# test = get_mlc_data("/Users/nightowl/PycharmProjects/DVH-Analytics/dvh/test_files/2.16.840.1.114362.1.6.6.12.17310.7693757184.449478830.864.1265.dcm")
