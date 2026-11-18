# Owner decisions on simplifying the schematic for one-sided placement (2026-11-18)

Owner request: "Be creative, simplify the schematic to strive for single side placement." The assistant measured part areas and
ran placement experiments (scratch copies of the generator, 46 mm board, all parts on top, vendor antenna keep-out on, 16 seeds
of 160000 iterations; journal `2026-11-18-overnight.md` for the method):

| Set | Changes | Best overlap (mm2, 0 = fits) |
|---|---|---|
| today | | 25.1 |
| X2 | step 3 = both ILIM switches on (U13 out); FAULT_N wired onto the hold-off node (U10 out); zeners SOD-323 | 10.5 |
| X4 | X2 + hold-off and spare capacitors 0805 + logic U2, U3, U4, U11 in SC-70 | 1.7 |
| X6 | X4 + 13 non-critical resistors 0402 + one pull-up fewer + button on the internal pull-up | **0.0** |

Movable-part area before the change: 469 mm2 (60 parts). Step-window calculation for "step 3 = both switches on"
(`hw/kicad/spike-gate/sim/ilim_steps.py`, 0.1 % resistors, TMUX1101 limits): with R_ILIM3 = 56.2 k (same part as R_ILIM2):
step 1 504.2 to 616.6 mA, step 2 934.9 to 1091.7 mA, step 3 1368.8 to 1553.5 mA (margins 2.8 and 23.5 mA); no switch state
exceeds the step-3 maximum (today "both on" gives 1817 to 2020 mA and only the NOR gate prevents it).

## Answers (owner, Ben Spoor, 2026-11-18, in the working session)
| # | Question | Answer |
|---|---|---|
| 1 | Step 3 = both ILIM switches on, R_ILIM3 = 56.2 k (U13 out; firmware sets both selects for step 3; SW-009 "never both" changes) | **Yes, R3 = 56.2 k** (recommended) |
| 2 | Wire FAULT_N onto the hold-off node, one pull-up to 3V3 (U10 and one pull-up out; a limiter fault now also closes the hardware gate) | **Yes, fault closes the gate** (recommended) |
| 3 | Package changes: SOD-323 zeners, 0805 capacitors, SC-70 logic, 0402 resistors, button pull-up removed | Free text: "What you recommend maybe lookup info" |

Assistant's choice for answer 3 (answer 19 of 2026-11-17: reversible, logged): all four package changes, because only the full
set X6 reached overlap 0 in the measurement. Part numbers for the new packages are looked up on the web (distributor listings,
snippets; datasheet and shop sites are blocked from this container) and marked as lookups, not verified sourcing.

## Effects (to be written into the controlled documents)
- ADR-0023 (new): records decisions 1 and 2 with alternatives; amends ADR-0016 (gate logic) and ADR-0018 (FAULT_N now gates).
- HW-010: steps no longer exclusive; step 3 = both switches; R_ILIM3 = 56.2 k (replaces trim T1, 27.7 k); fault-injection table
  rows change; HOLD_OK node pulled up to 3V3 and shared with FAULT_N.
- SW-009 / SW-005: firmware drives both selects for step 3; the "never both" rule and the "EN2 and EN3 both high is unknown"
  state change; gate.c and its tests follow (sw/ change after the requirement text is approved).
- HW-016: spare size [1206] becomes [0805]; HW-007: button pull-up internal.
