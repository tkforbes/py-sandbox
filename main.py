#!/usr/bin/python3
import pynmea2
#import geopy
#import geopy.distance

from groundstation import Groundstation
from observation import Observation
#from ognRegistrations import OgnRegistration
from event import Event
from event import TakeoffEvent
#from event import LandingEvent
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

        # ignore Flarm PFLAU sentences
        if (Observation.isPflauSentence(sentence)):
            continue

        # The groundstation must have received the UTC time from the GPS
        # before we permit any processing of Flarm PFLAA observations.
        if (groundstation.validTime() and
            Observation.isPflaaSentence(sentence)):
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
            if type(e) is TakeoffEvent:
                le = LaunchEvent(reg, e.getTimestamp(), e.getLat(), e.getLon(),
                                 e.getAltitudeAGL(), e.getTrack(), e.speed)
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
        if (previous - datetime.timedelta(seconds=30) <
                current <
                previous + datetime.timedelta(seconds=30)):
            # this is a takeoff pair
            print("%02d" % y,
                  "Launch ",
                  current,
                  "R%02d" % flightSheet[n].getRwy(),
                  flightSheet[n].getReg(),
                  flightSheet[n-1].getReg()
                  )
            y+=1
        # the pair is not a match. what about the upcoming pair?
        elif next - datetime.timedelta(seconds=30) < current < next + datetime.timedelta(seconds=30):
            # do nothing. the next iteration of the loop will process the pair
            pass
        else:
            # this is a lone takeoff event
            print("%02d" % y,
                  "Takeoff", current,
                  "R%02d" % flightSheet[n].getRwy(),
                  flightSheet[n].getReg()
                  )
            y+=1

    return


# ============================================================================

#processNmeaStream()
eachAircraft()
