# Piyak - a Raspberry Pi based kayak ergo training aid

![Screenshot](https://raw.githubusercontent.com/logicmonkey/piyak/master/piyak_screenshot.png)

## Features
* Displays time, distance, speed, RPM
* Shows progress around a virtual course
* Logs activity to a TCX file for upload to Strava or other
* Forensic mode logs the speed of each flywheel rotation for the entire session (see below)
* Should work with a touch screen - although this is untested
* Keyboard controls: r - reset, spacebar - play/pause, x - exit
* Demo mode generates synthetic movement data enabling development away from a Raspberry Pi

A short clip on YouTube:

[![IMAGE ALT TEXT](https://i.ytimg.com/vi/152-v3C7pP8/hqdefault.jpg)](http://www.youtube.com/watch?v=152-v3C7pP8 "Piyak in use")

## Forensics
The Raspberry Pi times the duration between events using a 1MHz clock - in theory to the nearest microsecond. So counting the revs on a wheel spinning at 900 rpm (15 times/second) should be no problem for it. The forensic_DATETIME.csv file contains the duration of every revolution and can be read into your favourite spreadsheet program.

This is for interest only - a kayak ergo is additional to (not a subsitute for) time on the water. Don't read too much into it.

Let's read too much into it. Here's a 70 second kayak session:

![Short Session](https://raw.githubusercontent.com/logicmonkey/piyak/master/piyak_session.png)

The vertical axis is RPM, time in seconds is along the bottom. Notice the jerky spin-up as a working speed is achieved, the oscillation in the work period and the smooth but non-linear spin down. Zooming in on a short work period shows every other stroke is slightly stronger than the previous:

![Zoom](https://raw.githubusercontent.com/logicmonkey/piyak/master/piyak_zoom.png)

I clearly have a stronger side. Zooming right in, each point represents one flywheel revolution:

![Left Right](https://raw.githubusercontent.com/logicmonkey/piyak/master/piyak_forensic.png)

Notice that the increase in speed is tailing off towards the end of each stroke and that the spin down before the next stroke is approximately linear. You can kind of make out the catch-drive-recovery-setup phases.

We could increase the accuracy of data by adding more magnets to the flywheel and timing quarter revs for example.

Amusing - but not really useful.
