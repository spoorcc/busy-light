# Analysis: replacement for the 2N7002 ILIM select switches (Q2, Q3) with stated leakage

Status: Draft. Desk research from vendor datasheets. Nothing was measured, simulated in SPICE or built. Nothing here is Approved or Accepted, and no requirement text is changed.
Traces: HW-010 (limit numbers), ADR-0016, ADR-0010, SW-009, RISK-027. Answers owner decision 5 of `owner-decisions-2026-11-05.md`. Extends `analysis-ilim-select-switch.md` (earlier desk study) and `analysis-ilim-steps.md` (leakage budget and 2N7002 addendum).
Datasheets are kept outside the repository in `/home/ben/Programming/busy-light-datasheets/` (ADR-0015 item 8). Page numbers are PDF page numbers of those copies.
Calculation: the existing `hw/kicad/spike-gate/sim/ilim_steps.py` functions, called with other leakage and Rds values. The script is unchanged.
Origin: written by a research subagent; saved by the main session because the subagent could not write files. Figures are as reported by that subagent and are not re-checked against the datasheets by the main session.

## 1. Requirement on the switch
From `analysis-ilim-steps.md`: R_ILIM 47.0 / 56.9 / 27.7 kohm (0.1 %), ILIM node about 1 V (ASSUMPTION, not found in the SLVS841G text read). The leakage budget is **118 nA per off switch at 1.0 V** (94 nA at 0.8 V, 142 nA at 1.2 V). Needed: leakage stated at about 1 V and at 70 degC, fully on from a 3V3 74LVC gate (about 2.9 V loaded; 2.5 V ideally), SOT-23 or smaller, LCSC number.

## 2. Result in short
1. No N-MOSFET was found that states leakage at low drain voltage (BSS138N ceiling 0.1 uA at 60 V, 25 degC; see section 3).
2. TI TMUX1101 (0.2 nA max to 85 degC) and TI TS5A3166 (20 nA max to 85 degC) state off-leakage near the 1 V node. Both are JLCPCB Extended.
3. Recommendation: TMUX1101DCKR (LCSC C2673506), with one open condition (section 4). Fallback: TS5A3166DBVR (C353035).
4. Stock and price at LCSC/JLCPCB could not be verified (section 7).

## 3. Candidates
Values read from the datasheet unless marked.

| # | Part, LCSC no., JLCPCB class | Package | Off leakage (spec) | Conditions | On-resistance | Control level, 3V3 supply | Datasheet |
|---|---|---|---|---|---|---|---|
| 1 | **TMUX1101DCKR**, C2673506, Extended (class seen on the twin TMUX1102DCKR page C2673555; the C2673506 JLCPCB page was not fetched) | SC70-5 (DCK) | IS(OFF), ID(OFF) max **0.05 nA at 25 degC, 0.2 nA at -40 to 85 degC, 0.9 nA to 125 degC** | VDD 3.3 V, off, VD 3 V / VS 1 V and swapped (Sec. 6.6, p. 6) | max 8.8 ohm at 25 degC, 9.5 ohm to 85 degC (ISD 10 mA) | VIH min 1.35 V, VIL max 0.8 V (p. 7) | TI SCDS410D, Feb 2024 |
| 2 | **TS5A3166DBVR**, C353035, Extended (JLCPCB page fetched) | SOT-23-5 (DBV) | INO(OFF), ICOM(OFF) max **2 nA at 25 degC, 20 nA at -40 to 85 degC** | V+ 3.6 V, VNO 1 V / VCOM 3 V and swapped (3.3 V table, p. 6) | ron max 1.4 ohm at 25 degC, 1.5 ohm full (V+ 3 V, ICOM 100 mA) | VIH min 2.0 V, VIL max 0.8 V (p. 6); 2.5 V supply table VIH 1.8 V | TI SCDS186E, Feb 2018 |
| 3 | **BSS138N** (Infineon), C94638 (C42410691 for the XTSA2 reel code; C42410691 seen as Extended, class of C94638 not shown) | SOT-23 | ID(off) max **0.1 uA at 25 degC, 5 uA at 150 degC** | **VDS 60 V**, VGS 0 V (p. 2). Nothing at 1 V or 70 degC | max 4.0 ohm at VGS 4.5 V, 30 mA (p. 2). **Nothing at 3.3 V or 2.5 V** | VGS(th) 0.6 / 1.0 / 1.4 V (p. 2) | Infineon Rev. 2.86, 2012-04-17 |
| 4 | BSS806N (comparison) | SOT-23 | IDSS max **1 uA at 25 degC, 100 uA at 150 degC** | VDS 20 V (p. 2) | max 57 mohm at 2.5 V, 82 mohm at 1.8 V | VGS(th) max 0.75 V | Infineon Rev. 2.3, 2011-07-11 |

