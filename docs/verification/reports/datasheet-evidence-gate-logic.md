# Datasheet evidence for the gate logic parts (SN74LVC1G11, SN74LVC1G17)

- **Status:** Draft
- **Date:** 2026-11-04
- **Author:** Claude. Not reviewed. Nothing here is Approved or Accepted. No part is chosen.
- **Related:** HW-003, HW-010, spike `docs/verification/reports/spike-hw-gate-fragment.md`, `docs/verification/reports/cc-ic-datasheet-evidence.md`
- **Labels:** each fact is marked **read** (read in the datasheet text on 2026-11-04), **derived** (computed here from read values; the arithmetic is shown) or **not found**. The PDFs were downloaded to a scratch folder and are not committed (ADR-0015: vendor datasheets are linked, not committed). Page numbers are the printed page numbers of the datasheet.

## Sources
- **S1** TI SN74LVC1G11, SCES487I, September 2003, revised November 2024: https://www.ti.com/lit/ds/symlink/sn74lvc1g11.pdf (10 pages as served; "PRODUCTION DATA").
- **S2** TI SN74LVC1G17, SCES351Y, July 2001, revised October 2025: https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf (10 pages as served; "PRODUCTION DATA").
- Not obtained: Nexperia second-source datasheets (74LVC1G11, 74LVC1G17). Not searched.

## A) SN74LVC1G11, 3-input AND (S1)
| # | Item | Fact | Status |
|---|------|------|--------|
| 1 | Pinout DBV (SOT-23-6) and DCK (SC70-6) | Figure 4-1 (p. 3) and Table 4-1 (p. 3): A = 1, GND = 2, B = 3, Y = 4, VCC = 5, C = 6. DBV and DCK share one drawing and one pin column | read |
| 2 | Match with KiCad symbol (1=A, 3=B, 6=C, 4=Y, 2=GND, 5=VCC) | Matches the datasheet for every pin | read (comparison derived) |
| 3 | Supply range | Operating VCC 1.65 to 5.5 V; data retention only 1.5 V (Table 5.3, p. 4). Absolute maximum VCC -0.5 to 6.5 V (5.1, p. 4) | read |
| 4 | Input 5 V tolerance | "Inputs accept voltages to 5.5 V" (Features, p. 1). Recommended VI 0 to 5.5 V (5.3, p. 4), independent of VCC in that table. Absolute maximum VI -0.5 to 6.5 V (5.1, p. 4). Ioff: VI or VO = 5.5 V at VCC = 0 gives at most +/-10 uA (5.5, p. 5), so the input stays within the specification with the part unpowered | read |
| 5 | VIH / VIL at 3.3 V | VCC = 3 V to 3.6 V: VIH min 2 V, VIL max 0.8 V (5.3, p. 4). At VCC = 4.5 to 5.5 V: VIH min 0.7 x VCC, VIL max 0.3 x VCC | read |
| 6 | tpd, A, B or C to Y | CL = 15 pF, -40 to 85 C (5.6, p. 6): VCC = 3.3 V +/-0.3 V min 1.2 ns, max 4.1 ns; 5 V +/-0.5 V min 1 ns, max 3.1 ns. CL = 30/50 pF (5.7): 3.3 V 1.3 to 4.9 ns. -40 to 125 C (5.8): 3.3 V 1.3 to 6.2 ns. **No typical value is given** | read; typ not found |
| 7 | Input leakage | II, all inputs, VI = 5.5 V or GND, VCC 0 to 5.5 V: at most +/-5 uA (5.5, p. 5). No typical value | read |
| 8 | Output drive and VOL | VOL max 0.4 V at 16 mA and 0.55 V at 24 mA (VCC = 3 V); VOH min VCC - 0.1 V at 100 uA (5.5, p. 5) | read |
| 9 | Temperature and package | -40 to 125 C for all packages except DSBGA (-40 to 85 C) (5.3, p. 4). Orderables DBV and DCK listed Active (orderable table) | read |
| 10 | ESD | HBM +/-2000 V, CDM +/-1000 V (5.2, p. 4) | read |

## B) SN74LVC1G17, Schmitt buffer (S2)
| # | Item | Fact | Status |
|---|------|------|--------|
| 11 | Pinout DBV (SOT-23-5) and DCK (SC70-5) | Pin Functions table (p. 3): N.C. = 1, A = 2, GND = 3, Y = 4, VCC = 5. The DBV and DCK packages have 5 pins (not 6) | read |
| 12 | Match with KiCad symbol (2=A, 4=Y, 3=GND, 5=VCC, 1=NC) | Matches the datasheet for every pin | read (comparison derived) |
| 13 | Thresholds, -40 to 85 C and -40 to 125 C (Table 5-1, p. 6) | See the table below. **The columns MIN and MAX only are filled; the TYP columns are empty in the text.** The 25 C columns are empty. **There is no row for VCC = 5.0 V**; the rows are 1.65, 2.3, 3, 4.5 and 5.5 V | read; typ not found; 5.0 V row not found |
| 14 | Hysteresis (VT+ minus VT-) | 4.5 V: min 0.58, max 0.93 V. 5.5 V: min 0.69, max 1.04 V. 3 V: min 0.51, max 0.83 V (Table 5-1, p. 6) | read |
| 15 | Input leakage | II, A input, VI = 5.5 V or GND, VCC 0 to 5.5 V: at most +/-5 uA (Table 5-1, p. 6). No typical value | read |
| 16 | Input 5 V tolerance | "Inputs accept voltages to 5.5 V" (Features, p. 1). Recommended VI 0 to 5.5 V (5.3, p. 5). Absolute maximum VI -0.5 to 6.5 V (5.1, p. 4). Ioff at VI or VO = 5.5 V, VCC = 0: at most +/-10 uA | read |
| 17 | Output at 5 V into a 3.3 V-powered LVC input | Output in the high state: absolute maximum VO = VCC + 0.5 V (5.1, p. 4), so a 5 V VCC output reaches about 5 V, and the receiving input (item 4 of A) accepts 5.5 V recommended / 6.5 V absolute maximum. With the receiver powered at 3.3 V this is inside the receiver ratings. The check against power order (receiver unpowered) is covered by Ioff of the receiver (A item 4) | read (conclusion derived) |
| 18 | Supply, temperature, tpd | VCC 1.65 to 5.5 V; TA -40 to 125 C (5.3, p. 5). tpd A to Y, CL = 15 pF, -40 to 85 C: 5 V +/-0.5 V min 0.9, max 4.4 ns; 3.3 V min 1.5, max 4.6 ns (5.6, p. 7). No typical value | read |
| 19 | Absolute maximum VCC | -0.5 to 6.5 V (5.1, p. 4) | read |

