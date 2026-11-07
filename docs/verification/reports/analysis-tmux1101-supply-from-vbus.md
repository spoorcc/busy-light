# Analysis: remove the TMUX1101 over-voltage by supplying the ILIM switches from VBUS_IC (HW-010, ADR-0016, DEV-001, RISK-045)

Status: Draft. Desk analysis from datasheet text and the spike netlist. No bench, no SPICE, no build. Nothing here is Approved.
Answers owner decision 3 of `docs/journal/2026-11-07-rv010-owner-decisions.md` ("remove it by design").
Continues `analysis-ilim-switch-replacement.md` (addendum A, the 3V3-off window).

## Problem
The TPS2553 (U7) takes IN and EN from VBUS_IC (spike netlist, `layout_full.py`: U7 pins 1 and 3 on VBUS_IC). 3V3 is derived from its output. So at every plug-in the ILIM node is regulated (about 1 V, assumed) while 3V3, the supply of the TMUX1101 switches U14 and U15, is still below about 0.5 V. The TMUX1101 absolute maximum for a signal pin is VDD + 0.5 V (datasheet section 6.1), and the datasheet states no behaviour above it.

## Facts read (TI TMUX1101 datasheet, copyright 2024 revision, stored as `tmux1101.pdf` in the datasheet directory)
| Item | Value | Section |
|---|---|---|
| Supply VDD, recommended operation | 1.08 to 5.5 V | 6.3 |
| VDD absolute maximum | -0.5 to 6 V | 6.1 |
| Signal pin absolute maximum | -0.5 V to VDD + 0.5 V | 6.1 |
| Off leakage IS(OFF), ID(OFF), VDD = 5 V | 0.08 nA at 25 degC, 0.3 nA to 85 degC, 0.9 nA to 125 degC | 6.5 (5 V table) |
| Off leakage, VDD = 3.3 V (the figure used so far) | 0.2 nA to 85 degC | 6.6 |
| Logic input SEL, VDD = 5 V table | VIH 1.49 V minimum, VIL 0.87 V maximum | 6.5 |
| Logic input SEL, VDD = 3.3 V table | VIH 1.35 V minimum, VIL 0.8 V maximum | 6.6 |
| SEL fail-safe | SEL may be driven up to 5.5 V regardless of VDD, also with VDD = 0 V | 8.3.4 |
| Polarity | TMUX1101 is on when SEL is logic 1 | description |

## Options
| Option | Effect on the abs. max. exceedance | Evidence | Verdict |
|---|---|---|---|
| A. Supply U14 and U15 (VDD) from VBUS_IC | Removed by the ordering: the ILIM node exists only while VBUS_IC is above the TPS2553 UVLO (2.35 to 2.45 V), so VDD is then at least 2.35 V and VDD + 0.5 V is at least 2.85 V against an ILIM node of about 1 V (margin 1.85 V; still 0.85 V if the ILIM node were 2 V). | Datasheet text for every number; netlist for the ordering | **Recommended** |
| B. Series resistor or clamp on the signal pin | Not removed, only limited. The clamp structure is not stated in the datasheet, so the limit cannot be computed. | None | Rejected |
| C. Fallback TS5A3166 | Not removed. Its powered-off leakage is stated (1 uA at 25 degC, 5 uA full range) and breaks the step 1 and step 3 margins in the same window (`analysis-ilim-switch-replacement.md`). | Datasheet | Rejected |
| D. Keep the TMUX1101 on 3V3 with DEV-001 | Exceeded at every power-up, effect unknown | None | Rejected by the owner decision of 2026-11-07 |

## Check of option A against the other states
| State | VDD (VBUS_IC) | ILIM node | SEL | Result |
|---|---|---|---|---|
| Plug-in, VBUS_IC rising | at least 2.35 V once the TPS2553 regulates | about 1 V (assumed) | low (gate enable low, 100 kohm pull-down, hold-off) | signal inside VDD + 0.5 V; switches off, step 1 |
| Normal run, VBUS 5 V | 5 V (up to 5.5 V) | about 1 V | 3V3 logic from the gate, high (above 1.49 V) or low | inside rating; leakage 0.3 nA to 85 degC (budget 118 nA per off switch) |
| VBUS present, 3V3 absent | 5 V | about 1 V | low (pull-down; the fail-safe input allows any level up to 5.5 V) | off, step 1; inside rating |
| VBUS gone, 3V3 present (D+ back-feed, VBUS_IC about 2.7 V) | about 2.7 V | 0 V (TPS2553 off) | gate output low | inside rating; within the 1.08 to 5.5 V operating range |
| VBUS drops out | falls with VBUS_IC and its decoupling capacitor, which discharges only through the switch supply current | falls with the TPS2553 (UVLO) | low | VDD stays at or above the ILIM node during the fall (the decoupling capacitor holds VDD up); to confirm with the scope in TC-210 |
| Hot-plug surge on VBUS_IC | up to the TVS clamp (TVS1 on VBUS_IC in the spike) | n/a | n/a | the 6 V absolute maximum of VDD needs a TVS clamp voltage under 6 V at the surge current. **TVS1 is a placeholder; the part is not chosen** (`part-evidence-fill-report.md`), so this cannot be checked from a datasheet yet. It is a selection requirement for TVS1 and applies equally to the other parts on VBUS_IC (TUSB321 VDD, TPS3840). Clamp voltages of common 5 V TVS diodes at surge are often above 6 V (a general expectation, not read here) |

## Effects on the numbers
- Off leakage at VDD = 5 V is 0.3 nA to 85 degC against 0.2 nA used so far: the step windows move by far less than 0.01 mA (the leakage budget is 118 nA per switch at 1 V ILIM).
- On-resistance at 5 V is not higher than at 3.3 V (the datasheet states it falls with supply), so the step 3 maximum used so far (Rds 9.5 ohm) stays conservative.
- SEL is driven from 74LVC gates on 3V3. A high of about 3.0 V or more is above the 5 V table VIH of 1.49 V (margin about 1.5 V). A low from the gates and the 100 kohm pull-down is below VIL 0.87 V.
- Cost: one net change (VDD pins of U14 and U15 from VBUS_IC instead of 3V3), one 100 nF decoupling capacitor at the switch supply. No new part.

## What this does not prove
- The 1 V on the ILIM pin is an assumption; the margin holds up to about 2 V.
- The TVS clamp voltage against the 6 V rating of VDD is not checked.
- The behaviour during VBUS dropout (VDD against the ILIM node) is a first-order argument and needs the scope record of TC-210.
- No bench record exists. DEV-001 and RISK-045 stay open until TC-210 (d) shows the ordering on the prototype.

## Recommendation
Option A. Amend ADR-0016 Amendment 2 and the HW-010 Proposed revision (switch supply from VBUS_IC, VBUS_IC to VDD with a 100 nF capacitor, TVS check). DEV-001 would be withdrawn when the owner approves the change and TC-210 (d) shows no exceedance.
