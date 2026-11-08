# Review Record RV-013

- **Subject:** HW-014 and HW-015 (Draft) in `docs/requirements/hw.md`, `docs/verification/reports/analysis-5v-bulk-capacitance.md`, `hw/sim/scripts/bulk_cap_bounds.py` and its test, TC-214, TC-215 (uncommitted working tree on branch `fix/spike-drc`, 2026-11-08)
- **Type:** Requirements
- **Date:** 2026-11-08  **Reviewer(s):** four stateless goldfish subagents (comprehension; failure modes and physics; testability; integration and manufacturability); resolution by the assistant (Elephant)  **Independent?** no (AI reviewers of AI-written drafts; the owner has not reviewed)

## Protocol
1. Comprehension: the restatement matched the intent. Nine unclear points (counting sets, bias voltages, the 10 uF rounding, the node of the droop limit, the regulatory field, the origin of HW-015) were fixed in the drafts before step 2.
2. Antagonistic review: three goldfish in parallel; 59 rows in total, merged below (duplicates joined, the reviewer lens in brackets: F failure modes, T testability, I integration).
3. Resolve: the assistant checked the main claims against the sources (HW-010 text "the CC IC is specified from 4.5 V"; USB 2.0 figure 7-47 "supply at hub can drop from 4.400V to 4.070V"; SK6812 FPWM 1.2 kHz, SK2020 FPWM 1.0 kHz, WS2812B "not less than 400Hz"; `analysis-vbus-5v-part-ratings.md` options S1 to S3 open; RV-006 S13 open). All were confirmed.
4. Implementation readiness: **not run**. The drafts are known to be not ready (findings 1 to 4), so a readiness goldfish would only repeat NO-GO.

