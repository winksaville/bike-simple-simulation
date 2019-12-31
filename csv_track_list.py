#!/usr/bin/env python3

# bike power calculation
from __future__ import annotations
from typing import Optional, List, TextIO
from dataclasses import dataclass
from time import struct_time, strptime

import csv
import math
import io
import os
import numpy as np
import xml.etree.ElementTree as et
import track_point as tp
import tcx_track_list as ttl

def CsvReaderTrackList(reader: TextIO, dialect: str='excel') -> List[tp.TrackPoint]:
    """Create a List[tp.TrackPoint] from a csv TextIO stream, result maybe empty if no data"""

    # Create a list of TrackPoints
    track: List[tp.TrackPoint] = []
    csvReader = csv.reader(reader, dialect=dialect)
    pt: tp.TrackPoint = tp.mkTrackPoint()
    for row in csvReader:
        #print(f'row={row}')
        pt.ele = float(row[0])
        pt.lat = float(row[1])
        pt.lon = float(row[2])
        pt.brg = float(row[3])
        pt.idx = int(row[4])
        pt.tot = float(row[5])
        pt.dis = float(row[6])
        pt.slp = float (row[7])
        pt.spd = float(row[8])
        pt.hrt = float(row[9])
        pt.wts = float(row[10])
        pt.rds = float(row[11])
        pt.tim = float(row[12])
        track.append(pt)

    return track

def CsvTrackList(filename: str) -> List[tp.TrackPoint]:
    with open(filename, 'r', newline='') as csvfile:
        return CsvReaderTrackList(csvfile)

def CsvStrTrackList(strg: str) -> List[tp.TrackPoint]:
    with io.StringIO(strg) as sio:
        return CsvReaderTrackList(sio)

def writeTrackListAsCsvToWriter(tl: List[tp.TrackPoint], writer: TextIO, dialect: str='excel') -> None:
        csvWriter = csv.writer(writer, dialect=dialect)
        csvWriter.writerows(tl)

def writeTrackListAsCsvToFile(tl: List[tp.TrackPoint], filename: str, dialect: str='excel') -> None:
    with open(filename, 'w', newline='') as csvfile:
        writeTrackListAsCsvToWriter(tl, csvfile, dialect=dialect)

def writeTrackListAsCsvToStr(tl: List[tp.TrackPoint], dialect: str='excel') -> str:
    with io.StringIO() as sio:
        writeTrackListAsCsvToWriter(tl, sio, dialect=dialect)
        return sio.getvalue()

if __name__ == '__main__':
    import copy
    import tempfile
    import uuid

    test_dir = './test/data'
    test_data = os.path.join(test_dir, 'RAAM_TS21_ride_snippet.tcx')

    tl = ttl.TcxTrackList(test_data)
    print(f'tl len={len(tl)}:')
    tp.printList(tl)

    import unittest

    class TestCsv(unittest.TestCase):

        def test_save_and_read_csv(self: TestCsv):
            ele=1.0; lat=math.radians(2.0); lon=math.radians(3.0); brg=math.radians(4.0); idx=5; tot=6.0; dis=7.0
            slp=math.radians(8.0); spd=9.0; hrt=10.0; wts=11.0; rds=12.0; tim=13.0
            pt: tp.TrackPoint = tp.mkTrackPoint(ele=ele, lat=lat, lon=lon, brg=brg, idx=idx, tot=tot, dis=dis, \
                                                slp=slp, spd=spd, hrt=hrt, wts=wts, rds=rds, tim=tim)

            # Test CsvStrTrackList
            s1: str = f'{ele},{lat},{lon},{brg},{idx},{tot},{dis},{slp},{spd},{hrt},{wts},{rds},{tim}\r\n'
            tl1: List[tp.TrackPoint] = CsvStrTrackList(s1)
            print(f'pt:     {pt}');
            print(f'tl1[0]: {tl1[0]}');
            self.assertTrue(tl1[0] == pt)

            # Test writeTrackListAsCsvToStr
            s2: str =  writeTrackListAsCsvToStr(tl1)
            #print(f's1={s1}')
            #print(f's2={s2}')
            self.assertTrue(s1 == s2)

            # Test writeTrackListAsCsvToFile and CsvTrackList
            tempFileName: str = os.path.join(test_dir, 'TestCsv.temp.' + str(uuid.uuid4()) + '.csv')
            #print(f'tempFileName={tempFileName}')
            try:
                writeTrackListAsCsvToFile(tl1, tempFileName)
                tl2: List[tp.TrackPoint] = CsvTrackList(tempFileName)
                #print('tl1:'); tp.printList(tl1)
                #print('tl2:'); tp.printList(tl2)
                self.assertTrue(tp.compareList(tl1, tl2))
            finally:
                os.remove(tempFileName)

    unittest.main()
