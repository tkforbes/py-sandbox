class Aircraft:
    def __init__(self, id):
        self.id = id
        self.status = "unknown"
        self.relativeNorth = 0.0
        self.relativeEast = 0.0
        self.relativeVertical = 0.0
        self.speed = 12.0

    def getSpeed(self):
        # speed in kph
        return self.speed*3.6

    def getAlt(self):
        return self.relativeVertical

    def getDistance(self):
        n = self.relativeNorth
        e = self.relativeEast
        return int(math.sqrt( n*n+e*e))