BSS806N, BSS214NW and BSR202N (Infineon sheets read) all give IDSS max 1 uA at 25 degC. This closes the gap in `analysis-ilim-select-switch.md` row 4, which used a third-party copy. Not candidates. Also not candidates: SN74LVC1G66 (1 uA over temperature) and the 2N7002.

## 4. Comparison and circuit effects
| Aspect | TMUX1101DCKR | TS5A3166DBVR | BSS138N |
|---|---|---|---|
| Leakage stated near 1 V node, to 85 degC | 0.2 nA | 20 nA | not stated (60 V ceiling only) |
| Margin to 118 nA | about 590 times | 5.9 times | 1.2 times at 25 degC and 60 V; hot not stated |
| Drive from 2.9 V gate | 1.55 V over VIH | 0.9 V over VIH | 1.5 V over VGS(th) max |
| Drive at 2.5 V gate | works (VIH 1.35 V) | only with its 2.5 V supply table; not on a 3.3 V supply | VGS(th) max 1.4 V; Rds not stated below 4.5 V |
| VDD = 0 V with ILIM node at 1 V | **not specified**; abs. max VS = VDD + 0.5 V (Sec. 6.1, p. 4) | **stated**: INO(PWROFF), ICOM(PWROFF) max 1 uA at 25 degC, 5 uA full range (p. 6) | gate low: off at any rail |
| Control input leakage | 5 nA, 50 nA hot (p. 7) | 2 nA, 20 nA hot (p. 6) | IGSS 10 nA |
| Package | SC70-5 | SOT-23-5 | SOT-23 |

Circuit changes for both analog switches (ASSUMPTIONS; schematic not re-read):
- Supply pin to 3V3 with 0.1 uF. The 74LVC output drives the control pin directly.
- 100 kohm pull-down on each control pin, so an open gate means off (step 1). Neither sheet defines an open control input. Check it against the N1/N2 readback divider (not re-read).
- The TMUX1101 control pin is fail-safe (Sec. 8.3.4, PDF p. 17: it may be driven before VDD). That says nothing about the signal pins.

**Open item for the TMUX1101.** If VBUS powers the TPS2553 while 3V3 is below about 0.5 V, the ILIM node (about 1 V) exceeds the absolute maximum VDD + 0.5 V, and the sheet gives no leakage or state. The effect on the limit is unknown, not zero. It matters only if the TPS2553 is enabled in that state. Whether the hold-off (ADR-0016, `analysis-n4-holdoff-capacitor.md`) keeps EN low until 3V3 is valid was not re-checked. Settle it by a gate-design argument or a bench ILIM measurement with 3V3 off. Otherwise use the TS5A3166.

## 5. Effect on the ILIM step margins
Candidate A (47.0 / 56.9 / 27.7 kohm, 0.1 %), V_ILIM 1.0 V. Limits in mA, min to max. Leakage per off switch raises the maximum; Rds raises the minimum. Margins are to HW-010: step 1 max 623, step 1 min 500 (ADR-0010 table), step 3 1366 to 1577. Step 2 has no requirement.

