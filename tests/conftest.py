"""Shared test fixtures.

The important one is ``isolated_config``: it points MOONFIELD_CONFIG at a
temporary file for every test, so running the suite can never read or clobber
the real configuration of whoever is running it.
"""

import pytest

from moonfield.location import Location


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Give every test its own throwaway config file."""
    monkeypatch.setenv("MOONFIELD_CONFIG", str(tmp_path / "config.json"))
    return tmp_path / "config.json"


@pytest.fixture
def greenwich():
    return Location(51.4779, -0.0015, "Greenwich", "Europe/London")


@pytest.fixture
def sydney():
    return Location(-33.8688, 151.2093, "Sydney", "Australia/Sydney")


@pytest.fixture
def saved_greenwich(greenwich):
    from moonfield.location import save_location

    save_location(greenwich)
    return greenwich
