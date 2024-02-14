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
from matplotlib.widgets import SpanSelector
import numpy as np
from postprocess import scan_data

if __name__ == '__main__' :

    session = sys.argv[1]

    energy, rpm, power, stroke, power_a, power_b = scan_data(session)

    rpm_color  = 'tab:green'
    pwr_color  = 'tab:orange'
    eny_color  = 'tab:blue'
    pwra_color = 'tab:red'
    pwrb_color = 'tab:green'
    stk_color  = 'tab:purple'
    color      = 'black'

    #fig, (rpm_ax, world_ax, zoom_ax) = plt.subplots(3, sharex=True)
    fig, (world_ax, zoom_ax) = plt.subplots(2)

    world_ax.set_title('Session: {}'.format(session))
    zoom_ax.set_xlabel('Time (seconds)')

    # Flywheel
    #rpm_ax.grid(visible=True)
    #rpm_ax.set_ylabel('Flywheel\n(rpm)', color=rpm_color)
    #rpm_x, rpm_y = zip(*rpm)
    #rpm_ax.plot(rpm_x, rpm_y, color=rpm_color)
    #rpm_scat = rpm_ax.scatter(rpm_x, rpm_y, color=rpm_color, marker='.')

    # Power
    world_ax.grid(visible=True)

    world_ax.set_ylabel('Flywheel Energy (joules)\nPower (watts)\nStroke Rate (dspm)', color=color)
    zoom_ax.set_ylabel('Flywheel Energy (joules)\nPower (watts))', color=color)

    pwr_x , pwr_y  = zip(*power)
    eny_x,  eny_y  = zip(*energy)
    pwra_x, pwra_y = zip(*power_a)
    pwrb_x, pwrb_y = zip(*power_b)
    stk_x,  stk_y  = zip(*stroke)

    world_ax.plot(eny_x,  eny_y,  color=eny_color)
    world_ax.plot(pwra_x, pwra_y, color=pwra_color)
    world_ax.plot(pwrb_x, pwrb_y, color=pwrb_color)
    world_ax.plot(pwr_x,  pwr_y,  color=pwr_color)
    world_ax.plot(stk_x,  stk_y,  color=stk_color)

    zoom_eny,  = zoom_ax.plot([], [], color=eny_color)
    zoom_pwra, = zoom_ax.plot([], [], color=pwra_color)
    zoom_pwrb, = zoom_ax.plot([], [], color=pwrb_color)

    eny_scat  = zoom_ax.scatter([], [], color=eny_color,  marker='.')
    pwra_scat = zoom_ax.scatter([], [], color=pwra_color, marker='.')
    pwrb_scat = zoom_ax.scatter([], [], color=pwrb_color, marker='.')

    #rpm_anno = rpm_axes.annotate("",
    #               xy=(0,0), xytext=(20,20),
    #               textcoords="offset points",
    #               bbox=dict(boxstyle="round", fc="w"),
    #               arrowprops=dict(arrowstyle="->"))
    #rpm_anno.set_visible(False)

    anno = zoom_ax.annotate("",
                xy=(0,0), xytext=(20,20),
                textcoords="offset points",
                bbox=dict(boxstyle="round", fc="w"),
                arrowprops=dict(arrowstyle="->"))

    anno.set_visible(False)

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

        if event.inaxes == zoom_ax:
            a_valid, a_index = pwra_scat.contains(event)
            b_valid, b_index = pwrb_scat.contains(event)
            e_valid, e_index = eny_scat.contains(event)
            anno.set_visible(a_valid or b_valid or e_valid)
            if a_valid:
                pos = pwra_scat.get_offsets()[a_index["ind"][0]]
                anno.xy = pos
                anno.set_text("Stroke Power {:.0f}W\nTime {:.3f}s".format(pos[1], pos[0]))
                fig.canvas.draw_idle()
            elif b_valid:
                pos = pwrb_scat.get_offsets()[b_index["ind"][0]]
                anno.xy = pos
                anno.set_text("Stroke Power {:.0f}W\nTime {:.3f}s".format(pos[1], pos[0]))
                fig.canvas.draw_idle()
            elif e_valid:
                pos = eny_scat.get_offsets()[e_index["ind"][0]]
                anno.xy = pos
                anno.set_text("Flywheel Energy {:.0f}J\nTime {:.3f}s".format(pos[1], pos[0]))
                fig.canvas.draw_idle()

    def spanselect(xmin, xmax):

        indmin, indmax = np.searchsorted(eny_x, (xmin, xmax))
        indmax = min(len(eny_x) - 1, indmax)

        eny_region_x = eny_x[indmin:indmax]
        eny_region_y = eny_y[indmin:indmax]

        indmin, indmax = np.searchsorted(pwra_x, (xmin, xmax))
        indmax = min(len(eny_x) - 1, indmax)

        pwra_region_x = pwra_x[indmin:indmax]
        pwra_region_y = pwra_y[indmin:indmax]

        indmin, indmax = np.searchsorted(pwrb_x, (xmin, xmax))
        indmax = min(len(eny_x) - 1, indmax)

        pwrb_region_x = pwrb_x[indmin:indmax]
        pwrb_region_y = pwrb_y[indmin:indmax]

        if len(eny_region_x) >= 2:
            zoom_eny.set_data(eny_region_x, eny_region_y)
            zoom_pwra.set_data(pwra_region_x, pwra_region_y)
            zoom_pwrb.set_data(pwrb_region_x, pwrb_region_y)

            eny_temp  = zoom_ax.scatter(eny_region_x,  eny_region_y )
            pwra_temp = zoom_ax.scatter(pwra_region_x, pwra_region_y)
            pwrb_temp = zoom_ax.scatter(pwrb_region_x, pwrb_region_y)

            eny_scat.set_offsets(eny_temp.get_offsets())
            pwra_scat.set_offsets(pwra_temp.get_offsets())
            pwrb_scat.set_offsets(pwrb_temp.get_offsets())

            zoom_ax.set_xlim(eny_region_x[0], eny_region_x[-1])
            zoom_ax.set_ylim(0, max(eny_region_y))
            fig.canvas.draw_idle()

    span = SpanSelector(
        world_ax,
        spanselect,
        "horizontal",
        useblit=True,
        props=dict(alpha=0.5, facecolor="tab:blue"),
        interactive=True,
        drag_from_anywhere=True)

    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.tight_layout()
    plt.show()
