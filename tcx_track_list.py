#!/usr/bin/env python3

# bike power calculation
from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass
from time import struct_time, strptime

import math
import numpy as np
import xml.etree.ElementTree as et
import track_point as tp

def parse_time_subElement(elem_time: et.Element, name: str) -> Optional[struct_time]:
    elem = elem_time.find('.//{*}' + name)
    val_time: Optional[struct_time]
    if elem is not None and elem.text:
        val_str: str = elem.text.strip()
        val_time = strptime(val_str, "%Y-%m-%dT%H:%M:%SZ")
    else:
        val_time = None
    return val_time

def parse_float_subElement(elem_float: et.Element, name: str) -> float:
    elem = elem_float.find('.//{*}' + name)
    val: str
    if elem is not None and elem.text:
        val = elem.text.strip()
        if val == '':
            val = '0.0'
    else:
        val = '0.0'
    return float(val)

def parse_trackpoint(elem: et.Element) -> Optional[tp.TrackPoint]:
    """Return PtData"""
    if not elem:
        return None

    tim: Optional[struct_time] = parse_time_subElement(elem, 'Time')
    lat: float = parse_float_subElement(elem, 'LatitudeDegrees')
    lon: float = parse_float_subElement(elem, 'LongitudeDegrees')
    ele: float = parse_float_subElement(elem, 'AltitudeMeters')
    hrt: float = parse_float_subElement(elem, 'HeartRateBpm//{*}Value')
    spd: float = parse_float_subElement(elem, 'Speed')
    wts: float = parse_float_subElement(elem, 'Watts')

    return tp.TrackPoint(lat=lat, lon=lon, ele=ele, hrt=hrt, spd=spd, wts=wts, tim=tim)

def TcxTrackList(filename: str) -> List[tp.TrackPoint]:
    """Create a List[tp.TrackPoint] which maybe empty if no trkpt's found"""

    # Create a list of TrackPoints
    track: List[tp.TrackPoint] = []
    elem: et.Element
    tree = et.parse(filename)
    root: et.Element = tree.getroot()
    for elem in root.findall('.//{*}Trackpoint'):
        p: Optional[tp.TrackPoint]
        p = parse_trackpoint(elem)
        if p is not None:
            track.append(p)

    return track

if __name__ == '__main__':
    test_data = './test/data/RAAM_TS21_ride_snippet.tcx'

    tl = TcxTrackList(test_data)
    print(f'len={len(tl)}')

    i: int
    pt: tp.TrackPoint
    for i, pt in enumerate(tl):
        print(f'pt[{i:>3}]={pt}')

    import unittest

    class TestTcx(unittest.TestCase):

        def test_TcxTrackList(self):
            tl = TcxTrackList(test_data)
            self.assertTrue(len(tl) != 0)

    unittest.main()
