"""Turning sky coordinates into "look over there".

Right ascension and declination describe where something is *on the celestial
sphere*. They are the same for everyone on Earth. They are also useless for
actually finding anything, because they do not tell you which way to turn your
head.

Horizontal coordinates fix that:

* **Azimuth** -- the compass bearing, measured clockwise from north.
  North 0, east 90, south 180, west 270.
* **Altitude** -- the angle above the horizon. 0 is on the horizon, 90 is
  straight up, negative means it is below the horizon and you cannot see it.

These depend on where you are and what time it is, which is why every function
here needs a :class:`~moonfield.location.Location`.
"""

from __future__ import annotations

import datetime as _dt
import math
from collections.abc import Callable
from dataclasses import dataclass

from moonfield import moon as moon_engine
from moonfield import sun as sun_engine
from moonfield import time as mtime
from moonfield.location import Location

__all__ = [
    "Horizontal",
    "RiseSet",
    "to_horizontal",
    "sun_position",
    "moon_position",
    "rise_set",
    "cardinal",
    "refraction",
    "angular_separation",
]

#: Standard altitude at which the Sun is considered to rise or set.
#: The disc's centre sits 0.833 degrees below the true horizon at that moment:
#: about 0.267 for the radius of the disc, and about 0.567 because the
#: atmosphere bends light and lifts the image.
SUN_HORIZON = -0.8333

#: Twilight thresholds, in degrees of Sun altitude.
CIVIL_TWILIGHT = -6.0
NAUTICAL_TWILIGHT = -12.0
ASTRONOMICAL_TWILIGHT = -18.0

_COMPASS = (
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
)


@dataclass(frozen=True)
class Horizontal:
    """A direction in the observer's own sky."""

    azimuth: float      # degrees clockwise from north
    altitude: float     # degrees above the horizon
    hour_angle: float   # degrees; 0 means on the meridian, due south/north

    @property
    def compass(self) -> str:
        return cardinal(self.azimuth)

    @property
    def is_up(self) -> bool:
        return self.altitude > 0.0

    def describe(self) -> str:
        state = "above" if self.is_up else "below"
        return (
            f"azimuth {self.azimuth:.1f} deg ({self.compass}), "
            f"altitude {self.altitude:+.1f} deg ({state} the horizon)"
        )


@dataclass(frozen=True)
class RiseSet:
    """Rise, transit and set times for one body on one day."""

    rise: _dt.datetime | None
    transit: _dt.datetime | None
    setting: _dt.datetime | None
    transit_altitude: float | None
    always_up: bool = False
    never_up: bool = False

    @property
    def note(self) -> str | None:
        if self.always_up:
            return "never sets today at this latitude"
        if self.never_up:
            return "never rises today at this latitude"
        return None

    def describe(self, zone: str | _dt.tzinfo | None = None) -> str:
        """One line summarising the day, in local civil time.

        Handles the polar cases first, because at high latitudes "rises at
        X, sets at Y" is not merely unknown -- it is the wrong shape of
        answer. Midnight sun and polar night are correct results, not
        missing data.
        """
        if self.always_up:
            return f"Up all day -- {self.note}."
        if self.never_up:
            return f"Down all day -- {self.note}."

        parts = []
        if self.rise is not None:
            parts.append(f"rises {mtime.to_zone(self.rise, zone):%H:%M}")
        if self.transit is not None:
            highest = ""
            if self.transit_altitude is not None:
                highest = f" ({self.transit_altitude:.0f} deg)"
            parts.append(
                f"highest {mtime.to_zone(self.transit, zone):%H:%M}{highest}"
            )
        if self.setting is not None:
            parts.append(f"sets {mtime.to_zone(self.setting, zone):%H:%M}")

        if not parts:
            return "No rise, transit or set found for this day."
        return ", ".join(parts).capitalize() + "."


def cardinal(azimuth: float) -> str:
    """Convert an azimuth in degrees to a 16-point compass name."""
    index = int((azimuth % 360.0) / 22.5 + 0.5) % 16
    return _COMPASS[index]


def refraction(true_altitude: float) -> float:
    """Extra apparent altitude in degrees caused by the atmosphere.

    Air is denser near the ground, so light from a low object bends downward
    and the object looks higher than it is. At the horizon the effect is about
    half a degree -- roughly the width of the Sun. It is the reason you can
    still see the Sun for a couple of minutes after it has geometrically set.

    Bennett's formula, as given in Meeus chapter 16.
    """
    if true_altitude < -2.0:
        return 0.0
    h = true_altitude
    return (
        1.02 / math.tan(math.radians(h + 10.3 / (h + 5.11))) / 60.0
    )


