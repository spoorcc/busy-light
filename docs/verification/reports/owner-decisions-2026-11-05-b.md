# Owner decisions of 2026-11-05 (second record): relaxed SYS-020 time, ILIM switch and resistors, hold-off capacitor, SW amendments

Status: Draft. Record of decisions that the owner (Ben Spoor) confirmed in the working session of 2026-11-05, as told to the assistant by the calling agent.
They are **Proposed amendments only**. Nothing here is Approved or Accepted, and no Approved or Draft requirement text was changed. Only "Proposed amendment" paragraphs, Draft test case outlines, one Proposed deviation and one Open risk were added.
Traces: SYS-020, HW-010, SW-005, SW-006, SW-007, SW-009, TC-105, TC-109, TC-210, RISK-044, RISK-045, DEV-001, ADR-0010, ADR-0016.
Continues `owner-decisions-2026-11-05.md`. Where an earlier proposal differs (ILIM resistor values, capacitor set), the new Proposed text of HW-010 says that it replaces those items.
Nothing here was run on the bench or in firmware. Numbers marked "calculated" come from the existing scripts `hw/kicad/spike-gate/sim/ilim_steps.py` and `holdoff_cap.py` (unchanged), called with the new values.

## 1. Decisions

| # | Decision | Where recorded | Evidence | Open or bench check |
|---|---|---|---|---|
| 1 | SYS-020: relax the time to the raised limit from [1] s to [2] s, measured from VBUS applied | SYS-020 Proposed amendment; SW-005 Proposed amendment | `analysis-sw005-holdoff-timing.md` P1: worst case 1222 ms (specified window) | TC-020 and TC-105 bench time |
| 2 | ILIM select switch: TMUX1101DCKR (LCSC C2673506) for Q2 and Q3, with a bench check and a deviation for the 3V3-off condition. Fallback TS5A3166DBVR (C353035) | HW-010 Proposed amendment (a), (e); DEV-001 (Proposed); RISK-045 (new, Open) | `analysis-ilim-switch-replacement.md` section 6 and addendum A.5 (verdict: open, not closed by design) | TC-210 point (d); stock and Extended-part fee not checked |
| 3 | ILIM resistors, 0.1 % 0603: step 1 47.0 kohm; step 2 56.9 kohm; step 3 27.7 kohm (owner decision of 2026-11-06, replacing the 56.2 kohm and 27.4 kohm + 301 ohm set of 2026-11-05, which stays as the sourcing fallback). **56.9 k and 27.7 k at 0.1 % 0603 are unsourced** (`stock-check-ilim-holdoff.md`); confirm before ordering | HW-010 Proposed amendment (b) | Section 2 below (calculated) | TC-210 point (b); stock of 56.9 k and 27.7 k NOT confirmed |
| 4 | Hold-off capacitor: 220 + 220 + 100 + 68 nF C0G 5 % in parallel; window 205.9 to 560.6 ms; bench check | HW-010 Proposed amendment (c), (d); TC-210 | Section 3 below (calculated) | TC-210 point (a); availability of the 68 nF C0G not checked |
| 5 | All SW-005, SW-006, SW-009 fixes drafted as Proposed amendments (P1 to P6 of `analysis-sw005-holdoff-timing.md`; section 6 of `zephyr-usb-console-and-gpio-pull-facts.md`); SW-007 gets one definition | SW-005, SW-006, SW-007, SW-009 Proposed paragraphs; TC-105, TC-109, TC-210 outlines | The two reports named | Owner approval of each; [X] ms of SW-009 open |

## 2. ILIM limits with the new values (calculated)

Updated 2026-11-06 for the owner decision of 47.0 / 56.9 / 27.7 kohm (recomputed with `ilim_steps.py`). The 2026-11-05 values (56.2 kohm; 27.4 kohm + 0.301 kohm; the sourcing fallback) are given in the last paragraph of this section.

Inputs: R_ILIM1 47.0 kohm, R_ILIM2 56.9 kohm, R_ILIM3 27.7 kohm, tolerance 0.1 % (all in the same direction), Rds 0 to 9.5 ohm (TMUX1101 maximum at 85 C), leakage 0.2 nA per off switch at 1.0 V (ASSUMED ILIM voltage), TPS2553 equations of SLVS841G. Values in mA, minimum to maximum.

