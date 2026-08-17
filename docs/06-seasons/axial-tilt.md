# Axial tilt

**Goal:** connect the 23.4° tilt to the Sun's declination, and to everything
you can observe.

---

## The one number

Earth's rotation axis is tilted **23.44°** from the perpendicular to its orbit.
The axis keeps pointing the same way in space all year; it does not wobble to
follow the Sun.

That fixed tilt, plus the orbit, produces everything.

## Declination is the tilt made visible

The Sun's **declination** is its angle north or south of the celestial equator.
It is, equivalently, the latitude where the Sun is directly overhead today.

```python
import datetime as dt
from moonfield import sun, time as mtime

for month in range(1, 13):
    when = dt.datetime(2026, month, 21, 12, tzinfo=mtime.UTC)
    print(f"{when:%b}  {sun.declination(when):+7.2f} deg")
```

It swings between +23.44° and −23.44° and back, once a year, roughly
sinusoidally.

- **+23.44°**: June solstice, Sun overhead at the Tropic of Cancer
- **0°**: equinoxes, Sun overhead at the equator
- **−23.44°**: December solstice, Tropic of Capricorn

The tropics are *defined* by the tilt. They are the latitudes the Sun can reach
overhead. The polar circles at 66.56° (= 90 − 23.44) are where the Sun can stay
up or down for a full day.

Change the tilt and you move all four lines.

## The formula that ties it together

From [module 05](../05-local-sky/why-latitude-matters.md):

```
noon altitude = 90° − |latitude − declination|
```

Latitude is fixed. Declination is the season. That single expression contains
your whole year of noon Suns.

## Try it yourself

1. Plot declination against date for a year. How close to a sine is it?
2. Compute the Arctic Circle latitude from the tilt alone
3. What would seasons be like with a 0° tilt? With 90°? (Uranus is at 98°.)
4. Track your own noon shadow length weekly for a term and plot it

## Checkpoint

- [ ] I know the tilt is 23.44° and stays fixed in space
- [ ] I know declination = the latitude where the Sun is overhead
- [ ] I can derive the tropics and polar circles from the tilt
- [ ] I can compute my noon solar altitude for any date

Next: [Solstices and equinoxes](solstices-and-equinoxes.md).
