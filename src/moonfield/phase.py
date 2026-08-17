"""What phase is the Moon in?

This module deliberately contains **two** models of the same thing, because
comparing them is the whole lesson.

``simple_phase``
    The clock model. Pick a date when we know there was a new Moon, count how
    many days have passed, divide by 29.53. You could do it on paper. It is
    usually right to within a few hours.

``compute``
    The geometry model. Work out where the Sun actually is, work out where the
    Moon actually is, and measure the angle between them as seen from Earth.
    Slower to explain, but it knows about the Moon's elliptical orbit, so it
    does not drift.

The difference between the two is not an error to be hidden. It is the reason
the Moon's orbit is interesting, and ``moonfield phase --explain`` shows you
both numbers side by side.
"""

from __future__ import annotations

import datetime as _dt
import math
from dataclasses import dataclass, field

from moonfield import moon, sun
from moonfield import time as mtime

__all__ = [
    "PhaseInfo",
    "compute",
    "simple_phase",
    "phase_name",
    "elongation",
    "next_phase",
    "PRIMARY_PHASES",
]

#: A new Moon that actually happened, used as the anchor for the simple model.
#: 2000 January 6 at 18:14 UTC.
REFERENCE_NEW_MOON = 2451550.259722

#: The four phases that are *instants* rather than stretches of time.
PRIMARY_PHASES: tuple[tuple[float, str], ...] = (
    (0.0, "New Moon"),
    (90.0, "First Quarter"),
    (180.0, "Full Moon"),
    (270.0, "Last Quarter"),
)

#: How close to a primary phase we still call it by that name, in degrees.
#: 9 degrees is about three quarters of a day of the Moon's motion.
PRIMARY_TOLERANCE = 9.0


@dataclass
class PhaseInfo:
    """Everything ``moonfield phase`` knows about one instant."""

    julian_day: float
    when: _dt.datetime
    elongation: float          # Moon minus Sun in ecliptic longitude, degrees
    phase_angle: float         # Sun-Moon-Earth angle, degrees
    illumination: float        # lit fraction of the visible disc, 0 to 1
    age_days: float            # time since the last true new Moon
    simple_age_days: float     # the same, from the clock model
    name: str
    waxing: bool
    distance_km: float
    angular_diameter: float
    next_phases: dict = field(default_factory=dict)

    @property
    def illumination_percent(self) -> float:
        return self.illumination * 100.0

    @property
    def model_disagreement_hours(self) -> float:
        """How far apart the two models are, in hours."""
        return (self.simple_age_days - self.age_days) * 24.0


# ---------------------------------------------------------------------------
# Model 1: the clock
# ---------------------------------------------------------------------------


def simple_phase(when: _dt.datetime | float | None = None) -> tuple[float, float]:
    """The beginner model: count days since a known new Moon.

    Returns ``(age_in_days, illuminated_fraction)``.

    The reasoning fits in one sentence: the Moon goes through its phases every
    29.53 days on average, so if you know one date when it was new, you can get
    to any other date by counting.

    The word doing the work there is *average*. The Moon's orbit is an ellipse,
    so it speeds up and slows down; individual cycles run from about 29.27 to
    29.83 days. Over a single month the error stays under about half a day.
    """
    jd = when if isinstance(when, (int, float)) else mtime.julian_day(when)
    age = (jd - REFERENCE_NEW_MOON) % mtime.SYNODIC_MONTH
    # A circle traced at constant speed, projected onto the line of sight.
    illumination = (1 - math.cos(2 * math.pi * age / mtime.SYNODIC_MONTH)) / 2
    return age, illumination


# ---------------------------------------------------------------------------
# Model 2: the geometry
# ---------------------------------------------------------------------------


def elongation(when: _dt.datetime | float | None = None) -> float:
    """Angle from the Sun to the Moon along the ecliptic, 0-360 degrees.

    0 means the Moon is in the same direction as the Sun -- new Moon.
    180 means it is opposite the Sun -- full Moon.
    The number always increases with time, which makes it easy to search.
    """
    jd = when if isinstance(when, (int, float)) else mtime.julian_day(when)
    return (moon.ecliptic_longitude(jd) - sun.apparent_longitude(jd)) % 360.0


def phase_name(elongation_deg: float, tolerance: float = PRIMARY_TOLERANCE) -> str:
    """Name the phase for a given elongation."""
    e = elongation_deg % 360.0
    for target, name in PRIMARY_PHASES:
        offset = abs(((e - target + 180.0) % 360.0) - 180.0)
        if offset <= tolerance:
            return name
    if e < 90.0:
        return "Waxing Crescent"
    if e < 180.0:
        return "Waxing Gibbous"
    if e < 270.0:
        return "Waning Gibbous"
    return "Waning Crescent"


