# 01: Time and place

Astronomy is the study of where things are, and *where* only means something
once you have said *when* and *from where*.

This module builds the two-part foundation everything else stands on: an
unambiguous instant, and a defined observing position.

## Lessons

| # | Lesson | What you get |
|---|---|---|
| 1 | [Local time, UTC and timezones](utc-and-timezones.md) | Why a bare time is not an instant |
| 2 | [Julian Day](julian-day.md) | The number astronomers actually compute with |
| 3 | [Where are you?](where-are-you.md) | Latitude, longitude, and sign conventions |
| 4 | [The Longitude Game](longitude-game.md) | Time difference *is* position |

## Prerequisites

[Module 00](../00-start-here/) complete. `moonfield doctor` passing.

## The project convention

> **Compute using an unambiguous time representation; display local civil time
> where useful.**

Internally, Moonfield uses UTC and Julian Day. Externally, it shows your local
civil time (because that is what you live in), but always alongside UTC, so
the two can never be confused.

## What this module deliberately leaves out

The core path covers local time, UTC, timezones, dates, and why astronomy needs
an unambiguous instant. That is enough for everything through module 06.

Deferred to optional advanced material:

- Daylight saving time in detail, and its many edge cases
- Apparent solar time versus mean solar time
- UT0, UT1, UT2 and the various rotational time scales
- Leap seconds and why they are being abolished
- TAI, TT, TDB and the relativistic corrections between them
- Precision timekeeping and clock synchronisation protocols

None of it is needed to predict where the Moon will be tonight. It becomes
relevant when you want accuracy better than a few seconds, which is a long way
from where we are starting.

## Background reading

- [Why UTC exists](../background/why-utc-exists.md): the longitude problem,
  marine chronometers, and how "what time is it" became "where am I"
