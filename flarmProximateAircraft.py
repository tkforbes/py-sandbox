import math

import sys

from ognRegistrations import OgnRegistration

proximateAircraftIndex = {
    'proximateRecordIndicator' : 0, # PFLAA
    'alarmLevel' : 1,
    'relativeNorth' : 2,
    'relativeEast' : 3,
    'relativeVertical' : 4,
    'idType' : 5,
    'radioId' : 6,
    'track' : 7,
    'turnRate' : 8,
    'groundSpeed' : 9,
    'climbRate' : 10,
    'aircraftType' : 11
}

class FlarmProximateAircraft:
    def __init__(self):
        self.observations = 0
        self.maxDistance = 0

    def set(self, timestamp, nmea_flaa, ):

        # PFLAA
        # must be a PFLAA sentence type i.e. value must be 'A'
        try:
            ndx = proximateAircraftIndex.get('proximateRecordIndicator')
            sentenceType = nmea_flaa.data[ndx]
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # hey, I can't set this sentence.
        if not (sentenceType == 'A'): return False

        # alarm level. valid values: 0 - 3
        try:
            ndx = proximateAircraftIndex.get('alarmLevel')
            int(ndx)
            alarmLevel = int(nmea_flaa.data[ndx])
            if not (alarmLevel >= 0 and alarmLevel <= 3):
                raise Exception("alarm level out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # relative north. range: from -32768 to 32767.
        try:
            ndx = proximateAircraftIndex.get('relativeNorth')
            int(ndx)
            relativeNorth = int(nmea_flaa.data[ndx])
            if not (relativeNorth >= -32768 and relativeNorth <= 32767):
                raise Exception("relative north out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # relative east. range: from -32768 to 32767.
        try:
            ndx = proximateAircraftIndex.get('relativeEast')
            int(ndx)
            relativeEast = int(nmea_flaa.data[ndx])
            if not (relativeEast >= -32768 and relativeEast <= 32767):
                raise Exception("relative east out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # relative vertical. range: from -32768 to 32767.
        try:
            ndx = proximateAircraftIndex.get('relativeVertical')
            int(ndx)
            relativeVertical = int(nmea_flaa.data[ndx])
            if not (relativeVertical >= -32768 and relativeVertical <= 32767):
                raise Exception("relative vertical out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # id type. integer. range: from 0 to 3.
        try:
            ndx = proximateAircraftIndex.get('idType')
            int(ndx)
            idType = int(nmea_flaa.data[ndx])
            if not (idType >= 0 and idType <= 3):
                raise Exception("id type out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # radio id
        # 6-digit hexadecimal value (e.g. “5A77B1”) as configured in the
        # target’s PFLAC,,IDsentence. The interpretation is delivered in
        # <ID-Type>.Field is empty if no identification is known (e.g.
        # Transponder Mode-C). Random ID will be sent if stealth mode is
        # activated either on the target or own aircraft and no alarm is
        # present at this time.
        try:
            ndx = proximateAircraftIndex.get('radioId')
            int(ndx)
            radioIdLong = nmea_flaa.data[ndx]
            # extract radio id from left of the '!' in the field. e.g.
            # it would usually look like this 'C03745!FLR_C03745'
            radioId = radioIdLong[0:radioIdLong.find("!")]
            if (len(radioId) != 6):
                msg = "radio id must be 6 chars in length. " + radioId
                raise Exception(msg)
            hex(int(radioId, 16)) # ensure radio id can convert to hex.
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # track.
        # Decimal integer value. Range: from 0 to 359.The target’s true
        # ground track in degrees. The value 0 indicates a true north track.
        # This field is empty if stealth mode is activated either on the
        # target or own aircraft and for non-directional targets.
        try:
            ndx = proximateAircraftIndex.get('track')
            int(ndx)
            track = int(nmea_flaa.data[ndx])
            if not (idType >= 0 and idType <= 339):
                raise Exception("track out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # turn rate.
        # Currently this field is empty.
        try:
            ndx = proximateAircraftIndex.get('turnRate')
            int(ndx)
            turnRate = nmea_flaa.data[ndx]
            if not (len(turnRate) == 0):
                raise Exception("turn rate found. unexpected.")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # groundSpeed.
        # Decimal integer value.  Range: from 0 to 32767.The target’s
        # ground speed in m/s. The field is 0 to indicate that the aircraft
        # is not moving, i.e. onground. This field is empty if stealth mode
        # is activated either on the target or own aircraft and for
        # non-directional targets.
        try:
            ndx = proximateAircraftIndex.get('groundSpeed')
            int(ndx)
            groundSpeed = int(nmea_flaa.data[ndx])
            if not (groundSpeed >= 0 and groundSpeed <= 32767):
                raise Exception("ground speed out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # climb rate.
        # Decimal fixed point number with one digit after the radix point
        # (dot). Range: from -32.7 to 32.7.The target’s climb rate in m/s.
        # Positive values indicate a climbing aircraft. This field is empty
        # if stealth mode is activated either on the target or own aircraft
        # and for non-directional targets.
        try:
            ndx = proximateAircraftIndex.get('climbRate')
            int(ndx)
            if ((len(nmea_flaa.data[ndx])) == 0):
                # target not moving, so climb rate is zero
                climbRate = 0
            else:
                climbRate = float(nmea_flaa.data[ndx])

            if not (climbRate >= -32.7 and climbRate <= 32.7):
                raise Exception("climb rate out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # aircraft type.
        # Hexadecimal value. Range: from 0 to F.
        # Aircraft types:
        #           0 = unknown
        #           1 = glider / motor glider
        #           2 = tow / tug plane
        #           3 = helicopter / rotorcraft
        #           4 = skydiver
        #           5 = drop plane for skydivers
        #           6 = hang glider (hard)
        #           7 = paraglider (soft)
        #           8 = aircraft with reciprocating engine(s)
        #           9 = aircraft with jet/turboprop engine(s)
        #           A =unknown
        #           B = balloon
        #           C = airship
        #           D = unmanned aerial vehicle (UAV)
        #           E = unknownF = static object
        try:
            ndx = proximateAircraftIndex.get('aircraftType')
            int(ndx)
            aircraftType = nmea_flaa.data[ndx]
            if (len(aircraftType) != 1):
                msg = "aircraft type must be a single char hex number. " + aircraftType
                raise Exception(msg)
            hex(int(aircraftType, 16)) # ensure ac type can convert to hex.
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()


        theOgnReg = OgnRegistration()
        self.aircraftId = theOgnReg.getAircraft(radioId)
        self.timestamp = timestamp

        self.relativeNorth = relativeNorth
        self.relativeEast = relativeEast
        self.relativeVertical = relativeVertical
        self.track = track
        self.speed = groundSpeed
        self.climbRate = climbRate

        self.observations += 1
        if (self.getDistance() > self.maxDistance ):
            self.maxDistance = self.getDistance()

        return True

    def report(self):
        print("")
        print("Proximiate aircraft")
        print("===================")
        print("observations:%6d" % self.observations,
            "max distance:%6d" % self.maxDistance
            )

    def print(self):
        """
        if (self.getDistance() > 3000): return
        if (self.getAltitudeAGL() > 40): return
        if (self.getSpeed() < 5): return
        """

        print(self.aircraftId,
            "%-17s" % self.timestamp,
            "dist:%5d" % self.getDistance(),
            "alt AGL:%4d" % self.getAltitudeAGL(),
            "speed: %3d" % self.getSpeed(),
            "track: %3d" % self.track,
            "climb: %3s" % self.climbRate
            )

    def getSpeed(self):
        # speed in kph
        return self.speed*3.6

    def getAltitudeAGL(self):
        return self.relativeVertical

    def getDistance(self):
        n = abs(self.relativeNorth)
        e = abs(self.relativeEast)
        return int(math.sqrt( n*n+e*e))
