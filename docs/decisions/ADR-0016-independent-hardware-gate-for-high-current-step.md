# ADR-0016: Independent hardware gate for the high current step

- **Status:** Accepted (by the owner, Ben Spoor, 2026-11-04, on explicit instruction in the session; option B). Replaces the sensing decision of ADR-0009 (option A) and the hardware-backstop wording of ADR-0010. Accepted before its own goldfish review; the review RV-008 followed and its amendments are listed below.
- **Date:** 2026-11-04
- **Deciders / reviewers:** Ben Spoor (owner); based on review RV-006 findings S1, S2 and S7; this ADR itself was accepted before its own review; a goldfish review of ADR-0015 and ADR-0016 is recorded as RV-008
- **Related:** SYS-020, HW-003, HW-010, RISK-003, RISK-024, RISK-025, RISK-029, RISK-042, RISK-044, RISK-045, DEV-001, ADR-0004, ADR-0009, ADR-0010, ADR-0015; RV-006, RV-008, RV-010; `docs/verification/reports/spike-7-5-power-budget-paper.md`

## Context and problem
ADR-0010 puts a current-limited load switch in the VBUS path: 500 mA at power-up, raised in steps by a firmware GPIO. Review RV-006 (finding S1) found that this does **not** protect a source that advertises only 500 mA if the firmware misreads the CC voltage and then raises the limit itself, because the same firmware decides both. It protects against a stopped, reset or never-started firmware and against a short circuit. The owner asked for a hardware limit because of this concern (SYS-020, owner decision 2026-11-04), so the gap is exactly the case the owner cares about. Finding S2 adds that a hung firmware with the GPIO high keeps the high step.
The wanted property: **the high step can switch on only if a part that is independent of the firmware has also seen that the source advertises at least 1.5 A.**
Related finding S7: the ADC margin of ADR-0009 option A is thin and its spike criterion cannot be met at worst-case band edges (reviewer recomputation, not repeated by me).

What this does and does not solve: it removes the firmware from the decision to raise the limit. A hung firmware at the high step on a source that really advertises 1.5 A draws the advertised current (up to the limit band of ADR-0010, which can exceed it: RISK-027); the remaining risk is heat in the closed housing at 1350 mA (RISK-005, RV-004 T2), which is a thermal question and not solved here.

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
**Owner decision 2026-11-04: Accepted, option B.** HW-003 and HW-010 (Draft) are drafted to match; the checks of item 3 are still required before a part is fixed. The decision: **B, a CC detection IC with its output ANDed with the firmware GPIO.** The owner may instead accept option A (and RISK-025 stays open) or choose C or D.
1. **Gate:** every step above the 500 mA step (the middle step of ADR-0010, if kept, and the top step) switches on only if the IC reports at least 1.5 A and the firmware GPIO for that step is high. Both must agree. The firmware can always hold or drop to a lower step.
2. **Firmware reads the IC outputs** (two GPIO pins), not the ADC. The ADC read of ADR-0009 option A is dropped, so the 90 mV gap and the +-35 mV ADC error no longer decide the limit. A firmware misread can no longer raise the limit above the hardware reading; a wrong IC reading is the remaining failure and is covered by the vendor specification and test.
3. **Part:** the part and its second source are decided after the checks below; no part number is fixed here. Required checks before a part is fixed and before HW-010 can be Approved: the CC pin ratings and VCONN behaviour, the temperature range of the actual part (the conflict of E14 and E15), the JLCPCB class and setup fee, and behaviour with a PD-capable charger.
4. **Defaults when the IC output is undefined** (IC failed, unpowered): the pull-ups read "default", so the high step stays off (500 mA).
5. **Hung firmware (finding S2):** with B the high step cannot be on unless the source advertises it; the remaining effect is heat at the advertised current, handled by the thermal requirement (RV-004 T2). A heartbeat gate (option D) is not added now; revisit if the thermal analysis shows the high step is unsafe for a hung firmware.

