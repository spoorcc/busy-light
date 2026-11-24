# ADR-0024: Gate rework after RV-017: hold-off AND gate restored, GPIO0 resistor, CC-pin protection

- **Status:** Accepted (owner, Ben Spoor, 2026-11-24, in the working session; recorded by the assistant). The three choices are owner decisions 1, 2 and 4 of 2026-11-22 (in the working session; recorded by
  the assistant, `docs/journal/2026-11-22-owner-decisions-p1-rework.md`). The owner accepted the ADR on 2026-11-24 on the assistant's
  summary of it; the requirement amendments stay for the owner to confirm; no goldfish review. Amends ADR-0023 (withdraws its decision 2) and
  returns to ADR-0018 option E.
- **Date:** 2026-11-22
- **Deciders / reviewers:** owner (Ben Spoor); written by the assistant
- **Related:** HW-010, HW-003, HW-006, SW-009, SW-005, ADR-0016, ADR-0018, ADR-0023, ADR-0025, RV-016 rows 2 to 4, RV-017 rows
  1 to 5, 8, 12 to 15, RISK-047 to RISK-050

## Context and problem
RV-017 rejected ADR-0023 decision 2 (U5 RESET and U7 FAULT wired on one node GATE_OK_RB, pulled up to 3V3 with 10 kohm, GPIO6
on the node). Its regressions: GPIO6 can hold the gate open (row 1), the node reads "OK" with VBUS gone and 3V3 up (row 2), a
reset loop and a latch under overload (rows 3, 4), a limiter trip at step 3 drops to step 1 (row 5), and the decision had no
alternatives of its own (row 12). RV-016 rows 2 and 4 add GPIO0 on CC_OK_1A5 without a series resistor and the missing CC-pin
protection that the owner chose on 2026-11-07 (P3) and that HW-003 (Approved) asks for. ADR-0023 decision 1 (step 3 = both
switches, U13 removed) and decision 3 (packages) are not changed here. This ADR records the three choices as separate
decisions, each with its own alternatives.

Numbers: `sim/gate_rework_levels.py` (`tests/test_gate_rework_levels.py`); evidence `sn74lvc1g08.yaml` (pin table of the DBV
and DCK packages read again 2026-11-22: 1 A, 2 B, 3 GND, 4 Y, 5 VCC), `tps3840dl40.yaml`, `tusb321.yaml`, `pesd5v0s1ba.yaml`.

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| The gate stays independent of the firmware (no GPIO can open it) | 5 | HW-010, ADR-0016 |
| Safe state in every partly powered state (VBUS gone, 3V3 up) | 5 | HW-010 criterion 8, SW-009 |
| No reset loop or latch under overload; SYS-020 "no reset at constant load" | 4 | SYS-020, SW-007 |
| Parts and area on the one-sided P1 | 3 | HW-008, plan 08 |
| Change to approved texts (fewer is better) | 2 | HW-010, SW-009 |

## Decision 1: the third gate input and the fault path
### 1A. Restore ADR-0018 option E (owner decision 1)
HOLD_OK = U5 RESET (open drain) with R6 150 kohm to VBUS_IC, on pin 6 of both 3-input ANDs (U3, U4). FAULT_N = U7 FAULT (open
drain) with R8 100 kohm to 3V3. U10 (SN74LVC1G08, SC-70 DCK, on 3V3) = HOLD_OK AND FAULT_N, its output GATE_OK_RB to GPIO6
only. A limiter fault reaches the processor (SW-009 shed), not the gate. HOLD_OK high level with R6 and the worst-case leakage
of three LVC inputs and U5 (15.1 uA): 2.04 V at VBUS_IC 4.3 V, 2.49 V at 4.75 V (VIH 2.0 V); R6 meets the VPOR rule (at least
134 kohm). A firmware output on GPIO6 now fights only U10's output, not the gate (row 1 closed for GPIO6).
### 1B. Keep the wired node, move the pull-up to VBUS_IC (at least 134 kohm) and add a 10 kohm resistor on GPIO6
Closes rows 1 and 2 with one part fewer than 1A. Keeps the coupling of a limiter fault to step 1 (rows 3 to 5) and puts the
TPS2553 FAULT pin (7 V absolute maximum) on a VBUS_IC pull-up during the hot-plug clamp (8 to 14 V, ADR-0021).
### 1C. Keep ADR-0023 as built (do nothing)
All regressions of RV-017 rows 1 to 5 stay.

