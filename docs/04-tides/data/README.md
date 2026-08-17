# Tide station datasets

For learners without access to tidal water, and for anyone who wants to
compare coastlines that behave completely differently.

## The stations

| File | Station | Character | Typical range |
|---|---|---|---|
| `brest-2026-08.csv` | Brest, France | Clean semidiurnal | ~6 m |
| `hilo-2026-08.csv` | Hilo, Hawaii | Mixed, unequal highs | ~0.8 m |
| `fremantle-2026-08.csv` | Fremantle, Australia | Mostly diurnal | ~0.6 m |
| `burntcoat-2026-08.csv` | Burntcoat Head, Bay of Fundy | Resonant | ~16 m |

## Format

```csv
datetime_utc,kind,height_m
2026-08-16T05:12,high,6.42
2026-08-16T11:34,low,1.18
```

- `datetime_utc`: ISO 8601, always UTC
- `kind`: `high` or `low`
- `height_m`: metres above chart datum

## Important

These are **illustrative datasets** with the characteristic timing, range and
shape of each station, generated for teaching. They are not official
predictions and must not be used for navigation.

For real data, go to the source: SHOM (France), NOAA (USA), the Bureau of
Meteorology (Australia), Fisheries and Oceans Canada. Using the real thing is
better, and getting it is part of the lesson.

## Using them

```bash
moonfield tide compare --lat 48.383 --lon -4.495 --timezone UTC \
    --date "2026-08-16T12:00:00Z" \
    --observed 2026-08-16T04:06 \
    --observed 2026-08-16T16:32
```

Those two times are the high waters listed for 2026-08-16 in
`brest-2026-08.csv`, so you can check them against the file yourself. The
`--timezone UTC` matters: the `datetime_utc` column is in UTC, and without it
your observed times would be read on your own clock and the comparison would
be wrong by your offset.