## Consequences
- Positive: RISK-025 (firmware misreads CC) gets an independent path; the thin ADC margin disappears from the decision; the hardware limit claim of ADR-0010 becomes true for the owner's main case.
- **Negative / trade-offs accepted:** one more IC and one gate (about USD 0.6 at 1 piece, my estimate from the snippet price); an extended-part fee is likely and not looked up; single-source risk (RISK-030 style); the CC pins and their ESD and VCONN handling now depend on one datasheet; the spike 7.5 ADC measurement is replaced by an IC test.
- New risks (to add after the owner decides): IC misclassifies a charger (wrong band) with no firmware second opinion; IC temperature range; IC out of stock.
- Requirements created or changed: HW-003 (CC sensing by IC, ESD and clamp on CC), HW-010 (gate), SYS-020 (no change), a new SW requirement (read the IC outputs, hold or lower the step, brown-out back-off), ADR-0009 (superseded by this ADR for sensing), ADR-0010 (select line is ANDed), RISK-025 (residual text).

## Amendments after RV-008 (made before the pull request was merged; the owner confirms)
The goldfish review RV-008 found points that this text did not state. They clarify the decision and do not change option B.
- **"Independent" means independent of firmware faults only.** The gate and the firmware read the same IC output. A fault in the IC or its output (misclassification, latch-up, output shorted low) makes both agree on "high"; then only the firmware stands in the way, as in option A. A diverse second opinion (the ADC kept, or a comparator, options C and D) would cover that, and is not part of this decision. Accepted risk: RISK-042.
- **Start-up hold-off (added after the TUSB321 datasheet read, 2026-11-04):** the datasheet does not state the output level before the first CC debounce (133 ms). The gate therefore has a hold-off of at least [200] ms after the IC supply is valid (HW-010); the circuit (for example an RC delay on the rising edge of the "1.5 A" signal) is a design task and is simulated before HW-010 is Approved. Owner to confirm.
- **Part chosen (owner, 2026-11-04): TI TUSB321**, with the NXP PTN5150A as the fallback if the IC ambient temperature in the closed housing exceeds 70 C on the prototype (TC-210 records it; a thermal figure is not available yet). Basis and gaps: `docs/verification/reports/cc-ic-datasheet-evidence.md`. The other checks of item 3 stay open: stock and price, assembly of the 1.6 mm package, the PTN5150A datasheet, VCONN pin handling on a sink-only board.
- **Single faults not covered:** the AND output or a series MOSFET stuck high (the same single fault as RISK-029); the IC misclassifying a charger; a non-compliant cable whose Rp advertises more than the port supplies (RV-006 S3); the thin band edges (the IC thresholds fill the whole 90 mV gap, 0.61 to 0.70 V, so protection depends on the IC meeting the Type-C bands, which was not read from the specification).
- **Truth table.** Every open or short on the gate path must resolve to "off": the gate input has a pull-down (so a floating GPIO or an unpowered gate reads "off", independent of the ESP32-C3 reset state, ADR-0010 E24); the active-low IC output is inverted to an enable with a pull-up of the IC output so that an unpowered or failed IC reads "default"; an open pull-up must not read as "high".
- **Tests.** The fault-injection list (IC unpowered, output shorted high and low, gate input open, MOSFET shorted, GPIO stuck high), a PD-capable charger, an e-marked cable and band-edge Rp (resistor-simulated sources at 0.61 V and 0.70 V) move into the acceptance criteria of HW-010 and HW-003.
- **Cost.** The added cost is a range of about USD 0.6 to 1.0 at 1 piece (the IC about USD 0.51, snippet, plus a gate and passives, my estimate; an extended-part fee is likely and not looked up).
- **Open, not closed by this ADR:** the hung-firmware case (S2) is deferred to a thermal requirement and a watchdog requirement that do not exist yet; the brown-out back-off and the PD chatter need a software requirement; a temperature range of 0 to 70 C in a closed housing is a blocking check.

## Verification and revisit
- Bench test with chargers that advertise default, 1.5 A and 3 A, an e-marked cable, a PD-capable charger and a non-compliant cable: the high step must stay off unless the IC reports at least 1.5 A and the GPIO is high; firmware stopped, GPIO high and source advertising default must give 500 mA (TC-203, TC-210).
- Fault injection: IC unpowered, output shorted high, output shorted low, GPIO stuck high.
- Revisit when: the part checks fail, a better part is found, the owner decides to accept the gap, or the thermal analysis shows that a hung firmware at the high step is unsafe (then option D).

