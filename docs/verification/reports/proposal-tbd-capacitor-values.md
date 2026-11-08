# Proposal: values for the five "tbd" capacitors C2 to C6 (HW-014, HW-015, HW-016, HW-010)

- **Date:** 2026-11-08. **Author:** assistant. **Status:** Draft proposal; owner decisions of 2026-11-08 recorded at the end. Nothing Approved, nothing measured. HW-014 to HW-016 stay Draft.
- **Why:** finding 4 of `spike-fab-review.md` (the BOM cannot be ordered with tbd values).

## Facts used
| ID | Fact | Source |
|---|---|---|
| T1 | TLV757P input: 1 uF or larger; nominal and effective capacitance above 0.47 uF; nominal derating taken as 50 % | TLV757P SBVS322C, pin table note 1 and section 7.1.1 (text extracted from the PDF on 2026-11-08) |
| T2 | TLV757P output: recommended 1 to 200 uF; 0.47 uF or larger needed for stability; use X5R or X7R | same, recommended operating conditions table and section 7.1.1 |
| T3 | VBUS pin: 1.0 to 10.0 uF over 0 to 5.25 V | HW-015 (F8 of `analysis-5v-bulk-capacitance.md`) |
| T4 | +5V upper bound 104 uF (assumed start load 0.1 A, C_3V3 10 uF); 77 uF at 0.2 A | `bulk_cap_bounds.py`, run 2026-11-08 |
| T5 | Chip rule "10 uF before the chip" | `docs/process/hw-generated-design-guardrails.md` (Espressif hardware guideline, quoted there) |

## Proposal
| Ref | Net | Now | Proposed | Reason | Check still open |
|---|---|---|---|---|---|
| C2 | VBUS_IC | 1u tbd | 4.7 uF, X7R or X5R, rating 25 V or higher | 50 % derating at 5 V gives about 2.3 uF, tolerance 10 % still above 1.0 uF (T3). At 0 V the sum with C24 to C26 (3 x 100 nF) stays far under 10 uF; the TVS and U6 junction capacitance is not read. A higher rating leaves room for hot-plug overshoot (RV-013 finding 10, open). | DC-bias curve of the real part; TVS capacitance |
| C3 | +5V | 10u tbd | 10 uF, X5R or X7R, 10 V or higher | Output of the TPS2553, populated. About 5 uF effective at 5 V with the 50 % rule. | DC-bias curve; TPS2553 output-capacitor text not re-read |
| C4 | +5V | bulk tbd | Do not populate (spare, 1206). Value left to the bench test | HW-014 criterion 3 and HW-016: more capacitance is decided from prototype measurement. HW-016 asks for 2 spare footprints; the board has one (C4), so HW-016 is not met yet. | Owner: add a second spare footprint or relax HW-016 |
| C5 | +5V at U8 | tbd | 2.2 uF, X7R, 10 V or higher | T1 needs 1 uF nominal and above 0.47 uF effective. 1 uF at 50 % derating gives 0.5 uF, only 0.03 uF of margin before tolerance, so 1 uF is too tight. | DC-bias curve |
| C6 | +3V3 at U8 | tbd | 10 uF, X5R or X7R, 10 V or higher | T2 minimum is 1 uF; T5 asks 10 uF before the chip; the module has its own capacitors (not known). Within 200 uF. The C_max in T4 was computed with 10 uF here, so this is consistent. | DC-bias curve; Wi-Fi transmit peak on the bench |

## Not shown
No manufacturer part is chosen, so no effective capacitance is calculated from a DC-bias curve; the 50 % rule of the TLV757P datasheet is a general rule, not a curve. No simulation and no measurement. The footprint of C3 (0805 on the board, 0603 in the schematic, `footprint_symbol_mismatch` for C3 and C4) is not changed here. A 10 uF part in 0603 or 0805 depends on the part chosen.

## Decisions needed (owner)
1. Accept or change the five values above.
2. C4: keep one spare footprint, or add a second (HW-016).
3. Footprint of C3 and C4 (resolves the two remaining DRC mismatches).
After the decision: change the generator values and footprints, regenerate the schematic, run the checks, update this report.

## Owner decisions and result (2026-11-08)
Decisions: all five values accepted; a second spare footprint added; C3 0805 and C4 1206 (the board footprints; the schematic follows).
Result on the stored board (`src/pcb_spare_caps.py`, `layout_full.py`): values set; C32 added as a copy of C4 on the **bottom side** because the top side has no free place near U7 (silkscreen texts and copper): C32 is 24.1 mm from U7 pin 6, C4 is 8.2 mm, so the `within [5] mm` of HW-016 is **not met** by either spare (the owner can relax the number; both are on the +5V plane net). C4 and C32 are do-not-populate. Routing by `pcb_fix.py`: 1 via, 13.7 mm of track. Strict DRC: 0 failing classes, tolerated only courtyards_overlap 8 and items_not_allowed 1 (DEV-004); no footprint mismatch; fab-minimum check PASS (132 vias, ring at the minimum); power drops unchanged (13.5, 18.0, 22.7 mV); ERC 0. C32 has no silkscreen designator. Not done: DC-bias curves, any part number for C2 to C6 and the spares (MPN list), bench.
