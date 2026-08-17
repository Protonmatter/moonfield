"""The accuracy table in the README must be measured, not remembered.

A project that tells you to check your model against reality cannot publish an
accuracy claim nobody checks. Each test here measures one row of that table
against the reference it names, and asserts the error is no worse than the
figure printed for readers.

The assertions are one-sided on purpose. Getting *better* than the table says
is not a failure, it is a reason to update the table -- so each test also
records what it actually measured, visible with ``pytest -q -s``.

Where the reference values come from
------------------------------------
* Meeus, *Astronomical Algorithms*, worked examples 25.b and 47.a. These are
  printed in the book with more digits than we need, which is what makes them
  useful as a fixed target.
* Published new Moon times for 2026, the same three quoted in
  ``docs/02-moon-phases/calculating-phase.md``.
* Published sunrise and sunset for Greenwich on the June 2026 solstice.
"""

from __future__ import annotations

import datetime as dt

from moonfield import moon, observer, phase, sun
from moonfield import time as mtime
from moonfield.location import Location

UTC = mtime.UTC
GREENWICH = Location(51.4779, -0.0015, "Greenwich", "Europe/London")

ARCSEC = 1.0 / 3600.0


class TestSolarPosition:
    """README row: under 0.1 arcsecond at Meeus example 25.b."""

    JD = 2448908.5  # 1992 October 13 at 0h TD
    REFERENCE_APPARENT_LONGITUDE = 199.90895

    def test_apparent_longitude(self):
        error = abs(sun.position(self.JD).apparent_longitude - self.REFERENCE_APPARENT_LONGITUDE)
        print(f"\n  solar apparent longitude error: {error / ARCSEC:.2f} arcsec")
        assert error < 0.1 * ARCSEC


class TestLunarPosition:
    """README row: ~2 arcseconds in position, ~12 km in distance, at 47.a."""

    JD = 2448724.5  # 1992 April 12 at 0h TD
    REFERENCE_LONGITUDE = 133.167265
    REFERENCE_LATITUDE = -3.229126
    REFERENCE_DISTANCE_KM = 368409.7

    def test_position_is_within_a_few_arcseconds(self):
        position = moon.position(self.JD)
        lon_error = abs(position.ecliptic_longitude - self.REFERENCE_LONGITUDE)
        lat_error = abs(position.ecliptic_latitude - self.REFERENCE_LATITUDE)
        print(
            f"\n  lunar longitude error: {lon_error / ARCSEC:.2f} arcsec"
            f"\n  lunar latitude  error: {lat_error / ARCSEC:.2f} arcsec"
        )
        assert lon_error < 3 * ARCSEC
        assert lat_error < 3 * ARCSEC

    def test_distance_is_within_about_fifteen_kilometres(self):
        error = abs(moon.position(self.JD).distance_km - self.REFERENCE_DISTANCE_KM)
        print(f"\n  lunar distance error: {error:.1f} km")
        assert error < 15.0


class TestPhaseTiming:
    """README row: 1.0 to 2.6 minutes against three published new Moons."""

    PUBLISHED_NEW_MOONS_2026 = (
        dt.datetime(2026, 1, 18, 19, 52, tzinfo=UTC),
        dt.datetime(2026, 3, 19, 1, 23, tzinfo=UTC),
        dt.datetime(2026, 8, 12, 17, 37, tzinfo=UTC),
    )

    def test_new_moons_land_within_three_minutes(self):
        worst = 0.0
        for published in self.PUBLISHED_NEW_MOONS_2026:
            found = phase.next_phase(published - dt.timedelta(days=2), 0.0)
            minutes = abs((found - published).total_seconds()) / 60.0
            worst = max(worst, minutes)
        print(f"\n  worst new Moon timing error: {worst:.1f} minutes")
        # The table says 2.6. Three leaves room for the published minute
        # itself being rounded, without leaving room for a real regression.
        assert worst < 3.0


class TestRiseAndSet:
    """README row: 1 to 2 minutes against published Greenwich solstice times."""

    SOLSTICE = dt.datetime(2026, 6, 21, 12, tzinfo=UTC)
    PUBLISHED_SUNRISE = (4, 43)  # BST
    PUBLISHED_SUNSET = (21, 22)

    def _error_minutes(self, moment, published) -> float:
        local = moment.astimezone(GREENWICH.zone)
        hours, minutes = published
        return abs((local.hour * 60 + local.minute) - (hours * 60 + minutes))

    def test_sunrise_and_sunset_land_within_three_minutes(self):
        result = observer.sun_rise_set(GREENWICH, self.SOLSTICE)
        rise_error = self._error_minutes(result.rise, self.PUBLISHED_SUNRISE)
        set_error = self._error_minutes(result.setting, self.PUBLISHED_SUNSET)
        print(
            f"\n  sunrise error: {rise_error:.0f} min"
            f"\n  sunset  error: {set_error:.0f} min"
        )
        assert rise_error <= 3
        assert set_error <= 3


class TestTidesAreHonestlyBad:
    """README row: over an hour, consistently, against the Brest tide table.

    This row is the only one where being *worse* than advertised would be less
    alarming than being better. If someone ever makes the equilibrium model
    accurate enough to look usable, that is a teaching problem: module 04 is
    built on discovering that it is not.
    """

    BREST = Location(48.383, -4.495, "Brest", "UTC")
    # High waters published for Brest, from docs/04-tides/data/brest-2026-08.csv
    PUBLISHED_HIGH_WATERS = (
        dt.datetime(2026, 8, 16, 4, 6, tzinfo=UTC),
        dt.datetime(2026, 8, 16, 16, 32, tzinfo=UTC),
        dt.datetime(2026, 8, 17, 4, 56, tzinfo=UTC),
    )

    def test_the_uncalibrated_model_is_more_than_an_hour_out(self):
        from moonfield import tides

        # interval 0.0 is the pure equilibrium model: high water exactly when
        # the Moon is overhead, which is the assumption module 04 dismantles.
        estimate = tides.rough(self.BREST, dt.datetime(2026, 8, 16, 12, tzinfo=UTC), 0.0)
        rows = tides.compare(estimate, list(self.PUBLISHED_HIGH_WATERS), kind="high")
        errors = [abs(row["delta_hours"]) for row in rows if row["delta_hours"] is not None]
        assert len(errors) == len(self.PUBLISHED_HIGH_WATERS), "every high water should match an event"
        print(f"\n  Brest high water errors: {[f'{e:.2f} h' for e in errors]}")
        assert min(errors) > 1.0, "the model should not look usable without calibration"
