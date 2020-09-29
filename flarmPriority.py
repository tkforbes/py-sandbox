from ognRegistrations import OgnRegistration

import sys

priorityIndex = {
    'rx' : 1,
    'tx' : 2,
    'gps' : 3,
    'power' : 4,
    'alarmLevel' : 5,
    'relativeBearing' : 6,
    'AlarmType' : 7,
    'relativeVertical' : 8,
    'relativeDistance' : 9,
    'radioId' : 10
}


class FlarmPriority:
    def __init__(self):
        aircraftId = ''
        timestamp = 0
        relativeBearing = 0
        relativeVertical = 0
        relativeDistance = 0

        self.relativeDistance = 0
        self.observations = 0
        self.maxDistance = 0

    def set(self, timestamp, nmea):

        #rx positive integer 0 to 99
        try:
            ndx = priorityIndex.get('rx')
            int(ndx)
            rx = int(nmea.data[ndx])
            if (rx < 0 or rx > 99):
                raise Exception("rx out of range")
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # tx 0 or 1
        try:
            ndx = priorityIndex.get('tx')
            int(ndx)
            tx = int(nmea.data[ndx])
            if not (tx == 0 or tx == 1):
                raise Exception("tx out of range")
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # gps 0 or 1 or 2
        try:
            ndx = priorityIndex.get('gps')
            int(ndx)
            gps = int(nmea.data[ndx])
            if (gps < 0 or gps > 2):
                msg = "gps value " + str(gps) + ": out of range"
                raise Exception(msg)
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # power 0 or 1
        try:
            ndx = priorityIndex.get('power')
            int(ndx)
            power = int(nmea.data[ndx])
            if not (power == 0 or power == 1):
                raise Exception("power out of range")
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()


        # alarm level 0 to 3
        try:
            ndx = priorityIndex.get('alarmLevel')
            int(ndx)
            alarmLevel = int(nmea.data[ndx])
            if (alarmLevel < 0 or alarmLevel > 3):
                msg = "alarm level. value " + str(alarmLevel) + ": out of range"
                raise Exception(msg)
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()


        # relativeBearing -180 to 180
        try:
            ndx = priorityIndex.get('relativeBearing')
            int(ndx)
            relativeBearing = int(nmea.data[ndx])
            if not (relativeBearing >= -180 and relativeBearing <= 180):
                msg = "relativeBearing. value " + str(relativeBearing) + ": out of range"
                raise Exception(msg)
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()



        """
        alarmtype - hex 0 to ff. values 0, 2, 3
        relativeVertical - -32768 to 32767
        relativeDistance - 0 to 2147483647.
        id - six digit hex
        """

        #if (nmea.sentence_type == 'ProprietarySentence'):
        #    print(True)
        #    prop = nmea

        #print("nmea:", nmea)
        theOgnReg = OgnRegistration()
        aircraftId = theOgnReg.getAircraft(nmea.data[10])
        if not (aircraftId == "not found"):
            self.aircraftId = aircraftId

        self.timestamp = timestamp

        self.relativeBearing = nmea.data[6]

        relVert = nmea.data[8]
        if (len(relVert) == 0):
            self.relativeVertical = 0
        else:
            self.relativeVertical = relVert

        relDist = nmea.data[9]
        if (len(relDist) == 0):
            self.relativeDistance = 0
        else:
            self.relativeDistance = int(relDist)
            if (self.relativeDistance > self.maxDistance):
                self.maxDistance = self.relativeDistance

        self.observations += 1

        print(
            self.aircraftId,
            self.timestamp,
            "\t dist:%5d" % int(self.relativeDistance),
            "alt AGL:%4s" % self.relativeVertical,
            "\t\t\t\tbearing:%s" % self.relativeBearing
            )

    def report(self):
        print("Priority")
        print("========")
        print("observations:%6d" % self.observations,
            "max distance:%6d" % self.maxDistance
            )

"""
valid

PFLAU,<RX>,<TX>,<GPS>,<Power>,<AlarmLevel>,<RelativeBearing>,
<AlarmType>,<RelativeVertical>,<RelativeDistance>,<ID>

checksum
rx positive integer 0 to 99
tx 0 or 1
gps 0 or 1 or 2
power 0 or 1
alarm level 1 or 2 or 3
relativeBearing -180 to 180
alarmtype - hex 0 to ff. values 0, 2, 3
relativeVertical - -32768 to 32767
relativeDistance - 0 to 2147483647.
id - six digit hex
"""
