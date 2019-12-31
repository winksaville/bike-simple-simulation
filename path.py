#!/usr/bin/env python3

# bike power calculation
from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass

import track_point as tp
import gpx_track_list as gpx_tl

@dataclass
class KmIdxDis:
    idx: int
    dis: float

class Path:
    """Provide access to a path, a list of TrackPoints"""

    def __init__(self: Path, tl: List[tp.TrackPoint]) -> None:
        # List of TrackPoints in this route
        self.__track_list: List[tp.TrackPoint] = tl

        # List of KmIdxDis with the last entrying being
        # the total distance
        self.__km_idx_dis: List[KmIdxDis] = []
        pt: tp.TrackPoint
        i: int

        # Build and index for each km
        km: float = 0
        if len(self.__track_list) > 1:
            prev: tp.TrackPoint
            for i, pt in enumerate(self.__track_list):
                pt.idx = i
                if i == 0:
                    pt.tot = 0.0
                    pt.dis = 0.0
                    pt.slp = 0.0
                    pt.brg = 0.0
                else:
                    distance: float = prev.disMeters(pt)
                    if distance< 0.0:
                        print(f'WARNING distance < 0.0 at point[{i:>3}]: prev={prev} pt={pt} is {distance:<6.3f}')
                    pt.tot = prev.tot + distance
                    #print(f'{i} distance={distance} pt.tot={pt.tot}')
                    prev.dis = distance
                    prev.slp = prev.slpRadians(pt)
                    prev.brg = prev.brgRadians(pt)

                # First point whose begining is >= km
                kmx: float = pt.tot / 1000.0
                if kmx >= km:
                    if (kmx == km):
                        self.__km_idx_dis.append(KmIdxDis(i, pt.tot))
                    else:
                        assert((i > 0) \
                                and (prev.tot < (km * 1000)) \
                                and (pt.tot > (km * 1000)))
                        self.__km_idx_dis.append(KmIdxDis(i - 1, prev.tot))
                    km += 1.0
                #print(f'{filename} point[{i:>3}]: {pt} is {distance:>6.3f} from prev, total is {tot:>11.3f}', end='')
                #print('')
                prev = pt

        last_index: int = len(self.__track_list) - 1
        tot: float = self.__track_list[last_index].tot
        self.__km_idx_dis.append(KmIdxDis(last_index, tot))
        #print(f'tot={tot}')

        #kid: KmIdxDis
        #for i, kid in enumerate(self.__km_idx_dis):
        #    print(f'km[{i}]: idx={kid.idx:>3} distance={kid.dis:>11.3f} pt: {self__track_list[kid.idx]}')

    def tot(self: Path) -> float:
        """Return the total distance of the route"""
        return self.__km_idx_dis[len(self.__km_idx_dis) - 1].dis

    def getTrackPoint(self: Path, distance: float) -> Optional[tp.TrackPoint]:
        """Return the index into track of the point that includes the distance"""
        i: int = int(distance / 1000)
        if i >= 0 and i < len(self.__km_idx_dis):
            kid: KmIdxDis = self.__km_idx_dis[i]
            pt: tp.TrackPoint
            j: int
            for j, pt in enumerate(self.__track_list[kid.idx:], kid.idx):
                # Two adjacent points could be the same point so we use <= for both cases
                if (pt.tot <= distance) and (distance <= (pt.tot + pt.dis)):
                    return pt;
        return None

    def slpRadians(self: Path, distance: float) -> float:
        """
        Return the slope in radians of the route at distance

        Some day maybe use three points and interpolate slope??
        """

        pt: Optional[tp.TrackPoint] = self.getTrackPoint(distance)
        if pt is not None:
            return pt.slp
        else:
            return 0

    def trackList(self: Path) -> List[tp.TrackPoint]:
        return self.__track_list

    def km_idx_dis(self: Path) -> List[KmIdxDis]:
        return self.__km_idx_dis

    def compare(self: Path, other: Path) -> bool:
        return tp.compareList(self.trackList(), other.trackList())

if __name__ == '__main__':
    gpx_test_file = './test/data/RAAM_TS00_route_snippet.gpx'

    path: Path = Path(gpx_tl.GpxTrackList(gpx_test_file))
    print(f'tot={path.tot()}')

    i: int
    pt: tp.TrackPoint
    for i, pt in enumerate(path.trackList()):
        print(f'pt[{i:>3}]={pt}')

    import unittest

    class TestGpx(unittest.TestCase):

        def test_CreatePath(self: TestGpx):
            path: Path = Path(gpx_tl.GpxTrackList(gpx_test_file))
            self.assertTrue(len(path.trackList()) != 0)
            self.assertTrue(len(path.km_idx_dis()) > 1)

        def test_getTrackPoint(self: TestGpx):
            path: Path = Path(gpx_tl.GpxTrackList(gpx_test_file))
            distance: float
            pt: Optional[tp.TrackPoint]

            distance = -1
            pt = path.getTrackPoint(distance) # before beginning
            self.assertTrue(pt is None)

            distance = 0
            pt = path.getTrackPoint(distance)
            self.assertTrue(pt is not None)
            if pt is not None:
                self.assertEqual(pt.idx, 0)
                self.assertEqual(pt.tot, distance)
                self.assertTrue((pt.tot <= distance) and (distance <= (pt.tot + pt.dis)))

            distance = 1000
            pt = path.getTrackPoint(distance)
            self.assertTrue(pt is not None)
            if pt is not None:
                self.assertEqual(pt.idx, 17)
                self.assertTrue((pt.tot <= distance) and (distance <= (pt.tot + pt.dis)))

            distance = 1300
            pt = path.getTrackPoint(distance)
            self.assertTrue(pt is not None)
            if pt is not None:
                self.assertEqual(pt.idx, 21)
                self.assertTrue((pt.tot <= distance) and (distance <= (pt.tot + pt.dis)))

            # We get the penultimate point when asking for the point which contains the length ?
            # I'm not sure this is the "correct" answer but the last point has a distance, bearing
            # and slope of zero, so returning the penultimate point is not unreasonable.
            distance = path.tot()
            pt = path.getTrackPoint(distance)
            self.assertTrue(pt is not None)
            if pt is not None:
                self.assertEqual(pt.idx, len(path.trackList()) - 2)
                self.assertTrue((pt.tot <= distance) and (distance <= (pt.tot + pt.dis)))

            distance = path.tot() + 1.0
            pt = path.getTrackPoint(distance)
            self.assertTrue(pt is None)

    unittest.main()
