#!/usr/bin/env python

tcx_preamble = """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
  xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
  xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"
  xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
  xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"
  xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">
  <Activities>
    <Activity Sport="Canoeing">
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
    <Name>LogicMonkey Tachometer</Name>
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
