#!/usr/bin/env python3

# bike power calculation
from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass

import math
import numpy as np
import xml.etree.ElementTree as et
import track_point as tp


def parse_trkpt(elem_trkpt: et.Element) -> Optional[tp.TrackPoint]:
    "Return TrackPointo or None"
    lat_str: str = ''
    lon_str: str = ''

    if not elem_trkpt:
        return None

    if elem_trkpt.attrib:
        lat_str = elem_trkpt.attrib['lat']
        lon_str = elem_trkpt.attrib['lon']
        if not (lat_str and lon_str):
            return None
    else:
        return None

    elem_ele = elem_trkpt.find('.//{*}ele')
    ele_str: str
    if elem_ele is not None and elem_ele.text:
        ele_str = elem_ele.text.strip()
        if ele_str == '':
            ele_str = '0.0'
    else:
        ele_str = '0.0'

    return tp.TrackPoint(lat=float(lat_str), lon=float(lon_str), ele=float(ele_str))

def GpxTrackList(filename: str) -> List[tp.TrackPoint]:
    """Create a List[tp.TrackPoint] which maybe empty if no trkpt's found"""

    # Create a list of TrackPoints
    track: List[tp.TrackPoint] = []
    elem: et.Element
    tree = et.parse(filename)
    root: et.Element = tree.getroot()
    for elem in root.findall('.//{*}trkpt'):
        p: Optional[tp.TrackPoint]
        p = parse_trkpt(elem)
        if p is not None:
            track.append(p)

    return track

if __name__ == '__main__':
    test_data = './test/data/RAAM_TS00_route_snippet.gpx'

    tl = GpxTrackList(test_data)
    print(f'len={len(tl)}')

    i: int
    pt: tp.TrackPoint
    for i, pt in enumerate(tl):
        print(f'pt[{i:>3}]={pt}')

    import unittest

    class TestGpx(unittest.TestCase):

        def test_GpxTrackList(self):
            tl = GpxTrackList(test_data)
            self.assertTrue(len(tl) != 0)

    unittest.main()
