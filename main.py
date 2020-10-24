#!/usr/bin/python3
import pynmea2
import geopy
import geopy.distance

from groundstation import Groundstation
from pflaa import Pflaa
from ognRegistrations import OgnRegistration
from event import Event
from event import TakeoffEvent
from event import LandingEvent
from event import FlightsheetTakeoffEvent
from event import FlightsheetLandingEvent
import datetime

pflaa = Pflaa()

def eachAircraft():

    groundstation = Groundstation()

    from aircraft import Aircraft

    aircraftSeen = {
    }

    nmea = open('data.nmea', 'r')

    for line in nmea:
        #line = nmea.readline()
        try:
            commas = line.count(',')
            sentence = pynmea2.parse(line, check=True)
        except pynmea2.ChecksumError:
            # ignore sentences that produce a checksum error
            continue
        except pynmea2.ParseError:
            # ignore sentences that can't be parsed
            continue
        except Exception:
            continue

        # don't do anything with Flarm sentences until the groundstation
        # has a valid datestamp.
        if (isinstance(sentence, pynmea2.nmea.ProprietarySentence) and
                groundstation.validTime()):
            if sentence.manufacturer == "FLA":
                # this is a Flarm sentence. try to set it.

                pflaa = Pflaa()
                if pflaa.set(groundstation, sentence):
                    aircraftId = pflaa.getAircraftId()
                    if not (aircraftId in aircraftSeen):
                        aircraftSeen[aircraftId] = Aircraft(aircraftId)
                    aircraftSeen[aircraftId].appendObservations(pflaa)

        elif sentence.sentence_type == 'RMC':
            # this sentence contains the current date

            groundstation.setDate(sentence.datestamp)
            groundstation.set(sentence)
            # update the date in the groundstation. the date is very important!
            #print("course true:", sentence.true_course)
        elif (sentence.sentence_type == 'GGA'
                and groundstation.validDate()
                and commas == 14):

            # this sentence has the groundstation timestamp, lat, lon, elevation
            groundstation.set(sentence)

    print("%s" % list(aircraftSeen.keys()))

    groundstation.report()

    reg = "C-GFOP"
    print("")
    print(reg)
    aircraftSeen[reg].printObservations()

    print("")
    print("FLIGHTS PER AIRCRAFT")
    print("====================")
    for ac in list(aircraftSeen.keys()):
        print("")
        print(ac)
        aircraftSeen[ac].detectEvents()
        aircraftSeen[ac].reportEvents()

    flightSheet = []
    for ac in list(aircraftSeen.keys()):
        reg = aircraftSeen[ac].getAircraftId()
        theEvents = aircraftSeen[ac].events
        for e in theEvents:
            if (type(e) is TakeoffEvent):
                takeoff= FlightsheetTakeoffEvent(reg, e.getTimestamp(), e.getLat(), e.getLon(),
                    e.getAltitudeAGL(), e.getTrack(), e.getSpeed())
                # print(le.getTimestamp(), reg, repr(le))
                flightSheet.append(takeoff)

    for ac in list(aircraftSeen.keys()):
        reg = aircraftSeen[ac].getAircraftId()
        theEvents = aircraftSeen[ac].events
        for e in theEvents:
            if (type(e) is LandingEvent):
                landing= FlightsheetLandingEvent(reg, e.getTimestamp(), e.getLat(), e.getLon(),
                    e.getAltitudeAGL(), e.getTrack(), e.getSpeed())
                # print(le.getTimestamp(), reg, repr(le))
                flightSheet.append(landing)

    flightSheet.sort()


    print("")
    print("Flight Sheet")
    print("============")

    y = 1

    # we work with pairs, so starting at the second takeoff and looking at
    # the first...
    for n in range(1, len(flightSheet)):
        previous = flightSheet[n-1].getTimestamp()
        current = flightSheet[n].getTimestamp()
        if n < len(flightSheet)-1:
            next = flightSheet[n+1].getTimestamp()
        else:
            next = Event.event_not_detected

        # are the current and previous takeoff within 30 seconds?
        if (previous - datetime.timedelta(seconds=30) < current < previous + datetime.timedelta(seconds=30)):
            # this is a takeoff pair
            print ("%02d" % y, "Launch ", current, "R%02d" % flightSheet[n].getRwy(), flightSheet[n].getReg(), flightSheet[n-1].getReg())
            y+=1
        # the pair is not a match. what about the upcoming pair?
        elif (next - datetime.timedelta(seconds=30) < current < next + datetime.timedelta(seconds=30)):
            # do nothing. the next iteration of the loop will process the pair
            pass
        else:
            # this is a lone takeoff event
            print ("%02d" % y, "Takeoff", current, "R%02d" % flightSheet[n].getRwy(), flightSheet[n].getReg())
            y+=1

    return

def processNmeaStream():

    aircraftSeen = {
    }

    from aircraft import Aircraft

    nmea = open('data.nmea', 'r')

    for line in nmea:
        #line = nmea.readline()
        try:
            sentence = pynmea2.parse(line, True)
            #print(sentence)
        except pynmea2.ChecksumError:
            # ignore sentences that produce a checksum error
            continue
        except pynmea2.ParseError:
            # ignore sentences that can't be parsed
            continue
        except:
             # ignore sentences that raise any other error
             continue

        #print(repr(sentence))

        #print(type(sentence))

        # don't do anything with Flarm sentences until the groundstation
        # has a valid datestamp.
        if (isinstance(sentence, pynmea2.nmea.ProprietarySentence) and
                groundstation.validTime()):
            if sentence.manufacturer == "FLA":
                # this is a Flarm sentence. try to set it.

                if pflaa.set(groundstation, sentence):
                    aircraftId = pflaa.getAircraftId()
                    if not (aircraftId in aircraftSeen):
                        aircraftSeen[aircraftId] = Aircraft(aircraftId)
                    aircraftSeen[aircraftId].appendObservations(sentence)
                    pflaa.printt()


        elif sentence.sentence_type == 'RMC':
            # this sentence contains the current date

            # update the date in the groundstation. the date is very important!
            groundstation.setDatestamp(sentence.datestamp)
            #print("course true:", sentence.true_course)
        elif (sentence.sentence_type == 'GGA'
            and groundstation.validDate()):
            #and line.count(',') == 14):
            # this sentence has the groundstation timestamp, lat, lon, elevation
#            print('comma count:', line.count(','))
            print("found^^")
            groundstation.set(sentence)

    #print(aircraftSeen['C-GDQK'].getAircraftId())
    #print(len(aircraftSeen['C-GDQK'].getSentences()))
    #print(aircraftSeen['C-GDQK'].getSentences())

    groundstation.report()
    pflaa.report()

# ============================================================================

#processNmeaStream()
eachAircraft()