| Criterion (weight) | 1A | 1B | 1C |
|---|---|---|---|
| Independence (5) | 5 | 4 | 1 |
| Partly powered (5) | 5 | 4 | 2 |
| Overload (4) | 5 | 2 | 1 |
| Parts (3) | 3 | 4 | 5 |
| Texts (2) | 4 | 2 | 3 |
| **Sum** | **87** | **64** | **40** |

## Decision 2: GPIO0 on CC_OK_1A5
### 2A. 10 kohm series resistor between CC_OK_1A5 and GPIO0 (owner decision 2)
A GPIO0 driven high sends at most 0.36 mA into the U2 output, which keeps CC_OK_1A5 low. **Finding:** with the ESP32-C3
internal pull-up left on at its 30 kohm corner the pin reads 0.75 V when U2 drives low, equal to VIL (0.25 x 3.0 V); with the
typical 45 kohm it reads 0.55 V. So the firmware keeps the GPIO0 pull-up off (as SW-009 already requires for GPIO20 and
GPIO21). New net CC_OK_RB (R23, 0402).
### 2B. No resistor; a software rule that GPIO0 stays an input, with a register test
No part, but the gate's independence then rests on the firmware (ADR-0016 says it must not).
### 2C. Nothing
RISK-048 stays open for GPIO0.

2A is the only option that keeps the gate independent of the firmware; it adds one 0402 part.

## Decision 3: CC1 and CC2 protection (owner decision 4: "P3", ESD part and series resistors)
### 3A. Two PESD5V0S1BA (the TVS1 part) at the connector and 100 ohm in series to the TUSB321 (recommended realisation)
Bidirectional, 5 V stand-off, breakdown 5.5 to 9.5 V, 35 pF typical, IEC 61000-4-2 contact 30 kV, no VBUS reference; no new
part type (C19224, 141,197 at JLCPCB on 2026-11-22). The 100 ohm limits the current into the TUSB321's own ESD structure;
it does not keep the pin under 6 V by itself (`analysis-cc-pin-protection.md`). Effect on detection: the voltage the TUSB321
sees drops by 0.16 to 0.68 % with a resistor Rp (none with a current-source Rp); the source sees 4.70 to 5.70 kohm (TUSB321
RCC_D 4.6 to 5.6 kohm plus 100 ohm). The USB Type-C limits for Rd were not read; the upper corner is 1.6 % above 5.61 kohm
(5.1 kohm + 10 %, as recalled, not read). New nets CC1_IC and CC2_IC; refs TVS3, TVS4, R24, R25.
### 3B. One USBLC6-2P6 (the U6 part) on CC1 and CC2 with its VBUS pin on VBUS
One part. Against: the source applies Rp before it turns VBUS on; the steering diode from CC to the VBUS pin then clamps CC
near the VBUS node plus a diode drop and feeds the source's Rp current into VBUS (and through R22 into VBUS_IC and the
TUSB321 supply), which can disturb the attach detection. Rejected for this reason (not measured).
### 3C. A dedicated two-line CC ESD part (for example the TPD2E2U06 class)
Lower capacitance, but a new part type with no datasheet read and no stock checked.
### 3D. Nothing (P2)
The owner chose P3 on 2026-11-07 and again on 2026-11-22.

