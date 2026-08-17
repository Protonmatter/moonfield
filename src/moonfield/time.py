"""Time handling for Moonfield.

Astronomy needs an *unambiguous instant*. "3 o'clock" is not one: it depends
on where you are and what time of year it is. This module converts civil time
(the kind on your phone) into the representations the maths actually needs.

Project convention
------------------
Compute using an unambiguous time representation (UTC / Julian Day);
display local civil time where useful.

Note on the module name
-----------------------
This file is called ``time.py``, the same as a Python standard-library module.
That is safe: Python 3 uses *absolute* imports by default, so ``import time``
anywhere else in the program still finds the standard library. Inside this
package we always write ``from moonfield import time as mtime``.
"""

from __future__ import annotations

import datetime as _dt
import math
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

__all__ = [
    "UTC",
    "J2000",
    "utc_now",
    "ensure_utc",
    "to_zone",
    "resolve_zone",
    "local_zone_name",
    "parse_datetime",
    "julian_day",
    "julian_centuries",
    "from_julian_day",
    "gmst_degrees",
    "lst_degrees",
    "nutation",
    "true_obliquity",
    "format_instant",
    "format_duration",
]

UTC = _dt.timezone.utc

#: The J2000.0 epoch: 2000 January 1 at 12:00 TT, as a Julian Day number.
#: Nearly every modern astronomical series is measured from this instant.
J2000 = 2451545.0

#: Mean length of the synodic month (new Moon to new Moon), in days.
SYNODIC_MONTH = 29.530588853

#: Mean length of the sidereal month (Moon returns to the same star), in days.
SIDEREAL_MONTH = 27.321661547


# ---------------------------------------------------------------------------
# Getting hold of an instant
# ---------------------------------------------------------------------------


def utc_now() -> _dt.datetime:
    """Return the current instant as a timezone-aware UTC datetime."""
    return _dt.datetime.now(tz=UTC)


def ensure_utc(when: _dt.datetime | None = None) -> _dt.datetime:
    """Return ``when`` as a timezone-aware UTC datetime.

    A datetime with no timezone attached is *naive* -- it does not identify a
    real instant. Rather than guess, we treat a naive input as UTC and say so
    in the documentation, because silently assuming the local timezone is the
    classic source of "my answer is off by a few hours" bugs.
    """
    if when is None:
        return utc_now()
    if when.tzinfo is None:
        return when.replace(tzinfo=UTC)
    return when.astimezone(UTC)


def resolve_zone(name: str | None) -> _dt.tzinfo:
    """Look up an IANA timezone such as ``Europe/Lisbon``.

    Falls back to the system's local timezone when ``name`` is None, and to
    UTC when the name is not in the system's timezone database.
    """
    if name is None:
        return _dt.datetime.now().astimezone().tzinfo or UTC
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, ModuleNotFoundError):
        return UTC


def local_zone_name() -> str:
    """Best-effort name of the machine's local timezone, for display."""
    tz = _dt.datetime.now().astimezone().tzinfo
    key = getattr(tz, "key", None)
    if key:
        return str(key)
    return _dt.datetime.now().astimezone().strftime("%Z") or "local"


def to_zone(when: _dt.datetime, zone: str | _dt.tzinfo | None) -> _dt.datetime:
    """Convert an instant into a particular timezone for display."""
    tz = zone if isinstance(zone, _dt.tzinfo) else resolve_zone(zone)
    return ensure_utc(when).astimezone(tz)


def parse_datetime(text: str, zone: str | _dt.tzinfo | None = None) -> _dt.datetime:
    """Parse a date or date-and-time string into a UTC instant.

    Accepted forms::

        2026-08-16                  -> that date at 00:00 in ``zone``
        2026-08-16 21:30            -> that local time in ``zone``
        2026-08-16T21:30            -> same, ISO 'T' separator
        2026-08-16T21:30:05
        2026-08-16T21:30:05Z        -> explicit UTC
        2026-08-16T21:30+01:00      -> explicit offset

    ``zone`` supplies the timezone for the forms that do not carry one.
    """
    raw = text.strip()
    if not raw:
        raise ValueError("empty date string")

    explicit_offset = raw.endswith("Z") or _has_offset(raw)
    candidate = raw[:-1] + "+00:00" if raw.endswith("Z") else raw

    parsed: _dt.datetime | None = None
    try:
        parsed = _dt.datetime.fromisoformat(candidate)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                parsed = _dt.datetime.strptime(candidate, fmt)
                break
            except ValueError:
                continue
    if parsed is None:
        raise ValueError(
            f"could not understand the date {text!r}. "
            "Try a form like 2026-08-16 or 2026-08-16T21:30"
        )

    if parsed.tzinfo is None and not explicit_offset:
        parsed = parsed.replace(tzinfo=resolve_zone(zone) if not isinstance(zone, _dt.tzinfo) else zone)
    return ensure_utc(parsed)


def _has_offset(raw: str) -> bool:
    """True when an ISO string carries a trailing ``+HH:MM`` / ``-HH:MM``."""
    tail = raw[10:] if len(raw) > 10 else ""
    return "+" in tail or tail.count("-") > 0


# ---------------------------------------------------------------------------
# Julian Day
# ---------------------------------------------------------------------------


