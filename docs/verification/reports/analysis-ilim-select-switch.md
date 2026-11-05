# Analysis: ILIM select switch candidates (replacement for 2N7002 Q2, Q3)

Status: desk research from vendor datasheets and web listings. Nothing was measured, simulated or built. Nothing here is approved, and no compliance is claimed.
Traces: HW-010 (limit numbers), ADR-0010, ADR-0016, SW-009, RISK-027. Follows `analysis-ilim-steps.md` (leakage budget and the 2N7002 addendum).
Vendor datasheets are linked, not committed (ADR-0015 item 8). Local copies are kept outside the repository.

## 1. Problem and requirement on the switch

Per `analysis-ilim-steps.md`: R_ILIM 47.0 / 56.9 / 27.7 kohm at 0.1 %, ILIM node about 1 V, off-state leakage budget about **118 nA per off switch at 1.0 V (94 nA at 0.8 V, 142 nA at 1.2 V)** up to 70 degC. The 2N7002 (Microchip DS20005797A) specifies IDSS only at VDS = 60 V (1 uA at 25 degC, 500 uA at 125 degC) and Rds(on) only at 5 V and 10 V. The datasheet therefore cannot show the budget.
On-resistance only needs to be known to a few hundred ohm (57 kohm branch). The control must be fully on at about 2.4 V minimum drive.
ASSUMPTION: the select gates are 3V3 74LVC outputs at about 2.9 V loaded, as stated in the task. I did not re-read the N1/N2 readback analysis, so the readback effect in section 4 is stated for the interface only.

## 2. Candidates

All values read from the datasheet unless marked. "Meets 118 nA" is judged by the datasheet limit at the stated temperature, with the test voltage near the 1 V node.

