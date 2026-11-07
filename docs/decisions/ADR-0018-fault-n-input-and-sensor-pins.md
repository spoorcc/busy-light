# ADR-0018: FAULT_N input of the current limiter and the pins of the orientation sensor

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-07
- **Deciders / reviewers:** Ben Spoor (owner); goldfish review RV-011 (findings 1 and 15) raised the open points
- **Related:** SYS-020, SYS-047, HW-010, HW-011, SW-009, ADR-0010, ADR-0016, RV-010, RV-011, RISK-029

## Context and problem
All usable GPIOs of the ESP32-C3-MINI-1 are used (HW-010, RV-010 finding 21). Deleting CC_OK_3A freed GPIO1. The orientation sensor of HW-011 (Draft, priority Should, no part chosen) needs two I2C pins, so a second pin must come from somewhere. The candidate is GPIO4, which reads FAULT_N, the fault output of the TPS2553 current limiter. ADR-0010 item 3 says: "the FAULT output goes to a processor input (and is logged). The firmware answers a fault by dropping to the lowest step." SW-009 and HW-010 criterion 8 mention FAULT_N.

Not known: whether the sensor part needs an interrupt pin (no part is chosen); how often a limiter fault happens in the field; whether the loss of the report matters to the user (not assessed).

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Fault response stays: the firmware sees an overload or an over-temperature of the limiter | 5 | SYS-020, ADR-0010 item 3 |
| Orientation sensor gets its pins on this board | 2 | SYS-047, HW-011 (Should) |
| Parts, cost and assembly (no new part) | 3 | SYS-021, SYS-022 |
| Testability of the fault path (fault injection in TC-210) | 3 | RV-010 finding 27 |
| Reversibility (a later respin changes it) | 2 | project |

## Alternatives considered
### A. Remove the FAULT_N input; GPIO1 and GPIO4 carry the sensor
The limiter keeps limiting current by itself (constant current, auto retry, `analysis` E5 in ADR-0010); the firmware no longer sees the flag. Strongest case: the hardware already protects the 5 V rail and the source without the firmware; the flag was only an input to log and to lower the step; the sensor feature (clock mode, level mode) gets its pins with no new part.
Cons: the firmware loses an overload report; SW-009, HW-010 criterion 8, TC-109 (d) and ADR-0010 item 3 change; a sustained overload is no longer visible to the user or in logs.
### B. Keep FAULT_N on GPIO4; defer the sensor to a later board
Strongest case: no safety input is lost for a feature that is only a Should and has no part; GPIO1 stays free as a spare. Cons: the board has no sensor, so SYS-047 is not met by the first prototype.
### C. Keep FAULT_N; add an I/O expander for the sensor and spares
Strongest case: both work. Cons: one more part with its own supply, stock check and test; the expander could not carry the FAULT_N interrupt without an interrupt pin.
### D. Do nothing / defer
Leave the spike as it is (FAULT_N on GPIO4, GPIO1 free, no sensor pins). The sensor then has no pins; this is B without the decision, so it scores the same as B.

## Comparison
Scores 0 (poor) to 5 (good), my judgement (maximum 75).

| Criterion (weight) | A | B | C | D |
|---|---|---|---|---|
| Fault response stays (5) | 1 | 5 | 5 | 5 |
| Sensor gets pins (2) | 5 | 0 | 5 | 0 |
| Parts, cost, assembly (3) | 5 | 5 | 2 | 5 |
| Testability of the fault path (3) | 2 | 5 | 4 | 5 |
| Reversibility (2) | 3 | 5 | 2 | 5 |
| **Weighted sum** | 42 | 65 | 57 | 65 |

## Decision
**Recommendation of the assistant: B.** The weighted sum favours B because the fault response is the only safety-relevant item and the sensor is a Should with no part.
**Owner decision (2026-11-07, in the working session): A.** The owner chose to remove the FAULT_N input so that the sensor gets GPIO1 and GPIO4. The assistant recorded this and states the disagreement with the table openly: the table does not support A on safety grounds, so A is accepted by the owner as a trade-off with the compensating measures below. Status stays Proposed until the owner accepts the text.
Compensating measures: (1) the FAULT_N net goes to a test point and is read in TC-210 at the bench; (2) the hardware gate and the limiter limit the current without the firmware (ADR-0016, ADR-0010 E5); (3) the hung-firmware and thermal cases keep SW-010 and HW-013; (4) the firmware infers an overload only from HOLD_OK_RB and the brown-out counter of SW-007.

## Consequences
- Positive: the sensor gets pins on the first board; one GPIO less to read.
- **Negative / trade-offs accepted:** the processor no longer sees a limiter fault; no log entry and no LED indication of a limiter overload; the answer "drop to the lowest step on a fault" of ADR-0010 item 3 is lost; the sensor part and its I2C addresses are still unchosen, so the pins may be wrong.
- New risks (to add to the risk register): a persistent limiter overload is invisible to the firmware; the sensor needs an interrupt pin that does not exist.
- Requirements created or changed (Proposed): SW-009 statement (remove the FAULT_N sentence and its test), HW-010 criterion 8 and the fault-injection table, TC-109 case (d), ADR-0010 item 3 (this ADR supersedes that item for FAULT_N), plan 07 pin map.

## Verification and revisit
Bench: TC-210 reads the FAULT_N test point in the fault-injection table. Revisit if the sensor part needs an interrupt line, if field data show limiter faults, or if the board is respun.

## Critical review notes
Strongest objection: "A removes a safety input to make room for a feature the requirement list marks Should." Answer: correct, and the weighted table says so. The owner accepts it because the limiter limits current by itself and the first prototype is a bench unit; the decision is cheap to reverse on the next board.
