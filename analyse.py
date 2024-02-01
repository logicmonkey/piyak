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
// Copyright (c) 2017 Piers Barber   piers.barber@logicmonkey.co.uk
//
// ------------------------------------------------------=--------------------

Analyse - data analysis part of the Piyak kayak simulator ergo software for
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

'''
  Synopsis:
    Draws a graph of power, stroke rate etc

  Usage:
    analyse.py <dat/activitydate>.dat
'''

import sys
import csv
import math
import re
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from report import scan_data

if __name__ == '__main__' :

    session = sys.argv[1]

    energy, rpm, power, stroke, power_a, power_b = scan_data(session)

    xlabel = 'Time (seconds)'
    xtitle = 'Session: {}'.format(session)

    fig, (rpm_axes, eny_axes, pwr_axes, stk_axes) = plt.subplots(4, sharex=True)

    rpm_axes.set_ylabel('Revolutions\n(per minute)')
    eny_axes.set_ylabel('Rotational\nEnergy\n(joules)')
    pwr_axes.set_ylabel('Power\n(watts)')
    stk_axes.set_ylabel('Double Strokes\n(per minute)')

    x, y = zip(*rpm)
    rpm_axes.plot(x, y, color='green')
    rpm_scat = rpm_axes.scatter(x, y, color='green', marker='.')

    x, y = zip(*energy)
    eny_axes.plot(x, y, color='blue')
    eny_scat = eny_axes.scatter(x, y, color='blue', marker='.')

    x, y = zip(*power)
    pwr_axes.plot(x, y, color='orange')

    x, y = zip(*power_a)
    pwr_axes.plot(x, y, color='red')
    pwra_scat = pwr_axes.scatter(x, y, color='red', marker='.')

    x, y = zip(*power_b)
    pwr_axes.plot(x, y, color='green')
    pwrb_scat = pwr_axes.scatter(x, y, color='green', marker='.')

    x, y = zip(*stroke)
    stk_axes.plot(x, y, color='gray')

    rpm_axes.grid(visible=True)
    eny_axes.grid(visible=True)
    pwr_axes.grid(visible=True)
    stk_axes.grid(visible=True)

    rpm_axes.set_title(xtitle)
    stk_axes.set_xlabel(xlabel)

    # ANNOTATION START - comment out between START and END for simple plot
    # create object for speed xy scatter because this can be queried and annotated

    rpm_anno = rpm_axes.annotate("", # set the annotation text based on value
                   xy=(0,0), xytext=(20,20),
                   textcoords="offset points",
                   bbox=dict(boxstyle="round", fc="w"),
                   arrowprops=dict(arrowstyle="->"))
    eny_anno = eny_axes.annotate("", # set the annotation text based on value
                   xy=(0,0), xytext=(20,20),
                   textcoords="offset points",
                   bbox=dict(boxstyle="round", fc="w"),
                   arrowprops=dict(arrowstyle="->"))
    pwr_anno = pwr_axes.annotate("", # set the annotation text based on value
                   xy=(0,0), xytext=(20,20),
                   textcoords="offset points",
                   bbox=dict(boxstyle="round", fc="w"),
                   arrowprops=dict(arrowstyle="->"))

    rpm_anno.set_visible(False)
    eny_anno.set_visible(False)
    pwr_anno.set_visible(False)

    def hover(event):
        rpm_vis = rpm_anno.get_visible()
        eny_vis = eny_anno.get_visible()
        pwr_vis = eny_anno.get_visible()

        if event.inaxes == rpm_axes:
            valid, index = rpm_scat.contains(event) # mouse event on scatter obj?
            rpm_anno.set_visible(valid)
            if valid:
                pos = rpm_scat.get_offsets()[index["ind"][0]]
                rpm_anno.xy = pos
                minutes, seconds = divmod(int(pos[0]), 60)
                rpm_anno.set_text("Time {:02d}:{:02d}\nTacho {:.0f}rpm".format(minutes, seconds, pos[1]))
                fig.canvas.draw_idle()
            elif rpm_vis:
                fig.canvas.draw_idle()

        if event.inaxes == eny_axes:
            valid, index = eny_scat.contains(event) # mouse event on scatter obj?
            eny_anno.set_visible(valid)
            if valid:
                pos = eny_scat.get_offsets()[index["ind"][0]]
                eny_anno.xy = pos
                eny_anno.set_text("Time {:.2f}s\nEnergy {:.0f}J".format(pos[0], pos[1]))
                fig.canvas.draw_idle()
            elif eny_vis:
                fig.canvas.draw_idle()

        if event.inaxes == pwr_axes:
            a_valid, a_index = pwra_scat.contains(event) # mouse event on scatter obj?
            b_valid, b_index = pwrb_scat.contains(event) # mouse event on scatter obj?
            if a_valid:
                pwr_anno.set_visible(a_valid)
                pos = pwra_scat.get_offsets()[a_index["ind"][0]]
                pwr_anno.xy = pos
                minutes, seconds = divmod(int(pos[0]), 60)
                pwr_anno.set_text("Time {:02d}:{:02d}\nPower {:.0f}W".format(minutes, seconds, pos[1]))
                fig.canvas.draw_idle()
            elif b_valid:
                pwr_anno.set_visible(b_valid)
                pos = pwrb_scat.get_offsets()[b_index["ind"][0]]
                pwr_anno.xy = pos
                minutes, seconds = divmod(int(pos[0]), 60)
                pwr_anno.set_text("Time {:02d}:{:02d}\nPower {:.0f}W".format(minutes, seconds, pos[1]))
                fig.canvas.draw_idle()
            elif pwr_vis:
                fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)
    # ANNOTATION END

    plt.tight_layout()
    plt.show()
