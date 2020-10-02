import sys

class Airfield:
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

        if not (Airfield.is_integer(nmea_gga.altitude)):
            return False # elevation is not a number

        return True

    def set(self, nmea):
        if (nmea.sentence_type == 'GGA'):
            gga = nmea

            print(repr(gga))
            ## UTC time
            try:
                utcTime = gga.timestamp
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
                return False

            # latitude
            try:
                lat = gga.lat
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # N/S indicator
            try:
                latDir = gga.lat_dir
                latDir = 'N'
                if not (latDir in ['N', 'S']):
                    raise Exception("lat dir must be N or S.")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # longitude
            try:
                lon = gga.lon
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # E/W indicator
            try:
                lonDir = gga.lon_dir
                lonDir = 'E'
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
                horizontalDil = gga.horizontal_dil
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # MSL altitude
            try:
                altitude = gga.altitude
            except Exception as e:
                print(gga, ":", e)
                sys.exit()


            # MSL altitude units
            try:
                altitudeUnits = gga.altitude_units
            except Exception as e:
                print(gga, ":", e)
                sys.exit()



            # geoid separation
            try:
                geoSep = gga.geo_sep
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            # geoid separation units
            try:
                geoSepUnits = gga.geo_sep_units
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
                refStationId = int(gga.ref_station_id)
                if not (0 <= refStationId <= 4095):
                    raise Exception("reference station id must be between 0 and 4095")
            except Exception as e:
                print(gga, ":", e)
                sys.exit()

            if (Airfield.isvalid(gga)):
                #print(repr(nmea))
                if (gga.altitude > self.ignoreAbove or
                    gga.altitude < self.ignoreBelow):
                    return

                self.elevation = gga.altitude
                self.elevationCumulative += self.elevation
                if (self.elevation > self.elevationMax):
                    self.elevationMax = self.elevation # highest
                if (self.elevation < self.elevationMin):
                    self.elevationMin = self.elevation # lowest
                self.lat = gga.lat
                self.lon = gga.lon
                self.timestamp = gga.timestamp
                self.observations += 1
        elif (nmea_gga.sentence_type == 'RMC'):
            rmc = nmea
            self.datestamp = rmc.datestamp


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
        self.courseTrue = int(courseTrue)

    def getTimestamp(self):
        return self.timestamp

    def averageElevation(self):
        if (self.observations == 0): return 0
        return self.elevationCumulative / self.observations

    def report(self):

        avg = self.averageElevation()

        print("")
        print("Airfield report")
        print("===============")
        print("date:", self.datestamp, "time:", self.timestamp)
        print("lat:", self.lat, "lon:", self.lon)
        print("Elevation",
                "min:%.1f" % self.elevationMin,
                "max:%.1f" % self.elevationMax,
                "curr:%.1f" % self.elevation,
                "avg:%.1f" % avg)
        print("observations:", self.observations)
