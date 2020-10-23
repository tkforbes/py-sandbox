import datetime
import pytz

class Event:

    event_not_detected = pytz.utc.localize(datetime.datetime(1970, 1, 1))

    def __init__(self, timestamp, lat, lon, altAGL, track, speed):
        self.timestamp = timestamp
        self.lat = lat
        self.lon = lon
        self.altAGL = altAGL
        self.track = track
        self.speed = speed
        return

    def getTimestamp(self):
        return self.timestamp

    def getLat(self):
        return self.lat

    def getLon(self):
        return self.lon

    def getAltitudeAGL(self):
        return self.altAGL

    def getSpeed(self):
        return self.speed

    def getTrack(self):
        return self.track

class TakeoffEvent(Event):
    def __init__(self, timestamp, lat, lon, altAGL, rwy, speed):
            super().__init__(timestamp, lat, lon, altAGL, rwy, speed)

    # in the context of TakeoffEvent, the track indicates the runway.
    def getRwy(self): return self.track

class LandingEvent(Event):
    def __init__(self, timestamp, lat, lon, altAGL, rwy, speed):
            super().__init__(timestamp, lat, lon, altAGL, rwy, speed)

    # in the context of LandingEvent, the track indicates the runway.
    def getRwy(self): return self.track

class LaunchEvent(Event):
    def __init__(self, registration, timestamp, lat, lon, altAGL, rwy, speed):
            super().__init__(timestamp, lat, lon, altAGL, rwy, speed)
            self.reg = registration

    def getReg(self): return self.reg

    # in the context of LaunchEvent, the track indicates the runway.
    def getRwy(self): return self.track

    def __lt__(self, other):
        if self.timestamp < other.timestamp: return True

        return False

    def getTimestamp(self):
        return self.timestamp
