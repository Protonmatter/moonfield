"""Tides -- applied Earth-Moon physics, and a lesson in model limits.

.. warning::

   **Nothing in this module is safe for navigation.** It is a teaching model.
   It does not know about the shape of your coastline, the depth of your bay,
   or the weather. Errors of several hours and several metres are normal and
   expected. For anything that matters, use your national hydrographic office.

That warning is not boilerplate -- it is the point of the module.

The equilibrium model
---------------------
Imagine Earth covered by a uniform ocean with no continents. The Moon's gravity
pulls harder on the near side of Earth than on the far side. That *difference*
in pull -- not the pull itself -- stretches the ocean into two bulges, one
facing the Moon and one directly away from it.

Earth rotates through both bulges each day, so most coasts get two high tides
and two low tides. Because the Moon has also moved along its orbit, it takes
about 24 hours 50 minutes to bring the Moon back overhead: the *lunar day*.
That is why the tide is roughly 50 minutes later each day.

Where it breaks
---------------
Real ocean basins are not uniform, and water cannot flow fast enough to keep up
with the bulge anyway. Real tides are better described as waves sloshing around
basins, with periods set by the size and depth of the basin. The consequences:

* Some places have one high tide a day, not two.
* Some places have almost no tide at all (parts of the Mediterranean).
* Some have enormous tides because the basin resonates (Bay of Fundy, 16 m).
* High tide almost never happens exactly when the Moon is overhead. The
  characteristic local lag is called the *lunitidal interval*, and it can be
  anything from minutes to many hours.

We expose the lunitidal interval as a knob you set yourself, from observation.
Discovering that you need it -- and how big it is where you live -- is the
lesson.
"""

from __future__ import annotations

import datetime as _dt
import math
from dataclasses import dataclass, field

from moonfield import moon as moon_engine
from moonfield import phase as phase_engine
from moonfield import time as mtime
from moonfield.location import Location

__all__ = [
    "TideEvent",
    "TideEstimate",
    "lunar_day_hours",
    "spring_neap",
    "rough",
    "compare",
    "LUNAR_DAY_HOURS",
]

#: Mean length of the lunar day, in hours: 24 h 50.47 min.
LUNAR_DAY_HOURS = 24.8412

#: Ratio of the Sun's tide-raising force to the Moon's.
#: The Sun is vastly more massive but much further away, and the tidal effect
#: falls off as the *cube* of distance, so the Sun ends up the junior partner.
SOLAR_TIDAL_RATIO = 0.46


@dataclass(frozen=True)
class TideEvent:
    """One predicted high or low water."""

    when: _dt.datetime
    kind: str  # "high" or "low"
    driver: str  # which bulge: "Moon overhead" or "Moon underfoot"

    def local(self, location: Location) -> _dt.datetime:
        return self.when.astimezone(location.zone)


@dataclass
class TideEstimate:
    """The rough model's output for one place and time."""

    location: Location
    when: _dt.datetime
    events: list[TideEvent]
    state: str                  # "rising" or "falling"
    fraction: float             # 0 at low water, 1 at high water
    hours_to_next: float
    next_event: TideEvent | None
    spring_neap_label: str
    range_factor: float         # 1.0 = mean, >1 spring, <1 neap
    lunitidal_interval: float
    moon_transit: _dt.datetime | None = None
    notes: list[str] = field(default_factory=list)


def lunar_day_hours() -> float:
    """Length of the lunar day in hours.

    A solar day is 24 hours: Earth turns once relative to the Sun. But while
    Earth turns, the Moon moves roughly 13 degrees further along its orbit, so
    Earth has to turn about 13 degrees extra to bring the Moon back overhead.
    13 degrees at 15 degrees per hour is about 50 minutes.
    """
    return LUNAR_DAY_HOURS


