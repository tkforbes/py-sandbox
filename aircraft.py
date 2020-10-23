import datetime
import pytz
from groundstation import Groundstation
from event import Event
from event import TakeoffEvent
from event import LandingEvent


class Aircraft:

    # static datetime value used by class to indicate failure
    event_not_detected = pytz.utc.localize(datetime.datetime.min)

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
            if (tStart <= window[-1].getTimestamp() <= tMax):
                # don't look any further.
                break
            else:
                # print(window[-1].getTimestamp())
                window.pop()

    def detectTrack(window):
        track = 0
        n = 0
        for obs in range(0, len(window)):
            if Groundstation.atGroundLevel(window[obs].getAltitudeAGL() and
                window[obs].getSpeedKPH() > 10):

                # this won't work for North, where values are near 360 and 0

                # print(
                #     "%2d" % obs,
                #     "%2dm" % window[obs].getAltitudeAGL(),
                #     "%3dkph" % window[obs].getSpeedKPH(),
                #     "%3ddeg" % window[obs].getTrack())

                # eventually, we will calculat the average runwaay
                track += window[obs].getTrack()
                n += 1
        # print(
        #     "%4d tot runway" % rwy,
        #     "%3d obs" % obs
        #     )

        # calculate the average
        track = int(track/n)

        # correct for known runways. This is Kars specific, for now.
        if (220 <= track <= 270):
            track = 260
        elif (60 <= track <= 100):
            track = 80

        return int(track)

    def detectTakeoff(self, timeframeOfWindow, window):
        t1 = window[0].getTimestamp()

        if not (len(window) > 0):
            return Aircraft.event_not_detected

        # takeoff inital rolling speed
        # when too slow, a towplane rolling-up to a glider
        # gets included! The heading of the towplane is wrong at that point,
        # which messes with runway calculation.
        initialSpeed = int(window[0].getSpeedKPH())
        if not (7 <= initialSpeed <= 19):
            return Aircraft.event_not_detected

        # climbout speed at least this
        finalSpeed = int(window[-1].getSpeedKPH())
        if not (finalSpeed > 50):
            return Aircraft.event_not_detected

        # must be close to the ground initially
        initialAltAGL = window[0].getAltitudeAGL()
        if not Groundstation.atGroundLevel(initialAltAGL):
            return Aircraft.event_not_detected

        # must be at least this much higher during climbout
        finalAltAGL = window[-1].getAltitudeAGL()
        if not (finalAltAGL > initialAltAGL + 30):
            return Aircraft.event_not_detected

        track = Aircraft.detectTrack(window)

        # print(
        #     "Takeoff ",
        #     window[0].getTimestamp().astimezone(Groundstation.TZ),
        #     " R%02d" % int(rwy),
        #     " %+4dagl" % initialAltAGL,
        #     " %3dkph" % initialSpeed,
        #      " ==>> ",
        #     window[-1].getTimestamp().astimezone(Groundstation.TZ),
        #      " %+4dagl" % finalAltAGL,
        #      " %3dkph" % finalSpeed,
        #      " ",
        #      window[-1].getTimestamp() - window[0].getTimestamp(),
        #      sep='')

        initialSpeedMS = int(window[0].getSpeed()) # speeds stored as metres per second
        e = TakeoffEvent(window[0].getTimestamp().astimezone(Groundstation.TZ),
                0, 0, initialAltAGL, track, initialSpeedMS)
        self.events.append(e)

        return t1

    def detectLanding(self, timeframeOfWindow, window):
        t1 = window[0].getTimestamp()
        windowSize = len(window)

        if not (len(window) > 0):
            return Aircraft.event_not_detected

        # ensure rollout speed
        finalSpeed = int(window[-1].getSpeedKPH())
        if not (finalSpeed < 16):
            return Aircraft.event_not_detected

        # ensure on the ground
        finalAltAGL = window[-1].getAltitudeAGL()
        if not (Groundstation.atGroundLevel(finalAltAGL)):
            return Aircraft.event_not_detected

        # ensure approaching at speed
        initialSpeed = int(window[0].getSpeedKPH())
        if not (initialSpeed > 40):
            return Aircraft.event_not_detected

        # ensure approaching from altitude
        initialAltAGL = window[0].getAltitudeAGL()
        if not (initialAltAGL > finalAltAGL + 30):
            return Aircraft.event_not_detected

        track = Aircraft.detectTrack(window)

        # print(
        #     "Landing ",
        #     window[0].getTimestamp().astimezone(Groundstation.TZ),
        #     " R%02d" % rwy,
        #     " %+4dagl" % initialAltAGL,
        #     " %3dkph" % initialSpeed,
        #      " ==>> ",
        #     window[-1].getTimestamp().astimezone(Groundstation.TZ),
        #      " %+4dagl" % finalAltAGL,
        #      " %3dkph" % finalSpeed,
        #      " ",
        #      window[-1].getTimestamp() - window[0].getTimestamp(),
        #      sep='')

        finalSpeedMS = int(window[-1].getSpeed()) # we store speed in M/S
        e = LandingEvent(window[-1].getTimestamp().astimezone(Groundstation.TZ),
                0, 0, finalAltAGL, track, finalSpeedMS)
        self.events.append(e)

        return window[-1].getTimestamp()

    def detectEvents(self):

        tTakeoff = Aircraft.event_not_detected
        tLanding = Aircraft.event_not_detected

        # num of seconds of an observation period. The period is used
        # in determining flight events like takeoff and landing.
        observationPeriod = 45


        n = len(self.getObservations())
        if (n > 0): n -= 1  # correct for zero-based index

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
                tTakeoff = self.detectTakeoff(observationPeriod, takeoffObservations)
                tLanding = self.detectLanding(observationPeriod, landingObservations)


        return

    def reportEvents(self):
        n = 1
        tTakeoffTimestamp = Aircraft.event_not_detected
        tLandingTimestamp = Aircraft.event_not_detected
        tTotal = datetime.timedelta(seconds=0)

        for e in self.events:
            if type(e) is TakeoffEvent:
                tTakeoffTimestamp = e.getTimestamp()
                takeoffRwy = e.getRwy()
                takeoffAltAGL = e.getAltitudeAGL()
                takeoffSpeed = e.getSpeedKPH()

            if type(e) is LandingEvent:
                tLandingTimestamp = e.getTimestamp()
                landingRwy = e.getRwy()
                landingAltAGL = e.getAltitudeAGL()
                landingSpeed = e.getSpeedKPH()

                tDuration = tLandingTimestamp - tTakeoffTimestamp
                tTotal += tDuration

                if (tLandingTimestamp < tTakeoffTimestamp + datetime.timedelta(hours=16)):
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
                    print("Landing", tLanding)

                tTakeoff = Aircraft.event_not_detected
                tLanding = Aircraft.event_not_detected


        print("%104s" % "======= ")
        print("%95s" % " ",
                tTotal)
        return

    def printObservations(self):
        observations = self.getObservations()
        for s in observations:
            if (s.getSource() == "PFLAA"):
                s.printt()

    def getMaxDistance(self):
        maxDistance = 0
        observations = self.getObservations()
        for s in observations:
            if (s.getSource() == "PFLAA"):
                distance = s.getDistance()
                if (distance > maxDistance):
                    maxDistance = distance
                    altitudeAGL = s.getAltitudeAGL()
        return maxDistance, altitudeAGL
