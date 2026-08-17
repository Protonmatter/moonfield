# What causes tides

**Goal:** understand why there are *two* bulges, and why the Sun loses to the
Moon despite being far more massive.

---

## Predict

Before reading:

1. The Moon pulls on the ocean. Why is there a high tide on the side of Earth
   *facing away* from the Moon?
2. The Sun is 27 million times more massive than the Moon. Which produces the
   bigger tide?

---

## Learn

### It is the difference, not the pull

Gravity weakens with distance. The near side of Earth is about 12,700 km closer
to the Moon than the far side, so it is pulled slightly harder. Earth's centre
is pulled a medium amount. The far side is pulled least.

Now work in the frame of Earth's centre — subtract the centre's acceleration
from everything. Relative to the centre:

- Near-side water is pulled **towards** the Moon
- Far-side water is left **behind**, so it moves away from the Moon

Both lift water away from the centre. **Two bulges, on opposite sides.**

The tide is caused by the *difference in pull across Earth*, not by the pull
itself. That single sentence resolves almost every tide misconception.

### Why the Sun loses

Gravitational force falls off as 1/r². But the *difference* across a body falls
off as 1/r³ — differentiate and see.

| | Mass vs Moon | Distance vs Moon | Force | Tidal effect |
|---|---|---|---|---|
| Moon | 1 | 1 | 1 | 1 |
| Sun | 27,000,000 | 390 | ~175 | ~0.46 |

The Sun pulls on Earth about 175 times harder than the Moon does. But it is so
far away that the *difference* across Earth's width is small, and the tidal
effect ends up at about 46% of the Moon's.

This is why the Moon rules the tides despite being a small rock.

The 1/r³ law is why tidal forces matter enormously close in — it is what tears
comets apart near Jupiter and what would stretch you unpleasantly near a black
hole.

### Two highs a day

Earth rotates through both bulges every day, so most coasts see two highs and
two lows. Not all — see [Why local tides are hard](why-local-tides-are-hard.md).

---

## Run

```bash
moonfield tide explain
```

## Checkpoint

- [ ] I can explain why there are two bulges, not one
- [ ] I know the tide comes from the *difference* in pull
- [ ] I know tidal effect falls off as 1/r³, not 1/r²
- [ ] I can explain why the Sun's tide is smaller despite its mass

## Questions to think about

- If Earth had no rotation, would there still be tides?
- The Moon is slowly moving away from Earth. What happens to tides over
  millions of years?
- Does the solid Earth have tides too? (Yes — about 30 cm. You are rising and
  falling twice a day.)

Next: [The lunar day](lunar-day.md).
