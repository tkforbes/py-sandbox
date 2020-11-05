import math

import pynmea2
import sqlite3

#import geopy
#import geopy.distance

#import sys

from ognRegistrations import OgnRegistration
from groundspeed import Groundspeed
from groundstation import Groundstation


class Observation:

    @staticmethod
    def r_earth(): return 6378.137 # radius of Earth in kms

    @staticmethod
    def is_pflau_sentence(sentence):
        if not (isinstance(sentence, pynmea2.nmea.ProprietarySentence)):
            return False

        if not (sentence.manufacturer == "FLA"):
            return False

        try:
            ndx = Observation.pflaa_index.get('pflaaRecordIndicator')
            sentenceType = sentence.data[ndx]
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # the sentence type must be 'U'.
        if not (sentenceType == 'U'):
            return False

        return True

    @staticmethod
    def is_pflaa_sentence(sentence):
        if not (isinstance(sentence, pynmea2.nmea.ProprietarySentence)):
            return False

        if not (sentence.manufacturer == "FLA"):
            return False

        try:
            ndx = Observation.pflaa_index.get('pflaaRecordIndicator')
            sentenceType = sentence.data[ndx]
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # the sentence type must be 'A'.
        if not (sentenceType == 'A'):
            return False

        return True

    pflaa_index = {
        'pflaaRecordIndicator' : 0, # PFLAA
        'alarm_level' : 1,
        'relative_north' : 2,
        'relative_east' : 3,
        'relative_vertical' : 4,
        'id_type' : 5,
        'radioId' : 6,
        'track' : 7,
        'turn_rate' : 8,
        'ground_speed' : 9,
        'climb_rate' : 10,
        'aircraft_type' : 11
    }

    def __init__(self):
        self.observations = 0
        self.distance_max = 0

    def get_track(self):
        return self.track

    def get_timestamp(self):
        return self.timestamp

    def get_alt_agl(self):
        return self.relative_vertical - Groundstation.height_of_groundstation()

    def get_distance(self):
        north = abs(self.relative_north)
        east = abs(self.relative_east)
        return int(math.sqrt(north*north+east*east))

    def get_aircraft_id(self):
        return self.aircraft_id

    def set_max_distance(self):
        if (self.get_distance() > self.distance_max ):
            self.distance_max = self.get_distance()

    def displace_lat_lon(self, groundstation):

        self.lat = groundstation.get_lat()
        + (self.relative_north / 1000 / Observation.r_earth()) * (180 / math.pi)

        self.lon = groundstation.get_lon()
        + (self.relative_east / 1000 / Observation.r_earth()) * (180 / math.pi) / math.cos(groundstation.get_lat() * math.pi/180)
        return

    def set(self, groundstation, nmea_flaa):

        # must be a PFLAA sentence type i.e. value must be 'A'
        try:
            ndx = Observation.pflaa_index.get('pflaaRecordIndicator')
            sentenceType = nmea_flaa.data[ndx]
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # the sentence type must be 'A'. Any other value indicates a serious problem!
        if not (sentenceType == 'A'): return False

        # alarm level. valid values: 0 - 3
        try:
            ndx = Observation.pflaa_index.get('alarm_level')
            int(ndx)
            alarm_level = int(nmea_flaa.data[ndx])
            if not (0 <= alarm_level <= 3):
                raise Exception("alarm level out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # relative north. range: from -32768 to 32767.
        try:
            ndx = Observation.pflaa_index.get('relative_north')
            int(ndx)
            relative_north = int(nmea_flaa.data[ndx])
            if not (-32768 <= relative_north <= 32767):
                raise Exception("relative north out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # relative east. range: from -32768 to 32767.
        try:
            ndx = Observation.pflaa_index.get('relative_east')
            int(ndx)
            relative_east = int(nmea_flaa.data[ndx])
            if not (-32768 <= relative_east <= 32767):
                raise Exception("relative east out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # relative vertical. range: from -32768 to 32767.
        try:
            ndx = Observation.pflaa_index.get('relative_vertical')
            int(ndx)
            relative_vertical = int(nmea_flaa.data[ndx])
            if not (-32768 <= relative_vertical <= 32767):
                raise Exception("relative vertical out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # id type. integer. range: from 0 to 3.
        try:
            ndx = Observation.pflaa_index.get('id_type')
            int(ndx)
            id_type = int(nmea_flaa.data[ndx])
            if not ( 0 <= id_type <= 3):
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
            ndx = Observation.pflaa_index.get('radioId')
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
            ndx = Observation.pflaa_index.get('track')
            int(ndx)
            track = int(nmea_flaa.data[ndx])
            if not (0 <= id_type <= 339):
                raise Exception("track out of range")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # turn rate.
        # Currently this field is empty.
        try:
            ndx = Observation.pflaa_index.get('turn_rate')
            int(ndx)
            turn_rate = nmea_flaa.data[ndx]
            if not (len(turn_rate) == 0):
                raise Exception("turn rate found. unexpected.")
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        # ground_speed.
        # Decimal integer value.  Range: from 0 to 32767.The target’s
        # ground speed in m/s. The field is 0 to indicate that the aircraft
        # is not moving, i.e. onground. This field is empty if stealth mode
        # is activated either on the target or own aircraft and for
        # non-directional targets.
        try:
            ndx = Observation.pflaa_index.get('ground_speed')
            int(ndx)
            ground_speed = Groundspeed(nmea_flaa.data[ndx])
            if not (0 <= ground_speed <= 32767):
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
            ndx = Observation.pflaa_index.get('climb_rate')
            int(ndx)
            if ((len(nmea_flaa.data[ndx])) == 0):
                # target not moving, so climb rate is zero
                climb_rate = 0
            else:
                climb_rate = float(nmea_flaa.data[ndx])

            if not (-32.7 <= climb_rate <= 32.7):
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
            ndx = Observation.pflaa_index.get('aircraft_type')
            int(ndx)
            aircraft_type = nmea_flaa.data[ndx]
            if (len(aircraft_type) != 1):
                msg = "aircraft type must be a single char hex number. " + aircraft_type
                raise Exception(msg)
            hex(int(aircraft_type, 16)) # ensure ac type can convert to hex.
        except Exception as e:
            print(nmea_flaa, ":", e)
            sys.exit()

        theOgnReg = OgnRegistration()
        self.aircraft_id = theOgnReg.getAircraft(radioId)
        self.timestamp = groundstation.timestamp

        self.relative_north = relative_north
        self.relative_east = relative_east
        self.relative_vertical = relative_vertical
        self.track = track
        self.speed = ground_speed
        self.climb_rate = climb_rate

        # set the lat, lon of the observation using rel north, rel east.
        self.displace_lat_lon(groundstation)

        # distance is the hypotenuse of relative_north and relative_east so,
        # now that those values are set, let's set our max distance
        self.set_max_distance();

# tstamp int,
# radioid char(6),
# aircraft_type int,
# lat double,
# lon double,
# relative_north int,
# relative_east int,
# relative_vertical int,
# track int,
# speed int,
# climb_rate double,
# PRIMARY KEY (tstamp, radioid)


# Insert a row of data
        statement = "INSERT INTO observations VALUES (%d, %s, %d, %f, %f, %d, %d, %d, %d, %d, %f);" % (
                int(groundstation.timestamp.timestamp()),
                theOgnReg.getAircraft(radioId),
                2,
                self.lat,
                self.lon,
                relative_north,
                relative_east,
                relative_vertical,
                track,
                ground_speed,
                climb_rate
                )
              #
              #
              # "2,",
              # "%f," % self.lat,
              # "%f," % self.lon,
              # "%d," % relative_north,
              # "%d," % relative_east,
              # "%d," % relative_vertical,
              # "%d," % track,
              # "%d," % ground_speed,
              # "%f)" % climb_rate
              # )

        print(statement)
        global conn
        c = conn.cursor()

        c.execute(statement)
# # c.execute('''INSERT INTO observations VALUES (
# # '2006-01-05','BUY','RHAT',100,35.14
# # )''')
#
# # Save (commit) the changes
# conn.commit()


        return True

    def report(self):
        print("")
        print("Observations")
        print("============")
        print("observations:%6d" % self.observations,
            "max distance:%6d" % self.distance_max
            )

    def printt(self):

        print(self.aircraft_id,
            " %-9s" % self.timestamp.time(),
            #"dist:%5d" % self.getDistance(),
            "%5dm" % self.getDistance(),
            #"%10s" % "",
            #"alt AGL:%4d" % self.getAltitudeAGL(),
            "\t%4dm AGL" % self.getAltitudeAGL(),
            "\t%3ddeg" % self.track,
            "@ %3dkph" % self.speed.kph(),
            "\tvV %+2.1f" % self.climb_rate,
            "\trN %5d" % self.relative_north,
            " rE %5d" % self.relative_east,
            " https://www.google.ca/maps/place/%f," % self.lat,
            "%f" % self.lon,
            sep=''
            )
