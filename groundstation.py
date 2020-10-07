import sys

import pynmea2

import geopy
import geopy.distance

import datetime
import re

import math


class Groundstation:
    def __init__(self, elevation, lat, lon):
        self.elevation = elevation
        self.lat = lat
        self.lon = lon
        self.datestamp = 0
        self.timestamp = 0
        self.observations = 0
        self.elevationCumulative = 0 # used in averaging.
        self.ignoreAbove = 97 # do not set elevation above this number.
        self.ignoreBelow = 77 # do not set elevation below this number.

        # looks counter-intuitive. these are the recorded max and min elevations
        self.elevationMax = self.ignoreBelow
        self.elevationMin = self.ignoreAbove

    """
    this doesn't belong here.
    """
    def is_integer(n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    def validDatestamp(self):
        if (self.datestamp == 0): return False

        return True

    def isvalid(nmea_gga):

        if (nmea_gga.altitude is None):
            return False # elevation missing from observation

        if (int(nmea_gga.num_sats) <= 4):
            return False # too few satellites for reliable data

        if not (Groundstation.is_integer(nmea_gga.altitude)):
            return False # elevation is not a number

        return True

    def setElevationMax(self):
        if self.elevation > self.elevationMax:
            self.elevationMax = self.elevation

    def setElevationMin(self):
        if self.elevation < self.elevationMin:
            self.elevationMin = self.elevation

    def setDatestamp(self, datestamp):
        self.datestamp = datestamp

    def setCourseTrue(self, courseTrue):
        # don't accept nonesense course
        try:
            float(courseTrue)
        except Exception as e:
            return

        # round the course, then convert to integer
        courseTrue += .5

        # if rounded value was 360 or more, adjust
        if (courseTrue >= 360): courseTrue -= 360

        self.courseTrue = int(courseTrue)

    def getTimestamp(self):
        return self.timestamp

    def getLat(self):
        return self.lat

    def getLon(self):
        return self.lon

    def averageElevation(self):
        if (self.observations == 0): return 0
        return self.elevationCumulative / self.observations

    def report(self):

        avg = self.averageElevation()

        print("")
        print("Groundstation report")
        print("====================")
        print("date:", self.datestamp, "time:", self.timestamp)
        print("lat:", self.lat, "lon:", self.lon)
        print("Elevation",
                "min:%.1f" % self.elevationMin,
                "max:%.1f" % self.elevationMax,
                "curr:%.1f" % self.elevation,
                "avg:%.1f" % avg,
                "crs:%d" % self.courseTrue
                )
        print("observations:", self.observations)

    def toDecimalDegrees(dddmmDOTmmmm):
        deg = int(dddmmDOTmmmm/100)
        x = dddmmDOTmmmm - deg*100
        return deg+x/60

    def set(self, nmea):
        if (nmea.sentence_type == 'GGA'):
            gga = nmea

            #print(repr(gga))

            ## UTC time
            try:
                timestamp = gga.timestamp
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # position fix indicator
            try:
                gpsQual = int(gga.gps_qual)
                if not (0 <= gpsQual <= 6):
                    raise Exception("position fix indicator must be between 1 and 6")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            if not (gpsQual in [1, 2]):
                # the fix method must be something useful to us
                #print(gpsQual, "gpsQual must be 1 or 2.")
                return False

            # latitude
            try:
                lat = float(gga.lat)
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # N/S indicator
            try:
                latDir = gga.lat_dir
                if not (latDir in ['N', 'S']):
                    raise Exception("lat dir must be N or S.")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # longitude
            try:
                lon = float(gga.lon)
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # E/W indicator
            try:
                lonDir = gga.lon_dir
                if not (lonDir in ['E', 'W']):
                    raise Exception("lon dir must be E or W.")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # position fix indicator
            try:
                gpsQual = int(gga.gps_qual)
                if not (0 <= gpsQual <= 6):
                    raise Exception("position fix indicator must be between 1 and 6")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # satellites used
            try:
                numSats = int(gga.num_sats)
                if not (0 <= numSats <= 24 ):
                    raise Exception("number of satellites must be between 0 and 24")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # hdop
            try:
                horizontalDil = float(gga.horizontal_dil)
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # MSL altitude
            try:
                altitude = float(gga.altitude)
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # MSL altitude units
            try:
                altitudeUnits = gga.altitude_units
                if altitudeUnits != 'M':
                    raise Exception("altitude units must be 'M'")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # geoid separation
            try:
                geoSep = float(gga.geo_sep)
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # geoid separation units
            try:
                geoSepUnits = gga.geo_sep_units
                if geoSepUnits != 'M':
                    raise Exception("Geo separation units must be 'M'")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # age of diff. corr.
            try:
                ageGpsData = gga.age_gps_data
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # diff. ref. station ID
            try:
                refStationId = gga.ref_station_id
                # refStationId = int(gga.ref_station_id)
                # if not (0 <= refStationId <= 4095):
                #     raise Exception("reference station id must be between 0 and 4095")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            if (Groundstation.isvalid(gga)):
                #print(repr(nmea))

                # ignore GGA sentence that is too inaccurate to be useful.
                if not (self.ignoreBelow < altitude < self.ignoreAbove):
                    return False

                self.elevation = altitude
                self.setElevationMax()
                self.setElevationMin()

                # convert lat to negative when South
                if (latDir in ['S']): lat *= -1

                # convert lon to negative when West
                if (lonDir in ['W']): lon *= -1

                self.timestamp = timestamp
                self.lat = Groundstation.toDecimalDegrees(lat)
                self.lon = Groundstation.toDecimalDegrees(lon)
                #print("time:", self.timestamp, "lat:", self.lat, "lon:", self.lon)

                # this is for the 'average' calculation
                self.elevationCumulative += self.elevation
                self.observations += 1

                return True

        elif (nmea.sentence_type == 'RMC'):

            rmc = nmea

            ## UTC time
            try:
                timestamp = rmc.timestamp
            except Exception as e:
                print(rmc, ":", e)
                sys.exit()

            try:
                status = rmc.status
                if not (status in ['A', 'V']):
                    raise Exception("status must be A or V.")
            except Exception as e:
                print(rmc, ":", e)
                sys.exit()

            if not (status in ['A']):
                # if status is not 'A', data is not valid
                return False

            # latitude
            try:
                lat = float(rmc.lat)
            except Exception as e:
                print(rmc, ":", e)
                sys.exit()

            # N/S indicator
            try:
                latDir = rmc.lat_dir
                if not (latDir in ['N', 'S']):
                    print (latDir)
                    raise Exception("lat dir must be N or S.")
            except Exception as e:
                print(rmc, ":", e)
                return False
                sys.exit()

            # longitude
            try:
                lon = float(rmc.lon)
            except Exception as e:
                print(rmc, ":", e)
                sys.exit()

            # E/W indicator
            try:
                lonDir = rmc.lon_dir
                if not (lonDir in ['E', 'W']):
                    raise Exception("lon dir must be E or W.")
            except Exception as e:
                print(rmc, ":", e)
                sys.exit()

            # speed over the ground
            try:
                #print(repr(rmc))
                groundSpeed = rmc.spd_over_grnd
                if not (0 <= groundSpeed <= 300):
                    print(groundSpeed)
                    raise Exception("groundspeed is out of range.")
            except Exception as e:
                print(rmc, ":", e)
                sys.exit()

            try:
                true_course = rmc.true_course
                if (true_course is None):
                    return False

                if not (0 <= true_course < 360):
                    print(true_course)
                    raise Exception("groundspeed is out of range.")

            except Exception as e:
                print(rmc, ":", e)
                sys.exit()

            self.timestamp = rmc.timestamp

            self.setCourseTrue(true_course)

            return True
