"""Where the Sun is.

The Sun is the easiest body to check your work against, because you can see
whether it is up without any equipment at all.

Strictly speaking the Sun does not orbit Earth -- Earth orbits the Sun. But if
you want to know where to *look*, what matters is the direction from you to the
Sun, and that is identical either way. Treating Earth as fixed and the Sun as
moving is a change of viewpoint, not a mistake.

Accuracy
--------
The series below is Meeus's low-precision solar theory (chapter 25). It is good
to roughly 0.01 degrees -- about a fiftieth of the Sun's own width -- for dates
within a few centuries of today. That is far better than you can measure by eye,
and much worse than a professional ephemeris. See ``docs/background`` for what
we left out.
"""

from __future__ import annotations

import datetime as _dt
import math
from dataclasses import dataclass

from moonfield import time as mtime

__all__ = ["SunPosition", "position", "apparent_longitude", "declination", "equation_of_time"]


@dataclass(frozen=True)
class SunPosition:
    """The Sun's position at one instant, in several coordinate systems."""

    julian_day: float
    apparent_longitude: float   # ecliptic longitude, degrees
    right_ascension: float      # degrees, 0-360
    declination: float          # degrees, +north
    distance_au: float          # Earth-Sun distance in astronomical units
    equation_of_time: float     # minutes; apparent solar time minus mean

    @property
    def distance_km(self) -> float:
        return self.distance_au * 149_597_870.7

    @property
    def angular_diameter(self) -> float:
        """Apparent diameter of the Sun's disc, in degrees."""
        return 2 * math.degrees(math.atan(696_000.0 / self.distance_km))


def position(when: _dt.datetime | float | None = None) -> SunPosition:
    """Compute the Sun's apparent geocentric position.

    ``when`` may be a datetime, a Julian Day number, or None for "now".
    """
    jd = when if isinstance(when, (int, float)) else mtime.julian_day(when)
    t = mtime.julian_centuries(jd)

    # Geometric mean longitude: where the Sun would be if Earth's orbit were a
    # perfect circle travelled at constant speed.
    l0 = (280.46646 + 36000.76983 * t + 0.0003032 * t * t) % 360.0

    # Mean anomaly: how far Earth has gone around its orbit since perihelion,
    # again pretending the motion is uniform.
    m = 357.52911 + 35999.05029 * t - 0.0001537 * t * t
    m_rad = math.radians(m)

    # Eccentricity of Earth's orbit -- how far from circular it is.
    e = 0.016708634 - 0.000042037 * t - 0.0000001267 * t * t

    # Equation of the centre: the correction from the pretend uniform motion to
    # the real motion along an ellipse. Earth moves faster when it is closer.
    c = (
        (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m_rad)
        + (0.019993 - 0.000101 * t) * math.sin(2 * m_rad)
        + 0.000289 * math.sin(3 * m_rad)
    )

    true_longitude = l0 + c
    true_anomaly = m + c

    # Radius vector: the actual Earth-Sun distance right now.
    radius = (1.000001018 * (1 - e * e)) / (
        1 + e * math.cos(math.radians(true_anomaly))
    )

    # Apparent longitude corrects for nutation and for aberration -- the small
    # tilt caused by Earth's own motion, the same effect that makes rain seem
    # to slant when you run through it.
    omega = math.radians(125.04 - 1934.136 * t)
    lambda_app = true_longitude - 0.00569 - 0.00478 * math.sin(omega)

    epsilon = mtime.mean_obliquity(jd) + 0.00256 * math.cos(omega)
    eps_rad = math.radians(epsilon)
    lam_rad = math.radians(lambda_app)

    ra = math.degrees(
        math.atan2(math.cos(eps_rad) * math.sin(lam_rad), math.cos(lam_rad))
    ) % 360.0
    dec = math.degrees(math.asin(math.sin(eps_rad) * math.sin(lam_rad)))

    eot = _equation_of_time(t, l0, m_rad, e, eps_rad)

    return SunPosition(
        julian_day=jd,
        apparent_longitude=lambda_app % 360.0,
        right_ascension=ra,
        declination=dec,
        distance_au=radius,
        equation_of_time=eot,
    )


def _equation_of_time(
    t: float, l0: float, m_rad: float, e: float, eps_rad: float
) -> float:
    """Equation of time in minutes (Meeus chapter 28).

    This is the gap between the Sun and a well-behaved clock. It comes from two
    things at once: Earth's orbit is elliptical (so the Sun runs fast in January
    and slow in July), and Earth's axis is tilted (so the Sun's daily motion is
    not always parallel to the equator). Together they can put real solar noon
    up to about 16 minutes away from clock noon.
    """
    y = math.tan(eps_rad / 2) ** 2
    l0_rad = math.radians(l0)
    eot_rad = (
        y * math.sin(2 * l0_rad)
        - 2 * e * math.sin(m_rad)
        + 4 * e * y * math.sin(m_rad) * math.cos(2 * l0_rad)
        - 0.5 * y * y * math.sin(4 * l0_rad)
        - 1.25 * e * e * math.sin(2 * m_rad)
    )
    return math.degrees(eot_rad) * 4.0  # 1 degree of rotation = 4 minutes


def apparent_longitude(when: _dt.datetime | float | None = None) -> float:
    """The Sun's apparent ecliptic longitude in degrees -- used for phases."""
    return position(when).apparent_longitude


def declination(when: _dt.datetime | float | None = None) -> float:
    """The Sun's declination in degrees.

    This single number drives the seasons. It swings between about +23.44 in
    June and -23.44 in December, and it equals the latitude at which the Sun
    passes directly overhead that day.
    """
    return position(when).declination


def equation_of_time(when: _dt.datetime | float | None = None) -> float:
    """Minutes by which apparent solar time leads mean solar time."""
    return position(when).equation_of_time
