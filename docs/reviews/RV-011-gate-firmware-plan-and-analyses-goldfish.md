# Review Record RV-011

- **Subject:** plan 07 (gate firmware), draft procedures TC-105, TC-106, TC-107, TC-109, TC-110, TC-210, TC-213, the analyses of the supply-pin surge, the regulator heat and the CC-pin protection, the TVS1 / regulator shortlist, and the Proposed amendments of 2026-11-07 (commit 7c42081 and later)
- **Type:** Design
- **Date:** 2026-11-07  **Reviewer(s):** four fresh goldfish subagents (comprehension, failure modes and safety, testability, integration)  **Independent?** yes (stateless, only file paths given)

## Comprehension check
The goldfish restated plan 07 correctly (host-only logic slice, one `gate` module behind a hardware abstraction, hardware gate as the independent check). Gaps it listed: no HAL function list, undefined LED-layer call, SW-006 not mapped, no edge-latch test, retained-flag set and clear rules unclear, step numbers undefined. Fixed in plan 07 (commit 92276d2) except the flag rule, now an open owner decision.

## Findings (merged; reviewer numbers in brackets: F = failure modes, T = testability, I = integration)
| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| 1 | High | FAULT_N removal (I2, F7): ADR-0010 item 3 says the firmware answers a fault by dropping to the lowest step; SW-009, HW-010 and TC-109 still use FAULT_N; the loss of the short-circuit report was never assessed; GPIO1 and GPIO4 go to a Draft "Should" sensor (I6) | Owner decision needed: keep FAULT_N, or accept the loss with an ADR-0010/0016 amendment | Owner |
| 2 | High | +5V rail parts (TLV75733P VIN 6 V, others) are not covered by the supply-pin surge work (I4, F9) | Assistant: table of every part on VBUS_IC and +5V with its absolute maximum and the surge result | Action |
| 3 | High | Regulator: package stated three ways, no requirement for the transmit-duty limit, TC-213 has no Wi-Fi update load, and a package and topology choice with alternatives needs an ADR (I3, F4, F5, T3) | HW-010 text and heat report corrected to the DBV choice. Open: requirement (owner said later), TC-213 update-load run, ADR | Part fixed; owner for ADR |
| 4 | High | SW-007 flag and clock: a flag set without a reset can stay set and hide a real brown-out; a power-on reset may lose RTC memory; the plan stores an absolute `now_ms` that restarts at 0 (F1, F2) | TC-107 cases (g) and (h) added; rule proposed, owner decides (clear when HOLD_OK_RB is high and the hold-off has ended; store elapsed time) | Owner |
| 5 | High | `gate_on_edge()` did not lower the selects and restart the count (SW-005 criterion 2), no LED-current feedback in the HAL, no sub-poll glitch test (F6) | Plan 07 mapping added; the edge handler to lower the selects is stated here and is added to the plan with the next revision | Action |
| 6 | High | TC-109 pass circular and [X] against [50] ms inconsistent (T1, I11) | Pass split into unit and bench parts; owner resolves [X] versus [50] ms | Fixed in the TC; owner for the value |
| 7 | High | TC-210 passes against criteria of an unapproved amendment, step 4 still requires a TVS1 clamp below 6 V, no surge or resistor/zener fault steps (T2, F3) | TC-210 rewritten: surge capture at both pins, resistor and zener fault rows, conditional on the amendment | Fixed in the TC |
| 8 | High | Plan 07 implements Proposed content (step table, FAULT_N, pin map) (I5) | Gate stated in plan 07: no `sw/` file before approval | Fixed in the plan |
| 9 | Medium | SW-005 has one CC input; TC-105 (g) and (h) and the "unknown combination" rule do not fit (F8, I1) | Open: rewrite SW-005 criteria 3 and 4 and TC-105 (g), (h) for a single input with the amendment | Action |
| 10 | Medium | Surge margin smaller than reported (F10): 0.14 V at the highest zener voltage; zener load understated; S3 threat model differs from the CC analysis | Zener corners added to the script and tests (27 tests pass); reports corrected | Fixed; zener datasheet still to read |
| 11 | Medium | 470 ohm costs 47 mV on a TUSB321 already near its 4.5 V minimum (I9) | Measure in TC-210 case 5; noted in the report | Bench |
| 12 | Medium | CC protection P3: no number, no TC, Type-C and band-edge thresholds not read (T8, I10, F11) | Open: requirement, IEC 61000-4-2 TC and the Type-C read | Action |
| 13 | Medium | Hold-off limit direction: widening by the uncertainty lets a unit below 200 ms pass (F12) | TC-210 now narrows the requirement limits; debounce margin marked not demonstrable | Fixed in the TC |
| 14 | Medium | Watchdog resets are not counted by the back-off; `BL_WDT_S` equals the [10] s limit (F13) | Owner decision needed | Owner |
| 15 | Medium | ADR status lines disagree with the requirements; ADR-0003 and ADR-0011 context text stale; zener part not chosen but values approved (I7, I8, I14) | Open: ADR-0016 Amendment 3, status line updates, HW-012 entries | Action |
| 16 | Low | Test counts, regulator report contradiction, "may be raised" wording, TC-110 details, TC-106 procedure missing (T4, T5, T12, T13, T10) | Fixed in commit 92276d2 | Fixed |
| 17 | Low | Resource budget, regulatory notes, spike pin map from a C6 footprint (T14, I13, I15) | Budget and map-validity statement added to plan 07; regulatory-check and HW-012 entries open | Part fixed |

## Rejected points
None rejected. One reviewer statement stays unverified: the claim that a power-on reset loses the retained memory (stated as "probably", not shown).

## Outcome
Approved with actions. The drafts are consistent enough to go on, but plan 07 and the test procedures are not ready for the owner's approval until findings 1, 4, 5, 9 and 14 are decided or fixed. No approval is stated here.

## Resolution record (2026-11-07, later)
Findings 1 (ADR-0018 option E), 3 (ADR-0019 Accepted), 4 and 14 (SW-007 and SW-010 amendments approved), 5 (plan 07 edge handler), 6, 7, 8, 9 (SW-005 single input approved), 10 and 13 are closed by the owner's decisions and the edits listed in the journal and CHANGELOG. Still open: finding 2 (table of every part on VBUS and +5V with its absolute maximum), the CC-pin requirement and ESD test (12), the transmit-duty requirement (3), ADR status lines and HW-012 entries (15), regulatory-check (17). The owner approved plan 07 with conditions and the test procedures as working procedures on 2026-11-07.
