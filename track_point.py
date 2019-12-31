#!/usr/bin/env python3

# Distance and bearing algorithms from https://www.movable-type.co.uk/scripts/latlong.html

from __future__ import annotations
from enum import Enum
from typing import Tuple, Optional, Any, List
from itertools import count

import math
import time
import calendar
import numpy as np

earthR1 = 6_371_008.7714

class Iterator:

    def __init__(self: Iterator, tp: TrackPoint, start: int = 0) -> None:
        self.cur = start
        self.tp = tp

    def __iter__(self: Iterator) -> Iterator:
        return self

    def __next__(self: Iterator) -> str:
        value: Any
        if (self.cur == 0):
            value = self.tp.idx
        elif (self.cur == 1):
            value = self.tp.ele
        elif (self.cur == 2):
            value = self.tp.lat
        elif (self.cur == 3):
            value = self.tp.lon
        elif (self.cur == 4):
            value = self.tp.brg
        elif (self.cur == 5):
            value = self.tp.tot
        elif (self.cur == 6):
            value = self.tp.dis
        elif (self.cur == 7):
            value = self.tp.slp
        elif (self.cur == 8):
            value = self.tp.spd
        elif (self.cur == 9):
            value = self.tp.hrt
        elif (self.cur == 10):
            value = self.tp.wts
        elif (self.cur == 11):
            value = self.tp.rds
        elif (self.cur == 12):
            value = self.tp.tim
        else:
            raise StopIteration
        self.cur += 1
        return str(value)

def mkTrackPoint(
    idx: int = 0,
    ele: float = 0.0,
    lat: float = 0.0,
    lon: float = 0.0,
    brg: float = 0.0,
    tot: float = 0.0,
    dis: float = 0.0,
    slp: float = 0.0,
    spd: float = 0.0,
    hrt: float = 0.0,
    wts: float = 0.0,
    rds: float = 0.0,
    tim: float = 0.0) -> TrackPoint:

    pt: TrackPoint = TrackPoint()
    pt.idx = idx
    pt.ele = ele
    pt.lat = lat
    pt.lon = lon
    pt.brg = brg
    pt.tot = tot
    pt.dis = dis
    pt.slp = slp
    pt.spd = spd
    pt.hrt = hrt
    pt.wts = wts
    pt.rds = rds
    pt.tim = tim

    return pt

def printList(tl: List[TrackPoint]) -> None:
    #print(f'len={len(tl)}')
    i: int
    pt: TrackPoint
    for i, pt in enumerate(tl):
        print(f'{i:>3} ', end='')
        if i is not None and pt is not None:
            print(f'pt[{i:>3}]={pt}')

def compareList(tl1: List[TrackPoint], tl2: List[TrackPoint]) -> bool:
    #print('tl1:'); printList(tl1)
    #print('tl2:'); printList(tl2)
    i: int
    pt1: TrackPoint
    pt2: TrackPoint

    if len(tl1) != len(tl2):
        #print(' --- False, len !=')
        return False
    for i, pt1, pt2 in zip(count(), tl1, tl2):
        if pt1 != pt2:
            #print(f' --- False, pt != at idx {i}')
            return False
    #print(' --- True')
    return True

