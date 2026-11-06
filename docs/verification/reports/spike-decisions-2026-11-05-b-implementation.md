# Spike implementation of the owner decisions of 2026-11-05 (b): ILIM switches, ILIM resistors, hold-off capacitors

Status: Draft. Exploratory spike on branch `spike/hw-gate`, not a product design. Nothing here is Approved or Accepted, and no requirement or ADR text is changed.
Traces: HW-010, SW-009, ADR-0016, ADR-0010, ADR-0012 (Proposed), RISK-027, RISK-044.
Inputs: `owner-decisions-2026-11-05.md`, `analysis-ilim-switch-replacement.md` (with addendum), `stock-check-ilim-holdoff.md` (with addendum 2).
All numbers below are the output of the scripts and tests named in section 5, as observed on 2026-11-05. Nothing was built, measured on the bench or simulated in SPICE.

**Amendment 2026-11-06 (owner decision, after the owner was told that 56.9 k and 27.7 k at 0.1 % 0603 have no confirmed LCSC or JLCPCB source):** the ILIM resistors are now one 56.9 k part (R_ILIM2) and one 27.7 k part (R_ILIM3), both 0.1 % 0603; R_ILIM1 stays 47.0 k. R_ILIM3B (301 ohm) and the net `ILIM_D_U15_MID` are removed; the net count is 53 and the component count 92. **These two values are unsourced at 0.1 % 0603: no stock or order evidence exists for them.** The text below is updated to the new values; the section 5 results of 2026-11-05 are replaced by those of 2026-11-06 (section 5.1). Sections 1 to 4 otherwise record the first implementation.

## 1. Decisions implemented
| Decision | Implemented in | Result |
|---|---|---|
| (a) TMUX1101DCKR (LCSC C2673506, SC70-5) replaces the 2N7002 Q2 and Q3 | `gen_gate.py`, `layout_sch.py`, `layout_full.py` | U14 (step 2) and U15 (step 3). Pins: 1 D, 2 S, 3 GND, 4 SEL, 5 VDD (SCDS410D table 5-1, read from the stored datasheet). SEL high = on (table 8-1). VDD on 3V3 with C24 or C25 (100 nF). SEL is driven by the existing gate output (`ILIM_STEP2_EN`, `ILIM_STEP3_EN`). R18 and R19 (100 kohm) pull SEL to GND. R2 and R3 (10 kohm) and the readback R14 and R15 stay. Pins S and GND go to GND. The D pin goes to the ILIM resistor. |
| (a) exclusive steps | unchanged | U13 still takes `ILIM_STEP3_EN` (now the SEL net of U15). Truth-table tests unchanged and green. |
| (b) ILIM resistors, 0.1 %, 0603 | `layout_full.py` PARTS, `gen_gate.py` | R_ILIM1 47.0 k, R_ILIM2 56.9 k, R_ILIM3 27.7 k (amended 2026-11-06; first implementation was 56.2 k and 27.4 k + 301 ohm in series with the extra part R_ILIM3B and the net `ILIM_D_U15_MID`, now removed). Both values unsourced at 0.1 % 0603. |
| (c) hold-off capacitors | same | C1 220 nF, C1B 220 nF, C1C 100 nF, C1D 68 nF, all C0G 5 % 50 V, footprint 1206. The schematic now carries the 1206 footprint. The `FOOTPRINT_OVERRIDE` entries for C1 and C1B in `pcb_full.py` are removed. |

Reference designators U14, U15, R18, R19, C24, C25, C1C, C1D were unused before this change (checked in `layout_full.py`). Q2 and Q3 no longer exist.

Choices of the implementer, not of the owner:
- The 100 kohm pull-downs R18 and R19 are separate parts, as the owner decision says, although R2 and R3 already pull the same net to GND. The two pull-downs on one net give 9.09 kohm.
- The TMUX1101 is drawn as a generated box symbol (no KiCad library symbol was used), like U1 and U5.
- Footprint for the TMUX1101 is `Package_TO_SOT_SMD:SOT-353_SC-70-5`. Its pad numbers 1 to 5 equal the symbol pin numbers. The land pattern was not compared with the TI package drawing.