| Case | Step 1 | Step 2 | Step 3 | Margin s1 max | Margin s3 max | Margin s1 min | Margin s3 min |
|---|---|---|---|---|---|---|---|
| Ideal, no leakage | 504.2 to 616.6 | 929.5 to 1085.9 | 1381.0 to 1566.7 | 6.4 | 10.3 | 4.2 | 15.0 |
| TMUX1101: 0.2 nA, Rds 9.5 ohm | 504.2 to 616.6 | 929.6 to 1085.9 | 1381.2 to 1566.7 | 6.4 | 10.3 | 4.2 | 15.2 |
| TS5A3166: 20 nA, Rds 1.7 ohm | 504.2 to 617.7 | 929.6 to 1086.4 | 1381.5 to 1567.2 | 5.3 | 9.8 | 4.2 | 15.5 |
| BSS138N, 100 nA assumed at 1 V (assumes the 60 V, 25 degC ceiling bounds 1 V; not a datasheet statement; no hot value) | 504.2 to 622.0 | 929.5 to 1088.5 | 1381.0 to 1569.2 | 1.0 | 7.8 | 4.2 | 15.0 |
| 1 uA (2N7002 / BSS806N ceiling), comparison | 504.2 to 670.9 | 929.5 to 1112.2 | 1381.0 to 1592.3 | -47.9 | -15.3 | 4.2 | 15.0 |
| TS5A3166 powered off, 1 uA at 25 degC | 504.2 to 670.9 | 929.6 to 1112.2 | 1381.5 to 1592.3 | -47.9 | -15.3 | 4.2 | 15.5 |
| TS5A3166 powered off, 5 uA full range | 504.2 to 885.4 | 929.6 to 1216.7 | 1381.5 to 1694.5 | -262.4 | -117.5 | 4.2 | 15.5 |

Findings:
- With either analog switch the stated leakage costs at most 1.1 mA of step 1 maximum margin (TS5A3166) and nothing measurable with the TMUX1101. The thin 4 to 15 mA margins stay set by resistor and TPS2553 equation tolerances.
- The Q2-and-Q3-on state is unchanged (2014 mA max). Gate logic must still exclude it (owner decision 4).
- BSS138N leaves 1.0 mA at the step 1 maximum on an unverified 25 degC number. Log-interpolating its two points gives about 0.4 uA at 70 degC and 60 V. That is arithmetic of the analyst, not a datasheet value, and it is for 60 V, not 1 V. It shows the ceiling cannot prove the budget, not that the part fails.
- The powered-off rows apply only if the TPS2553 is enabled while the switch supply is 0 V.
- Budget bisection gives 94 nA at 0.8 V and 142 nA at 1.2 V, same as `analysis-ilim-steps.md`. TMUX1101 and TS5A3166 stay inside the budget over that range.

## 6. Recommendation
Use **TMUX1101DCKR (C2673506)** for Q2 and Q3: active high, 3V3 supply, 100 kohm pull-down on each control pin. Conditions:
1. Settle the open item in section 4 (3V3 off with ILIM above 0.5 V) by a gate-design argument or a bench check.
2. The owner accepts SC70-5 and an Extended part. The JLCPCB per-type fee for Extended parts was not checked.

Reasons: it is the only candidate with leakage stated at about 1 V and over temperature that leaves the HW-010 margins unchanged (about 590 times below budget). It works from a 2.5 V gate. Its Rds is irrelevant against the 56.9 kohm branch.

Fallback: TS5A3166DBVR (C353035). It is a SOT-23-5, leakage is 20 nA (5.9 times margin), and powered-off behaviour is stated. Costs: VIH 2.0 V (0.9 V margin from 2.9 V), and the 5 uA powered-off leakage breaks the step margins if the TPS2553 is enabled with 3V3 absent.

Not recommended: BSS138N or any MOSFET found. A MOSFET stays an option only with a bench ILIM leakage measurement at 70 degC (decision 5 bench check).

A part change on a safety-relevant limit needs an ADR or an ADR-0016 amendment. The owner decides. No ADR was edited.

