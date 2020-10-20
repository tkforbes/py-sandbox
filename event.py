
class Event:

    def __init__(self):
        self.type = None
        self.timestamp = None
        self.lat = None
        self.lon = None
        self.altAGL = None
        self.altGroundstationAGL = None
        self.rwy = None
        self.track = None
        self.speed = None
        return

    def set(self, type, timestamp, lat, lon, altAGL,
            altGroundstationAGL, rwy, track, speed ):
        self.type = type
        self.timestamp = timestamp
        self.lat = lat
        self.lon = lon
        self.altAGL = altAGL
        self.altGroundstationAGL = altGroundstationAGL
        self.rwy = rwy
        self.track = track
        self.speed = speed
        return

    def getTrack(self):
        return self.track
