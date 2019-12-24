#!/usr/bin/env python3

# bike power calculation
from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass

import math
import numpy as np
import xml.etree.ElementTree as et
import track_point as tp

def parse_simple_float_subElement(elem_float: et.Element, name: str) -> float:
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

    lat: float = 0.0
    lon: float = 0.0
    ele: float = 0.0

    #lat = parse_simple_float_subElement(elem, 'Position//{*}LatitudeDegrees')
    lat = parse_simple_float_subElement(elem, 'LatitudeDegrees')
    lon = parse_simple_float_subElement(elem, 'LongitudeDegrees')
    ele = parse_simple_float_subElement(elem, 'AltitudeMeters')
    hrt = parse_simple_float_subElement(elem, 'HeartRateBpm//{*}Value')
    spd = parse_simple_float_subElement(elem, 'Speed')
    wts = parse_simple_float_subElement(elem, 'Watts')

    return tp.TrackPoint(lat=lat, lon=lon, ele=ele, hrt=hrt, spd=spd, wts=wts)

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
        for elem_trkpt in root.findall('.//{*}Trackpoint'):
            p: Optional[tp.TrackPoint]
            p = parse_trackpoint(elem_trkpt)
            if p is not None:
                self.__track.append(p)

        # Build and index for each km
        km: float = 0
        if len(self.__track) > 1:
            prev: tp.TrackPoint
            for i, pt in enumerate(self.__track):
                pt.index = i
                if i == 0:
                    pt.total_distance = 0.0
                    pt.distance = 0.0
                    pt.slope = 0.0
                    pt.bearing = 0.0
                else:
                    dist: float = prev.distanceMeters(pt)
                    if dist< 0.0:
                        print(f'WARNING distance < 0.0 ??', end='')
                        print(f'  {filename} point[{i:>3}]: prev={prev} pt={pt} is {dist:<6.3f}')
                    pt.total_distance = prev.total_distance + dist
                    #print(f'{i} dist={dist} pt.total_distance={pt.total_distance}')
                    prev.distance = dist
                    prev.slope = prev.slopeRadians(pt)
                    prev.bearing = prev.bearingRadians(pt)

                # First point whose begining is >= km
                kmx: float = pt.total_distance / 1000.0
                if kmx >= km:
                    if (kmx == km):
                        self.__km_index_distance.append(KmIndexDistance(i, pt.total_distance))
                    else:
                        assert((i > 0) \
                                and (prev.total_distance < (km * 1000)) \
                                and (pt.total_distance > (km * 1000)))
                        self.__km_index_distance.append(KmIndexDistance(i - 1, prev.total_distance))
                    km += 1.0
                #print(f'{filename} point[{i:>3}]: {pt} is {distance:>6.3f} from prev, total is {total_distance:>11.3f}', end='')
                #print('')
                prev = pt

        last_index: int = 0
        total_distance: float = 0.0
        if len(self.__track) > 1:
            last_index = len(self.__track) - 1
            total_distance = self.__track[last_index].total_distance
        self.__km_index_distance.append(KmIndexDistance(last_index, total_distance))

        #print(f'total_distance={total_distance}')

        #kid: KmIndexDistance
        #for i, kid in enumerate(self.__km_index_distance):
        #    print(f'km[{i}]: index={kid.index:>3} distance={kid.distance:>11.3f} pt: {self.__track[kid.index]}')

    def total_distance(self: Path) -> float:
        """Return the total distance of the route"""
        return self.__km_index_distance[len(self.__km_index_distance) - 1].distance

    def getTrackPoint(self: Path, distance: float) -> Optional[tp.TrackPoint]:
        """Return the index into track of the point that includes the distance"""
        i: int = int(distance / 1000)
        if i >= 0 and i < len(self.__km_index_distance):
            kid: KmIndexDistance = self.__km_index_distance[i]
            pt: tp.TrackPoint
            j: int
            for j, pt in enumerate(self.__track[kid.index:], kid.index):
                # Two adjacent points could be the same point so we use <= for both cases
                if (pt.total_distance <= distance) and (distance <= (pt.total_distance + pt.distance)):
                    return pt;
        return None


    def slopeRadians(self: Path, distance: float) -> float:
        """
        Return the slope in radians of the route at distance

        Some day maybe use three points and interpolate slope??
        """

        pt: Optional[tp.TrackPoint] = self.getTrackPoint(distance)
        if pt is not None:
            return pt.slope
        else:
            return 0

    def track(self: Path) -> List[tp.TrackPoint]:
        return self.__track

    def km_index_distance(self: Path) -> List[KmIndexDistance]:
        return self.__km_index_distance

if __name__ == '__main__':
    test_data = './test/data/RAAM_TS21_ride_snippet.tcx'

    path = Path(test_data)
    print(f'total_distance={path.total_distance()}')

    t: List[tp.TrackPoint] = path.track()
    for i, pt in enumerate(t):
        print(f'pt[{i:>3}]={pt}')

    #import unittest

    #class TestGpx(unittest.TestCase):

    #    def test_CreatePath(self):
    #        path = Path(test_data)
    #        self.assertTrue(len(path.track()) != 0)
    #        self.assertTrue(len(path.km_index_distance()) > 1)

    #    def test_getTrackPoint(self):
    #        path: Path = Path(test_data)
    #        dist: float

    #        dist = -1
    #        pt: tp.TrackPoint
    #        pt = path.getTrackPoint(dist) # before beginning
    #        self.assertTrue(pt is None)

    #        dist = 0
    #        pt = path.getTrackPoint(dist)
    #        self.assertTrue(pt is not None)
    #        self.assertEqual(pt.index, 0)
    #        self.assertEqual(pt.total_distance, dist)
    #        self.assertTrue((pt.total_distance <= dist) and (dist <= (pt.total_distance + pt.distance)))

    #        dist = 1000
    #        pt = path.getTrackPoint(dist)
    #        self.assertTrue(pt is not None)
    #        self.assertEqual(pt.index, 17)
    #        self.assertTrue((pt.total_distance <= dist) and (dist <= (pt.total_distance + pt.distance)))

    #        dist = 1300
    #        pt = path.getTrackPoint(dist)
    #        self.assertTrue(pt is not None)
    #        self.assertEqual(pt.index, 21)
    #        self.assertTrue((pt.total_distance <= dist) and (dist <= (pt.total_distance + pt.distance)))

    #        # We get the penultimate point when asking for the point which contains the length ?
    #        # I'm not sure this is the "correct" answer but the last point has a distance, bearing
    #        # and slope of zero, so returning the penultimate point is not unreasonable.
    #        dist = path.total_distance()
    #        pt = path.getTrackPoint(dist)
    #        self.assertTrue(pt is not None)
    #        self.assertEqual(pt.index, len(path.track()) - 2)
    #        self.assertTrue((pt.total_distance <= dist) and (dist <= (pt.total_distance + pt.distance)))

    #        dist = path.total_distance() + 1.0
    #        pt = path.getTrackPoint(dist)
    #        self.assertTrue(pt is None)

    #unittest.main()
