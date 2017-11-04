from kivy.app import App

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.behaviors import ToggleButtonBehavior, ButtonBehavior
from kivy.uix.button import Button

from kivy.properties import NumericProperty

from kivy.clock import Clock

from datetime import datetime

import random
import math

from generate_track import generate_track

class AppGrid(GridLayout):

    def __init__(self, **kwargs):
        super(AppGrid, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 1/60.0)

        self.old_play_not_pause = 0
        self.play_not_pause     = 0

        # elapsed gets reset to a zero time delta
        self.interval_start = datetime.now()
        self.elapsed = self.interval_start - self.interval_start

        self.pin_eventcount = 0
        self.pin_delta      = 0

        # course progress tracking
        self.track, self.lap_distance = generate_track('gerono', 'waikiki')
        self.trackptr   = 0
        self.lap_count  = 0
        self.timestamps = []

    def update(self, *args):

        if self.ids.i_elapsed.ids.i_buttons.ids.i_reset.state == 'down':
            self.old_play_not_pause               = 0
            self.play_not_pause                   = 0
            self.elapsed -= self.elapsed          # 0
            self.ids.i_elapsed.ids.i_elapsed.text = '00:00:00'
            self.ids.i_distspeed.ids.i_speed.text = '[b]0.0[/b] km/h'
            self.ids.i_distspeed.ids.i_dist.text  = '[b]0[/b] m'
            self.ids.i_gauge.angle                = 0.0
            self.trackptr                         = 0
            self.lap_count                        = 0
            self.timestamps                       = []

            self.pin_eventcount = 0
            self.pin_delta      = 0

        # read the play/pause button state
        #
        if self.ids.i_elapsed.ids.i_buttons.ids.i_playpause.state == 'down':
            self.play_not_pause = 1
        else:
            self.play_not_pause = 0

        # exiting pause, so take a snapshot of the time
        #
        if self.old_play_not_pause == 0 and self.play_not_pause == 1:
            self.interval_start = datetime.now()

        if self.play_not_pause == 1:

            # this is how we enter pause from play
            #
            self.old_play_not_pause = self.play_not_pause

            time_now = datetime.now()

            self.elapsed += time_now - self.interval_start
            hour, remr = divmod(self.elapsed.seconds, 60*60)
            mins, secs = divmod(remr, 60)

            self.ids.i_elapsed.ids.i_elapsed.text = "{:02d}:{:02d}:{:02d}".format(hour, mins, secs)

            # test value dummies - real pin samples need to go here
            self.pin_eventcount += 10 #8./60.
            self.pin_delta      = 75000

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
                self.lap_count, self.trackptr = divmod(len(self.timestamps), len(self.track))

        if self.ids.i_elapsed.ids.i_buttons.ids.i_exit.state == 'down':
            App.get_running_app().stop()

class GaugeBox(BoxLayout):
    angle = NumericProperty(0)

class DistSpeedBox(BoxLayout):
    pass

class ElapsedBox(BoxLayout):
    pass

class ButtonsBox(BoxLayout):
    pass

class PlayPauseButton(ToggleButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(PlayPauseButton, self).__init__(**kwargs)
        self.source = 'button_play.png'

    def on_state(self, widget, value):
        if value == 'down':
            self.source = 'button_pause.png'
        else:
            self.source = 'button_play.png'

class PiyakApp(App):
    def build(self):
        return AppGrid()

if __name__ == "__main__":
    PiyakApp().run()
