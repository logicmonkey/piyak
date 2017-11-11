#!/usr/bin/env python

import pigpio

class gpio_pin:
   def __init__(self, device, gpio):
      self.device = device
      self.gpio   = gpio

      self._watchdog   = 200 # milliseconds
      self._eventcount = 0
      self._last_edge  = None
      self._delta      = None

      # debounce in software
      #   the magnet is at 15 cm radius
      #   one revolution has circumference 2pi*0.15 = 3.2*0.3 = 0.96 m
      #   a 5 mm magnet accounts for 0.005/0.96 of one revolution
      #   at 20 Hz (1200 rpm) one revolution takes 50 ms
      #   time for magnet over the sensor is 50*0.005/0.96 = 260 us
      #     => discard triggers of less than 200 us duration
      #   this is easily achievable with the 1 MHz (1 us) clock

      DEBOUNCE = 200 # microseconds

      device.set_mode(gpio, pigpio.INPUT)
      device.set_glitch_filter(gpio, DEBOUNCE)
      device.set_watchdog(gpio, self._watchdog)

      # finally instantiate a callback function for activity on this pin
      self._cb = device.callback(gpio, pigpio.RISING_EDGE, self._cbf)

   def _cbf(self, gpio, level, now):
      if level == 1: # rising edge

         if self._last_edge is not None:
            self._delta = pigpio.tickDiff(self._last_edge, now)

         self._eventcount += 1
         self._last_edge = now

      elif level == 2: # watchdog timeout

         if self._delta is not None:
            if self._delta < 2000000000: # 2e9
               self._delta += (self._watchdog * 1000)

   def cancel(self):
      # clean up
      self.device.set_watchdog(self.gpio, 0) # zero watchdog
      self._cb.cancel()                      # cancel the callback