## Critical review notes
Strongest objection: "A CC IC is the same CC reading with a different part; if it misclassifies a charger, the limit is wrong and no firmware second opinion exists."
Answer: accepted. The gain is independence from firmware faults and a vendor-specified threshold, not a better reading of a bad source. A firmware ADC read could be kept as a second opinion (option C style) at the cost of more parts; the owner decides whether the second opinion is worth it.
Second objection: "A hung firmware at the high step still draws 1350 mA." Answer: yes, from a source that advertises it; that is a heat question, not a source-overload question, and belongs to the thermal requirement.

## Amendment 2 (Proposed, 2026-11-06): ILIM select switch, ILIM resistors and hold-off capacitor set

- **Status of this amendment:** Proposed. Not Accepted and not Approved; only the owner (Ben Spoor) decides. The sections above are unchanged, including the Accepted status of the decision (option B).
- **Origin:** owner decisions of 2026-11-05 (`docs/verification/reports/owner-decisions-2026-11-05-b.md`, decisions 2 to 4), which asked for a part change on a safety-relevant limit to be recorded as an ADR-0016 amendment. This amendment adds no new numbers: every figure is taken from `docs/verification/reports/analysis-ilim-switch-replacement.md` (section and addendum A), the owner-decisions record, HW-010 (Proposed amendment), DEV-001 and RISK-045.
- **Related:** SYS-020, HW-010, SW-005, SW-009, RISK-027, RISK-045, DEV-001, TC-210, ADR-0010.
- **Scope:** the gate decision of ADR-0016 (option B, CC IC and AND) is not touched. This amendment covers what sets the three current limits that the gate selects: the two analog switches that replaced the 2N7002 transistors Q2 and Q3 on the ILIM node of the TPS2553, the three ILIM resistors, and the capacitor set of the hold-off timer.

### Context
The 2N7002 transistors have a stated off leakage ceiling of 1 uA (comparison row of the analysis, section 5). The leakage budget for the HW-010 limits is 118 nA per off switch at 1.0 V (94 nA at 0.8 V, 142 nA at 1.2 V; the 1.0 V ILIM node is an ASSUMPTION, not found in the SLVS841G text read). With 1 uA the step 1 maximum is 670.9 mA against the 623 mA of HW-010 (margin -47.9 mA) and the step 3 maximum is 1592.3 mA against 1577 mA (-15.3 mA). So the transistor must change. No MOSFET with leakage stated at low drain voltage was found (the BSS138N states 0.1 uA at 60 V and 25 degC only).

Not known (owner and bench decide): the ILIM pin voltage, the 3V3 ramp (regulator not chosen), stock and price at LCSC and JLCPCB of every part named here, the JLCPCB Extended-part fee, the behaviour of the TMUX1101 signal pin above VDD + 0.5 V.

### Decision criteria
Weights are my judgement, derived from the analysis report (leakage budget, section 1; margins, section 5; open item, section 4 and addendum).
| Criterion | Weight (1-5) | Source |
|-----------|--------------|--------|
| Off leakage stated near 1 V and to 85 degC (evidence that the 118 nA budget holds) | 5 | analysis section 1, 3, 4; HW-010 limits |
| Retention of the HW-010 step margins with 3V3 on | 5 | analysis section 5; HW-010, SYS-020 |
| Behaviour with 3V3 off (ILIM node about 1 V, 3V3 below about 0.5 V) | 4 | analysis section 4 and A.3 to A.5; RISK-045 |
| Drive margin from the 74LVC gate (2.9 V loaded, 2.5 V ideal) | 3 | analysis section 4 |
| Availability, class and fee (stock not verified) | 3 | analysis section 7; RISK-030 |
| Package and assembly | 2 | analysis section 3 |

### Alternatives considered
**A. TMUX1101DCKR (LCSC C2673506), fallback TS5A3166DBVR (owner choice).** Off leakage max 0.05 nA at 25 degC and 0.2 nA at -40 to 85 degC, at VDD 3.3 V with 3 V / 1 V across the switch (SCDS410D, section 6.6, p. 6); about 590 times below the budget. VIH min 1.35 V, so it works from a 2.5 V gate; SEL is fail-safe; Rds max 9.5 ohm at 85 degC is irrelevant against the 56 kohm branch. Strongest case: the only candidate whose leakage is stated near 1 V over temperature and that leaves the margins unchanged (table row "TMUX1101": step 1 504.2 to 616.6 mA, step 3 1381.2 to 1566.7 mA). Cons: **no behaviour is stated for a signal above VDD + 0.5 V** and that case occurs at every power-up (open condition below); SC70-5; JLCPCB Extended (class inferred from the twin TMUX1102DCKR, not seen for C2673506); stock not verified.

