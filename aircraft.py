import math

from ognRegistrations import OgnRegistration

class AircraftPosition:
    def __init__(self):
        self.aircraftId = ''
        self.status = "unknown"
        self.relativeNorth = 0.0
        self.relativeEast = 0.0
        self.relativeVertical = 0.0
        self.speed = 0.0
        self.track = 0
        self.climbRate = 0.0
        self.type = 0
        self.timestamp = 0
        self.radioId = ''

    def set(self, timestamp, nmea_flaa, ):
        temp_str= nmea_flaa.data[6]
        #self.id = acid[temp_str[0:temp_str.find("!")]]
        self.radioId = temp_str[0:temp_str.find("!")]
        #print("radio id:", self.radioId)
        theOgnReg = OgnRegistration()
        self.aircraftId = theOgnReg.getAircraft(self.radioId)
        self.timestamp = timestamp

        #self.status = "unknown"
        self.relativeNorth = int(nmea_flaa.data[2])
        self.relativeEast = int(nmea_flaa.data[3])
        self.relativeVertical = int(nmea_flaa.data[4])
        self.track = int(nmea_flaa.data[7])
        self.speed = int(nmea_flaa.data[9])
        self.climbRate = nmea_flaa.data[10]

    def print(self):
        """
        if (self.getDistance() > 3000): return
        if (self.getAltitudeAGL() > 40): return
        if (self.getSpeed() < 5): return
        """

        print(self.aircraftId, self.timestamp, "dist:", self.getDistance(),
            "alt AGL:", self.getAltitudeAGL(), "speed:", self.getSpeed(),
            "track", self.track
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
