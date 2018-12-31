#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
from future.utils import listitems
import pickle
try:
    import pydicom as dicom  # for pydicom >= 1.0
except ImportError:
    import dicom
from paths import PREF_DIR
import types


def save_options(options):
    abs_file_path = os.path.join(PREF_DIR, 'options')

    out_options = {}
    for i in options.__dict__:
        if not i.startswith('_'):
            out_options[i] = getattr(options, i)

    outfile = open(abs_file_path, 'wb')
    pickle.dump(out_options, outfile)
    outfile.close()


def load_options(options):
    abs_file_path = os.path.join(PREF_DIR, 'options')

    if os.path.isfile(abs_file_path):

        try:
            infile = open(abs_file_path, 'rb')
            new_dict = pickle.load(infile)

            new_options = Object()
            for key, value in listitems(new_dict):
                setattr(new_options, key, value)

            infile.close()

            return new_options
        except EOFError:
            print('Corrupt options file, loading defaults.')

    out_options = Object()
    for i in options.__dict__:
        if not i.startswith('_'):
            value = getattr(options, i)
            if not isinstance(value, types.ModuleType):  # ignore imports in options.py
                setattr(out_options, i, value)
    return out_options


class Object():
    pass