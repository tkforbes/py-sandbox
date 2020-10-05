from ognRegistrations import OgnRegistration

import sys

class Pflau:

    # the fields of an NMEA PFLAU sentence
    priorityIndex = {
        'priorityRecordIndicator' : 0,  # PFLAU
        'rx' : 1,
        'tx' : 2,
        'gps' : 3,
        'power' : 4,
        'alarmLevel' : 5,
        'relativeBearing' : 6,
        'AlarmType' : 7,
        'relativeVertical' : 8,
        'relativeDistance' : 9,
        'radioId' : 10
    }

    # these are the cardinal directions of a 16-point compass
    cardinalDirection = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
        "N"
    ]

    #
    def __init__(self):
        self.maxDistance = 0
        self.observations = 0
        self.timestamp = 0
        self.relativeDistance = 0
        self.relativeVertical = 0
        self.relativeBearing = 0
        self.aircraftId = ''

    def getSource(self):
        return self.source

    def setMaxDistance(self):
        if (self.relativeDistance > self.maxDistance):
            self.maxDistance = self.relativeDistance

    #
    def set(self, timestamp, nmea):

        # PFLAU
        # must be a PFLAU sentence type i.e. value must be 'U'
        try:
            ndx = Pflau.priorityIndex.get('priorityRecordIndicator')
            sentenceType = nmea.data[ndx]
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # hey, I can't set this sentence.
        if not (sentenceType == 'U'): return False

        # rx
        # Decimal integer value. Range: from 0 to 99.
        #
        # Number of devices with unique IDs currently received regardless
        # of the horizontal or vertical separation.
        # Because the processing might be based on extrapolated historical
        # data, <Rx>might be lower than the number of aircraft in range,
        # i.e. there might be other traffic around (even if the number is
        # zero).
        #
        # Do not expect to receive <Rx> PFLAAsentences, because the number
        # of aircraft being processed might be higher or lower.
        try:
            ndx = Pflau.priorityIndex.get('rx')
            int(ndx)
            rx = int(nmea.data[ndx])
            if not (0 <= rx <= 99):
                raise Exception("rx out of range")
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # tx
        # Decimal integer value. Range: from 0 to 1.Transmission status: 1 for
        # OK and 0 for no transmission
        try:
            ndx = Pflau.priorityIndex.get('tx')
            int(ndx)
            tx = int(nmea.data[ndx])
            if not (tx in [0, 1]):
                raise Exception("tx out of range")
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # gps
        # Decimal integer value. Range: from 0 to 2.
        # GPS status:
        #       0 = no GPS reception
        #       1 = 3d-fix on ground, i.e. not airborne
        #       2 = 3d-fix when airborne
        #
        # If <GPS>goes to 0, FLARM will not work. Nevertheless, wait for
        # some seconds to issue any warnings.
        try:
            ndx = Pflau.priorityIndex.get('gps')
            int(ndx)
            gps = int(nmea.data[ndx])
            if not (gps in [0, 1, 2]):
                msg = "gps value " + str(gps) + ": out of range"
                raise Exception(msg)
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # power
        # Decimal integer value. Range: from 0 to 1.
        # Power status: 1 for OK and 0 for under-or over-voltage.
        try:
            ndx = Pflau.priorityIndex.get('power')
            int(ndx)
            power = int(nmea.data[ndx])
            if not (power in [0, 1]):
                raise Exception("power out of range")
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()


        # alarm level
        # Decimal integer value. Range: from 0 to 3.
        # Alarm level as assessed by FLARM:
        #   0 = no alarm (also used for no-alarm traffic information)
        #   1 = alarm, 13-18 seconds to impact
        #   2 = alarm, 9-12 seconds to impact
        #   3 = alarm, 0-8 seconds to impact
        #
        # Note: For Alert Zone alarm the alarm level cannot be more
        # than 1. Every 16 seconds for 4 seconds when inside the zone
        # alarm level is 1, otherwise is 0.
        try:
            ndx = Pflau.priorityIndex.get('alarmLevel')
            int(ndx)
            alarmLevel = int(nmea.data[ndx])
            if not (alarmLevel in [0, 1, 2, 3]):
                msg = "alarm level. value " + str(alarmLevel) + ": out of range"
                raise Exception(msg)
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # alarmtype
        # special note: process this ahead of relative bearing etc because
        #   its alarm type zerio causes relative bearing etc to be empty!
        #
        # Hexadecimal value. Range: from 0 to FF.
        # Type of alarm as assessed by FLARM
        #   0 = no aircraft within range or no-alarm traffic information
        #   2 = aircraft alarm
        #   3 = obstacle/Alert Zone alarm
        #
        # When data port >=7, the type of Alert Zone is sent as <AlarmType>
        # in the range 10..FF. Refer to the <ZoneType>parameter in the
        # PFLAOsentence for a description.
        try:
            ndx = Pflau.priorityIndex.get('AlarmType')
            int(ndx)

            # get alarm type. convert from hex but retain string form
            # in case it is required for printing.
            alarmTypeAsStr = nmea.data[ndx]
            alarmType = int(alarmTypeAsStr, 16)
            if not (alarmType in [0x00, 0x02, 0x03]):
                msg = "alarmType. value " + alarmTypeAsStr + ": invalid."
                raise Exception(msg)
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # alarm type is zero when no aircraft are in range. In that case,
        # there would not be a value for relative bearing, relative vertical
        # or relative distance. we won't pay any attention to type
        # zero records...
        if (alarmType == 0): return False

        # relativeBearing.
        # Decimal integer value. Range: -180 to 180.
        # Relative bearing in degrees from true ground track to the
        # intruder’s position. Positive values are clockwise. 0°
        # indicates that the object is exactly ahead. Field is empty
        # for non-directional targets or when no aircraft are within
        # range. For obstacle alarm and Alert Zone alarm, this field
        # is 0.
        try:
            ndx = Pflau.priorityIndex.get('relativeBearing')
            int(ndx)
            relativeBearing = int(nmea.data[ndx])
            if not (-180 <= relativeBearing <= 180):
                msg = "relativeBearing. value " + str(relativeBearing) + ": out of range"
                raise Exception(msg)
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # relativeVertical.
        # Decimal integer value. Range:from -32768 to 32767.
        # Relative vertical separation in meters above own position. Negative
        # values indicate that the other aircraft or obstacle is lower.
        # Field is empty when no aircraft are within rangeFor Alert Zone
        # and obstacle warnings, this field is 0.
        try:
            ndx = Pflau.priorityIndex.get('relativeVertical')
            int(ndx)
            relativeVertical = int(nmea.data[ndx])
            if not (-32768 <= relativeVertical <= 32767):
                msg = "relativeVertical. value " + str(relativeVertical) + ": out of range"
                raise Exception(msg)
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # relativeDistance.
        # Decimal integer value. Range: from 0 to 2147483647.
        # Relative horizontal distance in meters to the target or
        # obstacle. For non-directional targets this value is estimated
        # based on signal strength.
        # Field is empty when no aircraft are within range and no alarms
        # are generated.For Alert Zone, this field is 0.
        try:
            ndx = Pflau.priorityIndex.get('relativeDistance')
            int(ndx)
            relativeDistance = int(nmea.data[ndx])
            if not (0 <= relativeDistance <= 2147483647):
                msg = "relativeDistance. value " + str(relativeDistance) + ": out of range"
                raise Exception(msg)
        except Exception as e:
            print(nmea, msg, ":", e)
            sys.exit()


        # id (radio id)
        # The field is omitted for protocol version < 4.
        # 6-digit hexadecimal value (e.g. “5A77B1”) as configured in the
        # target’s PFLAC,,ID.
        # The interpretation is only delivered in <ID-Type>in the
        # PFLAAsentence (if received for the same aircraft).
        # The <ID>field is the ICAO 24-bit addressfor Mode-S targets and
        # a FLARM-generated ID for Mode-C targets. The ID for Mode-C
        # targets may change at any time.
        # Field is empty when no aircraft are within range and no alarms
        # are generated.
        # For obstacles this field is set to FFFFFF. In case of Alert Zone
        # warning, the FLARM ID of the Alert Zone station is output.
        try:
            ndx = Pflau.priorityIndex.get('radioId')
            int(ndx)
            radioId = nmea.data[ndx]
            if (len(radioId) != 6):
                msg = "radio id must be 6 chars in length. " + radioId
                raise Exception(msg)
            hex(int(radioId, 16)) # ensure radio id can convert to hex.
        except Exception as e:
            #print(nmea, ":", e)
            return False
            sys.exit()

        ## end of field validation. now set values as appropriate.

        self.source = 'PFLAU'

        # will be set to radioId if aircraft not found.
        self.aircraftId = OgnRegistration().getAircraft(radioId)
        self.timestamp = timestamp
        self.relativeBearing = relativeBearing
        self.relativeVertical = relativeVertical

        self.relativeDistance = relativeDistance
        self.setMaxDistance()

        self.relativeBearing = relativeBearing
        self.observations += 1

        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        return True

    def printt(self, airfield):
        bearing = airfield.courseTrue + self.relativeBearing

        # correct the bearing, given that the airfield may have a heading
        # although it is supposed to be stationary!
        if (bearing < 0):
            bearing +=360
        elif (bearing > 359):
            bearing -=360

        if not (0 <= bearing <= 359):
            print("problem. bearing/course/distance", bearing)

        # only use a cardinal direction if the bearing is 0deg (N)
        # note: this is only a guess at this stage.
        if (airfield.courseTrue == 0):
            cardinalDirection = Pflau.sixteenWindCompassPoint(bearing)
        else:
            cardinalDirection = ''

        print(
            self.aircraftId,
            self.timestamp,
            #"\t dist:%5d" % self.relativeDistance,
            "\t%6dm" % self.relativeDistance,
            "%s" % cardinalDirection,
            "(%3ddeg) " % bearing,
            "%4dm above" % self.relativeVertical
            #"alt AGL:%4s" % self.relativeVertical,
            # "\t\t\t\t\trel brng:%s" % self.relativeBearing,
            #"brng:%s" % bearing
            # Pflau.sixteenWindCompassPoint(bearing)
            )

    def sixteenWindCompassPoint(bearing):
        try:
            int(bearing)
            # note that bearing could be float, therefore fractional
            # part used in comparison is important.
            if not (0 <= bearing < 360):
                raise Exception("bearing is out of range 0 - 359")
        except Exception as e:
            print(bearing, ":", e)
            sys.exit()

        points = 16           # number of points on this compass
        degreesPerPoint = 360/points
        offset = (degreesPerPoint/2)*-1  # first comparison at this number of degrees

        if (bearing + offset < 0):
            bearing += 360

        bearing += offset
        ndx = int(bearing/degreesPerPoint)+1
        return Pflau.cardinalDirection[ndx]

    def report(self):
        print("")
        print("Priority Intruder")
        print("=================")
        print("observations:%6d" % self.observations,
            "max distance:%6d" % self.maxDistance
            )
        return

    def getAircraftId(self):
        return self.aircraftId
