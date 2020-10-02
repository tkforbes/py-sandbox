
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
