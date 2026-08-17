# Why phases happen

**Goal:** build the geometry physically, with objects you already own, before
touching any equations.

**Time:** 20 minutes, in a dark-ish room.

---

## Observe

You need:

- A lamp with the shade off, or a torch — this is the Sun
- A ball: an orange, a tennis ball, anything round — this is the Moon
- Your head — this is Earth

Put the lamp on one side of the room. Stand a few metres away, holding the ball
at arm's length.

---

## Predict

Before you move anything, answer:

1. How much of the ball is lit by the lamp at any moment?
2. When the ball is between you and the lamp, what do you see?
3. When the ball is on the far side of you from the lamp, what do you see?

Write them down.

---

## Run

Hold the ball at arm's length and slowly turn on the spot, keeping the ball
out at the same distance, so it circles you.

**Ball between you and the lamp.** The lit side faces away. You see a dark
disc. **New Moon.**

**Turn 90°.** The lamp is now off to one side. You see exactly half the ball
lit, split down the middle. **First quarter.**

**Turn until the ball is opposite the lamp**, over your shoulder, out of your
own shadow. Fully lit. **Full Moon.**

**Turn another 90°.** Half again, lit on the other side. **Last quarter.**

Keep going and you are back to new.

---

## Learn

### The one thing to hold on to

**Half the ball is lit the entire time.** You never changed that. The lamp
never moved, and it always illuminated exactly one hemisphere.

What changed is **how much of the lit half you could see**.

This is the whole of lunar phases. There is nothing else in it. The phase is not
a property of the Moon — it is a property of the *angle* between you, the Moon,
and the Sun.

That angle has a name, **elongation**, and it is the quantity every phase
calculation actually computes.

### The eight phases

| Elongation | Name | Lit fraction |
|---|---|---|
| 0° | New Moon | 0% |
| 45° | Waxing crescent | ~15% |
| 90° | First quarter | 50% |
| 135° | Waxing gibbous | ~85% |
| 180° | Full Moon | 100% |
| 225° | Waning gibbous | ~85% |
| 270° | Last quarter | 50% |
| 315° | Waning crescent | ~15% |

**Waxing** = growing, **waning** = shrinking. **Gibbous** is from the Latin for
humped.

"Quarter" means a quarter of the way through the cycle, not a quarter lit. A
first quarter Moon looks half lit. This confuses everyone once.

### Why phase controls when you see it

The elongation also fixes *when* the Moon is up, and this falls straight out of
the geometry:

| Phase | Rises | Highest | Sets |
|---|---|---|---|
| New | sunrise | noon | sunset |
| First quarter | noon | sunset | midnight |
| Full | sunset | midnight | sunrise |
| Last quarter | midnight | sunrise | noon |

A full Moon is opposite the Sun, so it must rise as the Sun sets. It cannot do
anything else. If someone shows you a photo of a full Moon high in a blue
midday sky, it is a composite.

This table is worth internalising. It turns "what phase is it?" into "when
should I go outside?"

### Why not an eclipse every month?

The obvious objection: if the Moon passes between Earth and Sun every new Moon,
why is there not a solar eclipse every month?

Because the Moon's orbit is tilted about 5.1° to Earth's orbital plane. Most
new Moons, the Moon passes above or below the Sun rather than across it. Only
when new Moon happens near one of the two **nodes** — the points where the
orbits cross — do you get an eclipse.

That tilt is why `moon.position()` returns an ecliptic *latitude* as well as a
longitude. Check it: it swings between about ±5.1°.

---

## Change one variable

Back to the lamp. Now tilt the ball's circular path slightly, so it passes
above the lamp on one side and below on the other.

Notice that the "new Moon" position no longer blocks the lamp — the ball goes
above it. That is why most new Moons are not eclipses. Adjust the tilt until it
does line up, and you have found a node.

---

## Validate

```bash
moonfield phase
moonfield now
```

Check the phase against the rise/set table above. If it says waxing gibbous, the
Moon should rise in the afternoon and set after midnight. Does `moonfield now`
agree?

Then check your own log from [Go and look](go-and-look.md).

---

## Explain

Here is a question worth sitting with: **why is a half Moon exactly half, and
not more or less?**

Because at first quarter the Sun-Earth-Moon angle is 90°. You are looking at
the terminator edge-on, straight down the boundary between lit and unlit. Any
other angle and you see some of the lit side curving toward or away from you.

And that is why the terminator on a crescent is *curved* while on a half Moon it
is *straight*. It is the same circle — the edge of the lit hemisphere — seen at
different angles. A circle seen at an angle is an ellipse; seen edge-on, a
straight line.

`phase.ascii_moon()` draws exactly this, and the code says so.

---

## Checkpoint

- [ ] I can demonstrate the phases with a ball and a lamp
- [ ] I can explain that half the Moon is always lit
- [ ] I know what elongation is
- [ ] I can name all eight phases and say roughly how lit each is
- [ ] I can say when a full Moon rises, without looking it up
- [ ] I can explain why there is not an eclipse every month
- [ ] I can explain why a half Moon has a straight terminator

## Try it yourself

1. Do the lamp experiment. Actually do it — it is much better than reading it.
2. Predict tonight's moonrise time from the phase alone, then check
3. From a photo of a crescent, work out which way the Sun is
4. Explain the phases to someone else using only your hands
5. Track `moon.position().ecliptic_latitude` over a month and find the nodes

## Questions to think about

- What would phases look like from a planet with two moons?
- What phase is Earth in, seen from the Moon, when we see a full Moon here?
- If the Moon's orbit were not tilted, how often would eclipses happen?
- Why do we always see the same face of the Moon? (Different question,
  different cause — tidal locking, module 03.)

## Common questions

**Is the dark part Earth's shadow?**
No, and this is the most common misconception in all of lunar astronomy. Earth's
shadow only touches the Moon during a lunar eclipse, which is rare. The dark
part of a normal Moon is simply the half not facing the Sun.

**Why can I sometimes faintly see the dark part?**
Earthshine — sunlight reflected off Earth onto the Moon. Best on a thin
crescent.

## Go deeper

- [Calculating a phase](calculating-phase.md)
- [Module 03 — The Earth-Moon system](../03-earth-moon-system/)

Next: [Calculating a phase](calculating-phase.md).
