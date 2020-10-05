#!/usr/bin/python3
import pynmea2

from airfield import Airfield
from flarmProximateAircraft import FlarmProximateAircraft
from ognRegistrations import OgnRegistration
from flarmPriorityIntruder import FlarmPriorityIntruder

airfield = Airfield(81, 45.062101, 075.374431)
proximateAircraft = FlarmProximateAircraft()
priorityIntruder = FlarmPriorityIntruder()

def eachAircraft():

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

        # don't do anything with Flarm sentences until the airfield
        # has a valid datestamp.
        if (isinstance(sentence, pynmea2.nmea.ProprietarySentence) and
                airfield.validDatestamp()):
            if sentence.manufacturer == "FLA":
                # this is a Flarm sentence. try to set it.

                proximateAircraft = FlarmProximateAircraft()
                priorityIntruder = FlarmPriorityIntruder()
                if proximateAircraft.set(airfield.timestamp, sentence):
                    aircraftId = proximateAircraft.getAircraftId()
                    if not (aircraftId in aircraftSeen):
                        aircraftSeen[aircraftId] = Aircraft(aircraftId)
                    aircraftSeen[aircraftId].append(proximateAircraft)
                elif priorityIntruder.set(airfield.timestamp, sentence):
                    aircraftId = priorityIntruder.getAircraftId()
                    if not (aircraftId in aircraftSeen):
                        aircraftSeen[aircraftId] = Aircraft(aircraftId)
                    aircraftSeen[aircraftId].append(priorityIntruder)

        elif sentence.sentence_type == 'RMC':
            # this sentence contains the current date

            # update the date in the airfield. the date is very important!
            airfield.setDatestamp(sentence.datestamp)
            airfield.setCourseTrue(sentence.true_course)
            #print("course true:", sentence.true_course)
        elif (sentence.sentence_type == 'GGA'
                and airfield.validDatestamp()
                and commas == 14):

            # this sentence has the airfield timestamp, lat, lon, elevation
            airfield.set(sentence)

    #print(aircraftSeen['C-GDQK'].getAircraftId())
    #print(len(aircraftSeen['C-GDQK'].getSentences()))
    #print(aircraftSeen['C-GDQK'].getSentences())

    print("%s" % list(aircraftSeen.keys()))

    airfield.report()

    for ac in list(aircraftSeen.keys()):
        print("")
        print(ac)
        sentences = aircraftSeen[ac].getSentences()
        for s in sentences:
            if (s.getSource() == 'PFLAU'):
                s.printt(airfield)
            elif (s.getSource() == "PFLAA"):
                s.printt()

def processNmeaStream():

    aircraftSeen = {
    }

    from aircraft import Aircraft

    #answer = FlarmPriorityIntruder.sixteenWindCompassPoint(1)
    #print("bearing: ", bearing, "ans:", answer)

    # def is_integer(n):
    #     try:
    #         int(n)
    #         return True
    #     except ValueError:
    #         return False

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

        # don't do anything with Flarm sentences until the airfield
        # has a valid datestamp.
        if (isinstance(sentence, pynmea2.nmea.ProprietarySentence) and
                airfield.validDatestamp()):
            if sentence.manufacturer == "FLA":
                # this is a Flarm sentence. try to set it.

                if proximateAircraft.set(airfield.timestamp, sentence):
                    aircraftId = proximateAircraft.getAircraftId()
                    if not (aircraftId in aircraftSeen):
                        aircraftSeen[aircraftId] = Aircraft(aircraftId)
                    aircraftSeen[aircraftId].append(sentence)
                    proximateAircraft.printt()
                elif priorityIntruder.set(airfield.timestamp, sentence):
                    aircraftId = priorityIntruder.getAircraftId()
                    if not (aircraftId in aircraftSeen):
                        aircraftSeen[aircraftId] = Aircraft(aircraftId)
                    aircraftSeen[aircraftId].append(sentence)
                    priorityIntruder.printt(airfield)


        elif sentence.sentence_type == 'RMC':
            # this sentence contains the current date

            # update the date in the airfield. the date is very important!
            airfield.setDatestamp(sentence.datestamp)
            airfield.setCourseTrue(sentence.true_course)
            #print("course true:", sentence.true_course)
        elif (sentence.sentence_type == 'GGA'
            and airfield.validDatestamp()):
            #and line.count(',') == 14):
            # this sentence has the airfield timestamp, lat, lon, elevation
#            print('comma count:', line.count(','))
            print("found^^")
            airfield.set(sentence)

    #print(aircraftSeen['C-GDQK'].getAircraftId())
    #print(len(aircraftSeen['C-GDQK'].getSentences()))
    #print(aircraftSeen['C-GDQK'].getSentences())

    airfield.report()
    proximateAircraft.report()
    priorityIntruder.report()

# ============================================================================

#processNmeaStream()
eachAircraft()
