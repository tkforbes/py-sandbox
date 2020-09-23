#!/usr/bin/python3

import io

import pynmea2

"""
ser = serial.Serial('/dev/ttyS1', 9600, timeout=5.0)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
"""

nmea = open('data.nmea', 'r')

for line in nmea:
    line = nmea.readline()
    msg = pynmea2.parse(line)
    print(repr(msg))
