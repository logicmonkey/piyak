#!/usr/bin/env python

'''
Piyak - a program to monitor and log the effort on a kayak ergo.
        Python on Raspberry Pi, with a user interface implemented
        in Kivy. The program should run in a dummy "demomode" if the
        Raspberry Pi pigpio library is not found. This allows it to
        be run/tested/modified on a platform other than Raspberry Pi

Copyright (c) 2017 Piers Barber

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
Raspberry Pi pins 1,3,9 are used. GPIO2 is pulled high through a 4k7 resistor
The standard bike computer sensor fitted to a Lawler ergo is a normally open
switch.

                                      /
                      4k7  +---------o  o----------+
                      ___  |        sensor         |
                   +-|___|-#                       |
                   |       |                       |
                   1       3      [5]     [7]      9
                  3V3    GPIO2                    GND
'''

from kivy.app import App

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.behaviors import ToggleButtonBehavior, ButtonBehavior
from kivy.uix.button import Button

from kivy.graphics.vertex_instructions import Line, Rectangle

from kivy.properties import NumericProperty, ListProperty

from kivy.clock import Clock

from kivy.core.window import Window

from datetime import datetime, timedelta

import math

from collections import deque

from generate_track import generate_track
from tcx import tcx_preamble, tcx_trackpoint, tcx_postamble

