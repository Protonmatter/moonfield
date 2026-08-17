# Altitude and azimuth

**Goal:** understand the transformation from sky coordinates to your coordinates.

---

## Two coordinate systems

**Equatorial**: right ascension and declination. Fixed to the stars, the same
for everyone on Earth. This is what `sun.position()` and `moon.position()`
return.

**Horizontal**: altitude and azimuth. Angle above your horizon, and compass
bearing. Depends on where you are *and* what time it is.

Every "where do I look?" question is a conversion from the first to the second.

## The hour angle

The bridge is **local sidereal time**, how far the sky has turned at your
longitude:

```
hour_angle = local_sidereal_time - right_ascension
```

Hour angle is zero when the object is on your meridian, due south or north and
at its highest. Negative before, positive after. It effectively *is* a clock
running on star time.

Then two spherical-trigonometry formulae:

```
sin(altitude) = sin(lat)·sin(dec) + cos(lat)·cos(dec)·cos(H)

tan(azimuth) = sin(H) / (cos(H)·sin(lat) − tan(dec)·cos(lat))
```

That is the whole conversion. Everything else (refraction, parallax) is a
correction on top.

## Refraction

Air bends light, lifting objects slightly. It is negligible overhead and about
**0.57°** at the horizon, larger than the Sun itself.

The consequence: when you see the Sun touching the horizon, it is geometrically
already fully below it. Every sunrise you have ever watched, you were looking at
something that had not happened yet.

Moonfield defines sunrise at a geometric altitude of −0.833°: −0.567° for
refraction, −0.267° for the Sun's radius, since sunrise means the *upper limb*.

## Run

```bash
moonfield now
moonfield frame --facing SE
```

## Checkpoint

- [ ] I can name both coordinate systems and say what each is fixed to
- [ ] I know what hour angle means and when it is zero
- [ ] I know refraction is ~0.57° at the horizon
- [ ] I can explain why a "setting" Sun has already set

Next: [Why your latitude matters](why-latitude-matters.md).
