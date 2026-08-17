"""Tests for horizontal coordinates and rise/set times.

Several of these check a physical identity rather than a stored number, which
is the more valuable kind of test: it would still be right if we replaced the
whole algorithm.
"""

import datetime as dt

import pytest

from moonfield import observer, sun
from moonfield import time as mtime
from moonfield.location import Location

UTC = mtime.UTC

GREENWICH = Location(51.4779, -0.0015, "Greenwich", "Europe/London")
SYDNEY = Location(-33.8688, 151.2093, "Sydney", "Australia/Sydney")
QUITO = Location(-0.1807, -78.4678, "Quito", "America/Guayaquil")
LONGYEARBYEN = Location(78.2232, 15.6267, "Longyearbyen", "Arctic/Longyearbyen")
MCMURDO = Location(-77.8419, 166.6863, "McMurdo", "Antarctica/McMurdo")


class TestCardinalPoints:
    @pytest.mark.parametrize(
        "azimuth, expected",
        [(0, "N"), (45, "NE"), (90, "E"), (135, "SE"),
         (180, "S"), (225, "SW"), (270, "W"), (315, "NW"), (360, "N")],
    )
    def test_compass_names(self, azimuth, expected):
        assert observer.cardinal(azimuth) == expected

    def test_wraps_past_a_full_circle(self):
        assert observer.cardinal(370) == observer.cardinal(10)


class TestNoonAltitude:
    """At local solar noon: altitude = 90 - |latitude - declination|."""

    @pytest.mark.parametrize("place", [GREENWICH, SYDNEY, QUITO])
    @pytest.mark.parametrize("month", [3, 6, 9, 12])
    def test_matches_the_identity(self, place, month):
        when = dt.datetime(2026, month, 15, 12, tzinfo=UTC)
        result = observer.sun_rise_set(place, when)
        if result.transit is None:
            pytest.skip("no transit at this latitude and date")
        declination = sun.declination(result.transit)
        expected = 90 - abs(place.latitude - declination)
        assert result.transit_altitude == pytest.approx(expected, abs=0.6)


class TestEquinoxSunrise:
    """At an equinox the Sun rises very close to due east, everywhere."""

    @pytest.mark.parametrize("place", [GREENWICH, SYDNEY, QUITO])
    def test_rises_near_due_east(self, place):
        when = dt.datetime(2026, 3, 20, 12, tzinfo=UTC)
        result = observer.sun_rise_set(place, when)
        azimuth = observer.sun_position(place, result.rise).azimuth
        assert abs(azimuth - 90) < 2.5

    @pytest.mark.parametrize("place", [GREENWICH, SYDNEY, QUITO])
    def test_sets_near_due_west(self, place):
        when = dt.datetime(2026, 3, 20, 12, tzinfo=UTC)
        result = observer.sun_rise_set(place, when)
        azimuth = observer.sun_position(place, result.setting).azimuth
        assert abs(azimuth - 270) < 2.5


class TestDayLength:
    def test_equator_is_always_about_twelve_hours(self):
        for month in (1, 4, 7, 10):
            result = observer.sun_rise_set(QUITO, dt.datetime(2026, month, 15, 12, tzinfo=UTC))
            hours = (result.setting - result.rise).total_seconds() / 3600
            assert 11.8 < hours < 12.4

    def test_hemispheres_are_opposite_in_june(self):
        when = dt.datetime(2026, 6, 21, 12, tzinfo=UTC)
        north = observer.sun_rise_set(GREENWICH, when)
        south = observer.sun_rise_set(SYDNEY, when)
        north_hours = (north.setting - north.rise).total_seconds() / 3600
        south_hours = (south.setting - south.rise).total_seconds() / 3600
        assert north_hours > 16 and south_hours < 10

    def test_hemispheres_swap_in_december(self):
        when = dt.datetime(2026, 12, 21, 12, tzinfo=UTC)
        north = observer.sun_rise_set(GREENWICH, when)
        south = observer.sun_rise_set(SYDNEY, when)
        north_hours = (north.setting - north.rise).total_seconds() / 3600
        south_hours = (south.setting - south.rise).total_seconds() / 3600
        assert north_hours < 9 and south_hours > 14


