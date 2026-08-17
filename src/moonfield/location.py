"""Where you are standing.

Almost every question about the sky is really a question about the sky *from
somewhere*. "Is the Moon up?" has no answer until you say where you are.

This module holds the :class:`Location` record and the small configuration
file that saves it, so you type your coordinates once instead of on every
command.

Sign conventions used everywhere in Moonfield
---------------------------------------------
* Latitude:  north positive, south negative.  Sydney is about -33.87.
* Longitude: **east positive**, west negative.  New York is about -74.0.

The east-positive convention is what modern astronomy and every mapping tool
uses. Some older navigation texts use west-positive, which is a rich source of
"my answer is mirrored" confusion -- so we state it loudly here.
"""

from __future__ import annotations

import json
import math
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from moonfield import time as mtime

__all__ = ["Location", "config_path", "load_location", "save_location", "parse_coordinate"]


@dataclass(frozen=True)
class Location:
    """An observing site on Earth."""

    latitude: float
    longitude: float
    name: str = "your location"
    timezone: str | None = None
    elevation_m: float = 0.0

    def __post_init__(self) -> None:
        if not -90.0 <= self.latitude <= 90.0:
            raise ValueError(
                f"latitude {self.latitude} is out of range: it must be between "
                "-90 (South Pole) and +90 (North Pole)"
            )
        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError(
                f"longitude {self.longitude} is out of range: it must be between "
                "-180 and +180, with east positive"
            )

    # -- derived conveniences -------------------------------------------------

    @property
    def latitude_rad(self) -> float:
        return math.radians(self.latitude)

    @property
    def longitude_rad(self) -> float:
        return math.radians(self.longitude)

    @property
    def hemisphere(self) -> str:
        if self.latitude > 0:
            return "northern"
        if self.latitude < 0:
            return "southern"
        return "equatorial"

    @property
    def zone(self):
        """The tzinfo to use when displaying civil time here."""
        return mtime.resolve_zone(self.timezone)

    def describe(self) -> str:
        """A one-line human summary, e.g. ``Lisbon (38.7223N, 9.1393W)``."""
        ns = "N" if self.latitude >= 0 else "S"
        ew = "E" if self.longitude >= 0 else "W"
        return (
            f"{self.name} ({abs(self.latitude):.4f}{ns}, "
            f"{abs(self.longitude):.4f}{ew})"
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Location:
        return cls(
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
            name=str(data.get("name", "your location")),
            timezone=data.get("timezone"),
            elevation_m=float(data.get("elevation_m", 0.0)),
        )


# ---------------------------------------------------------------------------
# Coordinate parsing
# ---------------------------------------------------------------------------

_DMS = re.compile(
    r"""^\s*
    (?P<sign>[+-])?
    (?P<deg>\d+(?:\.\d+)?)
    (?:\s*[°d:\s]\s*(?P<min>\d+(?:\.\d+)?))?
    (?:\s*['m:\s]\s*(?P<sec>\d+(?:\.\d+)?))?
    \s*["s]?\s*
    (?P<hemi>[NSEWnsew])?
    \s*$""",
    re.VERBOSE,
)


def parse_coordinate(text: str) -> float:
    """Parse a latitude or longitude written in any of the usual ways.

    All of these mean the same thing::

        -33.8688
        33.8688 S
        33 52 7.7 S
        33°52'07.7"S

    Returns signed decimal degrees, north/east positive.
    """
    raw = str(text).strip()
    if not raw:
        raise ValueError("empty coordinate")

    match = _DMS.match(raw)
    if not match:
        raise ValueError(
            f"could not read the coordinate {text!r}. Try a decimal number "
            "like -33.8688, or a form like 33 52 7.7 S"
        )

    degrees = float(match.group("deg"))
    degrees += float(match.group("min") or 0.0) / 60.0
    degrees += float(match.group("sec") or 0.0) / 3600.0

    hemi = (match.group("hemi") or "").upper()
    sign = -1.0 if match.group("sign") == "-" else 1.0
    if hemi in ("S", "W"):
        if sign < 0:
            raise ValueError(
                f"{text!r} is ambiguous: it has both a minus sign and a "
                f"{hemi} hemisphere letter. Use one or the other."
            )
        sign = -1.0
    return sign * degrees


# ---------------------------------------------------------------------------
# Configuration file
# ---------------------------------------------------------------------------


def config_path() -> Path:
    """Where Moonfield keeps your saved location.

    Honours ``MOONFIELD_CONFIG`` if set (handy for tests and for classrooms
    with shared machines), then the XDG config directory on Linux/macOS and
    ``%APPDATA%`` on Windows.
    """
    override = os.environ.get("MOONFIELD_CONFIG")
    if override:
        return Path(override).expanduser()

    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "moonfield" / "config.json"


def load_config() -> dict:
    """Read the configuration file, returning ``{}`` when there is none."""
    path = config_path()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(data: dict) -> Path:
    """Write the configuration file, creating parent directories as needed."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def load_location() -> Location | None:
    """Return the saved observing location, or None if none has been set."""
    data = load_config().get("location")
    if not isinstance(data, dict):
        return None
    try:
        return Location.from_dict(data)
    except (KeyError, ValueError, TypeError):
        return None


def save_location(location: Location) -> Path:
    """Persist an observing location for future commands."""
    config = load_config()
    config["location"] = location.to_dict()
    return save_config(config)
