'''
        _      ___
  o----o o----|___|----*---o
       sw       R      |
                      ---
  Vi                  --- C  Vc
                       |
  o--------------------*---o

  i = (Vi-Vc)/R
  i = CdVc/dt

  (Vi-Vc)/R1 = C dVc/dt

  dVc   Vi - Vc
  --- = -------
  dt       RC

  Solve this simple ODE twice, once for a single slow charge and again for
  multiple short pulses of the SAME amplitude

'''

def rc(vc, t, r, c, vi, charge):
    dvcdt = -vc
    if charge:
        if t<50:
            dvcdt += vi          # charge by adding energy in a single hit until t=50
    else:
        if int(t)%2 == 0 and t<90:
            dvcdt += vi          # pump by adding energy every other second until t=90
    return dvcdt/(r*c)

r, c, vi = 1, 1, 1               # wow - those parameters were easy :)

import numpy as np
t = np.linspace(0, 100, 1001)

from scipy.integrate import odeint

vc0 = 0.0 # initial condition, zero voltage across the capacitor

solc = odeint(rc, vc0, t, args=(r, c, vi, True))  # charge
solp = odeint(rc, vc0, t, args=(r, c, vi, False)) # pump

import matplotlib.pyplot as plt
plt.plot(t, solc, 'g', label='charge')
plt.plot(t, solp, 'b', label='pump')
plt.legend(loc='best')
plt.xlabel('t')
plt.grid()
plt.show()
