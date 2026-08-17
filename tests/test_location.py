"""Tests for locations, coordinate parsing and the config file."""

import json

import pytest

from moonfield.location import (
    Location,
    config_path,
    load_location,
    parse_coordinate,
    save_location,
)


class TestParseCoordinate:
    @pytest.mark.parametrize(
        "text, expected",
        [
            ("51.4779", 51.4779),
            ("-33.8688", -33.8688),
            ("+12.5", 12.5),
            ("0", 0.0),
        ],
    )
    def test_decimal(self, text, expected):
        assert parse_coordinate(text) == pytest.approx(expected)

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("51.4779 N", 51.4779),
            ("33.8688 S", -33.8688),
            ("151.2093 E", 151.2093),
            ("74.006 W", -74.006),
        ],
    )
    def test_hemisphere_letters(self, text, expected):
        assert parse_coordinate(text) == pytest.approx(expected)

    def test_degrees_minutes_seconds(self):
        assert parse_coordinate("33 52 7.7 S") == pytest.approx(-33.8688, abs=1e-4)

    def test_symbols(self):
        assert parse_coordinate("51°28'40.4\"N") == pytest.approx(51.4779, abs=1e-3)

    def test_rejects_nonsense(self):
        with pytest.raises(ValueError, match="could not read"):
            parse_coordinate("somewhere near the shops")

    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            parse_coordinate("  ")

    def test_rejects_contradictory_sign_and_letter(self):
        """-33 S is ambiguous: does the writer mean 33 south, or 33 north?"""
        with pytest.raises(ValueError, match="ambiguous"):
            parse_coordinate("-33.5 S")


class TestLocation:
    def test_rejects_impossible_latitude(self):
        with pytest.raises(ValueError, match="latitude"):
            Location(latitude=95.0, longitude=0.0)

    def test_rejects_impossible_longitude(self):
        with pytest.raises(ValueError, match="longitude"):
            Location(latitude=0.0, longitude=200.0)

    def test_accepts_the_poles(self):
        assert Location(90.0, 0.0).latitude == 90.0
        assert Location(-90.0, 0.0).latitude == -90.0

    @pytest.mark.parametrize(
        "latitude, expected",
        [(51.5, "northern"), (-33.9, "southern"), (0.0, "equatorial")],
    )
    def test_hemisphere(self, latitude, expected):
        assert Location(latitude, 0.0).hemisphere == expected

    def test_describe_uses_hemisphere_letters(self):
        text = Location(-33.8688, 151.2093, "Sydney").describe()
        assert "33.8688S" in text and "151.2093E" in text
        assert "Sydney" in text

    def test_describe_marks_west_as_w(self):
        assert "74.0060W" in Location(40.7128, -74.006, "New York").describe()

    def test_radians_conversion(self):
        location = Location(90.0, 180.0)
        assert location.latitude_rad == pytest.approx(1.5707963, abs=1e-6)
        assert location.longitude_rad == pytest.approx(3.1415927, abs=1e-6)

    def test_roundtrips_through_a_dict(self):
        original = Location(51.4779, -0.0015, "Greenwich", "Europe/London", 15.0)
        assert Location.from_dict(original.to_dict()) == original


class TestConfigFile:
    def test_honours_the_environment_override(self, tmp_path, monkeypatch):
        target = tmp_path / "custom" / "config.json"
        monkeypatch.setenv("MOONFIELD_CONFIG", str(target))
        assert config_path() == target

    def test_saves_and_reloads(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MOONFIELD_CONFIG", str(tmp_path / "config.json"))
        original = Location(35.6762, 139.6503, "Tokyo", "Asia/Tokyo")
        save_location(original)
        assert load_location() == original

    def test_creates_parent_directories(self, tmp_path, monkeypatch):
        target = tmp_path / "deeply" / "nested" / "config.json"
        monkeypatch.setenv("MOONFIELD_CONFIG", str(target))
        save_location(Location(0.0, 0.0))
        assert target.exists()

    def test_missing_file_gives_none(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MOONFIELD_CONFIG", str(tmp_path / "nothing.json"))
        assert load_location() is None

    def test_corrupt_file_does_not_crash(self, tmp_path, monkeypatch):
        target = tmp_path / "config.json"
        target.write_text("{ this is not json at all")
        monkeypatch.setenv("MOONFIELD_CONFIG", str(target))
        assert load_location() is None

    def test_partial_data_does_not_crash(self, tmp_path, monkeypatch):
        target = tmp_path / "config.json"
        target.write_text(json.dumps({"location": {"latitude": 10.0}}))
        monkeypatch.setenv("MOONFIELD_CONFIG", str(target))
        assert load_location() is None

    def test_out_of_range_saved_data_is_rejected(self, tmp_path, monkeypatch):
        target = tmp_path / "config.json"
        target.write_text(json.dumps({"location": {"latitude": 999, "longitude": 0}}))
        monkeypatch.setenv("MOONFIELD_CONFIG", str(target))
        assert load_location() is None

    def test_other_settings_survive_a_location_save(self, tmp_path, monkeypatch):
        target = tmp_path / "config.json"
        target.write_text(json.dumps({"favourite_planet": "Saturn"}))
        monkeypatch.setenv("MOONFIELD_CONFIG", str(target))
        save_location(Location(1.0, 2.0))
        assert json.loads(target.read_text())["favourite_planet"] == "Saturn"
