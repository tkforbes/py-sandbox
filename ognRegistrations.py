#

OgnDict = {
# sample of format...
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
        OgnDict[radioId] = aircraftId

class OgnRegistration:
    def getAircraft(self, radioId):
        return OgnDict.get(radioId)