3A follows the owner's P3 with a part that is already on the BOM and avoids the VBUS back-feed of 3B.

## Decision
1A, 2A and 3A, plus a FAULT_N test pad (TP7, bottom side, not in the BOM) because ADR-0018 condition (1) applies again now
that FAULT_N is its own net. U10 = SN74LVC1G08DCKR (C7832, 207,023 at JLCPCB on 2026-11-22), R6 = 150 kohm 0402
(0402WGF1503TCE, C25755, extended), R8 = 100 kohm 0402 (C25741), R23 = 10 kohm 0402 (C25744), R24 and R25 = 100 ohm 0402
(0402WGF1000TCE, C25076, basic), TVS3 and TVS4 = PESD5V0S1BA (C19224).

## Consequences
- Positive: RV-017 rows 1 to 5 closed by design (GPIO6 off the gate, pull-up on VBUS_IC, no fault-to-step-1 coupling, so no
  reset loop or latch from the hardware); GPIO0 cannot open the gate; HW-003 CC protection on the board; FAULT_N measurable.
- **Negative / trade-offs accepted:** seven more parts on the top side (U10, R6, R23, R24, R25, TVS3, TVS4; R8 changes value;
  TP7 is a bottom pad), on a board whose placement is tight (ADR-0025 option B removes five); the firmware cannot tell a
  hold-off from a fault on GPIO6 (ADR-0018 trade-off, unchanged); the HOLD_OK high level has 0.04 V margin at the 4.3 V
  reference with worst-case leakage (it rises with VBUS_IC; typical leakage is far lower); a missing or open U5 still leaves
  HOLD_OK pulled high (RISK-047: the gate fails open; inherent to an open-drain output with a pull-up).
- New or changed risks: RISK-048 to RISK-050 mitigated by design (to update); R6 open leaves HOLD_OK floating when U5 releases
  (an undefined CMOS input; add to the fault table); TVS3 or TVS4 shorted holds a CC line at 0 V (no attach, the safe side).
- Requirements created or changed (proposals for the owner, written in the requirement files): HW-010 (ADR-0023 amendment item
  2 withdrawn; the approved 2026-11-07 amendment item 3 applies; GPIO0 series resistor; fault-table rows), HW-003 (the CC
  protection parts), SW-009 (GATE_OK_RB = hold-off AND no fault again; GPIO0 and GPIO6 pull-ups off, GPIO0 never an output),
  HW-006 (TP7 FAULT_N). SW-005 is not changed by this ADR (RV-017 row 7 comes from ADR-0023 decision 1).

## Verification and revisit
`tests/test_layout_full.py` (nets of HOLD_OK, FAULT_N, GATE_OK_RB, CC_OK_RB, CC1_IC, CC2_IC), `tests/test_gate_logic_full.py`
(truth table and single faults of the gate on the generated `full.net`, RV-017 row 8), `tests/test_gate_rework_levels.py`;
strict ERC 0 findings. Bench TC-210: FAULT_N forced low with the gate open (GATE_OK_RB falls, the step does not), GPIO0 and
GPIO6 driven high (no step change), VBUS_IC below 1 V with 3V3 up (HOLD_OK low); IEC 61000-4-2 on CC1 and CC2 (test case to
write). Revisit if the ESD test fails or the CC detection misreads a band-edge Rp.

## Critical review notes
Strongest objection: "1A adds a part and a net back two days after ADR-0023 removed them for area." Answer: the area problem
is real, but ADR-0023 bought it with the gate's firmware independence and with safe states that HW-010 requires; ADR-0025
option B gives back more area than 1A and 3A take. Second objection: "100 ohm in series pushes the Rd seen by the source above
the Type-C tolerance at one corner." Answer: recorded; the shift at the TUSB321 is below 0.7 %, the Type-C document is not read,
and the band-edge tests of HW-003 cover it; a smaller resistor (for example 33 ohm) is the fallback if the owner prefers it.
