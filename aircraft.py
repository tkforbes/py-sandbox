from enum import Enum

import datetime

import numpy as np

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


    def reportFlights(self):
        # ground level is considered GPS AGL plus or minus x metres
        groundLevelDeviation = 30

        windowSize = 45

        n = len(self.getSentences())
        if (n > 0): n -= 1

        # move through the list, one observation at a time
        for x in range(0, n):
            # get a small segment of the list, at most 30 observations from now
            takeoffList = self.sentences[x:x+windowSize]
            landingList = takeoffList
            t1 = takeoffList[0].getTimestamp()

            # remove observations that are out of range
            for y in range(0, len(takeoffList)):
                if not(t1 < takeoffList[-1].getTimestamp() < t1+datetime.timedelta(seconds=windowSize)):
                    # print("** pop **", takeoffList[-1].getTimestamp())
                    takeoffList.pop()

            if (len(takeoffList) > 0):
                initialSpeed = int(takeoffList[0].getSpeed())
                finalSpeed = int(takeoffList[-1].getSpeed())
                initialAltAGL = takeoffList[0].getAltitudeAGL()
                finalAltAGL = takeoffList[-1].getAltitudeAGL()

                if (initialSpeed == 0 and finalSpeed > 45):
                    if (-1*groundLevelDeviation < initialAltAGL < groundLevelDeviation and
                        finalAltAGL > initialAltAGL + 20):
                        print(
                            "** takeoff **",
                            takeoffList[0].getTimestamp(),
                            "%+4dagl" % initialAltAGL,
                            " %3dkph" % initialSpeed,
                             " ==>> ",
                            takeoffList[-1].getTimestamp(),
                             "%+4dagl" % finalAltAGL,
                             " %3dkph" % finalSpeed,
                             sep='')

            # remove observations that are out of range
            for y in range(0, len(landingList)):
                if not(t1 < landingList[-1].getTimestamp() < t1+datetime.timedelta(seconds=windowSize)):
                    landingList.pop()

            if (len(landingList) > 0):
                initialSpeed = int(landingList[0].getSpeed())
                finalSpeed = int(landingList[-1].getSpeed())
                initialAltAGL = landingList[0].getAltitudeAGL()
                finalAltAGL = landingList[-1].getAltitudeAGL()

                if (initialSpeed > 40 and finalSpeed < 10):
                    if (-30 < finalAltAGL < 30 and
                        initialAltAGL > finalAltAGL + 30):
                        print(
                            "** landing **",
                            landingList[0].getTimestamp(),
                            "%+4dagl" % initialAltAGL,
                            " %3dkph" % initialSpeed,
                             " ==>> ",
                            landingList[-1].getTimestamp(),
                             "%+4dagl" % finalAltAGL,
                             " %3dkph" % finalSpeed,
                             sep='')

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
