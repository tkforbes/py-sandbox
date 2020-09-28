from ognRegistrations import OgnRegistration

class FlarmPriority:
    def __init__(self):
        aircraftId = ''
        timestamp = 0
        relativeBearing = 0
        relativeVertical = 0
        relativeDistance = 0

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
            self.relativeVertical = 0

        relDist = nmea.data[9]
        if (len(relDist) == 0):
            self.relativeDistance = 0
        else:
            self.relativeDistance = relDist

        print(
            self.aircraftId,
            self.timestamp,
            "\t dist:%5d" % int(self.relativeDistance),
            "alt AGL:%4d" % self.relativeVertical,
            "\t\t\t\tbearing:%s" % self.relativeBearing
            )
