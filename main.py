#!/usr/bin/python3

import io

import pynmea2

import math

try:
    print(x)
except:
    print("An exception occurred")

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
                print("relativeVertical", msg.data[3])

        #for property, value in vars(msg).items():
        #    print(property, ":", value)

    elif (msg.sentence_type == 'RMC' or msg.sentence_type == 'GGA' ):
        print(msg.sentence_type, msg.timestamp)
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
