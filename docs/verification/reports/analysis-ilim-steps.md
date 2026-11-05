# Analysis: TPS2553 current-limit steps (R_ILIM1..3) against HW-010

Status: calculation from datasheet equations and stated assumptions. Nothing here was measured, simulated in SPICE or run on hardware. Nothing is approved by this report.
Traces: HW-010 (limit numbers), SYS-020, ADR-0010 (E1 to E4, open points 1 and 2; Accepted/owner-decided points are not changed here), ADR-0016, RISK-027.
Script: `hw/kicad/spike-gate/sim/ilim_steps.py` (deterministic, prints the tables below). Regression test: `hw/kicad/spike-gate/tests/test_ilim_steps.py`.

## 1. Result in short

1. **ADR-0010 arithmetic error.** The ADR table lists a step 1 maximum of 623 mA for R1 = 46.4 kohm with a 1 % resistor. The datasheet equation gives 623 mA only for the exact value; with the resistor at -1 % it gives 629 mA. The HW-010 number 623 mA, copied from that table, is therefore not met by 46.4 kohm 1 %.
2. **No E96 1 % choice meets HW-010.** The search over E96 and E192 at 1 % finds no triple that meets the step 1 maximum (623 mA), the step 1 minimum (500 mA, from the ADR table) and the top step window (1366 to 1577 mA) together. The top step window is the exact width of the equation band plus 1 % resistor tolerance (ratio 1.155), so it has zero margin before the MOSFET and the E-series grid are added.
3. **One combination meets all four numbers: E192, 0.1 %, R_ILIM1 = 47.0 kohm, R_ILIM3 = 27.7 kohm** (R_ILIM2 = 56.9 kohm for the assumed middle step). The margin is thin (4 to 15 mA, 0.7 % relative at worst) and only holds if the off-state leakage of each 2N7002 is below about 100 nA at the ILIM voltage.
4. Per the task rule ("edit only with margin"), **the generator values stay `tbd`**. The owner decision is in section 7.

## 2. Sources and assumptions

| Item | Value | Label |
|---|---|---|
| IOSmax = 22980 / R^0.94, IOSnom = 23950 / R^0.977, IOSmin = 25230 / R^1.016 (mA, R in kohm); they include temperature and process, not the external resistor tolerance | TPS2552/53 SLVS841G, equations (1) to (3), recommended RILIM 15 to 232 kohm (1 % resistor) | datasheet (local PDF), read |
| Table points (min/nom/max): 15 kohm 1610/1700/1800 (-40 to 105 C); 20 kohm 1200/1295/1375 (-40 to 125 C); 49.9 kohm 475/520/565; 210 kohm 110/130/150 | SLVS841G section 6.5 | datasheet, read |
| Equations against table (script, "cross check"): min within 1 %; max 1802 vs 1800, 1375 vs 1375, **582 vs 565 at 49.9 kohm**, 151 vs 150; nom 1699 vs 1700, 1283 vs 1295, 525 vs 520 | | derived |
| The equations are used as the design envelope. At 49.9 kohm the table maximum is 3 % tighter than the equation, but the table has no point near 47 kohm or 17.4 kohm, so it cannot be used there | | decision of this analysis |
| Middle step target: **not stated in ADR-0010 or HW-010.** The ADR table only says "for a 1.0 A class value" (59.0 kohm example). Assumed here: nominal 1000 mA, window 850 to 1150 mA | | **ASSUMPTION** (owner to set) |
| Step 1 minimum 500 mA | ADR-0010 table column "min at or above 500 mA". HW-010 states only the start value [500] mA and the 623 mA maximum | ADR, not in HW-010 text |
| 2N7002 Rds(on): 0 to 15 ohm in series with R_ILIM2/3 (conservative for 3.3 V gate drive; a usual datasheet value is 7.5 ohm max at Vgs 5 V) | no 2N7002 datasheet is stored in the repository | **ASSUMPTION** |
| 2N7002 off-state leakage: 1 uA per MOSFET (the usual IDSS max at Vds 60 V, 25 C), also 0.1 uA and 10 uA as sensitivities. Hot leakage is higher and is not a datasheet number here | | **ASSUMPTION** |
| ILIM regulation voltage: 1.0 V (0.8 and 1.2 V as sensitivity). Not found in the SLVS841G text read. Used only to turn leakage current into a conductance | | **ASSUMPTION** |
| Resistor tolerance is initial tolerance applied to all resistors in the same direction (worst case); temperature coefficient, ageing and PCB leakage are not modelled | | assumption |
| Step definitions: step 1 = Q2, Q3 off; step 2 = Q2 on; step 3 = Q3 on, Q2 off (ADR-0010 table). Firmware state for step 3 is not fixed in a requirement | | assumption |

