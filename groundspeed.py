class Groundspeed(int):
    def __new__(cls, value):
        return int.__new__(cls, int(value))

    def kph(self):
        return self * 3.6
