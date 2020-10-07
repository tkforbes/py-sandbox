class Aircraft:

    #sentences = []

    def __init__(self, reg):
        self.aircraftId = reg
        self.sentences = []

    def append(self, sentence):
        self.sentences.append(sentence)

    def getSentences(self):
        return self.sentences

    def getAircraftId(self):
        return self.aircraftId

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
