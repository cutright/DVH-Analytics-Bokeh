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

# Options for the plot in the Multi-Variable Regression tab
CORRELATION_1_CIRCLE_SIZE = 10
CORRELATION_1_ALPHA = 0.5
CORRELATION_1_LINE_WIDTH = 2
CORRELATION_1_LINE_DASH = 'dashed'
CORRELATION_2_CIRCLE_SIZE = 10
CORRELATION_2_ALPHA = 0.5
CORRELATION_2_LINE_WIDTH = 2
CORRELATION_2_LINE_DASH = 'dashed'
