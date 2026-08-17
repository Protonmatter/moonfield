# Julian Day

**Goal:** understand the number astronomers actually calculate with, and why
calendars are unsuitable.

---

## Observe

How many days are there between 15 February 2024 and 3 March 2024?

Work it out. Notice what you had to know: how many days February has, and
whether 2024 is a leap year.

Now: how many days between 20 December 1580 and 10 January 1590?

That one has a trap in it, and we will come back to it.

---

## Predict

If you were writing a program to find the number of days between two dates,
what would you have to handle?

List as many complications as you can before reading on.

---

## Learn

### Calendars are for humans

Our calendar is optimised for social life, not arithmetic. It has:

- Months of 28, 29, 30 or 31 days, in no useful pattern
- Leap years every 4 years: except centuries, except every 400th century
- A ten-day gap in October 1582, when much of Europe switched from the Julian
  to the Gregorian calendar
- Different countries making that switch at different times, up to 1923
- Years that historically began in March, or at Christmas, or at Easter

That last group is why the 1580–1590 question is a trap: the answer depends
entirely on which country you were standing in.

Writing date arithmetic that survives all this is possible. Writing *astronomy*
on top of it is masochism.

### The Julian Day: just count

The solution is embarrassingly simple. Pick a moment long ago and count days
forward. One number. Decimals for fractions of a day.

```
2451545.0   =  2000 January 1 at 12:00 UTC
2461269.375 =  2026 August 16 at 21:00 UTC
```

No months. No leap years. No calendar reforms. The difference between two
Julian Days is the number of days between them, always, with no special cases.

### Why noon?

Julian Days begin at **noon**, not midnight. `2451545.0` is midday.

That looks perverse until you remember who invented it. Astronomers observe at
night. If the day rolled over at midnight, every observing session would be
split across two dates and half your notes would be filed under the wrong day.
Starting at noon puts a whole night inside a single Julian Day.

The practical consequence: a Julian Day for midnight ends in `.5`.

### Where does the count start?

4713 BC, January 1, on the Julian calendar. There is nothing astronomically
special about it. Joseph Scaliger chose it in 1583 because three separate
calendar cycles all began together that year, and it comfortably predates
recorded history, so no useful date needs a negative number.

### The J2000 epoch

Modern formulae are not built directly on Julian Days but on the time elapsed
since **J2000.0** = JD 2451545.0 = 2000 January 1, 12:00.

Nearly every series you will meet uses `T`, the Julian centuries since J2000:

```
T = (JD - 2451545.0) / 36525
```

Dividing by 36525 (a Julian century, 100 × 365.25 days) makes `T` a small
number near the present, which keeps the polynomials well behaved.

You will see `T` all over `src/moonfield/sun.py` and `moon.py`.

---

## Run

```bash
moonfield doctor
```

Look for:

```
  - Julian Day now: 2461269.37500
```

Or in Python:

```python
import datetime as dt
from moonfield import time as mtime

print(mtime.julian_day(dt.datetime(2000, 1, 1, 12, 0, tzinfo=mtime.UTC)))
# 2451545.0
```

---

## Change one variable

```python
from moonfield import time as mtime
import datetime as dt

a = mtime.julian_day(dt.datetime(2024, 2, 15, tzinfo=mtime.UTC))
b = mtime.julian_day(dt.datetime(2024, 3, 3, tzinfo=mtime.UTC))
print(b - a)     # 17.0
```

Seventeen days, with no leap-year logic anywhere. The awkwardness was absorbed
once, in the conversion, and never has to be thought about again.

Try it across a century boundary, or across 1582. Still just subtraction.

---

## Validate

Two reference values you can check against any astronomical source:

| Instant | Julian Day |
|---|---|
| 2000 Jan 1, 12:00 UTC | 2451545.0 |
| 1957 Oct 4, 19:28:34 UTC (Sputnik 1 launch) | 2436116.31 |

Both are in Moonfield's test suite. Run `pytest tests/test_time.py -v` to see
them checked.

---

## Explain

Julian Day is an example of a pattern worth recognising: **convert to a
representation your operations are natural in, do the work, convert back.**

The messy part happens once, at the boundary. Everything inside is clean
arithmetic. You will meet this idea again; it is why we use radians internally
and degrees for display, and why we compute in UTC and display local time.

---

## Checkpoint

- [ ] I can explain why calendars are bad for arithmetic
- [ ] I know a Julian Day is a running count of days
- [ ] I know why they start at noon
- [ ] I know what J2000.0 is and why formulae use `T`
- [ ] I can convert a date to a Julian Day with Moonfield

## Try it yourself

1. Find the Julian Day of your birthday
2. Compute how many days you have been alive, using subtraction only
3. Verify that JD for any midnight ends in `.5`
4. Find the Julian Day of the first Moon landing, 1969-07-20 20:17 UTC
5. Compute the gap between the two Apollo 11 landings-adjacent dates of your
   choice and sanity-check it by hand

## Questions to think about

- Why not count seconds since a fixed date, like Unix time does?
- What breaks if you store a Julian Day in a 32-bit float? (Try it. The answer
  is unpleasant and instructive.)
- The Julian Day count has no leap seconds in it. What does that imply about
  its relationship to UTC over long spans?

## Common questions

**Is this related to the Julian calendar?**
Only by name, and even that is contested, Scaliger may have named it after his
father, Julius. The Julian Day number is calendar-independent.

**Modified Julian Day?**
`MJD = JD - 2400000.5`. Smaller numbers, and it starts at midnight. Common in
satellite work. Moonfield uses plain JD.

## Go deeper

- Read `src/moonfield/time.py`, `julian_day` and `from_julian_day`
- Meeus, *Astronomical Algorithms*, chapter 7
- [Why UTC exists](../background/why-utc-exists.md)

Next: [Where are you?](where-are-you.md)
