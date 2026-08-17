"""Tests for the tide teaching model.

These tests check that the model behaves the way the *physics* says it should.
They deliberately do NOT check it against real tide tables, because it would
fail -- and that failure is the lesson, not a defect.
"""

import datetime as dt

import pytest

from moonfield import phase, tides
from moonfield import time as mtime
from moonfield.location import Location

UTC = mtime.UTC
BRIGHTON = Location(50.8225, -0.1372, "Brighton", "Europe/London")
SYDNEY = Location(-33.8688, 151.2093, "Sydney", "Australia/Sydney")


class TestLunarDay:
    def test_is_about_twenty_four_hours_fifty_minutes(self):
        assert tides.lunar_day_hours() == pytest.approx(24.84, abs=0.01)

    def test_is_longer_than_a_solar_day(self):
        assert tides.lunar_day_hours() > 24.0

    def test_the_extra_time_matches_the_moons_daily_motion(self):
        """13.2 degrees a day at 15 degrees an hour is about 53 minutes."""
        extra_minutes = (tides.lunar_day_hours() - 24.0) * 60
        assert 45 < extra_minutes < 55


class TestSpringNeap:
    def test_springs_at_new_moon(self):
        moment = phase.next_phase(dt.datetime(2026, 5, 1, tzinfo=UTC), 0.0)
        factor, label = tides.spring_neap(moment)
        assert "spring" in label
        assert factor > 1.4

    def test_springs_at_full_moon(self):
        moment = phase.next_phase(dt.datetime(2026, 5, 1, tzinfo=UTC), 180.0)
        factor, label = tides.spring_neap(moment)
        assert "spring" in label
        assert factor > 1.4

    def test_neaps_at_first_quarter(self):
        moment = phase.next_phase(dt.datetime(2026, 5, 1, tzinfo=UTC), 90.0)
        factor, label = tides.spring_neap(moment)
        assert "neap" in label
        assert factor < 0.6

    def test_neaps_at_last_quarter(self):
        moment = phase.next_phase(dt.datetime(2026, 5, 1, tzinfo=UTC), 270.0)
        _, label = tides.spring_neap(moment)
        assert "neap" in label

    def test_spring_range_is_roughly_double_the_neap_range(self):
        new_moon = phase.next_phase(dt.datetime(2026, 5, 1, tzinfo=UTC), 0.0)
        quarter = phase.next_phase(dt.datetime(2026, 5, 1, tzinfo=UTC), 90.0)
        spring, _ = tides.spring_neap(new_moon)
        neap, _ = tides.spring_neap(quarter)
        assert 2.0 < spring / neap < 3.0

    def test_cycle_repeats_twice_per_month(self):
        """Springs happen at BOTH new and full Moon, so the pattern has period 2."""
        start = dt.datetime(2026, 5, 1, tzinfo=UTC)
        factors = [
            tides.spring_neap(start + dt.timedelta(days=d))[0]
            for d in range(0, 30)
        ]
        peaks = [
            i for i in range(1, len(factors) - 1)
            if factors[i] > factors[i - 1] and factors[i] > factors[i + 1]
        ]
        assert len(peaks) == 2