def compute(when: _dt.datetime | float | None = None) -> PhaseInfo:
    """Full phase information for an instant, using real positions."""
    jd = when if isinstance(when, (int, float)) else mtime.julian_day(when)
    instant = mtime.from_julian_day(jd)

    sun_pos = sun.position(jd)
    moon_pos = moon.position(jd)

    elong = (moon_pos.ecliptic_longitude - sun_pos.apparent_longitude) % 360.0

    # Geocentric elongation measured properly on the sphere, not just along
    # the ecliptic -- this accounts for the Moon being off the ecliptic plane.
    ra_s, dec_s = map(math.radians, (sun_pos.right_ascension, sun_pos.declination))
    ra_m, dec_m = map(math.radians, (moon_pos.right_ascension, moon_pos.declination))
    cos_psi = math.sin(dec_s) * math.sin(dec_m) + math.cos(dec_s) * math.cos(
        dec_m
    ) * math.cos(ra_s - ra_m)
    psi = math.acos(max(-1.0, min(1.0, cos_psi)))

    # Phase angle: the Sun-Moon-Earth angle. This is what actually decides how
    # much of the lit half we can see, and it is *not* the same as elongation,
    # because the Sun is not infinitely far away.
    r_km = sun_pos.distance_km
    delta = moon_pos.distance_km
    phase_angle = math.atan2(
        r_km * math.sin(psi), delta - r_km * math.cos(psi)
    )

    illumination = (1 + math.cos(phase_angle)) / 2

    simple_age, _ = simple_phase(jd)
    true_age = jd - _previous_phase_jd(jd, 0.0)

    return PhaseInfo(
        julian_day=jd,
        when=instant,
        elongation=elong,
        phase_angle=math.degrees(phase_angle),
        illumination=illumination,
        age_days=true_age,
        simple_age_days=simple_age,
        name=phase_name(elong),
        waxing=elong < 180.0,
        distance_km=delta,
        angular_diameter=moon_pos.angular_diameter,
        next_phases=_next_primary_phases(jd),
    )


# ---------------------------------------------------------------------------
# Finding the moments when phases happen
# ---------------------------------------------------------------------------

#: Mean rate at which the elongation grows, in degrees per day.
_MEAN_RATE = 360.0 / mtime.SYNODIC_MONTH


def _signed_offset(jd: float, target: float) -> float:
    """Elongation minus target, wrapped to the range -180..+180."""
    return ((elongation(jd) - target + 180.0) % 360.0) - 180.0


def _refine(guess: float, target: float, iterations: int = 12) -> float:
    """Newton's method on the elongation, using the known mean rate.

    We are solving "at what time is the elongation exactly ``target``?".
    Because the elongation grows at a well-known average rate, dividing the
    current error by that rate gives a very good step, and three or four
    iterations already land within a second.
    """
    jd = guess
    for _ in range(iterations):
        offset = _signed_offset(jd, target)
        step = offset / _MEAN_RATE
        jd -= step
        if abs(step) < 1e-7:  # about a hundredth of a second
            break
    return jd


def next_phase(
    when: _dt.datetime | float | None = None, target: float = 0.0
) -> _dt.datetime:
    """The next time the elongation reaches ``target`` degrees, after ``when``."""
    jd = when if isinstance(when, (int, float)) else mtime.julian_day(when)
    offset = _signed_offset(jd, target)
    # How far short of the target we are, in days, then step forward.
    days_ahead = (-offset % 360.0) / _MEAN_RATE
    if days_ahead < 1e-6:
        days_ahead = mtime.SYNODIC_MONTH
    result = _refine(jd + days_ahead, target)
    if result <= jd:
        result = _refine(jd + days_ahead + mtime.SYNODIC_MONTH / 4, target)
    return mtime.from_julian_day(result)


def _previous_phase_jd(jd: float, target: float) -> float:
    """The most recent time before ``jd`` that the elongation hit ``target``."""
    offset = _signed_offset(jd, target)
    days_back = (offset % 360.0) / _MEAN_RATE
    result = _refine(jd - days_back, target)
    if result > jd:
        result = _refine(jd - days_back - mtime.SYNODIC_MONTH / 4, target)
    return result


def _next_primary_phases(jd: float) -> dict:
    """Upcoming new / first quarter / full / last quarter, in time order."""
    upcoming = []
    for target, name in PRIMARY_PHASES:
        moment = next_phase(jd, target)
        upcoming.append((moment, name, (mtime.julian_day(moment) - jd)))
    upcoming.sort(key=lambda item: item[0])
    return {name: (moment, days) for moment, name, days in upcoming}


# ---------------------------------------------------------------------------
# Drawing the Moon in a terminal
# ---------------------------------------------------------------------------


def ascii_moon(
    illumination: float, waxing: bool, size: int = 11, southern: bool = False
) -> str:
    """Draw the lit portion of the Moon using text characters.

    The terminator -- the line between lit and unlit -- is the edge of a circle
    seen at an angle, so it is an *ellipse*, not a straight line. That is why
    a half Moon has a straight edge but a crescent has a curved one.

    Seen from the southern hemisphere the Moon appears upside down relative to
    the north, so a waxing Moon is lit on the opposite side. Pass
    ``southern=True`` to flip it.
    """
    illumination = max(0.0, min(1.0, illumination))
    radius = size / 2.0
    lit_on_right = waxing != southern

    # Half-width of the terminator ellipse, from -1 (fully left) to +1.
    terminator = 1.0 - 2.0 * illumination

    rows = []
    for row in range(size):
        y = (row + 0.5 - radius) / radius
        line = []
        for col in range(size * 2):
            x = (col + 0.5 - size) / size
            if x * x + y * y > 1.0:
                line.append(" ")
                continue
            # Horizontal extent of the disc at this height.
            edge = math.sqrt(max(0.0, 1.0 - y * y))
            boundary = terminator * edge
            if lit_on_right:
                is_lit = x >= boundary
            else:
                is_lit = x <= -boundary
            line.append("#" if is_lit else ".")
        rows.append("".join(line).rstrip())
    return "\n".join(rows)
