# Why UTC exists

*Background reading. No commands. About 15 minutes.*

Modern astronomy runs on an unambiguous time standard. That standard was not
handed down; it was built, over centuries, by people trying to solve an
extremely practical problem: **not sinking.**

This is the story of how "what time is it?" turned out to be the same question
as "where am I?".

---

## Earth's rotation is the original clock

Every human timekeeping system starts from one observation: the sky goes round
once a day.

The Sun rises, climbs, reaches its highest point, descends, sets. The obvious
way to define noon is the moment the Sun is highest — when it crosses your
**meridian**, the imaginary line running from due north, over your head, to due
south.

That is **local solar noon**, and it is a perfectly good definition of time. It
needs no equipment beyond a stick and its shadow. Every civilisation that
needed a clock found it.

It has one property that turns out to matter enormously.

---

## Local solar noon depends on longitude

Earth turns as one solid body. When it is solar noon for you, it is not solar
noon for someone to your east — the Sun already crossed their meridian, minutes
or hours ago.

The relationship is exact:

```
360 degrees / 24 hours   =  15 degrees per hour
15 degrees / 60 minutes  =  0.25 degrees per minute
1 degree                 ≈  4 minutes of time
```

Two towns 100 km apart at mid-latitudes have local noons about four minutes
apart. For most of human history this did not matter at all. Everyone kept
their own local time, set by the sun, and nobody needed to compare.

---

## Latitude was easy. Longitude was not.

Now put yourself on a ship in the middle of an ocean with no land in sight.

**Latitude** — how far north or south — is straightforward. Measure how high
the Sun gets at noon, or how high Polaris sits above the horizon. Both are
directly related to your latitude, and sailors could do this reliably by the
1500s with a quadrant and a table.

**Longitude** — how far east or west — is genuinely hard. Every meridian looks
exactly the same. There is no star that tells you. The Earth rotates beneath
you and takes all the reference points with it.

Ships navigated by **dead reckoning**: known starting point, plus heading, plus
speed, plus elapsed time. Errors accumulated. Currents pushed you sideways
without any indication. After weeks at sea, a captain might be a hundred
kilometres from where the chart said, with no way to know.

The consequences were not academic. Ships missed islands they were aiming for
and ran out of water. Ships found land sooner than expected, at night, and hit
it. In 1707, four British warships struck the Scilly Isles and around 1,500
people died — a navigational error, not a storm.

---

## The insight: longitude is a clock problem

Here is the trick that solves it, and it is genuinely beautiful.

Carry a clock that still shows the time at your **home port**. When the Sun
reaches its highest point where you are, that is local noon. Look at your home
clock. The difference between the two is your longitude.

If it is noon where you stand and your London clock says 15:00, you are three
hours behind London. Three hours at fifteen degrees per hour is 45 degrees west.

That is it. That is the whole method. Longitude is *time difference*.

---

## Which turns it into a clock-making problem

The method was understood well before it was usable, because the clocks did not
exist.

A pendulum clock is useless on a ship — the deck pitches, the pendulum swings
wrong. Temperature changes metal dimensions and alters the rate. Humidity and
salt attack the mechanism. A voyage might last years.

The accuracy required is brutal. Four seconds of error is one nautical mile of
longitude error at the equator. To land within half a degree after six weeks at
sea, a clock must not gain or lose more than about three seconds per day, in
those conditions, unattended.

In 1714 the British Parliament offered £20,000 — a colossal sum — for a method
accurate to half a degree. Most people assumed the answer would be
astronomical: tables of the Moon's position against the stars, effectively
using the Moon as a clock face. That method (**lunar distances**) did
eventually work, but the calculations took hours per fix.

**John Harrison**, a carpenter and self-taught clockmaker, spent decades on the
mechanical route instead. His marine chronometers used counter-oscillating
beams immune to a pitching deck, bimetallic strips that compensated for
temperature, and bearings that needed no lubrication. His H4, tested on a
voyage to Jamaica in 1761, lost about five seconds in eighty-one days.

Getting the prize money took him rather longer than solving the problem.

---

## From ships to railways

Chronometers solved navigation. Everyone on land still kept local solar time,
and that was fine — until things started moving quickly.

Railways broke it. If Bristol keeps time about ten minutes behind London
(they are roughly 2.5 degrees apart), what time does the timetable say? Whose
noon? Get it wrong and two trains occupy the same track.