## 2. Placement change that the new parts forced
With the new netlist the annealer put R3 18.8 mm from the step 3 switch. The old layout rule (R3 within 6 mm of the switch) had held by chance. Changes:
- `pcb_place.py`: optional weights per net (default 1, so other nets behave as before).
- `pcb_rules.py`: `NET_WEIGHT` for `/ILIM_STEP2_EN`, `/ILIM_STEP3_EN`, `/SUP_CT`, `/ILIM`, and `PIN_TIES` for the bypass capacitors C24 and C25 at pin 5 of U14 and U15.
- `pcb_full.py`: passes the weights; the ties are pseudo-nets in the annealer only, not on the board.
- Test `test_gate_layout_rules` now also asks R18, R19, C24, C25 within 6 mm of their switch and C1C, C1D within 14 mm of U5 (C1 within 8 mm and C1B within 12 mm were already tested). Two new tests cover the weights.

## 3. Analysis re-run
### 3.1 ILIM step windows (`sim/ilim_steps.py`, new `candidate_c`)
Resistors 47.0 k, 56.9 k, 27.7 k, all 0.1 % (amended 2026-11-06; each step is one resistor). V_ILIM 1.0 V is still an ASSUMPTION (not found in the TPS2553 text read). The TMUX1101 numbers are data-sheet limits to 85 degC: leakage 0.2 nA per off switch, Rds(on) 9.5 ohm (SCDS410D table 6.6). Temperature coefficient of the resistors is not modelled.

| Step | Ideal switch, min to max (mA) | TMUX1101 limits, min to max (mA) | Requirement |
|---|---|---|---|
| 1 | 504.2 to 616.6 | 504.2 to 616.6 | HW-010 max 623; 500 min from the ADR-0010 table |
| 2 | 929.6 to 1085.9 | 929.6 to 1085.9 | proposed window 850 to 1150 (not Approved) |
| 3 | 1381.5 to 1566.7 | 1381.2 to 1566.7 | HW-010 1366 to 1577 |

- Margins with the TMUX1101 limits: step 1 minimum +4.2 mA, step 1 maximum +6.4 mA, step 3 minimum +15.2 mA, step 3 maximum +10.3 mA. The margins stay thin; they are set by the resistor tolerance and the TPS2553 equations.
- Step 2 is inside the proposed 850 to 1150 mA window: 79.6 mA of margin on the low side, 64.1 mA on the high side.
- Both switches on (excluded by the gate logic): 1812.0 to 2014.0 mA, above the top limit. The resistors alone do not exclude this state.
- Leakage budget per off switch (the value of leakage at which step 1 maximum or step 3 maximum reaches its limit): 118 nA at V_ILIM 1.0 V, 94 nA at 0.8 V, 142 nA at 1.2 V. The TMUX1101 figure of 0.2 nA is about 590 times below the 118 nA.
- Exit status of the script: 0 (the script prints "candidate C meets all four HW-010 numbers with the TMUX1101 limits: True").

### 3.2 Hold-off window (`sim/holdoff_cap.py`)
Set 220 + 220 + 100 + 68 nF (608 nF), 5 % per part, C0G 0 +/- 30 ppm/degC over -55 to 125 degC: tD 205.9 to 560.6 ms (window 200 to 600 ms), "in window". With the earlier 0.6 % temperature allowance: 205.2 to 562.2 ms. Margin to the limits: 5.9 ms to 200 ms and 39.4 ms to 600 ms. The old 470 + 150 nF set gave 210.0 to 571.6 ms. The 68 nF part named in the model is C3216C0G1H683JT000N; its stock figure (2,000, one source) comes from the stock report and was not re-checked. DC bias, ageing and leakage are taken as 0, as before. A new test reads C1, C1B, C1C, C1D from the netlist and checks the set against the window.

### 3.3 Readback divider with the pull-downs (`sim/readback_margin.py`)
The net `ILIM_STEPn_EN` now has R2 (10 kohm) in parallel with R18 (100 kohm): 9.09 kohm. The readback resistor is 100 kohm. Open gate output, worst-case supply 3.6 V:

| Case | Net voltage (V) | Against TMUX1101 SEL VIL max 0.8 V |
|---|---|---|
| GPIO21 drives high (ROM TX idle), ideal | 0.30 | 2.7 times margin |
| GPIO20 or GPIO21 input with pull-up 30 / 45 / 70 kohm | 0.24 / 0.21 / 0.18 | 3.3 times or more |
| Readback resistor shorted, pull-up 45 kohm | 0.61 | 1.3 times (excluded from the test, as before) |