class TestRoughModel:
    def test_produces_events(self):
        estimate = tides.rough(BRIGHTON, dt.datetime(2026, 8, 16, 12, tzinfo=UTC))
        assert len(estimate.events) >= 4

    def test_alternates_high_and_low(self):
        estimate = tides.rough(BRIGHTON, dt.datetime(2026, 8, 16, 12, tzinfo=UTC))
        kinds = [event.kind for event in estimate.events]
        assert all(a != b for a, b in zip(kinds, kinds[1:], strict=False))

    def test_consecutive_highs_are_about_half_a_lunar_day_apart(self):
        estimate = tides.rough(BRIGHTON, dt.datetime(2026, 8, 16, 12, tzinfo=UTC))
        highs = [e.when for e in estimate.events if e.kind == "high"]
        for a, b in zip(highs, highs[1:], strict=False):
            hours = (b - a).total_seconds() / 3600
            assert 11.5 < hours < 13.5

    def test_reports_rising_or_falling(self):
        estimate = tides.rough(BRIGHTON, dt.datetime(2026, 8, 16, 12, tzinfo=UTC))
        assert estimate.state in ("rising", "falling")

    def test_fraction_is_a_fraction(self):
        for hour in range(0, 24, 3):
            estimate = tides.rough(BRIGHTON, dt.datetime(2026, 8, 16, hour, tzinfo=UTC))
            assert 0.0 <= estimate.fraction <= 1.0

    def test_lunitidal_interval_shifts_everything(self):
        when = dt.datetime(2026, 8, 16, 12, tzinfo=UTC)
        base = tides.rough(BRIGHTON, when, lunitidal_interval=0.0)
        lagged = tides.rough(BRIGHTON, when, lunitidal_interval=3.0)
        base_high = [e.when for e in base.events if e.kind == "high"][0]
        lagged_high = [e.when for e in lagged.events if e.kind == "high"][0]
        shift = (lagged_high - base_high).total_seconds() / 3600
        assert shift == pytest.approx(3.0, abs=0.01)

    def test_warns_loudly_when_no_interval_is_set(self):
        estimate = tides.rough(BRIGHTON, dt.datetime(2026, 8, 16, 12, tzinfo=UTC))
        joined = " ".join(estimate.notes).lower()
        assert "lunitidal" in joined
        assert "not a navigational prediction" in joined

    def test_always_says_it_is_not_for_navigation(self):
        for place in (BRIGHTON, SYDNEY):
            estimate = tides.rough(place, dt.datetime(2026, 8, 16, 12, tzinfo=UTC))
            assert any("navigation" in note.lower() for note in estimate.notes)

    def test_works_in_the_southern_hemisphere(self):
        estimate = tides.rough(SYDNEY, dt.datetime(2026, 8, 16, 12, tzinfo=UTC))
        assert len(estimate.events) >= 4


class TestCompare:
    def test_reports_the_gap(self):
        when = dt.datetime(2026, 8, 16, 12, tzinfo=UTC)
        estimate = tides.rough(BRIGHTON, when)
        observed = [e.when + dt.timedelta(hours=2) for e in estimate.events if e.kind == "high"][:2]
        rows = tides.compare(estimate, observed)
        assert len(rows) == 2
        for row in rows:
            assert row["delta_hours"] == pytest.approx(-2.0, abs=0.1)

    def test_suggests_the_interval_that_would_fix_it(self):
        when = dt.datetime(2026, 8, 16, 12, tzinfo=UTC)
        estimate = tides.rough(BRIGHTON, when)
        observed = [e.when + dt.timedelta(hours=4) for e in estimate.events if e.kind == "high"][:3]
        rows = tides.compare(estimate, observed)
        assert tides.suggested_interval(rows) == pytest.approx(4.0, abs=0.1)

    def test_applying_the_suggestion_actually_lines_things_up(self):
        """A round trip: measure the lag, feed it back, check the error vanishes."""
        when = dt.datetime(2026, 8, 16, 12, tzinfo=UTC)
        naive = tides.rough(BRIGHTON, when)
        observed = [e.when + dt.timedelta(hours=5) for e in naive.events if e.kind == "high"][:3]

        suggestion = tides.suggested_interval(tides.compare(naive, observed))
        corrected = tides.rough(BRIGHTON, when, lunitidal_interval=suggestion)
        rows = tides.compare(corrected, observed)

        for row in rows:
            assert abs(row["delta_hours"]) < 0.1

    def test_handles_no_observations(self):
        estimate = tides.rough(BRIGHTON, dt.datetime(2026, 8, 16, 12, tzinfo=UTC))
        assert tides.suggested_interval(tides.compare(estimate, [])) is None
