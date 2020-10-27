#!/usr/bin/python3
import pynmea2
#import geopy
#import geopy.distance

from groundstation import Groundstation
from observation import Observation
from ognRegistrations import OgnRegistration
from event import Event
from event import TakeoffEvent
from event import LandingEvent
from event import LaunchEvent
import datetime
from aircraft import Aircraft


observation = Observation()

def eachAircraft():

    groundstation = Groundstation()


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

                observation = Observation()
                if observation.set(groundstation, sentence):
                    aircraftId = observation.getAircraftId()
                    if not (aircraftId in aircraftSeen):
                        aircraftSeen[aircraftId] = Aircraft(aircraftId)
                    aircraftSeen[aircraftId].appendObservations(observation)

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

    # reg = "C-GFOP"
    # print("")
    # print(reg)
    # aircraftSeen[reg].printObservations()

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
                le = LaunchEvent(reg, e.getTimestamp(), e.getLat(), e.getLon(),
                    e.getAltitudeAGL(), e.getTrack(), e.speed)
                # print(le.getTimestamp(), reg, repr(le))
                flightSheet.append(le)

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

                if observation.set(groundstation, sentence):
                    aircraftId = observation.getAircraftId()
                    if not (aircraftId in aircraftSeen):
                        aircraftSeen[aircraftId] = Aircraft(aircraftId)
                    aircraftSeen[aircraftId].appendObservations(sentence)
                    observation.printt()


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
    observation.report()

# ============================================================================

#processNmeaStream()
eachAircraft()
