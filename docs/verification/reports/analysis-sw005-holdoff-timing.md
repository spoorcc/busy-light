# Analysis: SW-005 stable-reading time against the hold-off maximum

- **Status:** Draft
- **Date:** 2026-11-05
- **Author:** Claude. Not reviewed. Nothing here is Approved or Accepted. No requirement, ADR or status was changed.
- **Closes:** the open item "SW-005 against the hold-off maximum" in `owner-decisions-2026-11-05.md` (analysis only; the owner decides every wording below).
- **Texts read:** SW-005, SW-006, SW-007, SW-009 (Draft text and Proposed amendment), HW-003, HW-010 (Approved text and Proposed amendment), SYS-020, ADR-0010, ADR-0016, TC-105, TC-109, TC-210, `cc-ic-datasheet-evidence.md`, `datasheet-evidence-supervisor.md`, `analysis-n4-holdoff-capacitor.md`. Branch `docs/review-actions` of the main worktree.
- **Script and test:** `hw/kicad/spike-gate/sim/sw005_holdoff_timing.py`, `hw/kicad/spike-gate/tests/test_sw005_holdoff_timing.py` (5 tests pass).
- **Labels:** **spec** (requirement text), **read** (datasheet evidence in this repository), **derived** (computed here), **ASSUMED** (no source), **not found**.
- Nothing was measured, simulated on the bench or run on hardware. Arithmetic only.

## 1. Summary

1. **The numbers do not fit SYS-020.** If the firmware counts the stable reading only after the hold-off (the proposed M2 rule), the step is raised at 700 to 1222 ms after connection with the specified 200 to 600 ms window, and at 710 to 1198 ms with the capacitor set of N4. SYS-020 asks for the limit within [1] s of connection. The HW-010 remark "the upper value keeps the limit change inside the [1] s of SYS-020" is true only if the firmware adds no delay at all.
2. **The hold-off window cannot be narrowed much.** A TPS3840 with a 5 % C0G capacitor gives a maximum of at least about 545 ms for a minimum of 200 ms (ratio 2.72 of the datasheet constants). So a 1 s budget cannot be met by tightening the hold-off; one of three numbers must change: SYS-020 (1 s), the SW-005 window (500 ms), or the hold-off minimum (200 ms).
3. **SW-005 is ambiguous about reads.** "[5] reads over at least [500] ms" has no read period. At 100 ms (SW-006) five reads span only 400 ms, so six reads are needed; at 1 ms the 500 ms term is the only binding one. The count clause is either redundant or contradicts the time clause.
4. **SW-005's acceptance anchor ("within [1] s of a stable reading") is not the SYS-020 anchor ("of connection")** and is about 1 s looser.
5. **SW-009's [50] ms has no derivation and cannot protect the rail.** With the only capacitance figure in the repository (assumed 100 uF, ADR-0010) the 5 V rail carries a 727 mA deficit for about 0.07 ms before it falls 0.5 V. 50 ms would need about 73 mF. So shedding within 50 ms limits how long the overload lasts; it does not prevent the brown-out. The Rationale of SW-009 says the opposite.
6. **The hold-off margin over the CC debounce is thin and based on a typical value.** 133 ms is "typ"; no minimum or maximum was read (`cc-ic-datasheet-evidence.md` item 8). The hold-off minimum of 200 ms leaves 67 ms over the typical value and an unknown margin over the maximum. The time of the first meaningful output is therefore not proved to be inside the hold-off.
7. **Gaps that make tests impossible today:** TC-105 and TC-109 have "Procedure: TBD"; the read period, poll or interrupt method, step mapping and the start point of the hold-off are not defined; "IC supply valid" cannot be observed.

## 2. Timing budget

All values in ms. "Worst" is the sum of maxima, "best" the sum of minima. Assumptions are in the last column and in the script header.

### 2.1 Stages from connection to the raised step (count starts when HOLD_OK_RB goes high)

