from ognRegistrations import OgnRegistration

class Priority:
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
        self.relativeVertical = nmea.data[8]
        self.relativeDistance = nmea.data[9]

        print(
            self.aircraftId,
            self.timestamp,
            "dist:", self.relativeDistance,
            "alt AGL:", self.relativeVertical,
            "bearing:", self.relativeBearing
            )