class TestPolarRegions:
    def test_midnight_sun_in_the_arctic_in_june(self):
        result = observer.sun_rise_set(LONGYEARBYEN, dt.datetime(2026, 6, 21, 12, tzinfo=UTC))
        assert result.always_up and result.note == "never sets today at this latitude"

    def test_polar_night_in_the_arctic_in_december(self):
        result = observer.sun_rise_set(LONGYEARBYEN, dt.datetime(2026, 12, 21, 12, tzinfo=UTC))
        assert result.never_up

    def test_antarctic_is_the_mirror_image(self):
        june = observer.sun_rise_set(MCMURDO, dt.datetime(2026, 6, 21, 12, tzinfo=UTC))
        december = observer.sun_rise_set(MCMURDO, dt.datetime(2026, 12, 21, 12, tzinfo=UTC))
        assert june.never_up and december.always_up


class TestKnownRiseSetTimes:
    """Greenwich on the June 2026 solstice: published times are 04:43 / 21:22 BST."""

    def test_sunrise(self):
        result = observer.sun_rise_set(GREENWICH, dt.datetime(2026, 6, 21, 12, tzinfo=UTC))
        local = result.rise.astimezone(GREENWICH.zone)
        minutes = local.hour * 60 + local.minute
        assert abs(minutes - (4 * 60 + 43)) <= 3

    def test_sunset(self):
        result = observer.sun_rise_set(GREENWICH, dt.datetime(2026, 6, 21, 12, tzinfo=UTC))
        local = result.setting.astimezone(GREENWICH.zone)
        minutes = local.hour * 60 + local.minute
        assert abs(minutes - (21 * 60 + 22)) <= 3


class TestHorizontalConversion:
    def test_altitude_never_leaves_its_range(self):
        for hour in range(0, 24):
            when = dt.datetime(2026, 5, 1, hour, tzinfo=UTC)
            for place in (GREENWICH, SYDNEY, QUITO):
                assert -90 <= observer.sun_position(place, when).altitude <= 90

    def test_azimuth_stays_in_a_full_circle(self):
        for hour in range(0, 24):
            when = dt.datetime(2026, 5, 1, hour, tzinfo=UTC)
            assert 0 <= observer.sun_position(GREENWICH, when).azimuth < 360

    def test_sun_is_due_south_at_noon_in_the_north(self):
        result = observer.sun_rise_set(GREENWICH, dt.datetime(2026, 5, 1, 12, tzinfo=UTC))
        azimuth = observer.sun_position(GREENWICH, result.transit).azimuth
        assert abs(azimuth - 180) < 1.0

    def test_sun_is_due_north_at_noon_in_the_south(self):
        result = observer.sun_rise_set(SYDNEY, dt.datetime(2026, 5, 1, 12, tzinfo=UTC))
        azimuth = observer.sun_position(SYDNEY, result.transit).azimuth % 360
        assert min(azimuth, 360 - azimuth) < 1.0

    def test_hour_angle_is_near_zero_at_transit(self):
        result = observer.sun_rise_set(GREENWICH, dt.datetime(2026, 5, 1, 12, tzinfo=UTC))
        assert abs(observer.sun_position(GREENWICH, result.transit).hour_angle) < 0.3


class TestRefraction:
    def test_is_about_half_a_degree_at_the_horizon(self):
        assert 0.45 < observer.refraction(0.0) < 0.65

    def test_shrinks_with_altitude(self):
        assert observer.refraction(45) < observer.refraction(10) < observer.refraction(0)

    def test_is_tiny_overhead(self):
        assert observer.refraction(90) < 0.02


class TestAngularSeparation:
    def test_same_direction_is_zero(self):
        assert observer.angular_separation(120, 30, 120, 30) == pytest.approx(0, abs=1e-6)

    def test_zenith_to_horizon_is_ninety(self):
        assert observer.angular_separation(0, 90, 180, 0) == pytest.approx(90, abs=1e-6)

    def test_opposite_horizons_are_one_eighty(self):
        assert observer.angular_separation(0, 0, 180, 0) == pytest.approx(180, abs=1e-6)

    def test_is_symmetric(self):
        a = observer.angular_separation(30, 20, 200, 55)
        b = observer.angular_separation(200, 55, 30, 20)
        assert a == pytest.approx(b)


