
class Aircraft:

    #sentences = []

    def __init__(self, reg):
        self.aircraftId = reg
        self.sentences = []

    def append(self, sentence):
        print("appending :", sentence)
        print("list len before:", len(self.sentences))
        self.sentences.append(sentence)
        print("list len after :", len(self.sentences))

    def getSentences(self):
        return self.sentences

    def getAircraftId(self):
        return self.aircraftId
