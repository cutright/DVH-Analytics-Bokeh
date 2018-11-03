from options import N
from future.utils import listitems
import numpy as np
from dateutil.relativedelta import relativedelta


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


def clear_source_data(sources, key):
    src = getattr(sources, key)
    src.data = {k: [] for k in list(src.data)}


def clear_source_selection(sources, key):
    getattr(sources, key).selected.indices = []