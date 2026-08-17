# Pre-flight check

**Goal:** remove environmental ambiguity, so that when an answer looks wrong you
know it is the astronomy and not your setup.

**Time:** 10 minutes.

---

## Why this exists

Later in this curriculum you will make a prediction, go outside, and find it
does not match. That moment is the most valuable one in the whole project, but
only if you can trust your instruments.

If your clock is ten minutes fast, or your longitude sign is backwards, or you
are running a different Python than you think, then every "interesting
discrepancy" is just a broken setup wearing a lab coat. You will spend an
evening learning nothing.

So: check the boring things once, deliberately, now.

---

## Run the doctor

```bash
moonfield doctor
```

Work down its output.

### Python

```
  - Python 3.12.3 at /home/you/moonfield/.venv/bin/python3
  - Version is new enough (need 3.10+). OK
```

Check that the path contains `.venv`. If it points somewhere else (like
`/usr/bin/python3` or `C:\Python312\`) your virtual environment is not active,
and you are installing and running things in the wrong place.

### Virtual environment

```
  - Active, at /home/you/moonfield/.venv. OK
```

If it says "Not detected", go back to
[Setup step 5](setup.md#step-5-activate-it).

### Time

```
  - System timezone: Europe/London
  - Local time: 2026-08-16 22:00:00 BST
  - UTC time:   2026-08-16 21:00:00 UTC
  - Offset from UTC: +1.00 hours
  - Julian Day now: 2461269.37500
```

Three things to verify by eye:

1. **Is the timezone actually where you are?** Laptops that have travelled, or
   VMs, or fresh installs, often are not.
2. **Is the local time right?** Compare against your phone.
3. **Does the offset look plausible?** UK in summer is +1. India is +5.5.
   Arizona is −7 all year. If yours is 0 and you are not near Greenwich in
   winter, investigate.

### Location

```
  - Greenwich (51.4779N, 0.0015W)
  - Hemisphere: northern
```

Check the **hemisphere letters**, not just the numbers.

This is where the classic error shows up. If you are in Chicago and it says
`87.6298E`, your longitude sign is wrong; you have been placed in central
China. Everything about your local sky will be wrong by about twelve hours, in
a way that looks mysterious rather than obviously broken.

### The self-test

```
  - Phase engine ran: Waxing Crescent, 19.6% illuminated. OK
```

The maths works.

---

## What the doctor cannot tell you

This is the important part, and Moonfield says it out loud every time:

> Everything above is a **configuration** check. It confirms that your computer
> knows which timezone it is in and can do the arithmetic. It cannot tell you
> whether your clock is actually set correctly.

No program can verify its own machine's clock using only that machine. Asking
your computer what time it is and then checking the answer against your
computer is not a test.

**Why it matters:** a one-minute clock error moves the sky by a quarter of a
degree, half the width of the Moon. A ten-minute error moves it two and a half
degrees, which is enough to make a careful observation disagree with a correct
prediction.

**How to actually check:** compare your clock against something independent:
a radio time signal, a phone on mobile network time, or an online clock. Most
operating systems have a setting like "Set time automatically"; switch it on.

Module 05 has a lovely trick: if you can measure when the Sun crosses your
meridian, you can work backwards and check your clock *against the sky*. That
is what the Longitude Game in module 01 is really about.

---

## The five things worth verifying by hand

Beyond the doctor, confirm these yourself once:

1. **Your latitude and longitude are right.** Look them up on a map, don't
   trust memory. Check the signs.
2. **Your clock is within a minute of true.** Compare against your phone.
3. **You know how to reactivate your environment.** Close your terminal, open a
   new one, and get back to a working `moonfield phase`. Do it now, while
   nothing is at stake.
4. **You know where the config lives.** `moonfield config path`.
5. **You know how to start over.** See
   [Resetting your environment](../troubleshooting/environment-reset.md).

---

## Checkpoint

- [ ] `moonfield doctor` reports everything working
- [ ] My Python path contains `.venv`
- [ ] My timezone and local time match reality
- [ ] My saved hemisphere letters are correct (N/S and E/W)
- [ ] I understand the doctor checks configuration, not clock accuracy
- [ ] I have compared my clock against an independent source
- [ ] I can close my terminal and get back to working from scratch

## Try it yourself

1. Run `moonfield doctor` and read every line rather than skimming for OK
2. Deliberately set a wrong location (`--lat 51.5 --lon 100`) and run
   `moonfield now`. Look at how wrong it gets. Then set it back.
3. Close your terminal entirely. Open a new one. Get back to a working
   `moonfield phase` without looking at the setup guide.

## Questions to think about

- Why can no program verify its own machine's clock?
- If your clock were exactly one hour fast, which outputs would be wrong, and
  which would still be right?
- A one-degree error in longitude is four minutes of time. What does a one-degree
  error in *latitude* cost you?

## Getting stuck?

[Getting Unstuck](../troubleshooting/getting-unstuck.md) ·
[Discussions](https://github.com/Protonmatter/moonfield/discussions)

## Go deeper

- [Why UTC exists](../background/why-utc-exists.md)
- [Module 01, Time and place](../01-time-and-place/)

Next: [Editors and IDEs](editors.md), or skip straight to
[Module 01](../01-time-and-place/).
