#!/usr/bin/env python3
# Distance and bearing algorithms from https://www.movable-type.co.uk/scripts/latlong.html

import math
import numpy as np
from enum import Enum

earthR1 = 6_371_008.7714

class TrackPointTypes(Enum):
    SignedDecDeg=1
    Radians=2

class TrackPoint:
    """
    Latitude and longitude of a point on a
    sphere in decimal degrees.
    """
    def __init__(self, lat=0.0, lon=0.0, format=TrackPointTypes.SignedDecDeg):
        if format == TrackPointTypes.SignedDecDeg:
            self.lat = math.radians(lat)
            self.lon = math.radians(lon)
        elif format == TrackPointTypes.Radians:
            self.lat = lat
            self.lon = lon
        else:
            print("Fatal error: {format} not recognized")

    def __str__(self):
        lat, lon = self.signedDecDegs()
        return f"{{'lat': {lat}, 'lon': {lon}}}"


    def radians(self):
        """Return lat, lon as radians"""
        return self.lat, self.lon

    def signedDecDegs(self):
        """Return lat, lon as radians"""
        return math.degrees(self.lat), math.degrees(self.lon)

    def distance(self, other, radius=earthR1):
        """Return distance between other and self in meters"""
        dLat_haversine = math.sin((other.lat - self.lat) / 2.0)
        dLon_haversine = math.sin((other.lon - self.lon) / 2.0)
        a = (dLat_haversine ** 2) + (math.cos(self.lat) * math.cos(other.lat) * (dLon_haversine ** 2.0))
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
        return radius * c

    def bearing(self, other):
        """Return bearing in degrees"""
        y = math.sin(other.lon - self.lon) * math.cos(other.lat)
        x = (math.cos(self.lat) * math.sin(other.lat)) - \
                (math.sin(self.lat) * math.cos(other.lat) * math.cos(other.lat - self.lat))
        return math.degrees(math.atan2(y, x))

    def bearing360(self, other):
        """Return bearing in degrees"""
        b = self.bearing(other)
        if (b < 0):
            return 360 + b
        else:
            return b

if __name__ == '__main__':
    # Compare haversine with TrackPoint.distance
    import timeit
    import haversine as hs

    # The reason these are slightly different is that
    # haversine computes radians(x2 - x1) where as
    # distance uses radians(x2) - radians(x1). The
    # advantage is that distance is about 15% faster
    # and the difference is in the noise:
    #   hs.haversine(pt1, pt2)=111178.14375531959
    #   perf=1.1505752360008046
    #       ptr1.distance(pt2)=111178.1437553196
    #   perf=0.9691372659999615

    pt1 = [1.0, 2.0]
    pt2 = [1.0, 3.0]
    d = hs.haversine(pt1, pt2)
    loops  = 1_000_000
    print(f'hs.haversine(pt1, pt2)={d}')
    print(f'perf={timeit.timeit("hs.haversine(pt1, pt2)", number=loops, globals=globals())}')

    pt1 = TrackPoint(lat=1.0, lon=2.0)
    pt2 = TrackPoint(lat=1.0, lon=3.0)
    d = pt1.distance(pt2)
    print(f'    ptr1.distance(pt2)={d}')
    print(f'perf={timeit.timeit("pt1.distance(pt2)", number=loops, globals=globals())}')

    import unittest

    class TestTrackPoint(unittest.TestCase):
        def test_init_default(self):
            pt = TrackPoint()
            self.assertEqual(pt.lat, 0.0)
            self.assertEqual(pt.lon, 0.0)

        def test_init_by_position(self):
            pt = TrackPoint(1.0, 2.0)
            self.assertEqual(pt.lat, math.radians(1.0))
            self.assertEqual(pt.lon, math.radians(2.0))

        def test_init_by_name(self):
            pt = TrackPoint(lon=1.0, lat=2.0)
            self.assertEqual(pt.lon, math.radians(1.0))
            self.assertEqual(pt.lat, math.radians(2.0))

        def test_str(self):
            pt = TrackPoint(lon=1.0, lat=2.0)
            self.assertEqual(f'{pt}', '{\'lat\': 2.0, \'lon\': 1.0}')

        def test_radians(self):
            pt = TrackPoint(lat=1.0, lon=2.0)
            lat, lon = pt.radians()
            self.assertEqual(lat, math.radians(1.0))
            self.assertEqual(lon, math.radians(2.0))

        def test_signedDecDegs(self):
            pt = TrackPoint(lat=1.0, lon=2.0)
            lat, lon = pt.signedDecDegs()
            self.assertEqual(lat, 1.0)
            self.assertEqual(lon, 2.0)

        def test_distance_0(self):
            pt1 = TrackPoint()
            pt2 = TrackPoint()
            d = pt1.distance(pt2)
            self.assertEqual(d, 0.0)

        def test_distance_non_0(self):
            pt1 = TrackPoint(lat=1.0, lon=2.0)
            pt2 = TrackPoint(lat=1.0, lon=3.0)
            d = pt1.distance(pt2)
            self.assertEqual(round(d, 3), 111178.144)

        def test_bearing_0(self):
            pt1 = TrackPoint(lat=0.0, lon=90.0)
            pt2 = TrackPoint(lat=1.0, lon=90.0)
            b = pt1.bearing(pt2)
            self.assertEqual(round(b, 3), 0.000)

        def test_bearing_90(self):
            pt1 = TrackPoint(lat=0.0, lon=90.0)
            pt2 = TrackPoint(lat=0.0, lon=91.0)
            b = pt1.bearing(pt2)
            self.assertEqual(round(b, 3), 90.000)

        def test_bearing_180(self):
            pt1 = TrackPoint(lat=1.0, lon=90.0)
            pt2 = TrackPoint(lat=0.0, lon=90.0)
            b = pt1.bearing(pt2)
            self.assertEqual(round(b, 3), 180.000)

        def test_bearing_270(self):
            pt1 = TrackPoint(lat=0.0, lon=90.0)
            pt2 = TrackPoint(lat=0.0, lon=89.0)
            b = pt1.bearing(pt2)
            self.assertEqual(round(b, 3), -90.000)
            b = pt1.bearing360(pt2)
            self.assertEqual(round(b, 3), 270.000)

    unittest.main()