| # | Stage | Min | Max | Label | Remark |
|---|---|---|---|---|---|
| 1 | VBUS rise to the supervisor release voltage | 0 | 10 | ASSUMED | Not in any document. USB inrush and cable length decide; M4 slow-ramp case is outside this row. |
| 2 | Supervisor start-up tSTRT | 0.1 | 0.35 | read | TPS3840 (A17), CT open; CT adds tD. |
| 3 | Hold-off tD, specified window | 200 | 600 | spec | HW-010 |
| 3b | Hold-off tD, N4 capacitor set 220+220+150+33 nF | 210.3 | 576.0 | derived | `holdoff_cap.py` set, 5 % C0G, temperature term included; tD(no cap) min not found. |
| 4 | Firmware boot to the first read | 100 | 500 | ASSUMED | No boot time in the repository (E0 to E12 spike reports do not give one). Runs in parallel with 1 to 3, matters only if longer. |
| 5 | Phase: first read after the HOLD_OK_RB edge | 0 | 100 | ASSUMED | One read period, 100 ms from SW-006. SW-005 gives no period. |
| 6 | Stable window, 6 reads at 100 ms | 500 | 500 | spec + derived | max(5-1 intervals, ceil(500/100) intervals) x 100 ms. |
| 7 | Select GPIO write after the decision | 0 | 10 | ASSUMED | Task latency. |
| 8 | ILIM switch and TPS2553 settling | 0 | 2 | ASSUMED | Not found in the evidence. Output rise time 1.5 ms max is read (E6), the ILIM step response is not. |
| | **Total, specified window** | **700.1** | **1222.35** | derived | Script: 700.1 to 1222.3 |
| | **Total, N4 set** | **710.4** | **1198.3** | derived | |
| | SYS-020 budget | | 1000 | spec | **Worst case exceeds it by 198 to 222 ms** |

With a 125 ms period (five reads exactly span 500 ms) the worst case is 1247 ms.

### 2.2 What would make 1 s feasible (derived, same assumptions)

| Change | Result | Feasible? |
|---|---|---|
| Hold-off maximum limited so the sum stays at 1000 ms | maximum 377.6 ms | Not with a 200 ms minimum: the TPS3840 spread forces a maximum of at least 545 ms. |
| Keep hold-off 200 to 600, shorten the stable window | window at most 200 ms (6 reads at 100 ms = 500 ms is replaced by 3 reads) | Yes, but 200 ms is only 1.5 x the typical CC debounce and 1.0 x its assumed maximum. Not recommended. |
| Keep both, relax SYS-020 to [2] s | worst 1222 ms, margin 778 ms | Yes. Cheapest. Costs a longer period at the 500 mA brightness after plug-in. |
| Lower hold-off minimum to 150 ms | maximum about 409 ms; sum about 1031 ms | No, and 150 ms is only 17 ms above the typical debounce. |

### 2.3 Other chains

| Chain | Min | Max | Label | Result |
|---|---|---|---|---|
| CC IC first meaningful output: VBUS_DET debounce + CC debounce | 2 + (min not found) | 2 + 133 typ | read | Maximum not found. The Type-C specification range for tCCDebounce (100 to 200 ms) is general knowledge, **not read in this project**; if it applies, the hold-off minimum of 200 ms has no margin. |
| Hold-off minimum minus typical debounce | | 67 ms (200 - 133) | derived | 77 ms with the N4 set (210.3 - 133). Margin against the maximum: unknown. |
| Gate closes after a VBUS dip | about 10 us | | read | tGI_VIT- 10 us at 5 % overdrive (A16). The gate closes at once; the 200 to 600 ms is the closed time after recovery, not the time before closing (SW-009 Rationale wording). |
| Gate closed time after a dip | shorter than 200 | 600 | read | A16: after a short dip the CT is not fully discharged, "reset delay is shorter than expected"; the discharge time is not given. So "at least 200 ms after every loss" is not guaranteed by the supervisor for a short dip. TC-210 has the measurement (RISK-044). |
| SW-006 firmware path: read period + shed | | 100 + 50 = 150 | spec | Longer than the rail hold-up (below). |
| SW-009 firmware path: edge or poll latency + shed | | poll period + shed | spec | Poll period not defined; 50 ms cannot be met at a 100 ms poll. |
| Rail hold-up, 5 V bulk C, load 1350 mA, limit 623 mA, 5.0 V to 4.5 V | | C = 47 uF: 0.032 ms; C = 100 uF: 0.069 ms | derived | Constant-current limit and load, so optimistic (a buck is a constant-power load, RISK-004). The 100 uF is the ADR-0010 assumption, not a design value. |
| Capacitance needed for 50 ms | | about 72.7 mF | derived | Not achievable. |

