# Glossary

Plain definitions. Where a term has a common misunderstanding, it is flagged.

## Time

**UTC**: Coordinated Universal Time. The global reference. Not a timezone;
the thing timezones are offsets from.

**Local civil time**: the clock on your wall, including daylight saving.

**Julian Day (JD)**: days elapsed since 1 January 4713 BC noon, as a decimal.
Turns date arithmetic into ordinary subtraction. J2000.0 = JD 2451545.0.

**Sidereal time**: time measured against the stars rather than the Sun. A
sidereal day is 23h 56m 04s.

**Equation of time**: the difference between sundial time and clock time,
swinging ±16 minutes over the year. Caused by Earth's elliptical orbit and
axial tilt.

**Tropical year**: 365.2422 days, equinox to equinox. Why leap years exist.

**Leap second**: an occasional extra second keeping UTC aligned with Earth's
slightly irregular rotation.

## Position

**Latitude**: degrees north (+) or south (−) of the equator.

**Longitude**: degrees east or west of Greenwich. **Moonfield uses
east-positive**, so New York is −74, Tokyo is +140. Getting this sign wrong is
the single most common setup error.

**Altitude**: angle above your horizon. 0° = horizon, 90° = overhead.

**Azimuth**: compass bearing, clockwise from **true** north. 0° N, 90° E,
180° S, 270° W.

**Zenith**: the point directly overhead.

**Meridian**: the north-south line through your zenith. Objects are highest
when crossing it.

**Right ascension / declination**: the sky's own coordinates, fixed to the
stars. Declination is celestial latitude; right ascension is celestial
longitude.

**Ecliptic**: the plane of Earth's orbit, and so the Sun's apparent path.

**Hour angle**: how far an object is past your meridian, in degrees or hours.
Zero at transit.

## The Moon

**Phase**: how much of the lit half faces you. A consequence of geometry, not
a property of the Moon.

**Elongation**: the Sun-Earth-Moon angle. 0° new, 180° full.

**Synodic month**: 29.53 days, new Moon to new Moon.

**Sidereal month**: 27.32 days, one true orbit against the stars.

**Perigee / apogee**: closest / furthest points of the Moon's orbit.

**Libration**: the Moon's apparent rocking, letting us see 59% of its surface.

**Terminator**: the line between lit and unlit. Curved on a crescent, straight
at half Moon.

**Earthshine**: sunlight reflected off Earth faintly lighting the Moon's dark
part.

**Waxing / waning**: growing / shrinking.

**Gibbous**: more than half lit, less than full.

## Tides

**Spring tide**: largest range, at new and full Moon. Nothing to do with the
season.

**Neap tide**: smallest range, at the quarters.

**Lunar day**: 24h 50m. The tidal clock.

**Lunitidal interval**: the lag at your port between the Moon crossing your
meridian and high water. A property of the place; must be measured, cannot be
computed.

**Semidiurnal / diurnal / mixed**: two highs a day / one / two unequal.

**Chart datum**: the reference level tide heights are measured from.

**Harmonic analysis**: how real tide prediction works: decompose a long
measured record into sine waves at known astronomical frequencies.

**Storm surge**: sea level change from weather, not astronomy. Can exceed the
astronomical tide.

## Seasons

**Axial tilt / obliquity**: 23.44°. The cause of seasons.

**Solstice / equinox**: instants when the Sun's longitude reaches 90°/270° and
0°/180°.

**Perihelion / aphelion**: Earth's closest / furthest approach to the Sun.
Early January and early July, note that these do *not* line up with the
seasons.

## Modelling

**Model**: a simplification that predicts something. All models are wrong;
the question is whether they are wrong in a way that matters for your purpose.

**Approximation**: a deliberate simplification with a known cost.

**Prediction**: what a model says will happen. Not an observation.

**Observation**: what actually happened. Also has error bars.

**Validation**: comparing prediction against observation.

**Calibration**: adjusting a model using local measurements, as with the
lunitidal interval.

**Ephemeris**: a table or algorithm giving positions of celestial bodies over
time.
