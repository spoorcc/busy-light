# Datasheet evidence for the inverter (SN74LVC1G04)

- **Status:** Draft
- **Date:** 2026-11-04
- **Author:** Claude. Not reviewed. Nothing here is Approved or Accepted. No part is chosen.
- **Related:** `docs/verification/reports/datasheet-evidence-gate-logic.md`, spike `docs/verification/reports/spike-hw-gate-fragment.md`
- **Labels:** each fact is marked **read** (read in the datasheet text on 2026-11-04) or **not found**. The PDF was downloaded to a scratch folder and is not committed (ADR-0015: vendor datasheets are linked, not committed). Page numbers are the printed page numbers of the datasheet.

## Source
- **S1** TI SN74LVC1G04 "Single Inverter Gate", document number SCES214AF, April 1999, revised October 2025: https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf (PDF metadata: "Rev. AF"; the file served has 47 pages including the package appendix).
- Not obtained: second-source datasheets (for example Nexperia 74LVC1G04). Not searched.

## Question
VCC = 3.3 V rail. Input pulled up to a 5 V rail (VBUS 4.5 to 5.5 V). Either rail can be present without the other (VCC = 0 V with 5 V on the input, and the reverse).

## Facts (S1)
| # | Item | Fact | Status |
|---|------|------|--------|
| 1 | Pins, DBV (SOT-23-5) and DCK (SC70-5) | Pin Functions table, Section 4 (p. 3): NC = 1, A = 2, GND = 3, Y = 4, VCC = 5. One column covers DBV, DCK and DRL. Other packages differ: DSF/DRY VCC = 6, NC = 1 and 5 (DSF/DRY); YZP A = B1, GND = C1, Y = C2, VCC = A2; DPW A = 2, GND = 3, Y = 4, VCC = 5, NC = 1 | read |
| 2 | VCC operating range | 1.65 to 5.5 V; data retention only 1.5 V (5.3 Recommended Operating Conditions, p. 5). Description: "designed for 1.65V to 5.5V VCC operation" (p. 1) | read |
| 3 | VCC absolute maximum | -0.5 to 6.5 V (5.1, p. 4) | read |
| 4 | Input voltage, recommended | VI 0 to 5.5 V (5.3, p. 5). The row carries no VCC condition. Features (p. 1): "Inputs accept voltages up to 5.5V allowing down translation to VCC". Section 7.3 (p. 10): "Inputs accept voltages to 5.5V" | read |
| 5 | Input voltage, absolute maximum | VI -0.5 to 6.5 V (5.1, p. 4). Footnote (2): the negative limits may be exceeded if the current ratings are observed. Input clamp current IIK -50 mA for VI < 0 | read |
| 6 | 5 V input at VCC = 3.3 V | Allowed: 5.5 V is inside the recommended VI range (item 4) and VCC = 3.3 V is inside the recommended VCC range (item 2). Margin to absolute maximum: 1.0 V (6.5 - 5.5) | read |
| 7 | Ioff / partial power down, statement | Features (p. 1): "Ioff supports live-insertion, partial-power-down mode, and back-drive protection". Section 7.1 (p. 10): "fully specified for partial-power-down applications using Ioff. The Ioff circuitry disables the outputs, preventing damaging current backflow through the device when it is powered down." Section 7.3 (p. 10): "Ioff feature allows voltages on the inputs and outputs, when VCC is 0V." | read |
| 8 | Ioff limit and test conditions | Electrical Characteristics 5.5 (p. 6): Ioff, test condition "VI or VO = 5.5V", VCC = 0 V, max +/-10 uA for both -40 to 85 C and -40 to 125 C. No MIN or TYP given. So the input at 5.5 V with VCC = 0 V is a tested condition | read; typ not found |
| 9 | VIH / VIL at VCC = 3 to 3.6 V | VIH min 2 V, VIL max 0.8 V (5.3, p. 5). At VCC = 4.5 to 5.5 V: VIH min 0.7 x VCC, VIL max 0.3 x VCC. Also 2.3 to 2.7 V: 1.7 V / 0.7 V; 1.65 to 1.95 V: 0.65 x VCC / 0.35 x VCC | read |
| 10 | Input leakage | II, A input, VI = 5.5 V or GND, VCC = 0 to 5.5 V: max +/-5 uA, both temperature ranges (5.5, p. 6). No TYP given. Note the VCC range includes 0 V | read; typ not found |
| 11 | Supply current | ICC at VI = 5.5 V or GND, IO = 0, VCC 1.65 to 5.5 V: max 10 uA. Delta ICC (one input at VCC - 0.6 V, VCC 3 to 5.5 V): max 500 uA (5.5, p. 6). Delta ICC does not describe an input at 5 V with VCC = 3.3 V; the datasheet gives no row for that case | read; the 5 V-input-at-3.3 V supply current not found |
| 12 | Behaviour / output state at VCC = 0 | Only the qualitative statement of item 7: Ioff circuitry "disables the outputs". Absolute Maximum 5.1 (p. 4) lists a separate VO row "applied to any output in the high-impedance or power-off state": -0.5 to 6.5 V. **No logic level, output impedance or leakage value for Y at VCC = 0 is stated beyond Ioff (VO = 5.5 V, max +/-10 uA).** The Function Table (7.4, p. 10) is H -> L and L -> H and is given for powered operation. The word "undefined" is not used for the VCC = 0 output; it appears only in Section 8.5.1 (p. 12) about floating unused inputs | read; output level at VCC = 0 not found |
| 13 | Floating input | Footnote to 5.3 (p. 5) and 8.5.1 (p. 12): unused or all inputs must be held at VCC or GND, not left floating | read |
| 14 | Output voltage limit when powered | VO (high or low state) -0.5 to VCC + 0.5 V (5.1, p. 4) | read |
| 15 | Input transition rate | VCC = 3.3 V +/-0.3 V: max 10 ns/V; 5 V +/-0.5 V: 5 ns/V (5.3, p. 5) | read |
| 16 | Output drive and VOL / VOH at VCC = 3 V | VOL max 0.4 V at 16 mA, 0.55 V at 24 mA; VOH min 2.4 V at -16 mA, 2.3 V at -24 mA; VOL max 0.1 V and VOH min VCC - 0.1 V at 100 uA (5.5, p. 6) | read |
| 17 | tpd A to Y | CL = 15 pF, -40 to 85 C (5.6, p. 6): VCC = 3.3 V +/-0.3 V min 0.7, max 3.3 ns; 5 V +/-0.5 V min 0.7, max 3.1 ns. No typical value | read; typ not found |
| 18 | Input capacitance | Ci 3.5 pF at VCC = 3.3 V, VI = VCC or GND (5.5, p. 6) | read |
| 19 | Temperature, ESD | TA -40 to 125 C (5.3, p. 5). HBM +/-2000 V, CDM +/-1000 V (5.2, p. 4) | read |

## Consequences for the question (read values only; no conclusion on part choice)
- 5 V rail present, VCC = 3.3 V: input at up to 5.5 V is within the recommended VI range (items 4, 6).
- 5 V rail present, VCC = 0 V: the input at 5.5 V is a tested Ioff condition, limit +/-10 uA (item 8). A pull-up resistor from the 5 V rail would then feed at most that leakage into the part; the datasheet gives no input-clamp or protection-diode current for this case beyond item 5.
- 3.3 V rail present, 5 V rail absent: the input sits at the pull-up node voltage, which is below VIL max 0.8 V only if the node is pulled low by something else. Without a source the input floats (item 13). That is a circuit matter, not a datasheet fact.
- The output level of Y with VCC = 0 is not specified (item 12). Any downstream logic that needs a defined level at VCC = 0 needs its own pull resistor or a part with a stated behaviour. Not read in S1.
- Input VIH at 3.3 V is 2 V min; a 5 V-derived divider or pull-up must be checked against 2 V / 0.8 V (item 9) in the worst case.

## Not run
No simulation. No second-source datasheet. Typical curves in Section 5.11 (Typical Characteristics, p. 7) were not read for this question.
