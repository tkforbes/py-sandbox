#!/usr/bin/python3

import io

import pynmea2

import math

import sys

from airfield import Airfield
from flarmProximateAircraft import FlarmProximateAircraft
from ognRegistrations import OgnRegistration
from flarmPriorityIntruder import FlarmPriorityIntruder

theAirfield = Airfield(81, 45.062101, 075.374431)
proximateAircraft = FlarmProximateAircraft()
theOgnReg = OgnRegistration()
priorityIntruder = FlarmPriorityIntruder()


#sys.exit()


def is_integer(n):
    try:
        int(n)
        return True
    except ValueError:
        return False

#try:
#    print(x)
#except:
#    print("An exception occurred")

altMax=-10000
altMin=+10000
alt=0
altitudeOberservations=0

nmea = open('data.nmea', 'r')

for line in nmea:
    #line = nmea.readline()
    try:
        msg = pynmea2.parse(line)
    except pynmea2.ChecksumError:
        #print("**bad nmea sentence. checksum error**")
        continue
    except pynmea2.ParseError:
        #print("**bad nmea sentence. parse error**")
        continue
    except:
        #print("**bad nmea sentence. something wrong error**")
        continue

    #print(repr(msg))

    #print(type(msg))

    #print(msg.sentence_type)

    if (type(msg) is pynmea2.nmea.ProprietarySentence and
        theAirfield.validDatestamp()):
        if (msg.manufacturer == "FLA"):
            if (msg.data[0] == 'U'):
                #print(repr(msg))
                if (priorityIntruder.set(theAirfield.timestamp, msg)):
                    priorityIntruder.print()
            elif (msg.data[0] == 'A'):
                #print(msg.data)
                # distance
                proximateAircraft.set(theAirfield.timestamp, msg)
                proximateAircraft.print()
        #for property, value in vars(msg).items():
        #    print(property, ":", value)

    elif (msg.sentence_type == 'RMC'):
        # this sentence contains the current date

        # set the date in the airfield. the date is very important!
        datestamp = msg.datestamp
        theAirfield.setDatestamp(datestamp)
    elif (msg.sentence_type == 'GGA' and
        theAirfield.validDatestamp()):
        # this sentence has the airfield timestamp, lat, lon, elevation
        theAirfield.set(msg)


print()
print(theAirfield.report())
print()
print(proximateAircraft.report())
print()
print(priorityIntruder.report())