class TestMoonRiseSet:
    """The daily retardation of moonrise, and why it is not a constant.

    "The Moon rises about 50 minutes later each day" is true *on average over a
    month*. On any given night it can be as little as 12 minutes or as much as
    90, because what matters is the angle the Moon's path makes with the
    horizon, and that angle swings through the month.

    When the path lies almost flat along the horizon, the Moon's eastward
    motion barely delays its rise -- successive moonrises bunch together. In the
    northern autumn that happens to coincide with the full Moon, giving several
    evenings of bright moonlight right after sunset. That is the Harvest Moon,
    and it is a geometry effect, not a change in the Moon itself.

    A test that sampled only a week could easily have "caught" this as a bug.
    """

    def _retardations(self, place, year=2026, month=5):
        gaps = []
        previous = None
        for day in range(1, 32):
            when = dt.datetime(year, month, day, 12, tzinfo=UTC)
            result = observer.moon_rise_set(place, when)
            if result.rise is None:
                continue
            if previous is not None:
                gap = (result.rise - previous).total_seconds() / 60 - 24 * 60
                if 0 < gap < 200:  # skip the days with no moonrise at all
                    gaps.append(gap)
            previous = result.rise
        return gaps

    def test_monthly_average_is_about_fifty_minutes(self):
        gaps = self._retardations(GREENWICH)
        assert len(gaps) > 20, "expected most days of the month to have a moonrise"
        average = sum(gaps) / len(gaps)
        assert 45 < average < 58, f"average shift was {average:.0f} minutes"

    def test_average_is_the_same_at_the_equator(self):
        """The monthly average is set by the orbit, not by your latitude."""
        average = sum(self._retardations(QUITO)) / len(self._retardations(QUITO))
        assert 45 < average < 58

    def test_night_to_night_variation_is_large_at_high_latitude(self):
        """This is the Harvest Moon effect showing up in the numbers."""
        gaps = self._retardations(GREENWICH)
        assert max(gaps) - min(gaps) > 40, "expected a wide spread at 51 degrees north"

    def test_variation_is_much_smaller_near_the_equator(self):
        """Near the equator the ecliptic never lies flat along the horizon."""
        greenwich_spread = max(self._retardations(GREENWICH)) - min(self._retardations(GREENWICH))
        quito_spread = max(self._retardations(QUITO)) - min(self._retardations(QUITO))
        assert quito_spread < greenwich_spread

    def test_parallax_lowers_the_moon(self):
        """Being on the surface rather than at Earth's centre pushes the Moon down."""
        from moonfield import moon as moon_engine

        when = dt.datetime(2026, 5, 10, 22, tzinfo=UTC)
        jd = mtime.julian_day(when)
        pos = moon_engine.position(jd)
        geocentric = observer.to_horizontal(
            pos.right_ascension, pos.declination, GREENWICH, jd
        )
        topocentric = observer.moon_position(GREENWICH, jd)
        assert topocentric.altitude < geocentric.altitude
        assert geocentric.altitude - topocentric.altitude < 1.1


class TestRiseSetDescribe:
    """describe() must stay honest at the latitudes where the usual shape of
    answer stops applying."""

    def test_describes_a_normal_day(self, greenwich):
        when = dt.datetime(2026, 6, 21, tzinfo=mtime.UTC)
        text = observer.sun_rise_set(greenwich, when).describe(greenwich.zone)
        assert "rises" in text.lower()
        assert "sets" in text.lower()
        assert text.endswith(".")

    def test_midnight_sun_is_not_reported_as_missing_data(self):
        arctic = Location(78.22, 15.65, "Longyearbyen", "Arctic/Longyearbyen")
        when = dt.datetime(2026, 6, 21, tzinfo=mtime.UTC)
        text = observer.sun_rise_set(arctic, when).describe(arctic.zone)
        assert "up all day" in text.lower()
        assert "rises" not in text.lower()

    def test_polar_night_is_not_reported_as_missing_data(self):
        arctic = Location(78.22, 15.65, "Longyearbyen", "Arctic/Longyearbyen")
        when = dt.datetime(2026, 12, 21, tzinfo=mtime.UTC)
        text = observer.sun_rise_set(arctic, when).describe(arctic.zone)
        assert "down all day" in text.lower()

    def test_partial_day_omits_the_event_that_did_not_happen(self):
        """The Moon often rises without setting on the same calendar day.
        That is a real result, so describe() should simply say less."""
        ushuaia = Location(-54.80, -68.30, "Ushuaia", "America/Argentina/Ushuaia")
        when = dt.datetime(2026, 6, 21, tzinfo=mtime.UTC)
        result = observer.moon_rise_set(ushuaia, when)
        text = result.describe(ushuaia.zone)
        if result.setting is None and result.rise is not None:
            assert "rises" in text.lower()
            assert "sets" not in text.lower()

    def test_uses_the_requested_zone(self, greenwich):
        when = dt.datetime(2026, 6, 21, tzinfo=mtime.UTC)
        result = observer.sun_rise_set(greenwich, when)
        london = result.describe("Europe/London")
        tokyo = result.describe("Asia/Tokyo")
        assert london != tokyo
