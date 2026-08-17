"""The ``moonfield`` command line.

Design rules for this file:

* Every command works with no arguments, or explains exactly what it needs.
* Every error message says what to do next, not just what went wrong.
* ``--explain`` shows the intermediate numbers, because a result you cannot
  check is a result you have to take on faith.
* No command silently assumes the northern hemisphere, the United States,
  a sea-level horizon, daylight saving time, or clear skies.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import math
import platform
import sys
from pathlib import Path

from moonfield import __version__, observer
from moonfield import moon as moon_engine
from moonfield import phase as phase_engine
from moonfield import sun as sun_engine
from moonfield import tides as tide_engine
from moonfield import time as mtime
from moonfield.location import (
    Location,
    config_path,
    load_config,
    load_location,
    parse_coordinate,
    save_config,
    save_location,
)

BULLET = "  - "


# ---------------------------------------------------------------------------
# Small output helpers
# ---------------------------------------------------------------------------


def heading(text: str) -> str:
    return f"\n{text}\n{'-' * len(text)}"


def _fail(message: str, hint: str | None = None) -> int:
    print(f"Error: {message}", file=sys.stderr)
    if hint:
        print(f"\nWhat to try: {hint}", file=sys.stderr)
    return 1


def _need_location(args) -> Location | None:
    """Resolve the observing location from flags, then saved config."""
    # Half an override is never what anyone meant. Silently falling back to
    # the saved location here would answer confidently about the wrong place,
    # which is the worst possible failure for a tool people use to check
    # their own observations.
    if (args.lat is None) != (args.lon is None):
        missing = "--lon" if args.lon is None else "--lat"
        given = "--lat" if args.lon is None else "--lon"
        print(
            f"Error: you gave {given} but not {missing}.\n"
            "\n"
            "Give both, or neither. Moonfield will not guess half a position,\n"
            "because answering about the wrong place is worse than refusing.\n"
            "\n"
            "    moonfield now --lat 51.4779 --lon -0.0015\n"
            "\n"
            "Longitude is EAST-positive: west of Greenwich is negative.",
            file=sys.stderr,
        )
        return None

    if args.lat is not None and args.lon is not None:
        try:
            return Location(
                latitude=parse_coordinate(str(args.lat)),
                longitude=parse_coordinate(str(args.lon)),
                name=getattr(args, "place", None) or "your location",
                timezone=getattr(args, "timezone", None),
            )
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return None

    saved = load_location()
    if saved is not None:
        return saved

    print(
        "This command needs to know where you are.\n"
        "\n"
        "Save your location once:\n"
        "    moonfield config set-location --lat 51.4779 --lon -0.0015 "
        '--name "Greenwich" --timezone Europe/London\n'
        "\n"
        "Or pass it just for this command:\n"
        "    moonfield now --lat 51.4779 --lon -0.0015\n"
        "\n"
        "Latitude is north-positive, longitude is EAST-positive.\n"
        "If you are west of Greenwich, your longitude is negative.\n"
        "You can find your coordinates on any map site by right-clicking "
        "where you are.",
        file=sys.stderr,
    )
    return None


def _when(args) -> _dt.datetime:
    """Resolve the instant a command should use.

    A time you type without a zone -- ``--date 2026-08-16T21:30`` -- is read
    as civil time in the first of these that exists: ``--timezone``, your
    saved location's timezone, your computer's own. Someone typing a bare
    time at a terminal means that time where they are standing.

    The library underneath makes the opposite choice and reads a bare time as
    UTC, so that its results do not depend on whose machine ran it. Both are
    right for their audience; the translation happens here.
    """
    text = getattr(args, "date", None)
    if not text:
        return mtime.utc_now()
    zone = getattr(args, "timezone", None)
    if zone is None:
        saved = load_location()
        zone = saved.timezone if saved else None
    if zone is None:
        zone = mtime.resolve_zone(None)
    return mtime.parse_datetime(text, zone)


def _display_zone(args, location: Location | None = None) -> _dt.tzinfo:
    """Decide which timezone to *show* results in.

    In order: an explicit --timezone, then your saved location's, then your
    computer's own. --timezone comes first because you asked for it directly,
    and it has to work on commands like `phase` that need no location at all
    -- otherwise the flag is advertised in the help of every command and
    quietly does nothing on most of them.

    A zone we cannot find is reported rather than swallowed. Falling back to
    UTC without a word means the times on screen are wrong by whole hours and
    look perfectly reasonable, which is the worst way for a teaching tool to
    fail.
    """
    name = getattr(args, "timezone", None)
    if name:
        resolved = mtime.resolve_zone(name)
        if getattr(resolved, "key", None) != name:
            print(
                f"Warning: '{name}' is not in this system's timezone database, "
                "so times below are shown in UTC.\n"
                "Names look like 'Europe/Lisbon' or 'America/Argentina/Cordoba'. "
                "On Windows, try: pip install tzdata",
                file=sys.stderr,
            )
        return resolved
    if location is not None:
        return location.zone
    return mtime.resolve_zone(None)


def _fmt(when: _dt.datetime | None, zone: _dt.tzinfo) -> str:
    if when is None:
        return "--:--"
    local = when.astimezone(zone)
    label = local.strftime("%Z") or "UTC"
    return f"{local.strftime('%H:%M')} {label}"


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------


def cmd_doctor(args) -> int:
    """Check that the environment is ready, and say what to fix if not."""
    print("Moonfield doctor")
    print("================")
    print("\nThis checks your setup. It does NOT prove your computer's clock is")
    print("accurate in absolute terms -- see the note at the end.")

    ok = True

    print(heading("Python"))
    version = sys.version_info
    print(f"{BULLET}Python {platform.python_version()} at {sys.executable}")
    if version < (3, 10):
        ok = False
        print(f"{BULLET}PROBLEM: Moonfield needs Python 3.10 or newer.")
        print(f"{BULLET}Fix: install a newer Python from python.org, then remake")
        print("       your virtual environment.")
    else:
        print(f"{BULLET}Version is new enough (need 3.10+). OK")

    print(heading("Virtual environment"))
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if in_venv:
        print(f"{BULLET}Active, at {sys.prefix}. OK")
    else:
        print(f"{BULLET}Not detected.")
        print(f"{BULLET}This is not fatal, but a virtual environment keeps this")
        print("       project's packages separate from everything else.")
        print(f"{BULLET}See docs/00-start-here/setup.md for how to make one.")

    print(heading("Moonfield"))
    print(f"{BULLET}Version {__version__}")
    print(f"{BULLET}Installed from {Path(__file__).resolve().parent}")

    print(heading("Platform"))
    print(f"{BULLET}{platform.system()} {platform.release()} ({platform.machine()})")

    print(heading("Time"))
    now = mtime.utc_now()
    local = now.astimezone()
    zone_name = mtime.local_zone_name()
    print(f"{BULLET}System timezone: {zone_name}")
    print(f"{BULLET}Local time: {local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"{BULLET}UTC time:   {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    offset = local.utcoffset() or _dt.timedelta(0)
    hours = offset.total_seconds() / 3600
    print(f"{BULLET}Offset from UTC: {hours:+.2f} hours")
    print(f"{BULLET}Julian Day now: {mtime.julian_day(now):.5f}")

    # Importing zoneinfo always succeeds -- it has been in the standard
    # library since Python 3.9. What can be missing is the IANA timezone
    # *database* it reads, which Windows does not ship. So the only honest
    # test is to look a real zone up and see whether it is found.
    try:
        from zoneinfo import ZoneInfo

        ZoneInfo("Europe/London")
        print(f"{BULLET}Timezone database available. OK")
    except Exception:
        ok = False
        print(f"{BULLET}PROBLEM: the IANA timezone database is missing.")
        print(f"{BULLET}Without it, any --timezone you ask for falls back to")
        print("       UTC, so displayed times can be wrong by hours.")
        print(f"{BULLET}Fix: pip install tzdata")

    print(heading("Location"))
    location = load_location()
    if location:
        print(f"{BULLET}{location.describe()}")
        print(f"{BULLET}Hemisphere: {location.hemisphere}")
        print(f"{BULLET}Timezone for display: {location.timezone or 'system default'}")
        print(f"{BULLET}Saved in {config_path()}")
    else:
        print(f"{BULLET}Not set yet. Commands that need it will say so.")
        print(f"{BULLET}Set it with:")
        print("       moonfield config set-location --lat <LAT> --lon <LON>")

    print(heading("A quick self-test"))
    try:
        info = phase_engine.compute(now)
        print(f"{BULLET}Phase engine ran: {info.name}, "
              f"{info.illumination_percent:.1f}% illuminated. OK")
    except Exception as exc:  # pragma: no cover - defensive
        ok = False
        print(f"{BULLET}PROBLEM: the phase engine raised {exc!r}")
        print(f"{BULLET}Fix: please open an issue with this whole output.")

    print(heading("About your clock"))
    print("Everything above is a CONFIGURATION check. It confirms that your")
    print("computer knows which timezone it is in and can do the arithmetic.")
    print("It cannot tell you whether your clock is actually set correctly.")
    print("")
    print("If your predictions are consistently off by a few minutes, check your")
    print("clock against an external time source. Most operating systems have a")
    print('setting called something like "set time automatically".')

    print()
    if ok:
        print("Result: everything essential is working.")
        if not location:
            print("Next step: set your location, then run 'moonfield phase'.")
        else:
            print("Next step: run 'moonfield phase' or 'moonfield now'.")
    else:
        print("Result: something needs fixing. See the PROBLEM lines above.")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# phase
# ---------------------------------------------------------------------------


def cmd_phase(args) -> int:
    when = _when(args)
    if getattr(args, "lat", None) is not None or getattr(args, "lon", None) is not None:
        location = _need_location(args)
        if location is None:
            return 1
    else:
        location = load_location()
    southern = bool(location and location.latitude < 0)
    zone = _display_zone(args, location)
    info = phase_engine.compute(when)

    print(f"Moon phase for {mtime.format_instant(when, zone)}")
    print()
    print(f"  Phase:        {info.name}")
    print(f"  Illuminated:  {info.illumination_percent:.1f}% of the visible disc")
    print(f"  Age:          {mtime.format_duration(info.age_days)} since new Moon")
    print(f"  Trend:        {'waxing (growing)' if info.waxing else 'waning (shrinking)'}")
    print(f"  Distance:     {info.distance_km:,.0f} km")

    if not args.no_art:
        print()
        art = phase_engine.ascii_moon(info.illumination, info.waxing, southern=southern)
        for line in art.splitlines():
            print("  " + line)
        if southern:
            print("\n  (drawn as seen from the southern hemisphere)")

    print("\n  Coming up:")
    for name, (moment, days) in info.next_phases.items():
        stamp = moment.astimezone(zone)
        label = stamp.strftime("%Y-%m-%d %H:%M %Z").rstrip() or stamp.strftime(
            "%Y-%m-%d %H:%M UTC"
        )
        print(f"    {name:<15} {label}   (in {mtime.format_duration(days)})")

    if args.explain:
        _explain_phase(info, when)
    return 0


def _explain_phase(info, when) -> None:
    sun_pos = sun_engine.position(info.julian_day)
    moon_pos = moon_engine.position(info.julian_day)

    print(heading("How that number was worked out"))
    print("\nStep 1 -- pin down the instant.")
    print(f"  Your input becomes {mtime.ensure_utc(when).strftime('%Y-%m-%d %H:%M:%S')} UTC,")
    print(f"  which is Julian Day {info.julian_day:.6f}.")
    print("  A Julian Day is just a running count of days, so no calendar")
    print("  awkwardness (leap years, unequal months) can creep into the maths.")

    print("\nStep 2 -- find the Sun.")
    print(f"  Ecliptic longitude: {sun_pos.apparent_longitude:.4f} deg")
    print(f"  Distance:           {sun_pos.distance_au:.6f} AU")

    print("\nStep 3 -- find the Moon.")
    print(f"  Ecliptic longitude: {moon_pos.ecliptic_longitude:.4f} deg")
    print(f"  Ecliptic latitude:  {moon_pos.ecliptic_latitude:+.4f} deg")
    print(f"  Distance:           {moon_pos.distance_km:,.1f} km")

    print("\nStep 4 -- subtract.")
    print("  Elongation = Moon longitude - Sun longitude")
    print(f"             = {moon_pos.ecliptic_longitude:.4f} - {sun_pos.apparent_longitude:.4f}")
    print(f"             = {info.elongation:.4f} deg  (wrapped into 0-360)")
    print("  0 deg is new Moon, 90 first quarter, 180 full, 270 last quarter.")

    print("\nStep 5 -- convert to a lit fraction.")
    print(f"  Phase angle (Sun-Moon-Earth): {info.phase_angle:.4f} deg")
    print("  Illumination = (1 + cos(phase angle)) / 2")
    print(f"               = (1 + cos({info.phase_angle:.4f})) / 2")
    print(f"               = {info.illumination:.6f}  ->  {info.illumination_percent:.1f}%")

    print(heading("The simple model, for comparison"))
    print("  Days since the reference new Moon, modulo 29.530589:")
    print(f"    simple age  = {info.simple_age_days:.4f} days")
    print(f"    true age    = {info.age_days:.4f} days")
    print(f"    difference  = {info.model_disagreement_hours:+.2f} hours")
    print()
    if abs(info.model_disagreement_hours) < 2:
        print("  The two models happen to agree closely right now.")
    else:
        print("  The gap is real, not a bug. The simple model assumes the Moon")
        print("  moves at a constant rate. It does not: its orbit is an ellipse,")
        print("  so it runs fast near perigee and slow near apogee. Individual")
        print("  cycles range from about 29.27 to 29.83 days.")

    print(heading("What this model still ignores"))
    print(f"{BULLET}We truncated the lunar series, leaving errors of a few")
    print("       tens of arcseconds in the Moon's position.")
    print(f"{BULLET}The illumination is for a smooth sphere. The real Moon has")
    print("       mountains, so the terminator is ragged.")
    print(f"{BULLET}Near new Moon the lit fraction is tiny but not zero, and")
    print("       earthshine can make the dark part faintly visible anyway.")
    print(f"{BULLET}This is a geocentric figure -- computed for Earth's centre,")
    print("       not your rooftop. For phase the difference is negligible.")


# ---------------------------------------------------------------------------
# now / sun / moon / frame
# ---------------------------------------------------------------------------


def cmd_now(args) -> int:
    location = _need_location(args)
    if location is None:
        return 1
    when = _when(args)
    zone = _display_zone(args, location)

    print(f"Sky report for {location.describe()}")
    print(f"Time: {mtime.format_instant(when, zone)}")

    sun_h = observer.sun_position(location, when)
    moon_h = observer.moon_position(location, when)
    info = phase_engine.compute(when)
    sun_rs = observer.sun_rise_set(location, when)
    moon_rs = observer.moon_rise_set(location, when)

    print(heading("Sun"))
    print(f"{BULLET}{sun_h.describe()}")
    print(f"{BULLET}Rise {_fmt(sun_rs.rise, zone)}   "
          f"Noon {_fmt(sun_rs.transit, zone)}   "
          f"Set {_fmt(sun_rs.setting, zone)}")
    if sun_rs.transit_altitude is not None:
        print(f"{BULLET}Highest today: {sun_rs.transit_altitude:.1f} deg above the horizon")
    if sun_rs.note:
        print(f"{BULLET}Note: the Sun {sun_rs.note}")

    print(heading("Moon"))
    print(f"{BULLET}{moon_h.describe()}")
    print(f"{BULLET}{info.name}, {info.illumination_percent:.0f}% illuminated")
    print(f"{BULLET}Rise {_fmt(moon_rs.rise, zone)}   "
          f"Transit {_fmt(moon_rs.transit, zone)}   "
          f"Set {_fmt(moon_rs.setting, zone)}")
    if moon_rs.note:
        print(f"{BULLET}Note: the Moon {moon_rs.note}")

    print(heading("What you should be able to see"))
    if moon_h.is_up and sun_h.altitude < -6:
        print("The Moon is up and the sky is dark. Go and look "
              f"{moon_h.compass} and about {moon_h.altitude:.0f} degrees up.")
    elif moon_h.is_up and sun_h.is_up:
        print("The Moon is up but so is the Sun. A gibbous or crescent Moon in")
        print("daylight is a common sight -- look carefully, it is faint.")
    elif moon_h.is_up:
        print("The Moon is up during twilight. Look "
              f"{moon_h.compass}, about {moon_h.altitude:.0f} degrees above the horizon.")
    else:
        print("The Moon is below your horizon right now.")
        if moon_rs.rise and moon_rs.rise > when:
            print(f"It rises at {_fmt(moon_rs.rise, zone)}.")

    print("\nRemember: 'degrees above the horizon' is easy to estimate with your")
    print("hand at arm's length. A fist is about 10 degrees; a thumb about 2.")
    return 0


def cmd_sun(args) -> int:
    location = _need_location(args)
    if location is None:
        return 1
    when = _when(args)
    pos = sun_engine.position(when)
    horiz = observer.sun_position(location, when)
    rs = observer.sun_rise_set(location, when)
    zone = _display_zone(args, location)

    print(f"Sun from {location.describe()}")
    print(f"Time: {mtime.format_instant(when, zone)}")
    print(heading("In your sky"))
    print(f"{BULLET}{horiz.describe()}")
    print(heading("On the celestial sphere"))
    print(f"{BULLET}Right ascension: {pos.right_ascension:.4f} deg")
    print(f"{BULLET}Declination:     {pos.declination:+.4f} deg")
    print(f"{BULLET}Distance:        {pos.distance_au:.6f} AU "
          f"({pos.distance_km:,.0f} km)")
    print(f"{BULLET}Angular size:    {pos.angular_diameter * 60:.2f} arcminutes")
    print(f"{BULLET}Equation of time: {pos.equation_of_time:+.2f} minutes")
    print("       (how far real solar noon is from clock noon, before timezones)")

    print(heading("Today"))
    print(f"{BULLET}Sunrise      {_fmt(rs.rise, zone)}")
    print(f"{BULLET}Solar noon   {_fmt(rs.transit, zone)}")
    print(f"{BULLET}Sunset       {_fmt(rs.setting, zone)}")
    if rs.rise and rs.setting:
        length = (rs.setting - rs.rise).total_seconds() / 3600.0
        if length < 0:
            length += 24
        print(f"{BULLET}Day length   {length:.2f} hours")
    if rs.note:
        print(f"{BULLET}Note: the Sun {rs.note}")

    if args.explain:
        print(heading("Where the declination comes from"))
        print("Earth's axis is tilted 23.44 degrees from the perpendicular to its")
        print("orbit. The Sun's declination is the latitude directly beneath it,")
        print("and it traces that tilt out over a year:")
        print(f"{BULLET}+23.44 around 21 June (overhead at the Tropic of Cancer)")
        print(f"{BULLET}0 at the equinoxes (overhead at the equator)")
        print(f"{BULLET}-23.44 around 21 December (Tropic of Capricorn)")
        print(f"\nToday it is {pos.declination:+.2f}, so the Sun passes overhead at")
        print(f"latitude {pos.declination:+.2f}.")
    return 0


def cmd_moon(args) -> int:
    location = _need_location(args)
    if location is None:
        return 1
    when = _when(args)
    pos = moon_engine.position(when)
    horiz = observer.moon_position(location, when)
    rs = observer.moon_rise_set(location, when)
    info = phase_engine.compute(when)
    zone = _display_zone(args, location)

    print(f"Moon from {location.describe()}")
    print(f"Time: {mtime.format_instant(when, zone)}")
    print(heading("In your sky"))
    print(f"{BULLET}{horiz.describe()}")
    print(f"{BULLET}{info.name}, {info.illumination_percent:.1f}% illuminated")

    print(heading("On the celestial sphere"))
    print(f"{BULLET}Right ascension:   {pos.right_ascension:.4f} deg")
    print(f"{BULLET}Declination:       {pos.declination:+.4f} deg")
    print(f"{BULLET}Ecliptic latitude: {pos.ecliptic_latitude:+.4f} deg")
    print(f"{BULLET}Distance:          {pos.distance_km:,.0f} km")
    print(f"{BULLET}Angular size:      {pos.angular_diameter * 60:.2f} arcminutes")
    print(f"{BULLET}Parallax:          {pos.parallax:.4f} deg")

    print(heading("Today"))
    print(f"{BULLET}Moonrise  {_fmt(rs.rise, zone)}")
    print(f"{BULLET}Transit   {_fmt(rs.transit, zone)}")
    print(f"{BULLET}Moonset   {_fmt(rs.setting, zone)}")
    if rs.note:
        print(f"{BULLET}Note: the Moon {rs.note}")
    print("\nThe Moon rises roughly 50 minutes later each day, so on some days it")
    print("does not rise at all within a single calendar day. That is normal.")
    return 0


def cmd_frame(args) -> int:
    """The 'Which Way Am I Facing?' lab."""
    location = _need_location(args)
    if location is None:
        return 1
    when = _when(args)

    facing = args.facing
    if facing is not None:
        try:
            facing = _parse_direction(facing)
        except ValueError as exc:
            return _fail(str(exc), "Try a bearing like 135, or a compass point like SE.")

    moon_h = observer.moon_position(location, when)
    sun_h = observer.sun_position(location, when)
    zone = _display_zone(args, location)

    print(f"Observer frame for {location.describe()}")
    print(f"Time: {mtime.format_instant(when, zone)}")

    print(heading("Your frame"))
    print(f"{BULLET}Latitude  {location.latitude:+.4f} deg ({location.hemisphere} hemisphere)")
    print(f"{BULLET}Longitude {location.longitude:+.4f} deg (east positive)")
    if facing is not None:
        print(f"{BULLET}Facing    {facing:.1f} deg ({observer.cardinal(facing)})")

    print(heading("Where things are"))
    print(f"{BULLET}Sun:  {sun_h.describe()}")
    print(f"{BULLET}Moon: {moon_h.describe()}")

    if facing is not None:
        offset = ((moon_h.azimuth - facing + 180) % 360) - 180
        print(heading("Relative to the way you are facing"))
        if not moon_h.is_up:
            print("The Moon is below the horizon, so it is not in view whichever")
            print("way you turn.")
        elif abs(offset) < 30:
            print(f"The Moon is {abs(offset):.0f} degrees to your "
                  f"{'right' if offset > 0 else 'left'} -- roughly straight ahead.")
        elif abs(offset) < 90:
            print(f"Turn {abs(offset):.0f} degrees to your "
                  f"{'right' if offset > 0 else 'left'}.")
        elif abs(offset) < 150:
            print(f"The Moon is well off to your "
                  f"{'right' if offset > 0 else 'left'} "
                  f"({abs(offset):.0f} degrees). Turn a long way.")
        else:
            print("The Moon is behind you. Turn around.")
        if moon_h.is_up:
            print(f"\nThen look {moon_h.altitude:.0f} degrees up. "
                  f"That is about {moon_h.altitude / 10:.1f} fist-widths at arm's length.")

    print(heading("Now go outside"))
    print("Before you check: write down where you think the Moon will be.")
    print("Then look. Then come back and explain any difference.")
    print("")
    print("Things that legitimately cause a mismatch:")
    print(f"{BULLET}Your phone compass is off (magnetic vs true north can differ")
    print("       by more than 20 degrees in some places)")
    print(f"{BULLET}Your saved coordinates are wrong or stale")
    print(f"{BULLET}Your clock is off")
    print(f"{BULLET}Hills or buildings hide the true horizon")
    print(f"{BULLET}You are estimating altitude by eye, which is genuinely hard")
    return 0


def _parse_direction(text: str) -> float:
    """Accept either a bearing in degrees or a compass point."""
    raw = text.strip().upper()
    points = {
        "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
        "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
        "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
        "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5,
    }
    if raw in points:
        return float(points[raw])
    try:
        return float(raw) % 360.0
    except ValueError as err:
        raise ValueError(f"could not read the direction {text!r}") from err


# ---------------------------------------------------------------------------
# seasons
# ---------------------------------------------------------------------------


def cmd_seasons(args) -> int:
    location = _need_location(args)
    if location is None:
        return 1
    when = _when(args)
    year = when.year

    print(f"Seasonal comparison for {location.describe()}")
    print(f"Hemisphere: {location.hemisphere}")

    rows = [
        ("Today", when),
        ("June solstice", _dt.datetime(year, 6, 21, 12, tzinfo=mtime.UTC)),
        ("September equinox", _dt.datetime(year, 9, 22, 12, tzinfo=mtime.UTC)),
        ("December solstice", _dt.datetime(year, 12, 21, 12, tzinfo=mtime.UTC)),
        ("March equinox", _dt.datetime(year, 3, 20, 12, tzinfo=mtime.UTC)),
    ]

    print(heading("Day length and sunrise direction"))
    print(f"  {'Date':<20} {'Day length':>12} {'Sunrise az':>12} {'Sunset az':>11} {'Noon alt':>10}")
    for label, moment in rows:
        rs = observer.sun_rise_set(location, moment)
        if rs.always_up:
            length, rise_az, set_az = "24.00 h", "  --", "  --"
        elif rs.never_up:
            length, rise_az, set_az = " 0.00 h", "  --", "  --"
        else:
            hours = (rs.setting - rs.rise).total_seconds() / 3600.0
            if hours < 0:
                hours += 24
            length = f"{hours:.2f} h"
            rise_az = f"{observer.sun_position(location, rs.rise).azimuth:.1f}"
            set_az = f"{observer.sun_position(location, rs.setting).azimuth:.1f}"
        alt = f"{rs.transit_altitude:.1f}" if rs.transit_altitude is not None else "--"
        print(f"  {label:<20} {length:>12} {rise_az:>12} {set_az:>11} {alt:>10}")

    print("\n  Azimuth is degrees clockwise from north: 90 is due east, 270 due west.")

    print(heading("What this shows"))
    dec_now = sun_engine.declination(when)
    print(f"{BULLET}The Sun's declination today is {dec_now:+.2f} degrees.")
    print(f"{BULLET}Sunrise is only exactly due east at the equinoxes. The rest of")
    print("       the year it swings north or south of east.")
    print(f"{BULLET}The size of that swing depends on your latitude. Near the")
    print("       equator it is small; near the poles it is enormous.")

    if args.explain:
        print(heading("Why seasons happen -- and why it is NOT distance"))
        pos_jun = sun_engine.position(_dt.datetime(year, 6, 21, tzinfo=mtime.UTC))
        pos_dec = sun_engine.position(_dt.datetime(year, 12, 21, tzinfo=mtime.UTC))
        print("A very common belief is that summer happens when Earth is closer to")
        print("the Sun. Here are the actual distances:")
        print(f"{BULLET}21 June:     {pos_jun.distance_km:,.0f} km")
        print(f"{BULLET}21 December: {pos_dec.distance_km:,.0f} km")
        closer = "December" if pos_dec.distance_km < pos_jun.distance_km else "June"
        print(f"\nEarth is actually CLOSER to the Sun in {closer}.")
        print("If distance drove the seasons, the whole planet would have summer")
        print("at the same time. It does not: when it is July in Norway it is")
        print("winter in New Zealand.")
        print("\nThe real cause is the 23.44-degree axial tilt, working two ways:")
        print(f"{BULLET}Height: a high Sun spreads its energy over a small patch of")
        print("       ground. A low Sun smears the same energy over a larger patch.")
        print(f"{BULLET}Duration: a high Sun also stays up longer, so the ground has")
        print("       more hours to absorb heat and fewer to radiate it away.")
    return 0


# ---------------------------------------------------------------------------
# tide
# ---------------------------------------------------------------------------


def cmd_tide(args) -> int:
    if args.tide_command == "explain":
        return _tide_explain()

    location = _need_location(args)
    if location is None:
        return 1
    when = _when(args)
    estimate = tide_engine.rough(location, when, args.interval)

    if args.tide_command == "rough":
        return _tide_rough(estimate, location, args)
    if args.tide_command == "compare":
        return _tide_compare(estimate, location, args)
    return _fail("unknown tide subcommand")


def _tide_explain() -> int:
    print("How tides work -- and where this model gives up")
    print("=" * 47)

    print(heading("1. What is a tide?"))
    print("The slow, regular rise and fall of sea level, usually twice a day.")
    print("It is not waves, and it is not the wind pushing water around.")

    print(heading("2. What causes it?"))
    print("The Moon's gravity. But not in the way most people first assume.")
    print("")
    print("Gravity gets weaker with distance. The side of Earth facing the Moon")
    print("is about 12,700 km closer than the far side, so it is pulled a little")
    print("harder. Earth's centre is pulled a medium amount. The far side is")
    print("pulled least.")
    print("")
    print("Relative to the centre, the near water is tugged towards the Moon and")
    print("the far water is left behind. Both effects lift water away from the")
    print("centre, so you get TWO bulges, on opposite sides.")
    print("")
    print("The tide comes from the DIFFERENCE in pull across Earth, not the pull")
    print("itself. This is why the Sun, which pulls on Earth 175 times harder")
    print("than the Moon does, produces a tide only about half as large: it is so")
    print("far away that the difference across Earth's width is tiny.")

    print(heading("3. Why two highs and two lows?"))
    print("Because Earth rotates through both bulges every day.")

    print(heading("4. The lunar day"))
    print("While Earth turns once, the Moon moves about 13 degrees further along")
    print("its orbit. Earth must turn that bit extra to bring the Moon back")
    print("overhead. At 15 degrees per hour, that is about 50 minutes.")
    print(f"\n  Lunar day = {tide_engine.LUNAR_DAY_HOURS:.4f} hours = 24 h 50 min")

    print(heading("5. Why tide times shift"))
    print("Straight from the lunar day: high water arrives roughly 50 minutes")
    print("later each day, which is why tide tables march forward through the")
    print("week rather than repeating.")

    print(heading("6. Spring and neap tides"))
    print("At new and full Moon the Sun and Moon line up and their bulges add:")
    print("SPRING tides, with the largest range. (Nothing to do with the season --")
    print("the word means 'to spring up'.) At the quarters they are at right")
    print("angles and partly cancel: NEAP tides, with the smallest range.")
    print("Springs and neaps therefore alternate about every 7 days.")

    print(heading("7. Sun-Moon geometry and phase"))
    print("This means you can predict the tidal RANGE from the Moon's phase alone,")
    print("without any tide table. Full or new Moon means big tides this week.")

    print(heading("8. Why this cannot predict your harbour"))
    print("Everything above describes an Earth covered by a deep, uniform ocean.")
    print("Yours is not. In the real world:")
    print(f"{BULLET}Continents block the bulges from travelling freely.")
    print(f"{BULLET}Water in a basin sloshes at its own natural period, and the")
    print("       tide drives that sloshing like a child on a swing.")
    print(f"{BULLET}Shallow water slows the wave down and distorts its shape.")
    print(f"{BULLET}Friction, wind and air pressure all shift the water further.")

    print(heading("9. Local effects"))
    print(f"{BULLET}Bay of Fundy: the basin resonates, giving 16-metre tides.")
    print(f"{BULLET}Parts of the Mediterranean: nearly no tide at all.")
    print(f"{BULLET}Some coasts get one high per day, not two, because the")
    print("       daily and twice-daily components combine differently.")
    print(f"{BULLET}Nearly everywhere, high water arrives some fixed time AFTER")
    print("       the Moon crosses the meridian. That lag is the LUNITIDAL")
    print("       INTERVAL, and it is a property of the place, not the sky.")

    print(heading("10. How real predictions are made"))
    print("Not from this geometry at all. Real tide prediction is done by")
    print("HARMONIC ANALYSIS: measure the water level at a station for a year or")
    print("more, decompose the record into dozens of sine waves at known")
    print("astronomical frequencies, and measure the amplitude and phase of each")
    print("one AT THAT STATION. Prediction is then adding those waves back up.")
    print("")
    print("The astronomy supplies the frequencies. Only measurement can supply")
    print("the amplitudes and phases. That is the deep lesson: a good model often")
    print("needs both theory and local data, and knowing which parts must come")
    print("from measurement is most of the skill.")

    print(heading("Try it"))
    print("  moonfield tide rough")
    print("  moonfield tide rough --interval 4.5")
    print("  moonfield tide compare --observed 2026-08-16T09:14 --observed 2026-08-16T21:41")
    return 0


def _tide_rough(estimate, location: Location, args) -> int:
    zone = _display_zone(args, location)
    print("ROUGH TIDE ESTIMATE -- FOR LEARNING ONLY, NOT FOR NAVIGATION")
    print("=" * 60)
    print(f"\n{location.describe()}")
    print(f"Time: {mtime.format_instant(estimate.when, zone)}")

    print(heading("The sky right now"))
    if estimate.moon_transit:
        print(f"{BULLET}Moon crosses your meridian at "
              f"{_fmt(estimate.moon_transit, zone)}")
    print(f"{BULLET}{estimate.spring_neap_label}")
    print(f"{BULLET}Relative range factor: {estimate.range_factor:.2f} "
          f"(1.00 would be an average tide)")
    print(f"{BULLET}Lunitidal interval in use: {estimate.lunitidal_interval:.2f} hours")

    print(heading("What the two-bulge model says"))
    print(f"{BULLET}Water is currently {estimate.state}")
    print(f"{BULLET}Roughly {estimate.fraction * 100:.0f}% of the way from low to high")
    if estimate.next_event:
        print(f"{BULLET}Next {estimate.next_event.kind} water: "
              f"{_fmt(estimate.next_event.when, zone)} "
              f"(in {estimate.hours_to_next:.1f} hours)")

    print(heading("Predicted events"))
    for event in estimate.events:
        marker = ">" if event is estimate.next_event else " "
        stamp = event.when.astimezone(zone)
        print(f"  {marker} {stamp.strftime('%a %d %b %H:%M %Z')}  "
              f"{event.kind.upper():<5} ({event.driver})")

    print(heading("Read this part"))
    for note in estimate.notes:
        print(f"{BULLET}{note}")

    print(heading("Your turn"))
    print("Before you check a real tide table, write down:")
    print(f"{BULLET}What time you think high water actually is")
    print(f"{BULLET}How confident you are, and why")
    print("\nThen find your nearest official tide station and compare. Feed the")
    print("difference back in with:")
    print("    moonfield tide compare --observed <TIME> --observed <TIME>")
    return 0


def _tide_compare(estimate, location: Location, args) -> int:
    if not args.observed:
        return _fail(
            "no observed times given",
            "Pass at least one real high-water time from an official tide table "
            "or your own observation, e.g.\n"
            "    moonfield tide compare --observed 2026-08-16T09:14",
        )

    zone = _display_zone(args, location)
    try:
        # Your observed times are read in the zone you are shown results in.
        # A high water you wrote down at 09:14 is 09:14 on the clock you were
        # looking at, not 09:14 UTC.
        observed = [mtime.parse_datetime(t, zone) for t in args.observed]
    except ValueError as exc:
        return _fail(str(exc), "Use a form like 2026-08-16T09:14")

    rows = tide_engine.compare(estimate, observed, kind=args.kind)

    print("MODEL VERSUS REALITY")
    print("=" * 20)
    print(f"\n{location.describe()}")
    print(f"Comparing {args.kind} waters. Lunitidal interval in use: "
          f"{estimate.lunitidal_interval:.2f} h")

    print(heading("Comparison"))
    print(f"  {'Observed':<22} {'Model predicted':<22} {'Model error':>12}")
    for row in rows:
        obs = row["observed"].astimezone(zone).strftime("%Y-%m-%d %H:%M")
        if row["predicted"] is None:
            print(f"  {obs:<22} {'(no prediction)':<22} {'--':>12}")
            continue
        pred = row["predicted"].astimezone(zone).strftime("%Y-%m-%d %H:%M")
        delta = row["delta_hours"]
        sign = "late" if delta > 0 else "early"
        print(f"  {obs:<22} {pred:<22} {abs(delta):>7.2f} h {sign}")

    suggestion = tide_engine.suggested_interval(rows)
    print(heading("What the difference is telling you"))
    if suggestion is None:
        print("Not enough data to say anything.")
        return 0

    deltas = [r["delta_hours"] for r in rows if r.get("delta_hours") is not None]
    spread = max(deltas) - min(deltas) if len(deltas) > 1 else 0.0

    print(f"Average model error: {sum(deltas)/len(deltas):+.2f} hours")
    if len(deltas) > 1:
        print(f"Spread across your samples: {spread:.2f} hours")

    print()
    if abs(spread) < 1.0:
        print("The error is CONSISTENT. That is the good case: a steady offset is")
        print("not random noise, it is a missing constant in the model. It is the")
        print("lunitidal interval for your port -- the fixed lag between the Moon")
        print("crossing your meridian and the tidal wave actually arriving.")
        print("\nTry running again with:")
        print(f"    moonfield tide rough --interval {estimate.lunitidal_interval + suggestion:.2f}")
        print("\nIf that lines the predictions up, you have just done in miniature")
        print("what tide stations do properly: calibrated a physical model with")
        print("local measurements.")
    else:
        print("The error VARIES between your samples. A single constant will not")
        print("fix it. Likely reasons:")
        print(f"{BULLET}Your coast has a strong daily (once-a-day) component as")
        print("       well as the twice-daily one, so alternate tides differ.")
        print(f"{BULLET}Shallow water distorts the wave, so the rise and the fall")
        print("       take unequal times.")
        print(f"{BULLET}Weather was pushing water around on one of those days.")
        print("\nThis is exactly the point at which the two-bulge model runs out,")
        print("and real forecasting switches to harmonic analysis of measured")
        print("water levels. See 'moonfield tide explain', section 10.")
    return 0


# ---------------------------------------------------------------------------
# longitude (text fallback for the browser game)
# ---------------------------------------------------------------------------


def cmd_longitude(args) -> int:
    """Text version of the Longitude Game, for people without a browser."""
    print("THE LONGITUDE PROBLEM")
    print("=" * 21)
    print("\nThe browser version of this lab lives in site/longitude-game/.")
    print("This is the text version. Same maths, fewer pictures.")

    print(heading("The idea in three lines"))
    print("  360 degrees / 24 hours = 15 degrees per hour")
    print("  15 degrees / 60 minutes = 0.25 degrees per minute")
    print("  1 degree = 4 minutes of time")

    print(heading("Why that solves navigation"))
    print("Latitude is easy: measure how high the Sun gets at noon, or how high")
    print("Polaris sits, and you have it. Sailors could do this by 1500.")
    print("")
    print("Longitude is hard, because the Earth is rotating underneath you and")
    print("every meridian looks identical. The trick: carry a clock still showing")
    print("the time at your home port. When the Sun reaches its highest point")
    print("where you are, it is local noon. Compare that to your home clock.")
    print("Every hour of difference is 15 degrees of longitude.")
    print("")
    print("That is why the search for longitude was really a search for a clock")
    print("that could survive years at sea -- damp, salt, and a pitching deck --")
    print("without gaining or losing more than a few seconds.")

    reference = args.reference_hours
    local_noon = args.local_noon_hours

    if reference is None or local_noon is None:
        print(heading("Try it"))
        print("Give the clock readings and this will work out your longitude:")
        print("    moonfield longitude --reference 14.5 --local-noon 12.0")
        print("")
        print("meaning: when the Sun was highest where you are, your Greenwich")
        print("clock read 14:30. Add --drift to see what a broken clock does.")
        return 0

    difference = reference - local_noon
    longitude = -difference * 15.0

    print(heading("Your position"))
    print(f"{BULLET}Reference clock at local noon: {_hours_to_clock(reference)}")
    print(f"{BULLET}Local apparent noon:           {_hours_to_clock(local_noon)}")
    print(f"{BULLET}Difference: {difference:+.4f} hours")
    print(f"\n  Longitude = -({difference:+.4f} h) x 15 deg/h = {longitude:+.3f} deg")
    hemi = "east" if longitude >= 0 else "west"
    print(f"  You are at {abs(longitude):.3f} degrees {hemi} of your reference.")

    if args.drift:
        drift_hours = args.drift / 3600.0
        wrong_longitude = -(difference + drift_hours) * 15.0
        error_deg = wrong_longitude - longitude
        km = abs(error_deg) * 111.32 * math.cos(math.radians(args.latitude))

        print(heading("WRONG LANDFALL"))
        print(f"Now suppose your chronometer has drifted by {args.drift:+.0f} seconds.")
        print(f"{BULLET}You would compute {wrong_longitude:+.3f} deg instead of "
              f"{longitude:+.3f} deg")
        print(f"{BULLET}An error of {abs(error_deg):.3f} degrees")
        print(f"{BULLET}At latitude {args.latitude:.0f}, that is about {km:.1f} km "
              "in the wrong place")
        print("")
        if km < 5:
            print("Survivable. You would see your mistake before it saw you.")
        elif km < 40:
            print("Uncomfortable. In fog, at night, near rocks: genuinely dangerous.")
        else:
            print("This is how ships were lost. Not through bad seamanship, but")
            print("through arithmetic done on a number that was quietly wrong.")

        print("\n  Rule of thumb: 4 seconds of clock error = 1 nautical mile")
        print("  of longitude error at the equator. A clock losing 1 second per")
        print("  day is 30 seconds out after a month -- about 14 km.")

    print(heading("What this teaches beyond navigation"))
    print(f"{BULLET}A measurement is only as good as its reference.")
    print(f"{BULLET}Errors in an input propagate into the output, sometimes")
    print("       amplified by a large constant (here, 15 degrees per hour).")
    print(f"{BULLET}Small errors accumulate silently until something hits them.")
    print(f"{BULLET}Calibration is not bureaucracy. It is the difference between")
    print("       a working instrument and a confident liar.")
    return 0


def _hours_to_clock(hours: float) -> str:
    h = int(hours) % 24
    m = int(round((hours - int(hours)) * 60))
    if m == 60:
        h, m = (h + 1) % 24, 0
    return f"{h:02d}:{m:02d}"


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------


def cmd_config(args) -> int:
    if args.config_command == "path":
        print(config_path())
        return 0

    if args.config_command == "show":
        config = load_config()
        if not config:
            print("No configuration saved yet.")
            print(f"It would live at: {config_path()}")
            print("\nSet your location with:")
            print("    moonfield config set-location --lat <LAT> --lon <LON>")
            return 0
        location = load_location()
        print(f"Configuration file: {config_path()}")
        if location:
            print(heading("Saved location"))
            print(f"{BULLET}Name:      {location.name}")
            print(f"{BULLET}Latitude:  {location.latitude:+.4f} "
                  f"({'north' if location.latitude >= 0 else 'south'})")
            print(f"{BULLET}Longitude: {location.longitude:+.4f} "
                  f"({'east' if location.longitude >= 0 else 'west'})")
            print(f"{BULLET}Timezone:  {location.timezone or 'system default'}")
            print(f"{BULLET}Elevation: {location.elevation_m:.0f} m")
        return 0

    if args.config_command == "set-location":
        try:
            location = Location(
                latitude=parse_coordinate(str(args.lat)),
                longitude=parse_coordinate(str(args.lon)),
                name=args.name or "your location",
                timezone=args.timezone,
                elevation_m=args.elevation,
            )
        except ValueError as exc:
            return _fail(
                str(exc),
                "Latitude runs -90 to +90 (north positive). "
                "Longitude runs -180 to +180 (EAST positive, so places west of "
                "Greenwich are negative).",
            )

        if args.timezone:
            resolved = mtime.resolve_zone(args.timezone)
            if getattr(resolved, "key", None) != args.timezone:
                print(
                    f"Warning: '{args.timezone}' is not in this system's timezone "
                    "database, so times will be shown in UTC.\n"
                    "Timezone names look like 'Europe/Lisbon' or "
                    "'America/Argentina/Cordoba'.",
                    file=sys.stderr,
                )

        path = save_location(location)
        print(f"Saved: {location.describe()}")
        print(f"Hemisphere: {location.hemisphere}")
        print(f"Written to: {path}")
        print("\nNow try:")
        print("    moonfield now")
        return 0

    if args.config_command == "clear":
        config = load_config()
        config.pop("location", None)
        save_config(config)
        print("Saved location cleared.")
        return 0

    return _fail("unknown config subcommand")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _add_common(parser: argparse.ArgumentParser, location: bool = True) -> None:
    parser.add_argument(
        "--date",
        metavar="WHEN",
        help="date or date and time, e.g. 2026-08-16 or 2026-08-16T21:30 "
        "(default: now). A time with no zone is read as your local civil "
        "time; add Z for UTC, or +01:00 for an explicit offset",
    )
    if location:
        parser.add_argument("--lat", help="latitude, north positive")
        parser.add_argument("--lon", help="longitude, EAST positive")
        parser.add_argument("--place", help="a name for this location")
    parser.add_argument(
        "--timezone", help="IANA timezone for display, e.g. Europe/Lisbon"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="moonfield",
        description=(
            "Learn the sky by running code you fully understand. "
            "Start with 'moonfield doctor', then 'moonfield phase'."
        ),
        epilog=(
            "Every command accepts --date. Most accept --lat and --lon, or use "
            "the location you saved with 'moonfield config set-location'."
        ),
    )
    parser.add_argument("--version", action="version", version=f"moonfield {__version__}")
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # doctor
    p = subparsers.add_parser(
        "doctor", help="check your setup and explain anything that is wrong"
    )
    p.set_defaults(func=cmd_doctor)

    # phase
    p = subparsers.add_parser("phase", help="what phase is the Moon in?")
    # Phase itself is geocentric, but the drawing is not: a waxing crescent is
    # lit on the right from the north and on the left from the south. So the
    # location flags are accepted here too.
    _add_common(p, location=True)
    p.add_argument(
        "--explain", action="store_true", help="show every intermediate number"
    )
    p.add_argument("--no-art", action="store_true", help="skip the ASCII Moon")
    p.set_defaults(func=cmd_phase)

    # now
    p = subparsers.add_parser("now", help="a full sky report for your location")
    _add_common(p)
    p.set_defaults(func=cmd_now)

    # sun
    p = subparsers.add_parser("sun", help="where the Sun is, and today's timings")
    _add_common(p)
    p.add_argument("--explain", action="store_true", help="explain the declination")
    p.set_defaults(func=cmd_sun)

    # moon
    p = subparsers.add_parser("moon", help="where the Moon is, and today's timings")
    _add_common(p)
    p.set_defaults(func=cmd_moon)

    # frame
    p = subparsers.add_parser(
        "frame", help="the 'Which Way Am I Facing?' observing lab"
    )
    _add_common(p)
    p.add_argument(
        "--facing", help="the way you are facing: a bearing like 135, or SE"
    )
    p.set_defaults(func=cmd_frame)

    # seasons
    p = subparsers.add_parser(
        "seasons", help="compare day length and sunrise direction across the year"
    )
    _add_common(p)
    p.add_argument(
        "--explain", action="store_true", help="why seasons happen (it is not distance)"
    )
    p.set_defaults(func=cmd_seasons)

    # tide
    p = subparsers.add_parser("tide", help="tide concepts and a rough teaching model")
    tide_sub = p.add_subparsers(dest="tide_command", metavar="SUBCOMMAND")

    t = tide_sub.add_parser("explain", help="how tides work, and where models fail")
    t.set_defaults(func=cmd_tide)

    t = tide_sub.add_parser(
        "rough", help="a crude estimate for learning -- NOT for navigation"
    )
    _add_common(t)
    t.add_argument(
        "--interval",
        type=float,
        default=0.0,
        help="lunitidal interval in hours: your local lag between the Moon "
        "crossing the meridian and high water",
    )
    t.set_defaults(func=cmd_tide)

    t = tide_sub.add_parser(
        "compare", help="check the rough model against real observed times"
    )
    _add_common(t)
    t.add_argument(
        "--observed",
        action="append",
        default=[],
        help="an observed high or low water time; repeat for several",
    )
    t.add_argument(
        "--kind", choices=["high", "low"], default="high", help="which waters you gave"
    )
    t.add_argument("--interval", type=float, default=0.0, help="lunitidal interval, hours")
    t.set_defaults(func=cmd_tide)

    # longitude
    p = subparsers.add_parser(
        "longitude", help="the Longitude Game, text version"
    )
    p.add_argument(
        "--reference",
        dest="reference_hours",
        type=float,
        help="what your reference clock read at local noon, in hours (14.5 = 14:30)",
    )
    p.add_argument(
        "--local-noon",
        dest="local_noon_hours",
        type=float,
        default=12.0,
        help="local apparent noon in hours (default 12.0)",
    )
    p.add_argument(
        "--drift",
        type=float,
        help="clock drift in seconds, to see Wrong Landfall mode",
    )
    p.add_argument(
        "--latitude",
        type=float,
        default=45.0,
        help="latitude, used to convert a longitude error into kilometres",
    )
    p.set_defaults(func=cmd_longitude)

    # config
    p = subparsers.add_parser("config", help="save your location and settings")
    config_sub = p.add_subparsers(dest="config_command", metavar="SUBCOMMAND")

    c = config_sub.add_parser("show", help="show the current configuration")
    c.set_defaults(func=cmd_config)

    c = config_sub.add_parser("path", help="print the configuration file path")
    c.set_defaults(func=cmd_config)

    c = config_sub.add_parser("set-location", help="save your observing location")
    c.add_argument("--lat", required=True, help="latitude, north positive")
    c.add_argument("--lon", required=True, help="longitude, EAST positive")
    c.add_argument("--name", help="a name for this place")
    c.add_argument("--timezone", help="IANA timezone, e.g. Europe/Lisbon")
    c.add_argument("--elevation", type=float, default=0.0, help="metres above sea level")
    c.set_defaults(func=cmd_config)

    c = config_sub.add_parser("clear", help="forget the saved location")
    c.set_defaults(func=cmd_config)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "command", None):
        parser.print_help()
        print("\nNew here? Run these three, in order:")
        print("    moonfield doctor")
        print("    moonfield config set-location --lat <LAT> --lon <LON>")
        print("    moonfield phase --explain")
        return 0

    if args.command == "tide" and not getattr(args, "tide_command", None):
        print("The tide command needs a subcommand:\n")
        print("    moonfield tide explain    how tides work")
        print("    moonfield tide rough      a crude estimate (learning only)")
        print("    moonfield tide compare    model versus reality")
        return 1

    if args.command == "config" and not getattr(args, "config_command", None):
        print("The config command needs a subcommand:\n")
        print("    moonfield config show")
        print("    moonfield config path")
        print("    moonfield config set-location --lat <LAT> --lon <LON>")
        print("    moonfield config clear")
        return 1

    try:
        return args.func(args)
    except ValueError as exc:
        return _fail(str(exc))
    except BrokenPipeError:  # pragma: no cover
        # Happens when output is piped into something that stops reading
        # early, such as `moonfield phase | head`. Without this, Python
        # prints an alarming traceback for what is completely normal.
        try:
            sys.stdout.close()
        except Exception:
            pass
        return 0
    except KeyboardInterrupt:  # pragma: no cover
        print("\nStopped.", file=sys.stderr)
        return 130


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
