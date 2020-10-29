
import datetime
import pytz

from groundstation import Groundstation
from event import TakeoffEvent, LandingEvent


class Aircraft:

    # static datetime value used by class to indicate failure
    event_not_detected = pytz.utc.localize(datetime.datetime.min)

    @staticmethod
    def observation_period(): return 45

    @staticmethod
    def takeoff_rolling_low(): return 7

    @staticmethod
    def takeoff_rolling_high(): return 19

    @staticmethod
    def takeoff_climboutSpeedMin(): return 50

    @staticmethod
    def takeoff_climboutAltMin(): return +30

    @staticmethod
    def landing_final_speedMax(): return 16

    @staticmethod
    def landing_approachSpeedMin(): return 40

    @staticmethod
    def landing_approachAltMin(): return +30

    def __init__(self, reg):
        self.aircraftId = reg
        self.aircraftType = ''

        # observations are the senquentially ordered sequence of
        # positions reported by an aircraft.
        self.observations = []

        # occurences of importance detected by processing the observations.
        self.events = []

    def appendObservations(self, observation):
        self.observations.append(observation)

    def getObservations(self):
        return self.observations

    def getAircraftId(self):
        return self.aircraftId

    def getAircraftType(self):
        return self.aircraftType

    @staticmethod
    def trim(timeframeOfWindow, window):
        '''
        check the tail of a window of observations for observations beyond
        the expected timeframe. trim the window to just the expected
        timeframe.
        '''

        tStart = window[0].getTimestamp()
        tMax = tStart + datetime.timedelta(seconds=timeframeOfWindow)
        # print(tStart, tMax)

        # remove observations that are out of range
        for count in range(0, len(window)):
            # remove tail observation if beyond timeframe
            if tStart <= window[-1].getTimestamp() <= tMax:
                # don't look any further.
                break

            window.pop()

    @staticmethod
    def detectTrack(window):
        track = 0
        count = 0
        for obs in range(0, len(window)):
            if Groundstation.atGroundLevel(
                    window[obs].getAltitudeAGL() and
                    window[obs].speed.kph() > 10):

                # this won't work for North, where values are near 360 and 0

                track += window[obs].getTrack()
                count += 1

        # calculate the average
        track = int(track/count)

        # correct for known runways. This is Kars specific, for now.
        if 220 <= track <= 270:
            track = 260
        elif 60 <= track <= 100:
            track = 80

        return int(track)

    def detectTakeoff(self, window):

        if not len(window) > 0:
            return Aircraft.event_not_detected

        # takeoff inital rolling speed
        # when too slow, a towplane rolling-up to a glider
        # gets included! The heading of the towplane is wrong at that point,
        # which messes with runway calculation.

        initial_speed = window[0].speed.kph()
        initial_time = window[0].getTimestamp()
        rolling_low = Aircraft.takeoff_rolling_low()
        rolling_high = Aircraft.takeoff_rolling_high()
        if not rolling_low <= initial_speed <= rolling_high:
            return Aircraft.event_not_detected

        # climbout speed at least this
        final_speed = window[-1].speed.kph()
        if not final_speed >= Aircraft.takeoff_climboutSpeedMin():
            return Aircraft.event_not_detected

        # must be close to the ground initially
        takeoff_alt_agl = window[0].getAltitudeAGL()
        if not Groundstation.atGroundLevel(takeoff_alt_agl):
            return Aircraft.event_not_detected

        # must be at least this much higher during climbout
        final_alt_agl = window[-1].getAltitudeAGL()
        if not final_alt_agl >= takeoff_alt_agl + Aircraft.takeoff_climboutAltMin():
            return Aircraft.event_not_detected

        track = Aircraft.detectTrack(window)

        # speed stored as metres per second
        takeoff = TakeoffEvent(initial_time, 0, 0, takeoff_alt_agl,
                               track, window[0].speed)
        self.events.append(takeoff)

        return initial_time

    def detectLanding(self, window):

        if not len(window) > 0:
            return Aircraft.event_not_detected

        # ensure rollout speed
        final_speed = window[-1].speed
        final_time = window[-1].getTimestamp()
        if not final_speed.kph() <= Aircraft.landing_final_speedMax():
            return Aircraft.event_not_detected

        # ensure on the ground
        final_alt_agl = window[-1].getAltitudeAGL()
        if not Groundstation.atGroundLevel(final_alt_agl):
            return Aircraft.event_not_detected

        # ensure approaching at speed
        initial_speed = window[0].speed.kph()
        if not initial_speed >= Aircraft.landing_approachSpeedMin():
            return Aircraft.event_not_detected

        # ensure approaching from altitude
        takeoff_alt_agl = window[0].getAltitudeAGL()
        if not takeoff_alt_agl >= final_alt_agl + Aircraft.landing_approachAltMin():
            return Aircraft.event_not_detected

        track = Aircraft.detectTrack(window)

        # store speed in M/S
        landing = LandingEvent(final_time, 0, 0, final_alt_agl,
                               track, final_speed)
        self.events.append(landing)

        return final_time

    def detectEvents(self):

        takeoff_time = Aircraft.event_not_detected
        landing_time = Aircraft.event_not_detected


        # num of seconds of an observation period. The period is used
        # in determining flight events like takeoff and landing.
        observation_period = Aircraft.observation_period()


        n = len(self.getObservations())
        if n > 0: n -= 1  # correct for zero-based index

        # move through the list, one observation at a time
        for x in range(0, n):

            # create a smaller, look-ahead views of a limited timeframe.
            takeoff_observations = self.observations[x:x+observation_period]
            Aircraft.trim(observation_period, takeoff_observations)
            landing_observations = self.observations[x:x+observation_period]
            Aircraft.trim(observation_period, landing_observations)

            t1 = landing_observations[0].getTimestamp()

            # detect takeoff, but skip ahead if takeoff just detected
            if (takeoff_time + datetime.timedelta(seconds=observation_period) > t1 or
                landing_time + datetime.timedelta(seconds=observation_period) > t1):
                pass
            else:
                takeoff_time = self.detectTakeoff(takeoff_observations)
                landing_time = self.detectLanding(landing_observations)


    def reportEvents(self):
        n = 1
        tTakeoffTimestamp = Aircraft.event_not_detected
        tLandingTimestamp = Aircraft.event_not_detected
        tTotal = datetime.timedelta(seconds=0)

        for e in self.events:
            if isinstance(e, TakeoffEvent):
                tTakeoffTimestamp = e.getTimestamp()
                takeoffRwy = e.getRwy()
                takeoffAltAGL = e.getAltitudeAGL()
                takeoffSpeed = e.speed.kph()

            if isinstance(e, LandingEvent):
                tLandingTimestamp = e.getTimestamp()
                landingRwy = e.getRwy()
                landingAltAGL = e.getAltitudeAGL()
                landingSpeed = e.speed.kph()

                tDuration = tLandingTimestamp - tTakeoffTimestamp
                tTotal += tDuration

                if tLandingTimestamp < tTakeoffTimestamp + datetime.timedelta(hours=16):
                    print(
                        "%2d " % n,
                        "%s" % str(tTakeoffTimestamp.astimezone(Groundstation.timezone())),
                        " R%02d" % takeoffRwy,
                        " %+3dagl" % takeoffAltAGL,
                        " %3dkph" % takeoffSpeed,
                        "%6s" % " ==>> ",
                        "%s" % str(tLandingTimestamp.astimezone(Groundstation.timezone())),
                        " R%02d" % landingRwy,
                        " %+3dagl" % landingAltAGL,
                        " %3dkph " % landingSpeed,
                        tDuration,
                        sep='')
                    n += 1
                    # print("Takeoff", tTakeoff, "Landing", tLanding, "Duration:", tDuration)
                else:
                    print("Landing", tLandingTimestamp)

        print("%104s" % "======= ")
        print("%95s" % " ",
              tTotal)

    def printObservations(self):

        for obs in self.getObservations():
            obs.printt()

    def getMaxDistance(self):
        maxDistance = 0
        observations = self.getObservations()
        for s in observations:
            distance = s.getDistance()
            if distance > maxDistance:
                maxDistance = distance
                altitudeAGL = s.getAltitudeAGL()
        return maxDistance, altitudeAGL