**B. TS5A3166DBVR (C353035) as the primary part.** Off leakage max 2 nA at 25 degC and 20 nA at -40 to 85 degC (SCDS186E, p. 6), 5.9 times below the budget; powered-off leakage is stated (1 uA at 25 degC, 5 uA full range). Strongest case: the 3V3-off behaviour is specified, so no deviation of an absolute maximum is needed on paper; SOT-23-5; JLCPCB page fetched, Extended. Cons: with 20 nA the step 1 maximum is 617.7 mA (margin 5.3 mA, 1.1 mA less than option A); VIH min 2.0 V leaves 0.9 V from a 2.9 V gate and it needs its 2.5 V supply table below that; if the TPS2553 is enabled with 3V3 absent, 1 uA gives step 1 maximum 670.9 mA and 5 uA gives 885.4 mA, which breaks the HW-010 numbers (margin -47.9 and -262.4 mA). The window exists by architecture (addendum A.5), so B replaces "not specified" by "stated and out of limit" and does not remove it.

**C. A MOSFET with a bench leakage measurement (BSS138N or similar).** Switch off at any rail with the gate low, so the 3V3-off case is not an issue. Strongest case: no abs. max. question, a basic-class part may exist (class of C94638 not seen). Cons: no part states leakage at 1 V; BSS138N leakage is a 60 V, 25 degC ceiling (0.1 uA); with an assumed 100 nA the margin is 1.0 mA at the step 1 maximum on an unverified number; Rds is not stated below 4.5 V; the search was not exhaustive (analysis section 7). Stays open only with a bench leakage measurement at 70 degC.

**D. Do nothing / defer: keep the 2N7002.** Same as A with respect to the window, but the stated 1 uA ceiling breaks the step 1 and step 3 maximum (rows above). Strongest case: no change, a known part. It cannot meet HW-010 on paper; it is listed because the owner may keep it for a first bench build and measure its real leakage.

### Comparison
Scores 0 to 5, my judgement. Evidence: analysis report sections 3 to 5 and addendum A (desk research of datasheets; nothing measured). Max 110.
| Criterion (weight) | A TMUX1101 | B TS5A3166 | C MOSFET | D 2N7002 |
|--------------------|------------|------------|----------|----------|
| Leakage stated near 1 V, to 85 degC (5) | 5 | 4 | 1 | 1 |
| Step margins with 3V3 on (5) | 5 | 4 | 2 | 0 |
| Behaviour with 3V3 off (4) | 1 | 3 | 5 | 5 |
| Drive from 2.9 V / 2.5 V gate (3) | 5 | 3 | 2 | 3 (not re-assessed) |
| Availability, class, fee (3) | 2 | 2 | 2 | 3 (not checked) |
| Package and assembly (2) | 3 | 4 | 5 | 5 |
| **Weighted sum (max 110)** | **81** | 75 | 57 | 53 |

A leads B by 6 points, which is within my scoring error. Sensitivity: if the weight of "behaviour with 3V3 off" rises from 4 to 7 the two tie, and above that B leads. The table therefore depends on how the 3V3-off condition is judged. The recommendation is conditional (see Decision).

