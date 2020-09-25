class Airfield:
    def __init__(self, alt, lat, lon):
        self.altitude = alt
        self.lat = lat
        self.lon = lon

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
        print("validating")
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

    def set(self, nmea_gga):
        print("KARS", nmea_gga)
        if (Airfield.isvalid(nmea_gga)):
            print("valid")
            print(repr(nmea_gga))
            self.altitude = nmea_gga.altitude
            self.lat = nmea_gga.lat
            self.lon = nmea_gga.lon
        else:
            return False



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
