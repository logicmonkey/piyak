#!/usr/bin/env python

import sys
import csv
import math
import matplotlib.pyplot as plt

# SI unit for moment of inertia is kg metres squared (not grammes)`
mass   = 4.360  # mass of Lawler flywheel in kilogrammes
radius = 0.200  # radius of Lawler flywheel in metres

def forensic(filename):

    rpm=[]         # this doesn't really get used yet
    period=[]      # neither does this - just the last thing pushed to it

    timestamp=[]
    energy=[]

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
    return timestamp, energy


if __name__ == '__main__' :

    filename = sys.argv[1]

    timestamp, energy = forensic(filename)

    plt.plot(timestamp, energy, 'r', marker='.', label='kinetic energy')
    plt.ylabel('rotational kinetic energy (Joules)')
    plt.xlabel('time (Seconds)')
    plt.grid()
    plt.show()
