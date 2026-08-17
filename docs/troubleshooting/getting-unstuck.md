# Getting unstuck

Being stuck is not a sign you are doing this wrong. It is the normal condition
of anyone learning something real. This page is about getting unstuck without
outsourcing your thinking.

## The five-minute rule

Give any problem five real minutes before asking for help. Not because
suffering is virtuous, but because the first five minutes is where most of the
learning happens.

After five minutes, ask. Sitting stuck for an hour is not more virtuous than
sitting stuck for five minutes — it is just slower.

## Debugging, in order

**1. Read the error message.** All of it, slowly. Python error messages are
unusually good. The last line says what went wrong; the lines above say where.

**2. Check the obvious three.**
```bash
moonfield doctor
```
Wrong longitude sign, wrong clock, wrong timezone. These cause most
"astronomy is broken" reports.

**3. Say what you expected out loud.** "I expected sunrise around 6 and got
18." Stating the gap precisely often reveals it — 12 hours is a suspiciously
round number, and suggests a longitude sign.

**4. Make it smaller.** Cut the input down until the problem disappears. The
last thing you removed is where the problem is.

**5. Print things.** Put a `print()` before the line that fails and look at
what is actually in the variables. This is not primitive; professionals do this
constantly.

**6. Check your assumptions with a case you know.** If your rise-time code
looks wrong, run it for the equator on an equinox, where you know the answer is
about 06:00 and 18:00 local.

## Asking a good question

A good question gets a good answer fast. Include:

- **What you were trying to do** — the goal, not just the command
- **What you ran** — the exact command, copied not retyped
- **What happened** — the full output, in a code block
- **What you expected** — this is the part people skip, and it is the most useful
- **What you already tried**
- **Your setup** — OS, Python version, and the output of `moonfield doctor`

Use [Discussions](../../discussions) for "how does this work?" and
[Issues](../../issues) for "this is broken."

## On using AI

Moonfield is built to be learned without an AI assistant, and no lesson assumes
one. If you use one anyway, that is your call — but two things are worth
knowing.

First, language models are confidently wrong about astronomy fairly often.
Sign conventions, timezone handling, and which of two near-identical formulae
applies are exactly the areas where they slip, and exactly the areas where you
cannot yet spot the slip.

Second, and more importantly: if an assistant hands you the answer, you have
lost the part that was going to teach you something. The struggle is not an
obstacle in front of the learning. It *is* the learning.

If you do ask one, ask it to explain a concept — not to write your code.

## When you are stuck on the *idea*, not the code

Different problem, different fix:

- **Re-read the Predict step.** Often the confusion is that you never actually
  committed to a prediction, so there is nothing to be surprised by.
- **Draw it.** Especially anything involving angles or geometry. Most of this
  curriculum is easier with a pencil.
- **Go outside and look.** Genuinely. Several concepts here become obvious in
  thirty seconds of looking at the actual sky.
- **Skip it and come back.** Understanding is not strictly sequential.

## See also

- [Glossary](glossary.md)
- [Command cheat sheet](cheat-sheet.md)
- [Environment reset](environment-reset.md)
- [Windows](windows.md) · [macOS](macos.md) · [Linux](linux.md)
