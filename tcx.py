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

tcx_preamble = """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
  xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
  xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"
  xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
  xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"
  xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">
  <Activities>
    <Activity Sport="Kayaking">
      <Id>{}Z</Id>
      <Lap StartTime="{}Z">
        <TotalTimeSeconds>{}</TotalTimeSeconds>
        <DistanceMeters>{}</DistanceMeters>
        <MaximumSpeed>{}</MaximumSpeed>
        <Calories>{}</Calories>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
        <Track>
"""

tcx_trackpoint = """          <Trackpoint>
            <Time>{}Z</Time>
            <Position>
              <LatitudeDegrees>{}</LatitudeDegrees>
              <LongitudeDegrees>{}</LongitudeDegrees>
            </Position>
            <AltitudeMeters>{}</AltitudeMeters>
            <DistanceMeters>{}</DistanceMeters>
            <Extensions>
              <ns3:TPX>
                <ns3:Speed>{}</ns3:Speed>
              </ns3:TPX>
            </Extensions>
          </Trackpoint>
"""

tcx_postamble = """        </Track>
        <Extensions>
          <ns3:LX>
            <ns3:AvgSpeed>{}</ns3:AvgSpeed>
          </ns3:LX>
        </Extensions>
      </Lap>
      <Creator xsi:type="Device_t">
        <Name>LogicMonkey Xayax One</Name>
        <UnitId>0000000001</UnitId>
        <ProductID>0000</ProductID>
        <Version>
          <VersionMajor>0</VersionMajor>
          <VersionMinor>0</VersionMinor>
          <BuildMajor>0</BuildMajor>
          <BuildMinor>0</BuildMinor>
        </Version>
      </Creator>
    </Activity>
  </Activities>
  <Author xsi:type="Application_t">
    <Name>Piyak</Name>
    <Build>
      <Version>
        <VersionMajor>0</VersionMajor>
        <VersionMinor>0</VersionMinor>
        <BuildMajor>0</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
    </Build>
    <LangID>en</LangID>
    <PartNumber>000-A0000-00</PartNumber>
  </Author>
</TrainingCenterDatabase>"""
