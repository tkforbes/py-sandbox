#!/usr/bin/python3

import io

import pynmea2

import math

import sys

from airfield import Airfield
from flarmProximateAircraft import FlarmProximateAircraft
from ognRegistrations import OgnRegistration
from flarmPriorityIntruder import FlarmPriorityIntruder

airfield = Airfield(81, 45.062101, 075.374431)
proximateAircraft = FlarmProximateAircraft()
priorityIntruder = FlarmPriorityIntruder()

def is_integer(n):
    try:
        int(n)
        return True
    except ValueError:
        return False

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

    # don't do anything with Flarm sentences until the airfield
    # has a valid datestamp.
    if (type(msg) is pynmea2.nmea.ProprietarySentence and
        airfield.validDatestamp()):
        if (msg.manufacturer == "FLA"):
            if (msg.data[0] == 'U'):
                #print(repr(msg))
                if (priorityIntruder.set(airfield.timestamp, msg)):
                    priorityIntruder.print()
            elif (msg.data[0] == 'A'):
                if (proximateAircraft.set(airfield.timestamp, msg)):
                    proximateAircraft.print()
        #for property, value in vars(msg).items():
        #    print(property, ":", value)

    elif (msg.sentence_type == 'RMC'):
        # this sentence contains the current date

        # update the date in the airfield. the date is very important!
        datestamp = msg.datestamp
        airfield.setDatestamp(datestamp)
    elif (msg.sentence_type == 'GGA' and
        airfield.validDatestamp()):
        # this sentence has the airfield timestamp, lat, lon, elevation
        airfield.set(msg)


airfield.report()
proximateAircraft.report()
priorityIntruder.report()