def to_horizontal(
    right_ascension: float,
    declination: float,
    location: Location,
    when: _dt.datetime | float | None = None,
) -> Horizontal:
    """Convert equatorial coordinates to the observer's horizon frame.

    The bridge between the two frames is *local sidereal time*: the right
    ascension that is currently crossing your meridian, the imaginary line
    running from due north, through the point overhead, to due south.

    The hour angle is then simply "how far past the meridian is it", and the
    rest is spherical trigonometry.
    """
    jd = when if isinstance(when, (int, float)) else mtime.julian_day(when)
    lst = mtime.lst_degrees(jd, location.longitude)
    hour_angle = (lst - right_ascension + 180.0) % 360.0 - 180.0

    h_rad = math.radians(hour_angle)
    dec_rad = math.radians(declination)
    lat_rad = location.latitude_rad

    sin_alt = math.sin(dec_rad) * math.sin(lat_rad) + math.cos(dec_rad) * math.cos(
        lat_rad
    ) * math.cos(h_rad)
    altitude = math.degrees(math.asin(max(-1.0, min(1.0, sin_alt))))

    # atan2 form: measured from south, so add 180 to get the usual
    # from-north convention.
    azimuth = math.degrees(
        math.atan2(
            math.sin(h_rad),
            math.cos(h_rad) * math.sin(lat_rad) - math.tan(dec_rad) * math.cos(lat_rad),
        )
    )
    azimuth = (azimuth + 180.0) % 360.0

    return Horizontal(azimuth=azimuth, altitude=altitude, hour_angle=hour_angle)


def sun_position(
    location: Location, when: _dt.datetime | float | None = None
) -> Horizontal:
    """Where the Sun is in your sky right now."""
    jd = when if isinstance(when, (int, float)) else mtime.julian_day(when)
    pos = sun_engine.position(jd)
    return to_horizontal(pos.right_ascension, pos.declination, location, jd)


def moon_position(
    location: Location, when: _dt.datetime | float | None = None
) -> Horizontal:
    """Where the Moon is in your sky right now.

    Includes the parallax correction. The Moon is close enough that standing on
    a different part of Earth genuinely shifts it against the stars -- by up to
    about a degree, twice its own width.
    """
    jd = when if isinstance(when, (int, float)) else mtime.julian_day(when)
    pos = moon_engine.position(jd)
    topo = to_horizontal(pos.right_ascension, pos.declination, location, jd)

    # Geocentric formulae assume you are at Earth's centre. You are not; you are
    # on the surface, one Earth radius off to the side. For the Moon that shifts
    # the apparent position downward by parallax * cos(altitude).
    shift = pos.parallax * math.cos(math.radians(topo.altitude))
    return Horizontal(
        azimuth=topo.azimuth,
        altitude=topo.altitude - shift,
        hour_angle=topo.hour_angle,
    )


# ---------------------------------------------------------------------------
# Rise, transit, set
# ---------------------------------------------------------------------------