- Gate output high (output resistance 100 ohm is an ASSUMPTION, not read from the data sheet): net 2.967 V against VIH min 1.35 V.
- SEL input leakage 0.05 uA (to 125 degC) on 9.09 kohm: 0.45 mV, negligible.
- The old 2N7002 test is kept as a regression and still passes.
- **Weak point found:** if one of R2 or R3 is open (single fault) and the gate output is also open and the MCU internal pull-up is on, only the 100 kohm remains and the net rises to 1.57 V with a 30 kohm pull-up. That is above VIL max (0.8 V). It needs two faults plus the pull-up, and the SW-009 rule (switch the internal pull-ups of GPIO20 and GPIO21 off) removes the pull-up. Without the added R18 and R19 the case is the same. This is recorded in a test (`test_one_pulldown_open_is_reported_not_hidden`), not fixed.
- Gate low with the internal pull-up on: pin 2.10 V, an invalid level (as in the earlier record). Unchanged. The firmware rule is still needed.

## 4. Open points that these changes do not close
- **TMUX1101 with ILIM near 1 V while 3V3 is below about 0.5 V** (addendum A.5 of `analysis-ilim-switch-replacement.md`): the schematic now has the part on exactly this node. The owner accepted the part; the condition was not settled by a bench measurement or a deviation. The generated sheet has no change for it.
- Stock: **0.1 % 56.9 k and 27.7 k 0603 have no confirmed LCSC or JLCPCB source (owner told 2026-11-06; the schematic uses them by owner decision). No stock or order evidence exists for either value.** The earlier values 56.2 k (query never succeeded in `stock-check-ilim-holdoff.md`), 301 ohm and 27.4 k are no longer used. 100 nF and 68 nF C0G 1206 (68 nF one source). TMUX1101DCKR JLCPCB class (Extended) is inferred from the twin part. Not re-checked here.
- The extra 301 ohm part of the first implementation is gone (92 components). Two unsourced values replace it; the risk that the board cannot be built from stock parts is open.
- Part evidence for the TMUX1101 in `hw/evidence`: **not written.** ADR-0017, `scripts/check_part_evidence.py` and `hw/evidence/` exist only on the branch `feature/part-evidence`, not on `spike/hw-gate`. Writing a file here would create a tree that conflicts with that branch. The TMUX1101 facts used above (pins, SEL levels, leakage, Rds) are from the stored datasheet `tmux1101.pdf` (SCDS410D) and were read again for this change; they are in this report only.
- Not done: docs `spike-full-board-schematic.md`, `analysis-ilim-steps.md`, `analysis-n4-holdoff-capacitor.md` still describe the earlier drawing and values (2N7002, 470 + 150 nF); they were not edited. HW-010 and SW-009 text, ADR-0016 and ADR-0010 were not edited (owner approval needed; an ADR amendment for the safety-relevant part change is still open, see section 6 of the switch analysis).
- Not run: Freerouting (no jar set, so the board was built and checked unrouted), SPICE, bench, regulatory check (a passive part swap and one analog switch are not expected to add a regulatory effect; not assessed), ERC with warnings (only the error severity is used by the scripts).

