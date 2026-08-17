"""Tests for the command line.

These check two things: that commands run, and that when they *cannot* run they
say something a beginner could act on. The second is at least as important --
an unhelpful error message is a bug in a teaching tool.
"""

import pytest

from moonfield.cli import main


def run(capsys, *args):
    """Run the CLI and return (exit code, stdout, stderr)."""
    code = main(list(args))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


class TestNoArguments:
    def test_prints_help_and_succeeds(self, capsys):
        code, out, _ = run(capsys)
        assert code == 0
        assert "moonfield doctor" in out

    def test_suggests_a_first_step(self, capsys):
        _, out, _ = run(capsys)
        assert "New here" in out


class TestDoctor:
    def test_runs_and_passes(self, capsys):
        code, out, _ = run(capsys, "doctor")
        assert code == 0
        assert "Result: everything essential is working" in out

    def test_reports_python_and_timezone(self, capsys):
        _, out, _ = run(capsys, "doctor")
        assert "Python" in out and "UTC time" in out

    def test_separates_config_checks_from_clock_accuracy(self, capsys):
        """The blueprint is explicit that these must not be conflated."""
        _, out, _ = run(capsys, "doctor")
        assert "CONFIGURATION check" in out
        assert "cannot tell you whether your clock is actually set correctly" in out

    def test_offers_a_next_step(self, capsys):
        _, out, _ = run(capsys, "doctor")
        assert "Next step" in out


class TestPhase:
    def test_runs_without_a_location(self, capsys):
        """Phase is geocentric, so it must work before you set a location."""
        code, out, _ = run(capsys, "phase")
        assert code == 0
        assert "Phase:" in out and "Illuminated:" in out

    def test_accepts_a_date(self, capsys):
        code, out, _ = run(capsys, "phase", "--date", "2026-08-28")
        assert code == 0
        assert "Full Moon" in out

    def test_draws_the_moon(self, capsys):
        _, out, _ = run(capsys, "phase", "--date", "2026-08-28")
        assert "#" in out

    def test_no_art_suppresses_the_drawing(self, capsys):
        _, out, _ = run(capsys, "phase", "--date", "2026-08-28", "--no-art")
        assert "#" not in out

    def test_lists_the_four_upcoming_phases(self, capsys):
        _, out, _ = run(capsys, "phase")
        for name in ("New Moon", "First Quarter", "Full Moon", "Last Quarter"):
            assert name in out

    def test_explain_shows_the_working(self, capsys):
        _, out, _ = run(capsys, "phase", "--date", "2026-08-16", "--explain")
        assert "Julian Day" in out
        assert "Elongation" in out
        assert "Step 1" in out and "Step 5" in out

    def test_explain_compares_the_two_models(self, capsys):
        _, out, _ = run(capsys, "phase", "--date", "2026-08-16", "--explain")
        assert "simple age" in out and "true age" in out

    def test_explain_states_the_limitations(self, capsys):
        _, out, _ = run(capsys, "phase", "--date", "2026-08-16", "--explain")
        assert "ignores" in out.lower()

    def test_rejects_a_bad_date_helpfully(self, capsys):
        code, _, err = run(capsys, "phase", "--date", "the day before yesterday")
        assert code == 1
        assert "could not understand" in err


class TestLocationRequirement:
    @pytest.mark.parametrize("command", ["now", "sun", "moon", "frame", "seasons"])
    def test_explains_how_to_set_a_location(self, capsys, command):
        code, _, err = run(capsys, command)
        assert code == 1
        assert "config set-location" in err

    @pytest.mark.parametrize("command", ["now", "sun", "moon"])
    def test_warns_about_the_longitude_sign(self, capsys, command):
        _, _, err = run(capsys, command)
        assert "EAST-positive" in err or "east" in err.lower()

    @pytest.mark.parametrize("command", ["now", "sun", "moon", "frame"])
    def test_accepts_inline_coordinates(self, capsys, command):
        code, out, _ = run(capsys, command, "--lat", "51.4779", "--lon", "-0.0015")
        assert code == 0
        assert out.strip()


class TestConfig:
    def test_set_location_saves(self, capsys):
        code, out, _ = run(
            capsys, "config", "set-location",
            "--lat", "35.6762", "--lon", "139.6503",
            "--name", "Tokyo", "--timezone", "Asia/Tokyo",
        )
        assert code == 0
        assert "Tokyo" in out

    def test_show_reads_it_back(self, capsys):
        run(capsys, "config", "set-location", "--lat", "35.6762", "--lon", "139.6503", "--name", "Tokyo")
        _, out, _ = run(capsys, "config", "show")
        assert "Tokyo" in out and "35.6762" in out

    def test_show_labels_the_hemispheres(self, capsys):
        run(capsys, "config", "set-location", "--lat", "-33.87", "--lon", "151.21")
        _, out, _ = run(capsys, "config", "show")
        assert "south" in out and "east" in out

    def test_accepts_dms_coordinates(self, capsys):
        code, out, _ = run(capsys, "config", "set-location", "--lat", "33 52 7.7 S", "--lon", "151 12 33 E")
        assert code == 0
        assert "33.8688S" in out

    def test_rejects_out_of_range_latitude(self, capsys):
        code, _, err = run(capsys, "config", "set-location", "--lat", "500", "--lon", "0")
        assert code == 1
        assert "latitude" in err.lower()

    def test_clear_forgets_the_location(self, capsys):
        run(capsys, "config", "set-location", "--lat", "1", "--lon", "2")
        run(capsys, "config", "clear")
        _, out, _ = run(capsys, "config", "show")
        assert "No configuration saved" in out

    def test_path_is_printed(self, capsys):
        code, out, _ = run(capsys, "config", "path")
        assert code == 0 and "config.json" in out

    def test_bare_config_lists_subcommands(self, capsys):
        code, out, _ = run(capsys, "config")
        assert code == 1 and "set-location" in out


