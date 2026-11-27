# Analysis: can the P1 placement rules be met together? (plan 08 section R, RV-019 pass 3, S4)

- **Date:** 2026-11-27. **Author:** assistant. **Status:** Draft analysis for the owner. Nothing chosen. Placement only: no router, no board stored.
- **Asked by:** readiness pass 3 of plan 08 section R (RV-019), finding S4: four placements of batch c1 all missed 7 to 12 of the 22 rules.
- **Tools:** `hw/kicad/spike-gate/run_place_best.sh`, `src/place_table.py`, `src/pcb_place.py` (`place(..., misses=)`, `PLACE_RULE_PEN`), `src/pcb_full.py`; tests `tests/test_pcb_place.py` (`SeedChoice`, `RulePenaltyKnob`), `tests/test_place_table.py`.
  Netlist `tests/data/full.net` (104 parts). Environment of plan 08 section 4.3: `P1=1 PLACE_GRID=1.0 PLACE_ANT_KEEPOUT=1 PLACE_BLOCKS=3 PLACE_ORIENT=1.5`, 160 000 annealing iterations, KiCad 10.0.8 image by digest.

## 1. Question
`pcb_full.py` puts the movable parts with an annealer. A proximity rule is a cost of `RULE_PEN` per mm beyond its limit, not a hard constraint. Plan 08 R4 (d) needs all 22 rules met (16 `LAYOUT_RULES`, 6 `INPUT_PATH_RULES`). Is that reachable, or are the rules over-constrained?

## 2. Runs (four placements per setting, seed groups 1 to 64 as `run_best.sh` gives them)
| Setting | Seed kept | Misses per placement | Overlap |
|---|---|---|---|
| `RULE_PEN` 40, shortest wire kept (as before; run by the readiness reviewer) | shortest wire | 8, 7, 10, 12 | 0 |
| `RULE_PEN` 300, fewest misses kept | fewest misses | 7, 6, 4, 5 | 0 |
| `RULE_PEN` 3000, fewest misses kept | fewest misses | 4, 4, 4, 4 | 0.13 to 0.26 mm2 |

At 3000 every placement misses four rules, all input-path rules (TVS1, TVS4, R22 and TVS3 in three placements; U6 instead of TVS3 in one), each by a small amount, and the placer needs overlap to get that close:
| Rule | Limit (mm) | Best distance at 3000 (mm) |
|---|---|---|
| TVS1 to J1 `VBUS` pad | 6.0 | 6.5 to 7.5 |
| TVS3 to J1 `/CC1` pad | 6.0 | 6.54 to 7.28 (met in one placement) |
| TVS4 to J1 `/CC2` pad | 6.0 | 6.89 to 8.31 |
| R22 to J1 `VBUS` pad | 8.0 | 8.45 to 10.89 |
| U6 to J1 `VBUS` pad | 8.0 | 8.04 (met in three placements) |

## 3. Space next to J1
J1 sits at the edge of the board. Its `VBUS` and `CC` pads are at x 22.5 to 23.9 mm, y -2.1 to 2.1 mm from the board centre. On the best placement of the 300 setting, the nearest footprints are J1, D1 (2.7 mm), C8, C23, D16, R_ILIM1, DZ15, then TVS1 (6.8), U6 (7.6), R22 (9.7), TVS4 (9.8).
The area within 8 mm of those pads is 273 mm2. Of it, positions where the smallest input-path part (3.3 x 2.0 mm) is legal, outside the U9 courtyard and inside the movable region, cover about 35 mm2 of part centres. The five input-path parts have courtyards of 6.5 (TVS1), 7.1 (U6), 10.9 (R22), 6.5 (TVS3) and 6.5 (TVS4) mm2, 37.5 mm2 together,
and D1, C8, C23, D16, R_ILIM1 and DZ15 compete for the same patch. This is a rough comparison (free area of part centres against courtyard area), not a packing proof.

## 4. Reading
- The rules are over-constrained, not the annealer too weak: ten times more cost per mm moves the best placement from 7 to 4 misses and then stops, with overlap.
- The CC rules for TVS3 and TVS4 (6.0 mm) were added with the ADR-0024 implementation (`INPUT_PATH_RULES` in `pcb_full.py`). ADR-0024 names the parts but gives no distance. The 6.0 mm is the assistant's copy of the TVS1 limit; no datasheet layout guidance was read.
  They add 13 mm2 of courtyard demand to the patch beside J1. TVS1, U6 and R22 come from plan 08 section 4.2 (HW-003, HW-017), also analyst values.
- Not shown: that no placement exists (four placements per setting, one seed group, the annealer is a heuristic), and what limits would be met without overlap. The runs only bound the limits from below at 6.5 mm (TVS), 8.5 mm (R22) and 8.0 mm (U6).

## 5. Options for the owner (the assistant does not change a rule)
1. **Relax the limits** of TVS1, TVS3, TVS4, R22 and U6 (for example TVS 9 mm, R22 and U6 10 mm; the assistant confirms by R2a before it asks for approval). The electrical cost (ESD clamp distance, input-path inductance and drop) is to be argued from the TVS datasheet layout guidance, which is not read yet.
2. **Allow input-path parts inside the U9 courtyard** where no antenna keep-out applies (DEV-004 gets a refs and count change). RF risk: a decision with the antenna analysis (TC-205), not run.
3. **Protect the CC lines differently** (reverses part of ADR-0024; the owner's CC-protection decision of 2026-11-07 stays), for example one TVS array part instead of TVS3, TVS4 and their resistors.
4. **Grow the board** beyond 60 mm (MECH-001 amendment, housing).
5. **Move parts to the bottom side**: not possible with one-sided assembly (HW-008).

Recommendation: option 1 first (cheapest, no requirement or housing change), after the TVS datasheet is read; option 2 only with an antenna review.

## 6. Not run
Routing, any batch beyond the seed groups above, the TVS datasheet check, the antenna range, and a placement with a rule changed (waits for the owner).