## 3. Findings

### 3.1 Contradictions

| ID | Finding | Where |
|---|---|---|
| C1 | Stable window (500 ms) plus hold-off (up to 600 ms) plus read phase exceeds the 1 s of SYS-020. The HW-010 parenthesis claims the opposite. | SYS-020 acceptance; HW-010 acceptance (hold-off sentence); SW-005 |
| C2 | SW-005 measures "[1] s of a stable reading"; SYS-020 measures "[1] s of connection". The SW-005 criterion can pass while SYS-020 fails. | SW-005 acceptance; SYS-020 acceptance |
| C3 | SW-009 Rationale says the shed prevents the brown-out and the back-off. Hold-up arithmetic says the rail falls in well under 1 ms. The shed shortens the overload; it does not prevent the reset. | SW-009 Rationale |
| C4 | SW-006 says the firmware lowers the load first and the step after. For a change from 1.5 A to default the IC output goes high and the hardware gate lowers the limit itself, before the firmware's next read (up to 100 ms). The order cannot be kept by the firmware. | SW-006 statement |
| C5 | HW-010 says the hold-off starts "after the IC supply becomes valid" (4.5 V, TUSB321); the supervisor timer starts at its release voltage (4.115 to 4.285 V). Different events. | HW-010 acceptance; proposed amendment M4 |

### 3.2 Gaps

| ID | Gap |
|---|---|
| G1 | SW-005 has no read period and no rule whether reads while HOLD_OK_RB is low count (the proposed M2 rule makes them invalid, but the count is not said to restart). |
| G2 | After a hold-off that follows a dip, the firmware's select GPIO may still be high. At the end of the hold-off the hardware then raises the limit with no new stable reading. SW-005 covers "after power-up" only. |
| G3 | The mapping from the stable value (default, 1.5 A, 3 A) to a step is not in SW-005. With three exclusive steps (HW-010 proposal) it is not stated whether the firmware goes 1 to 2 to 3 or 1 to 3, how long it waits between, or how a 3 A advertisement is mapped (SYS-020 cap is 1500 mA; OUT2 is not used by the gate). |
| G4 | "Unreadable or unknown value" has no definition for a digital input. Proposed meaning: HOLD_OK_RB low, or the two inputs in the combination that the IC cannot give. |
| G5 | The numbers [5] and [500] have no rationale. 500 ms is 3.75 x the typical debounce; 5 reads is not derived. |
| G6 | SW-007 and SW-009 say a brown-out "during a hold-off" is not counted. After a brown-out the MCU resets and restarts in the boot time; the hold-off may have ended or may still run. The rule has no observable test (reset cause alone does not say "during hold-off"; HOLD_OK_RB at the first read after boot, or a retained flag, would). |
| G7 | SW-009 does not define the readback debounce, the poll or interrupt method, or what happens when a hold-off is shorter than the poll period (a short dip, finding A16). |
| G8 | CC debounce minimum and maximum, tD(no cap) minimum, the TUSB321 output level before the first debounce: **not found** (evidence items 8 and 9). The 200 ms minimum cannot be shown to cover the debounce. |
| G9 | No boot-time number and no ILIM step-response number exist. |
| G10 | Rail bulk capacitance is not a requirement (HW-004 has no value). The shed time cannot be derived. |

