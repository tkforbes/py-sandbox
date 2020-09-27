

class OgnRegistration:
    def __init__(self):
        self.OgnDict = {
#                 '000368': 'C-GORE',
#                 '003974': 'C-GFOP',
#                 'FF4A68': 'C-GINY'
        }
        with open('aircraft.canada', 'r') as ognRegistrations:
            for detail in ognRegistrations:
                #.split(",")
                values = detail.strip().split(",")

                radioId = values[1].strip("\'")
                aircraftId = values[3].strip("\'")

                # append
                self.OgnDict[radioId] = aircraftId
                #print(detail[1], detail[3])
        #print(self.OgnDict)

    def getAircraft(self, radioId):
        return self.OgnDict.get(radioId, "not found")
