# Owner decisions on the P1 rework after RV-016 and RV-017 (2026-11-22)

The owner (Ben Spoor) answered eleven questions in the working session, one at a time, each with a short plain explanation
and the assistant's recommendation (the question texts are in the session). Source reviews:
`docs/reviews/RV-016-p1-plan-rev5-as-built-goldfish.md`, `docs/reviews/RV-017-adr0023-gate-simplification-goldfish.md`.

## Answers
| # | Question | Recommendation | Answer |
|---|---|---|---|
| 1 | Gate wiring after ADR-0023 | Restore U10 and R6 (gate takes only the supervisor, pull-up on VBUS_IC 150 k; the limiter fault reaches the processor through U10) | **Restore U10 + R6** |
| 2 | GPIO0 on CC_OK_1A5 | 10 kohm series resistor | **Add 10 k resistor** |
| 3 | R_ILIM3 value | 54.9 kohm (margins 13.1 / 12.7 mA) | **Keep 56.2 k, model it better** (resistor drift, ageing and the datasheet table anchor in the model first, then decide) |
| 4 | CC-pin protection | Add the P3 parts (ESD part and series resistors) chosen on 2026-11-07 | **Add P3 parts** |
| 5 | Source of U5 | Automotive twin if stocked, else JLCPCB global sourcing | **Other supervisor part** (a stocked supervisor with the same function; needs an ADR and new hold-off analysis) |
| 6 | R22 part | 1206 current-sense resistor of 2 to 5 mohm (meets HW-017 [10] mohm as approved) | **1206 shunt 2-5 mohm** |
| 7 | Drop from J1 to U7 | At most 100 mV at 1.5 A, R22 included | **100 mV at 1.5 A** |
| 8 | MECH-001 (housing 59.24 mm against 58 mm) | Deviation for P1 only | **Change MECH-001 to 60 mm** |
| 9 | Button SW1 (inside the LED ring, housing has a side button) | Accept for P1 | Free text: "Change mechanics so the entire center of the ring becomes the button. Change the button choice and mechanics etc to accommodate this" |
| 10 | Input-path placement rules on the re-placement | Enforce | **Enforce on re-place** |
| 11 | Records | Approve all four | **DEV-004 also for P1, DEV-007, DEV-008 as a record, ADR-0022 superseded** (all four) |

## Recorded in the controlled documents (this commit)
- MECH-001: upper limit 60 mm (approved amendment); the placer limit `mech_outline.MAX_DIM_MECH001` is 60.0; board test
  `test_housing_size_within_mech001` (board-p1: 59.24 mm).
- HW-017: approved amendment: J1 to U7 pin 1 at most [100] mV at 1.5 A with the link at its [10] mohm maximum; the link is
  a 1206 current-sense resistor of 2 to 5 mohm (part to be chosen). `pcb_power_check.py` `input_path.within_budget`, a gate
  in `fab_p1.sh` and in `test_board_p1.py` (board-p1: 83.0 mV).
- ADR-0022: Superseded. DEV-004: approved for the spike and P1. DEV-007: approved. DEV-008: accepted as a record.

## Work that follows (not done in this entry)
- Decisions 1, 2, 4 and 5 change the schematic and the gate: a new ADR for the gate rework (restore ADR-0018 option E with
  U10 and R6, GPIO0 resistor, P3 CC protection) and one for the supervisor choice (real alternatives, datasheet evidence,
  hold-off recalculation); the HW-010, HW-003, SW-009 and SW-005 texts as proposals for the owner; tests (gate truth table on
  the new netlist, RV-017 row 8).
- Decision 3: model resistor TCR, ageing and the table anchor in `sim/ilim_steps.py`, then the owner decides 56.2 k or 54.9 k.
- Decision 6: find the 1206 shunt part with datasheet evidence (rating, resistance, LCSC number).
- Decision 9: a new button concept (the whole centre of the ring is the button): requirement changes (HW-007, a MECH
  requirement for the actuation), an ADR, a plan with the owner's interview (EGM), and a new switch part and housing parts.
- Then plan 08 revision 6, its readiness review, and the new placement and routing with the enforced rules.
