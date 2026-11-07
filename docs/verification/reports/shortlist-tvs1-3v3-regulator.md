# Shortlist for TVS1 and the 3V3 regulator (HW-010, HW-012)

- **Date:** 2026-11-07. **Author:** assistant. **Status:** Draft for the owner's choice. No part is chosen and nothing is Approved.
- **Evidence level:** the TUSB321, TPS3840 and TLV757P datasheets were read as text (tables named below, TI documents fetched 2026-11-07); the TVS clamp figures and the AP2112K figures are web search snippets. No live JLCPCB stock was read, nothing was measured. Every number below is marked *snippet* or *memory* and has to go through HW-012 (`hw/evidence/`) before a part is chosen.

## 1. TVS1 on VBUS_IC

**Requirement (HW-010 criterion 4, ADR-0016 Amendment 2):** the clamp voltage at the surge current stays below the 6 V absolute maximum of the TMUX1101 supply pin (VDD abs max 6 V, recommended 1.08 to 5.5 V, TMUX1101 datasheet SCDS410D, *snippet*). It applies equally to the other parts on VBUS_IC. Read on 2026-11-07, table 6.1 Absolute Maximum Ratings: **TUSB321 VDD 6 V maximum** (so it has the same 6 V problem as the switch; its CC1/CC2 also 6 V), **TPS3840 VDD 12 V maximum** (recommended 1.5 to 10 V, no problem).

**Finding: a plain 5 V TVS cannot meet this requirement as written.** A TVS with a working voltage near 5 V clamps well above 6 V at any real surge current. Snippets for SOD-323 parts:

| Part | Clamp figure | Source status |
|---|---|---|
| Applied Power PESD5V0S (C712143) | 8 V at 1 A, 13 V at 8 A | snippet, hard-to-read PDF |
| Nexperia PESD5V0V1BA | 12.5 V at 4.8 A (8/20 us) | snippet |
| CESD5V0D3 | 10 V at 1 A, 15 V at 25 A | snippet |
| Nexperia PESD5V0S1BA | 14 V, 12 A peak rating | snippet |

All are above 6 V. A TVS cannot clamp lower without conducting at the normal 5 V rail. The requirement therefore needs a different mechanism, not a better TVS.

**Options (the owner chooses):**

| # | Option | Impact | Risk |
|---|---|---|---|
| T1 | Keep a standard 5 V TVS on VBUS and protect the switch supply pin with a series resistor ([100] ohm) and the 100 nF capacitor, plus a local 5.1 V zener at the pin. The switch supply draws about nA, so the resistor drops nothing at DC. | one resistor and one SOD-123 zener; no part change | the zener and resistor values are not derived; the TUSB321 VDD (6 V maximum, read) needs the same protection or a lower surge; TPS3840 (12 V maximum, read) does not |
| T2 | Relax the wording of HW-010 criterion 4: the clamp is measured on the bench at the real surge (IEC 61000-4-5 is not required for this product class, to be checked with `regulatory-check`) and only the measured peak at the switch pin has to be below 6 V | no new part | a TVS alone will still show 8 to 13 V at a 1 A to 8 A surge; this passes only if the cable and trace impedance limit the surge, which is not shown |
| T3 | Use the fallback switch TS5A3166 | none | its supply rating is not read; likely similar; the fallback also needs its own check |

**Recommendation: T1**, and apply it to the TUSB321 VDD as well (TPS3840 is not affected); add both to TC-210 and the evidence files. T2 trades a design measure for a measurement that a TVS will probably fail. Only the owner decides, and T1 changes HW-010, so it needs your approval of the amendment.

## 2. 3V3 regulator (U8)

**Load (from `spike-7-5-power-budget-paper.md`):** TX peak 350 mA plus 28 mA CPU is 378 mA; with 20 % margin 567 mA; the module datasheet asks for a supply that delivers at least 500 mA. The regulator needs a rating of at least about 600 mA. Input is the +5V rail (4.5 to 5.5 V assumed after the TPS2553). Regulator quiescent current and the other 3V3 loads are not in those numbers.

| # | Part | Key facts | Source status | Concern |
|---|---|---|---|---|
| R1 | Diodes AP2112K-3.3TRG1 (SOT-25, LDO) | 600 mA continuous minimum; dropout 250 mV typ, 0.4 V max at 600 mA; Iq 55 uA typ, 80 uA max; enable pin | snippets (Diodes page, Farnell, Digi-Key); the dropout table in the excerpt was garbled | the margin over the 567 mA case is 33 mA; the LCSC number C51118 that I tried could not be matched; JLCPCB stock and Basic/Extended status not read |
| R2 | TI TLV75733P (TLV757P family, fixed 3.3 V LDO, SOT-23-5) | read, table 5.1 and 5.3 of SBVS322C (March 2024): output current 0 to 1 A; VIN 1.45 to 5.5 V recommended, 6.0 V absolute maximum; dropout 300 to 425 mV max at 1 A for a 3.3 V output (DBV; 450 mV DYD); ground current 25 uA typ at 25 degC; current limit 1.2 to 1.78 A; RθJA 60.3 degC/W (DYD package) and 92.5 to 100.8 degC/W in the other columns | datasheet text read; which RθJA column belongs to the DBV package was not resolved; LCSC number, stock and Basic/Extended status not read | VIN maximum 5.5 V is the rail's top edge (4.5 to 5.5 V assumed); the 6 V absolute maximum is again the VBUS_IC surge question if +5V is not protected by the TPS2553; heat: see below |
| R3 | A small buck converter module-free design (3.3 V, 1 A) | lower heat | *memory*, not searched | inductor, layout, EMC noise near the antenna and a second DFx path; too heavy for the first board |

At 5 V in and 3.3 V out the LDO loss at 567 mA is about 0.96 W (1.7 V x 0.567 A); at 378 mA about 0.64 W. With RθJA of 60.3 degC/W (best case in the datasheet) the junction rises about 58 K at 0.96 W, and about 39 K at 0.64 W; with the higher RθJA values it is 89 to 97 K. Added to a 35 degC ambient and a closed housing, the junction approaches the 125 degC limit in the worst case. That heat adds to the housing thermal case of ADR-0011 (PETG, closed) and is not in HW-013 yet. This favours either a part with a thermal pad or a buck, and the heat should be counted before the choice.

**Recommendation: R2 (TLV75733P) only if the heat is accepted; otherwise R3.** R1 has 33 mA of margin over the 567 mA case. R2 has the current margin, but its loss is up to about 1 W in a closed PETG shell with a junction margin that is not comfortable at the worst-case RθJA; the load is mostly short TX bursts, so the average is lower, but no duty cycle is in the budget (this is a gap in `spike-7-5-power-budget-paper.md`). The owner chooses between: R2 with a duty-cycle estimate added to HW-013, or a small buck (R3) that moves the heat out of the shell at the cost of layout and noise near the antenna. I still need the LCSC number and live stock of the chosen part, and the HW-012 entry (`hw/evidence/parts/`), which I did not create because no part is chosen.

## Not done
Datasheets read for TUSB321, TPS3840 and TLV757P only; the TVS and AP2112K figures are snippets; no stock read, no measurement, no simulation, no HW-012 entry created. No `hw/` file changed.
