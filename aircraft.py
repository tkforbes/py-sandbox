from enum import Enum

class FlightState(Enum):
        LANDED = 1
        DEPARTING = 2
        FLYING = 3
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

    def reportFlights(self):

        state = FlightState.LANDED
        prevSpeed = 0

        sentences = self.getSentences()
        for s in sentences:
            if (s.getSource() == "PFLAA"):
                t = s.getTimestamp()
                v = s.getSpeed()
                agl = s.getAltitudeAGL()


                if (state == FlightState.LANDED):
                    if (v > 60 and 30 < agl < 130 ):
                        departed = t
                        state = FlightState.DEPARTING
                        print("%11s" %"departing",
                            "%8s" % t,
                            "%3dkph" % v,
                            "%4dm AGL" % agl
                        )

                if (state == FlightState.DEPARTING):
                    if (v > 60 and agl >= 130 ):
                        state = FlightState.FLYING
                        print("%11s" %"flying",
                            "%8s" % t,
                            "%3dkph" % v,
                            "%4dm AGL" % agl
                        )

                if (state == FlightState.FLYING):
                    if (v > 60 and 20 < agl < 100 ):
                        state = FlightState.APPROACHING
                        print("%11s" %"approaching",
                            "%8s" % t,
                            "%3dkph" % v,
                            "%4dm AGL" % agl
                        )

                if (state == FlightState.APPROACHING):
                    if (v < 30 and -30 < agl < 15 ):
                        state = FlightState.LANDED
                        print("%11s" %"landed",
                            "%8s" % t,
                            "%3dkph" % v,
                            "%4dm AGL" % agl,
                            "duration: %s" % str(t - departed)
                        )

        return


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