## 7. Not verified, not run
- **Stock and price (LCSC, JLCPCB): not verified.** The pages returned part number, package and (JLCPCB) the Extended label only. Earlier snippets (TS5A3166 at 0 stock, TMUX1101DCKR out of stock, about 1.13 to 1.16 USD) are undated. A search result shows TMUX1101DCKR at 10845 pieces at a non-LCSC distributor. That is not LCSC or JLCPCB stock.
- JLCPCB class Extended was seen on pages for TS5A3166DBVR (C353035), TMUX1102DCKR (C2673555) and BSS138NH6327XTSA2 (C42410691). TMUX1101DCKR (C2673506) and C94638 were not seen. Extended for TMUX1101DCKR is inferred from its twin.
- LCSC datasheet copies were not used. The part-to-sheet link rests on the manufacturer part numbers (TMUX1101DCKR C2673506, BSS138NH6327 C94638).
- The MOSFET search was not exhaustive. Read: Infineon BSS138N, BSS806N, BSS214NW, BSR202N and the Microchip 2N7002. Not read: Diodes DMN2004K and others (searched only). A CBI BSS123 LCSC listing was reported by a snippet as IDSS 10 nA at 20 V. The sheet could not be opened, and BSS123 is a 100 V part with higher VGS(th). Not verified.
- Leakage figures are limits at the listed test points (3 V / 1 V, so 2 V across the open switch), not 1 V to ground. The ILIM node sees about 1 V across the open switch (lower stress; ASSUMPTION).
- 70 degC is covered by the 85 degC column of each sheet.
- ILIM node 1.0 V, the 3V3 minimum and the gate level under load are assumptions.
- Not run: SPICE, bench, ILIM loop check, readback divider check against the pull-down, rail-sequencing check, regulatory check. A passive part swap is not expected to add a regulatory effect; this was not assessed.

## Addendum: 3V3-off sequencing of the ILIM node

Status: Draft. Desk analysis of the drawn schematic and datasheet text. Nothing was measured, simulated or built. Nothing here is Approved or Accepted. Sections 1 to 7 above are unchanged. This addendum answers the open item in section 4 (TMUX1101 abs. max. VS = VDD + 0.5 V; can the ILIM node be near 1 V while 3V3 is below about 0.5 V?). Traces: HW-010, ADR-0016, ADR-0010, SW-009, RISK-027.

### A.1 Sources
- `hw/kicad/spike-gate/src/layout_full.py` (generator of the full-board schematic; read in full): TPS2553 U7 pins IN and EN are both bound to net `VBUS_IC`; U7 OUT is `+5V`; regulator U8 IN is `+5V`, OUT is `+3V3`; `HOLD_OK` goes only to U3, U4 (gate ANDs, pin 6), U10 (buffer) and U5 (supervisor output). `HOLD_OK` is not connected to U7.
- `docs/verification/reports/spike-full-board-schematic.md` finding F6 (rail sequence) and F2/F3 (gate supply).
- `docs/decisions/ADR-0010-usb-input-current-limit.md`: "the switch must be on at power-up, with no help from the firmware"; "EN is pulled up to VIN"; rise time 0.7 to 1.5 ms (its E6, not re-read here).
- `docs/decisions/ADR-0016-independent-hardware-gate-for-high-current-step.md`, ADR-0009 (CC IC pull-ups): searched for 3V3, regulator, sequence and hold-off terms. They state no start-up order of 3V3. ADR-0016 holds the step 2/3 enables, not the TPS2553 enable.
- `analysis-n4-holdoff-capacitor.md`: this file only sets the hold-off delay (CT capacitor, 200 to 600 ms). It has no statement about the TPS2553 enable.
- `datasheet-evidence-inverter.md`, `datasheet-evidence-gate-logic.md`: 74LVC gate inputs tolerate 5 V with VCC = 0 V (Ioff, 10 uA max); the output level at VCC = 0 V is not specified (the outputs are disabled).
- TI TPS2553 SLVS841G (`/home/ben/Programming/busy-light-datasheets/tps2553.pdf`, text extracted): UVLO rising 2.35 to 2.45 V; EN thresholds 0.66 to 1.1 V; ton max 3 ms; section 8.5.1: "an internal regulation loop to provide a regulated voltage on the ILIM pin"; ILIM source current rating 0 to 1 mA; "ILIM must never be driven directly with an external signal".
- TI TMUX1101 SCDS410D (`tmux1101.pdf`): abs. max. VS or VD -0.5 V to VDD + 0.5 V (6.1); SEL is fail-safe (8.3.4). The text extract shows no statement of the signal-pin ESD structure, no leakage and no state for VS above VDD.

