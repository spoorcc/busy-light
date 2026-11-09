# ADR-0021: Hot-plug surge on VBUS_IC and +5V: measure first on the prototype (option S1)

- **Status:** Proposed (owner chose S1 in the working session of 2026-11-09; this text is not yet accepted)
- **Date:** 2026-11-09
- **Deciders / reviewers:** Ben Spoor (owner); open finding 9 of goldfish review RV-013
- **Related:** HW-010, HW-014, HW-015, HW-017, ADR-0010, ADR-0016, RISK-046, `docs/verification/reports/analysis-vbus-5v-part-ratings.md`, `docs/verification/reports/shortlist-tvs1-3v3-regulator.md`

## Context and problem
A live USB plug-in puts a surge on VBUS_IC. TVS1 is the only protection on the connector side. A plain 5 V TVS clamps at 10 V at 1 A and 14 V at 12 A (PESD5V0S1BA, datasheet text via web search, PDF not opened). Several parts have an absolute maximum below that: TPS2553 7 V, TUSB321 and TMUX1101 supply pins 6 V, TLV75733P 6 V, LED placeholder 5.3 V (`analysis-vbus-5v-part-ratings.md`, unverified evidence files for some). Not known: the real plug-in current and voltage. Ringing of the cable inductance against the low-ESR ceramics (4.7 uF on VBUS_IC, 10 uF and more on +5V) can overshoot the supply, up to about twice in the general experience of the author (not measured, not sourced here). The spike board exists to learn; no production surge level is set yet.

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Parts stay inside their absolute maximum | 5 | HW-010 criterion 4, RISK-046 |
| Decision rests on measured data | 4 | `docs/process/verification-strategy.md` |
| Change to the spike board and re-open of accepted ADRs | 3 | ADR-0010 decision 5 |
| Added voltage drop in the 1.5 A path | 3 | SYS-021, HW-004 |
| Cost and effort before the first board can be built | 3 | SYS-021 |

## Alternatives considered
### S1. Measure first; plain 5 V TVS on the spike, plus a damping footprint (HW-017)
Strongest case: the real surge is unknown and the measurement is cheap (TC-210 step 4, extended by TC-217). The footprint lets the spike test the series-element option without a respin. Cons: until measured the spike may see more than 6 V; one board may be damaged.
### S2. Replace the TPS2553 by the TPS25200
20 V input, 5.4 V output clamp, over-voltage lockout 7.6 V (values from ADR-0010 E11, datasheet not read in this work). Strongest case: one part protects VBUS_IC side and +5V; no dependence on a TVS clamp. Cons: re-opens ADR-0010 decision 5; different limit range and resistor values; stock and fee not checked; the 5.4 V clamp is above the 5.3 V of the LED placeholder; changes accepted ADR-0016 gate values.
### S3. Series element before the TPS2553 and a lower-clamp TVS now
Ferrite or a few ohm, plus a larger TVS. Strongest case: keeps the TPS2553 and reduces the surge current without a part change. Cons: the 1.5 A path drops 0.15 V per 0.1 ohm; not simulated; the value is chosen without data.
### D. Do nothing / defer
Keep the TVS and the supply-pin resistors and zeners and make no surge plan. Strongest case: no change. Cons: no evidence, and the unprotected parts stay unprotected.

## Comparison
| Criterion | S1 | S2 | S3 | D |
|-----------|----|----|----|---|
| Parts inside absolute maximum | unknown until measured | likely yes (not verified) | likely reduced, not shown | no |
| Measured data | yes | no | no | no |
| Change and re-opened ADRs | footprint only | high | medium | none |
| Added drop | 0 (0 ohm fitted) | not assessed | 0.15 V per 0.1 ohm | 0 |
| Effort before first board | low | high | medium | none |

## Decision
We choose S1 because the surge level is unknown and a measurement decides between S2 and S3 at low cost. The spike gets TVS1 PESD5V0S1BA,115 and the damping footprint of HW-017. The choice of S2 or S3 for the next board is not made here and needs its own ADR after the TC-217 record.

## Consequences
- Positive: the choice of the production protection rests on a scope record; the spike can test a series element by changing one part.
- **Negative / trade-offs accepted:** until the measurement the spike can exceed the absolute maximum of the 6 V and 7 V parts at plug-in; one board may be lost. The first plug-ins use a current-limited lab supply and a short cable.
- New risks (add to risk register): RISK-046.
- Requirements created or changed: HW-017 (new, Draft); HW-010 criterion 4 is not changed; HW-014 and HW-015 keep their wait on the surge decision until the TC-217 record exists.

## Verification and revisit
Verified by TC-217. Revisit when the TC-217 record exists, or when a part is damaged at plug-in. Trigger for S2 or S3: a peak above 6 V at any 6 V pin or above 7 V at the TPS2553 with the 0 ohm link fitted.

## Critical review notes
Strongest objection: S1 knowingly lets a first board run outside the ratings of several parts, and the TPS2553 and the 6 V parts are not protected by the resistor and zener work. Answer: partly accepted. The measurement is the point of the prototype; the lab supply and a short cable limit the first test, and HW-017 gives a fix to try on the same board. The expected overshoot is the author's judgement, not a measured or sourced figure. Second objection: S2 may be the end state anyway, so S1 delays it. Answer: possible; but S2 also reopens ADR-0010 and ADR-0016, and the data will say whether it is needed.
