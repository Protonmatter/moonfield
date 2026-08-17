# 04: Tides

Applied Earth-Moon physics, and the module where you meet a model that fails.

> **Nothing in this module is safe for navigation.** It is a teaching model.
> For anything that matters, use your national hydrographic office.

## Lessons

| # | Lesson | What you get |
|---|---|---|
| 1 | [What causes tides](what-causes-tides.md) | The two-bulge model, built properly |
| 2 | [The lunar day](lunar-day.md) | Why tide times march forward ~50 min/day |
| 3 | [Spring and neap](spring-and-neap.md) | Predicting tidal *range* from Moon phase |
| 4 | [Predict → Check → Explain](predict-check-explain.md) | **The core lab** |
| 5 | [Why local tides are hard](why-local-tides-are-hard.md) | Where the model gives up |

## Prerequisites

Modules [01](../01-time-and-place/), [02](../02-moon-phases/) and
[03](../03-earth-moon-system/). You need to be comfortable with the lunar day
and the Sun-Earth-Moon geometry.

## No coast nearby?

Not a problem. Lesson 4 supplies datasets from real tide stations around the
world, in `docs/04-tides/data/`. You can run the whole lab against Brest,
Hilo, Fremantle or the Bay of Fundy without leaving your desk.

If you *do* live near tidal water, use your own station; it is much better.

## Why this module matters more than it looks

Most of this curriculum builds models that work. This one builds a model that
is physically correct and practically useless, and then works out why.

That is not a detour. Knowing that a model can be *right about the physics* and
*wrong about your harbour* (and being able to say precisely which part is
missing) is one of the most transferable things here. It is the difference
between using a model and understanding one.

By the end you will have calibrated a physical model against real measurements,
which is, in miniature, exactly what an operational tide service does.
