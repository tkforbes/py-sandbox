
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
    def takeoff_rolling_limits():
        min = 7
        max = 19
        return min, max

    @staticmethod
    def climbout_speed_min(): return 50

    @staticmethod
    def climbout_alt_min(): return +30

    @staticmethod
    def rolling_speed_max(): return 16

    @staticmethod
    def approach_speed_min(): return 40

    @staticmethod
    def approach_alt_min(): return +30

    def __init__(self, reg):
        self.aircraft_id = reg
        self.aircraft_type = ''

        # observations are the senquentially ordered sequence of
        # positions reported by an aircraft.
        self.observations = []

        # occurences of importance detected by processing the observations.
        self.events = []

    def append_observations(self, observation):
        self.observations.append(observation)

    def get_observations(self):
        return self.observations

    def get_aircraft_id(self):
        return self.aircraft_id

    def get_aircraft_type(self):
        return self.aircraft_type

    @staticmethod
    def trim(timeframe_of_window, window):
        '''
        check the tail of a window of observations for any beyond
        the expected timeframe. trim the window to just the expected
        timeframe.
        '''

        time_start = window[0].get_timestamp()
        time_max = time_start + datetime.timedelta(seconds=timeframe_of_window)

        # remove observations that are out of range
        for count in range(0, len(window)):
            if window[-1].get_timestamp() > time_max:
                # tail observation not withing timeframe. remove.
                window.pop()
            else:
                # when the tail observation is within the timeframe,
                # don't waste more time looping because the remainder
                # are also within the timeframe.
                break

    @staticmethod
    def detect_track(window):
        track = 0
        count = 0

        for ndx, observation in enumerate(window):
            if Groundstation.at_groundlevel(
                    observation.get_alt_agl() and
                    observation.speed.kph() > 10):

                # this won't work for North, where values are near 360 and 0

                track += observation.get_track()
                count += 1

        # calculate the average
        track = int(track/count)

        # correct for known runways. This is Kars specific, for now.
        if 220 <= track <= 270:
            track = 260
        elif 60 <= track <= 100:
            track = 80

        return int(track)

    def detect_takeoff(self, window):

        if not window:
            return Aircraft.event_not_detected

        # takeoff inital rolling speed
        # when too slow, a towplane rolling-up to a glider
        # gets included! The heading of the towplane is wrong at that point,
        # which messes with runway calculation.

        rolling = window[0]
        # rolling_low = Aircraft.takeoff_rolling_min()
        # rolling_high = Aircraft.takeoff_rolling_max()
        lower_limit, higher_limit = Aircraft.takeoff_rolling_limits()
        if not lower_limit <= rolling.speed.kph() <= higher_limit:
            return Aircraft.event_not_detected

        climbout = window[-1]

        # climbout speed at least this
        if not climbout.speed.kph() >= Aircraft.climbout_speed_min():
            return Aircraft.event_not_detected

        # must be close to the ground initially
        if not Groundstation.at_groundlevel(rolling.get_alt_agl()):
            return Aircraft.event_not_detected

        # must be at least this much higher during climbout
        if not climbout.get_alt_agl() >= rolling.get_alt_agl() + Aircraft.climbout_alt_min():
            return Aircraft.event_not_detected

        track = Aircraft.detect_track(window)

        takeoff = TakeoffEvent(rolling.get_timestamp(), rolling.lat, rolling.lon,
                               rolling.get_alt_agl(), track, rolling.speed)
        self.events.append(takeoff)

        return rolling.get_timestamp()

    def detect_landing(self, window):

        if not window:
            return Aircraft.event_not_detected

        rollout = window[-1]

        # ensure rollout speed
        if not rollout.speed.kph() <= Aircraft.rolling_speed_max():
            return Aircraft.event_not_detected

        # ensure on the ground
        if not Groundstation.at_groundlevel(rollout.get_alt_agl()):
            return Aircraft.event_not_detected

        approach = window[0]

        # ensure approaching at speed
        if not approach.speed.kph() >= Aircraft.approach_speed_min():
            return Aircraft.event_not_detected

        # ensure approaching from altitude
        if not approach.get_alt_agl() >= rollout.get_alt_agl() + Aircraft.approach_alt_min():
            return Aircraft.event_not_detected

        track = Aircraft.detect_track(window)

        landing = LandingEvent(rollout.get_timestamp(), rollout.lat, rollout.lon,
                               rollout.get_alt_agl(), track, rollout.speed)
        self.events.append(landing)

        return rollout.get_timestamp()

    def detect_events(self):

        takeoff_time = Aircraft.event_not_detected
        landing_time = Aircraft.event_not_detected

        observation_period = Aircraft.observation_period()

        # move through the list, one observation at a time
        for count in range(0, len(self.get_observations())):

            of_interest = slice(count, count + observation_period)

            # slice an observation window giving the maximum possible view
            # of interest for takeoff
            takeoff_observations = self.observations[of_interest]

            # now trim the window of observations to discard out-of-range
            # values from the tail
            Aircraft.trim(observation_period, takeoff_observations)

            # slice an observation window giving the maximum possible view
            # of interest for landing
            landing_observations = self.observations[of_interest]

            # now trim the window of observations to discard out-of-range
            # values from the tail
            Aircraft.trim(observation_period, landing_observations)

            t1 = landing_observations[0].get_timestamp()

            # detect takeoff, but skip ahead if takeoff just detected
            if (takeoff_time + datetime.timedelta(seconds=observation_period) > t1 or
                    landing_time + datetime.timedelta(seconds=observation_period) > t1):
                pass
            else:
                takeoff_time = self.detect_takeoff(takeoff_observations)
                landing_time = self.detect_landing(landing_observations)


    def report_events(self):

        takeoff_time = Aircraft.event_not_detected
        landing_time = Aircraft.event_not_detected
        total_duration = datetime.timedelta(seconds=0)

        for count, event in enumerate(self.events):
            if isinstance(event, TakeoffEvent):
                takeoff_time = event.getTimestamp()
                takeoff_rwy = event.getRwy()
                takeoff_alt_agl = event.getAltitudeAGL()
                takeoff_speed = event.speed

            if isinstance(event, LandingEvent):
                landing_time = event.getTimestamp()
                landing_rwy = event.getRwy()
                landing_alt_agl = event.getAltitudeAGL()
                landing_speed = event.speed

                duration = landing_time - takeoff_time
                total_duration += duration

                if landing_time < takeoff_time + datetime.timedelta(hours=16):
                    print(
                        "%2d " % count,
                        "%s" % str(takeoff_time.astimezone(Groundstation.timezone())),
                        " R%02d" % takeoff_rwy,
                        " %+3dagl" % takeoff_alt_agl,
                        " %3dkph" % takeoff_speed.kph(),
                        "%6s" % " ==>> ",
                        "%s" % str(landing_time.astimezone(Groundstation.timezone())),
                        " R%02d" % landing_rwy,
                        " %+3dagl" % landing_alt_agl,
                        " %3dkph " % landing_speed.kph(),
                        duration,
                        sep='')
                else:
                    print("Landing", landing_time)

        print("%104s" % "======= ")
        print("%95s" % " ",
              total_duration)

    def print_observations(self):

        for obs in self.get_observations():
            obs.printt()

    def get_max_distance(self):

        distance_max = 0
        observations = self.get_observations()
        for observation in observations:
            distance = observation.get_distance()
            if distance > distance_max:
                distance_max = distance
                altitude_agl = observation.getAltitudeAGL()
        return distance_max, altitude_agl