class Piyak(BoxLayout):

    needle    = NumericProperty(0)
    polyline  = ListProperty([])
    play_mode = NumericProperty(0)

    global demomode, forensics

    def __init__(self, **kwargs):
        super(Piyak, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 1./60.)

        self.time_start = datetime.now()

        if not demomode:
            GPIO_PIN    = 2
            self.device = pigpio.pi()
            self.pin    = gpio_pin(self.device, GPIO_PIN)
            if forensics:
                self.forensics = open('forensics_{}.csv'.format(self.time_start.strftime("%Y%m%d%H%M")), 'w')

        self.elapsed        = timedelta(0)
        self.pin_delta      = deque([(1,0),(1,0),(1,0)], 3) # double ended queue = shift register 3 deep
        self.pin_eventcount = 0
        self.rot_ke_max     = 0.0                                        # power calc requires a maximum...
        self.max_timestamp  = datetime.now()
        self.rot_ke_min     = deque([0.0,0.0], 2)                        # ...and two minima
        self.stroke         = deque([datetime.now(), datetime.now()], 2) # stroke rate requires two minima

        # course progress tracking
        self.track, self.lap_distance = generate_track('gerono', 'waikiki')
        self.trackptr   = 0
        self.lap_count  = 0
        self.timestamps = []

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'x':
            self.exit_cbf()
        elif keycode[1] == 'r':
            self.reset_cbf()
        elif keycode[1] == 'spacebar':
            self.playpause_cbf()

        return True

    def update(self, *args):
        # constants for the revoltion period shift register elements
        NEW  = 2
        PREV = 1
        OLD  = 0

        def rot_ke(rotation_time):
            # SI unit for moment of inertia is kg metres squared (not grammes)
            # constants
            mass   = 4.360  # mass of Lawler flywheel in kilogrammes
            radius = 0.200  # radius of Lawler flywheel in metres

            period = rotation_time * 1e-6 # microseconds to seconds

            # w  = 2*pi/period (angular velocity omega = 2 pi radians * revolutions/second)
            # I  = 0.5*m*r^2 (half m radius squared)
            # KE = 0.5*I*w^2 (half I omega squared)

            return mass*(radius*math.pi/period)**2

        if self.play_mode == 1:
            time_now       = datetime.now()
            self.elapsed  += time_now - self.time_last
            self.time_last = time_now

            # on a real system we need to update the elapsed time even if there
            # are no events accumulated yet because the user isn't ready
            #
            hour, remr = divmod(self.elapsed.seconds, 60*60)
            mins, secs = divmod(remr, 60)
            self.ids.i_elapsed.text = "{:02d}:{:02d}:{:02d}".format(hour, mins, secs)

            if not demomode:
                if self.pin_eventcount != self.pin._eventcount and self.pin._delta != None:
                    # shift in the new measured rotation period on every update, along with a timestamp
                    self.pin_delta.append((self.pin._delta, time_now))

                    if forensics:
                        self.forensics.write("{},{},{}\n".format(self.elapsed, self.pin_eventcount, self.pin_delta[NEW][0]))

                self.pin_eventcount = self.pin._eventcount
            else:
                self.pin_delta.append((75000.0 + 4000.0*math.sin(self.pin_eventcount/5.0), time_now))
                self.pin_eventcount += 1000000.0/(60.0*self.pin_delta[NEW][0])

            if self.pin_delta[NEW][0] != None and self.pin_eventcount != 0:

                # the GPIO pin timer clock is 1MHz <=> 1us period
                # count hundreds of rpm, i.e. hrpm = 60*1E6/(100*delta)
                hrpm = 600000.0 / self.pin_delta[NEW][0]
                # using 750rpm = 11km/h as a model, km/h = rpm * 11/750
                # then kph = 60*1E6/delta * 11/750 = 880000/delta
                kph  = 880000.0 / self.pin_delta[NEW][0]     # 11km/h = 750rpm
                # using 60 minutes * 750rpm = 11km, 1 rev = 11E3/(60*750) metres
                # 1 rev = 11000/(60*750) = 11/45 = 0.2444m
                dist = self.pin_eventcount * 0.2444444444

                # look at the last three rotation measurements (NEW, PREV, OLD) to detect a local
                # min or max (start and end of power phase)
                if self.pin_delta[NEW][0] > self.pin_delta[PREV][0] and self.pin_delta[PREV][0] < self.pin_delta[OLD][0]:
                    # slow -> fast -> slow makes PREV a local maximum
                    self.rot_ke_max = rot_ke(self.pin_delta[PREV][0])
                    self.max_timestamp = self.pin_delta[PREV][1]

                elif self.pin_delta[NEW][0] < self.pin_delta[PREV][0] and self.pin_delta[PREV][0] > self.pin_delta[OLD][0]:
                    # fast -> slow -> fast makes PREV a local minimum
                    self.rot_ke_min.append(rot_ke(self.pin_delta[PREV][0]))
                    self.stroke.append(self.pin_delta[PREV][1])

                power_timedelta = self.max_timestamp - self.stroke[0]
                setup_timedelta = self.stroke[1] - self.max_timestamp

                tpower = power_timedelta.seconds + 1e-6*power_timedelta.microseconds
                tsetup = power_timedelta.seconds + 1e-6*power_timedelta.microseconds

                energy_in = 0
                if tsetup != 0: # check for zero divide
                    energy_in = self.rot_ke_max - self.rot_ke_min[0] + tpower/tsetup * (self.rot_ke_max - self.rot_ke_min[1])

                # update the telemetry based on the numbers
                self.needle            = -22.5 * hrpm
                self.ids.i_speed.text  = '[b]{0:.1f}[/b]km/h'.format(kph)
                self.ids.i_dist.text   = '[b]{0:.0f}[/b]m'.format(dist)

                stroke_timedelta = self.stroke[1] - self.stroke[0] # the time between two local minima
                stroke_period = stroke_timedelta.seconds + 1e-6*stroke_timedelta.microseconds

                # stroke rate is 1 minute divided by the non-zero stroke period
                if stroke_timedelta != timedelta(0):
                    self.ids.i_stroke.text = '[b]{0:.0f}[/b]'.format(60.0/stroke_period)
                    self.ids.i_power.text  = '[b]{0:.0f}[/b]W'.format(energy_in/stroke_period)

                # check progress along the track (course)
                if dist > (self.track[self.trackptr]['dist'] + self.lap_count*self.lap_distance):
                    self.timestamps.append({'time': time_now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3], 'speed': kph, 'dist': dist})
                    # let the trackpointer roll over and update the lap count
                    self.polyline.append(self.track[self.trackptr]['x'])
                    self.polyline.append(self.track[self.trackptr]['y'])
                    self.lap_count, self.trackptr = divmod(len(self.timestamps), len(self.track))

    def playpause_cbf(self):
        if self.play_mode == 0:
            self.play_mode = 1
            self.time_last = datetime.now()
        else:
            self.play_mode = 0

    def reset_cbf(self):
        self.elapsed            = timedelta(0)
        self.pin_delta          = deque([(0,timedelta(0)),(0,timedelta(0)),(0,timedelta(0))], 3)
        self.pin_eventcount     = 0
        self.ids.i_speed.text   = '[b]0.0[/b]km/h'
        self.ids.i_dist.text    = '[b]0[/b]m'
        self.ids.i_elapsed.text = '00:00:00'
        self.ids.i_power.text   = '[b]0[/b]W'
        self.ids.i_stroke.text  = '[b]0[/b]'
        self.needle             = 0.0
        self.polyline           = []
        self.trackptr           = 0
        self.lap_count          = 0
        self.timestamps         = []
        self.time_start         = datetime.now()

    def exit_cbf(self):
        if self.elapsed.seconds > 0:

            total_revs     = self.pin_eventcount
            total_distance = self.pin_eventcount * 0.2444444444

            # -------------------------------------------------------------------------
            # the app has run, now generate the activity file in tcx format

            max_speed = 0
            for x in self.timestamps:
                if x['speed'] > max_speed:
                    max_speed = x['speed']

            calories  = 1000*self.elapsed.seconds/3600        # crude calc: 1000 calories/hour
            elevation = 0

            average_speed = total_distance / self.elapsed.seconds

            time_start_str = self.time_start.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] # format for tcx file

            activity = open('activity_{}.tcx'.format(self.time_start.strftime("%Y%m%d%H%M")), 'w')
            activity.write(tcx_preamble.format(time_start_str,
                                               time_start_str,
                                               self.elapsed.seconds,
                                               total_distance,
                                               max_speed,
                                               calories))

            for tp in range(len(self.timestamps)): # loop over all trackpoints reached
                activity.write(tcx_trackpoint.format(self.timestamps[tp]['time'],
                               self.track[tp%len(self.track)]['lat'],
                               self.track[tp%len(self.track)]['lon'],
                               elevation,
                               self.timestamps[tp]['dist'],
                               self.timestamps[tp]['speed']))

            activity.write(tcx_postamble.format(average_speed))
            activity.close()

            print("Total distance: {}".format(total_distance))
            hour, remr = divmod(self.elapsed.seconds, 60*60)
            mins, secs = divmod(remr, 60)
            print("Total time: {:02d}:{:02d}:{:02d}".format(hour, mins, secs))
            print("Average speed: {}".format(average_speed))
            print("Total revs: {}".format(total_revs))
            print("Lap length: {}".format(self.lap_distance))
            print("Total laps: {}".format(total_distance/self.lap_distance))
            print("File: {}".format('activity_{}.tcx'.format(self.time_start.strftime("%Y%m%d%H%M"))))

        # exit cleanly by turning off the pin activities and stopping the device
        if not demomode:
            self.pin.cancel()
            self.device.stop()
            if forensics:
                self.forensics.close()

        App.get_running_app().stop()

class PiyakApp(App):
    def build(self):
        return Piyak()

if __name__ == "__main__":
    try:
        import pigpio
        demomode = False
        from gpio_pin import gpio_pin
        forensics = True
    except:
        demomode = True

    PiyakApp().run()
