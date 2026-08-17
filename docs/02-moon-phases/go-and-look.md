# Go and look

**Goal:** start an observation log. This lesson takes ten minutes today and
five minutes a night for the next month.

**Do this before the calculation lessons.** They are far more interesting when
you have your own data to check them against.

---

## Why a log

You are going to build models that predict the Moon. A model is only
interesting if you can be wrong about it, and you can only be wrong if you
wrote something down first.

Also: most people have never actually watched the Moon over a full cycle. It is
worth doing once in your life regardless of any of this.

---

## What to record

Each time you see the Moon, note:

| Field | Example | Why |
|---|---|---|
| Date and time | 2026-08-16 21:40 | An observation without a time is not data |
| Phase, in your own words | "thin crescent, lit on the right" | Your judgement, not the app's |
| Rough altitude | "two fists above the roofline" | Fist ≈ 10° at arm's length |
| Rough direction | "west, over the church" | A landmark is more reliable than a guess |
| Sky conditions | "clear", "thin cloud" | Explains gaps and odd readings |
| Anything odd | "looked huge near the horizon" | The best notes are the surprised ones |

A paper notebook is completely fine. So is a text file:

```
2026-08-16 21:40  thin crescent, lit on right, ~1 fist up, WNW over the church, clear
2026-08-17 21:45  slightly fatter, ~1.5 fists, W, thin cloud
2026-08-18 --     overcast, nothing visible
```

Record the misses. A gap in the data is data.

---

## Measuring angles with your hand

At arm's length, roughly, for most adults:

| Gesture | Angle |
|---|---|
| Little finger width | 1° |
| Thumb width | 2° |
| Three middle fingers | 5° |
| Closed fist | 10° |
| Hand span, thumb to little finger | 20° |

Hand size and arm length correlate, which is why this works across different
people better than it has any right to.

Calibrate once: find something whose altitude Moonfield can tell you — the Moon
right now — and compare against your fists.

---

## The predictions to make

Alongside the observations, write predictions **before** you look:

1. **Tonight:** what phase, roughly where in the sky?
2. **In one week:** what phase?
3. **Next full Moon:** which date?
4. **Where does the Moon rise?** Same place each night, or does it move?
5. **Does it rise at the same time each night?**

Do not look these up. Guess, commit, and check later. Questions 4 and 5 in
particular tend to produce confident wrong answers, which is exactly what you
want.

---

## Things worth noticing

Over a month, several of these will probably surprise you:

**The Moon is often up in daylight.** A gibbous Moon in a blue sky is common
and most people never notice it.

**It rises later each night**, by roughly 50 minutes — but not consistently.
The shift ranges from about 15 minutes to about 90, depending on the season and
your latitude. That variation has a name (the Harvest Moon effect) and a cause,
and it is in `tests/test_observer.py` if you want to skip ahead.

**It moves along the horizon.** Moonrise is not in the same place each night.
Over a month it swings through a wide arc.

**A crescent points at the Sun.** The line joining the horns of a crescent is
perpendicular to the direction of the Sun. You can find where the Sun is,
below the horizon, from the crescent alone.

**Earthshine.** Near new Moon, the dark part is faintly visible — lit by
sunlight reflected off Earth. Leonardo da Vinci worked out the cause around
1510.

**The Moon looks bigger near the horizon.** It is not. Photograph it low and
high on the same night and measure. This is the Moon Illusion, it is entirely
in your visual system, and it is still not fully explained.

---

## Cross-checking against Moonfield

After each observation, and *only after*:

```bash
moonfield now
```

Compare its azimuth and altitude with your fists-and-landmarks estimate. You
will be a few degrees out; that is normal and fine.

If you are wildly out — tens of degrees — check in this order:

1. Your saved longitude sign
2. Your clock
3. Whether you were facing the direction you thought

---

## Checkpoint

- [ ] I have started a log with at least one entry
- [ ] I have written down predictions I have not checked
- [ ] I can estimate angles with my hand
- [ ] I know to record the nights I see nothing
- [ ] I know to observe first, then check

## Try it yourself

Over the next month:

1. Observe on at least ten nights
2. Note the time of moonrise on three consecutive clear nights and compute the
   gaps
3. Photograph the Moon at the same time each night, from the same spot, for a
   week
4. Find earthshine on a crescent
5. Test the Moon Illusion with a camera and be annoyed by the result

## Questions to think about

- Why is the Moon sometimes visible in daylight and sometimes not?
- If the Moon rises later each night, is there a night when it does not rise at
  all?
- Why does a crescent point at the Sun?

## Go deeper

- [Why phases happen](why-phases-happen.md)
- [Module 05 — Your local sky](../05-local-sky/)

Next: [Why phases happen](why-phases-happen.md).
