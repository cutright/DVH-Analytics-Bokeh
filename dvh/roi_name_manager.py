#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:43:28 2017

@author: nightowl
"""

import os
from fuzzywuzzy import fuzz
from sql_to_python import QuerySQL
from sql_connector import DVH_SQL


class Physician:
    def __init__(self, initials):
        self.initials = initials

        self.physician_rois = {}

    def add_physician_roi(self, institutional_roi, physician_roi):
        institutional_roi = clean_name(institutional_roi)
        physician_roi = clean_name(physician_roi)
        self.physician_rois[physician_roi] = {'institutional_roi': institutional_roi,
                                              'variations': [physician_roi]}

    def add_physician_roi_variation(self, physician_roi, variation):
        physician_roi = clean_name(physician_roi)
        variation = clean_name(variation)
        if physician_roi in self.physician_rois.keys():
            if variation not in self.physician_rois[physician_roi]['variations']:
                self.physician_rois[physician_roi]['variations'].append(variation)
                self.physician_rois[physician_roi]['variations'].sort()


class DatabaseROIs:
    def __init__(self):

        self.physicians = {}
        self.institutional_rois = []

        self.script_dir = os.path.dirname(__file__)

        # Import institutional roi names
        rel_path = "preferences/institutional.roi"
        abs_file_path = os.path.join(self.script_dir, rel_path)
        if os.path.isfile(abs_file_path):
            with open(abs_file_path, 'r') as document:
                for line in document:
                    if not line:
                        continue
                    line = clean_name(str(line))
                    self.institutional_rois.append(line)

        physicians = get_physicians_from_roi_files()
        for physician in physicians:
            self.add_physician(physician)

        self.import_physician_roi_maps()

        if 'uncategorized' not in self.institutional_rois:
            self.institutional_rois.append('uncategorized')

    ##############################################
    # Import from file functions
    ##############################################
    def get_institutional_rois(self):
        return self.institutional_rois

    def get_institutional_roi(self, physician, physician_roi):
        physician = clean_name(physician).upper()
        physician_roi = clean_name(physician_roi)
        try:
            return self.physicians[physician].physician_rois[physician_roi]['institutional_roi']
        except KeyError:
            return ''

    def import_physician_roi_maps(self):

        for physician in self.physicians.keys():
            rel_path = 'preferences/physician_' + physician + '.roi'
            abs_file_path = os.path.join(self.script_dir, rel_path)
            if os.path.isfile(abs_file_path):
                self.import_physician_roi_map(abs_file_path, physician)

    def import_physician_roi_map(self, abs_file_path, physician):

        with open(abs_file_path, 'r') as document:
            for line in document:
                if not line:
                    continue
                line = str(line).lower().strip().replace(':', ',').split(',')
                institutional_roi = line[0].strip()
                physician_roi = line[1].strip()

                self.add_institutional_roi(institutional_roi)
                self.add_physician_roi(physician, institutional_roi, physician_roi)

                for i in range(2, len(line)):
                    variation = clean_name(line[i])
                    self.add_variation(physician, physician_roi, variation)

    ###################################
    # Physician functions
    ###################################
    def add_physician(self, physician):
        physician = clean_name(physician).upper()
        if physician not in self.get_physicians():
            self.physicians[physician] = Physician(physician)

    def delete_physician(self, physician):
        physician = clean_name(physician).upper()
        self.physicians.pop(physician, None)

    def get_physicians(self):
        physicians = self.physicians.keys()
        if 'DEFAULT' in physicians:
            physicians.pop(physicians.index('DEFAULT'))
        return physicians

    def get_physician(self, physician):
        return self.physicians[physician]

    def is_physician(self, physician):
        physician = clean_name(physician).upper()
        for initials in self.get_physicians():
            if physician == initials:
                return True
        return False

    #################################
    # Institutional ROI functions
    #################################
    def get_institutional_rois(self):
        return self.institutional_rois

    def add_institutional_roi(self, roi):
        roi = clean_name(roi)
        if roi not in self.institutional_rois:
            self.institutional_rois.append(roi)
            self.institutional_rois.sort()

    def set_institutional_roi(self, new_institutional_roi, institutional_roi):
        new_institutional_roi = clean_name(new_institutional_roi)
        institutional_roi = clean_name(institutional_roi)
        index = self.institutional_rois.index(institutional_roi)
        self.institutional_rois.pop(index)
        self.add_institutional_roi(new_institutional_roi)
        for physician in self.get_physicians():
            if physician != 'DEFAULT':
                for physician_roi in self.get_physician_rois(physician):
                    physician_roi_obj = self.physicians[physician].physician_rois[physician_roi]
                    if physician_roi_obj['institutional_roi'] == institutional_roi:
                        physician_roi_obj['institutional_roi'] = new_institutional_roi

    def delete_institutional_roi(self, roi):
        self.set_institutional_roi('uncategorized', roi)

    def is_institutional_roi(self, roi):
        roi = clean_name(roi)
        for institutional_roi in self.institutional_rois:
            if roi == institutional_roi:
                return True
        return False

    def get_unused_institutional_rois(self, physician):
        physician = clean_name(physician).upper()
        used_rois = []
        if self.get_physician_rois(physician)[0] != '':
            for physician_roi in self.get_physician_rois(physician):
                used_rois.append(self.get_institutional_roi(physician, physician_roi))

        unused_rois = ['']
        for roi in self.institutional_rois:
            if roi not in used_rois:
                unused_rois.append(roi)
        if 'uncategorized' not in unused_rois:
            unused_rois.append('uncategorized')

        return unused_rois

    ########################################
    # Physician ROI functions
    ########################################
    def get_physician_rois(self, physician):
        physician = clean_name(physician).upper()
        if self.is_physician(physician):
            physician_rois = self.physicians[physician].physician_rois.keys()
            if physician_rois:
                physician_rois.sort()
                return physician_rois
            else:
                return ['']
        else:
            return ['']

    def get_physician_roi(self, physician, roi):
        physician = clean_name(physician).upper()
        roi = clean_name(roi)
        for physician_roi in self.get_physician_rois(physician):
            for variation in self.get_variations(physician, physician_roi):
                if roi == variation:
                    return physician_roi
        return 'uncategorized'

    def add_physician_roi(self, physician, institutional_roi, physician_roi):
        physician = clean_name(physician).upper()
        institutional_roi = clean_name(institutional_roi)
        physician_roi = clean_name(physician_roi)
        if physician_roi not in self.get_physician_rois(physician):
            if institutional_roi in self.institutional_rois:
                self.physicians[physician].add_physician_roi(institutional_roi, physician_roi)

    def set_physician_roi(self, new_physician_roi, physician, physician_roi):
        if new_physician_roi != physician_roi:
            self.physicians[physician].physician_rois[new_physician_roi] = \
                self.physicians[physician].physician_rois.pop(physician_roi, None)

    def delete_physician_roi(self, physician, physician_roi):
        physician = clean_name(physician).upper()
        physician_roi = clean_name(physician_roi)
        if physician_roi in self.get_physician_rois(physician):
            self.physicians[physician].physician_rois.pop(physician_roi, None)

    def is_physician_roi(self, roi):
        roi = clean_name(roi)
        for physician in self.get_physicians():
            for physician_roi in self.get_physician_rois(physician):
                if roi == physician_roi:
                    return True
        return False

    ###################################################
    # Variation-of-Physician-ROI functions
    ###################################################
    def get_variations(self, physician, physician_roi):
        physician = clean_name(physician).upper()
        physician_roi = clean_name(physician_roi)
        try:
            variations = self.physicians[physician].physician_rois[physician_roi]['variations']
            if variations:
                return variations
            else:
                return ['']
        except KeyError:
            return ['']

    def get_all_variations_of_physician(self, physician):
        physician = clean_name(physician).upper()
        variations = []
        for physician_roi in self.get_physician_rois(physician):
            for variation in self.get_variations(physician, physician_roi):
                variations.append(variation)
        if variations:
            variations.sort()
        else:
            variations = ['']
        return variations

    def add_variation(self, physician, physician_roi, variation):
        physician = clean_name(physician).upper()
        physician_roi = clean_name(physician_roi)
        variation = clean_name(variation)
        if variation not in self.get_variations(physician, physician_roi):
            self.physicians[physician].add_physician_roi_variation(physician_roi, variation)

    def delete_variation(self, physician, physician_roi, variation):
        physician = clean_name(physician).upper()
        physician_roi = clean_name(physician_roi)
        variation = clean_name(variation)
        if variation in self.get_variations(physician, physician_roi):
            index = self.physicians[physician].physician_rois[physician_roi]['variations'].index(variation)
            self.physicians[physician].physician_rois[physician_roi]['variations'].pop(index)
            self.physicians[physician].physician_rois[physician_roi]['variations'].sort()

    def set_variation(self, new_variation, physician, physician_roi, variation):
        new_variation = clean_name(new_variation)
        physician = clean_name(physician).upper()
        physician_roi = clean_name(physician_roi)
        variation = clean_name(variation)
        if new_variation != variation:
            self.add_variation(physician, physician_roi, new_variation)
            self.delete_variation(physician, physician_roi, variation)

    def is_roi(self, roi):
        roi = clean_name(roi)
        for physician in self.get_physicians():
            for physician_roi in self.get_physician_rois(physician):
                for variation in self.get_variations(physician, physician_roi):
                    if roi == variation:
                        return True
        return False

    def get_best_roi_match(self, roi, **kwargs):
        roi = clean_name(roi)

        scores = []
        rois = []
        physicians = []

        for physician in self.get_physicians():
            for physician_roi in self.get_physician_rois(physician):
                scores.append(get_combined_fuzz_score(physician_roi, roi))
                rois.append(physician_roi)
                physicians.append(physician)
                for variation in self.get_variations(physician, physician_roi):
                    scores.append(get_combined_fuzz_score(variation, roi))
                    rois.append(variation)
                    physicians.append(physician)

        for institutional_roi in self.institutional_rois:
            scores.append(get_combined_fuzz_score(institutional_roi, roi))
            rois.append(institutional_roi)
            physicians.append('DEFAULT')

        best = []

        if 'length' in kwargs:
            if kwargs['length'] > len(scores):
                length = len(scores)
            else:
                length = kwargs['length']
        else:
            length = 1

        for i in range(0, length):
            max_score = max(scores)
            index = scores.index(max_score)
            scores.pop(index)
            best_match = rois.pop(index)
            best_physician = physicians.pop(index)
            if self.is_institutional_roi(best_match):
                best_institutional_roi = best_match
            else:
                best_institutional_roi = 'uncategorized'

            best_physician_roi = self.get_physician_roi(best_physician, best_match)

            best.append({'variation': best_match,
                         'physician_roi': best_physician_roi,
                         'physician': best_physician,
                         'institutional_roi': best_institutional_roi,
                         'score': max_score})

        return best

    ########################
    # Export to file
    ########################
    def write_to_file(self):
        script_dir = os.path.dirname(__file__)

        physicians = self.get_physicians()
        physicians.pop(physicians.index('DEFAULT'))  # remove 'DEFAULT' physician

        for physician in physicians:
            rel_dir = "preferences/"
            file_name = 'physician_' + physician + '.roi'
            abs_file_path = os.path.join(script_dir, rel_dir, file_name)
            document = open(abs_file_path, 'w')
            lines = []
            for physician_roi in self.get_physician_rois(physician):
                institutional_roi = self.get_institutional_roi(physician, physician_roi)
                variations = self.get_variations(physician, physician_roi)
                variations = ', '.join(variations)
                line = [institutional_roi,
                        physician_roi,
                        variations]
                line = ': '.join(line)
                line += '\n'
                lines.append(line)
            lines.sort()
            for line in lines:
                document.write(line)

            document.close()


def clean_name(name):
    return str(name).lower().strip().replace(' ', '_').replace('\'', '`')


def get_physicians_from_roi_files():

    script_dir = os.path.dirname(__file__)
    rel_path = "preferences/"
    abs_dir_path = os.path.join(script_dir, rel_path)

    physicians = ['DEFAULT']
    for file_name in os.listdir(abs_dir_path):
        if file_name.startswith("physician_") and file_name.endswith(".roi"):
            physician = file_name.replace('physician_', '').replace('.roi', '')
            physician = clean_name(physician).upper()
            physicians.append(physician)

    return physicians


def get_physician_from_uid(uid):
    cnx = DVH_SQL()
    condition = "study_instance_uid = '" + uid + "'"
    results = cnx.query('Plans', 'physician', condition)

    if len(results) > 1:
        print 'Warning: multiple plans with this study_instance_uid exist'

    return str(results[0][0])


def update_uncategorized_rois_in_database():
    roi_map = DatabaseROIs()
    dvh_data = QuerySQL('DVHs', "physician_roi = 'uncategorized'")
    cnx = DVH_SQL()

    for i in range(0, len(dvh_data.roi_name)):
        uid = dvh_data.study_instance_uid[i]
        mrn = dvh_data.mrn[i]
        physician = get_physician_from_uid(uid)
        roi_name = dvh_data.roi_name[i]

        new_physician_roi = roi_map.get_physician_roi(physician, roi_name)
        new_institutional_roi = roi_map.get_institutional_roi(physician, roi_name)

        if new_physician_roi != 'uncategorized':
            print mrn, physician, new_institutional_roi, new_physician_roi, roi_name
            condition = "study_instance_uid = '" + uid + "'" + "and roi_name = '" + roi_name + "'"
            cnx.update('DVHs', 'physician_roi', new_physician_roi, condition)
            cnx.update('DVHs', 'institutional_roi', new_institutional_roi, condition)

    cnx.close()


def reinitialize_roi_categories_in_database():
    roi_map = DatabaseROIs()
    dvh_data = QuerySQL('DVHs', "mrn != ''")
    cnx = DVH_SQL()

    for i in range(0, len(dvh_data.roi_name)):
        uid = dvh_data.study_instance_uid[i]
        physician = get_physician_from_uid(uid)
        roi_name = dvh_data.roi_name[i]

        new_physician_roi = roi_map.get_physician_roi(physician, roi_name)
        new_institutional_roi = roi_map.get_institutional_roi(physician, roi_name)

        print i, physician, new_institutional_roi, new_physician_roi, roi_name
        condition = "study_instance_uid = '" + uid + "'" + "and roi_name = '" + roi_name + "'"
        cnx.update('DVHs', 'physician_roi', new_physician_roi, condition)
        cnx.update('DVHs', 'institutional_roi', new_institutional_roi, condition)

    cnx.close()


def print_uncategorized_rois():
    dvh_data = QuerySQL('DVHs', "physician_roi = 'uncategorized'")
    print 'physician, institutional_roi, physician_roi, roi_name'
    for i in range(0, len(dvh_data.roi_name)):
        uid = dvh_data.study_instance_uid[i]
        physician = get_physician_from_uid(uid)
        roi_name = dvh_data.roi_name[i]
        physician_roi = dvh_data.physician_roi[i]
        institutional_roi = dvh_data.institutional_roi[i]
        print physician, institutional_roi, physician_roi, roi_name


def get_combined_fuzz_score(a, b, **kwargs):
    a = clean_name(a)
    b = clean_name(b)

    if 'simple' in kwargs:
        w_simple = float(kwargs['simple'])
    else:
        w_simple = float(1)

    if 'partial' in kwargs:
        w_partial = float(kwargs['partial'])
    else:
        w_partial = float(1)

    simple = fuzz.ratio(a, b) * w_simple
    partial = fuzz.partial_ratio(a, b) * w_partial
    combined = float(simple) * float(partial) / float(10000)
    return combined


if __name__ == '__main__':
    pass
