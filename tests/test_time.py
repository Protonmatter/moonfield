"""Tests for time handling.

The reference values come from Meeus, *Astronomical Algorithms*, chapter 7,
so a failure here means either a real bug or that you have found a typo in a
very well-checked textbook. Bet on the bug.
"""

import datetime as dt

import pytest

from moonfield import time as mtime


class TestJulianDay:
    @pytest.mark.parametrize(
        "moment, expected",
        [
            (dt.datetime(2000, 1, 1, 12, 0, tzinfo=mtime.UTC), 2451545.0),
            (dt.datetime(1999, 1, 1, 0, 0, tzinfo=mtime.UTC), 2451179.5),
            (dt.datetime(1987, 1, 27, 0, 0, tzinfo=mtime.UTC), 2446822.5),
            (dt.datetime(1988, 6, 19, 12, 0, tzinfo=mtime.UTC), 2447332.0),
            (dt.datetime(1900, 1, 1, 0, 0, tzinfo=mtime.UTC), 2415020.5),
            (dt.datetime(1600, 12, 31, 0, 0, tzinfo=mtime.UTC), 2305812.5),
        ],
    )
    def test_known_dates(self, moment, expected):
        assert mtime.julian_day(moment) == pytest.approx(expected, abs=1e-6)

    def test_sputnik_launch(self):
        """Meeus example 7.b, to the nearest ten-thousandth of a day."""
        launch = dt.datetime(1957, 10, 4, 19, 28, 34, tzinfo=mtime.UTC)
        assert mtime.julian_day(launch) == pytest.approx(2436116.31, abs=5e-3)

    def test_roundtrip(self):
        original = dt.datetime(2026, 8, 16, 21, 30, 45, tzinfo=mtime.UTC)
        recovered = mtime.from_julian_day(mtime.julian_day(original))
        assert abs((recovered - original).total_seconds()) < 0.01

    def test_j2000_constant_is_consistent(self):
        assert mtime.julian_centuries(mtime.J2000) == 0.0

    def test_advances_by_one_per_day(self):
        a = mtime.julian_day(dt.datetime(2026, 3, 1, tzinfo=mtime.UTC))
        b = mtime.julian_day(dt.datetime(2026, 3, 2, tzinfo=mtime.UTC))
        assert b - a == pytest.approx(1.0)

    def test_handles_leap_day(self):
        a = mtime.julian_day(dt.datetime(2024, 2, 28, tzinfo=mtime.UTC))
        b = mtime.julian_day(dt.datetime(2024, 3, 1, tzinfo=mtime.UTC))
        assert b - a == pytest.approx(2.0), "2024 is a leap year"


class TestEnsureUtc:
    def test_naive_is_treated_as_utc(self):
        naive = dt.datetime(2026, 8, 16, 12, 0)
        assert mtime.ensure_utc(naive).tzinfo == mtime.UTC
        assert mtime.ensure_utc(naive).hour == 12

    def test_aware_is_converted_not_relabelled(self):
        tz = dt.timezone(dt.timedelta(hours=5))
        aware = dt.datetime(2026, 8, 16, 12, 0, tzinfo=tz)
        assert mtime.ensure_utc(aware).hour == 7

    def test_none_gives_now(self):
        assert mtime.ensure_utc(None).tzinfo == mtime.UTC


class TestParseDatetime:
    def test_bare_date_is_midnight(self):
        parsed = mtime.parse_datetime("2026-08-16")
        assert (parsed.year, parsed.month, parsed.day) == (2026, 8, 16)

    def test_space_separator(self):
        parsed = mtime.parse_datetime("2026-08-16 21:30")
        assert parsed.hour == 21 and parsed.minute == 30

    def test_iso_t_separator(self):
        assert mtime.parse_datetime("2026-08-16T21:30").hour == 21

    def test_trailing_z_means_utc(self):
        parsed = mtime.parse_datetime("2026-08-16T21:30:00Z")
        assert parsed.hour == 21 and parsed.tzinfo == mtime.UTC

    def test_explicit_offset_is_respected(self):
        parsed = mtime.parse_datetime("2026-08-16T21:30:00+02:00")
        assert parsed.hour == 19

    def test_named_zone_is_applied(self):
        parsed = mtime.parse_datetime("2026-01-15T12:00", "Europe/Lisbon")
        assert parsed.hour == 12, "Lisbon is UTC+0 in January"

    def test_zone_offset_applied_in_summer(self):
        parsed = mtime.parse_datetime("2026-07-15T12:00", "Europe/Lisbon")
        assert parsed.hour == 11, "Lisbon is UTC+1 in July"

    def test_rubbish_gives_a_helpful_error(self):
        with pytest.raises(ValueError, match="could not understand"):
            mtime.parse_datetime("next tuesday")

    def test_empty_string_rejected(self):
        with pytest.raises(ValueError):
            mtime.parse_datetime("   ")


class TestSiderealTime:
    def test_known_gmst(self):
        """Meeus example 12.a: 1987 April 10 at 0h UT."""
        jd = mtime.julian_day(dt.datetime(1987, 4, 10, tzinfo=mtime.UTC))
        assert mtime.gmst_degrees(jd) == pytest.approx(197.693195, abs=1e-4)

    def test_sidereal_day_is_shorter_than_solar(self):
        jd = mtime.julian_day(dt.datetime(2026, 5, 1, tzinfo=mtime.UTC))
        drift = (mtime.gmst_degrees(jd + 1) - mtime.gmst_degrees(jd)) % 360.0
        minutes = drift / 15.0 * 60.0
        assert 3.9 < minutes < 4.0, "should gain about 3m56s per solar day"

    def test_local_sidereal_tracks_longitude(self):
        jd = mtime.julian_day(dt.datetime(2026, 5, 1, tzinfo=mtime.UTC))
        east = mtime.lst_degrees(jd, 15.0)
        prime = mtime.lst_degrees(jd, 0.0)
        assert (east - prime) % 360.0 == pytest.approx(15.0)


class TestObliquityAndNutation:
    def test_obliquity_is_about_23_44_degrees(self):
        jd = mtime.julian_day(dt.datetime(2026, 1, 1, tzinfo=mtime.UTC))
        assert 23.43 < mtime.mean_obliquity(jd) < 23.44

    def test_nutation_is_small(self):
        jd = mtime.julian_day(dt.datetime(2026, 1, 1, tzinfo=mtime.UTC))
        d_psi, d_eps = mtime.nutation(jd)
        assert abs(d_psi) < 0.01 and abs(d_eps) < 0.01


class TestFormatting:
    def test_duration_reads_naturally(self):
        assert mtime.format_duration(1.5) == "1 day 12 hours"
        assert mtime.format_duration(0.0) == "0 minutes"
        assert "2 days" in mtime.format_duration(2.25)

    def test_instant_shows_both_clocks(self):
        text = mtime.format_instant(dt.datetime(2026, 8, 16, 21, 0, tzinfo=mtime.UTC), "UTC")
        assert "2026-08-16" in text and "UTC" in text