### A.2 Findings
1. **EN of the TPS2553 is not held low by anything.** EN is tied to VBUS_IC (same net as IN). The hold-off supervisor does not control it. The assumption in section 4 ("the hold-off keeps EN low until 3V3 is valid") is **false for the drawn design**. The hold-off acts only on the step 2 and step 3 gates (HOLD_OK into U3 and U4).
2. **3V3 cannot be valid before the TPS2553 is on.** 3V3 comes from the regulator, whose input is `+5V`, which is the TPS2553 output. So the chain is VBUS_IC -> TPS2553 (on at once, above UVLO, EN = IN) -> +5V -> regulator -> 3V3. An EN that waits for 3V3 would be circular and cannot be used.
3. **The ILIM pin is driven when the TPS2553 runs.** The datasheet says only that ILIM carries a regulated voltage in operation. It does not state the voltage value (the 1 V in section 1 stays an ASSUMPTION) and does not say whether ILIM is driven in UVLO. EN is never low in this design except for VBUS_IC below 0.66 V, so the "EN low" case is not a normal case here.
4. **The ILIM node reaches the switch pins in every switch state.** Each switch sits on the low side of R_ILIM2 or R_ILIM3 (the resistor connects the switch pin to the ILIM node). With the switch off, the switch signal pin sits at the ILIM node voltage through 56.9 or 27.7 kohm (an ASSUMPTION that Q2/Q3 are replaced one-for-one on the same pin; the schematic is not changed).
5. **The gate enables cannot be high before 3V3 is valid.** U3, U4 and U13 are supplied from 3V3, and a step enable needs the GPIO select (MCU on 3V3, plus R4/R5 pull-downs) and HOLD_OK (200 to 600 ms). At VCC = 0 V the gate output is disabled (level not specified); the 100 kohm pull-down on SEL, the TMUX1101 fail-safe SEL and the 10 kohm R2/R3 keep the switch off. The remaining issue is therefore the signal pin, not the control state.

### A.3 Sequencing table
V_ILIM is the assumed 1 V while the TPS2553 runs. VDD is the switch supply (3V3). "Margin" is VDD + 0.5 V minus V_ILIM at the switch pin (negative means above the abs. max.).

| Case | TPS2553 | ILIM node | Switch VDD (3V3) | Margin to VDD + 0.5 V | Result |
|---|---|---|---|---|---|
| VBUS first (normal plug-in; 3V3 can only come from VBUS) | On when VBUS_IC > UVLO (2.45 V max), EN = IN | About 1 V from the start of operation (assumed) | 0 V rising; reaches 0.5 V only after OUT, +5V and the regulator have started (order of ms: ton up to 3 ms, output rise 0.7 to 1.5 ms, regulator not chosen) | **About -0.5 V at VDD = 0, zero at VDD about 0.5 V** | **Exceeds the abs. max. for a short time at every power-up.** Duration not known. |
| Both together (hot plug, VBUS ramp with 3V3 following) | Same as above | Same | Same, lags VBUS_IC | Same | Same as VBUS first. This is the only real order. |
| Brown-out or VBUS dropout, then return | Off below UVLO (falling), on again at return | Falls with VBUS_IC (assumed), then 1 V again | 3V3 decays with the load on the output capacitors (F6: a short decay) | Positive while 3V3 is above V_ILIM - 0.5 V | Decay is safe; the return repeats the first row if 3V3 fell below about 0.5 V. |
| 3V3 first (5 V on TP1 only, or D+ back-feed M1) | IN = 0 V or about 2.7 V; with 0 V it is off | 0 V (R_ILIM1 to GND), or driven only if VBUS_IC > UVLO | Valid | Positive (1 V node, VDD about 3.3 V) | Not a stress case. Reverse leakage of U7 (IREV 0.01 to 1 uA) is not an ILIM issue. |
| Steady state, 3V3 valid | On | About 1 V | 3.3 V | +2.8 V | In specification. |

