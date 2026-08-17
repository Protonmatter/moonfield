# The Longitude Game — Don't Get Lost at Sea

**Goal:** feel, rather than be told, that time difference *is* longitude — and
that a small clock error becomes a large position error.

Two versions, same maths:

- **Browser:** `site/longitude-game/` — open `index.html`, or visit the
  project's GitHub Pages site
- **Terminal:** `moonfield longitude`, no browser required

Neither is the "real" one. Use whichever suits you.

---

## Observe

You are on a ship. There is no land in any direction. You have:

- A sextant, so you can find local noon and your latitude
- A chronometer, still showing the time at your home port
- No satellites, no radio, no landmarks

Where are you?

---

## Predict

Before calculating: if your clock reads two hours *ahead* of your local noon,
are you east or west of home? By how much?

Commit to an answer. Most people get the direction wrong first time.

---

## Learn

### The arithmetic

```
360 degrees / 24 hours   =  15 degrees per hour
15 degrees / 60 minutes  =  0.25 degrees per minute
1 degree                 ≈  4 minutes of time
```

### The method

1. Watch the Sun. When it stops rising and starts falling, that is **local
   apparent noon** — the Sun is on your meridian.
2. At that exact instant, read your home-port chronometer.
3. The difference is your longitude.

If your London chronometer reads 15:00 at your local noon, then noon reached
you three hours *after* it reached London. Earth turns west to east, so the Sun
arrives at eastern places first. Three hours later means 45 degrees **west**.

```
longitude = -(reference_time - local_noon) × 15
```

The minus sign is the part people get backwards. Your clock reading *ahead* of
local noon means you are **west**.

---

## Run

```bash
moonfield longitude --reference 14.5 --local-noon 12
```

```
  Reference clock at local noon: 14:30
  Local apparent noon:           12:00
  Difference: +2.5000 hours

  Longitude = -(+2.5000 h) x 15 deg/h = -37.500 deg
  You are at 37.500 degrees west of your reference.
```

---

## Change one variable: Wrong Landfall

Now break the clock.

```bash
moonfield longitude --reference 14.5 --local-noon 12 --drift 30
moonfield longitude --reference 14.5 --local-noon 12 --drift 120
moonfield longitude --reference 14.5 --local-noon 12 --drift 600
```

Thirty seconds of drift:

```
  - An error of 0.125 degrees
  - At latitude 45, that is about 9.8 km in the wrong place
```

Ten minutes:

```
  - An error of 2.500 degrees
  - At latitude 45, that is about 196.8 km in the wrong place

This is how ships were lost. Not through bad seamanship, but
through arithmetic done on a number that was quietly wrong.
```

The rule of thumb worth memorising:

> **4 seconds of clock error = 1 nautical mile of longitude error at the
> equator.**

A chronometer losing one second per day is invisible on any given day, and
thirty seconds — about 14 km — wrong after a month at sea.

---

## Validate

Check the arithmetic yourself, on paper, for one case. Then check it against
reality: your own timezone offset is roughly your longitude divided by 15. If
you are at 74°W, you should be around UTC−5. You will find it is *roughly*
right and not exactly, because timezone borders follow politics.

---

## Explain

Why is latitude easy and longitude hard?

Because Earth's rotation gives latitude a natural reference — the equator and
the poles are physically distinguishable — while every meridian is identical.
There is no natural zero for longitude, so you must *carry* your reference with
you. That is what the chronometer is: a reference you brought from home.

The generalisation is worth keeping:

> **A measurement is only as good as its reference, and errors in the reference
> propagate into the result multiplied by whatever constant relates them.**

Here that constant is 15 degrees per hour. It is unforgiving, and it does not
care that your clock error was small.

---

## Checkpoint

- [ ] I can state the 15-degrees-per-hour relationship
- [ ] I can work out longitude from two clock readings
- [ ] I know which direction a clock reading *ahead* implies
- [ ] I can convert a clock error into a distance error
- [ ] I know why latitude was solved centuries before longitude
- [ ] I can explain why calibration matters, using this as the example

## Try it yourself

1. Work out the longitude for a reference reading of 09:00 at local noon.
   Which hemisphere?
2. How much clock drift puts you 1 km wrong at your own latitude?
3. Harrison's H4 lost about 5 seconds in 81 days. How far wrong was that
   voyage, at the equator?
4. Compute the error a 1-second-per-day clock accumulates over a two-year
   voyage.

## Questions to think about

- The lunar-distance method needed no clock but hours of computation per fix.
  Chronometers needed no computation but an expensive, fragile instrument.
  Which would you have backed in 1730?
- GPS works by comparing signal arrival times from satellites with known
  positions. How is that the same problem, and how is it different?
- What is the modern equivalent of a drifting chronometer — a small, invisible
  error in a reference that quietly poisons everything downstream?

## Go deeper

- [Why UTC exists](../background/why-utc-exists.md)
- Dava Sobel, *Longitude* (1995)
- The browser version in `site/longitude-game/`

Next: [Module 02 — Moon phases](../02-moon-phases/).
