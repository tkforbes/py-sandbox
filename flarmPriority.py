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

        # alarmtype - hex 0 to ff. values 0, 2, 3
        # - process this ahead of relative bearing because
        #   its value may cause relative bearing to be empty
        try:
            ndx = priorityIndex.get('AlarmType')

            # this is not strictly a good test, according to spec.
            # however, only three values are presently permitted and they
            # each fall within int range.
            int(ndx)
            alarmType = int(nmea.data[ndx])
            if not (alarmType == 0 or alarmType == 2 or alarmType == 3):
                msg = "alarmType. value " + str(alarmType) + ": invalid."
                raise Exception(msg)
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # alarm type is zero when no aircraft are in range. In that case,
        # there would not be a value for relative bearing, relative vertical
        # or relative distance. nothing else to do...
        if (alarmType == 0): return

        # relativeBearing. when alarm type is not zero, valid
        # range is -180 to 180
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

        # relativeVertical. when alarm type is not zero, valid
        # range is -32768 to 32767
        try:
            ndx = priorityIndex.get('relativeVertical')
            int(ndx)
            relativeVertical = int(nmea.data[ndx])
            if not (relativeVertical >= -32768 and relativeVertical <= 32767):
                msg = "relativeVertical. value " + str(relativeVertical) + ": out of range"
                raise Exception(msg)
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

        # relativeDistance. when alarm type is not zero, valid
        # range is 0 to 2147483647.
        try:
            ndx = priorityIndex.get('relativeDistance')
            int(ndx)
            relativeDistance = int(nmea.data[ndx])
            if not (relativeDistance >= 0 and relativeDistance <= 2147483647):
                msg = "relativeDistance. value " + str(relativeDistance) + ": out of range"
                raise Exception(msg)
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()


        # id (radio id) - six digit hex
        try:
            ndx = priorityIndex.get('radioId')
            int(ndx)
            radioId = nmea.data[ndx]
            if (len(radioId) != 6):
                msg = "radio id must be 6 chars in length. " + radioId
                raise Exception(msg)
            hex(int(radioId, 16)) # ensure radio id can convert to hex.
        except Exception as e:
            print(nmea, ":", e)
            sys.exit()

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
