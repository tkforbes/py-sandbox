from enum import Enum

import datetime
import pytz

class FlightState(Enum):
        LANDED = 1
        DEPARTED = 2
        APPROACHING = 4

class Aircraft:

    event_not_detected = pytz.utc.localize(datetime.datetime.min)
    #sentences = []

    def __init__(self, reg):
        self.aircraftId = reg
        self.aircraftType = ''
        self.sentences = []

    def append(self, sentence):
        self.sentences.append(sentence)

    def getSentences(self):
        return self.sentences

    def getAircraftId(self):
        return self.aircraftId

    def getAircraftType(self):
        return self.aircraftType

    def segment(self, t1, t2):
        return

    def atGroundLevel(alt):
        if (-30 < alt < 30): return True
        return False

    def trim(timeframeOfWindow, window):

        tStart = window[0].getTimestamp()
        tMax = tStart + datetime.timedelta(seconds=timeframeOfWindow)
        # print(tStart, tMax)

        # remove observations that are out of range
        for y in range(0, len(window)):
            # remove final observation if beyond range
            if (tStart <= window[-1].getTimestamp() <= tMax):
                break
            else:
                # print(window[-1].getTimestamp())
                window.pop()


    def detectTakeoff(timeframeOfWindow, window):
        EST = pytz.timezone('US/Eastern')
        t1 = window[0].getTimestamp()

        if not (len(window) > 0):
            return Aircraft.event_not_detected

        # takeoff inital rolling speed
        initialSpeed = int(window[0].getSpeed())
        if not (1 <= initialSpeed <= 19):
            return Aircraft.event_not_detected

        # initial climbout speed at least this
        finalSpeed = int(window[-1].getSpeed())
        if not (finalSpeed > 50):
            return Aircraft.event_not_detected

        # must be close to the ground initially
        initialAltAGL = window[0].getAltitudeAGL()
        if not Aircraft.atGroundLevel(initialAltAGL):
            return Aircraft.event_not_detected

        # must be at least this much higher during climbout
        finalAltAGL = window[-1].getAltitudeAGL()
        if not (finalAltAGL > initialAltAGL + 30):
            return Aircraft.event_not_detected

        print(
            "Takeoff ",
            window[0].getTimestamp().astimezone(EST),
            "%+4dagl" % initialAltAGL,
            " %3dkph" % initialSpeed,
             " ==>> ",
            window[-1].getTimestamp().astimezone(EST),
             "%+4dagl" % finalAltAGL,
             " %3dkph" % finalSpeed,
             sep='')
        return t1

    def detectLanding(timeframeOfWindow, window):

        EST = pytz.timezone('US/Eastern')
        t1 = window[0].getTimestamp()
        windowSize = len(window)

        if not (len(window) > 0):
            return Aircraft.event_not_detected

        # ensure rollout speed
        finalSpeed = int(window[-1].getSpeed())
        if not (finalSpeed < 16):
            return Aircraft.event_not_detected

        # ensure on the ground
        finalAltAGL = window[-1].getAltitudeAGL()
        if not (Aircraft.atGroundLevel(finalAltAGL)):
            return Aircraft.event_not_detected

        # ensure approaching at speed
        initialSpeed = int(window[0].getSpeed())
        if not (initialSpeed > 40):
            return Aircraft.event_not_detected

        # ensure approaching from altitude
        initialAltAGL = window[0].getAltitudeAGL()
        if not (initialAltAGL > finalAltAGL + 30):
            return Aircraft.event_not_detected

        print(
            "Landing ",
            window[0].getTimestamp().astimezone(EST),
            "%+4dagl" % initialAltAGL,
            " %3dkph" % initialSpeed,
             " ==>> ",
            window[-1].getTimestamp().astimezone(EST),
             "%+4dagl" % finalAltAGL,
             " %3dkph" % finalSpeed,
             sep='')

        return window[-1].getTimestamp()

    def reportFlights(self):

        tTakeoff = Aircraft.event_not_detected
        tLanding = Aircraft.event_not_detected
        observationPeriod = 45

        n = len(self.getSentences())
        if (n > 0): n -= 1

        # move through the list, one observation at a time
        for x in range(0, n):

            # carve out smaller lists of observations.
            takeoffObservations = self.sentences[x:x+observationPeriod]
            Aircraft.trim(observationPeriod, takeoffObservations)
            landingObservations = self.sentences[x:x+observationPeriod]
            Aircraft.trim(observationPeriod, landingObservations)

            t1 = landingObservations[0].getTimestamp()

            # detect takeoff, but skip ahead if takeoff just detected
            if (tTakeoff + datetime.timedelta(seconds=observationPeriod) > t1 or
                tLanding + datetime.timedelta(seconds=observationPeriod) > t1):
                pass
            else:
                tTakeoff = Aircraft.detectTakeoff(observationPeriod, takeoffObservations)
                tLanding = Aircraft.detectLanding(observationPeriod, landingObservations)

        return

            # if (t1 > tLanding+datetime.timedelta(seconds=timeframeOfWindow))
            # l = Aircraft.detectLanding(observationPeriod, landingObservations)

    # def reportFlights(self):
    #
    #     state = FlightState.LANDED
    #     prevSpeed = 0
    #     prevT = None
    #
    #     takeoffList = self.sentences[-5:-1]
    #     print(takeoffList[1].getTimestamp())
    #
    #     sentenceIterator = iter(self.getSentences())
    #
    #     sentences = self.getSentences()
    #     for s in sentences:
    #         if (s.getSource() == "PFLAA"):
    #             t = s.getTimestamp()
    #             if (prevT is None):
    #                 prevT = t
    #
    #             gap = t - prevT
    #             #permittedGap =
    #
    #             v = s.getSpeed()
    #             agl = s.getAltitudeAGL()
    #
    #
    #             if (state == FlightState.LANDED):
    #                 if (v > 60 and 30 < agl < 130 ):
    #                     departed = t
    #                     state = FlightState.DEPARTING
    #                     if (gap > datetime.timedelta(seconds=30)):
    #                         print ("=========== gap %s ===========" % gap)
    #                     print("%11s" %"departing",
    #                         "%8s" % t,
    #                         "%3dkph" % v,
    #                         "%4dm AGL" % agl
    #                     )
    #
    #             if (state == FlightState.DEPARTING):
    #                 if (v > 60 and agl >= 130 ):
    #                     state = FlightState.FLYING
    #                     if (gap > datetime.timedelta(seconds=30)):
    #                         print ("=========== gap %s ===========" % gap)
    #                     print("%11s" %"flying",
    #                         "%8s" % t,
    #                         "%3dkph" % v,
    #                         "%4dm AGL" % agl
    #                     )
    #
    #             if (state == FlightState.FLYING):
    #                 if (v > 60 and 20 < agl < 100 ):
    #                     state = FlightState.APPROACHING
    #                     if (gap > datetime.timedelta(seconds=30)):
    #                         print ("=========== gap %s ===========" % gap)
    #                     print("%11s" %"approaching",
    #                         "%8s" % t,
    #                         "%3dkph" % v,
    #                         "%4dm AGL" % agl
    #                     )
    #
    #             if (state == FlightState.APPROACHING):
    #                 if (v < 30 and -30 < agl < 15 ):
    #                     state = FlightState.LANDED
    #                     if (gap > datetime.timedelta(seconds=30)):
    #                         print ("=========== gap %s ===========" % gap)
    #                     print("%11s" %"landed",
    #                         "%8s" % t,
    #                         "%3dkph" % v,
    #                         "%4dm AGL" % agl,
    #                         "duration: %s" % str(t - departed)
    #                     )
    #
    #             prevT = t
    #     return


    def printObservations(self):
        sentences = self.getSentences()
        for s in sentences:
            if (s.getSource() == "PFLAA"):
                s.printt()

    def getMaxDistance(self):
        maxDistance = 0
        sentences = self.getSentences()
        for s in sentences:
            if (s.getSource() == "PFLAA"):
                distance = s.getDistance()
                if (distance > maxDistance):
                    maxDistance = distance
                    altitudeAGL = s.getAltitudeAGL()
        return maxDistance, altitudeAGL