## 3. Method

Total ILIM resistance = R_ILIM1 in parallel with each switched-on branch (R_ILIM2/3 plus Rds). Minimum current: all resistors +tol, Rds 15 ohm, IOSmin. Maximum current: all resistors -tol, Rds 0, IOSmax, plus the leakage of every off MOSFET as a conductance leak/V_ILIM. Nominal: exact resistors, Rds 7.5 ohm, IOSnom. Rds is 0.03 % of the 57 kohm branch; the effect on the step 3 minimum is below 1 mA (test `test_rds_has_negligible_effect`). The leakage is the dominant MOSFET term.

## 4. Candidate A: E192, 0.1 %: R_ILIM1 47.0 kohm, R_ILIM2 56.9 kohm, R_ILIM3 27.7 kohm

No leakage:

| State | Rtot kohm (hi/nom/lo) | min mA | nom mA | max mA | HW-010 number |
|---|---|---|---|---|---|
| Step 1 (Q2, Q3 off) | 47.05 / 47.00 / 46.95 | 504.2 | 556.8 | 616.6 | max <= 623, min >= 500 (ADR) |
| Step 2 (Q2 on) | 25.77 / 25.74 / 25.71 | 929.5 | 1002.6 | 1085.9 | none (assumed 850 to 1150) |
| Step 3 (Q3 on) | 17.45 / 17.43 / 17.41 | 1381.0 | 1467.3 | 1566.7 | 1366 to 1577 |
| Q2 and Q3 both on | 13.36 / 13.34 / 13.33 | 1811.8 | 1905.0 | 2014.0 | none: above 1577 |

Margins to the numbers: step 1 min 4.2 mA, step 1 max 6.4 mA, step 3 min 15.0 mA, step 3 max 10.3 mA.

With leakage per off MOSFET (maximum values): 0.1 uA gives step 1 max 622.0, step 3 max 1569.2; **1 uA gives step 1 max 670.9 and step 3 max 1592.3, both over the limit.** The leakage budget per off MOSFET is 118 nA at V_ILIM 1.0 V (94 nA at 0.8 V, 142 nA at 1.2 V).

## 5. Candidate B: E96, 1 %: R_ILIM1 47.5 kohm, R_ILIM2 56.2 kohm, R_ILIM3 27.4 kohm (best E96 try, no leakage)

| State | min mA | nom mA | max mA | Against HW-010 |
|---|---|---|---|---|
| Step 1 | 494.3 | 551.0 | 615.7 | max met (7.3 mA), min 5.7 mA below 500 |
| Step 2 | 921.0 | 1002.5 | 1095.1 | |
| Step 3 | 1372.7 | 1471.6 | 1584.5 | min met, **max 7.5 mA over 1577** |
| Q2 and Q3 both on | 1804.9 | 1914.7 | 2041.1 | |

The ADR reference (46.4 / 28.0 kohm, 1 %, ideal switch) gives step 1 506/564/629 and step 3 1366/1465/1577 mA: step 3 has zero margin and step 1 exceeds 623.

## 6. Findings and risks

