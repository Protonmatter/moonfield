# Predict → Check → Explain

**The core tide lab.** Everything in this module has been building to it.

**Prerequisites:** [What causes tides](what-causes-tides.md),
[The lunar day](lunar-day.md), [Spring and neap](spring-and-neap.md).

**Time:** 45 minutes, plus a return visit if you are observing in person.

---

## The question

> **What tide do you think it will be at this time, where you are?**

Do not look anything up yet. That is the whole point of the exercise.

---

## Step 1: Assemble what you know

Write these down:

1. **The time and date** you are asking about
2. **Your location**, or a tide station you have chosen from `data/`
3. **The Moon's phase**: `moonfield phase`
4. **When the Moon crosses your meridian**: `moonfield moon`, the transit time

```bash
moonfield phase --no-art
moonfield moon
```

---

## Step 2: Predict, in writing, before checking anything

Write down, on paper or in a file:

| Question | Your answer |
|---|---|
| Is the tide currently rising or falling? | |
| When is the next high water? | |
| When is the next low water? | |
| Will this week's range be large or small? | |
| How confident are you, out of 10? | |
| What is your reasoning? | |

**The reasoning line is the most important one.** In a month you will not
remember what you were thinking, and "I was wrong" is far less useful than
"I was wrong *because* I assumed high water coincides with the Moon overhead."

Being wrong here is expected. It is not a failure state; it is the data.

---

## Step 3: What the simple model says

```bash
moonfield tide rough
```

```
ROUGH TIDE ESTIMATE -- FOR LEARNING ONLY, NOT FOR NAVIGATION
============================================================

Brighton (50.8225N, 0.1372W)
Time: 2026-08-16 13:00 BST  (2026-08-16 12:00 UTC)

The sky right now
-----------------
  - Moon crosses your meridian at 16:04 BST
  - between springs and neaps
  - Relative range factor: 1.09 (1.00 is the Moon alone; 1.46 at springs, 0.54 at neaps)
  - Lunitidal interval in use: 0.00 hours

Predicted events
----------------
  > Sun 16 Aug 16:04 BST  HIGH  (Moon overhead)
    Sun 16 Aug 22:16 BST  LOW   (quarter cycle after Moon overhead)
    Mon 17 Aug 04:26 BST  HIGH  (Moon underfoot)
```

Compare with your prediction. Did you agree with the model?

Note what the model has assumed: **high water arrives exactly when the Moon is
overhead.** Hold that thought.

---

## Step 4: Check reality

Now, and only now, get real data.

**If you live near tidal water**, find your nearest official tide station:

| Region | Authority |
|---|---|
| UK | UK Hydrographic Office / National Tidal and Sea Level Facility |
| USA | NOAA Tides and Currents |
| Canada | Fisheries and Oceans Canada |
| Australia | Bureau of Meteorology |
| France | SHOM |
| Elsewhere | Your national hydrographic office |

Better still: **go and look.** Photograph the same spot every hour for six
hours. That is a real observation, and it beats any table.

**If you do not live near tidal water**, use a supplied dataset:

```
docs/04-tides/data/brest-2026-08.csv        Brest, France: textbook semidiurnal
docs/04-tides/data/hilo-2026-08.csv         Hilo, Hawaii: mixed tides
docs/04-tides/data/fremantle-2026-08.csv    Fremantle, Australia: diurnal, tiny range
docs/04-tides/data/burntcoat-2026-08.csv    Bay of Fundy: 16 m range
```

Each has published high and low water times. Read the header; it says where the
numbers came from.

---

## Step 5: Quantify the discrepancy

Do not eyeball it. Get a number.

Use your own observed high waters if you have them. If you do not yet, this
repository ships real published tide tables you can borrow: the three times
below are actual high waters at Brest, taken from
[`data/brest-2026-08.csv`](data/brest-2026-08.csv).

```bash
moonfield tide compare --lat 48.383 --lon -4.495 --timezone UTC \
    --date "2026-08-16T12:00:00Z" \
    --observed 2026-08-16T04:06 \
    --observed 2026-08-16T16:32 \
    --observed 2026-08-17T04:56
```

<!-- moonfield-check: tide compare --lat 48.383 --lon -4.495 --timezone UTC --date 2026-08-16T12:00:00Z --observed 2026-08-16T04:06 --observed 2026-08-16T16:32 --observed 2026-08-17T04:56 -->

```
Comparison
----------
  Observed               Model predicted         Model error
  2026-08-16 04:06       2026-08-16 03:00          1.09 h early
  2026-08-16 16:32       2026-08-16 15:22          1.15 h early
  2026-08-17 04:56       2026-08-17 03:45          1.18 h early

What the difference is telling you
----------------------------------
Average model error: -1.14 hours
Spread across your samples: 0.09 hours
```

