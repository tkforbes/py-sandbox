import datetime
import pytz

class Event:

    event_not_detected = pytz.utc.localize(datetime.datetime(1970, 1, 1))

    def __init__(self, timestamp, lat, lon, altAGL, rwy, speed):
        self.timestamp = timestamp
        self.lat = lat
        self.lon = lon
        self.altAGL = altAGL
        self.rwy = rwy
        self.speed = speed
        return

    def getTrack(self):
        return self.track

class TakeoffEvent(Event):
    def __init__(self, timestamp, lat, lon, altAGL, rwy, speed):
            super().__init__(timestamp, lat, lon, altAGL, rwy, speed)

class LandingEvent(Event):
    def __init__(self, timestamp, lat, lon, altAGL, rwy, speed):
            super().__init__(timestamp, lat, lon, altAGL, rwy, speed)

class LaunchEvent(Event):
    def __init__(self, registration, timestamp, lat, lon, altAGL, rwy, speed):
            super().__init__(timestamp, lat, lon, altAGL, rwy, speed)
            self.reg = registration

    def __lt__(self, other):
        if self.timestamp < other.timestamp: return True

        return False

    def getTimestamp(self):
        return self.timestamp
