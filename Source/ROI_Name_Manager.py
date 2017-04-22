#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:43:28 2017

@author: nightowl
"""

import os


class ROISet:
    def __init__(self, institutional_roi_name, physician_roi_name, roi_name, physician):
        self.institutional_roi_name = institutional_roi_name
        self.physician_roi_name = physician_roi_name
        self.roi_name = roi_name
        self.physician = physician


class DatabaseROIs:
    def __init__(self):
        self.count = 0
        self.roi = {}
        self.institutional_roi_map = {}
        self.physician_roi_map = {}
        self.roi_map = {}
        self.physician_map = {}
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "preferences/database.roi"
        abs_file_path = os.path.join(script_dir, rel_path)
        if os.path.isfile(rel_path):
            with open(abs_file_path, 'r') as document:
                for line in document:
                    if not line:
                        continue
                    line = str(line).split(',')
                    line[0] = line[0].strip()
                    line[1] = line[1].strip()
                    line[2] = line[2].strip()
                    if line[3]:
                        line[3] = line[3].strip()
                    else:
                        line[3] = 'default'
                    current_roi_map = ROISet(line[0], line[1], line[2], line[3])
                    self.update_maps(current_roi_map)
                    self.roi[self.count] = current_roi_map
                    self.count += 1
        else:
            rel_path = "preferences/default.roi"
            abs_file_path = os.path.join(script_dir, rel_path)
            with open(abs_file_path, 'r') as document:
                for line in document:
                    if not line:
                        continue
                    line = str(line).strip().lower()
                    current_roi_map = ROISet(line, line, line, 'default')
                    self.roi[self.count] = current_roi_map
                    self.update_maps(current_roi_map)
                    self.count += 1

            rel_path = "preferences/physicians.roi"
            abs_file_path = os.path.join(script_dir, rel_path)
            with open(abs_file_path, 'r') as document:
                physicians = []
                physician_files = []
                physician_count = 0
                for line in document:
                    if not line:
                        continue
                    line = str(line.strip()).upper()
                    physicians.append(line)
                    file_name = 'physician_map_' + line + '.roi'
                    physician_files.append(file_name)
                    physician_count += 1

            for i in range(0, physician_count):
                self.append(physician_files[i], physicians[i])

            self.write_to_file()

    def __len__(self):
        return self.count

    def __getitem__(self, x):
        indices = self.institutional_roi_map[x].split(',')
        all = []
        for i in range(0, len(indices)):
            s = []
            s.append(self.roi[int(indices[i])].physician_roi_name)
            s.append(self.roi[int(indices[i])].roi_name)
            s.append(self.roi[int(indices[i])].physician)
            s = ', '.join(s)
            all.append(s)
        all.sort()
        return all

    def __iter__(self):
        return self.roi.itervalues()

    def __repr__(self):
        keys = []
        for key in self.institutional_roi_map:
            keys.append(key)
        keys.sort()

        return '\n'.join(keys)

    def append(self, roi_file, physician):
        with open(roi_file, 'r') as document:
            for line in document:
                if not line:
                    continue

                line = line.lower().strip().replace(':', ',').split(',')
                institutional_roi_name = line[0].strip()
                physician_roi_name = line[1].strip()
                for i in range(2, len(line)):
                    current_roi_name = line[i].strip().replace(' ', '_')
                    current_roi_set = ROISet(institutional_roi_name,
                                             physician_roi_name,
                                             current_roi_name,
                                             physician)
                    self.roi[self.count] = current_roi_set
                    self.update_maps(current_roi_set)
                    self.count += 1

    def is_institutional_roi(self, roi):
        clean_roi = roi.replace(' ', '_').lower()
        for key in self.institutional_roi_map:
            if clean_roi == key.replace(' ','_').lower():
                return True
        return False

    def is_physician_roi(self, roi):
        clean_roi = roi.replace(' ', '_').lower()
        for key in self.physician_roi_map:
            if clean_roi == key.replace(' ','_').lower():
                return True
        return False

    def is_roi(self, roi):
        clean_roi = roi.replace(' ', '_').lower().strip()
        for key in self.roi_map:
            if clean_roi == key.replace(' ', '_').lower():
                return True
        return False

    def is_physician(self, physician):
        for key in self.physician_map:
            if physician.upper().strip() == key.upper():
                return True
        return False

    def get_physician_roi(self, roi, physician):
        physician = physician.upper()
        roi = roi.strip().replace(' ', '_').lower()
        if not self.is_physician(physician):
            physician = 'default'
        if self.is_roi(roi):
            indices = self.roi_map[roi].split(',')
            for i in indices:
                if physician == self.roi[int(i)].physician:
                    return self.roi[int(i)].physician_roi_name
            return 'uncategorized'
        else:
            return 'uncategorized'

    def get_physician_roi_list(self, physician):
        physician = physician.upper()
        physician_rois = []
        for key in self.roi:
            if self.roi[key].roi_name == self.get_physician_roi(self.roi[key].roi_name, physician):
                if self.roi[key].roi_name not in physician_rois:
                    physician_rois.append(self.roi[key].roi_name)
        physician_rois.sort()
        return physician_rois

    def get_institutional_roi(self, roi, physician):
        physician = physician.upper()
        roi = roi.strip().replace(' ', '_').lower()
        if not self.is_physician(physician):
            physician = 'default'
        if self.is_roi(roi):
            indices = self.roi_map[roi].split(',')
            for i in indices:
                if physician == self.roi[int(i)].physician:
                    return self.roi[int(i)].institutional_roi_name
            if self.is_institutional_roi(roi):
                return roi
            return 'uncategorized'
        else:
            return 'uncategorized'

    def update_maps(self, roi_set):
        institutional_roi = roi_set.institutional_roi_name.replace(' ', '_').lower().strip()
        physician_roi = roi_set.physician_roi_name.replace(' ', '_').lower().strip()
        roi = roi_set.roi_name.replace(' ', '_').lower().strip()
        physician = roi_set.physician.upper()

        # Add roi index to institutional_roi_map
        if self.is_institutional_roi(institutional_roi):
            self.institutional_roi_map[institutional_roi] += ',' + str(self.count)
        else:
            self.institutional_roi_map[institutional_roi] = str(self.count)

        # Add roi index to physician_roi_map
        if self.is_physician_roi(physician_roi):
            self.physician_roi_map[physician_roi] += ',' + str(self.count)
        else:
            self.physician_roi_map[physician_roi] = str(self.count)

        # Add roi index to roi_map
        if self.is_roi(roi):
            self.roi_map[roi] += ',' + str(self.count)
        else:
            self.roi_map[roi] = str(self.count)

        # Add roi index to physician_map
        if self.is_physician(physician):
            self.physician_map[physician] += ',' + str(self.count)
        else:
            self.physician_map[physician] = str(self.count)

    def write_to_file(self):
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "preferences/database.roi"
        abs_file_path = os.path.join(script_dir, rel_path)
        document = open(abs_file_path, 'w')

        for i in range(0, self.count):
            line = [self.roi[i].institutional_roi_name,
                    self.roi[i].physician_roi_name,
                    self.roi[i].roi_name,
                    self.roi[i].physician]
            line = ','.join(line)
            line += '\n'
            document.write(line)

        document.close()


if __name__ == '__main__':
    pass
