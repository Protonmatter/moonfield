# How accurate is Moonfield?

Every number a model produces has an error bar, whether or not anyone prints
it. This page states Moonfield's, where they come from, and when they stop
being good enough.

## Summary

| Quantity | Typical error | Good enough for |
|---|---|---|
| Sun position | ~0.01° | Anything visual |
| Moon position | ~0.002° (~7″) | Anything visual |
| Moon phase / illumination | ~2 minutes of timing | Anything |
| Sunrise / sunset | 1–2 minutes | Planning your evening |
| Moonrise / moonset | 1–2 minutes | Planning your evening |
| Solstices / equinoxes | ~1 minute | Anything |
| Julian Day | Exact | Anything |
| **Tides** | **Hours, and metres** | **Learning only. Not navigation.** |

The tide row is not a defect. See below.

## Where the numbers come from

**The Sun** uses the low-precision method from Meeus, *Astronomical
Algorithms*, chapter 25, a mean longitude plus a three-term equation of the
centre. Meeus states 0.01° and our check against his worked example (JD
2448908.5) reproduces his apparent longitude to 199.90894° against his
199.90895°.

**The Moon** uses a truncated ELP-2000/82, Meeus chapter 47: 35 longitude and
distance terms, 30 latitude terms, from a series with hundreds. Against Meeus's
worked example (JD 2448724.5), we get 133.166783° against his 133.167265°, about
1.7 arcseconds, entirely from the truncation.

Full ELP-2000/82 would reach milliarcseconds. It would also be thousands of
terms and unreadable, which defeats the purpose.

**Rise and set** are found by sampling every 10 minutes and then bisecting,
rather than by a closed-form formula. Closed forms assume the body does not
move during the day: acceptable for the Sun, poor for the Moon, which shifts
about 13° between one sunset and the next.

Sunrise is defined at a geometric altitude of −0.833°: −0.567° for atmospheric
refraction (Bennett's formula, Meeus ch. 16) and −0.267° for the Sun's radius,
because "sunrise" means the upper limb.

## What limits it

**Refraction is genuinely uncertain.** The standard formula assumes 10 °C and
1010 mb. Real refraction at the horizon varies with temperature, pressure and
lapse rate, and on a cold clear morning over water it can differ by several
arcminutes. This is a real physical limit, not a coding one, no algorithm
fixes it, because the atmosphere is not in the algorithm.

For sunrise timing, refraction uncertainty dominates everything else we do.

**Your horizon is not flat.** All rise/set times assume a level, sea-level
horizon. A hill to your east delays sunrise by far more than any error here. So
does altitude, in the other direction.

**Truncation.** More terms would help the Moon slightly. The current error is
smaller than the effects above, so it is not the bottleneck.

**ΔT.** For historical dates, the difference between Terrestrial Time and UT
matters. Moonfield ignores it, which is fine for the present day and
increasingly wrong before about 1900.

## Why the tides are different

The tide model is **not** an approximation of a good model. It is a
deliberately introductory model that is physically correct and operationally
inadequate, for reasons explained at length in
[why local tides are hard](../04-tides/why-local-tides-are-hard.md).

Briefly: it computes the equilibrium tide, which assumes a deep uniform ocean
responding instantly. The real ocean cannot move fast enough, is full of
continents, and resonates. Real prediction requires harmonic analysis of a year
or more of measurements at each specific station.

Errors of several hours in timing and a factor of several in range are normal
and expected. `moonfield tide compare` exists to help you *measure* your local
error rather than pretend it is not there.

**Do not use Moonfield's tide output for anything where being wrong has
consequences.** The LICENSE says this too.

## How this is checked

The test suite validates against three independent kinds of reference:

1. **Textbook worked examples.** Meeus's own examples, to his stated precision.
2. **Published ephemeris values.** New and full Moon times, solstices, sunrise
   and sunset for known locations and dates.
3. **Physical identities.** Noon altitude must equal 90° − |latitude −
   declination|. Equinox sunrise must be due east everywhere. Hemispheres must
   be opposite. These tests survive an algorithm rewrite, which stored numbers
   do not.

```bash
python -m pytest -v
```

If you find a case where Moonfield is worse than the table above claims,
[open an issue](../../issues). A reproducible accuracy failure is a valuable
contribution.

## The general point

Every model here has a domain where it is useful and a boundary past which it
is not. Knowing where that boundary is (and saying so out loud) is the
difference between a tool and a black box.

That is why this page exists, and why the tide module is in the curriculum at
all.
