

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
                print("**", values[1].strip("\'"), values[3].strip("\'"))
                self.OgnDict[values[1].strip("\'")] = values[3].strip("\'")
                #print(detail[1], detail[3])
        print(self.OgnDict)

    def getAircraft(self, radioId):
        pass
        #print(self.OgnDict[radioId])
        #return self.OgnDict[radioId]
