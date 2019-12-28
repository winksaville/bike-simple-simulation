#!/usr/bin/env python3

# bike power calculation
import math
import numpy as np
import xml.etree.ElementTree as et

import os
import track_point as tp
import path as p
import gpx_track_list as gpx_tl
import tcx_track_list as tcx_tl

# Some constants
bike = 8.62 # kg 19 lbs
rider = 81.65 # kg 180 lbs
mass = bike + rider

# I adjusted the frontalArea until max speed calculated here was 17.00mph
# I estimated the frontalArea from a flat section of a [ride](https://veloviewer.com/athletes/2039/activities/2802129759)
# I did between time 00:15:47 - 00:17:32. Then in the "Power (meter)" graph for that section I produced
# an avgerage Power of 142W at an average speed of 17.00mph.  I then twiddled the the frontalArea variable
# until max speed calculated was 17.00mph.
#
# [Here](https://www.triradar.com/training-advice/how-to-calculate-your-drag/) is another method for
# estimating the forntalArea using photoshop. When I do that I iwll then adjust the dragCoeff variable
# until the speed is again calculated to be 17.00mph.
power = 142 # Watts
frontalArea = 0.449 # Sq meters
dragCoeff = 0.88

# A few plausible factors from http://www.cyclingpowerlab.com/CyclingAerodynamics.aspx
rho = 1.2
eta = 0.97 # 1 - drive train loss = efficiency
rollingCoeff = 5.0e-3 # from haskell code

#grade = 0.0/100.0 #0.0
g = 9.81


# functions to compute the various forces:
def fDrag(velocity):
    return 0.5*dragCoeff*frontalArea*rho*velocity*velocity

def fRolling(grade, mass, velocity):
    if velocity > 0.01:
        return g * math.cos(math.atan(grade)) * mass * rollingCoeff
    else:
        return 0.0

def fGravity(grade, mass):
    return g*math.sin(math.atan(grade))*mass

def slopeRadians(dist):
    """
    Given the distance in meters find the slope in radians.

    We assume the "road" is an undulating sine wave
    with a constant frequency and amplitude. If amplitude
    is 0 there is no undulations.
    """
    # The cos(sin(x)) is the slope of a line tagent to the sin curve at x
    freq = 100.0 # 100 meters
    amplitude = 1.0 / freq # 0.0 for level 1.0 for slight undulation
    c = math.cos(2.0 * math.pi * (dist / freq)) * amplitude
    return c

def mph(mps):
    """
    Meters per second to miles per hour
    """
    mpsToMph = 3600.0 / (0.0254 * 12.0 * 5280.0)
    return mps * mpsToMph

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Process Path.")
    parser.add_argument('filename', type=str, help='file to process')
    parser.add_argument('power', type=float, help='power', default=power)
    args = parser.parse_args()
    print(f'filename={args.filename}')
    print(f'power={args.power}')

    power = args.power

    _, extension = os.path.splitext(args.filename)
    if extension == '.gpx':
        trklist: p.Path = p.Path(gpx_tl.GpxTrackList(args.filename))
    elif extension == '.tcx':
        trklist: p.Path = p.Path(tcx_tl.TcxTrackList(args.filename))
    else:
        print(f"Unknown file extension:'{extension}' for filename:{args.filename}")
        exit(1)


    print(f'total_distance={trklist.total_distance()}')

    # the actual program:
    v=0.0       # initial velocity
    dt = 0.1    # time step
    va=[0]      # velocity array
    ta=[0]      # time array
    da=[0]      # distance array
    pv = 0.0    # previous velocity
    d=0.0       # initial distance

    #for d in np.arange(0, 100, 0.1):
    #  print(f'd={d:.2f} slope={slopeRadians(d):.02f}')


    # loop over time until end of distance:
    t: float = 0.0
    total_distance: float = trklist.total_distance()
    while d < total_distance:
        grade = trklist.slopeRadians(d)
        totalForce = fDrag(v) + fRolling(grade, mass, v) + fGravity(grade, mass)
        powerNeeded = totalForce * v / eta
        netPower = power - powerNeeded

        av = (v + pv) / 2.0 # average velocity
        sd = av * dt # step distance
        if (d + sd) > total_distance:
            # Don't go past the last point
            sd = total_distance - d # Adjust the last stpe
            dt = sd / av # Adjust the dt
            d = total_distance # We're done
        else:
            d += sd # distance traveled

        # kinetic energy increases by net energy available for dt
        #print(f't={t:.2f} v={mph(v):.2f}mph drag={fDrag(v):.2f}N grade={grade:.02f} F roll={fRolling(grade, mass, v):.2f}N F gravity={fGravity(grade, mass):.2f}N d={d:.2f}m sd={sd:.2f}m')

        pv = v
        v = math.sqrt(v*v + 2 * netPower * dt * eta / mass)
        print(f't={t:.2f} d={d:.2f}m v={mph(v):.2f}mph grade={grade:.02f} sd={sd:.2f}m')
        va.append(mph(v))
        ta.append(t+dt)
        da.append(d)

        # incrment time
        t += dt

    hours: int = math.trunc(t / 3600.0)
    minutes: int = math.trunc((t  - (hours * 3600.0)) / 60)
    seconds: float = t - (hours * 3600) - (minutes * 60)
    print(f't={t:.2f} {hours}:{minutes}:{seconds:.2f} v={mph(v):.2f}mph drag={fDrag(v):.2f}N grade={grade:.02f} F roll={fRolling(grade, mass, v):.2f}N F gravity={fGravity(grade, mass):.2f}N d={d:.2f}m sd={sd:.2f}m')

    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(da, va)
    plt.xlabel('distance (m)')
    #plt.plot(ta, va)
    #plt.xlabel('time (s)')
    plt.ylabel('velocity (mph)')
    plt.show()
