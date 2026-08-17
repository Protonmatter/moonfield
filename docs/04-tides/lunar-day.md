# The lunar day

**Goal:** explain why tide times march forward by about 50 minutes a day.

---

## Predict

If Earth rotates once in 24 hours, and the tidal bulge points at the Moon,
shouldn't high tide be at the same time every day?

---

## Learn

While Earth turns once, the Moon moves along its orbit, about 13.2° per day.
So after 24 hours, the Moon is not where it was. Earth must turn about 13.2°
further to bring it back overhead.

```
13.2° ÷ 15°/hour ≈ 53 minutes
```

The **lunar day** is 24 h 50.5 min. That is the tidal clock, and it is why tide
tables march forward through the week instead of repeating.

This is the *same* effect as the synodic/sidereal month gap from
[module 02](../02-moon-phases/synodic-and-sidereal.md), one moving thing
measured against another moving reference.

## Run

```bash
moonfield tide rough
```

Look at the predicted events: consecutive highs are about 12 h 25 min apart,
half a lunar day.

## Checkpoint

- [ ] I can derive the 50-minute figure from the Moon's daily motion
- [ ] I know a lunar day is 24 h 50 min
- [ ] I can connect this to the synodic month and the sidereal day

Next: [Spring and neap](spring-and-neap.md).
