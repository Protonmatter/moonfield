# Spring and neap tides

**Goal:** predict the tidal *range* for the week from the Moon's phase alone.

---

## Learn

The Sun raises its own tide, about 46% the size of the Moon's. What matters is
whether the two line up.

- **New and full Moon**: Sun and Moon in line, bulges add → **spring tides**,
  largest range
- **First and last quarter**: at right angles, partly cancel → **neap tides**,
  smallest range

"Spring" has nothing to do with the season. It means *to spring up*.

Because springs happen at *both* new and full Moon, the cycle repeats twice per
month, roughly every 14.8 days, with about 7 days between a spring and the
next neap.

The combined range:

```
range ∝ √(1 + r² + 2r·cos(2 × elongation)),   r ≈ 0.46
```

Note the factor of 2. A bulge pointing at the Moon and one pointing away are
equally good at aligning with the Sun.

## Run

```bash
moonfield phase --no-art
moonfield tide rough
```

The `range factor` line: about 1.46 at springs, 0.54 at neaps.

## Try it yourself

1. Find the next spring tide from the phase alone, then verify with a tide table
2. Check whether the real spring/neap ratio at your port matches ~1.46/0.54
3. Springs often lag the full Moon by a day or two, find out why (friction)

## Checkpoint

- [ ] I can predict spring or neap from the Moon's phase
- [ ] I know why the cycle repeats twice a month
- [ ] I know "spring" is not about the season

Next: [Predict → Check → Explain](predict-check-explain.md).
