# Why your latitude matters

**Goal:** see how differently the same sky behaves from different places, and
stop assuming your own is normal.

---

## Run

```python
import datetime as dt
from moonfield import observer, time as mtime
from moonfield.location import Location

places = [
    Location(78.22,  15.65, "Longyearbyen", "Arctic/Longyearbyen"),
    Location(51.48,  -0.00, "Greenwich",    "Europe/London"),
    Location(-0.18, -78.47, "Quito",        "America/Guayaquil"),
    Location(-33.87, 151.21, "Sydney",      "Australia/Sydney"),
    Location(-54.80, -68.30, "Ushuaia",     "America/Argentina/Ushuaia"),
]

when = dt.datetime(2026, 6, 21, tzinfo=mtime.UTC)
for place in places:
    rs = observer.sun_rise_set(place, when)
    print(f"{place.name:14s} {rs.describe()}")
```

On the June solstice: Longyearbyen has no sunset at all, Ushuaia gets about
seven hours of daylight, and Quito gets twelve, as it does every single day of
the year.

---

## The rules that follow from latitude alone

**Maximum solar altitude at noon:**

```
altitude = 90° − |latitude − declination|
```

At Greenwich in June: 90 − |51.5 − 23.4| = 61.9°. In December: 15.1°. A
threefold difference in how directly sunlight arrives, which is what
[module 06](../06-seasons/) is about.

**Circumpolar stars.** Objects with declination greater than 90° − |latitude|
never set. At the pole, nothing rises or sets at all; the whole sky just
rotates horizontally. At the equator, everything rises and sets, and every star
in the sky is visible over a year.

**Which way the Sun goes.** In the northern hemisphere the Sun crosses the sky
to the *south*, moving left to right. In the southern hemisphere it crosses to
the *north*, moving right to left. Southern-hemisphere sundials run backwards.

**The Moon's crescent tips the other way.** A waxing crescent is lit on the
right in the north, on the left in the south. Near the equator it can look like
a bowl, lit underneath.

`phase.ascii_moon()` takes a hemisphere argument for exactly this reason.

---

## Why this module exists

Most astronomy writing is quietly northern and quietly mid-latitude. It says
"the Sun is due south at noon" and "Orion is a winter constellation" without
noticing these are local facts.

Moonfield tries not to do that. If you find a place where it slips, that is a
documentation bug worth reporting.

## Checkpoint

- [ ] I can compute noon solar altitude from latitude and declination
- [ ] I know what circumpolar means and can compute the limit for my latitude
- [ ] I know which way the Sun travels from my hemisphere
- [ ] I can explain why crescent orientation flips

## Try it yourself

1. Compute daylight length on both solstices for your latitude, and for the
   opposite one
2. Find the lowest declination star that is circumpolar from your location
3. Find the latitude where the Sun is exactly overhead today

Next: [Module 06, Seasons](../06-seasons/).