class TestNow:
    def test_reports_sun_and_moon(self, capsys, saved_greenwich):
        code, out, _ = run(capsys, "now")
        assert code == 0
        assert "Sun" in out and "Moon" in out

    def test_tells_you_where_to_look(self, capsys, saved_greenwich):
        _, out, _ = run(capsys, "now")
        assert "What you should be able to see" in out

    def test_gives_a_hand_span_hint(self, capsys, saved_greenwich):
        _, out, _ = run(capsys, "now")
        assert "fist" in out

    def test_handles_the_arctic_in_summer(self, capsys):
        code, out, _ = run(
            capsys, "now", "--lat", "78.22", "--lon", "15.63", "--date", "2026-06-21T12:00"
        )
        assert code == 0
        assert "never sets" in out


class TestSeasons:
    def test_compares_solstices_and_equinoxes(self, capsys, saved_greenwich):
        code, out, _ = run(capsys, "seasons", "--date", "2026-08-16")
        assert code == 0
        assert "June solstice" in out and "December solstice" in out

    def test_explain_debunks_the_distance_myth(self, capsys, saved_greenwich):
        _, out, _ = run(capsys, "seasons", "--date", "2026-08-16", "--explain")
        assert "CLOSER to the Sun in December" in out
        assert "axial tilt" in out

    def test_works_in_the_southern_hemisphere(self, capsys, sydney):
        from moonfield.location import save_location

        save_location(sydney)
        code, out, _ = run(capsys, "seasons", "--date", "2026-08-16")
        assert code == 0
        assert "southern" in out


class TestFrame:
    def test_accepts_a_compass_point(self, capsys, saved_greenwich):
        code, out, _ = run(capsys, "frame", "--facing", "SE")
        assert code == 0
        assert "SE" in out

    def test_accepts_a_bearing(self, capsys, saved_greenwich):
        code, out, _ = run(capsys, "frame", "--facing", "135")
        assert code == 0

    def test_rejects_nonsense_directions(self, capsys, saved_greenwich):
        code, _, err = run(capsys, "frame", "--facing", "thataway")
        assert code == 1
        assert "direction" in err.lower()

    def test_asks_for_a_prediction_first(self, capsys, saved_greenwich):
        _, out, _ = run(capsys, "frame", "--facing", "S")
        assert "write down where you think" in out

    def test_lists_reasons_a_mismatch_is_legitimate(self, capsys, saved_greenwich):
        _, out, _ = run(capsys, "frame", "--facing", "S")
        assert "compass" in out and "clock" in out


class TestTide:
    def test_bare_tide_lists_subcommands(self, capsys):
        code, out, _ = run(capsys, "tide")
        assert code == 1
        assert "explain" in out and "rough" in out and "compare" in out

    def test_explain_needs_no_location(self, capsys):
        code, out, _ = run(capsys, "tide", "explain")
        assert code == 0
        assert "lunar day" in out.lower()

    def test_explain_covers_all_ten_steps(self, capsys):
        _, out, _ = run(capsys, "tide", "explain")
        for topic in ("What is a tide", "lunar day", "Spring and neap",
                      "harbour", "harmonic analysis", "LUNITIDAL"):
            assert topic.lower() in out.lower(), f"missing: {topic}"

    def test_explain_says_the_difference_is_what_matters(self, capsys):
        """The classic misconception is that tides come from the pull itself."""
        _, out, _ = run(capsys, "tide", "explain")
        assert "DIFFERENCE in pull" in out

    def test_rough_shouts_that_it_is_not_navigational(self, capsys, saved_greenwich):
        code, out, _ = run(capsys, "tide", "rough", "--date", "2026-08-16T12:00")
        assert code == 0
        assert "NOT FOR NAVIGATION" in out

    def test_rough_asks_for_a_prediction_before_checking(self, capsys, saved_greenwich):
        _, out, _ = run(capsys, "tide", "rough", "--date", "2026-08-16T12:00")
        assert "Before you check a real tide table" in out

    def test_rough_accepts_a_lunitidal_interval(self, capsys, saved_greenwich):
        code, out, _ = run(capsys, "tide", "rough", "--date", "2026-08-16T12:00", "--interval", "4.5")
        assert code == 0
        assert "4.50 hours" in out

    def test_compare_needs_observations(self, capsys, saved_greenwich):
        code, _, err = run(capsys, "tide", "compare", "--date", "2026-08-16T12:00")
        assert code == 1
        assert "observed" in err

    def test_compare_reports_the_error(self, capsys, saved_greenwich):
        code, out, _ = run(
            capsys, "tide", "compare", "--date", "2026-08-16T12:00",
            "--observed", "2026-08-16T09:14", "--observed", "2026-08-16T21:41",
        )
        assert code == 0
        assert "Model error" in out or "model error" in out.lower()

    def test_compare_explains_a_consistent_offset(self, capsys, saved_greenwich):
        code, out, _ = run(
            capsys, "tide", "compare", "--date", "2026-08-16T12:00",
            "--observed", "2026-08-16T18:04", "--observed", "2026-08-17T06:26",
        )
        assert code == 0
        assert "lunitidal" in out.lower() or "VARIES" in out