| # | Part | Maker | Datasheet (rev) | Off leakage (spec) | On-resistance (spec) | Package | Stock / price | Meets 118 nA at 70 degC by datasheet? |
|---|------|-------|-----------------|--------------------|----------------------|---------|---------------|-----------------------------------------|
| 1 | **TMUX1101** (active high; TMUX1102 is the active-low twin) | Texas Instruments | [SCDS410D, Mar 2019, rev Feb 2024](https://www.ti.com/lit/ds/symlink/tmux1101.pdf) | VDD 3.3 V, switch off, VD/VS = 3 V/1 V: IS(OFF), ID(OFF) max **0.05 nA at 25 degC, 0.2 nA at -40 to 85 degC**, 0.9 nA to 125 degC | VDD 3.3 V, VS 0 V to VDD, ISD 10 mA: max 8.8 ohm (25 degC), 9.5 ohm (to 85 degC) | TMUX1101: DCK SC70-5. TMUX1102: DBV SOT-23-5 | LCSC C2673506 (TMUX1101DCKR) seen as out of stock, about 1.16 USD per piece in a search snippet; date unknown. Not checked directly | **Yes**, with about 500-fold margin (0.2 nA at 85 degC) |
| 2 | **TS5A3166** | Texas Instruments | [SCDS186E, Feb 2005, rev Feb 2018](https://www.ti.com/lit/ds/symlink/ts5a3166.pdf) | V+ 3 V to 3.6 V, off, VNO 1 V / VCOM 3 V: INO(OFF), ICOM(OFF) max **2 nA at 25 degC, 20 nA over -40 to 85 degC** | V+ 3 V, ICOM 100 mA: ron max 1.4 ohm (25 degC), 1.5 ohm (full) at VNO 2 V; peak 1.5 / 1.7 ohm | SOT-23-5 (DBV), SC70-5 (DCK), DSBGA | LCSC C353035 (DBV) and C133819 (DCK). Search snippets conflict (0 vs 814 in stock, about 0.17 USD); not checked directly | **Yes**, 20 nA at 85 degC is 5.9 times below budget |
| 3 | SN74LVC1G66 | Texas Instruments | [SCES323R, Jun 2001, rev Sep 2025](https://www.ti.com/lit/ds/symlink/sn74lvc1g66.pdf) | IS(off) max **+/-1 uA over temperature** (+/-0.1 uA at 25 degC), tested at rail voltages and VCC 5.5 V | ron max 15 ohm at VCC 3 V, IS 24 mA; peak 25 ohm | SOT-23-5, SC70-5, SOT-5x3 | Not checked | **No** (1 uA over temperature is 8.5 times the budget; only 25 degC value 0.1 uA is below) |
| 4 | BSS806N (MOSFET example) | Infineon | Infineon sheet not read. A third-party copy ([Diotec](https://diotec.com/tl_files/diotec/files/pdf/datasheets/bss806n.pdf)) shows IDSS max 1 uA at VDS 20 V, VGS 0 V | 1 uA max at 20 V, 25 degC per that copy (not verified against Infineon) | Rds(on) typ 57 mohm at 2.5 V per distributor listing (sources disagree: 41 to 82 mohm) | SOT-23-3 | Not checked | **No.** Rds at 2.5 V is specified, but the leakage ceiling is still 1 uA at 25 degC and no hot or 1 V value is given |
| 5 | 2N7002 (baseline) | Microchip | DS20005797A (2018) | 1 uA at 60 V, 25 degC; 500 uA at 125 degC | 7.5 ohm max at 5 V, 10 V; none at 3 V | SOT-23-3 | Not checked | **No** (see `analysis-ilim-steps.md` addendum) |

Finding: small-signal MOSFETs in general specify IDSS only as a high-voltage ceiling of 0.1 to 1 uA at 25 degC. My search found no SOT-23 MOSFET that guarantees a leakage below 118 nA at about 1 V and 70 degC. I read only one example (item 4, secondary copy). This is a search result, not proof that none exists. Analog switch ICs are the class that specifies leakage at a low signal voltage and at hot temperature.

## 3. Compare candidates 1 and 2

| Aspect | TMUX1101 (DCK) / TMUX1102 (DBV) | TS5A3166 |
|--------|----------------------------------|----------|
| Leakage margin at 85 degC | 0.2 nA vs 118 nA | 20 nA vs 118 nA |
| Ron | up to 9.5 ohm | up to 1.7 ohm; both negligible against 57 kohm (0.02 % of the branch) |
| Control thresholds at 3.3 V supply | VIH min 1.35 V, VIL max 0.8 V (VDD 3.3 V +/-10 %) | VIH min 2.0 V, VIL max 0.8 V (V+ 3 V to 3.6 V) |
| Drive margin at 2.9 V gate level | 1.55 V over VIH | 0.9 V over VIH; thin if the 3V3 rail droops to 3.0 V and the gate output sags |
| Active level | TMUX1101 high; TMUX1102 low | High (IN) |
| Power-off pin condition | Abs. max: VS, VD must stay at or below VDD + 0.5 V. No powered-off leakage spec | INO(PWROFF) at V+ = 0: max 1 uA at 25 degC and 5 uA full range at VNO 0 to 3.6 V |
| Supply leakage | IDD 3 nA typ, 1 uA max over temperature | Not extracted |
| Package fit | SC70 only for the active-high part | SOT-23-5, same footprint family as common logic |

## 4. Circuit changes a candidate causes

Common to both analog switches (ASSUMPTIONS, to be checked against the schematic):

1. **Gate drive.** The MOSFET gate load (about nA) is replaced by the control input (TMUX1101 SEL: +/-0.005 uA at 25 degC, +/-0.06 uA hot; TS5A3166: 2 nA to 20 nA). The 74LVC1G output drives the control pin directly, no level shifting. The 3V3 rail must be wired to VDD/V+ with a 0.1 uF decoupling capacitor. The 74LVC output and the switch supply should be the same rail, so the gate high level tracks VDD.
2. **ILIM node connection.** The ILIM node goes to one switch pin, the R_ILIM2 or R_ILIM3 branch to the other (bidirectional). The switch pin voltage (about 1 V) sits inside 0 to VDD.
3. **Fail-safe default.** Neither datasheet puts a pull resistor on the control pin. TMUX1101's "fail-safe logic" only means SEL may be driven before VDD; it does not define an open input. Add a pull-down (for example 100 kohm) at each SEL/IN so an open or tri-stated gate output leaves the switch off, which is step 1 (lowest limit). With the active-low TMUX1102, use a pull-up instead and invert the firmware polarity. A pull-down of 100 kohm loads the 74LVC by under 30 uA at 2.9 V.
4. **Unpowered 3V3.** If VBUS powers the TPS2553 while the 3V3 rail is down (cold start, brown-out, reset), the ILIM node (about 1 V) is above VDD = 0 V. TMUX1101: absolute maximum VS <= VDD + 0.5 V is exceeded, with no spec for the clamp current; TS5A3166 specifies up to 1 uA (25 degC) and 5 uA (full range) in that state. Either case adds current to ILIM and shifts the limit upward; with the switch closed state undefined at VDD = 0, a branch could also conduct through the ESD structure. **This is the main new risk against the MOSFET.** A 2N7002 with its gate pulled low is off at any rail. It needs checking against the rail-sequencing in ADR-0016 and the hold-off analysis; I did not do that check. A series resistor does not fix it (it would change the ILIM total).
5. **Readback.** I did not read the readback circuit. If the readback senses the select gate nets, nothing changes for candidate 1 or 2 as the control pin stays at the same nets, except the added pull-down shifts a high-impedance readback divider (check the divider against 100 kohm). If readback senses the drain side of Q2/Q3 (the branch node), that node now floats to the ILIM level through the switch when off and follows ILIM when on; unchanged in function, but the leakage budget in section 2 then also applies to the readback load.
6. **Count and BOM.** Two SOT-23 FETs (2N7002) become two 5-pin switch ICs, or one dual part (not researched; for example a dual SPST would save board area). Cost per part is about 10 times higher (see section 2, price unverified).

## 5. Recommendation

**TMUX1101 (DCK, SC70-5) on 3V3, with a 100 kohm pull-down on SEL**, subject to the unpowered-rail check in 4.4 and to the owner accepting SC70 and the stock risk.

Reasons:
- It is the only candidate whose datasheet guarantees leakage near the 1 V node at hot temperature (0.2 nA to 85 degC, VD/VS = 3 V/1 V at VDD 3.3 V), by a margin of about 500 against the 118 nA budget. This closes the open decision 5 of `analysis-ilim-steps.md` without a bench measurement.
- The control thresholds (1.35 V / 0.8 V) work directly from the 74LVC gate with 1.5 V margin at 2.9 V. TS5A3166 has 0.9 V margin and its 20 nA limit still passes.
- Ron (up to 9.5 ohm) is irrelevant against 57 kohm.

Fallbacks: TS5A3166DBVR (SOT-23, meets the budget with 5.9 times margin, easier to source at LCSC, but 2.0 V VIH and a specified powered-off leakage of up to 5 uA); or keep the 2N7002 and bench-measure ILIM at 70 degC (cheapest part, no datasheet guarantee, and the margin of leakage on a 1 uA ceiling is already 8.5 times over).
Rejected: SN74LVC1G66 (1 uA over temperature), MOSFET swap to a logic-level part (leakage still given only as a 1 uA ceiling at 25 degC in the one sheet read).

An ADR is needed before a change: it is a hard-to-reverse part change on a safety-relevant limit (HW-010, RISK-027). The owner decides; I did not edit the ADR.

## 6. Assumptions and not verified

- **Not verified**: LCSC/JLCPCB stock and price (search snippets only; conflicting for TS5A3166, TMUX1101DCKR seen out of stock); whether C2673506 is the SC70 TMUX1101; JLCPCB basic/extended status; Infineon's own BSS806N datasheet; a dual-switch alternative; the exact 3V3 rail minimum and the gate level under load.
- **Not run**: no SPICE, no bench, no ILIM loop check. The leakage numbers are datasheet limits, not measured. Datasheet leakage is specified with VD/VS = 3 V/1 V (TMUX1101) and VNO 1 V / VCOM 3 V (TS5A3166), that is 2 V reverse across the open switch, not 1 V to ground; the ILIM node actually sees about 1 V across the open switch, which is lower stress, so the limit is expected to hold (ASSUMPTION).
- The 70 degC limit is covered by the 85 degC column of each datasheet (interpolation not needed, values are maxima over the range).
- Powered-off behaviour of TMUX1101 is not specified in the sheet; this is the open item for the owner.
- Local copies of the three datasheets are in `/home/ben/Programming/busy-light-datasheets/` (outside the repository).
