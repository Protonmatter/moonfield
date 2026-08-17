# Moonfield

[![CI](https://github.com/Protonmatter/moonfield/actions/workflows/ci.yml/badge.svg)](https://github.com/Protonmatter/moonfield/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Licence: MIT](https://img.shields.io/badge/licence-MIT-green)](LICENSE)
[![Runtime dependencies: none](https://img.shields.io/badge/runtime%20dependencies-none-brightgreen)](pyproject.toml)

> **Mission:** Moonfield teaches the sky by running code you fully understand.
>
> **Method:** Observe → predict → learn → run → change → observe → validate → explain.

Moonfield is an open-source, learn-by-doing curriculum. It starts with things
you can see from your own doorstep — the time, the Moon, the Sun, the seasons,
which way is north — and builds them, step by step, into mathematics, astronomy,
physics, orbital mechanics, rocketry and 3D visualisation.

It assumes you know none of it yet. Not Python, not Git, not virtual
environments, not UTC, not coordinate systems, not trigonometry. If a lesson
here ever makes you feel you *should already know* something, that is a bug in
the lesson. [Please tell us](https://github.com/Protonmatter/moonfield/issues).

---

## This is an AI-free learning path

> **Moonfield is an AI-free learning path for astronomy, mathematics, physics
> and code. No AI tools are required or assumed. Every lesson can be completed
> using these documents, a terminal, an optional editor, and your own
> observations.**

That is a promise about this repository, not a rule about your life. Use
whatever tools you like. But the documents here must stand on their own: every
command is explained, every expected result is written down, every common error
has a recovery path. If you have to ask something outside this repo to get
unstuck, we have failed and we want the issue.

---

## Try it in five minutes

You need Python 3.10 or newer and Git. If you are not sure whether you have
them, that is fine — [`docs/00-start-here/setup.md`](docs/00-start-here/setup.md)
walks through it for Windows, macOS and Linux, assuming nothing.

```bash
git clone https://github.com/Protonmatter/moonfield.git
cd moonfield

python3 -m venv .venv                 # Windows PowerShell: python -m venv .venv
source .venv/bin/activate             # Windows PowerShell: .venv\Scripts\Activate.ps1

pip install -e .
moonfield doctor
```

`moonfield doctor` checks your setup and explains anything that is wrong. Then:

```bash
moonfield phase
```

```
Moon phase for 2026-08-16 22:00 BST  (2026-08-16 21:00 UTC)

  Phase:        Waxing Crescent
  Illuminated:  19.9% of the visible disc
  Age:          4 days 3 hours 22 minutes since new Moon
  Trend:        waxing (growing)
  Distance:     382,283 km

        ........##
     ..............##
    ................##
   ..................##
  ...................###
  ...................###
  ...................###
   ..................##
    ................##
     ..............##
        ........##

  Coming up:
    First Quarter   2026-08-20 03:47 BST   (in 3 days 5 hours)
    Full Moon       2026-08-28 05:19 BST   (in 11 days 7 hours)
```

Now the important part. Ask it to show its working:

```bash
moonfield phase --explain
```

Every intermediate number, where it came from, and what the model still gets
wrong.

---

## What you can do right now

| Command | What it does |
|---|---|
| `moonfield doctor` | Check your setup; explain anything broken |
| `moonfield phase` | What phase is the Moon in? Add `--explain` for the working |
| `moonfield now` | A full sky report for your location |
| `moonfield sun` | Where the Sun is, sunrise, solar noon, sunset |
| `moonfield moon` | Where the Moon is, moonrise, transit, moonset |
| `moonfield frame` | The "Which Way Am I Facing?" observing lab |
| `moonfield seasons` | Day length and sunrise direction across the year |
| `moonfield tide explain` | How tides work, and where simple models give up |
| `moonfield tide rough` | A crude tide estimate — for learning only |
| `moonfield tide compare` | Your model versus reality |
| `moonfield longitude` | The Longitude Game (text version) |
| `moonfield config` | Save your observing location |

Set your location once and every command uses it:

```bash
moonfield config set-location --lat 51.4779 --lon -0.0015 \
    --name "Greenwich" --timezone Europe/London
```

Latitude is **north-positive**. Longitude is **east-positive**, so anywhere
west of Greenwich is a negative number. Getting this backwards is the single
most common setup mistake, which is why it is written in bold here and in the
error messages.

---

## How every lesson is built

Each lesson runs the same laboratory loop:

1. **Observe** something concrete
2. **Predict** what should happen
3. **Learn** the minimum theory required
4. **Run** a command, calculation or observation
5. **Change** one variable
6. **Observe again**
7. **Validate** against an authoritative source where possible
8. **Explain** the result
9. **Checkpoint** your understanding
10. **Go deeper**, optionally

Predicting *before* checking is not a ritual. A prediction you wrote down is a
thing you can be wrong about, and being wrong on purpose, in writing, is the
fastest way to find out what you actually believed.

Every lesson closes with a **Checkpoint**, **Try It Yourself**, **Questions to
Think About**, **Common Questions**, **Getting Stuck?** and **Go Deeper**.

### Three layers, always

- **Beginner** — What do I need to make this work?
- **Standard** — Why does it work?
- **Advanced** — What did we simplify?

Take whichever layer you need today. Skipping the advanced layer is not
cheating; the advanced layer exists so that nothing is hidden from you, not so
you feel obliged to read it.

---

## The curriculum

| Module | Topic | Status |
|---|---|---|
| [00](docs/00-start-here/) | Start here, setup, pre-flight | Ready |
| [01](docs/01-time-and-place/) | Time, UTC and place | Ready |
| [02](docs/02-moon-phases/) | Moon phases | Ready |
| [03](docs/03-earth-moon-system/) | The Earth-Moon system | Ready |
| [04](docs/04-tides/) | Tides | Ready |
| [05](docs/05-local-sky/) | Your local sky | Ready |
| [06](docs/06-seasons/) | Seasons | Ready |
| [07](docs/07-planets/) | Planets | Planned |
| [08](docs/08-constellations/) | Constellations | Planned |
| [09](docs/09-physics/) | Physics | Planned |
| [10](docs/10-orbital-mechanics/) | Orbital mechanics | Planned |
| [11](docs/11-rocketry/) | Rocketry | Planned |
| [12](docs/12-visualization/) | 3D visualisation | Planned |

Supporting material: [background](docs/background/) ·
[interactives](docs/interactives/) · [troubleshooting](docs/troubleshooting/) ·
[glossary](docs/troubleshooting/glossary.md) ·
[command cheat sheet](docs/troubleshooting/cheat-sheet.md)

The "Planned" modules have scaffolding, a stated scope and open issues. They
are deliberately visible rather than hidden, so you can see where the path
leads — and so you can help build it.

---

## Global by default

Moonfield never silently assumes the northern hemisphere, the United States, a
temperate latitude, a sea-level horizon, daylight saving time, access to the
ocean, or clear skies.

Every lesson that could differ by location includes equatorial, mid-latitude
northern, mid-latitude southern, Arctic and Antarctic examples. If you are in
Nairobi or Ushuaia or Tromsø and a lesson only makes sense in Boston, that is a
bug — please file it.

---

## Accuracy, and being honest about it

Everything here is an approximation, and every approximation is labelled.

| Engine | Method | Typical accuracy |
|---|---|---|
| Solar position | Meeus ch. 25, low precision | ~0.01° |
| Lunar position | Truncated ELP-2000/82, Meeus ch. 47 | ~0.002° (a few tens of arcseconds) |
| Moon phase | Geometric, from real positions | Within ~2 minutes of published new/full |
| Rise and set | Iterative altitude search | Within ~1–2 minutes |
| Tides | Equilibrium two-bulge model | **Hours wrong. Not for navigation.** |

That last row is not an apology, it is a lesson. The tide model is deliberately
too simple, and [module 04](docs/04-tides/) is built around discovering exactly
how and why it fails, then calibrating it against real observations. Learning
where a model stops working is more useful than never meeting one that does.

---

## Repository map

```
moonfield/
├── README.md
├── LICENSE                     MIT, plus a note on not using this for navigation
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── pyproject.toml              Packaging; zero runtime dependencies
├── src/moonfield/
│   ├── time.py                 Julian Day, sidereal time, timezones
│   ├── location.py             Where you are; the config file
│   ├── sun.py                  Solar position and the equation of time
│   ├── moon.py                 Lunar position (truncated ELP-2000/82)
│   ├── phase.py                Phases, illumination, two competing models
│   ├── observer.py             Altitude, azimuth, rise and set
│   ├── tides.py                The equilibrium model and its limits
│   └── cli.py                  The `moonfield` command
├── tests/                      284 tests; many check physics, not stored numbers
├── examples/                   Short scripts you can read and modify
├── docs/                       The curriculum
└── site/                       GitHub Pages: interactives and the Longitude Game
```

---

## Contributing

Contributions are wanted, especially from people who have just learned
something and can still remember what was confusing about it. That perspective
is genuinely hard to get back once you have it.

The most valuable contributions are often not code:

- A lesson that assumed something it should have explained
- An error message that did not tell you what to do next
- A worked example from a location we do not cover
- A prediction of yours that did not match reality, with the numbers

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues labelled
[`good first issue`](https://github.com/Protonmatter/moonfield/labels/good%20first%20issue)
are sized for a first-time contributor.

**Questions go in [Discussions](https://github.com/Protonmatter/moonfield/discussions),
not Issues.** "I don't understand why the Moon is where it is" is a great
Discussion. It is not a bug, and we would rather you asked.

---

## Definition of success

Moonfield works if you can start here:

> "I can see the Moon, but I don't really know why it is there or why it looks
> like that."

...and get to here:

> "I can identify my time and observer frame, predict what I should see,
> calculate an approximation, test it against reality, explain the discrepancy,
> understand the physics behind the model, and improve the model myself."

The astronomy is the subject. The transferable part is the habit:

> **Make a model. State its assumptions. Predict. Measure. Compare. Explain the
> error. Improve the model.**

---

## Licence

[MIT](LICENSE). Use it, fork it, teach with it, sell a course with it.

Not for navigation.
