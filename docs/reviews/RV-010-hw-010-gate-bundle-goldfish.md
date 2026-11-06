# Review Record RV-010

- **Subject:** HW-010, SYS-020, SW-005, SW-006, SW-007, SW-009 Proposed amendments and ADR-0016 Amendment 2, branch `docs/review-actions` at 1ebee8f
- **Type:** Design
- **Date:** 2026-11-06  **Reviewer(s):** four stateless goldfish subagents (comprehension; failure modes and safety; testability and non-functional; dependencies and integration)  **Independent?** yes
- **Entry document given to the goldfish:** `docs/decisions/ADR-0016-independent-hardware-gate-for-high-current-step.md` (they followed its references)
- **Not done:** the implementation-readiness goldfish (step 4 of the protocol). It makes no sense before the High findings are closed. No bench, SPICE or build was run by any reviewer.

## Comprehension result
The goldfish explained the gate design as intended (TUSB321 plus AND gate, hold-off, E96 limit steps, TMUX1101). It could not find one place that states the built circuit, and it listed unclear points 1 to 10. These repeat in the findings below.

## Findings
Source tags: S = failure modes and safety, T = testability and non-functional, I = integration. Status: Fixed = changed in this branch; Owner = needs an owner decision; Action = work item before approval; Rejected = not accepted, reason given.

| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| 1 | High | S1: the ADR says an unpowered or failed IC reads "default" and the gate stays off. HW-010 amendment says CC_OK_1A5 and CC_OK_3A read high with VBUS gone and 3V3 up. Verified: ADR lines 78 and 93 against `hw.md` line 142. | Valid. Replace the ADR truth table by a full table over IC supply, 3V3, hold-off state and GPIO, marking rows where "off" depends on the hold-off alone. | Action |
| 2 | High | S2, I16: the supervisor releases at 4.115 to 4.285 V but the TUSB321 is specified from 4.5 V. A sagging source gives no stated IC output. | Valid and already listed as M4. Raise it from "proposal check" to an HW-010 acceptance item with a loaded-source sag test (4.2 V and 4.4 V). Whether to move the threshold needs the owner. | Owner |
| 3 | High | S3, T1, I2: margin to 200 ms is 3.2 ms and the maximum CC debounce is not found. The [20] ms margin criterion cannot be met with 203.2 ms if the maximum is 200 ms. The reviewers quote 100 to 200 ms from memory, not from the repo. | Valid. The evidence report lists only typical values (133 ms and 120 ms, which also disagree). Find the TUSB321 maximum debounce before approval. Treat [200] ms as a design target. Owner chose the 6 x 100 nF set knowing the margin; reconsider if the maximum is 200 ms or more. | Action, Owner |
| 4 | High | S4, T11, I11: the TMUX1101 abs-max exceedance at each power-up has an estimated effect of up to 7 uA against 21 uA at step 1. The ADR says "unknown, not zero". | Valid. State the bound in numbers (about +33 % at step 1, above 623 mA) in DEV-001 and RISK-045. Make TC-210 (d) a blocking item and write it as a standalone test with pass limits. Whether to remove the exceedance by design (VDD from VBUS_IC, series resistor) is an owner decision. | Owner, Action |
| 5 | High | S5, I15: exclusivity of the two select outputs. Both on gives 1817 to 2020 mA. | Partly valid. The spike has hardware exclusivity (a NOR forces step 2 off when step 3 enable rises, `gen_gate.py`). The ADR and HW-010 do not state it. State it, add GPIO2 = GPIO3 = 1 to the fault list, and say "not on together in steady state" (a few gate delays of overlap at the 2 to 3 change). | Action |
| 6 | High | T2, T3, I2: the Amendment 2 figures could not be repeated from the repo scripts (no 6 x 100 nF set, no 56.2/27.4+301 case). | Fixed. `hw/sim/scripts/amendment2_numbers.py` and its test reproduce 203.2 to 553.2 ms and 504.2/616.6, 934.9/1091.7, 1381.2/1566.6 mA. The spike scripts and tests still hold the old sets (finding 7). | Fixed |
| 7 | High | I1, T5: the spike (`gen_gate.py`, `layout_full.py`, its tests) still holds the E192 resistors and the 220+220+100+68 nF set. | Valid. hw/ content, blocked by rule 1 until HW-010 is Approved. After approval, regenerate the spike by script and change the locking tests. | Action |
| 8 | High | T4: SYS-020 says "1198 ms" for the owner capacitor set. That belonged to a superseded set. | Fixed. `system.md` now says about 1175 ms (1222 - 600 + 553.2) and names the supersession. Note it is arithmetic, not a re-run of `sw005_holdoff_timing.py`. | Fixed |
| 9 | High | T5, I6: the Approved HW-010 and the layered Proposed paragraphs disagree, and the first Proposed paragraph still names 56.9/27.7 k and 220+220+150+33 nF. | Valid. Consolidate the proposal into one clean HW-010 revision (one table of current values) before the owner approves. The step 2 level has no SYS requirement. Define it in SYS-020 or drop it. | Action, Owner |
| 10 | High | I3: CC_OK_3A reads OUT2, which the evidence report says is not a clean 3 A signal. SYS-020 caps the limit at 1500 mA. | Valid. Delete U12, R7 and GPIO1 CC_OK_3A, or write a requirement that explains it. Recommend deleting (frees a GPIO and a part). | Owner |
| 11 | High | I4, S7: PTN5150A is not a drop-in fallback. Its datasheet and output polarity were not read. | Valid. Say in the ADR that the fallback means a re-layout, read the datasheet, and make the 0 to 70 C check a gate before layout. | Action |
| 12 | High | I5: no hold-off after a CC change while VBUS stays up. | Valid. Add the case to HW-010, TC-210 and RISK-042. | Action |
| 13 | Medium | S6, T8, I12: step margins (6.4, 10.4, 15.2 mA) do not model temperature coefficient and ageing. T8 estimates the TC term at about 1.5 mA. | Valid. Add 25 ppm/degC to the model and state the temperature range. Make the 70 degC test mandatory. | Action |
| 14 | Medium | S8, I14: hung firmware at the top step and the thermal limit have no requirement. | Valid and known (S2 deferred). Record as an open blocking item in the technical file. Write the thermal and watchdog requirements. | Action |
| 15 | Medium | S9, T12: SYS-020 says "the device does not reset" but the rail falls in under 1 ms. SW-006 and SW-009 keep [50] ms. | Valid. Decide "shed in [X] ms" or "avoid reset". Remove the "no brown-out back-off starts" criterion. Matches the owner decision to keep the [X] ms placeholder. | Drafted as Proposed text in SYS-020, SW-005, SW-006, SW-007, SW-009 (2026-11-06); owner decides |
| 16 | Medium | S10: back-feed from the ESP32 D+ pull-up with VBUS gone. | Valid. Add the measurement to TC-210 with a pass criterion. | Action |
| 17 | Medium | S11, T-header: documents disagree on bracketed timing values. | Covered by finding 9. | Action |
| 18 | Medium | S12, I9: readback pins GPIO20 and GPIO21 at boot (ROM print, pull-up). | Valid. Decide readback resistor or eFuse and add a first-boot scope step. The Kconfig check is the open `west` build. | Action |
| 19 | Medium | T7, I7: Amendment 2 table sums C as 60, correct is 57. | Fixed in ADR-0016 (A 81, B 75, C 57, D 53; ranking unchanged). | Fixed |
| 20 | Medium | I8: pull-down values differ between the ADR (100 k), HW-010 and the spike (10 k in parallel with 100 k). | Valid. State one pull-down network in HW-010. | Action |
| 21 | Medium | I10: GPIO budget has no spare pin. | Valid. Record the pin map. Deleting CC_OK_3A frees one. | Action |
| 22 | Medium | I13, S15: sourcing unverified for TS5A3166, TUSB321 (X2QFN) and a second source for the resistors. Extended-part fees. | Valid. BOM-level JLCPCB check before layout (this includes the two unchecked parts already on the open list). | Action |
| 23 | Medium | T10: the ADR cites TC-203 for the gate test, but TC-203 verifies HW-003 only. Verified in `test-cases-hw-mech.md`. | Valid. Add HW-010 to TC-203 or drop the reference. | Action |
| 24 | Medium | T6: HW-010 does not say the top step limit (up to 1577 mA) is not overload protection for a 1.5 A source. | Valid. Say it. | Action |
| 25 | Medium | T9: no measurement-uncertainty allowance on the 3.2 ms margin. | Valid. Set pass limits with the uncertainty included. | Action |
| 26 | Medium | T13: SW-005 count against time, and the retained-flag method of SW-007 is undecided. | Valid. Choose a normative criterion. Make the flag method a design item before SW-007 is Approved. | Drafted as Proposed text in SYS-020, SW-005, SW-006, SW-007, SW-009 (2026-11-06); owner decides |
| 27 | Low | S13, S14, I17: fault-injection list is incomplete. Single-fault claims are wider than the evidence. | Valid. Put the faults in a table in TC-210. Keep the technical file wording to "in the cases listed". | Action |
| 28 | Low | T14: ADR header "Related" was stale, pre-review acceptance has no DEV, and a branch commit is cited. | "Related" Fixed. The pre-review acceptance is a process deviation worth a DEV entry (owner decision). The e296fa3 reference stays: it explains why a draft on another branch is superseded. | Fixed, Owner |
| 29 | Low | S3 side claim: the hold-off starts at VBUS_IC while the IC debounce starts after its own supply is valid. | Valid. Fold into finding 2. | Action |

## Rejected points
None rejected outright. Two reviewer statements are not accepted as facts: the USB Type-C debounce range (quoted from memory, not in the repo) and the 1.5 mA temperature coefficient estimate (a rough number; the model change in finding 13 settles it).

## Outcome
Rejected for approval as written. The Fixed items are in this branch. The Action and Owner items must be closed, then a fresh readiness goldfish (protocol step 4) must answer GO, before the owner approves. This record states no approval.
