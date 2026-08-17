# Synodic and sidereal

**Goal:** answer the puzzle, the Moon orbits Earth in 27.3 days, but takes
29.5 days from full Moon to full Moon. Where do the extra two days come from?

---

## Observe

Two well-established facts that appear to contradict each other:

- The Moon completes one orbit of Earth in **27.32 days**
- The Moon goes from full Moon to full Moon in **29.53 days**

Both are correct. The difference is 2.21 days, about 8%. That is far too large
to be measurement error.

---

## Predict

Before reading on, try to explain it. Draw it if that helps.

Hint: what else moves during those 27.32 days?

---

## Learn

### Two different questions

The confusion comes from "one orbit" being ambiguous.

**Sidereal month (27.32 days)**: the time for the Moon to return to the same
position *against the background stars*. This is one genuine orbit, measured
against a fixed frame.

**Synodic month (29.53 days)**: the time for the Moon to return to the same
*phase*. Phase depends on the Sun-Earth-Moon angle, and the Sun's direction
changes as Earth orbits.

### Why the second is longer

Start at full Moon: Sun, Earth, Moon in a line, Moon opposite the Sun.

Wait 27.32 days. The Moon has completed one full orbit and is back at the same
place against the stars.

But Earth has not been still. In 27.32 days it has travelled about 27 degrees
around its own orbit, so the direction to the Sun has shifted by 27 degrees.
The Moon is back where it started relative to the stars, but the Sun has
moved, so the alignment is off by 27 degrees.

The Moon must catch up. It moves about 13.2 degrees per day, so 27 degrees
takes roughly 2 more days.

```
27.32 + 2.21 = 29.53
```

### The relationship, exactly

Angular rates add:

```
1 / P_synodic = 1 / P_sidereal - 1 / P_year
```

or equivalently

```
1 / P_sidereal = 1 / P_synodic + 1 / P_year
```

Check it:

```
1/27.32155 = 0.0366  (Moon, per day)
1/365.256  = 0.0027  (Earth, per day)
0.0366 - 0.0027 = 0.0339
1/0.0339 = 29.53 days
```

This is the same arithmetic as a fast runner lapping a slow one: the relative
rate is the difference of the absolute rates.

### The same idea elsewhere

This is not a lunar curiosity. It shows up whenever you measure one moving
thing against another moving reference:

- A **solar day** (24 h) is longer than a **sidereal day** (23 h 56 m) for
  exactly this reason, Earth must turn a little extra to face the Sun again.
- The **lunar day** (24 h 50 m) that drives tides is the same effect once more,
  with the Moon as the target.
- Planetary **synodic periods** (how often Mars returns to opposition) work
  identically.

Three phenomena in this curriculum, one relationship.

---

## Run

```python
import datetime as dt
from moonfield import moon, phase, time as mtime

start = dt.datetime(2026, 3, 1, tzinfo=mtime.UTC)
start_lon = moon.ecliptic_longitude(start)

# Sidereal: back to the same longitude
for hours in range(26 * 24, 29 * 24):
    when = start + dt.timedelta(hours=hours)
    diff = ((moon.ecliptic_longitude(when) - start_lon + 180) % 360) - 180
    if abs(diff) < 0.3:
        print(f"sidereal month ≈ {hours / 24:.2f} days")
        break

# Synodic: back to the same phase
a = phase.next_phase(start, 0.0)
b = phase.next_phase(a + dt.timedelta(hours=1), 0.0)
print(f"synodic month  ≈ {(b - a).total_seconds() / 86400:.2f} days")
```

---

## Change one variable

What if Earth did not orbit the Sun? Set the year infinitely long:

```
1/P_synodic = 1/27.32 - 1/∞ = 1/27.32
```

The two months become identical. The 2.21-day gap exists *only* because Earth
is moving.

Now the other direction: what if Earth orbited in 100 days instead of 365?

```
1/P_synodic = 1/27.32 - 1/100 = 0.0366 - 0.0100 = 0.0266
P_synodic = 37.6 days
```

A much longer month. And if Earth's year were shorter than the Moon's orbit,
the arithmetic would go negative, phases would run backwards.

---

## Validate

Measure it yourself. In your observation log from
[Go and look](go-and-look.md), find two consecutive full Moons. The gap should
be 29 or 30 days.

For the sidereal month you need the Moon's position against the stars, note
which bright star or constellation it sits near, and wait for it to return. That
takes about 27 days. Doing this with your own eyes is how it was first measured.

---

## Explain

Why does this matter beyond trivia?

Because it is a worked example of something you will hit constantly:
**the answer depends on your reference frame, and "obvious" questions often
hide an ambiguity.**

"How long does the Moon take to orbit Earth?" has two correct answers. Not
because anyone is confused, but because "orbit" was underspecified. Noticing
that a question has a hidden parameter (before you argue about the answer) is
a genuinely transferable skill.

---

## Checkpoint

- [ ] I can define sidereal and synodic months
- [ ] I can explain why the synodic month is longer
- [ ] I can write down and use the reciprocal relationship
- [ ] I can name two other places the same effect appears
- [ ] I can explain what would happen if Earth's year were different
- [ ] I understand that "one orbit" is an ambiguous phrase

## Try it yourself

1. Compute the synodic month from the sidereal month and the year, by hand
2. If the Moon orbited in 20 days, what would the synodic month be?
3. Work out the sidereal day from the solar day and the year, same formula
4. Look up Mars's orbital period and compute its synodic period from Earth.
   Check it: Mars oppositions really are about that far apart.
5. Find the difference between the *longest* and *shortest* real synodic months
   in a year, using `phase.next_phase`

## Questions to think about

- If we lived on a moon of Jupiter, which "month" would our calendar use?
- Calendars try to fit months into years and never quite manage. Why is that
  fundamentally impossible?
- The Moon is tidally locked, so its rotation period equals its sidereal month.
  Does a lunar "day" (sunrise to sunrise on the Moon) last 27.3 days or 29.5?

That last one is a good test of whether the idea has landed.

## Go deeper

- [Module 03, The Earth-Moon system](../03-earth-moon-system/)
- [Module 04, Tides](../04-tides/): where the lunar day drives everything

Next: [Module 03](../03-earth-moon-system/).
