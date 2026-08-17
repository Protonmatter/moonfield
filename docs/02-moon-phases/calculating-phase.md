# Calculating a phase

**Goal:** compute the Moon's phase from scratch, twice, and understand why the
two answers differ.

**Prerequisites:** [Why phases happen](why-phases-happen.md).

---

## Observe

Run this, and look at the last section:

```bash
moonfield phase --explain
```

It shows two numbers for the Moon's age that do not agree. This lesson is about
why.

---

## Predict

Before you read on:

The Moon's cycle averages 29.53 days. Suppose you know a date when there was a
new Moon, and you count forward in steps of 29.53 days.

1. How far off would you expect to be after one month?
2. After a year?
3. After ten years?

Write these down. You will check them at the end.

---

## Model 1: the clock

### The idea

The Moon's phases repeat every 29.53 days on average. If you know one new Moon,
you can reach any other date by counting.

```
age = (today - known_new_moon) mod 29.53
```

That is the whole model. You could do it on paper.

### Doing it by hand

There was a new Moon on **2000 January 6 at 18:14 UTC**, which is Julian Day
2451550.2597.

For 2026 August 16 at 21:00 UTC, JD 2461269.375:

```
elapsed = 2461269.375 - 2451550.2597 = 9719.115 days
cycles  = 9719.115 / 29.530589      = 329.12 cycles
age     = 0.12 × 29.530589          ≈ 3.55 days
```

About three and a half days past new — a young waxing crescent.

### Turning age into illumination

Picture the terminator sweeping across the disc at a steady rate. Project a
circle rotating uniformly onto your line of sight and you get:

```
illumination = (1 - cos(2π × age / 29.530589)) / 2
```

At age 0 that gives 0. At 14.77 days it gives 1. At 7.38 days, 0.5.

### In code

```python
from moonfield import phase
age, illumination = phase.simple_phase()
print(f"{age:.2f} days old, {illumination * 100:.1f}% lit")
```

`src/moonfield/phase.py`, function `simple_phase`. Twelve lines including the
comments.

### What it assumes

1. The Moon moves at a constant rate — **false**
2. Every cycle is exactly 29.530589 days — **false**, they range 29.27 to 29.83
3. Earth's orbit does not affect it — **false**
4. The illumination curve is a clean cosine — **approximately true**

---

## Model 2: the geometry

### The idea

Stop counting. Find out where the Sun actually is, find out where the Moon
actually is, and measure the angle between them.

That angle is the **elongation**:

```
elongation = moon_longitude - sun_longitude   (mod 360)
```

- 0° — same direction as the Sun — new Moon
- 90° — first quarter
- 180° — opposite the Sun — full Moon
- 270° — last quarter

### Finding the Sun

Solvable in closed form to good accuracy. Earth's orbit is an ellipse; the
correction from pretend-uniform motion to real motion is the **equation of the
centre**:

```
C = 1.9146° sin(M) + 0.0200° sin(2M) + 0.0003° sin(3M)
```

where `M` is the mean anomaly. Add that to the mean longitude and you have the
true longitude, good to about 0.01°.

See `src/moonfield/sun.py`.

### Finding the Moon

Much harder. Earth pulls on the Moon, the Sun pulls on the Moon, and the
three-body problem has no closed-form solution. What exists instead is a
**series**: a long sum of sine terms, each a named wobble.

```
longitude = L' + 6.289° sin(M')
               + 1.274° sin(2D - M')
               + 0.658° sin(2D)
               + 0.214° sin(2M')
               - 0.185° sin(M)
               + ... (thirty more terms)
```

Each term is a real physical effect:

