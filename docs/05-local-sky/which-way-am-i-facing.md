# Which way am I facing?

**The lab for this module.** Find true north using the sky and arithmetic,
no compass, no phone.

**Time:** 20 minutes, needs sunshine or a visible Moon.

---

## The question

You are standing outside. Which direction are you facing?

Your phone's compass will answer instantly, and it will be a few degrees wrong,
and you will not know why. This lab answers it from first principles and tells
you your own error bar.

---

## Predict

Before doing anything:

1. Point at where you think north is. Note a landmark in that direction.
2. How confident are you, in degrees?

---

## Method 1: the Sun's azimuth

Ask Moonfield where the Sun is:

```bash
moonfield sun
```

```
Sun -- Brighton (50.8225N, 0.1372W)
2026-08-16 13:22 BST

  Altitude   52.4 deg above the horizon
  Azimuth   183.7 deg  (S)
```

Azimuth is measured clockwise from **true north**: 0° = N, 90° = E, 180° = S,
270° = W.

So: face the Sun. You are facing 183.7°. To face north, turn 183.7° to your
left, or equivalently, north is 176.3° clockwise from the Sun, which is very
nearly behind you.

**Never look directly at the Sun.** Use its shadow: a vertical stick's shadow
points *away* from the Sun, i.e. at azimuth 183.7 − 180 = 3.7°.

---

## Method 2: the shadow-tip method

No software at all.

1. Push a straight stick vertically into level ground
2. Mark the shadow tip. Wait 15 minutes. Mark it again.
3. The line from the first mark to the second points roughly **east**

This works because the Sun moves westward, so the shadow sweeps eastward. It is
crude (good to maybe 10°), but it needs nothing but a stick, and it works
anywhere on Earth including places where remembering "the Sun is due south at
noon" would get you badly lost.

---

## Method 3: local solar noon

The Sun is exactly on your meridian at local solar noon, due south in the
northern hemisphere, due **north** in the southern.

```bash
moonfield sun --explain
```

This prints your local solar noon, which is *not* 12:00 clock time. The
difference comes from your longitude within your timezone plus the equation of
time, both explained in
[module 01](../01-time-and-place/utc-and-timezones.md).

At that instant, the shadow of a vertical stick lies exactly along your
north-south line. This is the most accurate of the three.

---

## Method 4: at night

```bash
moonfield frame --facing 90
```

Give it a bearing, or a compass point like `NE`, and it lists what is in that
direction. Work backwards: find a bright object, ask Moonfield its azimuth, and
you have your reference.

---

## Check your prediction

Compare true north against the landmark you picked at the start. How far off
were you?

Then compare against your phone's compass. It will probably disagree by several
degrees, because:

- Magnetic north is not true north. The **magnetic declination** between them
  ranges from near zero to over 20° depending where you are, and it *drifts* by
  a fraction of a degree per year.
- Phone magnetometers are disturbed by nearby metal, speakers, and cars.

Your stick is more trustworthy than your phone, and now you know why.

---

## Explain

What just happened: you converted a position in a *global* coordinate system
(the Sun's celestial coordinates) into a *local* one (altitude and azimuth from
your exact spot), using nothing but your latitude, longitude and the time.

That transformation is the whole content of `observer.py`. Everything else in
that file is refinement.

---

## Checkpoint

- [ ] I found true north without a compass
- [ ] I know azimuth is clockwise from true north
- [ ] I know local solar noon is not 12:00, and why
- [ ] I know why a phone compass and true north disagree
- [ ] I know which of my methods was most accurate and roughly by how much

## Try it yourself

1. Do all four methods and compare. Which was best?
2. Mark your north-south line permanently and check it in six months
3. Look up your magnetic declination and predict your compass's error
4. Find true north from the Moon, at night
5. In the southern hemisphere: check the Sun really is due north at solar noon

## Questions to think about

- If you were dropped somewhere unknown, could you find your latitude from the
  Sun alone? (Yes, see [module 06](../06-seasons/).)
- Why does the shadow-tip method work at *any* latitude, including the tropics
  where "the Sun is due south at noon" is sometimes false?

## Go deeper

- [Altitude and azimuth](altitude-and-azimuth.md)
- Read `src/moonfield/observer.py`, function `to_horizontal`

Next: [Altitude and azimuth](altitude-and-azimuth.md).
