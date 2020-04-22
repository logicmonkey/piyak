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