### 3.3 Untestable or weak wording

| Text | Problem |
|---|---|
| "stable reading" (SW-005) | Needs: read period, equality (both inputs unchanged), and the clock start. |
| "the step is set within [1] s of a stable reading" | No start event for a test; measure at the ILIM pin or the input current? |
| "start-up hold-off ... at most [600] ms" (HW-010) | The end of the hold-off is the rise of the enable outputs; the start is not observable ("IC supply valid"). A bench test needs a named signal and threshold, for example VBUS_IC crossing 4.5 V with a ramp of at most 10 ms. |
| "a source that advertises the default current ... each select output forced high in turn" | Fine, but the hold-off interaction is not in it: the select must also be forced high during the hold-off. |
| "within [50] ms of the hold-off or the gate closing" (SW-009) | "the hold-off closing" is ambiguous; the start event is the HOLD_OK_RB falling edge (a pin edge that a test can see). |
| "no brown-out back-off starts" (SW-009) | Not a measurable result if the MCU resets (C3): the test needs a defined load level and defined reset behaviour. |
| TC-105, TC-109 | "Procedure: TBD". No injected-clock unit test, no bench steps. |

## 4. Proposals (all Proposed; none is entered in any requirement)

The owner decides. Bracketed numbers are working values that the owner sets.

### P1 SYS-020, anchor and budget (decision for the owner)

Recommendation: relax the bracket and state what is measured.

> Proposed acceptance text, replacing "The limit is set within [1] s of connection": "On a source that advertises 1.5 A, the input limit is raised to the advertised value minus the margin within [2] s of connection. The limit is the default value from connection until then."

Why: removes C1 and C2, costs nothing in safety (the 500 mA step is the safe state), margin 778 ms over the derived worst case of 1222 ms. Alternatives, worse: shorten the stable window to 200 ms (weakens SW-005, G5), or lower the hold-off minimum (weakens the debounce margin, G8). The hold-off window cannot be narrowed (summary 2).

### P2 SW-005

Proposed statement:

> "The firmware shall start with the lowest current step. It shall read the advertised-current inputs every [100] ms, shall count a read only while HOLD_OK_RB is high, and shall restart the count on any change of a read or when HOLD_OK_RB goes low. It shall select a higher step only after [6] consecutive equal reads (at least [500] ms), and shall select the step in the table of this requirement for that value, no higher."

Proposed acceptance additions:
- "The step is selected within [700] ms of the rising edge of HOLD_OK_RB (500 ms window, 100 ms read phase, GPIO and settling, with margin)."
- "After every falling edge of HOLD_OK_RB the firmware sets the select outputs low and starts a new count (also after a cable wobble, not only after power-up)." (closes G2)
- "Value table: default or HOLD_OK_RB low gives step 1; 1.5 A and 3 A give the highest step that the SYS-020 maximum allows [table to be agreed with ADR-0010 point 3]." (G3)
- "Unknown value means HOLD_OK_RB low or any input combination that the IC cannot output." (G4)
- A rationale sentence for [100], [6] and [500] (G5). The 700 ms figure in the first bullet is the 100 ms phase plus the 500 ms window plus 10 ms GPIO plus 2 ms settling, rounded up with margin; the derived sum is 612 ms.

Note that with 100 ms and 6 reads the count and the time agree, so one of the two numbers may be dropped. Suggested: keep the time and say "at least 6 reads", or keep only "[500] ms".

### P3 SYS-020 and HW-010 consistency