class TrackPoint:

    def __init__(self: TrackPoint, lat: float=0.0, lon: float=0.0, ele: float=0.0, brg: float=None, dis: float=None, spd: float=0.0, hrt: float=0.0, wts: float=0.0, tim: float=0.0, rds: float=earthR1) -> None:
        """
        Create a new TrackPoint using either lat, lon and ele to define the point
        or if brg and dis are supplied then create a new TrackPoint which is located
        at brg and dis from a starting point at lat lon. Raises a ValueError if brg
        and dis are not both None or if one is None and the other is not.

        lat: Latitude in SignedDecDeg, +90 to -90
        lon: Longitude in SignedDecDeg, +180 to -180
        ele: Elevation in meters.
        brg: Bearing in SignedDecDeg from lat, lon to this new point (dis must be supplied)
        dis: Distance in meters from lat, lon to this new point (brg must be supplied)
        rds: Radius of sphere only used with when creating a new point using brg and dis
        """
        self.idx: int   = 0   # Index of this point
        self.ele: float = ele # Elevation
        self.lat: float = 0.0 # Latitude
        self.lon: float = 0.0 # Longitude
        self.brg: float = 0.0 # Bearing
        self.tot: float = 0.0 # Total distance in meters to this point
        self.dis: float = 0.0 # Distance in meters to next point
        self.slp: float = 0.0 # Slope in radians to next point
        self.spd: float = spd # Speed in meters/sec at this point
        self.hrt: float = hrt # Heart rate in beats/min at this point
        self.wts: float = wts # Watts at this point
        self.rds: float = rds # Radius of sphere
        self.tim: float = tim # Time at this point

        if (brg is not None) and (dis is not None):
            brg = math.radians(brg)
            lat = math.radians(lat)
            lon = math.radians(lon)
            self.lat = math.asin((math.sin(lat) * math.cos(dis/rds)) + \
                                 (math.cos(lat) * math.sin(dis/rds) * math.cos(brg)))
            self.lon = lon + math.atan2((math.sin(brg) * math.sin(dis/rds) * math.cos(lat)),
                                        (math.cos(dis/rds) - (math.sin(lat) * math.sin(self.lat))))
            self.brg = brg
        elif (brg is None) and (dis is None):
            self.lat = math.radians(lat)
            self.lon = math.radians(lon)
            self.brg = 0.0
        elif (brg is None):
            raise ValueError("brg is None but dis is not")
        else:
            raise ValueError("dis is None but brg is not")

    def __iter__(self: TrackPoint) -> Iterator:
        return Iterator(self)

    def __eq__(self: TrackPoint, other: Any) -> bool:
        #print(f'TrackPoint.__eq__: self={self} other={other}', end='')
        if not isinstance(other, TrackPoint):
            #print(' --- False')
            return False
        if self is other:
            #print(' --- True')
            return True
        result = (self.idx == other.idx) and \
                 (self.ele == other.ele) and \
                 (self.lat == other.lat) and \
                 (self.lon == other.lon) and \
                 (self.brg == other.brg) and \
                 (self.tot == other.tot) and \
                 (self.dis == other.dis) and \
                 (self.slp == other.slp) and \
                 (self.spd == other.spd) and \
                 (self.hrt == other.hrt) and \
                 (self.wts == other.wts) and \
                 (self.rds == other.rds) and \
                 (self.tim == other.tim)
        #print(f' --- {result}')
        return result

    def __str__(self: TrackPoint) -> str:
        lat, lon, brg, slp = self.decDegrees()
        return f"{{'lat': {lat:>+9.6f}, 'lon': {lon:>+9.6f}, 'ele': {self.ele:>9.3f}, 'tot': {self.tot:>9.3f}, 'dis': {self.dis:>6.3f}, 'slp': {slp:>+9.6f}, 'brg': {brg:>+9.6f}, 'spd': {self.spd:>6.3f}, 'hrt': {self.hrt:>4.1f}, 'wts': {self.wts:>6.2f}, 'tim': {self.tim}}}"

    def radians(self: TrackPoint) -> Tuple[float, float, float, float]:
        """Return lat, lon and brg as radians"""
        return self.lat, self.lon, self.brg, self.slp

    def decDegrees(self: TrackPoint) -> Tuple[float, float, float, float]:
        """Return lat, lon and brg as degrees"""
        return math.degrees(self.lat), math.degrees(self.lon), math.degrees(self.brg), math.degrees(self.slp)

    def disMeters(self: TrackPoint, other: TrackPoint, rds: float=earthR1) -> float:
        """Return dis between other and self in meters"""
        dLat_haversine = math.sin((other.lat - self.lat) / 2.0)
        dLon_haversine = math.sin((other.lon - self.lon) / 2.0)
        a = (dLat_haversine ** 2) + (math.cos(self.lat) * math.cos(other.lat) * (dLon_haversine ** 2.0))
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
        return rds * c

    def brgRadians(self: TrackPoint, other: TrackPoint) -> float:
        """Return bearing in degrees North = 0.0, East = 90.0, South = 180, West = -90"""
        y = math.sin(other.lon - self.lon) * math.cos(other.lat)
        x = (math.cos(self.lat) * math.sin(other.lat)) - \
                (math.sin(self.lat) * math.cos(other.lat) * math.cos(other.lat - self.lat))
        return math.atan2(y, x)

    def brgDeg(self: TrackPoint, other: TrackPoint) -> float:
        """Return bearing in degrees 0..360"""
        b = self.brgRadians(other)
        if (b < 0):
            return 360 + math.degrees(b)
        else:
            return math.degrees(b)

    def eleDiffMeters(self: TrackPoint, other: TrackPoint) -> float:
        """Eleveation difference between returns other.diff - self.diff"""
        return other.ele - self.ele

    def slpPercent(self: TrackPoint, other: TrackPoint) -> float:
        """Slope as a precentage positive for uphill and negative for downhill"""
        return (self.eleDiffMeters(other) / self.disMeters(other)) * 100.0

    def slpRadians(self: TrackPoint, other: TrackPoint) -> float:
        """Slope in radians, positive for uphill and negative for downhill"""
        return math.atan2(self.eleDiffMeters(other), self.disMeters(other))

