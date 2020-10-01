#!/usr/bin/python3
import pynmea2

from airfield import Airfield
from flarmProximateAircraft import FlarmProximateAircraft
from ognRegistrations import OgnRegistration
from flarmPriorityIntruder import FlarmPriorityIntruder

r = OgnRegistration ()
print(r.getAircraft('r'))

airfield = Airfield(81, 45.062101, 075.374431)
proximateAircraft = FlarmProximateAircraft()
priorityIntruder = FlarmPriorityIntruder()


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
        msg = pynmea2.parse(line)
    except pynmea2.ChecksumError:
        # ignore sentences that produce a checksum error
        continue
    except pynmea2.ParseError:
        # ignore sentences that can't be parsed
        continue
    # except:
    #     # ignore sentences that raise any other error
    #     continue

    #print(repr(msg))

    #print(type(msg))

    # don't do anything with Flarm sentences until the airfield
    # has a valid datestamp.
    if (isinstance(msg, pynmea2.nmea.ProprietarySentence) and
            airfield.validDatestamp()):
        if msg.manufacturer == "FLA":
            # this is a Flarm sentence. try to set it.
            if proximateAircraft.set(airfield.timestamp, msg):
                proximateAircraft.printt()
            elif priorityIntruder.set(airfield.timestamp, msg):
                priorityIntruder.printt(airfield)

    elif msg.sentence_type == 'RMC':
        # this sentence contains the current date

        # update the date in the airfield. the date is very important!
        airfield.setDatestamp(msg.datestamp)
        airfield.setCourseTrue(msg.true_course)
        #print("course true:", msg.true_course)
    elif msg.sentence_type == 'GGA' and airfield.validDatestamp():
        # this sentence has the airfield timestamp, lat, lon, elevation
        airfield.set(msg)


airfield.report()
proximateAircraft.report()
priorityIntruder.report()