def spring_neap(when: _dt.datetime | float | None = None) -> tuple[float, str]:
    """How big the tides are this week, and what to call it.

    Returns ``(range_factor, label)`` where the factor is relative to a mean
    tide: about 1.32 at springs, about 0.68 at neaps.

    At new and full Moon the Sun and Moon pull along the same line and their
    bulges add together -- *spring* tides, nothing to do with the season. At the
    quarters they pull at right angles and partly cancel -- *neap* tides.

    Note the factor of two in ``cos(2 * elongation)``: the tidal pattern repeats
    twice per orbit, because a bulge pointing at the Moon and a bulge pointing
    away from it are equally good at lining up with the Sun.
    """
    elong = phase_engine.elongation(when)
    e = math.radians(elong)
    r = SOLAR_TIDAL_RATIO
    combined = math.sqrt(1 + r * r + 2 * r * math.cos(2 * e))
    factor = combined  # normalised so mean-ish is ~1.0

    offset = min(elong % 180.0, 180.0 - (elong % 180.0))
    if offset < 30.0:
        label = "spring tides (large range)"
    elif offset > 60.0:
        label = "neap tides (small range)"
    else:
        label = "between springs and neaps"
    return factor, label


# ---------------------------------------------------------------------------
# Finding when the Moon crosses the meridian
# ---------------------------------------------------------------------------


def _moon_hour_angle(location: Location, jd: float) -> float:
    """Moon's hour angle in degrees, wrapped to -180..+180.

    0 means the Moon is due south (northern hemisphere) or due north
    (southern) -- crossing the observer's meridian, at its highest.
    180 means it is on the opposite meridian, underfoot.
    """
    pos = moon_engine.position(jd)
    lst = mtime.lst_degrees(jd, location.longitude)
    return (lst - pos.right_ascension + 180.0) % 360.0 - 180.0


def _find_transits(
    location: Location, centre_jd: float, span_days: float = 1.6
) -> list[tuple[float, str]]:
    """Times when the Moon crosses the upper or lower meridian.

    Returns a list of ``(julian_day, "upper"|"lower")`` sorted by time.
    """
    step = 10.0 / 1440.0  # ten minutes
    start = centre_jd - span_days
    count = int(2 * span_days / step) + 1

    results: list[tuple[float, str]] = []
    prev_jd = start
    prev_ha = _moon_hour_angle(location, start)

    for i in range(1, count):
        jd = start + i * step
        ha = _moon_hour_angle(location, jd)

        # Upper transit: hour angle passes through zero going up.
        if prev_ha < 0 <= ha and abs(ha - prev_ha) < 180:
            results.append((_bisect_hour_angle(location, prev_jd, jd, 0.0), "upper"))
        # Lower transit: hour angle wraps from +180 to -180.
        elif prev_ha > 90 and ha < -90:
            results.append((_bisect_wrap(location, prev_jd, jd), "lower"))

        prev_jd, prev_ha = jd, ha

    return sorted(results)


def _bisect_hour_angle(
    location: Location, low: float, high: float, target: float
) -> float:
    for _ in range(40):
        if high - low < 1.0 / 86400.0:
            break
        mid = (low + high) / 2
        if _moon_hour_angle(location, mid) < target:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def _bisect_wrap(location: Location, low: float, high: float) -> float:
    """Narrow down the moment the hour angle wraps past 180 degrees."""
    for _ in range(40):
        if high - low < 1.0 / 86400.0:
            break
        mid = (low + high) / 2
        if _moon_hour_angle(location, mid) > 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2


# ---------------------------------------------------------------------------
# The rough model
# ---------------------------------------------------------------------------


