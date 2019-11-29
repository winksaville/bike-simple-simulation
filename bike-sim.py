#!/usr/bin/env python3

# bike power calculation
import math
import numpy as np
import matplotlib.pyplot as plt

# a few plausible factors from http://www.cyclingpowerlab.com/CyclingAerodynamics.aspx
dragCoeff = 0.88
frontalArea = 0.32 

rho = 1.2
eta = 0.97 # 1 - drive train loss = efficiency
rollingCoeff = 5.0e-3 # from haskell code
mass = 62 #kg
grade = 0.0
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

# the actual program:
v=0.0       # initial velocity
power = 600 # constant power in W
dt = 0.1    # time step
va=[0]      # velocity array
ta=[0]      # time array
da=[0]      # distance array
pv = 0.0    # previous velocity
d=0.0       # initial distance

# loop over time:
for t in np.arange(0,10,dt):
    totalForce = fDrag(v) + fRolling(grade, mass, v) + fGravity(grade, mass)
    powerNeeded = totalForce * v / eta
    netPower = power - powerNeeded

    av = (v + pv) / 2.0 # average velocity
    sd = av * dt # step distance
    d += sd # distance traveled

    # kinetic energy increases by net energy available for dt
    print("t = %.2f; v=%.1f; drag = %.2f N; F roll = %.2f N; F gravity = %.2f N d = %.2f m sd = %.2f m"%(t, v, fDrag(v), fRolling(grade, mass, v), fGravity(grade, mass), d, sd))
    pv = v
    v = math.sqrt(v*v + 2 * netPower * dt * eta / mass)
    va.append(v)
    ta.append(t+dt)
    da.append(d)

plt.figure()
plt.plot(da, va)
plt.xlabel('distance (m)')
#plt.plot(ta, va)
#plt.xlabel('time (s)')
plt.ylabel('velocity (m/s)')
plt.show()
