# Review Record RV-006

- **Subject:** ADR-0009 (USB-C power input, Proposed) and ADR-0010 (USB input current limit, Proposed), with SYS-020, HW-003, HW-010, RISK-003/004/005/024..030, TC-020/203/210 and `docs/verification/reports/spike-7-5-power-budget-paper.md`; commit d4f0d57 (text before this review)
- **Type:** Architecture
- **Date:** 2026-11-04  **Reviewer(s):** three stateless goldfish subagents (comprehension; failure modes and safety lens; testability, arithmetic and manufacturability lens)  **Independent?** partly: same model family as the author
- **Not run:** the implementation-readiness pass. The reviewers read the ADR evidence tables; none read the USB Type-C specification or a datasheet. Facts from the reviewers' own knowledge are marked "verify".

## Comprehension check
The comprehension goldfish restated both ADRs correctly: ADR-0009 senses the advertised current through the ADC on the CC lines, ADR-0010 enforces a hardware limit that starts at about 500 mA and is raised by firmware. Its open questions are findings S1, S12 and S13.

## Findings
The weighted sums (ADR-0009: A 136, B 127, C 88, D 115, E 135; ADR-0010: A 163, B 89, C 128, D 105, E 105, F 120) and the equations for the limit table recompute correctly (reviewer 2).

| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| S1 | Critical | The hardware limit does not cover a CC misread: the firmware that misreads CC also raises the limit. ADR-0010 claimed protection against a "wrong-reading firmware"; ADR-0009 says the opposite. Verified in the two texts. | Fixed now: ADR-0010 and RISK-025 state what the limit covers (stopped, reset, never started, short) and what it does not. Open for the owner: an independent decode path (ADR-0009 option B, or a comparator ANDed with the GPIO) or accept the gap. | Text fixed; design open (owner) |
| S2 | Critical | A hung firmware with the select GPIO high keeps the high limit (the main RISK-003 case); HW-010 tests only "held in reset"; the GPIO state after a watchdog reset is not read; no watchdog requirement exists. | Accepted. Do not accept ADR-0010 open point 4 on this evidence. Action: read the C3 GPIO reset state; watchdog requirement; consider a heartbeat-gated select. | Open (owner) |
| S3 | High | Non-compliant A-to-C cables (10 kohm Rp on a 500 mA port) advertise 3 A that the port cannot supply; no VBUS sense. | Accepted. Add to RISK-024/025; consider a VBUS sense and a slow ramp; add a bad-Rp cable to TC-203. | Open |
| S4 | High | Lowering the limit under load can cause the brown-out the design avoids; order (dim LEDs first, then lower the step) and latency are unspecified; continuous CC monitoring not required. | Accepted. SW requirement and test (1.5 A to default at full white). | Open |
| S5 | High | Brown-out and restart loop: after a reset the firmware re-reads 1.5 A and raises the limit again; the back-off is "to specify". | Accepted. Persistent brown-out flag, back-off, loop counter. | Open |
| S6 | High | PD traffic (BMC) on the CC line (about 1.1 V peak-to-peak, verify) crosses the threshold gap; the "several equal readings" rule may never settle or may flicker; Rp toggling in PD sources. | Accepted. Add a PD charger to the spike; define filter and hysteresis. | Open |
| S7 | High | The ADC margin is miscomputed: the ADR uses the +-35 mV figure over the whole range; the evidence table gives +-10 mV for the 0 to 1300 mV range; and the spike pass criterion (20 mV on each side) needs 110 mV in a 90 mV gap, so it cannot be met at worst-case band edges. Reviewer 2 recomputed; I did not recompute the margin myself. | Accepted. Recompute with the 0 to 1.3 V range and the real Rd and Rp tolerances; rewrite the spike pass criterion so it can be met (saturation above range is harmless). | Open |
| S8 | High | CC pin protection and ESD under-specified (HW-003 lists ESD on VBUS and data only); VBUS-to-CC shorts; chip unpowered with Rp present; GPIO absolute maximum not found. | Accepted. Requirement for a CC clamp and series resistor; test with the chip unpowered. | Open |
| S9 | High | VBUS over-voltage and hot-plug transient not covered (TPS2553 is rated 6.5 V; TPS25200 with a 5.4 V clamp is an open point). | Accepted. TVS or surge requirement; decide open point 5 now. | Open (owner) |
| S10 | High | Thermal analysis covers only the 500 mA step; a short at the top step can be about 7.9 W in a SOT-23-6 with auto-retry cycling in a closed shell; RISK-005 severity is low. | Accepted. Analyse and test the top step; re-rate RISK-005. | Open |
| S11 | High | The limit band does not match the claims: 506 to 629 mA at the 500 mA step (the ADR shows 623), 1366 to 1577 mA at the top (above the 1500 mA cap); the firmware budget has about 1 % margin; the paper budget shows the clamp engaging at the 20 % worse corner. | Accepted. Close ADR-0010 open points 1 and 2 with numbers; consider current feedback. The reviewer's 629 mA vs the ADR's 623 mA is a small difference to settle in `hw/sim/`. | Open (owner) |
| S12 | High | The cap formula is ambiguous: "advertised minus 10 %, capped at 1500" gives 1500 mA for a 3 A source, but the text says 1350 mA; the top hardware step has a minimum of 1366 mA. | Accepted. Write the formula and a table of vectors (default, 1.5 A, 3 A) into SYS-020, HW-003 and the PC tests; owner decides the cap. | Open (owner) |
| S13 | High | Start-up inrush (100 uF, an assumption; no source for the sink capacitance limit) plus boot current can exceed the step-1 minimum and cause a boot loop. | Accepted. Look up the capacitance limit; inrush and boot current in TC-210. | Open |
| S14 | Medium | The 100 mA unconfigured-host case, Ra and e-marked cables with VCONN (about 5 V on the second CC pin read as high), and an upper plausibility window for CC are not covered. | Accepted. Add a window rule (accept 0.25 to about 2.2 V, verify), test cases, and a USB-A host test. | Open |
| S15 | Medium | The middle step (about 900 mA) has no firmware rule that uses it; the "within 1 s" timing has no budget; "ILIM open gives a lower limit" and the gate pull-down state in reset are unverified. | Accepted. Delete step 2 or define its rule; timing budget; FMEA row per single fault. | Open |
| S16 | Medium | ADR-0009 text is stale: it says RISK-024 to RISK-026 are "not added there" but they are in the register. | Fixed now. | Resolved |
| S17 | Medium | Scoring: the do-nothing options score high on some criteria; the gate wording differs between the ADRs; the lead of A over B in ADR-0009 is inside the stated error. | Accepted. One gate sentence; drop the do-nothing row from the scored table. | Open |
| S18 | Medium | Verification: TC-020, TC-203, TC-210 are "Procedure: TBD"; no fault-injection tests; no SW requirement for the CC read, stable-reading rule, brown-out back-off or FAULT response; extended-part fee and cost not computed; second source not named. | Accepted. | Open |
| S19 | Low | Back-feed energy not computed; firmware budget per step not stated as numbers; spike sample counts, temperatures and number of chargers not defined. | Accepted. | Open |

## Outcome
**Not ready for acceptance. Actions required.** Verdict (inferred from the findings, readiness pass not run): **NO-GO** for accepting either ADR. The central safety argument was circular (S1); it is now stated correctly, but the owner must decide between an independent decode path and accepting the gap, and must decide S2 before ADR-0010 can be accepted.

## Actions
Owner decisions: S1 (independent path or accept), S2 (hung firmware), S9 (over-voltage part), S11 and S12 (limit numbers and cap formula). Author work: recompute the margins (S7), thermal analysis at the top step (S10), write the SW requirements and test procedures (S18), behavioural ngspice model.