def rise_set(
    altitude_of: Callable[[float], float],
    location: Location,
    when: _dt.datetime | None = None,
    horizon: float = SUN_HORIZON,
    step_minutes: int = 10,
) -> RiseSet:
    """Find rise, transit and set by sampling and then narrowing down.

    There are closed-form equations for this, but they assume the body does not
    move during the day -- fine for a star, poor for the Moon, which shifts
    about 13 degrees between one sunset and the next.

    So we do it the honest way instead:

    1. Walk through the local day in ten-minute steps, recording the altitude.
    2. Wherever the altitude crosses the horizon, we have trapped a rise or a
       set between two known samples.
    3. Bisect that interval until it is under a second wide.

    This is slower, and it does not care how complicated the body's motion is.
    ``altitude_of`` takes a Julian Day and returns an altitude in degrees.
    """
    day_start = _local_midnight(location, when)
    jd_start = mtime.julian_day(day_start)
    steps = int(24 * 60 / step_minutes) + 1
    dt_days = step_minutes / 1440.0

    samples = [
        (jd_start + i * dt_days, altitude_of(jd_start + i * dt_days))
        for i in range(steps)
    ]

    rise_jd: float | None = None
    set_jd: float | None = None
    for (jd_a, alt_a), (jd_b, alt_b) in zip(samples, samples[1:], strict=False):
        if alt_a < horizon <= alt_b and rise_jd is None:
            rise_jd = _bisect(altitude_of, jd_a, jd_b, horizon)
        elif alt_a >= horizon > alt_b and set_jd is None:
            set_jd = _bisect(altitude_of, jd_a, jd_b, horizon)

    # Transit is the highest point of the day: refine around the best sample.
    best_index = max(range(len(samples)), key=lambda i: samples[i][1])
    transit_jd, transit_alt = _refine_maximum(
        altitude_of,
        samples[max(0, best_index - 1)][0],
        samples[min(len(samples) - 1, best_index + 1)][0],
    )

    altitudes = [alt for _, alt in samples]
    always_up = rise_jd is None and set_jd is None and min(altitudes) > horizon
    never_up = rise_jd is None and set_jd is None and max(altitudes) <= horizon

    return RiseSet(
        rise=mtime.from_julian_day(rise_jd) if rise_jd else None,
        transit=mtime.from_julian_day(transit_jd) if not never_up else None,
        setting=mtime.from_julian_day(set_jd) if set_jd else None,
        transit_altitude=transit_alt if not never_up else None,
        always_up=always_up,
        never_up=never_up,
    )


def _bisect(
    altitude_of: Callable[[float], float],
    low: float,
    high: float,
    horizon: float,
    tolerance: float = 1.0 / 86400.0,
) -> float:
    """Narrow a bracketed horizon crossing down to about one second."""
    f_low = altitude_of(low) - horizon
    for _ in range(60):
        if high - low < tolerance:
            break
        mid = (low + high) / 2
        f_mid = altitude_of(mid) - horizon
        if (f_low < 0) == (f_mid < 0):
            low, f_low = mid, f_mid
        else:
            high = mid
    return (low + high) / 2


def _refine_maximum(
    altitude_of: Callable[[float], float], low: float, high: float
) -> tuple[float, float]:
    """Golden-section search for the highest altitude in an interval."""
    ratio = (math.sqrt(5) - 1) / 2
    a, b = low, high
    c = b - ratio * (b - a)
    d = a + ratio * (b - a)
    for _ in range(50):
        if abs(b - a) < 1.0 / 86400.0:
            break
        if altitude_of(c) > altitude_of(d):
            b, d = d, c
            c = b - ratio * (b - a)
        else:
            a, c = c, d
            d = a + ratio * (b - a)
    peak = (a + b) / 2
    return peak, altitude_of(peak)


def _local_midnight(location: Location, when: _dt.datetime | None = None) -> _dt.datetime:
    """The start of the local civil day containing ``when``."""
    instant = mtime.ensure_utc(when)
    local = instant.astimezone(location.zone)
    midnight = local.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.astimezone(mtime.UTC)


def sun_rise_set(
    location: Location, when: _dt.datetime | None = None, horizon: float = SUN_HORIZON
) -> RiseSet:
    """Sunrise, solar noon and sunset for the local day containing ``when``."""

    def altitude(jd: float) -> float:
        return sun_position(location, jd).altitude

    return rise_set(altitude, location, when, horizon=horizon)


def moon_rise_set(location: Location, when: _dt.datetime | None = None) -> RiseSet:
    """Moonrise, lunar transit and moonset for the local day containing ``when``.

    The Moon's own horizon altitude is +0.125 degrees rather than the Sun's
    -0.833, because parallax (already applied in :func:`moon_position`) pushes
    it the other way.
    """

    def altitude(jd: float) -> float:
        return moon_position(location, jd).altitude

    return rise_set(altitude, location, when, horizon=0.125)


def angular_separation(
    az1: float, alt1: float, az2: float, alt2: float
) -> float:
    """Angle between two directions in the sky, in degrees.

    Useful for "I predicted the Moon would be *there* and it was *here*" --
    this turns that into a single number you can argue about.
    """
    a1, h1, a2, h2 = map(math.radians, (az1, alt1, az2, alt2))
    cos_sep = math.sin(h1) * math.sin(h2) + math.cos(h1) * math.cos(h2) * math.cos(
        a1 - a2
    )
    return math.degrees(math.acos(max(-1.0, min(1.0, cos_sep))))
