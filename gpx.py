#!/usr/bin/env python3

# bike power calculation
from __future__ import annotations

import math
import numpy as np
import xml.etree.ElementTree as et
import track_point as tp

from typing import Optional, Tuple

def parse_trkpt(elem_trkpt: et.Element) -> Optional[tp.TrackPoint]:
    "Return lat, lon, ele"
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

class Route:
    """Provide access ot a route"""

    def __init__(self: Route, filename: str) -> None:
        elem_trkpt: et.Element
        tree = et.parse(filename)
        root: et.Element = tree.getroot()

        for elem_trkpt in root.findall('.//{*}trkpt'):
            pt = parse_trkpt(elem_trkpt)
            print(f'pt={pt}')

    def length(self: Route) -> float:
        """Return the total length of the route"""
        return 0.0

    def slope(self: Route, distance: float) -> float:
        """Return the slope of the route at distance"""
        return 0.0

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Display gpx trkpt's.")
    parser.add_argument('filename', type=str, help='gpx file to process')
    args = parser.parse_args()
    print(f'filename={args.filename}')

    Route(args.filename)