## Findings
| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| 1 | Critical | Lower bound has no DC resistance (cable, connector, switch). The static drop (I0 + dI) x R can use most or all of the 300 mV budget; no capacitance recovers it (F1, T1, I2) | Accepted. The droop model is wrong in kind, not only in numbers. Redraft needed | Open |
| 2 | Critical | dI = 0.6 A assumes the firmware ramps LED changes, but WS2812-class LEDs switch the full channel current at their internal PWM (1.0 to 1.2 kHz, 400 Hz or more); in phase, the step is the whole LED current, up to about 1.35 A at step 3 (F2, I3) | Accepted. dI must come from the LED PWM worst case or from an LED/SW requirement; the "firmware ramps" assumption is withdrawn | Open |
| 3 | High | The binding threshold is not the supervisor: the CC IC is specified from 4.5 V (HW-010 M4), above the 4.40 V static assumption; and USB 2.0 allows a hub transient to 4.07 V, at the supervisor maximum before any cable loss. Capacitance on the board cannot protect against either (T3, F3) | Accepted. The H2 problem (silent hold-off restart) belongs to HW-010 M4 and the supervisor threshold, not to a capacitance bound. The lower bound needs another driver (for example LED PWM ripple on +5V with a defined limit) | Open, owner |
| 4 | High | Operating point mixes cases: a 0.6 A step on top of the start load exceeds step 1, so it exists only on a 1.5 A Type-C source, while 4.40 V is a USB 2.0 low-power port value; "before the cable drop" is wrong (4.40 V is at the plug) (T2, F3, I2) | Accepted. Split per step and source type; read Type-C vSafe5V and the cable IR-drop rule | Open |
| 5 | High | USB inrush rule: if the USB-IF inrush test counts all charge against 50 uC, even the lower bound (10 uF at 5 V) plus HW-015 fails, so the requirement set is infeasible; HW-014 acceptance (4) has no pass value (F4, T9, I1) | Accepted. Reading the USB-IF compliance test procedure and the Type-C sink rules is an entry condition for In Review. If all charge counts, the answer is a slower soft start, an ADR | Open |
| 6 | High | HW-015 stated as fact that the switch hides the +5V capacitance; USB 2.0 counts "capacitive effects visible through the regulator" (T7, F4, I4) | Fixed: rewritten as an open assumption in the HW-015 rationale | Closed (text); question open |
| 7 | High | HW-015 bench method turns the switch on (EN tied to IN, UVLO 2.35 V), so the meter sees +5V; zeners conduct at 5.25 V; no frequency (T6, F10, I4) | Fixed: build without U7, LCR at [120] Hz, zener current recorded. The ECN names the inrush test as the method: see 5 | Closed (text) |
| 8 | High | Upper bound rests on unbounded inputs: C_3V3 = 10 uF (module and C6 not known) and I_start = 0.1 A (nothing shown holds the module in reset for 1.5 ms); margin only 4 % (104 vs 100 uF); 22 uF on 3V3 gives about 97 uF (T4, T5, F5, I10, T22) | Accepted. Either bound the total charge Q(+5V) + Q(3V3), or add a +3V3 capacitance and start-load limit; add a sensitivity table | Open |
| 9 | High | Surge decision S1/S2/S3 is open; S2 (TPS25200) changes F1 to F4, S3 changes the droop model; the +5V capacitance also sets the surge level on +5V (I5) | Accepted. HW-014 approval waits for, or is linked to, that decision | Open, owner |
| 10 | Medium | HW-015 minimum ignores inductive overshoot on VBUS_IC (switch turn-off into a short, load release, hot-plug ringing of an all-ceramic node against the 7 V TPS2553 rating) (I6, F8) | Accepted. Add an overshoot check (ngspice, existing surge script) over the HW-015 range; consider a lossy part | Open |
| 11 | Medium | Reverse current and unplug back-feed: the TPS2553 reverse comparator acts after 3 to 7 ms, so the +5V bulk feeds VBUS_IC and the pin; effect on the supervisor and FAULT_N not analysed (F6, I11) | Accepted. Add to the analysis and to TC-210 item 7 or 8 | Open |
| 12 | Medium | Counting C24 to C26 (behind 470 ohm and 1 kohm) toward the 1.0 uF minimum lets C2 be marginal (I19) | Fixed: they count only toward the 10 uF maximum; C2 alone meets 1.0 uF | Closed |
| 13 | Medium | Bench criteria weak: no pass limit for the time in current limit, no 5.5 V or temperature corner, FAULT_N observation window and probe point, load-step edge rate, source and cable not named (T10, T11, T12, F9, I8, I9) | Accepted. Write in the TC-214 procedure at the redraft | Open |
| 14 | Medium | Script cannot check "the chosen values" (no capacitor table input); tests confirm the assumed constants only; no failure cases for a negative budget or C_max (T13, T14, I22) | Accepted. Add a capacitor-table check and corner tests at the redraft | Open |
| 15 | Medium | Statement quality: one "shall" with two limits and two counting sets; "operating temperature range" is not defined in any requirement; ageing and dielectric not addressed (T15, I14) | Accepted. Split min and max at the redraft; reference a temperature range or set one | Open |
| 16 | Medium | Failure path after a missed lower bound: hold-off restart at full white, no foldback, LEDs keep their frame if the processor browns out; possible stuck state with the switch thermal cycling (F7) | Accepted. Add to the risk register and the HW-010 fault table | Open |
| 17 | Medium | Placement unconstrained: no pin ties for C3, C5 or C4; the "track inductance" reason for leaving out the LED capacitors is physically weak (tens of nH against 1 to 2 uH) (T21, I12) | Accepted. The exclusion is a margin choice; reword at the redraft; pin ties are a spike change for a later batch | Open |
| 18 | Medium | Feasibility not shown: for small X5R parts C(5.5 V)/C(0 V) can be about 0.2, so the window may close; bounding Q instead of C(0 V) is less conservative and more correct (I13) | Accepted. Add a worked example with a real part and its DC-bias curve | Open |
| 19 | Medium | No risk register entry for false FAULT at plug-in or USB inrush non-conformance; RV-006 S13 and TC-210 already cover part of the inrush test (I15) | Accepted. Add a RISK at the redraft; TC-214 reuses the TC-210 captures | Open |
| 20 | Medium | HW-014 parent SYS-027 (watchdog restart) does not fit (T17, I21) | Fixed: parent SYS-020, derived with HW-004 and HW-010 | Closed |
| 21 | Low | Verification method "Analysis" while the criteria hold bench tests (T8, F12, I17) | Partly fixed: the TC line names the bench parts; the method field keeps one value because the template allows one | Closed (text) |
| 22 | Low | 5.5 V (HW-014) and 5.25 V (HW-015) as maximum VBUS; 5.5 V exceeds the 5.3 V of the WS2812B placeholder (I16) | Accepted. One source of truth for VBUS maximum after the Type-C read | Open |
| 23 | Low | F8 quoted too broadly ("powered or unpowered" applies to the minimum); USB package hash truncated (F11, T18) | Fixed | Closed |
| 24 | Low | Supervisor glitch immunity (10 us typical) not stated as not credited; height of the bulk part on B.Cu (about 3 mm) not constrained; LED power-on state not quoted (F13, I20, F14) | Accepted for the redraft | Open |

## Outcome
Rejected for In Review. HW-014 and HW-015 stay Draft. The upper bound of HW-014 and the whole of HW-015 are close to usable after findings 5, 8, 9 and 10; the lower bound of HW-014 needs a new model and probably a new driver (finding 3). Owner decisions needed: what the lower bound protects (finding 3), and the order against the surge decision S1/S2/S3 (finding 9).

## Owner decision after the review (2026-11-08)
The derived lower bound is withdrawn. The HW-014 lower bound is the part makers' minimum (TLV757P input), the prototype
gets spare footprints (HW-016, Draft), and the prototype measurement decides whether more capacitance is fitted. The
owner first chose a bound from the LED PWM; the assistant showed that smoothing the PWM needs about 5 mF and that only
edge damping (4 to 50 uF, assumed cable values) is possible; the owner then chose the makers' minimum. Findings 1, 2, 3
and 4 are closed by the withdrawal (finding 3: the supervisor and CC IC margin stays an HW-010 M4 item). The
redraft has not been reviewed again.