HW-010 (Approved) is not edited here. A Proposed amendment sentence: replace the parenthesis "(the upper value keeps the limit change inside the [1] s of SYS-020)" with "(the upper value, with the stable reading time of SW-005, is within the time that SYS-020 gives for the raise of the limit)". Also define the measurement: "hold-off = time from VBUS_IC crossing [4.3] V to the rise of each enable output through [1.65] V, measured with a VBUS ramp of at most [10] ms"; both levels are working values and the IC supply threshold (4.5 V) is dropped from the hold-off definition (C5). Add to the acceptance criteria that the TUSB321 maximum debounce (value to be read from the datasheet; not found) is below the measured minimum hold-off with at least [20] ms margin, and set the measured values in TC-210. If the datasheet maximum is 200 ms or more, the hold-off minimum or the 200 ms needs a new ADR-0016 amendment (the 200 ms came from the typical value).

### P4 SW-009

Replace the Rationale sentence "closes by itself after a dip of VBUS for [200] to [600] ms" by: "closes within about 10 us of a VBUS dip and stays closed for [200] to [600] ms after VBUS returns (a short dip can give a shorter time, TC-210)." Replace the claim in the Rationale that the shed avoids the brown-out by: "The shed limits the time of the overload and the time in which the MCU can reset; the 5 V rail falls in under 1 ms at the assumed capacitance (analysis-sw005-holdoff-timing.md), so the reset is not prevented." Statement changes (Proposed):
- "[50] ms" becomes "[X] ms of the HOLD_OK_RB or EN2/EN3 readback falling edge, with edge-triggered interrupts and a latency of at most [1] ms". X to be set from a measured rail hold-up; the derivation is open (G10).
- "A hold-off shorter than the poll period shall not be missed: the firmware latches the falling edge." (G7)
- Define "during a hold-off" for SW-007 as: HOLD_OK_RB low at the first read after the reset, or a retained flag set by the readback interrupt (G6).
Open for the owner: whether a hardware measure is wanted because the firmware cannot beat the rail (more bulk capacitance, which also costs inrush and cost, or a gate that waits for a firmware "load shed done" signal). I do not recommend one without a measured hold-up.

### P5 SW-006

Add: "or when an enable readback (EN2, EN3) goes low, whichever is first" to the trigger, and change the statement of order to: "reduce the LED current to the new allowed level, within [50] ms of the stable value falling, or of the readback falling, whichever is first; the select line is set low after that (the hardware gate has usually lowered the step already)". Removes C4.

### P6 Tests (fills "TBD")

- TC-105, unit level with an injected clock and fake GPIO: (a) 6 equal reads at 100 ms give the step at read 6; (b) a change at read 5 restarts; (c) HOLD_OK_RB low during the count restarts; (d) falling edge of HOLD_OK_RB sets the selects low and the next raise needs a new count; (e) default reading never sets a select; (f) the step arrives within 700 ms of the HOLD_OK_RB rising edge for a 5 ms jitter of the clock. Bench level: scope on HOLD_OK_RB and the select GPIO with a 1.5 A source; the limit step is read from the input current at the SYS-020 time.
- TC-109: unit, edge interrupt to shed within [X] ms; bench, forced VBUS dip of 10 us, 10 ms and 100 ms, record the time from HOLD_OK_RB fall to the LED current and whether the MCU resets (record, not pass criterion until [X] is set).
- TC-210: add the measured hold-off from the named signals (P3), the full-restart question after a dip of 10 us to 100 ms (RISK-044), and the debounce of the CC IC at start and at a source change on a scope.

## 5. What was not done

- No bench measurement, no simulation, no firmware exists to test. All stage values labelled ASSUMED are guesses to be replaced: VBUS rise (1), boot time (4), GPIO latency (7), ILIM step response (8), bulk capacitance (G10).
- Not read: the TUSB321 minimum and maximum CC debounce, the Type-C specification, the TPS2553 ILIM step response, the board's real 5 V capacitance.
- tD(no cap) minimum of the supervisor (neglected, as in N4).
- Whether the TUSB321 restarts the debounce after a source change (the second chain of SW-006 and SW-005 after a source swap).
- The step mapping for 3 A sources was not decided.
- Regulatory aspects: no statement of compliance is made; the changes concern timing only (SYS-020 safety category is Safety, so a review by the owner is needed).
