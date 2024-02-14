#!/usr/bin/env python

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
// Copyright (c) 2017-24 Piers Barber   piers.barber@logicmonkey.co.uk
//
// ------------------------------------------------------=--------------------

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

'''
Synopsis
Data analysis part of the Piyak kayak simulator ergo software for use on Lawler
ergos. This software reads session yyyymmddhhmm.dat files and calculates
athlete power output. The calculation is given below and relies upon flywheel
mass (to weigh it, you will have to dismantle your machine - a bit :)

Draws a graph of power, stroke rate etc

  Usage:
    analyse.py <dat/activitydate>.dat
'''

import sys
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from postprocess import scan_data

if __name__ == '__main__' :

    session = sys.argv[1]

    energy, rpm, power, stroke, power_a, power_b = scan_data(session)

    xlabel = 'Time (seconds)'
    xtitle = 'Session: {}'.format(session)

    #fig, (rpm_axes, pwr_axes) = plt.subplots(2, sharex=True)
    fig, pwr_axes = plt.subplots()

    # Flywheel
    #color = 'tab:green'
    #rpm_axes.grid(visible=True)
    #rpm_axes.set_ylabel('Flywheel\n(rpm)', color=color)
    #x, y = zip(*rpm)
    #rpm_axes.plot(x, y, color=color)
    #rpm_scat = rpm_axes.scatter(x, y, color=color, marker='.')

    # Power
    pwr_axes.grid(visible=True)

    color = 'black'
    pwr_axes.set_ylabel('Energy (joules)\nPower (watts)\nStroke Rate (dspm)', color=color)
    color = 'tab:orange'
    x, y = zip(*power)
    pwr_axes.plot(x, y, color=color)

    color = 'tab:blue'
    x, y = zip(*energy)
    pwr_axes.plot(x, y, color=color)
    eny_scat = pwr_axes.scatter(x, y, color=color, marker='.')

    color = 'tab:red'
    x, y = zip(*power_a)
    pwr_axes.plot(x, y, color=color)
    pwra_scat = pwr_axes.scatter(x, y, color=color, marker='.')

    color = 'tab:green'
    x, y = zip(*power_b)
    pwr_axes.plot(x, y, color=color)
    pwrb_scat = pwr_axes.scatter(x, y, color=color, marker='.')

    # Stroke rate
    color = 'tab:purple'
    x, y = zip(*stroke)
    pwr_axes.plot(x, y, color=color)

    #rpm_axes.set_title(xtitle)
    pwr_axes.set_xlabel(xlabel)

    # ANNOTATION START - comment out between START and END for simple plot
    # create object for speed xy scatter because this can be queried and annotated

    #rpm_anno = rpm_axes.annotate("",
    #               xy=(0,0), xytext=(20,20),
    #               textcoords="offset points",
    #               bbox=dict(boxstyle="round", fc="w"),
    #               arrowprops=dict(arrowstyle="->"))
    pwr_anno = pwr_axes.annotate("",
                   xy=(0,0), xytext=(20,20),
                   textcoords="offset points",
                   bbox=dict(boxstyle="round", fc="w"),
                   arrowprops=dict(arrowstyle="->"))

    #rpm_anno.set_visible(False)
    pwr_anno.set_visible(False)

    def hover(event):

    #    if event.inaxes == rpm_axes:
    #        r_valid, r_index = rpm_scat.contains(event)
    #        rpm_anno.set_visible(r_valid)
    #        if r_valid:
    #            pos = rpm_scat.get_offsets()[r_index["ind"][0]]
    #            rpm_anno.xy = pos
    #            minutes, seconds = divmod(int(pos[0]), 60)
    #            rpm_anno.set_text("Time {:02d}:{:02d}\nTacho {:.0f}rpm".format(minutes, seconds, pos[1]))
    #            fig.canvas.draw_idle()

        if event.inaxes == pwr_axes:
            a_valid, a_index = pwra_scat.contains(event)
            b_valid, b_index = pwrb_scat.contains(event)
            e_valid, e_index = eny_scat.contains(event)
            pwr_anno.set_visible(a_valid or b_valid or e_valid)
            if a_valid:
                pos = pwra_scat.get_offsets()[a_index["ind"][0]]
                pwr_anno.xy = pos
                pwr_anno.set_text("Time {:.3f}s\nPower {:.0f}W".format(pos[0], pos[1]))
                fig.canvas.draw_idle()
            elif b_valid:
                pos = pwrb_scat.get_offsets()[b_index["ind"][0]]
                pwr_anno.xy = pos
                pwr_anno.set_text("Time {:.3f}s\nPower {:.0f}W".format(pos[0], pos[1]))
                fig.canvas.draw_idle()
            elif e_valid:
                pos = eny_scat.get_offsets()[e_index["ind"][0]]
                pwr_anno.xy = pos
                pwr_anno.set_text("Time {:.3f}s\nEnergy {:.0f}J".format(pos[0], pos[1]))
                fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)
    # ANNOTATION END

    plt.tight_layout()
    plt.show()