### A.4 Effect on the current limit during the window
The abs. max. is a stress rating, not a function limit. In the window of the first row the datasheet gives no state, no leakage and no clamp current for a signal pin above VDD. If the signal pin has an ESD clamp to VDD (not stated in the extracted text), the current into it is bounded by the series resistor: about (1.0 V - 0.6 V) / 56.9 kohm = 7 uA at most (ASSUMED 0.6 V clamp, not from a datasheet). That current is taken from the ILIM node and so raises the current limit. For comparison, the step 1 ILIM current is about 1.0 V / 47 kohm = 21 uA, so a few uA is a visible fraction. This was not quantified further, and it applies only while 3V3 is low, when the load on `+5V` is the output capacitors and the regulator input. The same window exists for the fallback TS5A3166, where the stated powered-off leakage (1 uA at 25 degC, 5 uA full range, section 4 and 5 rows) applies. So switching to the fallback does not remove the window; it replaces "not specified" with "stated, and breaks the step margins if enabled with 3V3 absent" (section 5).

### A.5 Verdict
**Open. Not closed by design.** The condition "ILIM node near 1 V while 3V3 is below about 0.5 V" occurs at every power-up by architecture, because the TPS2553 is enabled directly from VBUS_IC and 3V3 is derived from its output. The gate design (hold-off, AND gates) does not and cannot prevent it, and the earlier assumption that the hold-off holds EN low is not supported. Whether it is acceptable depends on three unknowns that this desk study cannot settle: (a) the ILIM pin voltage and when it appears (UVLO, soft start); (b) the 3V3 ramp (regulator not chosen); (c) the TMUX1101 behaviour with VS above VDD + 0.5 V (not specified).

Needs bench (proposed, not run): with a scope, record VBUS_IC, +5V, 3V3 and the ILIM node (one probe on the node, high impedance, not loading it) at plug-in and at VBUS dropout, for each build. Record time with 3V3 below 0.5 V and the peak of V_ILIM - 3V3. Measure the ILIM node current error in that window if feasible (the effect on the limit).

Options for the owner (no recommendation changed here; section 6 stands as written, condition 1 stays open):
1. Accept the TMUX1101 with a bench record of the window and a written deviation for a brief abs. max. exceedance. Weak: a rating exceeded at every power-up on a safety-relevant limit has no datasheet support.
2. Choose a switch with stated powered-off signal behaviour (TS5A3166 has it; its 1 to 5 uA leakage must be reviewed for the window) or another part found by a new search.
3. Add a series resistor in the switch signal path or a clamp only after the bench numbers exist. Not analysed.

### A.6 Not verified, not run
- No bench, no SPICE. ILIM pin voltage value and UVLO behaviour are not in the extracted SLVS841G text (the 1 V is an assumption carried from `analysis-ilim-steps.md`).
- Regulator is a placeholder (U8, part not chosen), so 3V3 ramp time and the start-up order inside the window are not known.
- ADR-0010 E6 (rise time 0.7 to 1.5 ms) was taken from the ADR and not re-read in the TPS2553 sheet (the sheet shows ton max 3 ms and a rise-time table).
- TMUX1101 signal-pin ESD structure: not found in the text extract; figures were not inspected.
- The generated sheet was read, not exported or re-run (no ERC, no netlist export). The schematic was not changed and a TMUX1101 is not drawn in it.
- Section A.4 numbers are first-order arithmetic with an assumed clamp voltage.
