from enum import Enum

import datetime
import pytz
from groundstation import Groundstation

class Aircraft:

    # static datetime value used by class to indicate failure
    event_not_detected = pytz.utc.localize(datetime.datetime.min)


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

    def trim(timeframeOfWindow, window):
        '''
        a window of observations might contain observations beyond
        the unexpected timeframe. trim the window to just the expected
        timeframe by removing extraneous observations from the tail end.
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

    def detectRunway(window):
        rwy = 0
        n = 0
        for obs in range(0, len(window)):
            if Groundstation.atGroundLevel(window[obs].getAltitudeAGL() and
                window[obs].getSpeed() > 10):

                # this won't work for North, where values are near 360 and 0

                # print(
                #     "%2d" % obs,
                #     "%2dm" % window[obs].getAltitudeAGL(),
                #     "%3dkph" % window[obs].getSpeed(),
                #     "%3ddeg" % window[obs].getTrack())

                # eventually, we will calculat the average runwaay
                rwy += window[obs].getTrack()
                n += 1
        # print(
        #     "%4d tot runway" % rwy,
        #     "%3d obs" % obs
        #     )

        # calculate the average and divide by ten
        rwy = int(rwy/n/10)

        # correct for known runways. This is Kars specific, for now.
        if (22 <= rwy <= 27):
            rwy = 26
        elif (6 <= rwy <= 10):
            rwy = 8

        return rwy

    def detectTakeoff(timeframeOfWindow, window):
        t1 = window[0].getTimestamp()

        if not (len(window) > 0):
            return Aircraft.event_not_detected

        # takeoff inital rolling speed
        # when too slow, a towplane rolling-up to a glider
        # gets included! The heading of the towplane is wrong at that point,
        # which messes with R calculation.
        initialSpeed = int(window[0].getSpeed())
        if not (9 <= initialSpeed <= 19):
            return Aircraft.event_not_detected

        # initial climbout speed at least this
        finalSpeed = int(window[-1].getSpeed())
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

        rwy = Aircraft.detectRunway(window)

        print(
            "Takeoff ",
            window[0].getTimestamp().astimezone(Groundstation.TZ),
            " R%02d" % int(rwy),
            " %+4dagl" % initialAltAGL,
            " %3dkph" % initialSpeed,
             " ==>> ",
            window[-1].getTimestamp().astimezone(Groundstation.TZ),
             " %+4dagl" % finalAltAGL,
             " %3dkph" % finalSpeed,
             " ",
             window[-1].getTimestamp() - window[0].getTimestamp(),
             sep='')
        return t1

    def detectLanding(timeframeOfWindow, window):
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
        if not (Groundstation.atGroundLevel(finalAltAGL)):
            return Aircraft.event_not_detected

        # ensure approaching at speed
        initialSpeed = int(window[0].getSpeed())
        if not (initialSpeed > 40):
            return Aircraft.event_not_detected

        # ensure approaching from altitude
        initialAltAGL = window[0].getAltitudeAGL()
        if not (initialAltAGL > finalAltAGL + 30):
            return Aircraft.event_not_detected

        rwy = Aircraft.detectRunway(window)

        print(
            "Landing ",
            window[0].getTimestamp().astimezone(Groundstation.TZ),
            " R%02d" % rwy,
            " %+4dagl" % initialAltAGL,
            " %3dkph" % initialSpeed,
             " ==>> ",
            window[-1].getTimestamp().astimezone(Groundstation.TZ),
             " %+4dagl" % finalAltAGL,
             " %3dkph" % finalSpeed,
             " ",
             window[-1].getTimestamp() - window[0].getTimestamp(),
             sep='')

        return window[-1].getTimestamp()

    def reportFlights(self):

        tTakeoff = Aircraft.event_not_detected
        tLanding = Aircraft.event_not_detected

        # num of seconds of an observation period. The period is used
        # in determining flight events like takeoff and landing.
        observationPeriod = 45


        n = len(self.getSentences())
        if (n > 0): n -= 1  # correct for zero-based index

        # move through the list, one observation at a time
        for x in range(0, n):

            # create views of a limited timeframe.
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
