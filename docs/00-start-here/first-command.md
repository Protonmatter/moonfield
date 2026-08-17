# Your first command

**Prerequisites:** [Setup](setup.md) complete, `moonfield doctor` passing.

**Goal:** run a real astronomical calculation and understand every line of what
comes back.

---

## Observe

Before you type anything: **do you know what phase the Moon is in right now?**

Most people do not. It is directly overhead roughly half the time, it is the
brightest thing in the night sky, and most of us could not say whether it is
waxing or waning today.

Write down a guess. Any guess. You are about to find out.

---

## Predict

Write down:

1. Your guess at the phase (new, crescent, half, gibbous, full)
2. How confident you are, out of 10
3. Where you would look for it right now, if you went outside

Keep this. You will want it in a moment.

---

## Run

```bash
moonfield phase
```

Your output will show today's Moon, not the one below. To see exactly this
run, pin the instant the way the rest of this page does:

```bash
moonfield phase --date "2026-08-16T21:00:00Z" --timezone Europe/London --no-art
```

<!-- moonfield-check: phase --date 2026-08-16T21:00:00Z --timezone Europe/London --no-art -->

```
Moon phase for 2026-08-16 22:00 BST  (2026-08-16 21:00 UTC)

  Phase:        Waxing Crescent
  Illuminated:  19.9% of the visible disc
  Age:          4 days 3 hours 22 minutes since new Moon
  Trend:        waxing (growing)
  Distance:     387,412 km
```

---

## Learn: reading every line

### The heading

<!-- moonfield-check: phase --date 2026-08-16T21:00:00Z --timezone Europe/London --no-art -->

```
Moon phase for 2026-08-16 22:00 BST  (2026-08-16 21:00 UTC)
```

Two times, for one instant.

**BST** is British Summer Time, a civil timezone. **UTC** is Coordinated
Universal Time, the reference everyone shares. Moonfield always shows both,
because a time without a timezone is not a real instant. "9pm" happens at
twenty-something different moments around the world.

All the calculation happens in UTC. The local time is shown only because it is
what you actually live in. This convention (*compute in an unambiguous
representation, display local time where useful*) holds throughout the project.

Module 01 covers why this matters so much.

### Phase

<!-- moonfield-check: phase --date 2026-08-16T21:00:00Z --timezone Europe/London --no-art -->

```
  Phase:        Waxing Crescent
```

The traditional name. There are eight:

| Name | Roughly |
|---|---|
| New Moon | Not visible; between us and the Sun |
| Waxing Crescent | A growing sliver, visible in the evening |
| First Quarter | Half lit, growing. Up at sunset, sets at midnight |
| Waxing Gibbous | More than half, growing |
| Full Moon | Fully lit. Rises at sunset, sets at sunrise |
| Waning Gibbous | More than half, shrinking |
| Last Quarter | Half lit, shrinking. Rises at midnight |
| Waning Crescent | A shrinking sliver, visible before dawn |

**Waxing** means growing, **waning** means shrinking.

"Quarter" trips people up: a First Quarter Moon *looks* half lit. The name
refers to the Moon being a quarter of the way through its cycle, not a quarter
lit.

### Illuminated

<!-- moonfield-check: phase --date 2026-08-16T21:00:00Z --timezone Europe/London --no-art -->

```
  Illuminated:  19.9% of the visible disc
```

The fraction of the disc facing you that is sunlit.

Worth being precise about: **half the Moon is always lit.** The Sun is always
shining on it. What changes is how much of the lit half happens to be pointing
at us. "19.9% illuminated" means about a fifth of the face we can see is the
lit part.

### Age

<!-- moonfield-check: phase --date 2026-08-16T21:00:00Z --timezone Europe/London --no-art -->

```
  Age:          4 days 3 hours 22 minutes since new Moon
```

Time since the last new Moon. The full cycle takes about 29.5 days, so this
number runs from 0 to 29.5 and then resets.

### Trend

<!-- moonfield-check: phase --date 2026-08-16T21:00:00Z --timezone Europe/London --no-art -->

```
  Trend:        waxing (growing)
```

Which way it is going. Useful because a photograph of a crescent is ambiguous,
a waxing and a waning crescent look identical apart from which side is lit.

### Distance

<!-- moonfield-check: phase --date 2026-08-16T21:00:00Z --timezone Europe/London --no-art -->

```
  Distance:     387,412 km
```

