#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
baseline plans model for admin view
Created on Sun Jan 20 2019
@author: Dan Cutright, PhD
This module is to designed to provide quick notes for the import process
"""

from bokeh.models.widgets import Div, PreText
from bokeh.layouts import column


class Step:
    def __init__(self, step, title, text):
        self.title = Div(text='<b>Step %s: %s</b>' % (step, title))
        self.text = PreText(text=text, width=1000)
        self.layout = column(self.title, self.text)


class ImportNotes:
    def __init__(self):
        self.step_0 = Step(0, 'First Time Users',
                           'Be sure you have run the Settings server to setup import directories and SQL connection \n'
                           'settings.')

        self.step_1 = Step(1, 'Importing',
                           'Place all DICOM files to be imported (including RTPlan, RTDose, and RTStruct) in your \n'
                           'inbox. Then click Import Inbox in the Database Editor tab.\n\n'
                           'NOTE: It will be very helpful to define the physician and label all PTVs as ROI Type PTV \n'
                           'in your TPS prior to DICOM export. Having a nearly uniform ROI naming scheme will help too.')

        self.step_2 = Step(2, 'Physician and ROI Type Clean-Up',
                           'Query the Plans table including the physician to ensure all imported plans have a \n'
                           'physician assigned. You can add conditions in postgres SQL syntax like:\n'
                           '\timport_time_stamp > \'01/20/2019\'\n'
                           '\tphysician is NULL\n\n'
                           'Query the DVHs table to make sure your PTVs are tagged as PTV or PTV# in the roi_type \n'
                           'column. The following condition may be helpful:\n'
                           '\troi_type == \'ORGAN\' and roi_name like \'%ptv%\'\n\n'
                           'If necessary (which it won\'t be if you defined these in your TPS prior to export), \n'
                           'update the physician and roi_type columns. Be sure to apply appropriate conditions')

        self.step_3 = Step(3, 'ROI Map Generation/Updating',
                           'From the ROI Name Manager, add a new physician is necessary. Any ROIs in the Uncategorized \n'
                           'dropdown will be ignored in Step 5. Its best practice to either add variations and point \n'
                           'to the appropriate Physician ROI or click \'Ignore\' so that the Uncategorized dropdown \n'
                           'is not cluttered and easy to review later (or just delete the DVH).\n')

        self.step_4 = Step(4, 'Applying ROI Map to SQL Database',
                           'Saving the ROI map simply saves the text file containing the map. You need to click Remap \n'
                           'with the appropriate drop down selected to update the SQL database. New users might as \n'
                           'well remap the entire database.')

        self.step_5 = Step(5, 'Post-Import Calculations',
                           'In the Database Editor tab, click Perform Calc. Default Post-Import should be sufficient')

        self.layout = column(self.step_0.layout, Div(text="<hr>", width=700),
                             self.step_1.layout, Div(text="<hr>", width=700),
                             self.step_2.layout, Div(text="<hr>", width=700),
                             self.step_3.layout, Div(text="<hr>", width=700),
                             self.step_4.layout, Div(text="<hr>", width=700),
                             self.step_5.layout)
