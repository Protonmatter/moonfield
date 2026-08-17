# What is this?

**Time:** 5 minutes. No computer needed.

## The problem this solves

Most people learn astronomy in one of two unsatisfying ways.

The first is passive: you read that the Moon has phases because of the changing
Sun-Earth-Moon geometry, you nod, and a week later you cannot reconstruct it.
You were told a fact. You did not build anything with it.

The second is opaque: you open an app, it tells you the Moon is 43% illuminated,
and you believe it. But you have no idea where that number came from, no way to
check it, and no way to find out what happens if the assumptions change.

Moonfield takes a third route. You calculate it yourself, with code you can
read, and then you go outside and check.

## What "learn by doing" means here

Every lesson follows the same loop:

1. **Observe** something concrete
2. **Predict** what should happen
3. **Learn** the minimum theory required
4. **Run** a command or calculation
5. **Change** one variable
6. **Observe again**
7. **Validate** against an authoritative source, where possible
8. **Explain** the result
9. **Checkpoint** your understanding
10. **Go deeper**, if you want

Step 2 is the one people want to skip. Don't. A prediction written down before
you look is a claim you can be wrong about, and finding out you were wrong — in
writing, about something specific — is worth ten paragraphs of explanation.

## What makes this different

**You will be shown the working.** Every command has an `--explain` mode or a
lesson that walks through the arithmetic. There is no step where the answer
just appears.

**You will be told what is simplified.** Every model here is an approximation.
The docs say which one, from which textbook, accurate to roughly what. When we
truncated a series, we say what we dropped and what it costs.

**You will meet a model that fails.** Module 04 builds a tide model from first
principles, and then you discover it can be hours wrong for your local harbour.
That is not a bug to be fixed. Understanding *why* a physically correct model
gives a practically useless answer is one of the most transferable things in
this whole curriculum.

**Nothing assumes where you live.** Not the hemisphere, not the country, not
the latitude, not whether you can see the ocean.

## What this is not

- **Not a telescope guide.** Everything here works with your eyes.
- **Not astrology.** Different thing entirely.
- **Not a substitute for professional data.** Do not navigate with it.
- **Not a Python course** — though you will pick up Python on the way.
- **Not linear.** Skip around. The dependency notes tell you what a lesson
  actually needs.

## Do I need to know how to code?

No.

For the first several modules you type commands that already exist and read
their output. That is enough to learn a great deal.

Later, if you want to change how something is calculated, you will open a file
and edit a number. The code is written to be read by someone who has not
written Python before: every non-obvious line has a comment explaining *why*,
not just *what*.

If you never write a line, you can still complete the observational curriculum.

## How long does it take?

There is no schedule. But roughly:

| Module | Rough time |
|---|---|
| 00 — Start here | 1 hour |
| 01 — Time and place | 2 hours |
| 02 — Moon phases | 3 hours, plus a month of occasional looking up |
| 03 — Earth-Moon system | 2 hours |
| 04 — Tides | 3 hours, plus observation |
| 05 — Local sky | 3 hours, mostly outdoors |
| 06 — Seasons | 2 hours, plus a year if you want to see it properly |

Some of this is genuinely gated on the sky. You cannot watch a full lunar cycle
in an afternoon. That is fine — start the observation log early and keep
reading in the meantime.

## Checkpoint

- [ ] I understand this is about doing, not just reading
- [ ] I know I will be asked to predict before I check
- [ ] I know every model here is approximate, and labelled as such
- [ ] I know I do not need to code, or own equipment, to start

Next: [Setup](setup.md).
