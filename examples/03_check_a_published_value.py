"""Validate Moonfield against numbers someone else published.

This is the habit the whole curriculum is trying to build: never trust a
model until you have checked it against something independent.

    python examples/03_check_a_published_value.py
"""

import datetime as dt

from moonfield import phase, sun
from moonfield import time as mtime

# New Moon times published by national almanac offices, in UTC.
PUBLISHED_NEW_MOONS = [
    (dt.datetime(2026, 1, 18, 19, 52, tzinfo=mtime.UTC), "18 Jan 2026"),
    (dt.datetime(2026, 3, 19, 1, 23, tzinfo=mtime.UTC), "19 Mar 2026"),
    (dt.datetime(2026, 8, 12, 17, 37, tzinfo=mtime.UTC), "12 Aug 2026"),
]

print("New Moon: published vs computed\n")
print(f"{'published':<16} {'illumination':>13} {'computed new Moon':<22} {'error':>9}")
print("-" * 66)

for published, label in PUBLISHED_NEW_MOONS:
    info = phase.compute(published)

    # Search backwards a little, then forward, for the true new Moon.
    computed = phase.next_phase(published - dt.timedelta(days=2), 0.0)
    error_minutes = (computed - published).total_seconds() / 60

    print(f"{label:<16} {info.illumination * 100:11.3f} %  "
          f"{computed:%Y-%m-%d %H:%M} UTC     {error_minutes:+6.1f} m")

# Meeus, Astronomical Algorithms, example 25.a
print("\n\nSun position against Meeus example 25.a (JD 2448908.5)\n")
when = mtime.from_julian_day(2448908.5)
position = sun.position(when)

for name, computed, expected in [
    ("apparent longitude", position.apparent_longitude, 199.90895),
    ("right ascension", position.right_ascension, 198.38083),
    ("declination", position.declination, -7.78507),
]:
    print(f"  {name:<20} {computed:12.5f}   textbook {expected:12.5f}   "
          f"diff {computed - expected:+.5f}")

print(
    "\nDifferences of a few units in the fifth decimal are rounding in the\n"
    "textbook's own printed intermediate values, not error in the method."
)
