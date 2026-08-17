# Local time, UTC and timezones

**Goal:** understand why "9pm" is not a moment in time, and what to use instead.

---

## Observe

Ask someone in another country what time it is. They will give you a different
number than you would.

Neither of you is wrong. You are both reporting the same instant, in different
units.

---

## Predict

Before running anything, answer these:

1. If it is 21:00 where you are, is it 21:00 everywhere?
2. If you and a friend on another continent both look at the Moon "at 9pm",
   are you looking at the same time?
3. How many distinct moments does "3am on the last Sunday in October" describe
   in a country that uses daylight saving?

Write your answers down.

---

## Learn

### A bare time is not an instant

"21:00" is incomplete information. It is like saying "it is 15 degrees" without
saying Celsius or Fahrenheit — a number with the units left off.

To specify a real moment you need a time *and* a reference frame:

- `21:00 BST` — a specific instant
- `21:00 UTC` — a different specific instant
- `21:00` — not an instant at all

The Moon moves about half a degree — its own width — every hour. An ambiguous
time is an ambiguous sky.

### UTC: the shared reference

**Coordinated Universal Time** is the reference everyone measures against. It
does not change for daylight saving. It is the same everywhere on the planet
simultaneously. Every timezone is defined as an offset from it.

| Place | Offset | When it is 12:00 UTC |
|---|---|---|
| Los Angeles | −8 (−7 in summer) | 04:00 / 05:00 |
| New York | −5 (−4 in summer) | 07:00 / 08:00 |
| Reykjavík | +0 all year | 12:00 |
| London | +0 (+1 in summer) | 12:00 / 13:00 |
| Lagos | +1 all year | 13:00 |
| Mumbai | +5:30 all year | 17:30 |
| Kathmandu | +5:45 all year | 17:45 |
| Sydney | +10 (+11 in summer) | 22:00 / 23:00 |

Note that offsets are not all whole hours. India is +5:30, Nepal is +5:45,
parts of Australia are +8:45. Any code that assumes whole-hour offsets is
broken for well over a billion people.

### Why time zones exist at all

Before railways, every town kept its own solar time and nobody minded. Trains
made that impossible — a timetable needs one clock. Standard time zones were the
fix. [Why UTC exists](../background/why-utc-exists.md) tells the whole story;
it is genuinely a good one.

### Daylight saving time

Many countries shift their clocks seasonally. This creates two genuinely
horrible situations twice a year:

- **Spring forward:** clocks jump 02:00 → 03:00. The times between never
  happened. `02:30` on that date does not exist.
- **Autumn back:** clocks jump 03:00 → 02:00. The times between happen
  **twice**. `02:30` on that date is ambiguous — there are two of them, an
  hour apart.

This is why software that stores local timestamps has a bad October. UTC never
does either of these things.

Southern hemisphere countries shift in the opposite months. Many countries do
not shift at all. Some have changed policy recently. Do not hard-code any of
it — that is what the timezone database is for.

### The timezone database

Timezone rules are political and they change. Governments alter offsets, adopt
or abandon DST, and occasionally move a whole country across the date line.

The IANA timezone database records all of it, historically. Names look like:

```
Europe/Lisbon
America/Argentina/Cordoba
Africa/Nairobi
Asia/Kathmandu
Pacific/Auckland
```

The format is `Region/City` — a city rather than a country, because countries
sometimes span several zones or change their minds. Python reads this database
through `zoneinfo`, which Moonfield uses.

Avoid abbreviations like `EST` or `CST`. They are ambiguous — `CST` is used for
US Central, China Standard, and Cuba Standard time, which are hours apart.

---

## Run

```bash
moonfield doctor
```

Look at the time section:

```
  - System timezone: Europe/London
  - Local time: 2026-08-16 22:00:00 BST
  - UTC time:   2026-08-16 21:00:00 UTC
  - Offset from UTC: +1.00 hours
```

Now watch the same instant expressed two ways:

```bash
moonfield phase --date "2026-08-16T21:00" --timezone UTC
moonfield phase --date "2026-08-16T17:00" --timezone America/New_York
```

Same instant. Same Moon. Different local clocks.

---

## Change one variable

Run the same *local* wall-clock time in different zones:

```bash
moonfield phase --date "2026-08-16T21:00" --timezone Europe/London
moonfield phase --date "2026-08-16T21:00" --timezone Asia/Tokyo
```

These are **different instants** — nine hours apart — so the Moon has moved.
Check the illumination percentages: they differ slightly.

This is the whole lesson in two commands. "9pm" is not one moment.

---

## Validate

Pick any online world clock and compare it against `moonfield doctor`. If your
local time or offset is wrong, fix it before continuing — everything downstream
inherits the error.

---

## Explain

Why does Moonfield compute in UTC rather than your local time?

Because UTC is **monotonic and unambiguous**. It never repeats an hour, never
skips one, and never depends on politics. Local time does all three.

Why display local time at all, then? Because "the Moon rises at 20:47 UTC" is
useless to a person standing in a garden in Auckland. The computation needs
rigour; the human needs relevance. You do both, and you label them.

---

## Checkpoint

- [ ] I can explain why "21:00" is not a specific moment
- [ ] I know what UTC is and why it does not observe daylight saving
- [ ] I know some offsets are not whole hours
- [ ] I can name the two things DST does to local time twice a year
- [ ] I know why IANA names use cities rather than countries
- [ ] I understand the convention: compute in UTC, display local

## Try it yourself

1. Find your IANA timezone name. Is it the city you expected?
2. Run `moonfield phase` for the same UTC instant expressed in three zones.
   Confirm the Moon is identical.
3. Run it for the same local time in three zones. Confirm the Moon differs.
4. Find a country with a 45-minute offset. Why might a government choose that?
5. Look up when your country last changed its DST rules.

## Questions to think about

- If everyone used UTC and abandoned local time, what would actually break?
- Why do timezone boundaries follow political borders rather than meridians?
- China spans about 60 degrees of longitude and uses one timezone. What is
  solar noon like in its far west?
- Is there any moment when the whole world is on the same calendar date?

## Common questions

**Is UTC the same as GMT?**
Close enough for this curriculum, and different in principle. GMT is based on
Earth's rotation; UTC is atomic time kept within 0.9 seconds of it. They agree
to under a second.

**Why "UTC" and not "CUT" or "TUC"?**
A compromise between English "Coordinated Universal Time" and French "Temps
Universel Coordonné". Neither language got its acronym.

**What is Zulu time?**
UTC. Military and aviation phonetic alphabet — zone Z is offset zero. The `Z`
on the end of `2026-08-16T21:00:00Z` means exactly this.

## Getting stuck?

[Getting Unstuck](../troubleshooting/getting-unstuck.md) ·
[Discussions](https://github.com/Protonmatter/moonfield/discussions)

## Go deeper

- [Why UTC exists](../background/why-utc-exists.md)
- [Julian Day](julian-day.md) — what astronomers compute with instead
- Read `src/moonfield/time.py`

Next: [Julian Day](julian-day.md).
