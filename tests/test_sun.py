"""Tests for the solar position engine."""

import datetime as dt

import pytest

from moonfield import sun
from moonfield import time as mtime


class TestAgainstTextbook:
    """Meeus example 25.a: 1992 October 13 at 0h TD, JD 2448908.5."""

    JD = 2448908.5

    def test_apparent_longitude(self):
        assert sun.position(self.JD).apparent_longitude == pytest.approx(
            199.90895, abs=1e-3
        )

    def test_right_ascension(self):
        assert sun.position(self.JD).right_ascension == pytest.approx(
            198.38083, abs=1e-3
        )

    def test_declination(self):
        assert sun.position(self.JD).declination == pytest.approx(-7.78507, abs=1e-3)

    def test_radius_vector(self):
        assert sun.position(self.JD).distance_au == pytest.approx(0.99766, abs=1e-4)


class TestDeclination:
    def test_stays_within_the_tropics(self):
        """The Sun is never overhead outside +/- 23.44 degrees."""
        for day in range(0, 366, 5):
            when = dt.datetime(2026, 1, 1, tzinfo=mtime.UTC) + dt.timedelta(days=day)
            assert -23.45 <= sun.declination(when) <= 23.45

    def test_maximum_near_june_solstice(self):
        june = sun.declination(dt.datetime(2026, 6, 21, 12, tzinfo=mtime.UTC))
        assert june == pytest.approx(23.44, abs=0.05)

    def test_minimum_near_december_solstice(self):
        december = sun.declination(dt.datetime(2026, 12, 21, 12, tzinfo=mtime.UTC))
        assert december == pytest.approx(-23.44, abs=0.05)

    def test_near_zero_at_equinoxes(self):
        march = sun.declination(dt.datetime(2026, 3, 20, 14, tzinfo=mtime.UTC))
        september = sun.declination(dt.datetime(2026, 9, 23, 1, tzinfo=mtime.UTC))
        assert abs(march) < 0.5 and abs(september) < 0.5


class TestDistance:
    def test_perihelion_is_in_early_january(self):
        """Earth is CLOSEST to the Sun in January -- the seasons are not distance."""
        days = [dt.datetime(2026, 1, 1, tzinfo=mtime.UTC) + dt.timedelta(days=d)
                for d in range(0, 365, 5)]
        closest = min(days, key=lambda d: sun.position(d).distance_au)
        assert closest.month == 1

    def test_aphelion_is_in_early_july(self):
        days = [dt.datetime(2026, 1, 1, tzinfo=mtime.UTC) + dt.timedelta(days=d)
                for d in range(0, 365, 5)]
        farthest = max(days, key=lambda d: sun.position(d).distance_au)
        assert farthest.month == 7

    def test_distance_varies_only_a_few_percent(self):
        values = [
            sun.position(dt.datetime(2026, 1, 1, tzinfo=mtime.UTC) + dt.timedelta(days=d)).distance_au
            for d in range(0, 365, 10)
        ]
        assert (max(values) - min(values)) / min(values) < 0.04

    def test_angular_diameter_is_about_half_a_degree(self):
        size = sun.position(dt.datetime(2026, 4, 1, tzinfo=mtime.UTC)).angular_diameter
        assert 0.52 < size < 0.55


class TestEquationOfTime:
    def test_stays_within_about_17_minutes(self):
        for day in range(0, 366, 3):
            when = dt.datetime(2026, 1, 1, tzinfo=mtime.UTC) + dt.timedelta(days=day)
            assert abs(sun.equation_of_time(when)) < 17.0

    def test_has_four_zero_crossings_a_year(self):
        values = [
            sun.equation_of_time(dt.datetime(2026, 1, 1, tzinfo=mtime.UTC) + dt.timedelta(days=d))
            for d in range(366)
        ]
        crossings = sum(
            1 for a, b in zip(values, values[1:], strict=False) if (a < 0) != (b < 0)
        )
        assert crossings == 4

    def test_early_november_is_the_big_positive_peak(self):
        peak = max(
            (dt.datetime(2026, 1, 1, tzinfo=mtime.UTC) + dt.timedelta(days=d) for d in range(365)),
            key=sun.equation_of_time,
        )
        assert peak.month == 11
