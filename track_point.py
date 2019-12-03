#!/usr/bin/env python3

# bike power calculation
import math
import numpy as np

earthR1 = 6_371_008.7714
print(f'earthR1={earthR1}')

class TrackPoint:
    """
    Latitude and longitude of a point on a
    sphere in decimal degrees.
    """
    def __init__(self, lat=0.0, lon=0.0):
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return f"{{'lat': {self.lat}, 'lon': {self.lon}}}"


    def radians(self):
        """Return lat, lon as radians"""
        return math.radians(self.lat), math.radians(self.lon)

    def deltasAsRadians(self, other):
        """
        Return self.lat - othe.lat, self.lon - other.lon
        each as radians
        """
        return math.radians(self.lat - other.lat), \
                math.radians(self.lon - other.lon)

    def distanceInMeters(self, other):
        """Return distance between other and self in meters"""
        lat, lon = self.radians(other)
        deltaLat, deltaLon = self.deltasAsRadians(other)
        return 0.0

if __name__ == '__main__':
    import unittest

    class TestTrackPoint(unittest.TestCase):
        def test_init_default(self):
            pt = TrackPoint()
            self.assertEqual(pt.lat, 0.0)
            self.assertEqual(pt.lon, 0.0)

        def test_init_by_position(self):
            pt = TrackPoint(1.0, 2.0)
            self.assertEqual(pt.lat, 1.0)
            self.assertEqual(pt.lon, 2.0)

        def test_init_by_name(self):
            pt = TrackPoint(lon=1.0, lat=2.0)
            self.assertEqual(pt.lon, 1.0)
            self.assertEqual(pt.lat, 2.0)

        def test_str(self):
            pt = TrackPoint(lon=1.0, lat=2.0)
            self.assertEqual(f'{pt}', '{\'lat\': 2.0, \'lon\': 1.0}')

        def test_radians(self):
            pt = TrackPoint(lat=1.0, lon=2.0)
            lat, lon = pt.radians()
            self.assertEqual(lat, math.radians(1.0))
            self.assertEqual(lon, math.radians(2.0))

        def test_deltasAsRadians(self):
            pt1 = TrackPoint(lat=1.0, lon=2.0)
            pt2 = TrackPoint(lat=1.0, lon=3.0)
            dLat, dLon = pt1.deltasAsRadians(pt2)
            self.assertEqual(dLat, math.radians(pt1.lat - pt2.lat))
            self.assertEqual(dLon, math.radians(pt1.lon - pt2.lon))

    unittest.main()

