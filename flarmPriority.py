from ognRegistrations import OgnRegistration

class FlarmPriority:
    def __init__(self):
        aircraftId = ''
        timestamp = 0
        relativeBearing = 0
        relativeVertical = 0
        relativeDistance = 0

        self.relativeDistance = 0
        self.observations = 0
        self.maxDistance = 0

    def set(self, timestamp, nmea):

        #if (nmea.sentence_type == 'ProprietarySentence'):
        #    print(True)
        #    prop = nmea

        #print("nmea:", nmea)
        theOgnReg = OgnRegistration()
        aircraftId = theOgnReg.getAircraft(nmea.data[10])
        if not (aircraftId == "not found"):
            self.aircraftId = aircraftId

        self.timestamp = timestamp

        self.relativeBearing = nmea.data[6]

        relVert = nmea.data[8]
        if (len(relVert) == 0):
            self.relativeVertical = 0
        else:
            self.relativeVertical = relVert

        relDist = nmea.data[9]
        if (len(relDist) == 0):
            self.relativeDistance = 0
        else:
            self.relativeDistance = int(relDist)
            if (self.relativeDistance > self.maxDistance):
                self.maxDistance = self.relativeDistance

        self.observations += 1

        print(
            self.aircraftId,
            self.timestamp,
            "\t dist:%5d" % int(self.relativeDistance),
            "alt AGL:%4s" % self.relativeVertical,
            "\t\t\t\tbearing:%s" % self.relativeBearing
            )

    def report(self):
        print("Priority")
        print("========")
        print("observations:%6d" % self.observations,
            "max distance:%6d" % self.maxDistance
            )
