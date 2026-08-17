# Scale

**Goal:** get the Earth-Moon distance right in your head. Almost every diagram
you have ever seen has lied to you about it.

---

## Predict

Take a ball about 10 cm across; that is Earth, roughly to scale.

1. How big is the Moon at that scale? Pick an object.
2. How far away do you put it? Guess in centimetres, before measuring.

Write both down. Most people are wrong about the second by a factor of five or
more.

---

## Run

```python
from moonfield import moon
import datetime as dt
from moonfield import time as mtime

p = moon.position(mtime.utc_now())
print(f"distance right now: {p.distance_km:,.0f} km")
```

The numbers:

| Quantity | Value | At 10 cm Earth |
|---|---|---|
| Earth diameter | 12,742 km | 10 cm |
| Moon diameter | 3,475 km | 2.7 cm |
| Mean distance | 384,400 km | **302 cm** |

**Three metres.** A tennis ball, three metres from a football.

Textbook diagrams almost always show the Moon a few Earth-diameters away,
because the true spacing does not fit on a page. That distortion quietly
sabotages your intuition about eclipses, tides and orbits.

Go and lay it out on the floor. It is worth the two minutes.

---

## The consequence you can check

At that distance the Moon subtends about 0.52°, half a degree. So does the Sun,
which is 400 times larger and 400 times further away. That coincidence is why
total solar eclipses exist at all, and why they are so nearly-not-quite.

```python
from moonfield import moon, sun
print(f"Moon: {moon.angular_diameter(mtime.utc_now()):.4f} deg")
print(f"Sun:  {sun.angular_diameter(mtime.utc_now()):.4f} deg")
```

Half a degree is about the width of your little fingernail at arm's length.
Check it against the real Moon tonight. Almost everyone thinks the Moon is
bigger than that, see the Moon Illusion in
[Go and look](../02-moon-phases/go-and-look.md).

---

## Checkpoint

- [ ] I know the Moon is ~30 Earth-diameters away, not 3
- [ ] I have laid it out physically, or at least paced it
- [ ] I know both Sun and Moon are about half a degree wide
- [ ] I can explain why that makes total eclipses possible

## Questions to think about

- All the crewed Moon landings crossed that three-metre gap. How does that
  change your sense of the achievement?
- The Moon recedes ~3.8 cm per year. Will there still be total solar eclipses in
  600 million years?

Next: [Tidal locking](tidal-locking.md).
