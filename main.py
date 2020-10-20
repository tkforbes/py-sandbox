#!/usr/bin/python3
import pynmea2
import geopy
import geopy.distance

from groundstation import Groundstation
from pflaa import Pflaa
from ognRegistrations import OgnRegistration

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

    #print(aircraftSeen['C-GDQK'].getAircraftId())
    #print(len(aircraftSeen['C-GDQK'].getSentences()))
    #print(aircraftSeen['C-GDQK'].getSentences())

    print("%s" % list(aircraftSeen.keys()))

    groundstation.report()

    print("")
    print("REPORT FLIGHTS")
    print("==============")
    for ac in list(aircraftSeen.keys()):
        print("")
        print(ac)
        aircraftSeen[ac].reportFlights()
        aircraftSeen[ac].reportEvents()

    # for ac in list(aircraftSeen.keys()):
    #     print("")
    #     print(ac)
    #     aircraftSeen[ac].printObservations()
    #     distance, altAGL = aircraftSeen[ac].getMaxDistance()
    #     print("max dist: %5dm" % distance,
    #             "@%dm AGL" % altAGL)

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
