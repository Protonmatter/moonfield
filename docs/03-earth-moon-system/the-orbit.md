# The orbit is not a circle

**Goal:** see the Moon's varying distance in real data, and work out what a
"supermoon" is actually worth.

---

## Run

```python
import datetime as dt
from moonfield import moon, time as mtime

start = dt.datetime(2026, 1, 1, tzinfo=mtime.UTC)
distances = []
for day in range(60):
    when = start + dt.timedelta(days=day)
    distances.append((when, moon.position(when).distance_km))

near = min(distances, key=lambda x: x[1])
far  = max(distances, key=lambda x: x[1])
print(f"perigee {near[0]:%Y-%m-%d}  {near[1]:,.0f} km")
print(f"apogee  {far[0]:%Y-%m-%d}  {far[1]:,.0f} km")
print(f"ratio   {far[1] / near[1]:.3f}")
```

Perigee ~356,500 km, apogee ~406,700 km. About a 12% variation.

## What follows from it

**Apparent size** varies by the same 12% — 0.49° to 0.56°.

**Speed** varies too: fastest at perigee, slowest at apogee (Kepler's second
law). This is the direct cause of the up-to-half-a-day disagreement between the
two phase models in [module 02](../02-moon-phases/calculating-phase.md).

**Tidal force** varies as 1/r³, so it swings by about 40% between perigee and
apogee — much more than the size does. Perigean spring tides are the highest of
the year.

## Supermoons

A "supermoon" is a full Moon near perigee. It is genuinely about 14% wider and
30% brighter than a full Moon at apogee — but you can only tell by measuring,
because you never see the two side by side.

The dramatic photographs are telephoto compression, not the supermoon.

## Try it yourself

1. Find the perigean spring tides in the next year and check them against a real
   tide table
2. Photograph the Moon at perigee and apogee with identical settings and measure
   the pixel diameter
3. Plot distance against time for a year. The pattern is not a clean sine — why?

## Checkpoint

- [ ] I know the distance varies by ~12%
- [ ] I know tidal force varies by ~40% because of the 1/r³ law
- [ ] I can connect the varying speed to the phase-model disagreement
- [ ] I can explain what a supermoon is and is not

Next: [Module 04 — Tides](../04-tides/).
