# Analysis: exclusive current-limit steps (Q2 and Q3 never both on)

Status: logic analysis and drawing check. Nothing here was measured, simulated in SPICE or run on hardware. Nothing is approved by this report.
Traces: HW-010 (Draft proposal, owner decision 2026-11-05 item 4), ADR-0016, ADR-0010, SW-009 (proposed readback rule), RISK-042, RISK-044.
Implementation: `hw/kicad/spike-gate/src/layout_full.py` (full-board sheet), `src/layout_sch.py` and `src/gen_gate.py` (gate fragment, `tests/data/gate.net`). Tests: `tests/test_gate_logic.py` (class `ExclusiveSteps`), `tests/test_layout_full.py`.

## 1. Why

With both select MOSFETs on, R_ILIM2 and R_ILIM3 are in parallel with R_ILIM1 and the limit rises above the top step maximum (analysis-ilim-steps.md, test `both_select_mosfets_on_exceed_top_limit`). The owner decided that this state must be impossible by hardware for any input combination, not only by firmware.

## 2. Chosen logic

Added one part: **U13, 74LVC1G02 (2-input NOR), SOT-23-5**. Pins as in the KiCad symbol: A = 1, B = 2, GND = 3, Y = 4, VCC = 5 (+3V3). Datasheet pin order for this part was **not** read in this change (open item, same status as the other gate symbols; see datasheet-evidence-gate-logic.md for the 74LVC1G11).

```
CC_OUT1_N (IC output, active low) --A
                                      U13 NOR -- CC_OK_NOT_S3 = CC_OK AND NOT step 3 enable
ILIM_STEP3_EN (U4 output, Q3 gate) -B

U4 (AND3):  ILIM_STEP3_EN = CC_OK_1A5     AND SEL_STEP3 AND HOLD_OK     -> Q3
U3 (AND3):  ILIM_STEP2_EN = CC_OK_NOT_S3  AND SEL_STEP2 AND HOLD_OK     -> Q2
```

So `ILIM_STEP2_EN = CC_OK AND SEL2 AND HOLD_OK AND NOT ILIM_STEP3_EN`. NOR(CC_OUT1_N, EN3) equals CC_OK AND NOT EN3 because CC_OK is the inverse of CC_OUT1_N (U2). U13 replaces the CC_OK input of U3 only; U4, U2 and the CC_OK_1A5 net (GPIO0) are unchanged. U13 reads the real step 3 gate output, not the select line, so a fault in U4 is also seen. There is no logic loop (EN3 does not depend on EN2).

Alternatives not chosen: (a) inverter plus AND2 on the output side (two parts, no gain over one part for the faults below); (b) gating with SEL3 instead of EN3 (does not see a stuck U4 output); (c) a 4-input AND (no such single-gate part in the family used).

## 3. Truth table (all inputs, ideal gates)

CC_OK = 1 means CC_OUT1_N low (1.5 A or more advertised). HOLD = HOLD_OK. Rows with HOLD = 0 or CC_OK = 0 give EN2 = EN3 = 0, so they are shown once.

| CC_OK | HOLD | SEL2 | SEL3 | EN2 (Q2) | EN3 (Q3) | Result |
|---|---|---|---|---|---|---|
| 0 | x | x | x | 0 | 0 | step 1 only |
| x | 0 | x | x | 0 | 0 | step 1 only |
| 1 | 1 | 0 | 0 | 0 | 0 | step 1 |
| 1 | 1 | 1 | 0 | 1 | 0 | step 2 |
| 1 | 1 | 0 | 1 | 0 | 1 | step 3 |
| 1 | 1 | 1 | 1 | **0** | 1 | step 3 (the top step wins; was both on) |

The test `test_truth_table_all_input_combinations` checks all 16 combinations of CC_OK, HOLD, SEL2, SEL3 against `EN3 = ok AND SEL3` and `EN2 = ok AND SEL2 AND NOT SEL3`; `test_never_both_on_for_any_input_combination` checks that EN2 and EN3 are never both 1.

Readback: GPIO20 and GPIO21 read ILIM_STEP2_EN and ILIM_STEP3_EN through R14 and R15 (100 k, unchanged). Both nets are the real gate outputs, so with SEL2 and SEL3 both high firmware reads GPIO20 = 0 and GPIO21 = 1: the readback shows the real state, not the select request. R2 and R3 (10 k pull-downs) are unchanged; the added NOR input (B) loads EN3 with a leakage current only (value not looked up here).

Timing: when step 3 turns on, EN2 falls one NOR delay plus one AND delay after EN3 rises, so Q2 and Q3 can both conduct for a few ns to tens of ns (MOSFET turn-off with the 10 k pull-down is slower than the gate delay). Not analysed; the TPS2553 current limit response to such a transient is not known here. Turning step 3 off does not overlap (EN2 rises after EN3 falls).

