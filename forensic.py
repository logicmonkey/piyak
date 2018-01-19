#!/usr/bin/env python

import sys
import csv
import math
import matplotlib.pyplot as plt

# SI unit for moment of inertia is kg metres squared (not grammes)
mass   = 4.360  # mass of Lawler flywheel in kilogrammes
radius = 0.200  # radius of Lawler flywheel in metres

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
    return timestamp, energy, rpm

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

    llabel = 'Rotational Kinetic Energy (Joules)'
    rlabel = 'RPM'
    xlabel = 'Time (Seconds)'

    fig, yaxis = plt.subplots()
    ly, ry = share_axis(yaxis, timestamp, xlabel, energy, llabel, 'b-', rpm, rlabel, 'r.')

    colour_axis(ly, 'b')
    colour_axis(ry, 'r')

    plt.grid()
    plt.show()
