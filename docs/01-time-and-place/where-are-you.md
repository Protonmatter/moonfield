# Where are you?

**Goal:** define your observing position unambiguously, and get the signs right.

---

## Observe

Go outside. Which way is north?

Most people point confidently and are somewhere between slightly and completely
wrong. Try it before reading on, then check with a compass or a map.

---

## Learn

### Two numbers locate you

**Latitude** — how far north or south of the equator, from −90 (South Pole)
through 0 (equator) to +90 (North Pole).

**Longitude** — how far east or west of the prime meridian at Greenwich, from
−180 through 0 to +180.

Latitude has an obvious natural zero: the equator, where Earth's rotation
defines it. Longitude does not. There is nothing physically special about
Greenwich; it won a vote in 1884 because most of the world's shipping already
used charts based on it.

### Sign conventions, and the one mistake everyone makes

Moonfield, like all modern astronomy and mapping software, uses:

- **Latitude: north positive**, south negative
- **Longitude: east positive**, west negative

So:

| Place | Latitude | Longitude |
|---|---|---|
| Greenwich | +51.4779 | −0.0015 |
| New York | +40.7128 | **−74.0060** |
| Nairobi | −1.2921 | +36.8219 |
| Sydney | −33.8688 | +151.2093 |
| Ushuaia | −54.8019 | −68.3030 |
| Longyearbyen | +78.2232 | +15.6267 |

> **Everything west of Greenwich has a negative longitude.** The whole of the
> Americas. Most of western Europe. Much of west Africa. If you are in Chicago
> and you enter `+87.6298`, you have placed yourself in central China, and every
> result will be wrong by about twelve hours in a way that looks mysterious
> rather than obviously broken.

Some older navigation texts use west-positive. If you are reading historical
material, check which convention it uses before trusting a number.

### Formats you will encounter

The same place, four ways:

```
-33.8688                  decimal degrees, signed
33.8688 S                 decimal degrees with hemisphere
33° 52' 7.7" S            degrees, minutes, seconds
33 52 7.7 S               the same, without symbols
```

One degree of latitude is about 111 km everywhere. One arcminute is about
1.85 km — that is one nautical mile, which is where the unit comes from. One
arcsecond is about 31 metres.

Moonfield accepts all four formats:

```bash
moonfield config set-location --lat "33 52 7.7 S" --lon "151 12 33 E"
```

### Longitude degrees shrink with latitude

A degree of *latitude* is the same distance everywhere. A degree of *longitude*
is not: meridians converge at the poles.

```
distance ≈ 111.32 km × cos(latitude)
```

At the equator, 111 km. At 51°N (London), about 70 km. At 78°N
(Longyearbyen), about 23 km. At the pole, zero — all meridians meet.

This is why the Longitude Game asks for your latitude before converting a
longitude error into kilometres.

### Elevation and horizon

Two things Moonfield's core path simplifies:

**Elevation** raises your horizon. From a mountain you see slightly *past* the
geometric horizon, so the Sun rises a little earlier and sets a little later.
The effect is small — a few minutes at a few hundred metres.

**Your actual horizon** is almost certainly not flat. Hills, buildings and
trees block the lower sky. Moonfield computes rise and set against a
mathematically flat sea-level horizon. If a building sits to your east, the Sun
will appear later than predicted, and your prediction is not wrong — your
horizon is just not the one the model assumed.

Module 05 covers horizon profiles properly.

---

## Run

```bash
moonfield config set-location --lat 51.4779 --lon -0.0015 \
    --name "Greenwich" --timezone Europe/London

moonfield config show
```

Check the **hemisphere letters** in the output, not just the digits:

```
  - Latitude:  +51.4779 (north)
  - Longitude: -0.0015 (west)
```

---

## Change one variable

Flip your longitude sign deliberately and watch what happens:

```bash
moonfield now --lat 41.8781 --lon -87.6298 --date 2026-06-21T18:00
moonfield now --lat 41.8781 --lon 87.6298  --date 2026-06-21T18:00
```

Chicago versus a point in central China at the same instant. In one the Sun is
well up; in the other it is the middle of the night.

This is what the sign error looks like. Now you will recognise it.

---

## Validate

Find your coordinates on any map site: right-click your location. The first
number is latitude, the second longitude. Compare with what you saved.

Then sanity-check by prediction: run `moonfield sun` and compare sunrise and
sunset against a weather app for your town. They should agree within a few
minutes. If they are hours apart, your longitude is wrong. If they are
symmetric but wrong in day length, your latitude is wrong.

---

## Checkpoint

- [ ] I know my own latitude and longitude
- [ ] I know north and east are positive
- [ ] I know places west of Greenwich have negative longitude
- [ ] I can read degrees-minutes-seconds format
- [ ] I know a longitude degree shrinks as you go poleward
- [ ] I know Moonfield assumes a flat sea-level horizon
- [ ] I have sanity-checked my location against sunrise times

## Try it yourself

1. Enter your location in decimal degrees, then in DMS. Confirm they match.
2. Find three cities on nearly the same latitude as you, on different
   continents. Compare their day lengths — should be nearly identical.
3. Find a city at nearly your longitude but the opposite hemisphere. Compare
   sunrise times, then day lengths.
4. Compute the width of one longitude degree at your latitude.

## Questions to think about

- Why did longitude need an international conference and latitude did not?
- If you stand exactly on the North Pole, what is your longitude?
- Antarctic research stations sit at extreme southern latitudes where all
  timezones converge. How do they decide what time to keep?

## Go deeper

- [Why UTC exists](../background/why-utc-exists.md)
- [The Longitude Game](longitude-game.md)
- Read `src/moonfield/location.py`

Next: [The Longitude Game](longitude-game.md).
