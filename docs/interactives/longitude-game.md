# The Longitude Game

**The problem:** you are on a ship. You can find your latitude in minutes with a
sextant. Finding your longitude is so hard that it killed people by the
thousand and stayed unsolved for two centuries.

Why the asymmetry?

## Play it

**In the browser:** open [`site/longitude-game/index.html`](../../site/longitude-game/index.html)
— no install, no network.

**In the terminal:**

```bash
moonfield longitude --reference
moonfield longitude --local-noon 12:34
moonfield longitude --drift 4
```

## The idea in one line

Earth turns 360° in 24 hours, so **15° of longitude = 1 hour of time**.

If you know the time at a reference meridian, and you can measure local noon
where you are, the difference gives you your longitude.

```
longitude = (reference_time_at_local_noon − 12:00) × 15°
```

Local noon is easy — the Sun is highest, a vertical stick's shadow is shortest.
Reference time is the hard part, because it means carrying an accurate clock
across an ocean on a rolling, damp, temperature-swinging ship.

Latitude is easy because it can be read from the sky alone. Longitude is hard
because it needs a *memory of somewhere else*.

## Wrong Landfall mode

The game's second mode is the one worth playing.

You are given a clock that drifts by a few seconds a day. You sail for weeks.
Then you make landfall — and find out where you actually are versus where you
thought.

Four seconds of drift per day, over a two-month crossing, is about four minutes
of error, which is about one degree of longitude, which at that latitude is
roughly 60 nautical miles of ocean between you and the harbour you were aiming
for.

That is not a rounding error. That is rocks.

In 1707 four ships of the Royal Navy struck the Isles of Scilly and around 1,500
men died, in a disaster generally attributed to longitude error. The Longitude
Act followed in 1714, offering a prize worth millions in today's money.

## What it is really teaching

Three things that recur throughout Moonfield:

1. **Time and position are the same problem.** This is why UTC gets a whole
   background page, why `moonfield doctor` checks your clock, and ultimately why
   GPS is a constellation of atomic clocks.
2. **Error accumulates.** A tiny per-day error becomes a fatal per-voyage error.
   Knowing the *rate* is not enough; you have to integrate it over the mission.
3. **The hard part is often not the physics.** Everyone understood the theory by
   1600. The problem was building a clock that worked on a ship, and that took
   John Harrison forty years.

## See also

- [Why UTC exists](../background/why-utc-exists.md)
- [Module 01 — Time and place](../01-time-and-place/longitude-game.md)
