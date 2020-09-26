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

    def getTimestamp(self):
        return self.timestamp

    def averageElevation(self):
        return self.elevationCumulative / self.observations



"""
        if (msg.altitude is not None and is_integer(msg.altitude) and int(msg.num_sats) > 4):
            alt += int(msg.altitude)
            altitudeOberservations += 1
            print(msg)
            if (int(msg.altitude) > altMax ): altMax = msg.altitude
            if (int(msg.altitude) < altMin ): altMin = msg.altitude


        print(msg.sentence_type, msg.timestamp, "alt: ", msg.altitude)
        if (msg.altitude is not None and is_integer(msg.altitude) and int(msg.num_sats) > 4):
            alt += int(msg.altitude)
            altitudeOberservations += 1
            print(msg)
            if (int(msg.altitude) > altMax ): altMax = msg.altitude
            if (int(msg.altitude) < altMin ): altMin = msg.altitude

    altitude = 0
    latitude = 0.0
    longitude = 0.0

    altMax = 0.0
    altMin = 0.0
    altitudeOberservations = 0
"""
