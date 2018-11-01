#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
utilities for data in bokeh objects in the DVH Analytics main Bokeh program
Created on Tue Oct 30 2018
@author: Dan Cutright, PhD
"""
from options import N
import numpy as np
from future.utils import listitems


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


def validate_correlation(correlation, bad_uid):

    for n in N:
        if correlation[n]:
            for range_var in list(correlation[n]):
                for i, j in enumerate(correlation[n][range_var]['data']):
                    if j == 'None':
                        current_uid = correlation[n][range_var]['uid'][i]
                        if current_uid not in bad_uid[n]:
                            bad_uid[n].append(current_uid)
                        print("%s[%s] is non-numerical, will remove this patient from correlation data"
                              % (range_var, i))

            new_correlation = {}
            for range_var in list(correlation[n]):
                new_correlation[range_var] = {'mrn': [], 'uid': [], 'data': [],
                                              'units': correlation['1'][range_var]['units']}
                for i in range(len(correlation[n][range_var]['data'])):
                    current_uid = correlation[n][range_var]['uid'][i]
                    if current_uid not in bad_uid[n]:
                        for j in {'mrn', 'uid', 'data'}:
                            new_correlation[range_var][j].append(correlation[n][range_var][j][i])

            correlation[n] = new_correlation

    return correlation, bad_uid


def get_correlation(sources, correlation_variables, range_categories):

    correlation = {'1': {}, '2': {}}

    temp_keys = ['uid', 'mrn', 'data', 'units']

    # remove review and stats from source
    include = get_include_map(sources)
    # Get data from DVHs table
    for key in correlation_variables:
        src = range_categories[key]['source']
        curr_var = range_categories[key]['var_name']
        table = range_categories[key]['table']
        units = range_categories[key]['units']

        if table in {'DVHs'}:
            temp = {n: {k: [] for k in temp_keys} for n in N}
            temp['units'] = units
            for i in range(len(src.data['uid'])):
                if include[i]:
                    for n in N:
                        if src.data['group'][i] in {'Group %s' % n, 'Group 1 & 2'}:
                            temp[n]['uid'].append(src.data['uid'][i])
                            temp[n]['mrn'].append(src.data['mrn'][i])
                            temp[n]['data'].append(src.data[curr_var][i])
            for n in N:
                correlation[n][key] = {k: temp[n][k] for k in temp_keys}

    uid_list = {n: correlation[n]['ROI Max Dose']['uid'] for n in N}

    # Get Data from Plans table
    for key in correlation_variables:
        src = range_categories[key]['source']
        curr_var = range_categories[key]['var_name']
        table = range_categories[key]['table']
        units = range_categories[key]['units']

        if table in {'Plans'}:
            temp = {n: {k: [] for k in temp_keys} for n in N}
            temp['units'] = units

            for n in N:
                for i in range(len(uid_list[n])):
                    uid = uid_list[n][i]
                    uid_index = src.data['uid'].index(uid)
                    temp[n]['uid'].append(uid)
                    temp[n]['mrn'].append(src.data['mrn'][uid_index])
                    temp[n]['data'].append(src.data[curr_var][uid_index])

            for n in N:
                correlation[n][key] = {k: temp[n][k] for k in temp_keys}

    # Get data from Beams table
    for key in correlation_variables:

        src = range_categories[key]['source']
        curr_var = range_categories[key]['var_name']
        table = range_categories[key]['table']
        units = range_categories[key]['units']

        stats = ['min', 'mean', 'median', 'max']

        if table in {'Beams'}:
            beam_keys = stats + ['uid', 'mrn']
            temp = {n: {bk: [] for bk in beam_keys} for n in N}
            for n in N:
                for i in range(len(uid_list[n])):
                    uid = uid_list[n][i]
                    uid_indices = [j for j, x in enumerate(src.data['uid']) if x == uid]
                    plan_values = [src.data[curr_var][j] for j in uid_indices]

                    temp[n]['uid'].append(uid)
                    temp[n]['mrn'].append(src.data['mrn'][uid_indices[0]])
                    for s in stats:
                        temp[n][s].append(getattr(np, s)(plan_values))

            for s in stats:
                for n in N:
                    corr_key = "%s (%s)" % (key, s.capitalize())
                    correlation[n][corr_key] = {'uid': temp[n]['uid'],
                                                'mrn': temp[n]['mrn'],
                                                'data': temp[n][s],
                                                'units': units}

    return correlation


def update_or_add_endpoints_to_correlation(sources, correlation, multi_var_reg_vars):

    include = get_include_map(sources)

    # clear out any old DVH endpoint data
    for n in N:
        if correlation[n]:
            for key in list(correlation[n]):
                if key.startswith('ep'):
                    correlation[n].pop(key, None)

    src = sources.endpoint_calcs
    for j in range(len(sources.endpoint_defs.data['label'])):
        key = sources.endpoint_defs.data['label'][j]
        units = sources.endpoint_defs.data['units_out'][j]
        ep = "DVH Endpoint: %s" % key

        temp_keys = ['uid', 'mrn', 'data', 'units']
        temp = {n: {k: [] for k in temp_keys} for n in N}
        temp['units'] = units

        for i in range(len(src.data['uid'])):
            if include[i]:
                for n in N:
                    if src.data['group'][i] in {'Group %s' % n, 'Group 1 & 2'}:
                        temp[n]['uid'].append(src.data['uid'][i])
                        temp[n]['mrn'].append(src.data['mrn'][i])
                        temp[n]['data'].append(src.data[key][i])

        for n in N:
            correlation[n][ep] = {k: temp[n][k] for k in temp_keys}

        if ep not in list(multi_var_reg_vars):
            multi_var_reg_vars[ep] = False

    # declare space to tag variables to be used for multi variable regression
    for n in N:
        for key, value in listitems(correlation[n]):
            correlation[n][key]['include'] = [False] * len(value['uid'])