class TestLongitude:
    def test_explains_the_arithmetic(self, capsys):
        code, out, _ = run(capsys, "longitude")
        assert code == 0
        assert "15 degrees per hour" in out

    def test_computes_a_longitude(self, capsys):
        code, out, _ = run(capsys, "longitude", "--reference", "14.5", "--local-noon", "12")
        assert code == 0
        assert "-37.500" in out

    def test_wrong_landfall_shows_the_consequence(self, capsys):
        code, out, _ = run(
            capsys, "longitude", "--reference", "14.5", "--local-noon", "12", "--drift", "120"
        )
        assert code == 0
        assert "WRONG LANDFALL" in out
        assert "km" in out

    def test_bigger_drift_means_bigger_error(self, capsys):
        _, small, _ = run(capsys, "longitude", "--reference", "14.5", "--drift", "10")
        _, large, _ = run(capsys, "longitude", "--reference", "14.5", "--drift", "600")
        assert "how ships were lost" in large
        assert "how ships were lost" not in small


class TestVersion:
    def test_version_flag(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            main(["--version"])
        assert excinfo.value.code == 0
        assert "moonfield" in capsys.readouterr().out


class TestLocationOverrideSafety:
    """A half-given location must never silently fall back to the saved one.

    Regression test: `moonfield sun --lat 40` used to quietly answer for
    whatever location happened to be saved, which is the worst failure mode
    for a tool people use to check their own observations against the sky.
    """

    def test_lat_without_lon_is_refused(self, capsys, saved_greenwich):
        code, out, err = run(capsys, "sun", "--lat", "40")
        assert code == 1
        assert "--lon" in err
        # It must not have quietly answered for the saved location instead.
        assert "Greenwich" not in out

    def test_lon_without_lat_is_refused(self, capsys, saved_greenwich):
        code, out, err = run(capsys, "sun", "--lon", "40")
        assert code == 1
        assert "--lat" in err

    def test_the_error_explains_the_sign_convention(self, capsys, saved_greenwich):
        _, _, err = run(capsys, "sun", "--lat", "40")
        assert "EAST-positive" in err

    def test_both_together_are_accepted(self, capsys, saved_greenwich):
        code, out, _ = run(capsys, "sun", "--lat", "-33.87", "--lon", "151.21")
        assert code == 0
        assert "33.8700S" in out
        assert "Greenwich" not in out

    def test_neither_falls_back_to_saved(self, capsys, saved_greenwich):
        code, out, _ = run(capsys, "sun")
        assert code == 0
        assert "Greenwich" in out


class TestPhaseRespectsHemisphere:
    """The phase numbers are geocentric, but the drawing is not."""

    def test_phase_accepts_a_location(self, capsys):
        code, out, _ = run(capsys, "phase", "--no-art", "--lat", "51.48", "--lon", "0.0")
        assert code == 0
        assert "Phase:" in out

    def test_art_flips_between_hemispheres(self, capsys):
        _, northern, _ = run(
            capsys, "phase", "--lat", "51.48", "--lon", "0.0", "--date", "2026-08-16"
        )
        _, southern, _ = run(
            capsys, "phase", "--lat", "-33.87", "--lon", "151.21", "--date", "2026-08-16"
        )
        assert "southern hemisphere" in southern
        assert "southern hemisphere" not in northern
        assert northern != southern

    def test_illumination_does_not_depend_on_hemisphere(self, capsys):
        _, northern, _ = run(
            capsys, "phase", "--no-art", "--lat", "51.48", "--lon", "0.0",
            "--date", "2026-08-16",
        )
        _, southern, _ = run(
            capsys, "phase", "--no-art", "--lat", "-33.87", "--lon", "151.21",
            "--date", "2026-08-16",
        )

        def illumination(text):
            for line in text.splitlines():
                if "Illuminated:" in line:
                    return line.split(":")[1].strip()
            raise AssertionError("no illumination line found")

        assert illumination(northern) == illumination(southern)
