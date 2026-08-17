"""Your first script: where are the Sun and Moon right now?

Run it:
    python examples/01_hello_sky.py

Every line here is something you will meet again in the curriculum.
"""

from moonfield import observer, phase
from moonfield import time as mtime
from moonfield.location import load_location

# Load the location you saved with `moonfield config set-location`.
here = load_location()
now = mtime.utc_now()

print(f"{here.describe()}")
print(f"{mtime.format_instant(now, here.zone)}\n")

sun = observer.sun_position(here, now)
moon = observer.moon_position(here, now)

# Altitude below zero means the object is under your horizon.
print(f"Sun   {sun.altitude:+6.1f} deg altitude   {sun.azimuth:6.1f} deg azimuth "
      f"({observer.cardinal(sun.azimuth)})")
print(f"Moon  {moon.altitude:+6.1f} deg altitude   {moon.azimuth:6.1f} deg azimuth "
      f"({observer.cardinal(moon.azimuth)})")

info = phase.compute(now)
print(f"\nMoon is {info.name.lower()}, {info.illumination * 100:.1f}% lit, "
      f"{info.age_days:.1f} days old.")

if moon.altitude > 0:
    print("It is above your horizon right now. Go and look.")
else:
    rs = observer.moon_rise_set(here, now)
    print(f"It is below your horizon. {rs.describe()}")
