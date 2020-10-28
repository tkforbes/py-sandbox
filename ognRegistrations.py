OgnDb = {
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
        OgnDb[radioId] = detail

class OgnRegistration:
    def getAircraft(self, radioId):
        ognReg = OgnDb.get(radioId)
        if ognReg is None:
            # when registration is not found, return the radio id.
            ac = radioId
        else:
            values = ognReg.strip().split(",")
            ac = values[3].strip("\'")

        return ac

    def getAircraftType(self, radioId):
        ognReg = OgnDb.get(radioId)
        if ognReg is None:
            # when registration is not found, return the radio id.
            acType = radioId
        else:
            values = ognReg.strip().split(",")
            acType = values[7].strip("\'")

        return acType