def julian_day(when: _dt.datetime | None = None) -> float:
    """Convert an instant to a Julian Day number.

    A Julian Day is just "days elapsed since a fixed moment in 4713 BC", as a
    single decimal number. Calendars have months of unequal length, leap years
    and a gap where the Gregorian reform happened; a plain running count of
    days has none of those problems, so every formula downstream uses it.

    The algorithm is the standard one from Meeus, *Astronomical Algorithms*,
    chapter 7, valid for any Gregorian-calendar date.
    """
    moment = ensure_utc(when)
    year = moment.year
    month = moment.month
    day = (
        moment.day
        + moment.hour / 24.0
        + moment.minute / 1440.0
        + (moment.second + moment.microsecond / 1e6) / 86400.0
    )

    # January and February are counted as months 13 and 14 of the previous
    # year, which makes the leap-day land at the end of the "year".
    if month <= 2:
        year -= 1
        month += 12

    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)  # Gregorian calendar correction

    return (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + day
        + b
        - 1524.5
    )


def from_julian_day(jd: float) -> _dt.datetime:
    """Convert a Julian Day number back into a UTC datetime."""
    jd = jd + 0.5
    z = math.floor(jd)
    f = jd - z

    if z < 2299161:
        a = z
    else:
        alpha = math.floor((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - math.floor(alpha / 4)

    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d = math.floor(365.25 * c)
    e = math.floor((b - d) / 30.6001)

    day_frac = b - d - math.floor(30.6001 * e) + f
    day = int(math.floor(day_frac))
    month = int(e - 1 if e < 14 else e - 13)
    year = int(c - 4716 if month > 2 else c - 4715)

    seconds = (day_frac - day) * 86400.0
    base = _dt.datetime(year, month, day, tzinfo=UTC)
    return base + _dt.timedelta(seconds=seconds)


def julian_centuries(jd: float) -> float:
    """Julian centuries elapsed since J2000.0 -- the ``T`` in every series."""
    return (jd - J2000) / 36525.0


# ---------------------------------------------------------------------------
# Sidereal time: where the sky has rotated to
# ---------------------------------------------------------------------------


def gmst_degrees(jd: float) -> float:
    """Greenwich Mean Sidereal Time, in degrees.

    Sidereal time is the clock the *sky* keeps. A sidereal day (one rotation
    relative to the stars) is about 3 minutes 56 seconds shorter than a solar
    day, because Earth also moves along its orbit and has to turn slightly
    further to point back at the Sun.

    Meeus, chapter 12, formula 12.4.
    """
    t = julian_centuries(jd)
    theta = (
        280.46061837
        + 360.98564736629 * (jd - J2000)
        + 0.000387933 * t * t
        - (t * t * t) / 38710000.0
    )
    return theta % 360.0


def lst_degrees(jd: float, longitude_east: float) -> float:
    """Local Mean Sidereal Time in degrees, for an east-positive longitude."""
    return (gmst_degrees(jd) + longitude_east) % 360.0


# ---------------------------------------------------------------------------
# Nutation and obliquity
# ---------------------------------------------------------------------------


def nutation(jd: float) -> tuple[float, float]:
    """Return (nutation in longitude, nutation in obliquity) in degrees.

    Earth's axis wobbles slightly as the Moon tugs on the equatorial bulge.
    The effect is small -- under 20 arcseconds -- but it is the difference
    between a "mean" and an "apparent" sky position.

    Low-precision form from Meeus, chapter 22 (accurate to ~0.5 arcsecond).
    """
    t = julian_centuries(jd)
    omega = math.radians(125.04452 - 1934.136261 * t)
    l_sun = math.radians(280.4665 + 36000.7698 * t)
    l_moon = math.radians(218.3165 + 481267.8813 * t)

    d_psi = (
        -17.20 * math.sin(omega)
        - 1.32 * math.sin(2 * l_sun)
        - 0.23 * math.sin(2 * l_moon)
        + 0.21 * math.sin(2 * omega)
    ) / 3600.0
    d_eps = (
        9.20 * math.cos(omega)
        + 0.57 * math.cos(2 * l_sun)
        + 0.10 * math.cos(2 * l_moon)
        - 0.09 * math.cos(2 * omega)
    ) / 3600.0
    return d_psi, d_eps


def mean_obliquity(jd: float) -> float:
    """Mean obliquity of the ecliptic in degrees -- Earth's axial tilt."""
    t = julian_centuries(jd)
    seconds = 21.448 - t * (46.8150 + t * (0.00059 - t * 0.001813))
    return 23.0 + (26.0 + seconds / 60.0) / 60.0


def true_obliquity(jd: float) -> float:
    """Obliquity including nutation, in degrees."""
    return mean_obliquity(jd) + nutation(jd)[1]


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def format_instant(when: _dt.datetime, zone: str | _dt.tzinfo | None = None) -> str:
    """Format an instant as local civil time with its UTC equivalent."""
    utc = ensure_utc(when)
    local = to_zone(utc, zone)
    label = local.strftime("%Z") or "local"
    return (
        f"{local.strftime('%Y-%m-%d %H:%M')} {label}"
        f"  ({utc.strftime('%Y-%m-%d %H:%M')} UTC)"
    )


def format_duration(days: float) -> str:
    """Turn a duration in days into something a human reads at a glance."""
    total_minutes = int(round(abs(days) * 1440))
    d, rem = divmod(total_minutes, 1440)
    h, m = divmod(rem, 60)
    parts = []
    if d:
        parts.append(f"{d} day{'s' if d != 1 else ''}")
    if h:
        parts.append(f"{h} hour{'s' if h != 1 else ''}")
    if m or not parts:
        parts.append(f"{m} minute{'s' if m != 1 else ''}")
    return " ".join(parts)
