#!/usr/bin/python3
import io

import pynmea2

import math

from airfield import Airfield
from aircraft import AircraftPosition
from registrations import Registration

theAirfield = Airfield(81, 45.062101, 075.374431)
theAircraftPosition = AircraftPosition("C-FXYZ")

def is_integer(n):
    try:
        int(n)
        return True
    except ValueError:
        return False

try:
    print(x)
except:
    print("An exception occurred")

altMax=-10000
altMin=+10000
alt=0
altitudeOberservations=0

nmea = open('data.nmea', 'r')

for line in nmea:
    line = nmea.readline()
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
                registration = Registration()
                radio = msg.data[10]
                #print(registration.get(radio))
                pass
            elif (msg.data[0] == 'A'):
                #print(msg.data)
                # distance
                theAircraftPosition.set(theAirfield.timestamp, msg)
                if (theAircraftPosition.id == "C-GDQK"):
                    theAircraftPosition.print()
        #for property, value in vars(msg).items():
        #    print(property, ":", value)

    elif (msg.sentence_type == 'RMC'):
        # this sentence has the airfield datestamp
        datestamp = msg.datestamp
        theAirfield.setDatestamp(datestamp)
        #print(repr(msg))
    elif (msg.sentence_type == 'GGA' and
        theAirfield.validDatestamp()):
        # this sentence has the airfield timestamp, lat, lon, elevation
        theAirfield.set(msg)


print()
print("Airfield report")
print("===============")
print("min alt:", theAirfield.elevationMin, "max alt:", theAirfield.elevationMax, "curr alt", theAirfield.elevation)
print("average elevation", theAirfield.averageElevation())
print("lat:", theAirfield.lat, "lon:", theAirfield.lon)
print("date:", theAirfield.datestamp, "time:", theAirfield.timestamp)
print("observations:", theAirfield.observations)
