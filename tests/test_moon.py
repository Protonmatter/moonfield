"""Tests for the lunar position engine."""

import datetime as dt

import pytest

from moonfield import moon
from moonfield import time as mtime


class TestAgainstTextbook:
    """Meeus example 47.a: 1992 April 12 at 0h TD, JD 2448724.5.

    The tolerances are loose on purpose. We deliberately truncated the series,
    and these tests document how much that costs us: a couple of arcseconds in
    position and about 15 km in distance.
    """

    JD = 2448724.5

    def test_longitude(self):
        assert moon.position(self.JD).ecliptic_longitude == pytest.approx(
            133.167265, abs=0.002
        )

    def test_latitude(self):
        assert moon.position(self.JD).ecliptic_latitude == pytest.approx(
            -3.229126, abs=0.002
        )

    def test_distance(self):
        assert moon.position(self.JD).distance_km == pytest.approx(368409.7, abs=50)

    def test_parallax(self):
        assert moon.position(self.JD).parallax == pytest.approx(0.991990, abs=0.001)


class TestOrbit:
    def test_distance_stays_in_the_known_range(self):
        """Perigee is about 356,500 km, apogee about 406,700 km."""
        for day in range(0, 400, 2):
            when = dt.datetime(2026, 1, 1, tzinfo=mtime.UTC) + dt.timedelta(days=day)
            distance = moon.position(when).distance_km
            assert 355_000 < distance < 408_000

    def test_latitude_stays_within_orbital_inclination(self):
        """The Moon's orbit is tilted about 5.1 degrees to the ecliptic."""
        for day in range(0, 400, 2):
            when = dt.datetime(2026, 1, 1, tzinfo=mtime.UTC) + dt.timedelta(days=day)
            assert abs(moon.position(when).ecliptic_latitude) < 5.5

    def test_completes_a_sidereal_circuit_in_about_27_3_days(self):
        start = dt.datetime(2026, 3, 1, tzinfo=mtime.UTC)
        start_lon = moon.ecliptic_longitude(start)
        for hours in range(int(26 * 24), int(29 * 24)):
            when = start + dt.timedelta(hours=hours)
            if abs(((moon.ecliptic_longitude(when) - start_lon + 180) % 360) - 180) < 0.3:
                period = hours / 24.0
                assert period == pytest.approx(mtime.SIDEREAL_MONTH, abs=0.6)
                return
        pytest.fail("the Moon never came back around")

    def test_moves_about_13_degrees_a_day(self):
        when = dt.datetime(2026, 5, 5, tzinfo=mtime.UTC)
        step = (
            moon.ecliptic_longitude(when + dt.timedelta(days=1))
            - moon.ecliptic_longitude(when)
        ) % 360.0
        assert 11.0 < step < 15.5

    def test_angular_size_is_about_half_a_degree(self):
        size = moon.position(dt.datetime(2026, 4, 1, tzinfo=mtime.UTC)).angular_diameter
        assert 0.48 < size < 0.57

    def test_apparent_size_matches_the_suns_closely(self):
        """The coincidence that makes total solar eclipses possible."""
        from moonfield import sun

        when = dt.datetime(2026, 6, 1, tzinfo=mtime.UTC)
        ratio = (
            moon.position(when).angular_diameter / sun.position(when).angular_diameter
        )
        assert 0.9 < ratio < 1.1
