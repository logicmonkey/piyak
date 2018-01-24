#!/usr/bin/env python

'''
Forensic - data analysis part of the Piyak kayak simulator ergo software for
           use on Lawler ergos. This software reads forensic_yyyymmddhhmm.csv
           files and calculates athlete power output. The calculation is
           given below and relies upon flywheel mass (to weigh it, you will
           have to dismantle your machine - a bit :)

Copyright (c) 2017-18 Piers Barber

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

    Pin is the power of the stroke (energy over total time, not just tpull)

              Ein
    Pin = ------------                   (2)
          tpull+tsetup

    '''

    power=[]

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

            local_min = (e3, t3) # e3 is the next e1
            min_index = i
            looking_for_e2 = True
            looking_for_e3 = False

    # replicate final entries in power to match the energy data set size
    for i in range(0, len(energy) - len(power)):
        power.append(pin)

    KERNEL=40
    fpower = []
    for i, p in enumerate(power):
        psum = 0
        for j in range(0, KERNEL):
            if i > j:
                psum += power[i-j]

        fpower.append(psum/KERNEL)

    return power, fpower

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

    power, fpower = calculate_power(energy, timestamp)

    return timestamp, energy, rpm, power, fpower

if __name__ == '__main__' :

    filename = sys.argv[1]

    timestamp, energy, rpm, power, fpower = forensic(filename)

    rlabel = 'Revolutions\n(per minute)'
    elabel = 'Rotational Energy\n(joules)'
    plabel = 'Power\n(watts)'
    xlabel = 'Time (seconds)'

    fig, (raxes, eaxes, paxes) = plt.subplots(3, sharex=True)

    raxes.set_title('Data source: {}'.format(filename))

    # make the markers a separate plot so they can be turned on and off

    rline, = raxes.plot(timestamp, rpm, 'g', label='line')
    rdots, = raxes.plot(timestamp, rpm, 'g', marker='.', label='samples')
    rleg   = raxes.legend(loc='upper left', fancybox=True, shadow=True)
    rleg.get_frame().set_alpha(0.4)
    raxes.grid(b=True)
    raxes.set_ylabel(rlabel)

    eline, = eaxes.plot(timestamp, energy, 'b', label='line')
    edots, = eaxes.plot(timestamp, energy, 'b', marker='.', label='samples')
    eleg   = eaxes.legend(loc='upper left', fancybox=True, shadow=True)
    eleg.get_frame().set_alpha(0.4)
    eaxes.grid(b=True)
    eaxes.set_ylabel(elabel)

    paxes.plot(timestamp, fpower, color='orange')
    paxes.grid(b=True)
    paxes.set_ylabel(plabel)

    paxes.set_xlabel(xlabel)

    # we will set up a dict mapping legend line to orig line, and enable
    # picking on the legend line
    rlines = [rline, rdots]
    elines = [eline, edots]
    lined = dict()
    for legline, origline in zip(rleg.get_lines(), rlines):
        legline.set_picker(5)  # 5 pts tolerance
        lined[legline] = origline

    for legline, origline in zip(eleg.get_lines(), elines):
        legline.set_picker(5)  # 5 pts tolerance
        lined[legline] = origline

    def onpick(event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        legline = event.artist
        origline = lined[legline]
        vis = not origline.get_visible()
        origline.set_visible(vis)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        if vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()