| Term | Name | Cause |
|---|---|---|
| 6.289° sin(M') | Equation of the centre | The Moon's own elliptical orbit |
| 1.274° sin(2D−M') | **Evection** | The Sun distorting that ellipse |
| 0.658° sin(2D) | **Variation** | Sun's pull varying around the orbit |
| −0.185° sin(M) | **Annual equation** | Earth's distance from the Sun changing |

Evection was found by Ptolemy around 150 AD. Variation and the annual equation
by Tycho Brahe in the 1590s. These are centuries of patient observation, each
term a discrepancy someone refused to ignore.

See `src/moonfield/moon.py`.

### From elongation to illumination

Not quite the same as the elongation, because the Sun is not infinitely far
away. What matters is the **phase angle** — the Sun-Moon-Earth angle:

```
tan(phase_angle) = R sin(ψ) / (Δ - R cos(ψ))
illumination = (1 + cos(phase_angle)) / 2
```

with `R` the Earth-Sun distance, `Δ` the Earth-Moon distance, `ψ` the
elongation.

---

## Run both

```bash
moonfield phase --date 2026-08-16 --explain
```

```
  Elongation = Moon longitude - Sun longitude
             = 191.5083 - 143.9155
             = 47.5928 deg

  Phase angle (Sun-Moon-Earth): 132.2178 deg
  Illumination = (1 + cos(132.2178)) / 2
               = 0.164318  ->  16.4%

The simple model, for comparison
--------------------------------
    simple age  = 3.5530 days
    true age    = 4.1418 days
    difference  = -14.13 hours
```

Fourteen hours apart. Neither is buggy.

---

## Explain the difference

The simple model assumes constant speed. The Moon's orbit is an ellipse, so it
moves fastest at perigee and slowest at apogee — a variation of about 12%.

Over one cycle, that means the real Moon can be up to roughly half a day ahead
of or behind the clock model. The error is **cyclic, not cumulative**: it swings
back and forth rather than growing without limit. Check your predictions from
the start of this lesson — most people expect the error to grow.

```python
import datetime as dt
from moonfield import phase, time as mtime

worst = 0
for day in range(0, 365, 3):
    when = dt.datetime(2026, 1, 1, tzinfo=mtime.UTC) + dt.timedelta(days=day)
    info = phase.compute(when)
    worst = max(worst, abs(info.model_disagreement_hours))
print(f"worst disagreement over a year: {worst:.1f} hours")
```

---

## Validate

Both models against reality. Published new Moons for 2026:

| Date | Time (UTC) |
|---|---|
| 18 January | 19:52 |
| 19 March | 01:23 |
| 12 August | 17:37 |

```bash
moonfield phase --date "2026-08-12T17:37" --no-art
```

Illumination should be essentially zero. Moonfield's test suite checks exactly
this in `tests/test_phase.py` and requires agreement within 30 minutes; it
actually achieves about two.

---

## Change one variable

Open `src/moonfield/phase.py` and change `REFERENCE_NEW_MOON` by one day. Run
`moonfield phase --explain`.

The simple model shifts by a day. The geometric model does not move at all — it
does not use that constant. That is the practical difference between a model
anchored to a measurement and one derived from geometry.

Change it back.

---

## Checkpoint

- [ ] I can compute a Moon phase with arithmetic and a known new Moon date
- [ ] I know what elongation is and what 0/90/180/270 mean
- [ ] I know why the geometric model needs a long series for the Moon
- [ ] I can name at least two terms in that series and what causes them
- [ ] I can explain why the two models disagree by up to half a day
- [ ] I know the error is cyclic, not cumulative
- [ ] I have checked both models against a published new Moon

## Try it yourself

1. Do the simple calculation by hand for today. Compare with `simple_phase`.
2. Find the date this year where the two models disagree most.
3. Truncate the lunar series further — comment out all but the first five terms
   in `moon.py` — and see how much accuracy you lose.
4. Work out how many terms you need for 0.1° accuracy.
5. Compute the illumination for a date, then again with the Sun's distance
   pretended infinite. How much does the phase-angle correction actually matter?

## Questions to think about

- The simple model is wrong by up to half a day and needs one constant. The
  geometric model needs thirty-five. When is the simple one the better choice?
- Ptolemy found evection with naked-eye observations around 150 AD. What does
  that tell you about how carefully people were watching?
- Why does the Moon need a series when the Sun does not?

## Common questions

**Why is the Moon so much harder than the Sun?**
The Sun's apparent motion is really Earth's orbit — a two-body problem with an
exact solution. The Moon is a genuine three-body problem, and those have no
closed form.

**Could I just use a lookup table?**
Yes, and for a few years that is fine. It stops working the moment you want a
date outside the table, and it teaches you nothing about why.

## Go deeper

- [Synodic and sidereal](synodic-and-sidereal.md)
- [How accurate is Moonfield?](../background/accuracy.md)
- Meeus, *Astronomical Algorithms*, chapters 25 and 47
- Read `src/moonfield/phase.py` — both models, side by side

Next: [Synodic and sidereal](synodic-and-sidereal.md).