### Decision (proposed)
**Proposed: option A, TMUX1101DCKR for Q2 and Q3, conditional on the bench check TC-210 point (d); fallback TS5A3166DBVR.** The owner has chosen this on 2026-11-05; this text records it for acceptance.
1. **Switch:** TMUX1101DCKR (C2673506), supply pin on 3V3 with 0.1 uF, active-high control driven by the 74LVC gate, a 100 kohm pull-down on each control pin (an open control reads "off", step 1). These circuit points are ASSUMPTIONS of the analysis (schematic not re-read) and the readback divider is to be checked against the pull-down.
2. **ILIM resistors,** 0.1 % 0603 thin film: step 1 47.0 kohm; step 2 56.2 kohm; step 3 27.4 kohm plus 301 ohm in series (HW-010 Proposed revision, table of current values). Calculated limits (owner-decisions record, section 2; Rds 0 to 9.5 ohm, 0.2 nA, 1.0 V assumed): step 1 504.2 to 616.6 mA (maximum 623, margin 6.4 mA); step 2 934.9 to 1091.7 mA (proposed window 850 to 1150 mA); step 3 1381.2 to 1566.6 mA (window 1366 to 1577, margins 15.2 and 10.4 mA); Q2 and Q3 both on 1817.4 to 2019.5 mA, excluded by the exclusive gate. Alternatives for the resistors: (i) the earlier set 47.0 / 56.9 / 27.7 kohm gives step 2 929.6 to 1085.9 mA and step 3 1381.2 to 1566.7 mA with the TMUX1101, so it also meets the numbers; the records read do not state why the owner changed the step 2 value to 56.2 kohm or split the step 3 value (the sum 27.701 kohm gives the same limits as 27.7 kohm; stock of E192 values is not checked, which may be the reason, the owner confirms); (ii) 27.4 kohm alone gives a step 3 maximum of 1576.8 mA, margin 0.2 mA, rejected for that reason. The margins of 6.4, 10.4 and 15.2 mA are small against resistor temperature coefficient, ageing and layout leakage, which are not modelled.
3. **Hold-off capacitor C1:** six 100 nF C0G 5 % 50 V 1206 capacitors in parallel, Murata GRM31C5C1H104JA01L (LCSC C97946), 600 nF (owner choice of 2026-11-06; it replaces 220 + 220 + 100 + 68 nF, 608 nF, which gave 205.9 to 560.6 ms and was also purchasable). Calculated window 203.2 to 553.2 ms, a margin of only 3.2 ms to the lower edge (script `holdoff_cap.py`, run 2026-11-06; TPS3840 constants k_min 357.6 kohm, k_max 875.6 kohm; 202.5 to 554.8 ms with the 0.6 % allowance of `analysis-n4-holdoff-capacitor.md`), inside the [200] to [600] ms of ADR-0016 and HW-010; the margin to the typical CC debounce (133 ms) is 72.9 ms, and the maximum debounce is not found. Alternatives from the N4 report: 3 x 220 nF (660 nF) gives 222.8 to 610.3 ms and misses the 600 ms limit; 220 + 220 + 150 nF (590 nF) gives 199.2 ms and misses 200 ms; 220 + 220 + 150 + 33 nF (623 nF) gives 210.3 to 576.0 ms and also fits (the earlier example, replaced by the owner set; the report read does not state why). A single 620 nF C0G part was not found. Ageing, DC bias and leakage of C0G are taken as 0 (not checked); the 100 nF part had 96,458 pieces in stock on 2026-11-06 (Extended).
4. **Open condition, the 3V3-off window (not closed by design).** The TPS2553 is enabled from VBUS_IC and 3V3 comes from its output through the regulator, so at every power-up the ILIM node (about 1 V, assumed) can exceed the TMUX1101 absolute maximum VDD + 0.5 V while 3V3 is below about 0.5 V. The hold-off does not hold EN low (addendum A.2 finding 1, which corrects the earlier assumption), and an enable on 3V3 would be circular. The datasheet states no leakage, clamp current or switch state in that case; first-order estimate up to about 7 uA, taken from the ILIM node (assumed 0.6 V clamp), against 21 uA of step 1, so the effect on the limit is unknown, not zero. Recorded as DEV-001 (Proposed, prototype only) and RISK-045 (Open, initial risk 9). Compensating measures: the switch is off in the window (pull-down, fail-safe control), the firmware starts at the lowest step, the window is short.
5. **Bench check, TC-210 point (d):** with a scope, VBUS_IC, +5V, 3V3 and the ILIM node (one high-impedance probe) at plug-in and at VBUS dropout, for each build, with repeated plug-ins: time with 3V3 below 0.5 V, peak of the ILIM node minus 3V3, limit error in that window. Other TC-210 points: (a) hold-off measured against 203.2 to 553.2 ms and against the CC IC debounce with at least [20] ms margin; (b) each step measured against the numbers in item 2, also at 70 degC if possible. Nothing of this has been run; the procedure stays "TBD" until approval.
6. **Branch on the bench result:** if the effect in the window is acceptable, DEV-001 closes or becomes a permanent deviation with the evidence; if not, use TS5A3166DBVR and review its 1 to 5 uA powered-off leakage, or add a series resistor or clamp once the bench numbers exist (not analysed), or withdraw to option C with a leakage measurement.

