# ADR-0016: Independent hardware gate for the high current step

- **Status:** Proposed (only the owner sets Accepted). If accepted, it replaces the sensing decision of ADR-0009 (option A, ADC on the CC lines) and the "hardware backstop" wording of ADR-0010.
- **Date:** 2026-11-04
- **Deciders / reviewers:** Ben Spoor (owner); based on review RV-006 findings S1, S2 and S7; this ADR itself has no review yet
- **Related:** SYS-020, HW-003, HW-010, RISK-003, RISK-024, RISK-025, RISK-029, ADR-0004, ADR-0009, ADR-0010; RV-006; `docs/verification/reports/spike-7-5-power-budget-paper.md`

## Context and problem
ADR-0010 puts a current-limited load switch in the VBUS path: 500 mA at power-up, raised in steps by a firmware GPIO. Review RV-006 (finding S1) found that this does **not** protect a source that advertises only 500 mA if the firmware misreads the CC voltage and then raises the limit itself, because the same firmware decides both. It protects against a stopped, reset or never-started firmware and against a short circuit. The owner asked for a hardware limit because of this concern (SYS-020, owner decision 2026-11-04), so the gap is exactly the case the owner cares about. Finding S2 adds that a hung firmware with the GPIO high keeps the high step.
The wanted property: **the high step can switch on only if a part that is independent of the firmware has also seen that the source advertises at least 1.5 A.**
Related finding S7: the ADC margin of ADR-0009 option A is thin and its spike criterion cannot be met at worst-case band edges (reviewer recomputation, not repeated by me).

What this does and does not solve: it removes the firmware from the decision to raise the limit. A hung firmware at the high step on a source that really advertises 1.5 A stays within the source rating; the remaining risk is heat in the closed housing at 1350 mA (RISK-005, RV-004 T2), which is a thermal question and not solved here.

Not known: the CC-pin ratings of the candidate IC (datasheet pages not read for this ADR), its behaviour with a PD-capable charger (BMC traffic on the CC line, RV-006 S6), JLCPCB class and setup fee of the part, the pin state of the chosen ESP32-C3 GPIO during reset (E24 of ADR-0010).

## Decision criteria
| Criterion | Weight (1-5) | Source |
|-----------|--------------|--------|
| Independent of firmware for raising the limit (gate: score 0 excludes it unless the owner accepts the gap) | 5 | SYS-020, HW-010, RV-006 S1 |
| Detection accuracy and evidence (vendor-specified thresholds) | 4 | ADR-0009 E5, RV-006 S7 |
| Firmware can still lower or hold the lower step (brown-out back-off, RV-006 S5) | 4 | SYS-020 |
| Parts count, cost and board area | 4 | SYS-021, SYS-022 |
| Availability and second source | 3 | RISK-030 |
| Temperature range and datasheet evidence | 3 | ADR-0009 E14, E15 |
| Testability (fault injection, observable states) | 3 | process README |

## Alternatives considered

### A. Accept the gap (ADR-0009 option A with ADR-0010 as written)
The firmware reads the CC lines with the ADC and drives the select GPIO. The hardware limit covers a stopped firmware and a short.
Strongest case: no extra part, cheapest, ADC pins already planned, firmware keeps full control.
Cons: the main case of the owner's concern (source advertises 500 mA, firmware wrong) is not covered; RISK-025 stays open; the gate score is 0.

### B. CC detection IC, output ANDed with the firmware GPIO
A sink IC with its own Rd (TUSB321 type) reports the level on open-drain outputs (E14: OUT1 low means 1.5 A or 3 A). One AND gate (or a series MOSFET) lets the firmware GPIO select the high step only while the IC reports at least 1.5 A. The firmware also reads the IC outputs on two GPIO pins instead of two ADC pins, so the ADC read and its margin problem go away.
Strongest case: the thresholds are set and specified by the vendor (attach 0.20 V, 1.5 A at 0.66 V with 0.61 to 0.70 V, ADR-0009 E5); the firmware cannot raise the limit alone, but can still hold or lower it; if the IC fails the pull-ups read "default", the safe side (ADR-0009 B).
Cons: one more part (about USD 0.51 at 1 piece, snippet, E16) plus a gate; X2QFN 1.6 mm placement by the shop is unchecked; the datasheet lists 0 to 70 C recommended while LCSC lists -40 to +85 C (E14, E15); single source in the evidence (PTN5150A is a second candidate, snippet only, E17); the CC pins now belong to the IC, so ESD and VCONN questions (RV-006 S8, S14) move to its datasheet.

### C. Discrete window comparator on the CC lines, ANDed with the GPIO
Two comparators (or a dual comparator) with a divider reference at about 0.66 V, output ANDed with the GPIO.
Strongest case: no special IC; common parts; keeps an ADC read for the firmware as a second opinion.
Cons: more parts and area; accuracy depends on reference, resistor and comparator tolerances that I did not budget; the same CC levels as A, so the thin margin remains but now in hardware.

### D. Option B plus a heartbeat gate (retriggerable monostable) on the select line
As B, and the high step drops by itself if the firmware stops toggling a heartbeat pin.
Strongest case: also covers a hung firmware with the GPIO high (RV-006 S2) without the processor.
Cons: more parts (monostable and passives) and board area; the heartbeat adds a firmware task that can itself fail; the gain over B is small because B already limits the high step to sources that advertise it.