if __name__ == '__main__':
    # Compare haversine with TrackPoint.dis
    import copy
    import timeit
    import haversine as hs

    # The reason these are slightly different is that
    # haversine computes radians(x2 - x1) where as
    # dis uses radians(x2) - radians(x1). The
    # advantage is that dis is about 15% faster
    # and the difference is in the noise:
    #   hs.haversine(pt1, pt2)=111178.14375531959
    #   perf=1.1505752360008046
    #       ptr1.dis(pt2)=111178.1437553196
    #   perf=0.9691372659999615

    hpt1: Tuple[float, float] = 1.0, 2.0
    hpt2: Tuple[float, float] = 1.0, 3.0
    hd: float = hs.haversine(hpt1, hpt2)
    print(f'hs.haversine(hpt1, hpt2)={hd}')
    #loops: int  = 1_000_000
    #print(f'perf={timeit.timeit("hs.haversine(hpt1, hpt2)", number=loops, globals=globals())}')

    pt1: TrackPoint = TrackPoint(lat=1.0, lon=2.0)
    pt2: TrackPoint = TrackPoint(lat=1.0, lon=3.0)
    d: float = pt1.disMeters(pt2)
    print(f'    ptr1.disMeters(pt2)={d}')
    #print(f'perf={timeit.timeit("pt1.disMeters(pt2)", number=loops, globals=globals())}')

    import unittest

    class TestTrackPoint(unittest.TestCase):

        def test_init_default(self: TestTrackPoint):
            pt = TrackPoint()
            self.assertEqual(pt.lat, 0.0)
            self.assertEqual(pt.lon, 0.0)
            self.assertEqual(pt.ele, 0.0)

        def test_init_by_position(self: TestTrackPoint):
            pt = TrackPoint(1.0, 2.0, 3.0)
            self.assertEqual(pt.lat, math.radians(1.0))
            self.assertEqual(pt.lon, math.radians(2.0))
            self.assertEqual(pt.ele, 3.0)

        def test_init_by_name(self: TestTrackPoint):
            pt = TrackPoint(lon=1.0, lat=2.0, ele=3.0)
            self.assertEqual(pt.lon, math.radians(1.0))
            self.assertEqual(pt.lat, math.radians(2.0))
            self.assertEqual(pt.ele, 3.0)

        def test_str(self: TestTrackPoint):
            pt = TrackPoint(lon=1.0, lat=2.0, ele=3.0)
            self.assertEqual(f'{pt}', '{\'lat\': +2.000000, \'lon\': +1.000000, \'ele\':     3.000, \'tot\':     0.000, \'dis\':  0.000, \'slp\': +0.000000, \'brg\': +0.000000, \'spd\':  0.000, \'hrt\':  0.0, \'wts\':   0.00, \'tim\': 0.0}')

        def test_radians(self: TestTrackPoint):
            pt = TrackPoint(lat=1.0, lon=2.0)
            lat, lon, brg, slp = pt.radians()
            self.assertEqual(lat, math.radians(1.0))
            self.assertEqual(lon, math.radians(2.0))
            self.assertEqual(brg, math.radians(0))
            self.assertEqual(slp, math.radians(0))

        def test_decDegrees(self: TestTrackPoint):
            pt = TrackPoint(lat=1.0, lon=2.0)
            lat, lon, brg, slp = pt.decDegrees()
            self.assertEqual(lat, 1.0)
            self.assertEqual(lon, 2.0)
            self.assertEqual(brg, math.radians(0))
            self.assertEqual(slp, math.radians(0))

        def test_dis_0(self: TestTrackPoint):
            pt1 = TrackPoint()
            pt2 = TrackPoint()
            d = pt1.disMeters(pt2)
            self.assertEqual(d, 0.0)

        def test_dis_non_0(self: TestTrackPoint):
            pt1 = TrackPoint(lat=1.0, lon=2.0)
            pt2 = TrackPoint(lat=1.0, lon=3.0)
            d = pt1.disMeters(pt2)
            self.assertEqual(round(d, 3), 111178.144)

        def test_bearing_0(self: TestTrackPoint):
            pt1 = TrackPoint(lat=0.0, lon=90.0)
            pt2 = TrackPoint(lat=1.0, lon=90.0)
            b = pt1.brgDeg(pt2)
            self.assertEqual(round(b, 3), 0.000)

        def test_bearing_90(self: TestTrackPoint):
            pt1 = TrackPoint(lat=0.0, lon=90.0)
            pt2 = TrackPoint(lat=0.0, lon=91.0)
            b = pt1.brgDeg(pt2)
            self.assertEqual(round(b, 3), 90.000)

        def test_bearing_180(self: TestTrackPoint):
            pt1 = TrackPoint(lat=1.0, lon=90.0)
            pt2 = TrackPoint(lat=0.0, lon=90.0)
            b = pt1.brgDeg(pt2)
            self.assertEqual(round(b, 3), 180.000)

        def test_bearing_270(self: TestTrackPoint):
            pt1 = TrackPoint(lat=0.0, lon=90.0)
            pt2 = TrackPoint(lat=0.0, lon=89.0)
            b = pt1.brgDeg(pt2)
            self.assertEqual(round(b, 3), 270.000)

        def test_eleDiffMeters_default_0(self: TestTrackPoint):
            pt1 = TrackPoint(lat=0.0, lon=90.0)
            pt2 = TrackPoint(lat=0.0, lon=89.0)
            d = pt1.eleDiffMeters(pt2)
            self.assertEqual(0.0, d)

        def test_eleDiffMeters_1(self: TestTrackPoint):
            pt1 = TrackPoint(lat=0.0, lon=90.0, ele=99.0)
            pt2 = TrackPoint(lat=0.0, lon=89.0, ele=100.0)
            d = pt1.eleDiffMeters(pt2)
            #print(f'eleDiffMeters_1: {d}')
            self.assertEqual(1.0, d)

        def test_eleDiffMeters_neg_1(self: TestTrackPoint):
            pt1 = TrackPoint(lat=0.0, lon=90.0, ele=100.0)
            pt2 = TrackPoint(lat=0.0, lon=89.0, ele=99.0)
            d = pt1.eleDiffMeters(pt2)
            #print(f'eleDiffMeters_neg_1: {d}')
            self.assertEqual(-1.0, d)

        def test_lat_lon_1deg_0_to_90(self: TestTrackPoint):
             #print("")
             pt1 = TrackPoint(lat=89.0, lon=0.0, ele=3.0)
             pt2 = TrackPoint(lat=90.0, lon=0.0, ele=3.0)
             a = pt1.disMeters(pt2)
             #print(f'a is {a}')
             self.assertEqual(round(a, 6), 111195.079734)

             pt1 = TrackPoint(lat=81.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=80.0, lon=2.0, ele=3.0)
             b = pt1.disMeters(pt2)
             #print(f'b is {b}')
             self.assertEqual(round(b, 6), 111195.079734)

             pt1 = TrackPoint(lat=71.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=70.0, lon=2.0, ele=3.0)
             c = pt1.disMeters(pt2)
             #print(f'c is {c}')
             self.assertEqual(round(c, 6), 111195.079734)

             pt1 = TrackPoint(lat=61.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=60.0, lon=2.0, ele=3.0)
             d = pt1.disMeters(pt2)
             #print(f'd is {d}')
             self.assertEqual(round(d, 6), 111195.079734)

             pt1 = TrackPoint(lat=51.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=50.0, lon=2.0, ele=3.0)
             e = pt1.disMeters(pt2)
             #print(f'e is {e}')
             self.assertEqual(round(e, 6), 111195.079734)

             pt1 = TrackPoint(lat=46.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=45.0, lon=2.0, ele=3.0)
             f = pt1.disMeters(pt2)
             #print(f'f is {f}')
             self.assertEqual(round(f, 6), 111195.079734)

             pt1 = TrackPoint(lat=41.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=40.0, lon=2.0, ele=3.0)
             s = pt1.disMeters(pt2)
             #print(f's is {s}')
             self.assertEqual(round(s, 6), 111195.079734)

             pt1 = TrackPoint(lat=31.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=30.0, lon=2.0, ele=3.0)
             u = pt1.disMeters(pt2)
             #print(f'u is {u}')
             self.assertEqual(round(u, 6), 111195.079734)

             pt1 = TrackPoint(lat=21.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=20.0, lon=2.0, ele=3.0)
             v = pt1.disMeters(pt2)
             #print(f'v is {v}')
             self.assertEqual(round(v, 6), 111195.079734)

             pt1 = TrackPoint(lat=11.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=10.0, lon=2.0, ele=3.0)
             w = pt1.disMeters(pt2)
             #print(f'w is {w}')
             self.assertEqual(round(w, 6), 111195.079734)

             pt1 = TrackPoint(lat=1.0, lon=2.0, ele=3.0)
             pt2 = TrackPoint(lat=0.0, lon=2.0, ele=3.0)
             x = pt1.disMeters(pt2)
             #print(f'x is {x}')
             self.assertEqual(round(x, 6), 111195.079734)

             pt1 = TrackPoint(lat=0.0, lon=-20.0, ele=3.0)
             pt2 = TrackPoint(lat=1.0, lon=-20.0, ele=3.0)
             y = pt1.disMeters(pt2)
             #print(f'y is {y}')
             self.assertEqual(round(y, 6), 111195.079734)

        def test_bearing_dis_exception_brg_not_None_dst_is_None(self: TestTrackPoint):
            self.assertRaises(ValueError, TrackPoint, lat=10.0, lon=20.0, ele=3.0, brg=15.0, dis=None)
            self.assertRaises(ValueError, TrackPoint, lat=10.0, lon=20.0, ele=3.0, brg=15.0)

        def test_bearing_dis_exception_brg_is_None_dst_is_not_None(self: TestTrackPoint):
            self.assertRaises(ValueError, TrackPoint, lat=10.0, lon=20.0, ele=3.0, brg=None, dis=1.0)
            self.assertRaises(ValueError, TrackPoint, lat=10.0, lon=20.0, ele=3.0, dis=1.0)

        def test_bearing_dis_same_point(self: TestTrackPoint):
             pt1 = TrackPoint(lat=10.0, lon=20.0, ele=3.0)
             pt2 = TrackPoint(lat=10.0, lon=20.0, ele=3.0, brg=15.0, dis=0.0)
             self.assertEqual(pt1.lat, pt2.lat)
             self.assertEqual(pt1.lon, pt2.lon)
             self.assertEqual(pt1.ele, pt2.ele)

        def test_bearing_dis_different_points(self: TestTrackPoint):
             pt1 = TrackPoint(lat=10.0, lon=20.0, ele=3.0)
             pt2 = TrackPoint(lat=11.0, lon=20.0, ele=3.0)
             dis = pt1.disMeters(pt2)
             bearing = pt1.brgRadians(pt2)
             pt3 = TrackPoint(lat=10.0, lon=20.0, ele=3.0, brg=bearing, dis=dis)
             self.assertEqual(pt2.lat, pt3.lat)
             self.assertEqual(pt2.lon, pt3.lon)
             self.assertEqual(pt2.ele, pt3.ele)

        def test_makeTrackPoint(self: TestTrackPoint):
            pt: TrackPoint = mkTrackPoint()
            self.assertEqual(pt.idx, 0)
            self.assertEqual(pt.ele, 0.0)
            self.assertEqual(pt.lat, 0.0)
            self.assertEqual(pt.lon, 0.0)
            self.assertEqual(pt.brg, 0.0)
            self.assertEqual(pt.tot, 0.0)
            self.assertEqual(pt.dis, 0.0)
            self.assertEqual(pt.slp, 0.0)
            self.assertEqual(pt.spd, 0.0)
            self.assertEqual(pt.hrt, 0.0)
            self.assertEqual(pt.wts, 0.0)
            self.assertEqual(pt.rds, 0.0)
            self.assertEqual(pt.tim, 0.0)

        def test_makeTrackPointNonZero(self: TestTrackPoint):
            pt: TrackPoint = mkTrackPoint(idx=1, ele=2, lat=3, lon=4, brg=5, tot=6, dis=7,
                                          slp=8, spd=9, hrt=10, wts=11, rds=12, tim=13)
            self.assertEqual(pt.idx, 1)
            self.assertEqual(pt.ele, 2.0)
            self.assertEqual(pt.lat, 3.0)
            self.assertEqual(pt.lon, 4.0)
            self.assertEqual(pt.brg, 5.0)
            self.assertEqual(pt.tot, 6.0)
            self.assertEqual(pt.dis, 7.0)
            self.assertEqual(pt.slp, 8.0)
            self.assertEqual(pt.spd, 9.0)
            self.assertEqual(pt.hrt, 10.0)
            self.assertEqual(pt.wts, 11.0)
            self.assertEqual(pt.rds, 12.0)
            self.assertEqual(pt.tim, 13.0)

        def test_iterator(self: TestTrackPoint):
            idx=1; ele=2; lat=3; lon=4; brg=5; tot=6; dis=7; slp=8; spd=9; hrt=10; wts=11; rds=12; tim=13
            pt: TrackPoint = mkTrackPoint(idx=idx, ele=ele, lat=lat, lon=lon, brg=brg, tot=tot, \
                                          dis=dis, slp=slp, spd=spd, hrt=hrt, wts=wts, rds=rds, tim=tim)
            i: int
            f: Any
            for i, f in enumerate(pt):
                if (i == 0):
                    self.assertEqual(f, str(idx))
                elif (i == 1):
                    self.assertEqual(f, str(ele))
                elif (i == 2):
                    self.assertEqual(f, str(lat))
                elif (i == 3):
                    self.assertEqual(f, str(lon))
                elif (i == 4):
                    self.assertEqual(f, str(brg))
                elif (i == 5):
                    self.assertEqual(f, str(tot))
                elif (i == 6):
                    self.assertEqual(f, str(dis))
                elif (i == 7):
                    self.assertEqual(f, str(slp))
                elif (i == 8):
                    self.assertEqual(f, str(spd))
                elif (i == 9):
                    self.assertEqual(f, str(hrt))
                elif (i == 10):
                    self.assertEqual(f, str(wts))
                elif (i == 11):
                    self.assertEqual(f, str(rds))
                elif (i == 12):
                    self.assertEqual(f, str(tim))

        def test_eq(self: TestTrackPoint):
            idx=1; ele=2; lat=3; lon=4; brg=5; tot=6; dis=7; slp=8; spd=9; hrt=10; wts=11; rds=12; tim=13
            pt1: TrackPoint = mkTrackPoint(idx=idx, ele=ele, lat=lat, lon=lon, brg=brg, tot=tot, \
                                          dis=dis, slp=slp, spd=spd, hrt=hrt, wts=wts, rds=rds, tim=tim)

            self.assertFalse(pt1 == 1)
            self.assertTrue(pt1 == pt1)
            pt2: TrackPoint = copy.deepcopy(pt1)
            self.assertTrue(pt1 == pt2)
            self.assertTrue(pt2 == pt1)
            pt2.tot = pt1.tot + 1
            self.assertTrue(pt1 != pt2)
            self.assertTrue(pt2 != pt1)
            pt2.tot = pt1.tot
            self.assertTrue(pt1 == pt2)
            self.assertTrue(pt2 == pt1)

        def test_compareList(self: TestTrackPoint):
            idx=1; ele=2; lat=3; lon=4; brg=5; tot=6; dis=7; slp=8; spd=9; hrt=10; wts=11; rds=12; tim=13
            pt1: TrackPoint = mkTrackPoint(idx=idx, ele=ele, lat=lat, lon=lon, brg=brg, tot=tot, \
                                          dis=dis, slp=slp, spd=spd, hrt=hrt, wts=wts, rds=rds, tim=tim)

            pt2: TrackPoint = copy.deepcopy(pt1)
            pt2.tot = pt1.tot + 1

            tl1: List[TrackPoint] = [pt1, pt1]
            tl2: List[TrackPoint] = [pt1, pt2]
            tl3: List[TrackPoint] = [pt2, pt1]

            self.assertTrue(compareList(tl1, tl1))
            self.assertTrue(compareList(tl2, tl2))
            self.assertTrue(compareList(tl3, tl3))

            self.assertFalse(compareList(tl1, tl2))
            self.assertFalse(compareList(tl2, tl1))

            self.assertFalse(compareList(tl1, tl3))
            self.assertFalse(compareList(tl3, tl1))

    unittest.main()
