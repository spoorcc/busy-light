# 2026-11-08: routing experiments for a tidier spike board

Owner request: a board that looks hand-made (clear, symmetric, grouped, aligned). Scope: spike board, HW-010. Batches in the
session scratchpad (not committed): ring8_1 to ring8_3 (seeds only), ring9_g05, ring9_g10 (placement grid), ring10 (grid 1.0 and antenna keep-out). Results and numbers: report `spike-pcb-placement-routing.md`, section "ring8 to ring10".

Decision (owner, 2026-11-08): both placement rules and ring-link geometry. The ring-link idea was dropped after measurement: the off-45 segments are about 0.1 mm each (pad jogs), so the picker weighs off-45 length.

Open: decoupling ties C5/C6 at U8; grouped placement of the USB, power and CC blocks; second batch of the ring10 setting; fab DFM check.

## Later the same day: ring11 to ring14

Batches (session scratchpad, not committed): ring11 (C5/C6 ties), ring12 (functional blocks and orientation), ring13 (strict ICs and test-point row, no gain, left off), ring14 (ring12 settings, new seeds, clean-up fix). Numbers: report section "ring11 to ring14".

Decisions (owner, 2026-11-08): grouped blocks with orientation (answer to "use grouped blocks but also consider orientation"); render and review, then write up (A then C); ring14 repeat of the ring12 setting (A). Schematic simplification (question of the owner): possible for the ILIM resistor pair and the supervisor timing capacitors, but a separate revision with requirement and ADR; the gate logic and switch steps are the HW-010 interlock and stay.

Finding: `pcb_fix.snap_to_vias` was never called; calling it at the reported sites removed the last `track_not_centered_on_via` findings (regression tests added). Two of 12 ring14 runs pass the strict gate.

Open: fab DFM check on ring14 run 9; second ring14 batch for a pass rate; test points and IC rotations of run 9; the six-capacitor supervisor cluster and the ILIM pair (separate revision); `test_gate_logic.py` errors (`GATE_NET` not set in my runs, not investigated). Nothing committed, nothing pushed.

Fab check (owner choice "A then c"): `src/pcb_fabcheck.py` compares ring14 run 9 with the JLCPCB minimums of ADR-0020: all seven checks pass, the via ring is exactly at the absolute minimum (131 vias below the recommended 0.20 mm). Partial and single-fabricator: ADR-0020 stays Proposed, so the fine profile of every gate-clean board is not a decided rule.

## Ring15

Owner choice: soft placement rules for the test points and IC rotations, then one more batch (answer "Yes"). Batch ring15 (ring12 settings, `PLACE_ROWS=0.5`, `SEED_OFFSET=300`): 3 of 12 runs pass the strict gate (1, 2, 5). The picker chose run 1, but the power check found no +5V path on it and 50.4 mV on VBUS_IC. Run 5 passes all checks but is not better than ring14 run 9 (its test points are not in a row; VBUS_IC 41.9 mV against 13.5 mV). Decision (assistant, from the numbers): keep ring14 run 9 as the stored result. Follow-up: put the power check into the picker. The `test_gate_logic.py` errors need `GATE_NET` (by design). Owner request "store the board, update the README images": board stored in `hw/kicad/spike-gate/board/`, images re-rendered, README caption and status updated. Not done: push, PR.
