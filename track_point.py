#!/usr/bin/env python3
# Distance and bearing algorithms from https://www.movable-type.co.uk/scripts/latlong.html

import math
import numpy as np
from enum import Enum

earthR1 = 6_371_008.7714

class TrackPoint:

    def __init__(self, lat=0.0, lon=0.0, ele=0.0):
        """
        lat: Latitude in SignedDecDeg, +90 to -80
        lon: Longitude in SignedDecDeg, +180 to -180
        ele: Elevation in meters.
        """
        self.lat = math.radians(lat)
        self.lon = math.radians(lon)
        self.ele = ele

    #def __init__(self, sLat, sLon, brg, dis, ele=0.0, radius=earthR1):
    #    """
    #    sLat: starting Latitude in SignedDecDeg, +90 to -80
    #    sLon: starting Longitude in SignedDecDeg, +180 to -180
    #    brg: Bearing in SignedDecDeg
    #    dis: Distance from lat, lon to new point
    #    ele: Elevation in meters.
    #    radius: Radius of the sphere
    #    """
    #    brgRadians = math.radians(brg)
    #    lat = math.radians(sLat)
    #    lon = math.radians(sLon)
    #    self.lat = math.asin((math.sin(lat) * math.cos(dis/radius)) + \
    #                         (math.cos(lat) * math.sin(dis/radius) * math.cos(brgRadians)))
    #    self.lon = lat + math.atan2((math.sin(brgRadians) * math.sin(d/radius) * math.cos(lat)),
    #                                (math.cos(d/radius) - math.sin(lat) * math.sin(self.lat)))
    #    self.ele = ele

    def __str__(self):
        lat, lon = self.signedDecDegs()
        return f"{{'lat': {lat}, 'lon': {lon}, 'ele': {self.ele}}}"


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
        """Return bearing in degrees North = 0.0, East = 90.0, South = 180, West = -90"""
        y = math.sin(other.lon - self.lon) * math.cos(other.lat)
        x = (math.cos(self.lat) * math.sin(other.lat)) - \
                (math.sin(self.lat) * math.cos(other.lat) * math.cos(other.lat - self.lat))
        return math.degrees(math.atan2(y, x))

    def bearing360(self, other):
        """Return bearing in degrees 0..360"""
        b = self.bearing(other)
        if (b < 0):
            return 360 + b
        else:
            return b

    def eleDiff(self, other):
        """Eleveation difference between returns other.diff - self.diff"""
        return other.ele - self.ele

    def slopePercent(self, other):
        """Slope as a precentage positive for uphill and negative for downhill"""
        return (self.eleDiff(other) / self.distance(other)) * 100.0

    def slopeRadians(self, other):
        """Slope in radians, positive for uphill and negative for downhill"""
        return math.atan2(self.eleDiff(other), self.distance(other))

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
    #print(f'perf={timeit.timeit("hs.haversine(pt1, pt2)", number=loops, globals=globals())}')

    pt1 = TrackPoint(lat=1.0, lon=2.0)
    pt2 = TrackPoint(lat=1.0, lon=3.0)
    d = pt1.distance(pt2)
    print(f'    ptr1.distance(pt2)={d}')
    #print(f'perf={timeit.timeit("pt1.distance(pt2)", number=loops, globals=globals())}')

    import unittest

    class TestTrackPoint(unittest.TestCase):

        def test_init_default(self):
            pt = TrackPoint()
            self.assertEqual(pt.lat, 0.0)
            self.assertEqual(pt.lon, 0.0)
            self.assertEqual(pt.ele, 0.0)

        def test_init_by_position(self):
            pt = TrackPoint(1.0, 2.0, 3.0)
            self.assertEqual(pt.lat, math.radians(1.0))
            self.assertEqual(pt.lon, math.radians(2.0))
            self.assertEqual(pt.ele, 3.0)

        def test_init_by_name(self):
            pt = TrackPoint(lon=1.0, lat=2.0, ele=3.0)
            self.assertEqual(pt.lon, math.radians(1.0))
            self.assertEqual(pt.lat, math.radians(2.0))
            self.assertEqual(pt.ele, 3.0)

        def test_str(self):
            pt = TrackPoint(lon=1.0, lat=2.0, ele=3.0)
            self.assertEqual(f'{pt}', '{\'lat\': 2.0, \'lon\': 1.0, \'ele\': 3.0}')

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

        def test_eleDiff_default_0(self):
            pt1 = TrackPoint(lat=0.0, lon=90.0)
            pt2 = TrackPoint(lat=0.0, lon=89.0)
            d = pt1.eleDiff(pt2)
            self.assertEqual(0.0, d)

        def test_eleDiff_1(self):
            pt1 = TrackPoint(lat=0.0, lon=90.0, ele=99.0)
            pt2 = TrackPoint(lat=0.0, lon=89.0, ele=100.0)
            d = pt1.eleDiff(pt2)
            #print(f'eleDiff_1: {d}')
            self.assertEqual(1.0, d)

        def test_eleDiff_neg_1(self):
            pt1 = TrackPoint(lat=0.0, lon=90.0, ele=100.0)
            pt2 = TrackPoint(lat=0.0, lon=89.0, ele=99.0)
            d = pt1.eleDiff(pt2)
            #print(f'eleDiff_neg_1: {d}')
            self.assertEqual(-1.0, d)

        def test_lat_lon_1deg_0_to_90(self):
             #print("")
             pt1 = TrackPoint(lat=89.0, lon=0.0, ele=3.0)
             pt2 = TrackPoint(lat=90.0, lon=0.0, ele=3.0)
             a = pt1.distance(pt2)
             #print(f'a is {a}')
             self.assertEqual(round(a, 6), 111195.079734)

             pt1 = TrackPoint(lat=81.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=80.0, lon=2.0, ele=3.0)
             b = pt1.distance(pt2)
             #print(f'b is {b}')
             self.assertEqual(round(b, 6), 111195.079734)

             pt1 = TrackPoint(lat=71.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=70.0, lon=2.0, ele=3.0)
             c = pt1.distance(pt2)
             #print(f'c is {c}')
             self.assertEqual(round(c, 6), 111195.079734)

             pt1 = TrackPoint(lat=61.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=60.0, lon=2.0, ele=3.0)
             d = pt1.distance(pt2)
             #print(f'd is {d}')
             self.assertEqual(round(d, 6), 111195.079734)

             pt1 = TrackPoint(lat=51.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=50.0, lon=2.0, ele=3.0)
             e = pt1.distance(pt2)
             #print(f'e is {e}')
             self.assertEqual(round(e, 6), 111195.079734)

             pt1 = TrackPoint(lat=46.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=45.0, lon=2.0, ele=3.0)
             f = pt1.distance(pt2)
             #print(f'f is {f}')
             self.assertEqual(round(f, 6), 111195.079734)

             pt1 = TrackPoint(lat=41.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=40.0, lon=2.0, ele=3.0)
             s = pt1.distance(pt2)
             #print(f's is {s}')
             self.assertEqual(round(s, 6), 111195.079734)

             pt1 = TrackPoint(lat=31.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=30.0, lon=2.0, ele=3.0)
             u = pt1.distance(pt2)
             #print(f'u is {u}')
             self.assertEqual(round(u, 6), 111195.079734)

             pt1 = TrackPoint(lat=21.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=20.0, lon=2.0, ele=3.0)
             v = pt1.distance(pt2)
             #print(f'v is {v}')
             self.assertEqual(round(v, 6), 111195.079734)

             pt1 = TrackPoint(lat=11.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=10.0, lon=2.0, ele=3.0)
             w = pt1.distance(pt2)
             #print(f'w is {w}')
             self.assertEqual(round(w, 6), 111195.079734)

             pt1 = TrackPoint(lat=1.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=0.0, lon=2.0, ele=3.0)
             x = pt1.distance(pt2)
             #print(f'x is {x}')
             self.assertEqual(round(x, 6), 111195.079734)

             pt1 = TrackPoint(lat=0.0, lon=-20.0, ele=3.0)
             pt2 = TrackPoint(lat=1.0, lon=-20.0, ele=3.0)
             y = pt1.distance(pt2)
             #print(f'y is {y}')
             self.assertEqual(round(y, 6), 111195.079734)

    unittest.main()
