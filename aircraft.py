
import datetime
import pytz

from groundstation import Groundstation
from event import TakeoffEvent, LandingEvent


class Aircraft:

    # static datetime value used by class to indicate failure
    event_not_detected = pytz.utc.localize(datetime.datetime.min)

    @staticmethod
    def takeoff_initialSpeedLowerBound(): return 7

    @staticmethod
    def takeoff_initialSpeedUpperBound(): return 19

    @staticmethod
    def takeoff_climboutSpeedMin(): return 50

    @staticmethod
    def takeoff_climboutAltMin(): return +30

    @staticmethod
    def landing_finalSpeedMax(): return 16

    @staticmethod
    def landing_approachSpeedMin(): return 40

    @staticmethod
    def landing_approachAltMin(): return +30

    def __init__(self, reg):
        self.aircraftId = reg
        self.aircraftType = ''

        # observations are the senquentially ordered sequence of
        # positions reported by an aircraft.
        self.observations = []

        # occurences of importance detected by processing the observations.
        self.events = []

    def appendObservations(self, observation):
        self.observations.append(observation)

    def getObservations(self):
        return self.observations

    def getAircraftId(self):
        return self.aircraftId

    def getAircraftType(self):
        return self.aircraftType

    @staticmethod
    def trim(timeframeOfWindow, window):
        '''
        check the tail of a window of observations for observations beyond
        the expected timeframe. trim the window to just the expected
        timeframe.
        '''

        tStart = window[0].getTimestamp()
        tMax = tStart + datetime.timedelta(seconds=timeframeOfWindow)
        # print(tStart, tMax)

        # remove observations that are out of range
        for y in range(0, len(window)):
            # remove tail observation if beyond timeframe
            if tStart <= window[-1].getTimestamp() <= tMax:
                # don't look any further.
                break

            window.pop()

    @staticmethod
    def detectTrack(window):
        track = 0
        n = 0
        for obs in range(0, len(window)):
            if Groundstation.atGroundLevel(window[obs].getAltitudeAGL() and
                window[obs].speed.kph() > 10):

                # this won't work for North, where values are near 360 and 0

                track += window[obs].getTrack()
                n += 1

        # calculate the average
        track = int(track/n)

        # correct for known runways. This is Kars specific, for now.
        if 220 <= track <= 270:
            track = 260
        elif 60 <= track <= 100:
            track = 80

        return int(track)

    def detectTakeoff(self, window):
        t1 = window[0].getTimestamp()

        if not len(window) > 0:
            return Aircraft.event_not_detected

        # takeoff inital rolling speed
        # when too slow, a towplane rolling-up to a glider
        # gets included! The heading of the towplane is wrong at that point,
        # which messes with runway calculation.

        initialSpeed = window[0].speed.kph()
        initialSpeedLowerBound = Aircraft.takeoff_initialSpeedLowerBound()
        initialSpeedUpperBound = Aircraft.takeoff_initialSpeedUpperBound()
        if not initialSpeedLowerBound <= initialSpeed <= initialSpeedUpperBound:
            return Aircraft.event_not_detected

        # climbout speed at least this
        finalSpeed = window[-1].speed.kph()
        if not finalSpeed >= Aircraft.takeoff_climboutSpeedMin():
            return Aircraft.event_not_detected

        # must be close to the ground initially
        initialAltAGL = window[0].getAltitudeAGL()
        if not Groundstation.atGroundLevel(initialAltAGL):
            return Aircraft.event_not_detected

        # must be at least this much higher during climbout
        finalAltAGL = window[-1].getAltitudeAGL()
        if not finalAltAGL >= initialAltAGL + Aircraft.takeoff_climboutAltMin():
            return Aircraft.event_not_detected

        track = Aircraft.detectTrack(window)

        # speed stored as metres per second
        e = TakeoffEvent(window[0].getTimestamp().astimezone(Groundstation.timezone()),
                         0, 0, initialAltAGL, track, window[0].speed)
        self.events.append(e)

        return t1

    def detectLanding(self, window):

        if not len(window) > 0:
            return Aircraft.event_not_detected

        # ensure rollout speed
        finalSpeed = window[-1].speed.kph()
        if not finalSpeed <= Aircraft.landing_finalSpeedMax():
            return Aircraft.event_not_detected

        # ensure on the ground
        finalAltAGL = window[-1].getAltitudeAGL()
        if not Groundstation.atGroundLevel(finalAltAGL):
            return Aircraft.event_not_detected

        # ensure approaching at speed
        initialSpeed = window[0].speed.kph()
        if not initialSpeed >= Aircraft.landing_approachSpeedMin():
            return Aircraft.event_not_detected

        # ensure approaching from altitude
        initialAltAGL = window[0].getAltitudeAGL()
        if not initialAltAGL >= finalAltAGL + Aircraft.landing_approachAltMin():
            return Aircraft.event_not_detected

        track = Aircraft.detectTrack(window)

        # store speed in M/S
        e = LandingEvent(window[-1].getTimestamp().astimezone(Groundstation.timezone()),
                         0, 0, finalAltAGL, track, window[-1].speed)
        self.events.append(e)

        return window[-1].getTimestamp()

    def detectEvents(self):

        tTakeoff = Aircraft.event_not_detected
        tLanding = Aircraft.event_not_detected

        # num of seconds of an observation period. The period is used
        # in determining flight events like takeoff and landing.
        observationPeriod = 45


        n = len(self.getObservations())
        if n > 0: n -= 1  # correct for zero-based index

        # move through the list, one observation at a time
        for x in range(0, n):

            # create a smaller, look-ahead views of a limited timeframe.
            takeoffObservations = self.observations[x:x+observationPeriod]
            Aircraft.trim(observationPeriod, takeoffObservations)
            landingObservations = self.observations[x:x+observationPeriod]
            Aircraft.trim(observationPeriod, landingObservations)

            t1 = landingObservations[0].getTimestamp()

            # detect takeoff, but skip ahead if takeoff just detected
            if (tTakeoff + datetime.timedelta(seconds=observationPeriod) > t1 or
                tLanding + datetime.timedelta(seconds=observationPeriod) > t1):
                pass
            else:
                tTakeoff = self.detectTakeoff(takeoffObservations)
                tLanding = self.detectLanding(landingObservations)


    def reportEvents(self):
        n = 1
        tTakeoffTimestamp = Aircraft.event_not_detected
        tLandingTimestamp = Aircraft.event_not_detected
        tTotal = datetime.timedelta(seconds=0)

        for e in self.events:
            if isinstance(e, TakeoffEvent):
                tTakeoffTimestamp = e.getTimestamp()
                takeoffRwy = e.getRwy()
                takeoffAltAGL = e.getAltitudeAGL()
                takeoffSpeed = e.speed.kph()

            if isinstance(e, LandingEvent):
                tLandingTimestamp = e.getTimestamp()
                landingRwy = e.getRwy()
                landingAltAGL = e.getAltitudeAGL()
                landingSpeed = e.speed.kph()

                tDuration = tLandingTimestamp - tTakeoffTimestamp
                tTotal += tDuration

                if tLandingTimestamp < tTakeoffTimestamp + datetime.timedelta(hours=16):
                    print(
                        "%2d " % n,
                        # "%8s" % "Takeoff ",
                        tTakeoffTimestamp,
                        " R%02d" % takeoffRwy,
                        " %+3dagl" % takeoffAltAGL,
                        " %3dkph" % takeoffSpeed,
                        "%6s" % " ==>> ",
                        tLandingTimestamp,
                        " R%02d" % landingRwy,
                        " %+3dagl" % landingAltAGL,
                        " %3dkph " % landingSpeed,
                        tDuration,
                        sep='')
                    n += 1
                    # print("Takeoff", tTakeoff, "Landing", tLanding, "Duration:", tDuration)
                else:
                    print("Landing", tLandingTimestamp)

        print("%104s" % "======= ")
        print("%95s" % " ",
              tTotal)

    def printObservations(self):

        for obs in self.getObservations():
            obs.printt()

    def getMaxDistance(self):
        maxDistance = 0
        observations = self.getObservations()
        for s in observations:
            distance = s.getDistance()
            if distance > maxDistance:
                maxDistance = distance
                altitudeAGL = s.getAltitudeAGL()
        return maxDistance, altitudeAGL
