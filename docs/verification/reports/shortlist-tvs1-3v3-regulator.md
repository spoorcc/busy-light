# Shortlist for TVS1 and the 3V3 regulator (HW-010, HW-012)

- **Date:** 2026-11-07. **Author:** assistant. **Status:** Draft for the owner's choice. No part is chosen and nothing is Approved.
- **Evidence level:** web search snippets only. No datasheet PDF was opened in full, no live JLCPCB stock was read, nothing was measured. Every number below is marked *snippet* or *memory* and has to go through HW-012 (`hw/evidence/`) before a part is chosen.

## 1. TVS1 on VBUS_IC

**Requirement (HW-010 criterion 4, ADR-0016 Amendment 2):** the clamp voltage at the surge current stays below the 6 V absolute maximum of the TMUX1101 supply pin (VDD abs max 6 V, recommended 1.08 to 5.5 V, TMUX1101 datasheet SCDS410D, *snippet*). It applies equally to the other parts on VBUS_IC (TUSB321 VDD, TPS3840; their ratings are not read).

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
| T1 | Keep a standard 5 V TVS on VBUS and protect the switch supply pin with a series resistor ([100] ohm) and the 100 nF capacitor, plus a local 5.1 V zener at the pin. The switch supply draws about nA, so the resistor drops nothing at DC. | one resistor and one SOD-123 zener; no part change | the zener and resistor values are not derived; the other VBUS_IC parts (TUSB321, TPS3840) need the same check |
| T2 | Relax the wording of HW-010 criterion 4: the clamp is measured on the bench at the real surge (IEC 61000-4-5 is not required for this product class, to be checked with `regulatory-check`) and only the measured peak at the switch pin has to be below 6 V | no new part | a TVS alone will still show 8 to 13 V at a 1 A to 8 A surge; this passes only if the cable and trace impedance limit the surge, which is not shown |
| T3 | Use the fallback switch TS5A3166 | none | its supply rating is not read; likely similar; the fallback also needs its own check |

**Recommendation: T1**, and add the same check for TUSB321 VDD and TPS3840 VDD to TC-210 and to the evidence files. T2 trades a design measure for a measurement that a TVS will probably fail. Only the owner decides, and T1 changes HW-010, so it needs your approval of the amendment.

## 2. 3V3 regulator (U8)

**Load (from `spike-7-5-power-budget-paper.md`):** TX peak 350 mA plus 28 mA CPU is 378 mA; with 20 % margin 567 mA; the module datasheet asks for a supply that delivers at least 500 mA. The regulator needs a rating of at least about 600 mA. Input is the +5V rail (4.5 to 5.5 V assumed after the TPS2553). Regulator quiescent current and the other 3V3 loads are not in those numbers.

| # | Part | Key facts | Source status | Concern |
|---|---|---|---|---|
| R1 | Diodes AP2112K-3.3TRG1 (SOT-25, LDO) | 600 mA continuous minimum; dropout 250 mV typ, 0.4 V max at 600 mA; Iq 55 uA typ, 80 uA max; enable pin | snippets (Diodes page, Farnell, Digi-Key); the dropout table in the excerpt was garbled | the margin over the 567 mA case is 33 mA; the LCSC number C51118 that I tried could not be matched; JLCPCB stock and Basic/Extended status not read |
| R2 | A 1 A class fixed 3.3 V LDO in SOT-23-5 or SOT-223 (for example TLV75733P class or AMS1117-3.3 class) | more current margin | *memory*, not searched | not checked at all; an AMS1117 class part has high dropout loss at 5 V and poor quiescent current; the TLV75733 class needs its rating and stock read |
| R3 | A small buck converter module-free design (3.3 V, 1 A) | lower heat | *memory*, not searched | inductor, layout, EMC noise near the antenna and a second DFx path; too heavy for the first board |

At 5 V in and 3.3 V out the LDO loss at 567 mA is about 1.0 W (1.7 V x 0.567 A); at 378 mA about 0.64 W. That heat adds to the housing thermal case of ADR-0011 (PETG, closed) and is not in HW-013 yet. This favours either a part with a thermal pad or a buck, and the heat should be counted before the choice.

**Recommendation: R2 class, read before choosing.** R1 as drawn has too little margin and adds about 0.6 to 1.0 W inside a PETG shell. I will read two 1 A candidates in full, with their LCSC stock, and write the HW-012 entries before you pick. Only the owner chooses.

## Not done
No datasheet opened in full, no stock read, no measurement, no simulation. No `hw/` file changed.
