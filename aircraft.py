import math

class Aircraft:
    def __init__(self, id):
        self.id = id
        self.status = "unknown"
        self.relativeNorth = 0.0
        self.relativeEast = 0.0
        self.relativeVertical = 0.0
        self.speed = 0.0
        self.track = 0
        self.climbRate = 0.0
        self.type = 0
        self.timestamp = 0

    def set(self, timestamp, nmea_flaa, ):
        #print(nmea_flaa)
        self.timestamp = timestamp
        self.id = nmea_flaa.data[6]
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

        print("id:", self.id, "time", self.timestamp, "distance:", self.getDistance(),
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