### VT+ and VT- (Table 5-1, p. 6; -40 to 85 C columns, identical for -40 to 125 C)
| VCC | VT+ min | VT+ max | VT- min | VT- max | VT+ typ / VT- typ |
|-----|---------|---------|---------|---------|------------------|
| 4.5 V | 2.19 V | 2.74 V | 1.51 V | 1.97 V | not found |
| 5.0 V | not found | not found | not found | not found | not found |
| 5.5 V | 2.65 V | 3.33 V | 1.88 V | 2.4 V | not found |

For information (read): 3 V VT+ 1.48 to 1.92 V, VT- 0.89 to 1.2 V.

## C) Hold-off window, R = 1 Mohm 1 %, C = 510 nF 10 %, charge from the supply rail (derived)
**Method.** The capacitor charges from 0 V towards VCC: v(t) = VCC (1 - exp(-t/RC)). The Schmitt input switches when v = VT+. So t = R C ln(1 / (1 - VT+/VCC)). Because the threshold and the charging source share one rail, only the ratio r = VT+/VCC matters.

**Ratios from the read values**
- smallest ratio (earliest): VT+ min at 5.5 V: r = 2.65 / 5.5 = 0.4818 (the 4.5 V minimum gives 2.19 / 4.5 = 0.4867, larger).
- largest ratio (latest): VT+ max at 4.5 V: r = 2.74 / 4.5 = 0.6089 (the 5.5 V maximum gives 3.33 / 5.5 = 0.6055, smaller).
- 5.0 V is not in the table. A linear interpolation between the 4.5 V and 5.5 V rows is **not read**, it is an assumption; at 5.0 V it gives VT+ 2.42 to 3.04 V, r = 0.484 to 0.607, inside the two extremes above. The extremes use read values only.
- "Typical": the datasheet has no typical VT+. The middle value below uses the mid-point of the two interpolated 5.0 V ratios, r = 0.5455. It is **a derived mid-point, not a datasheet typical**.

**Logarithms (natural)**
- ln(1 / (1 - 0.4818)) = ln(1.9298) = 0.6574
- ln(1 / (1 - 0.5455)) = ln(2.2002) = 0.7886
- ln(1 / (1 - 0.6089)) = ln(2.5569) = 0.9388

**RC product**
- min: 0.99 Mohm x 0.459 uF = 0.4544 s
- nominal: 1.00 Mohm x 0.510 uF = 0.5100 s
- max: 1.01 Mohm x 0.561 uF = 0.5666 s

**Results**
| Case | RC | ln term | t |
|------|----|---------|---|
| Minimum (R, C and r all low) | 0.4544 s | 0.6574 | 0.4544 x 0.6574 = **299 ms** |
| Middle (nominal R, C; mid-point r) | 0.5100 s | 0.7886 | 0.5100 x 0.7886 = **402 ms** |
| Maximum (R, C and r all high) | 0.5666 s | 0.9388 | 0.5666 x 0.9388 = **532 ms** |

**Result.** The window 299 to 532 ms fits 200 to 600 ms with margin of 99 ms at the low end and 68 ms at the high end. The result holds only while the capacitor charges from the same rail that sets the threshold. Sensitivity on r only (nominal R, C): 0.510 x 0.6574 = 335 ms to 0.510 x 0.9388 = 479 ms.

**What the calculation does not cover**
- **Input leakage.** II is at most +/-5 uA (item 15). Across 1 Mohm this would be up to 5 V, so a worst-case leakage at the datasheet limit would stop the capacitor from charging. Only the maximum is specified; the typical leakage is **not found**. The hold-off needs a measured or separately sourced leakage figure, plus PCB surface leakage and capacitor leakage, before the 1 Mohm value is relied on.
- Capacitor tolerance other than the stated 10 %: temperature coefficient, DC-bias loss of a ceramic part (a class II capacitor can lose a large part of its value at 5 V), ageing. Not in the scope of these datasheets.
- Supply ramp time, a non-zero starting charge on the capacitor, and the discharge path after a power cycle.
- Threshold variation between -40 and 125 C: the datasheet shows one MIN/MAX range for the whole range, which the calculation uses.

## Not done
No Nexperia datasheet, no 5.0 V threshold row (the datasheet has none), no typical VT+ or VT-, no typical leakage, no simulation, no bench measurement, no check of the third-party distributor listing or stock.
