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

@dataclass
class KmIndexDistance:
    index: int
    distance: float

class Path:
    """Provide access to a path, a list of TrackPoints"""

    def __init__(self: Path, filename: str) -> None:
        # List of TrackPoints in this route
        self.__track: List[tp.TrackPoint] = []

        # List of KmIndexDistance with the last entrying being
        # the total distance
        self.__km_index_distance: List[KmIndexDistance] = []
        pt: tp.TrackPoint
        i: int

        elem_trkpt: et.Element
        tree = et.parse(filename)
        root: et.Element = tree.getroot()

        # Create a list of TrackPoints
        for elem_trkpt in root.findall('.//{*}trkpt'):
            p: Optional[tp.TrackPoint]
            p = parse_trkpt(elem_trkpt)
            if p is not None:
                self.__track.append(p)

        # Build and index for each km
        total_distance: float = 0.0
        km: float = 0
        if len(self.__track) > 1:
            distance: float
            prev: tp.TrackPoint
            for i, pt in enumerate(self.__track):
                if i == 0:
                    distance = 0.0
                else:
                    distance = prev.distance(pt)
                total_distance += distance
                if (total_distance / 1000.0) >= km:
                    self.__km_index_distance.append(KmIndexDistance(i, total_distance))
                    km += 1.0
                #print(f'{filename} point[{i:>3}]: {pt} is {distance:>6.3f} from prev, total is {total_distance:>11.3f}', end='')
                #if distance < 0.0:
                #    print(f'WARNING distance < 0.0 ??')
                #print('')
                if distance < 0.0:
                    print(f'WARNING distance < 0.0 ??')
                    print(f'  {filename} point[{i:>3}]: {pt} is {distance:>6.3f} from prev, total is {total_distance:>11.3f}', end='')
                prev = pt
        else:
            total_distance = 0.0
        self.__km_index_distance.append(KmIndexDistance(i, total_distance))
        #print(f'total_distance={total_distance}')

        #for i, pt in enumerate(self.__track):
        #    print(f'pt[{i:>3}]={pt}', end='')
        #    if i < len(self.__track) - 1:
        #        first_point = self.__track[i]
        #        second_point = self.__track[i+1]
        #        percent = first_point.slopePercent(second_point)
        #        degrees = math.degrees(first_point.slopeRadians(second_point))
        #        print(f' slope: {percent:>+5.3f}% {degrees:>+5.3f}degs', end='')
        #    print('')

        #kid: KmIndexDistance
        #for i, kid in enumerate(self.__km_index_distance):
        #    print(f'km[{i}]: index={kid.index:>3} distance={kid.distance:>11.3f} pt: {self.__track[kid.index]}')

    def total_distance(self: Path) -> float:
        """Return the total distance of the route"""
        return self.__km_index_distance[len(self.__km_index_distance) - 1].distance

    def slopePercent(self: Path, distance: float) -> float:
        """Return the slope as percentage of the route at distance"""

        i: int = int(distance / 1000)
        if i >= 0 and i < len(self.__km_index_distance):
            first_point = self.__track[self.__km_index_distance[i].index]
            second_point = self.__track[self.__km_index_distance[i + 1].index]
            return first_point.slopePercent(second_point)
        else:
            return 0.0

    def slopeRadians(self: Path, distance: float) -> float:
        """Return the slope as percentage of the route at distance"""

        i: int = int(distance / 1000)
        if i >= 0 and i < len(self.__km_index_distance):
            first_point = self.__track[self.__km_index_distance[i].index]
            second_point = self.__track[self.__km_index_distance[i + 1].index]
            return first_point.slopeRadians(second_point)
        else:
            return 0.0

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Display gpx trkpt's.")
    parser.add_argument('filename', type=str, help='gpx file to process')
    args = parser.parse_args()
    print(f'filename={args.filename}')

    path = Path(args.filename)
    print(f'total_distance={path.total_distance()}')