## 4. Fault cases (single fault)

| Fault | Result | Covered? |
|---|---|---|
| U13 unpowered or output stuck low | U3 sees 0, EN2 = 0 (step 2 lost, no hazard) | yes (fail-safe to lower step) |
| U13 output open (net CC_OK_NOT_S3 floating at U3 pin 1) | floating input of U3, not defined | **no**; layout rule: short net, no stub |
| U13 output shorted to 3V3 or stuck high | U3 no longer sees step 3; both can be on when SEL2 = SEL3 = 1 | **no** (readbacks show both high; SW-009 rule can catch it) |
| U13 input B open (pin or trace) | NOR input floating, output undefined, can be high | **no** |
| U3 output shorted high (Q2 gate) | Q2 on regardless of U13; both on when step 3 is commanded | **no** (the logic acts on the input of U3, not on its output) |
| U4 output (EN3) stuck high | Q3 on, U13 forces EN2 = 0 | yes (the top step alone, as faulted) |
| EN3 stuck low or open at the U4/R3/NOR node | Q3 off; step 2 allowed; never both | yes |
| Open between the EN3 node (R3, U13 B, U4 Y) and the Q3 gate | Q3 gate floating, may conduct while the NOR sees 0 | **no**; layout rule: R3 and the U13 tap at the Q3 gate pin |
| CC_OUT1_N open or IC unpowered | pull-up R1 gives high, NOR output 0, EN2 = 0 | yes |
| CC_OUT1_N shorted high | NOR output 0, EN2 = 0 | yes |
| CC_OUT1_N shorted low (RISK-042) | CC_OK appears true for both; exclusion still holds | existing gap, unchanged |
| Q2 or Q3 drain-source short | step permanently enabled | **no**; not a logic fault |
| 3V3 gone, VBUS present | U13 and U3 unpowered, outputs low | yes |
| VBUS gone, 3V3 up | CC_OUT1_N reads 0 V, NOR gives 1 when EN3 = 0; HOLD_OK (pull-up to VBUS_IC) is the only barrier, as before | as before (RISK-044) |

Inputs of U13: A is on the 5 V domain (CC_OUT1_N, pulled to VBUS_IC), as for U2. Whether the 74LVC1G02 input is rated for 5 V with VCC = 0 V was **not** read (same open item as U2); the repeat of U2's argument is not evidence.

Single-fault coverage is therefore partial. The cases not covered are failures of the last gate stage or of the node to Q2/Q3, which a NOR on the input side cannot see. A full cover would need the exclusion at the Q2 gate itself (a gate after U3 with its own output as the new single point) or a hardware interlock outside the logic; no such option was drawn. The firmware can detect both-high with the two readbacks (HW-010 proposal, SW-009); that is detection, not prevention.

## 5. Other changes in the same commit

- ILIM resistor value strings set to the E192 0.1 % set of analysis-ilim-steps.md: R_ILIM1 `47k 0.1%`, R_ILIM2 `56.9k 0.1%`, R_ILIM3 `27.7k 0.1%`. R_ILIM2 stays an ASSUMPTION of that report (middle step target not stated in HW-010). `tests/test_ilim_steps.py` now reads the number before the tolerance (`ohms()` takes the first word) and its margin check now runs on these values (it returned early while they were `tbd`).
- A CC_OUT1_N net label was added next to U2 pin 2 on the full sheet and the fragment, so U13 pin 1 joins the drawn net.
- `tests/data/gate.net` was regenerated with `gen_gate.py --netlist-only` (adds U13 and net CC_OK_NOT_S3; the file header carries the generation time and source path as before).
- Not changed: R2, R3 (10 k), R4, R5 (100 k), R14, R15 (100 k), the GPIO20/21 assignment.
- Open for the PCB: 100 nF bypass of U13 (not drawn for U2, U3, U4 either), placement per the layout rules in section 4.

## 6. Evidence

Run from `hw/kicad/spike-gate` with the scratchpad venv (SKiDL 3.0.0, kicad-cli):

- `GATE_NET=tests/data/gate.net python -m unittest discover -s tests`: 69 tests, OK.
- `run_full.sh`: ERC errors 0; intent nets 53, drawn nets 53, only in intent 0, only in drawing 0; two builds identical.
- `run_layout.sh` (gate fragment): ERC errors 0, parity differences 0, deterministic identical.

Not run: SPICE or timing simulation of the transient in section 3, datasheet check of the 74LVC1G02 (pin order, 5 V input with VCC = 0 V, leakage), hardware test, worst-case analysis of the added load on EN3, PCB layout. The requirement text of HW-010 is a Draft proposal; no document was approved or set to Approved/Accepted by this work.
