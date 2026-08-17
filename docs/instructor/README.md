# Instructor playbook

Moonfield is usable as a taught course, a club activity, or a self-study path.
This page is for anyone running it for other people.

## What this repository is, and what it is not

Everything here is public and always will be: lessons, source, tests, answers to
the *conceptual* questions.

Material that would spoil the labs if learners could read it — worked solutions
to the prediction exercises, assessment rubrics, marking schemes, exam questions
— belongs in a **separate private repository**.

To be explicit about something that is easy to get wrong: putting a folder
called `instructor/` in a public repository provides no privacy whatsoever.
Neither does `.gitignore`, and neither do branch protection rules or CODEOWNERS.
Those govern *workflow* — who may merge what — not *visibility*. A private repo
is the only mechanism here that actually restricts who can read something.

Suggested split:

| Public (this repo) | Private (yours) |
|---|---|
| Lessons, code, tests | Worked solutions to prediction exercises |
| Checkpoints and self-checks | Rubrics and mark schemes |
| "Questions to think about" | Model answers to those questions |
| Accuracy claims | Exam and assessment material |
| Troubleshooting | Cohort notes, individual progress |

The private repo can reference the public one by URL. Keep learner data out of
both unless you have a lawful basis and a retention policy.

## Time budget

| Module | Contact time | Homework | Notes |
|---|---|---|---|
| 00 Start here | 45 min | — | Do setup together; it is where people drop out |
| 01 Time and place | 2 h | 1 h | The Longitude Game is the hook |
| 02 Moon phases | 3 h | **1 month** | Start the observation log in week one |
| 03 Earth–Moon | 1.5 h | 30 min | Do the scale exercise physically |
| 04 Tides | 3 h | 1 h | The most valuable module; do not compress it |
| 05 Local sky | 2 h | 1 h | Needs one sunny session outdoors |
| 06 Seasons | 2 h | 30 min | Opens with a misconception; let them be wrong first |

**The observation log gates everything.** Start module 02's log in the first
session, whatever else you are covering. A lunar cycle takes a month and there
is no way to hurry it.

## The one thing that makes this work

Learners must **write a prediction down before they run anything**. If you let
that slip, Moonfield degrades into a tour of some software.

Practical enforcement that does not feel like policing:

- Collect predictions before revealing results — a shared document, a folded
  piece of paper, anything committed
- Score participation on *making* a prediction, never on its accuracy
- Publicly discuss the most interesting wrong predictions, with the predictor's
  consent, and say why they were reasonable

Most learners have been trained that being wrong is punished. Undoing that takes
a few weeks of visible, cheerful wrongness from you.

## Running the sessions

**Set up together.** Setup failures are the main cause of attrition, and they
cluster by platform. Have the [troubleshooting pages](../troubleshooting/) open.
Run `moonfield doctor` on every machine before anyone leaves the room.

**Pair on labs.** The Predict step works well as a discussion between two people
who must agree an answer.

**Model the debugging.** When something breaks in front of the class, do not
fix it silently. Narrate: read the error, check the obvious three, shrink the
input. That performance teaches more than the lesson you had planned.

**Say "I don't know."** Then find out together, in front of them. This is the
single most useful thing you can do for a room of people who are afraid of
looking stupid.

## Common sticking points

| Symptom | Actual cause |
|---|---|
| "Everything is 12 hours out" | Longitude sign — Moonfield is east-positive |
| "Sunrise is wrong by an hour" | Timezone, or daylight saving |
| "The two phase models disagree" | They should; that is lesson 02.3 |
| "The tide prediction is useless" | Correct; that is the entire point of module 04 |
| "My rise time is 5 minutes out" | Their horizon has hills in it |
| Learners silently stuck | They have not been given permission to ask |

## Assessment, if you must

Assess the *reasoning*, not the answer:

- Did they make a prediction before running anything?
- Did they quantify the discrepancy rather than describe it?
- Can they name what the model does not know?
- Can they state the limits of their own result?

A learner who predicts wrongly, measures the error precisely, and explains its
cause has done better work than one who guessed right.

## Adaptations

**Younger learners (11–14).** Modules 00–03 and 06, Beginner layer. Heavy on
the lamp-and-ball demonstration and the observation log. Skip the series
expansions entirely.

**No outdoor access.** Everything works from published data. Module 04's
supplied station datasets exist for exactly this. Module 02's log can be
replaced with a public observation archive, though it is a real loss.

**Short course (one day).** Modules 00, 01, and the Longitude Game, then
module 02 lessons 2 and 3. Ends on a genuine calculation.

**Physics-first course.** Reorder to 00, 01, 05, 06, 03, 04. Seasons and local
sky are the strongest bridges to mechanics.

## Contributing back

If you run this with a cohort, the most valuable thing you can report is **where
people got stuck**. Open a documentation issue. You are seeing failure modes
that no individual learner can see.
