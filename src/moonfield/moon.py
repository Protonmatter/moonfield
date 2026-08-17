"""Where the Moon is.

The Moon is much harder than the Sun. Earth pulls on it, the Sun pulls on it,
and the two pulls compete in a way that has no exact solution. What we have
instead is a *series*: a long sum of sine waves, each one a named wobble, that
together reproduce the real motion to whatever accuracy you are willing to type
in.

This module uses a truncated form of the ELP-2000/82 theory as tabulated in
Meeus, *Astronomical Algorithms*, chapter 47.

Accuracy and what we truncated
------------------------------
The full table has 60 terms for longitude and distance and 60 for latitude. We
keep the largest 35 and 30 of them respectively.

Against Meeus's own worked example 47.a, what that costs is about 2 arcseconds
of position and 12 km of distance, and ``tests/test_accuracy_claims.py``
measures exactly that rather than taking this comment's word for it.

Do not read 2 arcseconds as a guarantee. Each dropped term is under about
0.002 degrees on its own, but there are 25 of them, and on a day when several
happen to peak together the error can reach a few tens of arcseconds. That is
still around a thousandth of the Moon's own width, so you will never see it by
eye. You *can* see it against a professional ephemeris, which is exactly the
kind of discrepancy this project wants you to notice and explain.
"""

from __future__ import annotations

import datetime as _dt
import math
from dataclasses import dataclass

from moonfield import time as mtime

__all__ = ["MoonPosition", "position", "ecliptic_longitude"]


# Periodic terms for longitude (Sigma l) and distance (Sigma r).
# Columns: multiple of D, M, M', F, then the longitude coefficient in units of
# 1e-6 degrees, then the distance coefficient in units of 1e-3 km.
_TERMS_LR: tuple[tuple[int, int, int, int, int, int], ...] = (
    (0, 0, 1, 0, 6288774, -20905355),
    (2, 0, -1, 0, 1274027, -3699111),
    (2, 0, 0, 0, 658314, -2955968),
    (0, 0, 2, 0, 213618, -569925),
    (0, 1, 0, 0, -185116, 48888),
    (0, 0, 0, 2, -114332, -3149),
    (2, 0, -2, 0, 58793, 246158),
    (2, -1, -1, 0, 57066, -152138),
    (2, 0, 1, 0, 53322, -170733),
    (2, -1, 0, 0, 45758, -204586),
    (0, 1, -1, 0, -40923, -129620),
    (1, 0, 0, 0, -34720, 108743),
    (0, 1, 1, 0, -30383, 104755),
    (2, 0, 0, -2, 15327, 10321),
    (0, 0, 1, 2, -12528, 0),
    (0, 0, 1, -2, 10980, 79661),
    (4, 0, -1, 0, 10675, -34782),
    (0, 0, 3, 0, 10034, -23210),
    (4, 0, -2, 0, 8548, -21636),
    (2, 1, -1, 0, -7888, 24208),
    (2, 1, 0, 0, -6766, 30824),
    (1, 0, -1, 0, -5163, -8379),
    (1, 1, 0, 0, 4987, -16675),
    (2, -1, 1, 0, 4036, -12831),
    (2, 0, 2, 0, 3994, -10445),
    (4, 0, 0, 0, 3861, -11650),
    (2, 0, -3, 0, 3665, 14403),
    (0, 1, -2, 0, -2689, -7003),
    (2, 0, -1, 2, -2602, 0),
    (2, -1, -2, 0, 2390, 10056),
    (1, 0, 1, 0, -2348, 6322),
    (2, -2, 0, 0, 2236, -9884),
    (0, 1, 2, 0, -2120, 5751),
    (0, 2, 0, 0, -2069, 0),
    (2, -2, -1, 0, 2048, -4950),
)

# Periodic terms for latitude (Sigma b), coefficient in units of 1e-6 degrees.
_TERMS_B: tuple[tuple[int, int, int, int, int], ...] = (
    (0, 0, 0, 1, 5128122),
    (0, 0, 1, 1, 280602),
    (0, 0, 1, -1, 277693),
    (2, 0, 0, -1, 173237),
    (2, 0, -1, 1, 55413),
    (2, 0, -1, -1, 46271),
    (2, 0, 0, 1, 32573),
    (0, 0, 2, 1, 17198),
    (2, 0, 1, -1, 9266),
    (0, 0, 2, -1, 8822),
    (2, -1, 0, -1, 8216),
    (2, 0, -2, -1, 4324),
    (2, 0, 1, 1, 4200),
    (2, 1, 0, -1, -3359),
    (2, -1, -1, 1, 2463),
    (2, -1, 0, 1, 2211),
    (2, -1, -1, -1, 2065),
    (0, 1, -1, -1, -1870),
    (4, 0, -1, -1, 1828),
    (0, 1, 0, 1, -1794),
    (0, 0, 0, 3, -1749),
    (0, 1, -1, 1, -1565),
    (1, 0, 0, 1, -1491),
    (0, 1, 1, 1, -1475),
    (0, 1, 1, -1, -1410),
    (0, 1, 0, -1, -1344),
    (1, 0, 0, -1, -1335),
    (0, 0, 3, 1, 1107),
    (4, 0, 0, -1, 1021),
    (4, 0, -1, 1, 833),
)