### Update 2026-11-06 (owner decisions of the working session; nothing Accepted or Approved)
- Switch: option A (TMUX1101DCKR) is kept with the bench check TC-210 (d). Live stock on 2026-11-06: C2673506 has 2,258 pieces (Extended). Stock of the fallback TS5A3166DBVR (C353035) is not checked.
- Resistors: the owner confirmed the E96 set 47.0 / 56.2 / 27.4 kohm + 301 ohm, 0.1 % 0603, and not the E192 set. Reason found: 56.9 kohm and 27.7 kohm at 0.1 % have no JLCPCB stock in 0603 (27.7 kohm exists in 0805 and 0402 only). Parts, all in stock and Extended on 2026-11-06: Yageo RT0603BRD0747KL (C326725, 17,621), Yageo RT0603BRD0756K2L (C705784, 7,107), Yageo RT0603BRD0727K4L (C861274, 14,937), Panasonic ERA-3AEB3010V (C2074494, 5,222) for the 301 ohm. A commit of the branch `docs/adr-0016-tmux1101` (e296fa3) that reverted to the E192 set is superseded by this decision and is not part of this branch.
- Capacitors: six 100 nF, as item 3.
- Option C: `hw/sim/analysis-ilim-switch-leakage.md` bounds the BSS138 and AO3400A leakage from their datasheets (BSS138: 100 nA at 30 V, 0.5 uA at 50 V; AO3400A: 1 uA at 30 V). The BSS138 fits the 118 nA budget only if the ILIM node is about 0.85 V or more and the part stays near 25 degC; no datasheet states the leakage at the ILIM voltage.
- Evidence: `docs/journal/2026-11-06-decisions-and-live-stock.md`. Not run: no bench, no SPICE.

### Update 2026-11-06 (RV-010 finding 1): truth table over the supply states, status Proposed
The text above says an unpowered or failed IC "reads default", so the gate stays off. That overstates the fail-safe. With VBUS gone and 3V3 present the open-drain IC outputs are low and the 3V3 inverter turns that into "1.5 A seen". The table below states what holds each enable low. It follows the spike netlist (`hw/kicad/spike-gate/src/gen_gate.py`: a 3-input AND per step of select line, CC OK and hold-off done; step 2 also forced off by step 3). It is a desk statement and is verified against the schematic and the bench (TC-210) before approval.

| State | CC OK signal | Hold-off (HOLD_OK) | Select GPIO | Enable | What holds it off |
|---|---|---|---|---|---|
| VBUS 0 V, 3V3 present | reads high (IC unpowered, outputs low, inverted) | low (supervisor off) | any | off | hold-off only |
| VBUS_IC below the supervisor release (4.0 V part, release 4.115 to 4.285 V) | undefined | low | any | off | hold-off only |
| VBUS_IC between release and 4.5 V (IC below its minimum supply) | undefined, not stated by the datasheet | runs, then releases after 203 to 553 ms | high | **not guaranteed off** | nothing; open point M4, bench sag test |
| VBUS_IC 4.5 V or more, inside the hold-off | undefined until the first debounce (133 ms typical) | low | any | off | hold-off only |
| VBUS_IC 4.5 V or more, after the hold-off, default-current source | "not 1.5 A" | high | high | off | the IC reading |
| same, source advertises 1.5 A | "1.5 A" | high | low | off | the firmware |
| same, source advertises 1.5 A | "1.5 A" | high | high | on | (intended) |
| 3V3 absent, VBUS present | any | any | undefined | off | pull-down on the gate input; not yet verified for the unpowered AND gate |
| IC output stuck or misclassifying | wrong | high | high | on | not covered (RISK-042) |
| AND output stuck high, or select switch shorted | any | any | any | on | not covered (RISK-029) |

Consequences for the text above: item 4 ("the pull-ups read default") holds only while the IC is powered. For the first four rows the hold-off is the single element that keeps the step off, so its failure modes (supervisor output stuck high, delay capacitor short) are fault-injection rows in TC-210, and the firmware treats the CC OK inputs as valid only while HOLD_OK_RB is high (SW-009 Proposed). The row between release and 4.5 V is the weakest and has no design answer yet.