The Moon's orbit is an ellipse, not a circle. It ranges from about 356,500 km
(perigee) to 406,700 km (apogee), a variation of about 14%. That is why some
full Moons look noticeably bigger.

### The drawing

The ASCII Moon shows the lit portion. The curved boundary between light and
dark is called the **terminator**, and it is a curve rather than a straight line
because you are looking at the edge of a sphere at an angle. A half Moon has a
straight terminator; a crescent has a curved one.

> **Southern hemisphere:** if you have set a southern location, the drawing
> flips. This is not a cosmetic touch. Seen from Sydney, the Moon genuinely
> appears rotated compared to London; a waxing crescent is lit on the *left*,
> not the right. Nothing changed about the Moon; you are standing upside down
> relative to the other observer.

### Coming up

```
  Coming up:
    First Quarter   2026-08-20 03:47 BST   (in 3 days 5 hours)
    Full Moon       2026-08-28 05:19 BST   (in 11 days 7 hours)
```

The next occurrence of each major phase, found by searching for the exact
moment the geometry lines up.

---

## Compare

Get out your prediction.

- Did you get the phase right?
- Were you more or less confident than you should have been?

Most people are wrong the first time, and *more confident than they should be*.
That gap between confidence and accuracy is worth noticing. It shows up
everywhere in this curriculum, and calibrating it is a large part of what
scientific practice actually is.

---

## Change one thing

Try a different date:

```bash
moonfield phase --date 2026-12-25
moonfield phase --date 2000-01-01
moonfield phase --date 1969-07-20
```

That last one is the day of the first Moon landing. Was the Moon full?

Now the important one:

```bash
moonfield phase --explain
```

This shows every intermediate value: the Julian Day, the Sun's position, the
Moon's position, the subtraction, the conversion to a percentage. It also shows
you a *second*, much simpler model, and how far apart the two are.

Do not worry about following all of it yet. Module 02 builds it up properly.
Notice, for now, that it can be followed; there is no step that says "and then
magic happens".

---

## Validate

Check against an independent source: a printed almanac, a newspaper weather
page, a planetarium program, or an observatory website.

Moonfield should agree to within a percent or two of illumination, and within a
few minutes on phase times.

If it disagrees badly, the most likely causes in order are:

1. Your computer's clock or timezone is wrong
2. You are comparing different instants (an almanac's "today" may be a
   different UTC day from yours)
3. A genuine bug, in which case please
   [open an issue](https://github.com/Protonmatter/moonfield/issues), including
   both numbers and your `moonfield doctor` output

---

## Checkpoint

- [ ] I can explain what "waxing" and "waning" mean
- [ ] I know why the output shows two different times
- [ ] I can explain why "illuminated" is not the same as "how much is lit"
- [ ] I can run `phase` for any date
- [ ] I know that `--explain` shows the working
- [ ] I noticed whether my confidence matched my accuracy

## Try it yourself

1. Find the phase on the day you were born
2. Find a date this year with a full Moon
3. Run `moonfield phase --date` for the same day across three different years;
   is the phase the same? Why not?
4. Compare `moonfield phase` today and in exactly 29 days. How close is it?
5. Find a date where the Moon is closest to Earth this year

## Questions to think about

- Why does the Moon have phases at all? What would have to be true for it not
  to?
- If half the Moon is always lit, why can we never see a "quarter" of it lit
  from a fully random angle?
- The Moon takes 27.3 days to go around Earth, but 29.5 days from full Moon to
  full Moon. Where do the extra two days come from?

That last question is module 02.

## Common questions

**Why does it say 19.9% rather than 20%?**
Because it computed it rather than rounding to something friendly. The extra
digit is a reminder that this is a calculation, not a lookup.

**Can I get output for another location?**
`phase` is the same everywhere on Earth; the illuminated fraction does not
depend on where you stand. Where the Moon *appears in your sky* very much does;
that is `moonfield now` and module 05.

**What if I have no internet?**
Everything works offline. There is no server. All the astronomy happens on your
machine.

## Getting stuck?

- `command not found: moonfield` → your virtual environment is not active. See
  [Getting Unstuck](../troubleshooting/getting-unstuck.md).
- Times look wrong by hours → [Time and place](../01-time-and-place/).
- Anything else → [Discussions](https://github.com/Protonmatter/moonfield/discussions).

## Go deeper

- [Module 02 (Moon phases](../02-moon-phases/)) build this calculation yourself
- [How accurate is Moonfield?](../background/accuracy.md)

Next: [Pre-flight check](pre-flight.md).