## 5. Evidence (commands and observed results)
### 5.1 Amendment of 2026-11-06 (56.9 k and 27.7 k, R_ILIM3B removed)
Python: `/home/ben/Programming/busy-light/.venv/bin/python`.
- Tests first (red): after changing the tests to the new values and before changing the generators, 7 tests failed: `test_step_3_resistor_is_a_single_part`, `test_generator_values_are_the_checked_set`, `test_candidate_values`, `test_ilim_resistor_values`, `test_tmux1101_ilim_switches`, `test_board_matches_netlist`, `test_netlist_facts` (`Ran 173 tests`, `FAILED (failures=7)`). The step window assertions of `test_windows_of_the_three_steps` were set to the new windows after the script run (they were not run red).
- After the change: `cd hw/kicad/spike-gate; PYTHONPATH=src:tests GATE_NET=tests/data/gate.net <venv python> -m unittest discover -s tests`: `Ran 173 tests`, `OK`.
- `sh run_full.sh <venv python> <out>`: `ERC errors: 0; intent nets: 53; drawn nets: 53; only in intent: 0; only in drawing: 0`. The script then **exits 1** at the strict ERC step: `footprint_link_issues: 95 > allowed 89`, `lib_symbol_issues: 240 > allowed 226` (known-open caps, see plan 06 A-9; the counts are one lower than before this change: 96 and 241). Because the script stops there, its determinism step did not run; it was run by hand: a second `layout_full.py` output compared with `cmp` to the first is identical.
- `sh run_layout.sh <venv python> <out>`: `ERC errors: 0 []; parity differences: 0`, then **exits 1** at the strict ERC step: `footprint_link_issues: 27 > allowed 21`, `lib_symbol_issues: 60 > allowed 46` (same known-open caps; the determinism step did not run in this script and was not run by hand).
- Fixtures `tests/data/gate.net` and `tests/data/full.net` were regenerated from these runs; neither contains R_ILIM3B.
- `python3 -I sim/ilim_steps.py` exit 0. Candidate C (TMUX1101 limits, 0.1 %): step 1 504.2 to 616.6 mA; step 2 929.6 to 1085.9 mA; step 3 1381.2 to 1566.7 mA; both on 1812.0 to 2014.0 mA. Margins: s1_min 4.2, s1_max 6.4, s3_min 15.2, s3_max 10.3 mA. Step 2 margin to the proposed 850 to 1150 mA window: 79.6 mA low side, 64.1 mA high side. Script line: `candidate C meets all four HW-010 numbers with the TMUX1101 limits: True`.
- Not run in this amendment: Freerouting, `run_pcb.sh`, `run_gate.sh`, `holdoff_cap.py`, `readback_margin.py` (not affected by the resistor values; not re-run), SPICE, bench, stock check. The 2026-11-05 results below are the first implementation and are not repeated for the new values.

### 5.2 First implementation, 2026-11-05 (values then: 56.2 k, 27.4 k + 301 ohm; 54 nets, 93 components)
Python: `/home/ben/Programming/busy-light/.venv/bin/python` (has kiutils, skidl and pcbnew); system `python3` has pcbnew but no kiutils.
- Tests first (red): the new and changed tests failed before the generator change (the failing list included the new gate-logic, layout, ILIM, hold-off, readback and PCB tests).
- `cd hw/kicad/spike-gate; PYTHONPATH=src:tests GATE_NET=tests/data/gate.net <venv python> -m unittest discover -s tests`: `Ran 119 tests ... OK`.
- Same with system `python3`: `Ran 73 tests`, 5 errors, all `ModuleNotFoundError: No module named 'kiutils'` (the same 5 modules as before the change). Not a pass; the venv run is the evidence.
- `sh run_full.sh <venv python> <out>`: `ERC errors: 0; intent nets: 54; drawn nets: 54; only in intent: 0; only in drawing: 0` and `deterministic: identical`. (Before: 53 nets; the new net is `ILIM_D_U15_MID`.)
- `sh run_layout.sh <venv python> <out>` (gate fragment, own writer): `ERC errors: 0 []; parity differences: 0` and `deterministic: identical`. The fragment sheet is now A3 (the cell no longer fits A4).
- Fixtures `tests/data/gate.net` and `tests/data/full.net` were regenerated from these runs (components 86 to 93).
- `sh run_pcb.sh <full out> <pcb out>` (system python3, no Freerouting): `placement build: identical`; KiCad DRC of the placed board: 95 schematic parity issues, all of the kind seen before (box symbols with named pins have no pad, substituted footprints); none names U14 or U15. The DRC list also has 93 `lib_footprint_issues`, 46 `silk_edge_clearance`, 43 `courtyards_overlap`, 43 `silk_overlap`; these were not compared with the run before the change. Placement: overlap 0.0 mm2, `largest_dim_mm` 59.79 (the earlier mech conflict, MECH-001 58 mm, is unchanged in kind).
- `python3 -I sim/ilim_steps.py` exit 0; `python3 -I sim/holdoff_cap.py`; `python3 -I sim/readback_margin.py`: numbers in section 3.
- The legacy path `run_gate.sh` (SKiDL schematic writer with its own router) was started and had not finished after about 3 minutes in its first generation attempt. It was stopped. **Not run to completion; no result.** The own-writer path (`run_layout.sh`, `run_full.sh`) is the one used for the checks above. Whether the old path was this slow before the change was not measured.
- Visual check: the changed area of the full sheet was exported to SVG and looked at once (one text overlap between R_ILIM3B and R_ILIM3 was fixed by moving the text). Not a review.