| State | Result | Number to meet | Margin |
|---|---|---|---|
| Step 1 | 504.2 to 616.6 | at most 623 (no minimum, owner decision of the first record) | 6.4 mA to the maximum |
| Step 2 | 929.6 to 1085.9 | window 850 to 1150 (proposed) | 79.6 mA low side, 64.1 mA high side |
| Step 3 | 1381.2 to 1566.7 | 1366 to 1577 | 15.2 mA and 10.3 mA |
| Q2 and Q3 both on | 1812.0 to 2014.0 | above the ceiling | prevented by the exclusive gate (HW-010 earlier proposal) |

Sourcing fallback (2026-11-05 set, calculated then): 47.0 / 56.2 / 27.4 kohm + 301 ohm gives step 1 504.2 to 616.6 mA, step 2 934.9 to 1091.7 mA, step 3 1381.2 to 1566.6 mA, both on 1817.4 to 2019.5 mA. Without the 301 ohm, 27.4 kohm alone gives a step 3 maximum of 1576.8 mA (margin 0.2 mA), which is why the pair exists. 56.9 k and 27.7 k at 0.1 % 0603 have no confirmed LCSC/JLCPCB source (only 0.5 % found; `stock-check-ilim-holdoff.md`), so they must be confirmed before ordering. With the TS5A3166 fallback (20 nA, Rds 1.5 ohm) the step 1 maximum is 617.7 mA and step 3 maximum 1567.1 mA, so the fallback keeps the numbers while the 3V3 is on; powered off it does not (5 uA breaks them, `analysis-ilim-switch-replacement.md` section 5). Leakage budget per off switch for these values: 118 nA at 1.0 V.
Not modelled: temperature coefficient and ageing of the resistors, layout leakage, the real ILIM voltage.

## 3. Hold-off window (calculated)

220 + 220 + 100 + 68 nF = 608 nF, 5 % per part, C0G temperature term over -55 to 125 C, TPS3840 constants k_min 357.6 kohm and k_max 875.6 kohm (`datasheet-evidence-supervisor.md`, A6): **205.9 to 560.6 ms**, which agrees with the owner figure. With the 0.6 % allowance of the earlier N4 report the window is 205.2 to 562.2 ms. Both are inside [200] to [600] ms. The minimum margin over the typical CC debounce (133 ms) is 72.9 ms; the maximum debounce is not found. Ageing, DC bias and leakage of C0G are taken as 0 (not checked).

## 4. New documents and records

- DEV-001 in `docs/standards/deviations.md`: TMUX1101 signal pin above VDD + 0.5 V while 3V3 is below about 0.5 V (Proposed, prototype only). It is the first entry of the register; the next free number is DEV-002.
- RISK-045 in `docs/risk/risk-register.md` (Open). Check made: RISK-027 (limit band), RISK-028 (rail), RISK-042 and RISK-044 (gate) do not cover the 3V3-off condition of the ILIM node, so a new entry was added; the next free number is RISK-046.
- TC-105, TC-109 and TC-210: "Proposed procedure outline" lines added; "Procedure: TBD" stays until approval.

## 5. Open points and what was not run

- Nothing was measured, simulated or built; no firmware exists. No test was run.
- The ILIM pin voltage (1 V), the 3V3 ramp (regulator not chosen), the TMUX1101 behaviour above VDD + 0.5 V and its signal-pin ESD structure are unknown (DEV-001 evidence is TC-210 point (d)).
- Stock and price at LCSC/JLCPCB of C2673506 (Extended part, per-type fee), of the 68 nF C0G are not checked. The 0.1 % 0603 56.9 k and 27.7 k have no confirmed source (`stock-check-ilim-holdoff.md`); the fallback 56.2 k, 27.4 k and 301 ohm parts are listed there, live stock not checked.
- The part change on a safety-relevant limit needs an ADR-0016 or ADR-0010 amendment; none was written. The owner decides.
- SW-009 [X] ms has no derivation (rail hold-up not measured). The Zephyr Kconfig symbols were not verified by a build.
- TC-106, TC-107 and TC-020 have no new outline; their behaviour follows from the SW-006, SW-007 and SYS-020 proposals and needs an update at approval.
- The schematic and generator values in `hw/` were not changed (CLAUDE.md rules 1 and 12: only Approved requirements, no hand edits of CAD files).
- No statement of compliance is made. SYS-020 is in the safety category, so the owner reviews all of these changes before approval.
