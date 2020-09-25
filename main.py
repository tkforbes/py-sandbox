#!/usr/bin/python3

import io

import pynmea2

import math

from airfield import Airfield
from aircraft import Aircraft

kars = Airfield(81, 45.062101, 075.374431)
aircraft = Aircraft("TUB")
print(aircraft.status)
print(aircraft.getSpeed())

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
        print("**bad nmea sentence. checksum error**")
        continue
    except pynmea2.ParseError:
        print("**bad nmea sentence. parse error**")
        continue
    except:
        print("**bad nmea sentence. something wrong error**")
        continue

    #print(repr(msg))

    #print(type(msg))

    #print(msg.sentence_type)

    if (type(msg) is pynmea2.nmea.ProprietarySentence):
        if (msg.manufacturer == "FLA"):
            if (msg.data[0] == 'U'):
                pass
            elif (msg.data[0] == 'A'):
                print(msg.data)
                # distance
                n= abs(int(msg.data[2]))
                e= abs(int(msg.data[3]))
                print("distance", int(math.sqrt( n*n+e*e)))
                print("relativeVertical", msg.data[4])
                print("gnd speed kph", int(int(msg.data[9])*3.6))

        #for property, value in vars(msg).items():
        #    print(property, ":", value)

    elif (msg.sentence_type == 'RMC'):
        print(msg.sentence_type, msg.timestamp)
        datestamp = msg.datestamp
        kars.setDatestamp(datestamp)
        #print(repr(msg))
    elif (msg.sentence_type == 'GGA' ):
        print("*******")
        kars.set(msg)
        """
        print(type(msg))
        print(msg.sentence_type, msg.timestamp, "alt: ", msg.altitude)
        """
        if (msg.altitude is not None and is_integer(msg.altitude) and int(msg.num_sats) > 4):
            alt += int(msg.altitude)
            altitudeOberservations += 1
            print(msg)
            if (int(msg.altitude) > altMax ): altMax = msg.altitude
            if (int(msg.altitude) < altMin ): altMin = msg.altitude

    #elif (msg.sentence_type == 'GGA'):
    #    print(msg.sentence_type, msg.timestamp)
    #else:
    #    print(msg)



    #for property, value in vars(msg).items():
    #    print(property, ":", value)


    # start getting the information ready to log. to do this,
    # we want the information about the reporting aircraft.
    #
    # a rough list is
    # - timestamp
    # - ac_id
    # - elevation
    # - ground speed
    # - direction

print("alt max", altMax)
print("alt min", altMin)
print ("alt avg:", alt/altitudeOberservations, "from", altitudeOberservations, "observations")

print(kars.altitude, kars.lat, kars.lon, kars.datestamp, kars.timestamp)
