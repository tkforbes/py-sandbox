from enum import Enum

import datetime

class FlightState(Enum):
        LANDED = 1
        DEPARTED = 2
        APPROACHING = 4

class Aircraft:

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

    def detectTakeoff(timeframeOfWindow, window):
        t1 = window[0].getTimestamp()

        # remove observations that are out of range
        for y in range(0, len(window)):
            if (t1 < window[-1].getTimestamp() < t1+datetime.timedelta(seconds=timeframeOfWindow)):
                break
            else:
                window.pop()

        if not (len(window) > 0):
            return False

        # takeoff inital rolling speed
        initialSpeed = int(window[0].getSpeed())
        if not (1 <= initialSpeed <= 19):
            return False

        # initial climbout speed at least this
        finalSpeed = int(window[-1].getSpeed())
        if not (finalSpeed > 50):
            return False

        # must be close to the ground initially
        initialAltAGL = window[0].getAltitudeAGL()
        if not Aircraft.atGroundLevel(initialAltAGL):
            return False

        # must be at least this much higher during climbout
        finalAltAGL = window[-1].getAltitudeAGL()
        if not (finalAltAGL > initialAltAGL + 30):
            return False

        print(
            "** takeoff **",
            window[0].getTimestamp(),
            "%+4dagl" % initialAltAGL,
            " %3dkph" % initialSpeed,
             " ==>> ",
            window[-1].getTimestamp(),
             "%+4dagl" % finalAltAGL,
             " %3dkph" % finalSpeed,
             sep='')
        return True, t1

    def detectLanding(timeframeOfWindow, window):

        t1 = window[0].getTimestamp()
        windowSize = len(window)

        # remove observations that are out of range
        for y in range(0, windowSize):
            if (t1 < window[-1].getTimestamp() < t1+datetime.timedelta(seconds=timeframeOfWindow)):
                break
            else:
                window.pop()

        if not (len(window) > 0):
            return False

        # ensure rollout speed
        finalSpeed = int(window[-1].getSpeed())
        if not (finalSpeed < 16):
            return False

        # ensure on the ground
        finalAltAGL = window[-1].getAltitudeAGL()
        if not (Aircraft.atGroundLevel(finalAltAGL)):
            return False

        # ensure approaching at speed
        initialSpeed = int(window[0].getSpeed())
        if not (initialSpeed > 40):
            return False

        # ensure approaching from altitude
        initialAltAGL = window[0].getAltitudeAGL()
        if not (initialAltAGL > finalAltAGL + 30):
            return False

        print(
            "** landing **",
            window[0].getTimestamp(),
            "%+4dagl" % initialAltAGL,
            " %3dkph" % initialSpeed,
             " ==>> ",
            window[-1].getTimestamp(),
             "%+4dagl" % finalAltAGL,
             " %3dkph" % finalSpeed,
             sep='')
        return window[-1].getTimestamp()

        return True, t1

    def reportFlights(self):

        observationPeriod = 45

        n = len(self.getSentences())
        if (n > 0): n -= 1

        # move through the list, one observation at a time
        for x in range(0, n):

            # carve out smaller lists of observations.
            takeoffObservations = self.sentences[x:x+observationPeriod]
            landingObservations = self.sentences[x:x+observationPeriod]
            takeoffTime = Aircraft.detectTakeoff(observationPeriod, takeoffObservations)
            if not (takeoffTime):
                l = Aircraft.detectLanding(observationPeriod, landingObservations)

        return

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
