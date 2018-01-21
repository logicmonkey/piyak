#!/usr/bin/env python

import sys
import csv
import math
import matplotlib.pyplot as plt

# SI unit for moment of inertia is kg metres squared (not grammes)
mass   = 4.360  # mass of Lawler flywheel in kilogrammes
radius = 0.200  # radius of Lawler flywheel in metres

def calculate_power(energy):
'''
    1) look for an upward energy trend
    2) the first measurement in an upward trend is a local minimum
    3) look for a downward trend in energy
    4) the first measurement in a downward trend is a local maximum
    5) look for an upward energy trend
    6) the first measurement in an upward trend is a local minimum

    This is all the data required for analysis of a stroke.

    These values are calculated from measured values of angular velocity:

        E1     - starting rotational energy of the flywheel
        E2     - local maximum energy at the end of a pull
        E3     - energy that the flywheel decays to before the next stroke
        tpull  - time difference between energies E2 and E1
        tsetup - time difference between energies E3 and E2


                               E2
                               *. max
                              /: `.
                             / :   `.
                            *  :     *.
                           /   :       `. E4
                          /    :<-tpull->`.
                         *     :           *.    *
                        /      :             `. /
                       /       :<---tsetup---->* min
                    \ /        :               E3
                 min *<-tpull->:
                    E1

    E4 is the energy level dropped to from E2 over a period equal to tpull
    as the flywheel spins down due to air resistance. It is calculated from
    the spin down gradient

    Ein is the total energy put into the flywheel plus the energy lost to
    air resistance of the fan. Ein = E2-E1+E4

                       (E2-E3)
    Ein = E2-E1 + tpull--------
                        tsetup

    Pin is the power of the stroke (energy over total time)

              Ein
    Pin = ------------
          tpull+tsetup

'''

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
    return timestamp, energy, rpm, power

def share_axis(lyaxis, xdata, xlabel, lydata, lylabel, lycol, rydata, rylabel, rycol):
    ryaxis = lyaxis.twinx()

    lyaxis.plot(xdata, lydata, lycol)
    lyaxis.set_xlabel(xlabel)
    lyaxis.set_ylabel(lylabel)

    ryaxis.plot(xdata, rydata, rycol)
    ryaxis.set_ylabel(rylabel)
    return lyaxis, ryaxis

def colour_axis(axis, color):
    for t in axis.get_yticklabels():
        t.set_color(color)
    return None

if __name__ == '__main__' :

    filename = sys.argv[1]

    timestamp, energy, rpm = forensic(filename)

    llabel = 'RPM'
    rlabel = 'Rotational Kinetic Energy (Joules)'
    xlabel = 'Time (Seconds)'

    fig, yaxis = plt.subplots()
    ly, ry = share_axis(yaxis, timestamp, xlabel, rpm, llabel, 'b-', energy, rlabel, 'r.')

    colour_axis(ly, 'r')
    colour_axis(ry, 'b')

    plt.grid()
    plt.show()
