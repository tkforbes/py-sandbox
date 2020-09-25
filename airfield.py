class Airfield:
    def __init__(self, alt, lat, lon):
        self.altitude = alt
        self.lat = lat
        self.lon = lon
        self.datestamp= 0
        self.timestamp = 0

    """
    this doesn't belong here.
    """
    def is_integer(n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    def isvalid(nmea_gga):
        if (nmea_gga.altitude is None):
            print("none prob")
            return False

        if not (Airfield.is_integer(nmea_gga.altitude)):
            print("alt prob")
            return False

        if (int(nmea_gga.num_sats) <= 4):
            print("sats prob")
            return False

        return True

    def set(self, nmea):
        if (nmea.sentence_type == 'GGA'):
            gga = nmea
            if (Airfield.isvalid(gga)):
                #print("valid")
                #print(repr(nmea))
                self.altitude = gga.altitude
                self.lat = gga.lat
                self.lon = gga.lon
                self.timestamp = gga.timestamp
        elif (nmea_gga.sentence_type == 'RMC'):
            rmc = nmea
            self.datestamp = rmc.datestamp


    def setDatestamp(self, datestamp):
        self.datestamp = datestamp

    def getTimestamp(self):
        return self.timestamp



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
