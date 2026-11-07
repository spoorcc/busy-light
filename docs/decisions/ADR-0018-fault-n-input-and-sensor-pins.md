# ADR-0018: FAULT_N input of the current limiter and the pins of the orientation sensor

- **Status:** Accepted (by the owner, Ben Spoor, 2026-11-07, in the working session; option E, the AND gate, proposed by the owner's question and written up by the assistant; recorded by the assistant). Open conditions: the AND gate part and its 5 V input tolerance are not read; the SW-009, HW-010 and TC text amendments are Proposed until the owner approves them.
- **Date:** 2026-11-07
- **Deciders / reviewers:** Ben Spoor (owner); goldfish review RV-011 (findings 1 and 15) raised the open points
- **Related:** SYS-020, SYS-047, HW-010, HW-011, SW-009, ADR-0010, ADR-0016, RV-010, RV-011, RISK-029

## Context and problem
All usable GPIOs of the ESP32-C3-MINI-1 are used (HW-010, RV-010 finding 21). Deleting CC_OK_3A freed GPIO1. The orientation sensor of HW-011 (Draft, priority Should, no part chosen) needs two I2C pins, so a second pin must come from somewhere. The candidate is GPIO4, which reads FAULT_N, the fault output of the TPS2553 current limiter. ADR-0010 item 3 says: "the FAULT output goes to a processor input (and is logged). The firmware answers a fault by dropping to the lowest step." SW-009 and HW-010 criterion 8 mention FAULT_N.

Not known: whether the sensor part needs an interrupt pin (no part is chosen); how often a limiter fault happens in the field; whether the loss of the report matters to the user (not assessed).

## Decision
**Owner decision (2026-11-07): E**, the AND gate. Earlier the owner chose A (remove FAULT_N); the assistant recommended B (keep it) because the weighted table favours B (65 against 42 for A). After the owner asked whether the fault could be combined with another input, the assistant wrote up E: it scores 60, five points under B, which is inside the error of the scores, and it removes the main drawback of A (the fault response is kept) while still freeing GPIO1 and GPIO4 for the sensor. The assistant agrees with E.
Compensating measures and conditions: (1) FAULT_N also goes to a test point, read in TC-210; (2) the gate part and its 5 V input tolerance are read and entered in HW-012 before the schematic changes; (3) the hold-off and the limiter fault stay distinguishable on the bench by the test point; (4) the firmware logs the count of GATE_OK_RB falls and the EN readbacks at each fall, so a field fault can be inferred later.

## Consequences
- Positive: the sensor gets pins on the first board; the firmware still drops to the lowest step on a limiter fault (ADR-0010 item 3 stays true); no new part.
- **Negative / trade-offs accepted:** the firmware cannot tell the cause of a GATE_OK_RB fall; a flapping limiter fault keeps restarting the SW-005 count; the sensor part and its I2C addresses are still unchosen, so the pins may be wrong.
- New risks (to add to the risk register): a field limiter fault is only inferred, not seen; the AND gate's behaviour with 3V3 absent or with a floating FAULT_N is not read.
- Requirements created or changed (Proposed): SW-009 statement (HOLD_OK_RB becomes GATE_OK_RB = gate ok and no limiter fault; the FAULT_N sentence and TC-109 case (d) are replaced), HW-010 (buffer replaced by an AND gate, FAULT_N pull-up, criterion 8 and the fault-injection table), plan 07 pin map (GPIO4 reserved for the sensor, GPIO6 is GATE_OK_RB).

## Verification and revisit
Bench: TC-210 forces FAULT_N low with the gate open and checks that GATE_OK_RB falls and the firmware sheds within [X] ms; the FAULT_N test point is read. Revisit if the sensor part needs an interrupt line, if field data show limiter faults, or if the board is respun.

## Critical review notes
Strongest objection: "E merges two signals, so a field limiter fault cannot be told from a normal hold-off, and a flapping fault restarts the stable-reading count forever." Answer: the response is the same by design (lowest step), a restarting count is the safe direction, and the bench test point and the logged counts give the cause when needed. The earlier objection against option A (it removed a safety input for a Should feature) is the reason A was dropped.
