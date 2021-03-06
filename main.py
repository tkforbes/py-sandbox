#!/usr/bin/python3
import datetime
import pynmea2
#import geopy
#import geopy.distance

import sqlite3

from groundstation import Groundstation
from observation import Observation
#from ognRegistrations import OgnRegistration
from event import Event
from event import TakeoffEvent
#from event import LandingEvent
from event import LaunchEvent
from aircraft import Aircraft




def eachAircraft():

    groundstation = Groundstation()

    aircraft_seen = {}

    conn = sqlite3.connect('flightevents.db')

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

        # ignore Flarm PFLAU sentences
        if Observation.is_pflau_sentence(sentence):
            continue

        # The groundstation must have received the UTC time from the GPS
        # before we permit any processing of Flarm PFLAA observations.
        if (groundstation.valid_time() and
                Observation.is_pflaa_sentence(sentence)):
            observation = Observation()
            if observation.set(conn, groundstation, sentence):
                aircraft_id = observation.get_aircraft_id()
                if aircraft_id not in aircraft_seen:
                    aircraft_seen[aircraft_id] = Aircraft(aircraft_id)
                aircraft_seen[aircraft_id].append_observations(observation)

        elif sentence.sentence_type == 'RMC':
            # this sentence contains the current date
            groundstation.set_date(sentence.datestamp)
            groundstation.set(sentence)
        elif (sentence.sentence_type == 'GGA'
              and groundstation.valid_date()
              and commas == 14):

            # this sentence has the groundstation timestamp, lat, lon, elevation
            groundstation.set(sentence)


    conn.close()


    print("%s" % list(aircraft_seen.keys()))

    groundstation.report()

    # reg = "C-GFOP"
    # print("")
    # print(reg)
    # aircraft_seen[reg].printObservations()

    print("")
    print("FLIGHTS PER AIRCRAFT")
    print("====================")
    for aircraft in list(aircraft_seen.keys()):
        print("")
        print(aircraft)
        aircraft_seen[aircraft].detect_events()
        aircraft_seen[aircraft].report_events()

    flight_sheet = []
    for aircraft in list(aircraft_seen.keys()):
        reg = aircraft_seen[aircraft].get_aircraft_id()
        the_events = aircraft_seen[aircraft].events
        for event in the_events:
            if isinstance(event, TakeoffEvent):
                launch_event = LaunchEvent(
                    reg, event.getTimestamp(), event.getLat(), event.getLon(),
                    event.getAltitudeAGL(), event.getTrack(), event.speed)
                flight_sheet.append(launch_event)

    flight_sheet.sort()


    print("")
    print("Flight Sheet")
    print("============")

    item_num = 1

    # we work with pairs, so starting at the second takeoff and looking at
    # the first...
    for ndx in range(1, len(flight_sheet)):
        previous = flight_sheet[ndx-1].getTimestamp()
        current = flight_sheet[ndx].getTimestamp()
        if ndx < len(flight_sheet)-1:
            nxt = flight_sheet[ndx+1].getTimestamp()
        else:
            nxt = Event.event_not_detected

        # are the current and previous takeoff within 30 seconds?
        if (previous - datetime.timedelta(seconds=30) <
                current <
                previous + datetime.timedelta(seconds=30)):
            # this is a takeoff pair
            print("%02d" % item_num,
                  "Launch ",
                  current,
                  "R%02d" % flight_sheet[ndx].getRwy(),
                  flight_sheet[ndx].getReg(),
                  flight_sheet[ndx-1].getReg()
                  )
            item_num += 1
        # the pair is not a match. what about the upcoming pair?
        elif nxt - datetime.timedelta(seconds=30) < current < nxt + datetime.timedelta(seconds=30):
            # do nothing. the next iteration of the loop will process the pair
            pass
        else:
            # this is a lone takeoff event
            print("%02d" % item_num,
                  "Takeoff", current,
                  "R%02d" % flight_sheet[ndx].getRwy(),
                  flight_sheet[ndx].getReg()
                  )
            item_num += 1

    return


# ============================================================================

#processNmeaStream()
eachAircraft()
