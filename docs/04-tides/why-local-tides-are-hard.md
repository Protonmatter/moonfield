# Why local tides are hard

**Goal:** understand why a physically correct model gives a practically useless
answer, and how real tide prediction actually works.

---

## The equilibrium model's hidden assumptions

Everything so far assumed Earth is covered by a deep, uniform ocean that
responds instantly. Every part of that is false.

**Continents are in the way.** The bulge cannot travel freely westward; it hits
Africa.

**Water cannot move fast enough.** The bulge would need to travel at about
1,600 km/h at the equator. A shallow-water wave in a 4 km deep ocean travels at
about 700 km/h. The ocean physically cannot keep up, so the tide is not a bulge
riding under the Moon; it is a **wave** sloshing around basins.

**Basins resonate.** Each ocean basin has a natural period set by its size and
depth. When that is near 12.4 hours, the tide is amplified enormously, like
pushing a child on a swing at the right rhythm. The Bay of Fundy resonates
almost perfectly and gets 16-metre tides.

**Shallow water distorts.** The crest travels faster than the trough, so rise
and fall take unequal times.

**Friction lags everything.** Which is where the lunitidal interval comes from.

**Weather.** ~1 cm of sea level per millibar of pressure. Wind piles water up.

## Consequences

- Most coasts: two highs a day (semidiurnal)
- Some coasts: one (diurnal), parts of the Gulf of Mexico, Fremantle
- Some: two unequal (mixed), much of the Pacific coast
- Mediterranean: almost no tide, because it is nearly enclosed
- Bay of Fundy: 16 m

## How real prediction works

Not from this geometry at all. It works by **harmonic analysis**:

1. Measure water level at a station, every few minutes, for a year or more
2. Decompose the record into ~40 sine waves at known astronomical frequencies
   (M2, S2, N2, K1, O1...)
3. Measure the **amplitude and phase of each one at that station**
4. Predict by adding the waves back up

The astronomy supplies the **frequencies**, those come from orbital mechanics
and are the same everywhere. Only measurement can supply the **amplitudes and
phases**, those are properties of the coastline.

That is the deep lesson of this module:

> A good model often needs both theory and local data. Knowing which parts must
> come from measurement is most of the skill.

## Checkpoint

- [ ] I can explain why the ocean cannot keep up with the bulge
- [ ] I know what basin resonance is and can name an example
- [ ] I can explain why some coasts have one high a day
- [ ] I know what harmonic analysis is
- [ ] I can say which parts of a tide prediction come from theory and which
      from measurement

## Questions to think about

- Harmonic analysis needs a year of data per station. What about uninstrumented
  coasts?
- Could you predict tides for a coastline that does not exist yet, a planned
  reclamation, say?
- What other everyday predictions are theory plus local calibration?

Next: [Module 05, Your local sky](../05-local-sky/).
