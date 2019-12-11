'''
Calculate distance using the Haversine Formula

Flgorithm from:
  https://community.esri.com/groups/coordinate-reference-systems/blog/2017/10/05/haversine-formula
 
 Slight changes:
  - Changed the coordinate order from lon, lat to lat, lon
  - Pass radius as a parameter
  - Return distance in meters
  - Removed output
  - Added test for "main" to output a copule values
'''

import math
from typing import Tuple

earthR1 = 6_371_008.7714

def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float], radius: float=earthR1) -> float:

    # Coordinates in decimal degrees (e.g. 2.89078, 12.79797)
    lat1: float
    lon1: float
    lat2: float
    lon2: float
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    R = 6371008.7714  # radius of Earth in meters
    phi_1: float = math.radians(lat1)
    phi_2: float = math.radians(lat2)
    delta_phi: float = math.radians(lat2 - lat1)
    delta_lambda: float = math.radians(lon2 - lon1)

    #lambda_1: float = math.radians(lon1)
    #lambda_2: float = math.radians(lon2)
    #delta_phi: float = phi_2 - phi_1
    #delta_lambda: float = lambda_2 - lambda_1

    a = (math.sin(delta_phi / 2.0) ** 2.0) + (math.cos(phi_1) * math.cos(phi_2) * (math.sin(delta_lambda / 2.0) ** 2.0))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    meters = radius * c  # output distance in meters
    return meters

if __name__ == '__main__':
    print(f'distance: {haversine((-0.116773, 51.510357), (-77.009003, 38.889931))}m')
    print(f'disnance: {haversine((1.0, 2.0), (1.0, 3.0))}m')
