"""
Various options for DVH Analytics
Created on Sat Oct 28 2017
@author: Dan Cutright, PhD
"""

# Setting this to true enables log in screens
# You must add your own code in into check_credentials of auth.py
# main.py sends a usergroup of 'generic', settings.py and admin.py send usergroup of 'admin',
# user this in your check_credentials function to enable proper access
AUTH_USER_REQ = False

# The backup module can be convoluted and is really just a simple GUI for psql dump commands
# if you do not have pgsql command line tool installed, maybe best to just disable this tab to be cautious
DISABLE_BACKUP_TAB = False

# DVH Endpoint Table view cap, bokeh is very slow to delete a table and add another
# This would need to happen if "changing" number of columns in a table, so DVH Analytics prints
# and empty table with the number of endpoints set below.  All endpoints specified in main app will be calulated,
# but only the number specified below will be displayed
ENDPOINT_COUNT = 10

# These colors propagate to all tabs that visualize your two groups
GROUP_1_COLOR = 'blue'
GROUP_1_COLOR_NEG_CORR = 'green'
GROUP_2_COLOR = 'red'
GROUP_2_COLOR_NEG_CORR = 'purple'
GROUP_1_and_2_COLOR = 'purple'  # only for data in time-series that fit both groups

# The line width of selected DVHs in the DVH plot
DVH_LINE_WIDTH = 2

# Adjusts the opacity of the inner-quartile ranges
IQR_1_ALPHA = 0.075
IQR_2_ALPHA = 0.075

# Adjust the plot font sizes
PLOT_AXIS_LABEL_FONT_SIZE = "14pt"
PLOT_AXIS_MAJOR_LABEL_FONT_SIZE = "10pt"

# Number of data points are reduced by this factor during dynamic plot interaction to speed-up visualizations
# This is only applied to the DVH plot since it has a large amount of data
LOD_FACTOR = 100

# Options for the group statistical DVHs in the DVHs tab
STATS_1_MEDIAN_LINE_WIDTH = 1
STATS_1_MEDIAN_LINE_DASH = 'solid'
STATS_1_MEDIAN_ALPHA = 0.6
STATS_1_MEAN_LINE_WIDTH = 2
STATS_1_MEAN_LINE_DASH = 'dashed'
STATS_1_MEAN_ALPHA = 0.5
STATS_2_MEDIAN_LINE_WIDTH = 1
STATS_2_MEDIAN_LINE_DASH = 'solid'
STATS_2_MEDIAN_ALPHA = 0.6
STATS_2_MEAN_LINE_WIDTH = 2
STATS_2_MEAN_LINE_DASH = 'dashed'
STATS_2_MEAN_ALPHA = 0.5

# Options for the time-series plot
TIME_SERIES_1_CIRCLE_SIZE = 10
TIME_SERIES_1_CIRCLE_ALPHA = 0.25
TIME_SERIES_1_TREND_LINE_WIDTH = 1
TIME_SERIES_1_TREND_LINE_DASH = 'solid'
TIME_SERIES_1_AVG_LINE_WIDTH = 1
TIME_SERIES_1_AVG_LINE_DASH = 'dotted'
TIME_SERIES_1_PATCH_ALPHA = 0.1
TIME_SERIES_2_CIRCLE_SIZE = 10
TIME_SERIES_2_CIRCLE_ALPHA = 0.25
TIME_SERIES_2_TREND_LINE_WIDTH = 1
TIME_SERIES_2_TREND_LINE_DASH = 'solid'
TIME_SERIES_2_AVG_LINE_WIDTH = 1
TIME_SERIES_2_AVG_LINE_DASH = 'dotted'
TIME_SERIES_2_PATCH_ALPHA = 0.1

# Adjust the opacity of the histograms
HISTOGRAM_1_ALPHA = 0.3
HISTOGRAM_2_ALPHA = 0.3

# Default selections for teh correlation matrix
CORRELATION_MATRIX_DEFAULTS_1 = list(range(20, 28)) + [29, 30]
CORRELATION_MATRIX_DEFAULTS_2 = list(range(0, 3))

# Options for the plot in the Multi-Variable Regression tab
CORRELATION_1_CIRCLE_SIZE = 10
CORRELATION_1_ALPHA = 0.5
CORRELATION_1_LINE_WIDTH = 2
CORRELATION_1_LINE_DASH = 'dashed'
CORRELATION_2_CIRCLE_SIZE = 10
CORRELATION_2_ALPHA = 0.5
CORRELATION_2_LINE_WIDTH = 2
CORRELATION_2_LINE_DASH = 'dashed'

# This is the number of bins up do 100% used when resampling a DVH to fractional dose
RESAMPLED_DVH_BIN_COUNT = 5000

# For MLC Analyzer module
MAX_FIELD_SIZE_X = 400  # in mm
MAX_FIELD_SIZE_Y = 400  # in mm
CP_TIME_SPACING = 0.2  # in sec
MLC_COLOR = 'green'
JAW_COLOR = 'blue'
COMPLEXITY_SCORE_X_WEIGHT = 1.
COMPLEXITY_SCORE_Y_WEIGHT = 1.

# The automated import will only take the latest plan file if set to True
# If set to false, all plan files will be processed and imported
IMPORT_LATEST_PLAN_ONLY = False

# The following tabs are not dependent on each other, therefore could be excluded from the user view
# The layout for DVH Analytics is relatively large for Bokeh and can be relatively slow due to this
# Therefore, if there are particular tabs a user does not want to render, they can be set to False
# here to speed-up load times
OPTIONAL_TABS = {'ROI Viewer': True,
                 'Planning Data': True,
                 'Time-Series': True,
                 'Correlation': True,
                 'Regression': True,
                 'MLC Analyzer': True}

# Note that docker paths are absolute, default will be treated as relative to script directory
SETTINGS_PATHS = {'docker': {'import': "/import_settings.txt",
                             'sql': "/sql_connection.cnf"},
                  'default': {'import': "preferences/import_settings.txt",
                              'sql': "preferences/sql_connection.cnf"}}

# Set this to True to turn off all modules except Query and DVHs.  No graphics are generated.  Activating this will
# be useful for VERY large datasets when the user is only interested in raw data and DVH Endpoint calculation
LITE_VIEW = False