- F1: the 623 mA figure in ADR-0010 and HW-010 is the nominal-resistor maximum, not the 1 % band edge. With E96 1 % no value gives both "min >= 500" and "max <= 623" (47.5 kohm: 494 to 616; 46.4 kohm: 506 to 629). Only the E192 value 47.0 kohm at 1 % reaches 500.0 to 622 mA, with no margin.
- F2: at the top step a 1 % resistor cannot meet 1366 to 1577 mA (window 15.4 % wide, band needs about 15.5 % before grid and Rds).
- F3: the state "Q2 and Q3 both on" gives up to about 2014 mA (candidate A). HW-010 gates each select output separately; a firmware or fault state with both on at a 1.5 A source exceeds the 1577 mA ceiling and the advertised current. Needs either a SW-009 rule "never both", a gate that makes the states exclusive, or the top step defined as both on (different R3). Not decided here.
- F4: leakage of the off 2N7002 acts on step 1 with two off MOSFETs (9 % of conductance at 1 uA and 1 V). The true leakage at Vds near 1 V is expected to be far below the Vds 60 V datasheet figure, but no source for that was read.
- F5: E192 0.1 % thin-film parts cost more and may not be basic parts at JLCPCB (not checked). 27.7 and 56.9 kohm are E192 values only; the E192 table was generated by the IEC 60063 rule in the script (the three values 47.0, 27.7 and 56.9 are standard table entries by my reading; check against the vendor list).

## 7. Open decisions for the owner

1. Accept 0.1 % E192 parts (candidate A), or widen HW-010: for 1 % E96 parts, step 1 min ~494 mA (below the 500 mA firmware budget; RISK-028) and top step max ~1585 mA (above the 1500 mA ceiling already accepted as up to 1577 mA by ADR-0010 open point 2).
2. Middle step target (assumed 1000 mA nominal) and whether the middle step is kept at all.
3. Whether the step 1 minimum is required to be >= 500 mA (ADR table) or only the maximum (HW-010 text).
4. How to exclude the "both on" state (section 6, F3).
5. Source for 2N7002 leakage at low Vds and Rds at 3.3 V: read the datasheet of the chosen part, or bench-check ILIM leakage at 70 C.

## 8. Not checked

No SPICE model of the TPS2553 ILIM loop; no bench measurement (TC-210 would record the limits per step); no 2N7002 datasheet read; ILIM voltage unknown; resistor temperature coefficient and ageing; layout leakage (flux, humidity) at the 21 uA ILIM current; interaction of the 500 mA firmware budget with the minimum limit (RISK-028); JLCPCB stock and price of the resistors; E192 table cross-check against a vendor list.

## Addendum: 2N7002 vendor datasheet read (2026-11-05)

Source: Microchip 2N7002, DS20005797A (2018), DC electrical characteristics table, page 2 (supplied by the owner; kept outside the repository, ADR-0015 item 8). It replaces the web copy of another vendor's sheet used in `analysis-n1-n2-readback-backfeed.md` for the 2N7002 threshold; the values agree (VGS(th) 1 V min, 2.5 V max).

| Item | Value in the datasheet | Conditions | Effect on the ILIM analysis |
|------|------------------------|------------|------------------------------|
| VGS(th) | min 1 V, max 2.5 V; temperature change max -5.5 mV/degC | VGS = VDS, ID = 250 uA | Gate drive is about 2.9 V (N1 analysis), so the margin over the 2.5 V maximum is about 0.4 V at 25 degC. Rds(on) at that overdrive is not guaranteed. |
| IDSS | max 1 uA at 25 degC; max 500 uA at 125 degC | VGS = 0 V, VDS = maximum rating (60 V); 125 degC row at 0.8 x rating | The leakage at the ILIM node (about 1 V) is **not specified**. The guaranteed maximum is far above the 118 nA budget, so the datasheet cannot prove that step 1 and the top step stay inside the HW-010 limits. No value at 70 degC is given. |
| RDS(ON) | max 7.5 ohm at VGS = 5 V, ID = 50 mA; 7.5 ohm at VGS = 10 V, ID = 500 mA; +1 %/degC max | 25 degC | No value at VGS = 3.3 V or below. The 57 k branch makes even tens of ohms negligible (below 1 mA); the unguaranteed overdrive matters more. |
| IGSS | max +/-100 nA | VGS = +/-20 V, VDS = 0 V | Not relevant to the ILIM node. |

Conclusion (analysis only, nothing measured): the leakage budget of about 118 nA per off MOSFET cannot be shown with this part from its datasheet. The typical leakage at 1 V is probably far lower than the 1 uA ceiling, but that is not a guarantee. Options for the owner: choose a part that specifies leakage at low VDS (or a lower IDSS ceiling), keep the 2N7002 and measure at 70 degC on the prototype, or place the select MOSFET so that its leakage does not add to the ILIM node. Not run: a search for a replacement part.
