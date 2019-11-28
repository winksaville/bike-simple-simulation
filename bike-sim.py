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
v=0.0  # initial velocity
power = 600 # constant power in W
dt = 0.1    # time step
va=[0]      # store the results in a list which will grow in each iteration
ta=[0]

# loop over time:
for t in np.arange(0,10,dt):
    totalForce = fDrag(v) + fRolling(grade, mass, v) + fGravity(grade, mass)
    powerNeeded = totalForce * v / eta
    netPower = power - powerNeeded
    # kinetic energy increases by net energy available for dt
    print("t = %.2f; v=%.1f; drag = %.2f N; F roll = %.2f N; F gravity = %.2f N"%(t, v, fDrag(v), fRolling(grade, mass, v), fGravity(grade, mass)))
    v = math.sqrt(v*v + 2 * netPower * dt * eta / mass)
    va.append(v)
    ta.append(t+dt)

plt.figure()
plt.plot(ta, va)
plt.xlabel('time (s)')
plt.ylabel('velocity (m/s)')
plt.show()
