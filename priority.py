from registrations import Registration

class Priority:
    def __init__(self):
        relativeBearing = 0
        relativeVertical = 0
        relativeDistance = 0
        id = ''


    def set(self, nmea):
        print

        #if (nmea.sentence_type == 'ProprietarySentence'):
        #    print(True)
        #    prop = nmea

        id = nmea.data[10]
        if (len(id) > 0):
            registration = Registration()
            radio = registration.get(nmea.data[10])
            self.id = radio.get()
            print(self.id)