### E. Hardware-only select: the IC output drives the select directly, no GPIO permission
The IC output sets the step; the firmware cannot raise or lower it.
Strongest case: simplest and strictly independent; no gate part.
Cons: the firmware cannot hold the lower step after a brown-out, so the restart loop of RV-006 S5 has no hardware stop (only the LED budget); the limit follows the source whatever the firmware state.

### F. Do nothing / defer
Same as A until the owner decides. Not a separate option in the table.

## Comparison
Scores 0 to 5, my judgement; evidence from ADR-0009 E5, E14 to E17 (read or snippet as marked there); nothing measured. Max 130.
| Criterion (weight) | A | B | C | D | E |
|--------------------|---|---|---|---|---|
| Independent of firmware (5) | 0 | 4 | 4 | 5 | 5 |
| Accuracy and evidence (4) | 2 | 4 | 3 | 4 | 4 |
| Firmware can lower or hold (4) | 5 | 5 | 5 | 5 | 1 |
| Parts, cost, area (4) | 5 | 3 | 2 | 2 | 4 |
| Availability, second source (3) | 5 | 3 | 4 | 3 | 3 |
| Temperature range and evidence (3) | 4 | 2 | 4 | 2 | 2 |
| Testability (3) | 3 | 4 | 3 | 3 | 4 |
| **Weighted sum (max 130)** | 84 (gate 0) | **95** | 93 | 93 | 88 |

B leads C and D by 2 points, which is inside my scoring error. Sensitivity: if the weight of "firmware can lower or hold" falls by 2, E leads (86 against 85); if the weight of "temperature range" rises by 2, C leads (101 against 99). So the table does not decide between B, C and D. The recommendation rests on evidence: B is the only option whose thresholds and outputs I read in a datasheet (E5, E14), and it removes the thin ADC margin of finding S7.

## Decision
**Owner instruction 2026-11-04: follow the recommended option (B).** The status stays Proposed until the owner sets Accepted; HW-003 and HW-010 (Draft) are already drafted to match. The recommendation: **B, a CC detection IC with its output ANDed with the firmware GPIO.** The owner may instead accept option A (and RISK-025 stays open) or choose C or D.
1. **Gate:** the high step switches on only if the IC reports at least 1.5 A and the firmware GPIO is high. Both must agree. The firmware can always hold or drop to the lower step.
2. **Firmware reads the IC outputs** (two GPIO pins), not the ADC. The ADC read of ADR-0009 option A is dropped, so the 90 mV gap and the +-35 mV ADC error no longer decide the limit. A firmware misread can no longer raise the limit above the hardware reading; a wrong IC reading is the remaining failure and is covered by the vendor specification and test.
3. **Part:** the part and its second source are decided after the checks below; no part number is fixed here. Required checks before acceptance: the CC pin ratings and VCONN behaviour, the temperature range of the actual part (the conflict of E14 and E15), the JLCPCB class and setup fee, and behaviour with a PD-capable charger.
4. **Defaults when the IC output is undefined** (IC failed, unpowered): the pull-ups read "default", so the high step stays off (500 mA).
5. **Hung firmware (finding S2):** with B the high step cannot be on unless the source advertises it; the remaining effect is heat at the advertised current, handled by the thermal requirement (RV-004 T2). A heartbeat gate (option D) is not added now; revisit if the thermal analysis shows the high step is unsafe for a hung firmware.

## Consequences
- Positive: RISK-025 (firmware misreads CC) gets an independent path; the thin ADC margin disappears from the decision; the hardware limit claim of ADR-0010 becomes true for the owner's main case.
- **Negative / trade-offs accepted:** one more IC and one gate (about USD 0.6 at 1 piece, my estimate from the snippet price); an extended-part fee is likely and not looked up; single-source risk (RISK-030 style); the CC pins and their ESD and VCONN handling now depend on one datasheet; the spike 7.5 ADC measurement is replaced by an IC test.
- New risks (to add after the owner decides): IC misclassifies a charger (wrong band) with no firmware second opinion; IC temperature range; IC out of stock.
- Requirements created or changed: HW-003 (CC sensing by IC, ESD and clamp on CC), HW-010 (gate), SYS-020 (no change), a new SW requirement (read the IC outputs, hold or lower the step, brown-out back-off), ADR-0009 (superseded by this ADR for sensing), ADR-0010 (select line is ANDed), RISK-025 (residual text).

## Verification and revisit
- Bench test with chargers that advertise default, 1.5 A and 3 A, an e-marked cable, a PD-capable charger and a non-compliant cable: the high step must stay off unless the IC reports at least 1.5 A and the GPIO is high; firmware stopped, GPIO high and source advertising default must give 500 mA (TC-203, TC-210).
- Fault injection: IC unpowered, output shorted high, output shorted low, GPIO stuck high.
- Revisit when: the part checks fail, a better part is found, the owner decides to accept the gap, or the thermal analysis shows that a hung firmware at the high step is unsafe (then option D).

## Critical review notes
Strongest objection: "A CC IC is the same CC reading with a different part; if it misclassifies a charger, the limit is wrong and no firmware second opinion exists."
Answer: accepted. The gain is independence from firmware faults and a vendor-specified threshold, not a better reading of a bad source. A firmware ADC read could be kept as a second opinion (option C style) at the cost of more parts; the owner decides whether the second opinion is worth it.
Second objection: "A hung firmware at the high step still draws 1350 mA." Answer: yes, from a source that advertises it; that is a heat question, not a source-overload question, and belongs to the thermal requirement.
