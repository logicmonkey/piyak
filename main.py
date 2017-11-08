#!/usr/bin/env python

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

from datetime import datetime, timedelta

import random
import math

from generate_track import generate_track
from tcx import tcx_preamble, tcx_trackpoint, tcx_postamble

class AppGrid(GridLayout):

    def __init__(self, **kwargs):
        super(AppGrid, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 1./60.)

        self.elapsed = timedelta(0)

        self.pin_eventcount = 0
        self.pin_delta      = 0

        # course progress tracking
        self.track, self.lap_distance = generate_track('gerono', 'waikiki')
        self.trackptr   = 0
        self.lap_count  = 0
        self.timestamps = []
        self.time_start = datetime.now()

    def update(self, *args):

        if self.ids.i_elapsed.ids.i_buttons.ids.i_reset.state == 'down':
            self.elapsed                          = timedelta(0)
            self.ids.i_distspeed.ids.i_speed.text = '[b]0.0[/b] km/h'
            self.ids.i_distspeed.ids.i_dist.text  = '[b]0[/b] m'
            self.ids.i_gauge.angle                = 0.0
            self.ids.i_map.polyline               = []
            self.trackptr                         = 0
            self.lap_count                        = 0
            self.timestamps                       = []
            self.time_start                       = datetime.now()

            self.pin_eventcount = 0
            self.pin_delta      = 0

        hour, remr = divmod(self.elapsed.seconds, 60*60)
        mins, secs = divmod(remr, 60)
        self.ids.i_elapsed.ids.i_elapsed.text = "{:02d}:{:02d}:{:02d}".format(hour, mins, secs)

        if self.ids.i_elapsed.ids.i_buttons.ids.i_playpause.state == 'down':
            time_now = datetime.now()

            if self.play_mode == 0:
                self.play_mode = 1
            else:
                self.elapsed += time_now - self.time_last

            self.time_last = time_now

            # test value dummies - real pin samples need to go here
            self.pin_eventcount += 10 #8./60.
            self.pin_delta      = 75000 + 7500*math.sin(self.pin_eventcount/1500)

            # the GPIO pin timer clock is 1 MHz <=> 1 us period
            # count hundreds of rpm, i.e. hrpm = 60*1E6/(100*delta)
            hrpm = 600000 / self.pin_delta
            # using 750 rpm = 11 kph as a model, kph = rpm * 11/750
            # then kph = 60*1E6/delta * 11/750 = 880000/delta
            kph  = 880000 / self.pin_delta        # 11 kph = 750 rpm
            # using 60 mins * 750 rpm = 11 km, 1 rev = 11E3/(60*750) metres
            # 1 rev = 11000/(60*750) = 11/45 = 0.244.. m
            dist = self.pin_eventcount * 0.2444444444

            # update the telemetry based on the numbers
            self.ids.i_gauge.angle                = -22.5 * hrpm
            self.ids.i_distspeed.ids.i_speed.text = '[b]{0:.1f}[/b] km/h'.format(kph)
            self.ids.i_distspeed.ids.i_dist.text  = '[b]{0:.0f}[/b] m'.format(dist)

            # check progress along the track (course)
            if dist > (self.track[self.trackptr]['dist'] + self.lap_count*self.lap_distance):
                self.timestamps.append({'time': time_now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3], 'speed': kph, 'dist': dist})
                # let the trackpointer roll over and update the lap count
                self.ids.i_map.polyline.append(self.track[self.trackptr]['x'])
                self.ids.i_map.polyline.append(self.track[self.trackptr]['y'])
                self.lap_count, self.trackptr = divmod(len(self.timestamps), len(self.track))

        else:
            self.play_mode = 0

        if self.ids.i_elapsed.ids.i_buttons.ids.i_exit.state == 'down':
            if self.elapsed.seconds > 0:

                # grab the final value from the pin
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
            #pin.cancel()
            #device.stop()

            App.get_running_app().stop()

class GaugeBox(BoxLayout):
    angle = NumericProperty(0)

class MapBox(BoxLayout):
    polyline = ListProperty([])

class DistSpeedBox(BoxLayout):
    pass

class ElapsedBox(BoxLayout):
    pass

class ButtonsBox(BoxLayout):
    pass

class PlayPauseButton(ToggleButtonBehavior, Image):
    pass

class PiyakApp(App):
    def build(self):
        return AppGrid()

if __name__ == "__main__":
    PiyakApp().run()
