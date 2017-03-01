#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 11:06:28 2017

@author: nightowl
"""

from dicompylercore import dicomparser, dvhcalc


class ROI:
    def __init__(self, Name, Type, Volume, MinDose, MeanDose, MaxDose,
                 DoseBinSize, DoseUnits, VolumeString, VolumeUnits):
        self.Name = Name
        self.Type = Type
        self.Volume = Volume
        self.MinDose = MinDose
        self.MeanDose = MeanDose
        self.MaxDose = MaxDose
        self.DoseBinSize = DoseBinSize
        self.DoseUnits = DoseUnits
        self.VolumeString = VolumeString
        self.VolumeUnits = VolumeUnits


def Create_ROI_PyTable(StructureFile, DoseFile):
    # Import RT Structure and RT Dose files using dicompyler
    RT_St = dicomparser.DicomParser(StructureFile)
    Structures = RT_St.GetStructures()
    ROI_Count = len(Structures)
    # ROI_Count = 10
    Seperator = ','

    ROI_List = {}

    ROI_List_Counter = 1

    for ROI_Counter in range(1, ROI_Count):
        # Import DVH from RT Structure and RT Dose files
        if Structures[ROI_Counter]['type'] != 'MARKER':
            print 'importing:       ' + Structures[ROI_Counter]['type'] + ' ' + Structures[ROI_Counter]['name'] + '...'
            Current_DVH = dvhcalc.get_dvh(StructureFile, DoseFile, ROI_Counter)
            if Current_DVH.volume > 0:
                Current_ROI = ROI(Structures[ROI_Counter]['name'],
                                  Structures[ROI_Counter]['type'],
                                  Current_DVH.volume,
                                  Current_DVH.min,
                                  Current_DVH.mean,
                                  Current_DVH.max,
                                  Current_DVH.bins[1],
                                  Current_DVH.dose_units,
                                  Seperator.join(['%.2f' % num for num in Current_DVH.counts]),
                                  Current_DVH.volume_units)
                ROI_List[ROI_List_Counter] = Current_ROI
                print 'import complete: ' + ROI_List[ROI_List_Counter].Type + ' ' + ROI_List[ROI_List_Counter].Name
                ROI_List_Counter += 1
            else:
                print 'import skipped:  ' + Structures[ROI_Counter]['type'] + ' ' + Structures[ROI_Counter]['name']

        else:
            print 'import skipped:  ' + Structures[ROI_Counter]['type'] + ' ' + Structures[ROI_Counter]['name']
    return ROI_List

if __name__ == '__main__':
    Create_ROI_PyTable()