British railways adopted London time across their networks in the 1840s —
"railway time". Other countries did the same. In 1884 the International Meridian
Conference in Washington chose Greenwich as the prime meridian, largely because
most of the world's shipping already used charts based on it, and standard time
zones followed: bands of roughly 15 degrees, each an hour apart, each keeping
one uniform time.

That is why time zones exist, why they are (roughly) an hour wide, and why
their boundaries wander around political borders rather than following clean
lines of longitude.

---

## From Earth's rotation to atomic time

For a long time the second was defined as a fraction of a day: 1/86,400.

Then clocks got good enough to check, and the answer was uncomfortable. **Earth's
rotation is not constant.** Tidal friction — the Moon's pull dragging on the
oceans — is slowly slowing it down. Earthquakes redistribute mass. Seasonal
movement of air and water shifts the moment of inertia measurably. The length
of a day varies by milliseconds, unpredictably.

If you want a reliable second, you cannot get it from a wobbly planet.

In 1967 the second was redefined atomically: 9,192,631,770 oscillations of the
radiation from a caesium-133 atom. Atoms of a given element are identical
everywhere, so any two caesium clocks agree. This is **TAI**, International
Atomic Time.

But now there are two disagreeing time scales:

- **TAI** — perfectly uniform, drifts away from the Sun
- **UT1** — tied to Earth's actual rotation, so noon stays at noon, but not
  uniform

**UTC** is the compromise, and it is the standard almost everything uses today.
It ticks at the atomic rate, so intervals are exact. When it drifts more than
0.9 seconds from UT1, a **leap second** is inserted to pull it back in line.
That is why some years have a 23:59:60.

Leap seconds are unpredictable — they depend on how the planet feels — so they
cannot be computed in advance, only announced. They cause enough trouble in
computing that there is a resolution to stop issuing them by 2035.

---

## Why computing and astronomy need this

**Astronomy** needs it because everything moves. The Moon travels its own width
in about an hour. Getting the time wrong by ten minutes puts it a couple of
degrees from where you predicted. Any position without a precise instant is
meaningless.

**Computing** needs it because of ordering. Distributed systems must agree
which event happened first. Local time cannot do this: it jumps forward and
backward for daylight saving, it differs by machine, and during the autumn
switch the same local timestamp occurs twice. Storing local time in a log is a
bug waiting for October.

Hence Moonfield's convention, which is standard practice everywhere:

> **Compute using an unambiguous time representation; display local civil time
> where useful.**

Internally we use UTC and Julian Day. Externally we show your local time,
because that is what you live in. The two are never confused, and every output
shows both.

---

## What this teaches beyond timekeeping

The longitude problem is a small, complete example of something much more
general:

- **A measurement is only as good as its reference.** The chronometer was
  useless without knowing what it was set to.
- **Errors propagate, often amplified.** One second of clock error becomes a
  quarter nautical mile of position error. The amplification factor is fifteen
  degrees per hour, and it does not care how you feel about it.
- **Small errors accumulate silently.** A clock losing a second a day is
  invisible daily and thirty kilometres wrong after a month.
- **Calibration is not bureaucracy.** It is the difference between an
  instrument and a confident liar.
- **Standards are infrastructure.** UTC is boring, and civilisation runs on it.

---

## Try it yourself

```bash
moonfield longitude --reference 14.5 --local-noon 12
moonfield longitude --reference 14.5 --local-noon 12 --drift 30
moonfield longitude --reference 14.5 --local-noon 12 --drift 600
```

The interactive version is [The Longitude Game](../interactives/longitude-game.md).

## Questions to think about

- Why is latitude so much easier than longitude? What is the asymmetry?
- Lunar distances required hours of computation per fix. Chronometers required
  an expensive instrument. Which would you have bet on in 1730?
- We stopped defining the second by Earth's rotation because the planet is
  unreliable. What else that seems fixed might not be?
- If leap seconds end in 2035, UTC will slowly drift from solar time. How long
  until anyone notices?

## Go deeper

- [Module 01 — Time and place](../01-time-and-place/)
- [Julian Day: why astronomers count days](../01-time-and-place/julian-day.md)
- Dava Sobel, *Longitude* (1995) — the popular account of Harrison
- Meeus, *Astronomical Algorithms*, chapters 7 and 10
