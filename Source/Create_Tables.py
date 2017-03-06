#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 19:16:16 2017

@author: nightowl
"""

from SQL_Tools import Create_Table_DVHs, Create_Table_Plans


def Create_Tables():

    Create_Table_DVHs()
    Create_Table_Plans()


if __name__ == '__main__':
    Create_Tables()
