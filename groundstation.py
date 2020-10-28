import sys

#import pynmea2

#import geopy
#import geopy.distance

import datetime
import pytz
#import re

#import math


class Groundstation:

    @staticmethod
    def timezone(): return pytz.timezone('US/Eastern')

    @staticmethod
    def groundLevelLowerLimitAGL(): return -30

    @staticmethod
    def groundLevelUpperLimitAGL(): return +30

    # returns the height (in metres) of the grounstation's GPS AGL
    # e.g. a tower-mounted groundstation might be 9m AGL.
    @staticmethod
    def heightOfGroundstationAGL(): return 0

    @staticmethod
    def atGroundLevel(alt):
        '''
        upper and lower boundardies of AGL zero that are
        sufficiently close to the ground to be considered as good as AGL zero.
        '''

        if alt in range(Groundstation.groundLevelLowerLimitAGL(), Groundstation.groundLevelUpperLimitAGL()):
            return True

        return False

    def __init__(self):
        self.lat = None
        self.lon = None
        self.elevation = None
        self.datestamp = None
        self.timestamp = None
        self.observations = 0
        self.elevationCumulative = 0 # used in averaging.

        self.elevationMax = -99999
        self.elevationMin = +99999

        self.timestampMin = None
        self.timestampMax = None


    def setDate(self, d):
        self.datestamp = d

    def setTime(self, ti):
        # don't permit the time to be set until after the date has been set
        if self.datestamp is None: return

        d = self.datestamp
        t = pytz.utc.localize(
                datetime.datetime(d.year, d.month, d.day, ti.hour, ti.minute, ti.second))

        # if timestamp has not be set before, this is the initial time value
        if self.timestamp is None:
            self.timestampMin = t
            self.timestampMax = t

        #utc_now = pytz.utc.localize(datetime.datetime.utcnow())

        self.timestamp = t
        self.setTimestampMax()
        return

    @staticmethod
    def is_integer(n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    def validDate(self):
        if self.datestamp is None: return False

        return True

    def validTime(self):
        if self.timestamp is None: return False

        return True

    @staticmethod
    def isvalid(nmea_gga):

        if nmea_gga.altitude is None:
            return False # elevation missing from observation

        if int(nmea_gga.num_sats) <= 4:
            return False # too few satellites for reliable data

        if not Groundstation.is_integer(nmea_gga.altitude):
            return False # elevation is not a number

        return True

    def setTimestampMax(self):
        if self.timestamp > self.timestampMax:
            self.timestampMax = self.timestamp

    def setElevationMax(self):
        if self.elevation is None: return

        if self.elevation > self.elevationMax:
            self.elevationMax = self.elevation

    def setElevationMin(self):
        if self.elevation is None: return

        if self.elevation < self.elevationMin:
            self.elevationMin = self.elevation

    def setDatestamp(self, datestamp):
        self.datestamp = datestamp

    def getLat(self):
        return self.lat

    def getLon(self):
        return self.lon

    def averageElevation(self):
        if self.observations == 0: return 0

        return self.elevationCumulative / self.observations

    def report(self):

        avg = self.averageElevation()

        print("")
        print("Groundstation report")
        print("====================")
        print("lat:", self.lat, "lon:", self.lon)
        print("Start: %24s" % str(self.timestampMin.astimezone(Groundstation.timezone())))
        print("End:   %24s" % str(self.timestampMax.astimezone(Groundstation.timezone())))
        print("Dur:   %19s" % str(self.timestampMax - self.timestampMin))
        print("Elevation",
              "min:%.1f" % self.elevationMin,
              "max:%.1f" % self.elevationMax,
              "curr:%.1f" % self.elevation,
              "avg:%.1f" % avg
              )
        print("observations:", self.observations)

    @staticmethod
    def toDecimalDegrees(dddmmDOTmmmm):
        deg = int(dddmmDOTmmmm/100)
        x = dddmmDOTmmmm - deg*100
        return deg+x/60

    def set(self, nmea):
        if (nmea.sentence_type == 'GGA'):
            gga = nmea
            try:
                timestamp = gga.timestamp
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # position fix indicator
            try:
                gpsQual = int(gga.gps_qual)
                if not 0 <= gpsQual <= 6:
                    raise Exception("position fix indicator must be between 1 and 6")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            if gpsQual not in [1, 2]:
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
                if latDir not in ['N', 'S']:
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
                if lonDir not in ['E', 'W']:
                    raise Exception("lon dir must be E or W.")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # position fix indicator
            try:
                gpsQual = int(gga.gps_qual)
                if not 0 <= gpsQual <= 6:
                    raise Exception("position fix indicator must be between 1 and 6")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # satellites used
            try:
                numSats = int(gga.num_sats)
                if not 0 <= numSats <= 24 :
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

            if Groundstation.isvalid(gga):

                self.elevation = altitude
                self.setElevationMax()
                self.setElevationMin()

                # convert lat to negative when South
                if latDir in ['S']: lat *= -1

                # convert lon to negative when West
                if lonDir in ['W']: lon *= -1

                self.setTime(timestamp)
                self.lat = Groundstation.toDecimalDegrees(lat)
                self.lon = Groundstation.toDecimalDegrees(lon)

                # this is for the 'average' calculation
                self.elevationCumulative += self.elevation
                self.observations += 1

                return True

        elif nmea.sentence_type == 'RMC':

            rmc = nmea

            ## UTC time
            try:
                timestamp = rmc.timestamp
            except Exception as e:
                print(rmc, ":", e)
                sys.exit()

            try:
                status = rmc.status
                if status not in ['A', 'V']:
                    raise Exception("status must be A or V.")
            except Exception as e:
                print(rmc, ":", e)
                sys.exit()

            if status not in ['A']:
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
                if latDir not in ['N', 'S']:
                    print(latDir)
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
                if not 0 <= groundSpeed <= 300:
                    print(groundSpeed)
                    raise Exception("groundspeed is out of range.")
            except Exception as e:
                print(rmc, ":", e)
                sys.exit()

            self.setTime(rmc.timestamp)

            return True