def rough(
    location: Location,
    when: _dt.datetime | None = None,
    lunitidal_interval: float = 0.0,
) -> TideEstimate:
    """A deliberately crude tide estimate, for learning only.

    ``lunitidal_interval`` is the local lag in hours between the Moon crossing
    your meridian and high water actually arriving. Leave it at 0 to see the
    pure equilibrium model; set it from your own observations, or from a
    published value for your port, to see how much of the error it explains.
    """
    instant = mtime.ensure_utc(when)
    jd = mtime.julian_day(instant)

    transits = _find_transits(location, jd)
    lag = lunitidal_interval / 24.0

    events: list[TideEvent] = []
    for transit_jd, kind in transits:
        high_jd = transit_jd + lag
        driver = "Moon overhead" if kind == "upper" else "Moon underfoot"
        events.append(TideEvent(mtime.from_julian_day(high_jd), "high", driver))
        # Low water sits a quarter of a lunar day after each high.
        low_jd = high_jd + (LUNAR_DAY_HOURS / 4) / 24.0
        events.append(
            TideEvent(mtime.from_julian_day(low_jd), "low", f"quarter cycle after {driver}")
        )

    events.sort(key=lambda e: e.when)

    future = [e for e in events if e.when > instant]
    next_event = future[0] if future else None
    past = [e for e in events if e.when <= instant]
    last_event = past[-1] if past else None

    if next_event and last_event:
        span = (next_event.when - last_event.when).total_seconds() / 3600.0
        gone = (instant - last_event.when).total_seconds() / 3600.0
        progress = gone / span if span else 0.0
        if last_event.kind == "low":
            state, fraction = "rising", progress
        else:
            state, fraction = "falling", 1.0 - progress
    else:
        state, fraction = "unknown", 0.5

    hours_to_next = (
        (next_event.when - instant).total_seconds() / 3600.0 if next_event else float("nan")
    )

    factor, label = spring_neap(jd)
    upper = [t for t, k in transits if k == "upper"]
    nearest_transit = (
        mtime.from_julian_day(min(upper, key=lambda t: abs(t - jd))) if upper else None
    )

    notes = [
        "This is the equilibrium (two-bulge) model. It is a teaching tool, "
        "not a navigational prediction.",
        "It ignores coastline shape, water depth, basin resonance, friction, "
        "wind and air pressure.",
    ]
    if lunitidal_interval == 0.0:
        notes.append(
            "The lunitidal interval is set to 0, so this assumes high water "
            "arrives exactly when the Moon is overhead. Almost nowhere on Earth "
            "does that. Measure your local lag and pass it with --interval."
        )

    return TideEstimate(
        location=location,
        when=instant,
        events=events,
        state=state,
        fraction=max(0.0, min(1.0, fraction)),
        hours_to_next=hours_to_next,
        next_event=next_event,
        spring_neap_label=label,
        range_factor=factor,
        lunitidal_interval=lunitidal_interval,
        moon_transit=nearest_transit,
        notes=notes,
    )


def compare(
    estimate: TideEstimate, observed: list[_dt.datetime], kind: str = "high"
) -> list[dict]:
    """Match predicted events against real observed or published times.

    For each observed time, find the nearest predicted event of the same kind
    and report the gap. A consistent one-directional gap is your lunitidal
    interval showing up; a scattered gap means something else is going on.
    """
    predicted = [e for e in estimate.events if e.kind == kind]
    rows = []
    for actual in observed:
        actual_utc = mtime.ensure_utc(actual)
        if not predicted:
            rows.append({"observed": actual_utc, "predicted": None, "delta_hours": None})
            continue
        best = min(
            predicted, key=lambda e: abs((e.when - actual_utc).total_seconds())
        )
        delta = (best.when - actual_utc).total_seconds() / 3600.0
        rows.append(
            {
                "observed": actual_utc,
                "predicted": best.when,
                "delta_hours": delta,
                "driver": best.driver,
            }
        )
    return rows


def suggested_interval(rows: list[dict]) -> float | None:
    """Average lag implied by a set of comparisons, in hours.

    If every predicted high water is consistently early by the same amount,
    that amount *is* the lunitidal interval for that port. Feeding it back in
    is the single biggest improvement you can make to this model.
    """
    deltas = [r["delta_hours"] for r in rows if r.get("delta_hours") is not None]
    if not deltas:
        return None
    return -sum(deltas) / len(deltas)
