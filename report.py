'''
// ---------------------------------------------------------------------------
//
//                                      ,`\
//  L                              ...    /  M   M             k
//  L      ooo   ggg  i  ccc     @ o o @.'   M\ /M  ooo  n nn  k k   ee  y   y
//  L     o   o g   g . c      .' ( o )      M V M o   o n'  n kk   e__e y   y
//  L     o   o g   g i c     /  (     )     M   M o   o n   n k k  e    y   y
//  LLLLL  ooo   gggg i  ccc  \.' \ : /      M   M  ooo  n   n K  k  ee'  yyyy
//                  g            nnn nnn                                    y
//                gg                                                     yyy
//
// ------------------------------------------------------=--------------------
//
// Piyak - a program to monitor and log the effort on a kayak ergo.
//
// Copyright (c) 2017-18 Piers Barber   piers.barber@logicmonkey.co.uk
//
// ------------------------------------------------------=--------------------

Forensic - data analysis part of the Piyak kayak simulator ergo software for
           use on Lawler ergos. This software reads activity_yyyymmddhhmm.csv
           files and calculates athlete power output. The calculation is
           given below and relies upon flywheel mass (to weigh it, you will
           have to dismantle your machine - a bit :)

This is free software released under the terms of the MIT licence

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import sys
import csv
import math
import re
import matplotlib.pyplot as plt

def calculate_power(energy, timestamp):
    '''
    Identify Individual Strokes

    Traditionally the kayak stroke is split into four phases:

      Catch    - point at which the blade has fully entered the water
      Power    - pulling past the blade
      Recovery - extraction of the blade from the water (inverse of catch)
      Setup    - dead time after recovery on the current side and catch on
                 the next. No part of the paddle is in the water.

    A simpler model for use on an ergo has the catch as the start of the power
    phase and recovery as the start of the setup phase. The rotation speed
    increases with energy input (power) and falls away beteen strokes (setup).

    On the water, catch and recovery are important periods as far as technique
    is concerned as respectively, they optimise the effort during the power
    phase and boat glide during setup. But for the purposes of ergo power
    calculations they don't matter.

                 |                   .    .
             RPM |              .   / `. / `.  .
                 |    .    .   / `.'    '    `/ `.  .
                 |   / `. / `.'                   `/ `.
                 |  '    '                             `.
                -+----------------------------------------> time
                 '

    Every ergo flywheel revolution is timed individually, so the actual
    rotational kinetic energy is easily calculated from the angular velocity,
    moment of inertia and flywheel mass.

    repeat {
       look for an upward energy trend (energy input)
              # the first measurement in an upward trend is a local minimum
       look for a downward trend in energy (energy loss)
              # the first measurement in a downward trend is a local maximum
       }

    This is all the data required for power analysis of a stroke.

    Calculate Rate of Energy Input

    These values are calculated from measured values of angular velocity:

        E1     - starting rotational energy of the flywheel
        E2     - local maximum energy at the end of a pull (power phase)
        E3     - energy that the flywheel decays to before the next stroke
        tpower - time difference between energies E1 and E1 (t2-t1)
        tsetup - time difference between energies E2 and E3 (t3-t2)


                               E2
                               o. max
                              /: `.
                             / :   `.
                            o  :     o.
                           /   :       `.
                          /    :<-tpower->.E4
                         o     :           o.    o
                        /      :             `. /
                       /       :<---tsetup---->o min
                      /        :               E3
                   \ /         :
                min o<-tpower->:
                    E1

    E4 is the energy level dropped to from E2 over a period equal to tpower
    as the flywheel spins down due to air resistance. It is calculated from
    the spin down gradient. This energy is equal to the energy lost to air
    resistance during the power phase.

    Ein is the total energy put into the flywheel plus the energy lost to
    air resistance of the fan. Ein = E2-E1+E4

                        (E2-E3)
    Ein = E2-E1 + tpower--------          (1)
                         tsetup

    Pin is the power of the stroke (energy over total time, not just tpower)

              Ein
    Pin = ------------                    (2)
          tpower+tsetup

    '''

    power = []
    stroke = []

    looking_for_e1 = True     # start here in hunt for first local minimum
    looking_for_e2 = False    # then alternate between this state and the next
    looking_for_e3 = False

    min_index = 0             # position of the last minimum

    for i, v in enumerate(energy[:-1]): # loop over all i, i+1 pairs

        if looking_for_e1 and v < energy[i+1]:
            local_min = (v, timestamp[i])

            # pad all power entries up to the first local minimum with zero
            for j in range(0, i - min_index):
                power.append(0)
                stroke.append(0)

            min_index = i

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

            # we're at E3 in the data, so calculate the power for this stroke
            # and update the values from the E1 position to here
            pin = (e2-e1+(t2-t1)*(e2-e3)/(t3-t2))/(t3-t1) # eqs.(1,2)

            for j in range(0, i - min_index):
                power.append(pin)
                stroke.append(30.0/(t3-t1)) # double strokes/min = strokes/30s

            local_min = (e3, t3) # e3 is the next e1
            min_index = i
            looking_for_e2 = True
            looking_for_e3 = False

    # replicate final entries in power to match the energy data set size
    for i in range(0, len(energy) - len(power)):
        power.append(pin)
        stroke.append(0)

    KERNEL=40
    fpower = []
    fstroke = []
    for i, p in enumerate(power):
        psum = 0
        ssum = 0
        for j in range(0, KERNEL):
            if i > j:
                psum += power[i-j]
                ssum += stroke[i-j]

        fpower.append(psum/KERNEL)
        fstroke.append(ssum/KERNEL)

    return fpower, fstroke

def forensic(filename):

    # SI unit for moment of inertia is kg metres squared (not grammes)
    mass   = 4.360  # mass of Lawler flywheel in kilogrammes
    radius = 0.200  # radius of Lawler flywheel in metres

    period = []     # not fully used - just the last thing pushed to it

    timestamp = []
    energy = []
    rpm = []

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

    fpower, fstroke = calculate_power(energy, timestamp)

    return timestamp, energy, rpm, fpower, fstroke

def report(filename):

    timestamp, energy, rpm, fpower, fstroke = forensic(filename)

    xlabel    = 'Time (seconds)'
    xtitle    = 'Data source: {}'.format(filename)
    rpm_label = 'Revolutions\n(per minute)'
    eny_label = 'Rotational\nEnergy\n(joules)'
    pwr_label = 'Power\n(watts)'
    stk_label = 'Double Strokes\n(per minute)'

    fig, (rpm_axes, eny_axes, pwr_axes, stk_axes) = plt.subplots(4, sharex=True)

    rpm_dots, = rpm_axes.plot(timestamp, rpm, 'g', marker='.', label='samples')
    rpm_axes.grid(b=True)
    rpm_axes.set_ylabel(rpm_label)

    eny_line, = eny_axes.plot(timestamp, energy, 'b', label='line')
    eny_axes.grid(b=True)
    eny_axes.set_ylabel(eny_label)

    pwr_axes.plot(timestamp, fpower, color='orange')
    pwr_axes.grid(b=True)
    pwr_axes.set_ylabel(pwr_label)

    stk_axes.plot(timestamp, fstroke, color='gray')
    stk_axes.grid(b=True)
    stk_axes.set_ylabel(stk_label)

    rpm_axes.set_title(xtitle)
    stk_axes.set_xlabel(xlabel)

    plt.tight_layout()

    fig.savefig(re.compile('csv').sub('png', filename))
    #plt.show()
    plt.close(fig)
