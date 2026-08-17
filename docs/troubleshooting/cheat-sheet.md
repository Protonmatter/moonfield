# Command cheat sheet

## Setup

```bash
moonfield doctor                              # check everything
moonfield config set-location --lat 51.48 --lon -0.00 --name "Greenwich"
moonfield config show
moonfield config path                          # where the config lives
moonfield config clear
```

**Longitude is east-positive.** New York −74, Tokyo +140.

## Daily use

```bash
moonfield now                                  # Sun and Moon right now
moonfield phase                                # phase, with ASCII art
moonfield phase --explain                      # both models, worked through
moonfield phase --date 2026-12-25 --no-art
moonfield sun                                  # rise, transit, set
moonfield sun --explain                        # incl. solar noon, equation of time
moonfield moon                                 # rise, transit, set, distance
moonfield seasons --explain                    # incl. the distance misconception
```

## Direction finding

```bash
moonfield frame --facing 90                    # what lies at bearing 90
moonfield frame --facing NE                    # compass points work too
```

## Tides

```bash
moonfield tide explain                         # the ten-step walkthrough
moonfield tide rough                           # rough prediction
moonfield tide rough --interval 2.0            # with your calibrated lag
moonfield tide compare --observed 2026-08-16T18:04 --observed 2026-08-17T06:26
```

## Longitude game

```bash
moonfield longitude --local-noon 12:34         # find your longitude
moonfield longitude --drift 4                  # clock drift consequences
moonfield longitude --reference               # the background
```

## Options that work almost everywhere

```
--date YYYY-MM-DD or an ISO datetime      compute for another moment
--lat AND --lon                           override saved location
--explain                                 show the working
--json                                    machine-readable output
```

`--lat` and `--lon` must be given **together**. Passing only one is an error
rather than a partial override, answering confidently about the wrong place
would be worse than refusing.

## Python

```python
import datetime as dt
from moonfield import sun, moon, phase, observer, tides, time as mtime
from moonfield.location import Location, load_location

here = load_location()
now = mtime.utc_now()

sun.position(now)                # SunPosition
moon.position(now)               # MoonPosition
phase.compute(now)               # PhaseInfo
observer.sun_rise_set(here, now) # RiseSet
observer.moon_position(here, now)
tides.rough(here, now)
```

## Development

```bash
python -m pytest                 # run the tests
python -m pytest -k phase -v     # just the phase tests
python -m pytest --cov=moonfield
ruff check src tests
pip install -e ".[dev]"
```
