# Interactives

Small, self-contained things you can play with. Each exists because some ideas
land faster when you can move a slider than when you read a paragraph.

| Interactive | Where | What it teaches |
|---|---|---|
| [The Longitude Game](longitude-game.md) | Browser + CLI | Why longitude needs a clock |

Browser versions live in [`site/`](../../site/) and run with no install and no
network. Open the HTML file directly if you prefer not to use the published
site.

## Planned

- **Phase explorer**: drag the Moon around its orbit, watch phase and rise time
  change together
- **Tide composer**: add harmonic constituents and watch a real tide curve
  assemble
- **Seasons globe**: tilt the axis and see what happens to daylight by latitude

Want one of these? Say so in [Discussions](../../discussions).

## Design rules for interactives here

If you contribute one, it should:

1. **Run offline.** No CDN, no analytics, no network calls of any kind.
2. **Be one file** where possible. Easy to read, easy to fork.
3. **Show its working.** A black box that produces a right answer teaches
   nothing.
4. **Let the learner be wrong.** Prediction before revelation.
5. **Not assume a hemisphere or a coastline.**
