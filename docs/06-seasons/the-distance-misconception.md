# The distance misconception

**Goal:** disprove, with two commands, the most widely believed wrong idea in
everyday astronomy.

---

## The claim

> Seasons happen because Earth is closer to the Sun in summer and further away
> in winter.

Surveys of graduating university students, including science graduates, find
most give some version of this. It is intuitive, it sounds physical, and it is
wrong.

---

## Predict

Before checking:

1. When is Earth closest to the Sun?
2. How much does the Earth-Sun distance vary over a year, as a percentage?
3. What is happening in Australia when it is July in Europe?

---

## Disproof 1: the hemispheres disagree

```bash
moonfield seasons --explain
```

It is summer in Sydney when it is winter in London. **Simultaneously.**

Both cities are on the same planet, at the same distance from the Sun, at the
same instant. If distance caused seasons, the whole planet would have summer at
once.

That single observation is sufficient. Everything below is confirmation.

---

## Disproof 2: the timing is backwards

```python
import datetime as dt
from moonfield import sun, time as mtime

start = dt.datetime(2026, 1, 1, tzinfo=mtime.UTC)
samples = [(start + dt.timedelta(days=d),
            sun.position(start + dt.timedelta(days=d)).distance_au)
           for d in range(365)]
near = min(samples, key=lambda s: s[1])
far  = max(samples, key=lambda s: s[1])
print(f"perihelion {near[0]:%d %b}  {near[1]:.5f} AU")
print(f"aphelion   {far[0]:%d %b}  {far[1]:.5f} AU")
print(f"variation  {(far[1] - near[1]) / near[1] * 100:.2f}%")
```

Earth is **closest to the Sun in early January** (northern midwinter) and
furthest in early July. Exactly backwards for the northern hemisphere.

The variation is about **3.4%**, giving roughly 7% in received energy. Real, but
small, and swamped by the tilt effect.

---

## What actually causes them

Two things, both from the 23.4° axial tilt:

**1. The angle of the light.** Sunlight arriving at 60° above the horizon is
concentrated on a small patch of ground. The same beam arriving at 15° is
smeared over about four times the area. Same energy, quartered intensity.

```bash
moonfield sun --date 2026-06-21
moonfield sun --date 2026-12-21
```

Compare the noon altitudes. From Greenwich: about 62° versus about 15°.

**2. The length of the day.** Longer days mean more hours of heating and fewer
of cooling. At Greenwich, 16h39m in June against 7h50m in December.

These compound. Long days *and* steep sunlight, or short days *and* shallow
sunlight.

---

## Test it with a torch

Shine a torch straight down onto paper, small bright circle. Tilt it to 20°,
the light smears into a long dim ellipse. Same torch, same power, far less
energy per square centimetre.

That is summer and winter.

---

## Why the misconception survives

It is not stupid. It is a reasonable inference from a true fact: closer to a
heat source *is* warmer. The mistake is not the physics but a missing check,
"does this explain everything I know?" It does not explain Australia.

That habit (testing an explanation against a case it should also cover) is
the actual transferable skill here.

---

## Checkpoint

- [ ] I can disprove the distance explanation in one sentence
- [ ] I know Earth is closest to the Sun in January
- [ ] I know the distance varies ~3.4%
- [ ] I can name both tilt effects and explain how they compound
- [ ] I have compared noon altitudes on both solstices for my location

## Try it yourself

1. Compute noon solar altitude on both solstices for your latitude
2. Compute daylight length on both solstices
3. Work out the ratio of sunlight intensity between them (hint: sin of altitude)
4. Explain to someone why Australia has Christmas in summer
5. Find the latitude where seasons are weakest, and explain why

## Questions to think about

- The hottest weather is usually a month or two *after* the solstice. Why?
- Southern summer coincides with perihelion. Are southern summers hotter?
  (Look up how much of each hemisphere is ocean before answering.)
- If Earth's orbit were perfectly circular, would seasons change at all?

Next: [Axial tilt](axial-tilt.md).
