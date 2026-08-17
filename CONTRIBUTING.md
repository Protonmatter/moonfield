# Contributing to Moonfield

Moonfield is a curriculum first and a codebase second. That shapes what a good
contribution looks like: a clear lesson is worth more here than a clever
algorithm.

## Ways to contribute, in rough order of value

1. **Tell us where you got stuck.** Confusion is a documentation bug. If a
   lesson lost you, that is the most useful thing you can report, and you are
   the only person who can report it.
2. **Report where the sky disagrees with the code.** Use the "Observation
   doesn't match" issue template. Include your location, time and what you
   actually saw.
3. **Fix or improve a lesson.** Typos, unclear paragraphs, missing steps,
   examples that assume a northern hemisphere.
4. **Write a lesson.** Especially for the planned modules 07–12.
5. **Add tests.** Particularly for locations and dates we do not cover:
   southern hemisphere, tropics, polar, date boundaries.
6. **Fix a bug.**

Beginners: contributions of type 1 and 2 are genuinely valuable and require no
programming. Please do not think you have to write code to be useful here.

## Ground rules

### AI-free by design

Moonfield teaches by having you understand what you run. Please do not submit
AI-generated lessons or code.

This is not a purity test, and it is not about tooling snobbery. It is that the
value of a lesson here lies in someone having genuinely worked out how to
explain a thing, and the value of a line of code lies in someone being able to
answer questions about it. Generated text is confidently wrong in exactly the
places (sign conventions, timezone edge cases, near-identical formulae) where
a learner cannot yet catch it.

If you use an assistant to check your grammar, nobody will ever know or mind.
If you generate a lesson and submit it, it will be closed.

### Global by default

Never assume the reader is in the northern hemisphere, has ocean access, uses
daylight saving, or lives in the United States.

Concretely:
- Give examples from more than one hemisphere
- Do not write "the Sun is due south at noon" without qualification
- Do not require a coastline for a tide exercise
- Use ISO dates (2026-08-16), 24-hour times, and metric units first
- Longitude is **east-positive** everywhere in this project

### Explain the limits

Every model here must state what it assumes and where it breaks. A lesson that
presents an approximation as truth will be sent back.

### Prediction before revelation

Lessons ask the learner to commit to an answer before showing them one. If your
lesson gives the answer in the first paragraph, restructure it.

## Writing a lesson

Follow the pattern in [what-is-this.md](docs/00-start-here/what-is-this.md):

```
Goal / Prerequisites / Time
Observe:         something real, first
Predict:         the learner commits, in writing
Learn:           the concept
Run:             the command or code
Change one variable
Validate:        against reality or a published source
Explain:         what the discrepancy means
Checkpoint:      a self-check list
Try it yourself: extensions
Questions to think about
Common questions
Go deeper
```

Not every lesson needs every section, but the Predict → Run → Validate spine is
not optional.

### Layers

Where useful, mark content as **Beginner** (works with no maths beyond
arithmetic), **Standard** (the default path), or **Advanced** (derivations,
error analysis). A learner should be able to complete any module at Beginner
level and get a real result.

## Code

- **Python 3.10+, standard library only** for anything in `src/moonfield/`.
  This is a hard rule. Zero runtime dependencies is what makes installation
  nearly unfailable and every formula readable.
- Dev dependencies (pytest, ruff) are fine.
- Comment the *why* and cite sources. Every non-obvious constant should say
  where it came from, most cite Meeus by chapter.
- Prefer clear over clever. Someone is going to read this to learn from it.

```bash
pip install -e ".[dev]"
python -m pytest
ruff check src tests
```

### Tests

New astronomy code needs tests. The best ones assert **physical identities**
rather than stored numbers:

```python
# good: survives an algorithm rewrite
assert abs(noon_altitude - (90 - abs(lat - dec))) < 0.5

# weaker: only catches changes, not errors
assert round(altitude, 4) == 61.9243
```

Validate against Meeus's worked examples or published ephemeris values where
you can, and say in a comment which source you used.

## Pull requests

1. Fork, branch from `main`
2. Make the change
3. Run `python -m pytest` and `ruff check src tests`
4. Open a PR describing **what a learner can now do that they could not
   before**

Small PRs get reviewed faster. One lesson or one fix per PR.

## Discussions vs Issues

- **[Discussions](../../discussions)**: questions, ideas, "am I understanding
  this right?", showing off an observation. No question is too basic.
- **[Issues](../../issues)**: something is broken, wrong, or missing.

If you are not sure, use Discussions. It can always be converted.

## Code of Conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md). The
short version: this is a place where people learn in public, which means being
visibly wrong in front of strangers. Protect that.
