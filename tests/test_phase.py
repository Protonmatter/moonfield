"""Tests for the phase engine.

The reference new and full Moon times below are published values. If these
start failing, the first thing to check is whether the phase-finding search is
converging, not whether the astronomy is wrong.
"""

import datetime as dt

import pytest

from moonfield import phase
from moonfield import time as mtime

UTC = mtime.UTC

# Published times of new and full Moon, to the nearest minute.
KNOWN_NEW = [
    dt.datetime(2026, 1, 18, 19, 52, tzinfo=UTC),
    dt.datetime(2026, 3, 19, 1, 23, tzinfo=UTC),
    dt.datetime(2026, 8, 12, 17, 37, tzinfo=UTC),
]
KNOWN_FULL = [
    dt.datetime(2026, 1, 3, 10, 3, tzinfo=UTC),
    dt.datetime(2026, 6, 29, 23, 57, tzinfo=UTC),
    dt.datetime(2026, 8, 28, 4, 18, tzinfo=UTC),
]


class TestKnownPhases:
    @pytest.mark.parametrize("moment", KNOWN_NEW)
    def test_new_moon_elongation_is_near_zero(self, moment):
        elong = phase.compute(moment).elongation
        wrapped = min(elong, 360 - elong)
        assert wrapped < 0.5, "elongation should be ~0 at new Moon"

    @pytest.mark.parametrize("moment", KNOWN_NEW)
    def test_new_moon_is_barely_illuminated(self, moment):
        assert phase.compute(moment).illumination < 0.005

    @pytest.mark.parametrize("moment", KNOWN_FULL)
    def test_full_moon_elongation_is_near_180(self, moment):
        assert abs(phase.compute(moment).elongation - 180) < 0.5

    @pytest.mark.parametrize("moment", KNOWN_FULL)
    def test_full_moon_is_almost_fully_lit(self, moment):
        assert phase.compute(moment).illumination > 0.995

    @pytest.mark.parametrize("moment", KNOWN_NEW)
    def test_search_finds_the_published_new_moon(self, moment):
        found = phase.next_phase(moment - dt.timedelta(days=10), 0.0)
        error_minutes = abs((found - moment).total_seconds()) / 60
        assert error_minutes < 30, f"off by {error_minutes:.1f} minutes"

    @pytest.mark.parametrize("moment", KNOWN_FULL)
    def test_search_finds_the_published_full_moon(self, moment):
        found = phase.next_phase(moment - dt.timedelta(days=10), 180.0)
        error_minutes = abs((found - moment).total_seconds()) / 60
        assert error_minutes < 30, f"off by {error_minutes:.1f} minutes"


class TestIllumination:
    def test_always_between_zero_and_one(self):
        for day in range(0, 400, 3):
            when = dt.datetime(2026, 1, 1, tzinfo=UTC) + dt.timedelta(days=day)
            assert 0.0 <= phase.compute(when).illumination <= 1.0

    def test_quarter_moons_are_about_half_lit(self):
        for target in (90.0, 270.0):
            moment = phase.next_phase(dt.datetime(2026, 5, 1, tzinfo=UTC), target)
            assert phase.compute(moment).illumination == pytest.approx(0.5, abs=0.02)

    def test_waxing_flag_matches_elongation(self):
        for day in range(0, 60):
            when = dt.datetime(2026, 4, 1, tzinfo=UTC) + dt.timedelta(days=day)
            info = phase.compute(when)
            assert info.waxing == (info.elongation < 180.0)

    def test_illumination_grows_while_waxing(self):
        new_moon = phase.next_phase(dt.datetime(2026, 5, 1, tzinfo=UTC), 0.0)
        values = [
            phase.compute(new_moon + dt.timedelta(days=d)).illumination
            for d in range(1, 14)
        ]
        assert all(b > a for a, b in zip(values, values[1:], strict=False))


class TestPhaseNames:
    @pytest.mark.parametrize(
        "elongation, expected",
        [
            (0, "New Moon"),
            (2, "New Moon"),
            (45, "Waxing Crescent"),
            (90, "First Quarter"),
            (135, "Waxing Gibbous"),
            (180, "Full Moon"),
            (225, "Waning Gibbous"),
            (270, "Last Quarter"),
            (315, "Waning Crescent"),
            (358, "New Moon"),
        ],
    )
    def test_names(self, elongation, expected):
        assert phase.phase_name(elongation) == expected

    def test_wraps_past_360(self):
        assert phase.phase_name(361) == phase.phase_name(1)


class TestTheTwoModels:
    def test_simple_model_stays_close_to_the_real_one(self):
        """The clock model should be within about a day of the truth."""
        worst = 0.0
        for day in range(0, 365, 7):
            when = dt.datetime(2026, 1, 1, tzinfo=UTC) + dt.timedelta(days=day)
            info = phase.compute(when)
            gap = abs(info.model_disagreement_hours)
            worst = max(worst, min(gap, abs(gap - 24 * mtime.SYNODIC_MONTH)))
        assert worst < 26, f"simple model drifted {worst:.1f} hours"

    def test_simple_model_illumination_is_in_range(self):
        for day in range(0, 60):
            when = dt.datetime(2026, 2, 1, tzinfo=UTC) + dt.timedelta(days=day)
            _, illum = phase.simple_phase(when)
            assert 0.0 <= illum <= 1.0

    def test_simple_age_cycles_within_a_synodic_month(self):
        age, _ = phase.simple_phase(dt.datetime(2026, 7, 4, tzinfo=UTC))
        assert 0 <= age < mtime.SYNODIC_MONTH


class TestNextPhases:
    def test_all_four_are_reported(self):
        info = phase.compute(dt.datetime(2026, 8, 16, tzinfo=UTC))
        assert set(info.next_phases) == {
            "New Moon", "First Quarter", "Full Moon", "Last Quarter"
        }

    def test_all_are_in_the_future(self):
        when = dt.datetime(2026, 8, 16, tzinfo=UTC)
        info = phase.compute(when)
        for moment, _ in info.next_phases.values():
            assert moment > when

    def test_all_are_within_one_synodic_month(self):
        when = dt.datetime(2026, 8, 16, tzinfo=UTC)
        info = phase.compute(when)
        for _, days in info.next_phases.values():
            assert 0 < days <= mtime.SYNODIC_MONTH + 0.1

    def test_consecutive_new_moons_are_a_synodic_month_apart(self):
        first = phase.next_phase(dt.datetime(2026, 1, 1, tzinfo=UTC), 0.0)
        second = phase.next_phase(first + dt.timedelta(hours=1), 0.0)
        gap = (second - first).total_seconds() / 86400
        assert 29.2 < gap < 29.9, "real synodic months vary; the mean is 29.53"


class TestAsciiMoon:
    def test_new_moon_is_dark(self):
        art = phase.ascii_moon(0.0, waxing=True)
        assert "#" not in art

    def test_full_moon_is_lit(self):
        art = phase.ascii_moon(1.0, waxing=True)
        assert "." not in art and "#" in art

    def test_waxing_lights_the_right_in_the_north(self):
        art = phase.ascii_moon(0.25, waxing=True)
        row = max(art.splitlines(), key=len)
        assert row.index("#") > row.index(".")

    def test_southern_hemisphere_is_mirrored(self):
        north = phase.ascii_moon(0.25, waxing=True, southern=False)
        south = phase.ascii_moon(0.25, waxing=True, southern=True)
        assert north != south

    def test_lit_area_grows_with_illumination(self):
        counts = [phase.ascii_moon(k / 10, True).count("#") for k in range(11)]
        assert counts == sorted(counts)
