# Solstices and equinoxes

**Goal:** compute the four turning points yourself, to the minute.

---

## Definitions that are more precise than you think

These are **instants**, not days:

| Event | Definition |
|---|---|
| March equinox | Sun's apparent longitude reaches 0° |
| June solstice | reaches 90° |
| September equinox | reaches 180° |
| December solstice | reaches 270° |

Not "the day with equal light and dark" — that is close, but not the
definition, and not even quite true (see below).

## Compute them

```python
import datetime as dt
from moonfield import sun, time as mtime

def find_event(year, target_longitude):
    """Bisect for the instant the Sun's apparent longitude hits the target."""
    lo = dt.datetime(year, 1, 1, tzinfo=mtime.UTC)
    hi = lo + dt.timedelta(days=366)

    def offset(when):
        lon = sun.apparent_longitude(when)
        return ((lon - target_longitude + 180) % 360) - 180

    # coarse scan for the sign change
    step = dt.timedelta(hours=6)
    when = lo
    while when < hi:
        if offset(when) < 0 <= offset(when + step):
            lo, hi = when, when + step
            break
        when += step

    for _ in range(60):
        mid = lo + (hi - lo) / 2
        if offset(mid) < 0:
            lo = mid
        else:
            hi = mid
    return lo

for name, lon in [("March equinox", 0), ("June solstice", 90),
                  ("September equinox", 180), ("December solstice", 270)]:
    print(f"{name:20s} {find_event(2026, lon):%Y-%m-%d %H:%M} UTC")
```

Check against a published almanac. You should be within a couple of minutes.

## Why the dates drift

The tropical year is 365.2422 days, not 365. That quarter-day is why the events
drift about six hours later each year and jump back on leap years — and why the
Gregorian calendar exists at all. The 400-year rule (skip the leap year in 1900
and 2100 but not 2000) tracks 365.2422 to within about 27 seconds a year.

## The equinox is not equal day and night

"Equinox" means equal night, but equal daylight actually falls a few days
*earlier* in spring and *later* in autumn. Two reasons, both from
[module 05](../05-local-sky/altitude-and-azimuth.md):

- Sunrise and sunset are defined by the Sun's **upper limb**, not its centre
- **Refraction** lifts the Sun about 0.57° at the horizon

Together these add several minutes of daylight at both ends. Check it:

```bash
moonfield sun --date 2026-03-20
```

Daylight will be slightly over 12 hours. The date of true 12-hour daylight is
called the equilux, and it depends on your latitude.

## Checkpoint

- [ ] I know the four events are defined by solar longitude
- [ ] I have computed them and checked against an almanac
- [ ] I know why the dates shift year to year
- [ ] I can explain why the equinox is not exactly equal day and night

## Try it yourself

1. Compute all four for the year you were born
2. Find the equilux date for your latitude
3. Measure the interval between successive March equinoxes — that is the
   tropical year, and you just measured it
4. Compare the lengths of the four seasons. They are not equal — why not?

That last one is a good one. The answer involves Kepler's second law.

Next: [Module 07 — Planets](../07-planets/) (planned).
