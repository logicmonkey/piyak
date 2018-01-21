#!/usr/bin/env python

import sys
import csv
import math
import matplotlib.pyplot as plt

# SI unit for moment of inertia is kg metres squared (not grammes)
mass   = 4.360  # mass of Lawler flywheel in kilogrammes
radius = 0.200  # radius of Lawler flywheel in metres

def calculate_power(energy, timestamp):
    '''
    Identify individual Strokes

    1) look for an upward energy trend
       the first measurement in an upward trend is a local minimum
    3) look for a downward trend in energy
       the first measurement in a downward trend is a local maximum
    5) look for an upward energy trend
       the first measurement in an upward trend is a local minimum

    This is all the data required for analysis of a stroke.

    Calculate Rate of Energy Input

    These values are calculated from measured values of angular velocity:

        E1     - starting rotational energy of the flywheel
        E2     - local maximum energy at the end of a pull
        E3     - energy that the flywheel decays to before the next stroke
        tpull  - time difference between energies E2 and E1 (t2-t1)
        tsetup - time difference between energies E3 and E2 (t3-t2)


                               E2
                               o. max
                              /: `.
                             / :   `.
                            o  :     o.
                           /   :       `. E4
                          /    :<-tpull->`.
                         o     :           o.    o
                        /      :             `. /
                       /       :<---tsetup---->o min
                    \ /        :               E3
                 min o<-tpull->:
                    E1

    E4 is the energy level dropped to from E2 over a period equal to tpull
    as the flywheel spins down due to air resistance. It is calculated from
    the spin down gradient

    Ein is the total energy put into the flywheel plus the energy lost to
    air resistance of the fan. Ein = E2-E1+E4

                       (E2-E3)
    Ein = E2-E1 + tpull--------          (1)
                        tsetup

    Pin is the power of the stroke (energy over total time)

              Ein
    Pin = ------------                   (2)
          tpull+tsetup

    '''

    power=[]

    looking_for_e1 = True     # start here in hunt for first local minimum
    looking_for_e2 = False    # then alternate between this state and the next
    looking_for_e3 = False

    stroke_power = 0

    for i, v in enumerate(energy[:-1]): # loop over all i, i+1 pairs

        power.append(stroke_power) # redundancy keeps data sets the same size

        if looking_for_e1 and v < energy[i+1]:
            local_min = (v, timestamp[i])
            looking_for_e1 = False
            looking_for_e2 = True

        elif looking_for_e2 and v > energy[i+1]:
            local_max = (v, timestamp[i])
            looking_for_e2 = False
            looking_for_e3 = True

        elif looking_for_e3 and v < energy[i+1]:
            e1, t1 = local_min
            e2, t2 = local_max
            e3, t3 = v, timestamp[i]

            stroke_power = (e2-e1+(t2-t1)*(e2-e3)/(t3-t2))/(t3-t1) # eqs.(1,2)

            local_min = (e3, t3) # e3 is the next e1
            looking_for_e2 = True
            looking_for_e3 = False

    # push a final value as there is one less interval than energy data points
    power.append(stroke_power)
    return power

def forensic(filename):

    period=[]      # not fully used - just the last thing pushed to it

    timestamp=[]
    energy=[]
    rpm=[]

    with open(filename) as csvfile:
        alldata = csv.reader(csvfile, delimiter=',')
        for row in alldata:
            if row[2] != 'None' and row[2] != '0':
                h, m, s = row[0].split(':')
                timestamp.append(int(h)*3600 + int(m)*60 + float(s))
                # the millisecond rotation periods into seconds
                period.append(int(row[2])*1.0e-6)
                # current rotation period to frequency in rpm
                rpm.append(60.0/period[-1])

                # w  = 2*pi/period (angular velocity omega = 2 pi radians * revolutions/second)
                # I  = 0.5*m*r^2 (half m radius squared)
                # KE = 0.5*I*w^2 (half I omega squared)
                energy.append(mass*(radius*math.pi/period[-1])**2)

    power = calculate_power(energy, timestamp)

    return timestamp, energy, rpm, power

if __name__ == '__main__' :

    filename = sys.argv[1]

    timestamp, energy, rpm, power = forensic(filename)

    rlabel = 'Revolutions\n(per minute)'
    elabel = 'Rotational Energy\n(joules)'
    plabel = 'Power\n(watts)'
    xlabel = 'Time (seconds)'

    fig, (raxes, eaxes, paxes) = plt.subplots(3, sharex=True)

    raxes.plot(timestamp, rpm, 'g-')
    raxes.grid(b=True)
    raxes.set_ylabel(rlabel)

    eaxes.plot(timestamp, energy, 'b-')
    eaxes.grid(b=True)
    eaxes.set_ylabel(elabel)

    paxes.plot(timestamp, power, 'r-')
    paxes.grid(b=True)
    paxes.set_ylabel(plabel)

    paxes.set_xlabel(xlabel)

    plt.show()