@dataclass(frozen=True)
class MoonPosition:
    """The Moon's geocentric position at one instant."""

    julian_day: float
    ecliptic_longitude: float   # degrees
    ecliptic_latitude: float    # degrees
    distance_km: float
    right_ascension: float      # degrees, 0-360
    declination: float          # degrees
    parallax: float             # equatorial horizontal parallax, degrees

    @property
    def angular_diameter(self) -> float:
        """Apparent diameter of the Moon's disc, in degrees."""
        return 2 * math.degrees(math.atan(1737.4 / self.distance_km))


def position(when: _dt.datetime | float | None = None) -> MoonPosition:
    """Compute the Moon's apparent geocentric position.

    ``when`` may be a datetime, a Julian Day number, or None for "now".
    """
    jd = when if isinstance(when, (int, float)) else mtime.julian_day(when)
    t = mtime.julian_centuries(jd)

    # --- The five fundamental arguments -----------------------------------
    # Each is an angle that grows almost uniformly with time. Every periodic
    # term below is a sine or cosine of some whole-number combination of them.

    # Moon's mean longitude: where the Moon would be with no perturbations.
    lp = (
        218.3164477
        + 481267.88123421 * t
        - 0.0015786 * t * t
        + t**3 / 538841.0
        - t**4 / 65194000.0
    ) % 360.0

    # Mean elongation: the Moon's angular distance from the Sun. This is the
    # argument that governs the phases -- 0 at new Moon, 180 at full.
    d = (
        297.8501921
        + 445267.1114034 * t
        - 0.0018819 * t * t
        + t**3 / 545868.0
        - t**4 / 113065000.0
    ) % 360.0

    # Sun's mean anomaly: where Earth is in its own elliptical orbit.
    m = (357.5291092 + 35999.0502909 * t - 0.0001536 * t * t + t**3 / 24490000.0) % 360.0

    # Moon's mean anomaly: where the Moon is in its elliptical orbit.
    mp = (
        134.9633964
        + 477198.8675055 * t
        + 0.0087414 * t * t
        + t**3 / 69699.0
        - t**4 / 14712000.0
    ) % 360.0

    # Argument of latitude: how far the Moon is from the node where its tilted
    # orbit crosses the ecliptic. This governs eclipses.
    f = (
        93.2720950
        + 483202.0175233 * t
        - 0.0036539 * t * t
        - t**3 / 3526000.0
        + t**4 / 863310000.0
    ) % 360.0

    # Eccentricity correction: Earth's orbit is slowly becoming less elliptical,
    # so terms that depend on the Sun's anomaly need a slow scaling.
    e = 1 - 0.002516 * t - 0.0000074 * t * t

    d_r, m_r, mp_r, f_r = map(math.radians, (d, m, mp, f))

    sum_l = 0.0
    sum_r = 0.0
    for cd, cm, cmp, cf, coef_l, coef_r in _TERMS_LR:
        arg = cd * d_r + cm * m_r + cmp * mp_r + cf * f_r
        scale = e ** abs(cm)
        sum_l += coef_l * scale * math.sin(arg)
        sum_r += coef_r * scale * math.cos(arg)

    sum_b = 0.0
    for cd, cm, cmp, cf, coef_b in _TERMS_B:
        arg = cd * d_r + cm * m_r + cmp * mp_r + cf * f_r
        sum_b += coef_b * (e ** abs(cm)) * math.sin(arg)

    # --- Additive corrections ---------------------------------------------
    # A1 is the action of Venus, A2 the action of Jupiter, A3 a flattening
    # effect. Small, but they are the largest things left over.
    a1 = math.radians((119.75 + 131.849 * t) % 360.0)
    a2 = math.radians((53.09 + 479264.290 * t) % 360.0)
    a3 = math.radians((313.45 + 481266.484 * t) % 360.0)
    lp_r = math.radians(lp)

    sum_l += 3958 * math.sin(a1) + 1962 * math.sin(lp_r - f_r) + 318 * math.sin(a2)
    sum_b += (
        -2235 * math.sin(lp_r)
        + 382 * math.sin(a3)
        + 175 * math.sin(a1 - f_r)
        + 175 * math.sin(a1 + f_r)
        + 127 * math.sin(lp_r - mp_r)
        - 115 * math.sin(lp_r + mp_r)
    )

    longitude = (lp + sum_l / 1_000_000.0) % 360.0
    latitude = sum_b / 1_000_000.0
    distance = 385000.56 + sum_r / 1000.0
    parallax = math.degrees(math.asin(6378.14 / distance))

    # Apparent longitude includes the nutation wobble of Earth's axis.
    d_psi, _ = mtime.nutation(jd)
    apparent_longitude = (longitude + d_psi) % 360.0

    eps = math.radians(mtime.true_obliquity(jd))
    lam = math.radians(apparent_longitude)
    beta = math.radians(latitude)

    ra = math.degrees(
        math.atan2(
            math.sin(lam) * math.cos(eps) - math.tan(beta) * math.sin(eps),
            math.cos(lam),
        )
    ) % 360.0
    dec = math.degrees(
        math.asin(
            math.sin(beta) * math.cos(eps)
            + math.cos(beta) * math.sin(eps) * math.sin(lam)
        )
    )

    return MoonPosition(
        julian_day=jd,
        ecliptic_longitude=apparent_longitude,
        ecliptic_latitude=latitude,
        distance_km=distance,
        right_ascension=ra,
        declination=dec,
        parallax=parallax,
    )


def ecliptic_longitude(when: _dt.datetime | float | None = None) -> float:
    """The Moon's apparent ecliptic longitude in degrees."""
    return position(when).ecliptic_longitude
