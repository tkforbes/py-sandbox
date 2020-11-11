#!/usr/bin/python3
import datetime
import pynmea2

import sqlite3

from groundstation import Groundstation
from observation import Observation

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

    return


# ============================================================================

#processNmeaStream()
eachAircraft()