Read those two summary numbers carefully, because they are the whole point of
the step. The model is off by more than an hour every time, and it is off by
*almost exactly the same amount* every time. An error that large would be
alarming if it were random. An error that consistent is barely an error at
all: it is a missing constant, sitting there waiting to be measured.

---

## Step 6: Explain

Now the real work. Answer these in writing:

### Was the error consistent or scattered?

**Consistent**: every prediction off by roughly the same amount, in the same
direction. That is not noise. A steady offset is a *missing constant*, and a
missing constant is fixable.

**Scattered**: the error varies between tides. A single constant will not fix
that; something more structural is wrong.

### If consistent: you have measured the lunitidal interval

The **lunitidal interval** is the characteristic lag at your port between the
Moon crossing your meridian and high water actually arriving. It exists because
the tidal bulge is not a rigid thing that rides under the Moon; it is a wave,
and waves take time to travel across a shelf and up an estuary.

It is a property of *the place*, not of the sky. It cannot be computed from
astronomy. It has to be measured.

Feed yours back in:

```bash
moonfield tide rough --lat 48.383 --lon -4.495 --interval 1.14
```

Then compare again. The error should mostly vanish, because you have just
handed the model the one number it could never have worked out for itself.

**You have just calibrated a physical model with local measurements.** That is
the lesson.

### If scattered: something structural is missing

Likely causes:

- **A strong diurnal component.** Your coast has a once-daily as well as a
  twice-daily tide, so consecutive highs are genuinely unequal. Hilo shows this.
- **Shallow-water distortion.** In shallow water the crest travels faster than
  the trough, so the rise and fall take unequal times.
- **Weather.** A deep low-pressure system raises sea level by roughly 1 cm per
  millibar. Onshore wind piles water up. A storm surge can exceed the
  astronomical tide entirely.
- **Resonance.** If your basin's natural period is near 12.4 hours, the tide is
  amplified enormously and its phase is set by the basin, not the Moon.

### What information was missing?

The most useful question in the lab. The two-bulge model knows about the Moon,
the Sun and your latitude. It does not know:

- The shape of your coastline
- The depth of the water
- The natural period of your basin
- Friction
- Today's weather

Which of these do you think matters most where you are?

---

## Step 7: Compare four coastlines

Run the same lab against all four supplied datasets. They behave completely
differently:

| Station | Character | What it teaches |
|---|---|---|
| **Brest** | Clean semidiurnal, ~6 m | The model works best here |
| **Hilo** | Mixed, unequal highs | Diurnal component matters |
| **Fremantle** | Mostly diurnal, <1 m | Sometimes there is barely a tide |
| **Bay of Fundy** | 16 m range | Resonance dominates everything |

Same physics. Same Moon. Four completely different answers.

That is the most important observation in this module.

---

## Four things that are not the same

The lab forces a distinction that is easy to blur:

| Thing | What it is | How reliable |
|---|---|---|
| **Model prediction** | What theory says should happen | Depends entirely on the model |
| **Published prediction** | What a tide table forecasts | Very good; still a prediction |
| **Observation** | What the water actually did | Ground truth, with measurement error |
| **Uncertainty** | How far off any of these might be | Usually unstated, always present |

A tide table is not an observation. It is a *very good model*, fitted to years
of measurements at that specific station. Even it can be half a metre out in a
storm.

---

## Checkpoint

- [ ] I made a written prediction before checking anything
- [ ] I compared it against an authoritative source
- [ ] I quantified the discrepancy rather than eyeballing it
- [ ] I can say whether my error was consistent or scattered
- [ ] I know what a lunitidal interval is and why it cannot be computed
- [ ] I fed a measured interval back in and saw the error shrink
- [ ] I can name three things the model does not know about my coast
- [ ] I can distinguish model prediction, published prediction, and observation

## Try it yourself

1. Run the lab for all four supplied stations. Rank them by how badly the model
   does, and explain the ranking.
2. Find the lunitidal interval for a port near you. Is it published anywhere?
3. Predict a week of tides using only your measured interval. Check them.
4. Find a day when a storm made a real tide differ from its published
   prediction. How big was the surge?
5. Compare a spring high water with a neap high water. Is the ratio the ~1.3/0.7
   the model predicted?

## Questions to think about

- The two-bulge model is physically correct and practically useless. How can
  both be true at once?
- If harmonic analysis needs a year of measurements at every station, what
  happens at a coast nobody has ever instrumented?
- Your calibrated model now works for one port. What would it take to make it
  work for the next port along the coast?
- Where else in life do you use a model whose local calibration you have never
  checked?

## Go deeper

- [Why local tides are hard](why-local-tides-are-hard.md)
- `moonfield tide explain`: the full ten-step walkthrough
- Read `src/moonfield/tides.py`, the model and its stated limits

Next: [Why local tides are hard](why-local-tides-are-hard.md).
