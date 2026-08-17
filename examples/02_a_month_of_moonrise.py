"""How much later does the Moon rise each night?

The usual answer is "about 50 minutes". Run this and see how much that
figure actually varies; the spread is the interesting part, not the mean.

    python examples/02_a_month_of_moonrise.py
"""

import datetime as dt

from moonfield import observer
from moonfield import time as mtime
from moonfield.location import load_location

here = load_location()
start = dt.datetime.now(mtime.UTC).replace(hour=0, minute=0, second=0, microsecond=0)

previous = None
gaps = []

print(f"{here.name}, moonrise, one lunar month\n")
print(f"{'date':<12} {'moonrise (UTC)':<16} {'later by':>10}")
print("-" * 40)

for day in range(30):
    when = start + dt.timedelta(days=day)
    rs = observer.moon_rise_set(here, when)

    if rs.rise is None:
        # At high latitudes, or when moonrise skips a calendar day, there
        # simply is no rise. That is a real result, not a failure.
        print(f"{when:%Y-%m-%d} {'(no moonrise)':<16}")
        previous = None
        continue

    if previous is None:
        gap = ""
    else:
        minutes = (rs.rise - previous).total_seconds() / 60 - 24 * 60
        gaps.append(minutes)
        gap = f"{minutes:+6.0f} min"

    print(f"{when:%Y-%m-%d} {rs.rise:%H:%M:%S}        {gap:>10}")
    previous = rs.rise

if gaps:
    print("-" * 40)
    print(f"mean {sum(gaps) / len(gaps):+.0f} min   "
          f"min {min(gaps):+.0f}   max {max(gaps):+.0f}")
    print(
        "\nThe spread is the Harvest Moon effect. The retardation depends on the\n"
        "angle the Moon's path makes with your horizon, which changes through the\n"
        "year and with your latitude. Try this from a different latitude and watch\n"
        "the spread shrink towards the equator."
    )