### Update 2026-11-07 (owner decision 3): the ILIM switches are supplied from VBUS_IC, status Proposed
The owner decided on 2026-11-07 to remove the TMUX1101 over-voltage of the previous update by design, not to accept it with DEV-001 (this was not the assistant's recommendation; the recommendation was to accept it with a bench check). Analysis: `docs/verification/reports/analysis-tmux1101-supply-from-vbus.md`. Decision: the supply pins (VDD) of U14 and U15 move from 3V3 to VBUS_IC with a 100 nF capacitor. The ILIM node exists only while VBUS_IC is above the TPS2553 UVLO (2.35 to 2.45 V), so the switch supply is then at least 2.35 V and the signal limit VDD + 0.5 V is at least 2.85 V against an ILIM node of about 1 V (margin about 1.85 V). Alternatives rejected: a series resistor or clamp (the clamp structure is not stated, so the limit cannot be computed), the TS5A3166 fallback (its stated powered-off leakage of 1 to 5 uA breaks the step margins in the same window), and keeping the part on 3V3 with DEV-001. Datasheet numbers used: VDD 1.08 to 5.5 V, off leakage 0.3 nA to 85 degC at VDD = 5 V, SEL VIH 1.49 V minimum and fail-safe up to 5.5 V. Not shown: the TVS clamp voltage of VBUS_IC against the 6 V rating of VDD; the VBUS dropout order; the 1 V ILIM voltage (the margin holds up to about 2 V). DEV-001 is withdrawn when the owner approves this change and TC-210 (d) shows no exceedance; RISK-045 stays open until then. The spike schematic still has the supply on 3V3 and is not changed (HW-010 not Approved).

### Consequences
- Positive: the leakage of the select switch leaves the margins unchanged (0.2 nA against 118 nA); the 2N7002 problem of HW-010 is removed on paper; the fallback is a drop-in on one package change.
- **Negative / trade-offs accepted:** a rated maximum is exceeded at every power-up on a safety-relevant limit with no datasheet support, accepted for the prototype only (DEV-001); two Extended parts or more, per-type fee not checked, stock not verified (earlier undated snippets showed TMUX1101DCKR out of stock and TS5A3166 at 0 stock); small step margins (6.4 to 15.2 mA) that rest on 0.1 % resistors and unmodelled temperature effects; more parts in the hold-off (six capacitors) and a minimum hold-off margin of 3.2 ms.
- New risks: RISK-045 (added, Open). Existing: RISK-027 (limit band), RISK-030 (availability), RISK-044 and RISK-042 (gate).
- Requirements and records changed or to be changed on approval: HW-010 (Proposed amendment (a) to (e)), SW-005 and SW-009 (Proposed amendments, unchanged by this text), TC-210 (outline, point (d)), DEV-001, RISK-045. No hardware file is changed (CLAUDE.md rules 1 and 12).

### Verification and revisit
Bench TC-210 points (a), (b), (d) as above; leakage at 70 degC if the setup allows. Revisit when: the TC-210 (d) record shows a limit error or damage; stock or fee make the part unusable; the real ILIM voltage or the regulator changes the window; the maximum CC debounce is 200 ms or more (then the hold-off minimum needs a new decision).

### Critical review notes
Strongest objection: "The primary part is chosen although the datasheet gives no behaviour for the case that occurs at every power-up, and the fallback has the better paper behaviour; a rated maximum on a safety limit is exceeded by design."
Answer: partly accepted. The TMUX1101 is the only part with stated leakage near 1 V and unchanged margins, and the fallback does not remove the window (its stated 5 uA breaks the step 1 and step 3 maxima if the TPS2553 runs with 3V3 absent), so the choice is between an unknown effect and a known out-of-limit one. The scores do not separate A from B (6 points, tie at weight 7 for the 3V3-off criterion). The decision is therefore conditional: prototype only, DEV-001 and the TC-210 (d) record decide, and the fallback stays ready. If the owner weighs a rating exceedance as unacceptable without evidence, option B is the consistent choice.
Second objection: "The 118 nA budget and every margin rest on an assumed 1.0 V ILIM node." Answer: yes; the SLVS841G text read does not state it, and TC-210 point (d) measures it. Third: "Stock and fees are unchecked." Answer: yes; unchecked, stated here, and a reason to revisit.
Not run: no SPICE, no bench, no firmware; scores and numbers are desk results as reported in the cited analyses and were not re-checked against the datasheets by this amendment.
