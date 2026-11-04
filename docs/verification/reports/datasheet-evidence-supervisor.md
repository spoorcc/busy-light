# Datasheet evidence for the VBUS hold-off supervisor (TPS3840, TPS3808, TPS3839) and the TUSB321 OUT1/OUT2 pins

- **Status:** Draft
- **Date:** 2026-11-04
- **Author:** Claude. Not reviewed. Nothing here is Approved or Accepted. No part is chosen.
- **Related:** HW-003, HW-010, `docs/verification/reports/spike-hw-gate-fragment.md` (Version 3, placeholder U5/C1/R6), `docs/verification/reports/datasheet-evidence-gate-logic.md`
- **Labels:** each fact is marked **read** (read in the datasheet text on 2026-11-04), **derived** (computed here from read values; the arithmetic is shown) or **not found** (searched for, not in the text). The PDFs were downloaded to a scratch folder and are not committed (ADR-0015: vendor datasheets are linked, not committed). Page numbers are the printed page numbers. Values in figures (graphs) were not read: the text extraction does not give curve values.
- **Requirement being checked (from the request, not from an Approved document):** output "reset" (low) while VBUS is below the threshold and 200 to 600 ms after VBUS recovers; a dip to 3.5 V and back restarts the full delay; output low when unpowered (open-drain pulled up to VBUS), valid down to VDD about 1 V or less; threshold below 4.5 V and above about 3.6 V; VBUS 4.5 to 5.5 V.

## Sources
- **S1** TI TPS3840, SNVSB03E, December 2018, revised May 2026: https://www.ti.com/lit/ds/symlink/tps3840.pdf (10 pages as served by the symlink; the printed page numbers run to 31).
- **S2** TI TPS3808, SBVS050N, May 2004, revised August 2026: https://www.ti.com/lit/ds/symlink/tps3808.pdf
- **S3** TI TPS3831/TPS3839, SBVS193D, June 2012, revised July 2015: https://www.ti.com/lit/ds/symlink/tps3839.pdf
- **S4** TI TUSB321, SLLSEO6C (Rev. C), June 2015, revised August 2018, 25 pages. Downloaded earlier in this session (scratch folder `ds_tusb321`); the download URL was not recorded. **The request named SLLSF53; that number is not in the file.** The file is SLLSEO6C. It was not checked whether SLLSF53 is a later revision or a different document.
- **Not obtained** (download failed or returned an HTML page, not a PDF): Microchip MCP130/MCP1316, Analog Devices/Maxim MAX809/MAX6xxx, ST STM6xx, Diodes Inc. These families are **not evaluated**. No claim is made about them.

## A) TPS3840DL (S1), programmable delay, fixed threshold, open-drain
| # | Item | Fact | Status |
|---|------|------|--------|
| A1 | Threshold options | VIT- 1.6 to 4.9 V in 0.1 V steps (Features p. 1; Table 9-2, p. 30). Variants DL40 (4.0 V), DL41, DL42, DL43, DL44 (4.4 V) are in Table 9-2. Typical hysteresis 0.200 V for 3.1 to 4.9 V | read |
| A2 | Orderables "Active, Production" (addendum, 1 Nov 2026) | TPS3840DL31, DL35, DL40, DL42, DL44, DL45, DL46, DL49 (DBVR). **DL41 and DL43 are not in the orderable list** (the list says "other options on request, minimum order quantities apply", p. 30) | read |
| A3 | Threshold accuracy | VIT- -1.5 % / +1 % typ / +1.5 % max over -40 to 125 C (6.5, p. 6) | read |
| A4 | Hysteresis | VIT- 3.1 to 4.9 V: min 175, typ 200, max 225 mV (6.5, p. 6). Reset is released after tD once VDD > VIT+ = VIT- + VHYS (7.3.1.1, p. 17) | read |
| A5 | Delay formula | tD = -ln(0.29) x RCT x CCT + tD(no cap) = 618937 x CCT + 50 us (Equations 3 and 4, p. 18). Check: CT = 1 uF gives 619 ms typ (6.6, p. 7) | read |
| A6 | Delay limits | Equation 6: tD min = -ln(0.36) x RCT min x CCT min + tD(no cap) min. Equation 7: tD max = -ln(0.26) x RCT max x CCT max + tD(no cap) max (p. 18). RCT = 350 / 500 / 650 kohm (min/typ/max, 6.5, p. 6). tD(no cap) max 50 us; **tD(no cap) min not found** (the calculation uses 0) | read; tD(no cap) min not found |
| A7 | Delay tolerance over temperature | Electrical table is given over -40 to 125 C (6.5, 6.6); no separate temperature coefficient of tD is given. The tolerance is carried by the three constants of A6 | read (no separate figure) |
| A8 | CT dependence, CT leakage | CT maximum 10 uF; abs max on CT -0.3 to 5.5 V (6.1, p. 5). Datasheet gives no CT pin leakage and no CT voltage during the delay. "Capacitor leakage" is not mentioned in 7.3.2 | CT leakage: not found |
| A9 | Output type | TPS3840DL: open-drain, active-low RESET, needs a pull-up; "can be pulled up to any voltage up to 10 V independent of the VDD voltage" (7.3.4.1, p. 19) | read |
| A10 | Minimum VDD for a valid low | VPOR (open-drain) max 950 mV at IOUT(sink) = 5.6 uA, VOL(max) = 0.2 V (6.5, p. 6). Below VPOR the output is undefined (7.4.3, p. 20). Between VPOR and VDD(min) = 1.5 V the output is asserted (7.4.2, Table 7-1 note 1: UVLO holds reset until VDD falls below VPOR) | read |
| A11 | VOL | max 200 mV at 2 mA, VDD below VIT-, 1.5 V < VDD < 5 V (6.5, p. 6) | read |
| A12 | Abs max on RESET (DL) | -0.3 to 12 V; VDD -0.3 to 12 V; RESET current +/-70 mA (6.1, p. 5). Recommended RESET 0 to 10 V, 0 to +/-5 mA (6.3, p. 5) | read |
| A13 | Operating temperature | -40 to 125 C (TJ, 6.3, p. 5) | read |
| A14 | Supply current | IDD 300 nA typ, 700 nA max, 1.5 V to 10 V, VDD > VIT+, -40 to 125 C (6.5, p. 6) | read |
| A15 | Package and pins | DBV, SOT-23-5 (p. 4): RESET 1, VDD 2, GND 3, MR/NC 4, CT 5. Same numbering for DL and PL | read |
| A16 | Delay restart on a dip | Reset is asserted when VDD < VIT- (7.3.4.1). Glitch immunity tGI_VIT- 10 us typ at 5 % overdrive (6.6, p. 7), so a dip below 5 % under VIT- for 10 us counts; larger overdrive: figure only, not read. 7.3.2 (p. 18): "the previously charged up capacitor discharges, and if the monitored voltage returns ... before the delay capacitor discharges completely, ... the reset delay is shorter than expected." **The CT discharge time is not given** (no number for how long a dip must last for a full restart). Whether a dip to 3.5 V restarts the **full** delay is therefore not guaranteed by the text | read; discharge time: not found |
| A17 | Start-up | tSTRT 100 / 220 / 350 us (CT open); a CT capacitor adds tD to tSTRT (6.6, p. 7) | read |
| A18 | ESD | HBM +/-2000 V, CDM +/-750 V (6.2, p. 5) | read |
| A19 | LCSC / JLCPCB stock | not checked (see the end) | not checked |

**Threshold check for the DL40, DL41, DL42, DL44 (derived from A1, A3, A4).** VIT- min = VIT- x 0.985, VIT- max = VIT- x 1.015; reset is released at VIT+ = VIT- + VHYS, so the highest release voltage is VIT- max + 225 mV.

| Variant | VIT- min | VIT- max | VIT+ min (VIT- min + 175 mV) | VIT+ max (VIT- max + 225 mV) | VIT+ max against VBUS min 4.5 V |
|---------|----------|----------|------------------------------|-------------------------------|--------------------------------|
| DL40 (4.0 V) | 3.940 V | 4.060 V | 4.115 V | 4.285 V | margin 215 mV |
| DL41 (4.1 V, not stocked per A2) | 4.0385 V | 4.1615 V | 4.2135 V | 4.3865 V | margin 113 mV |
| DL42 (4.2 V) | 4.137 V | 4.263 V | 4.312 V | 4.488 V | **margin 12 mV** |
| DL44 (4.4 V) | 4.334 V | 4.466 V | 4.509 V | 4.691 V | **above 4.5 V: reset would not release at VBUS = 4.5 V** |

DL40 gives VIT- min 3.94 V, above 3.6 V, and a dip to 3.5 V is 440 mV below it. DL42 releases at up to 4.488 V, 12 mV below the 4.5 V minimum of VBUS; that margin is smaller than any plausible plug-in drop, so DL42 is not usable. DL44 is not usable.

**Delay window, TPS3840 (derived).** Constants from A6, natural logarithms: -ln(0.36) = 1.0217, -ln(0.29) = 1.2379, -ln(0.26) = 1.3471.
- k_min = 1.0217 x 350 kohm = 357.6 kohm
- k_typ = 1.2379 x 500 kohm = 618.9 kohm (equals 618937 of Equation 4)
- k_max = 1.3471 x 650 kohm = 875.6 kohm
- tD min = k_min x C x (1 - tol); tD max = k_max x C x (1 + tol); tD(no cap) and tSTRT (tens to hundreds of us) neglected.
- Ratio k_max / k_min = 2.449. The window ratio 600 / 200 = 3.0. The capacitor tolerance must satisfy (1 + tol) / (1 - tol) <= 3.0 / 2.449 = 1.225, that is **total capacitor tolerance <= 10.1 %** (including temperature, DC bias and ageing), and then only for one exact value.

| C (nominal) | tol | tD min | tD typ (k_typ x C) | tD max | In 200 to 600 ms? |
|-------------|-----|--------|---------------------|--------|-------------------|
| 560 nF | +/-5 % | 357.6 k x 0.532 uF = 190.2 ms | 346.6 ms | 875.6 k x 0.588 uF = 514.9 ms | no (190 ms) |
| **620 nF** | +/-5 % | 357.6 k x 0.589 uF = **210.6 ms** | 383.7 ms | 875.6 k x 0.651 uF = **570.0 ms** | **yes**, margin 10.6 ms low, 30 ms high |
| 620 nF | +/-10 % | 357.6 k x 0.558 uF = 199.5 ms | 383.7 ms | 875.6 k x 0.682 uF = 597.2 ms | **no, 0.5 ms short** |
| 680 nF | +/-5 % | 231.0 ms | 420.9 ms | 875.6 k x 0.714 uF = 625.2 ms | no (625 ms) |

**Result.** With a 620 nF capacitor whose total tolerance (initial, temperature, DC bias at the CT voltage, ageing) stays within +/-5 %, the window is 211 to 570 ms. With +/-10 % it is not met. A capacitor with a total tolerance of +/-5 % at 620 nF needs a C0G/film type; that is a part-selection fact **not** taken from a datasheet here. A class II ceramic (X7R) loses an unknown part of its value with DC bias, and the datasheet gives no CT voltage, so the DC-bias loss cannot be computed. CT leakage (A8) and the discharge time on a dip (A16) are not in the numbers.

## B) TPS3808G01 (S2), programmable delay, adjustable threshold via SENSE divider, open-drain
| # | Item | Fact | Status |
|---|------|------|--------|
| B1 | Threshold options | Fixed versions G09 to G50, VIT 0.84 to 4.65 V (Table 4-1, p. 3): G33 3.07 V, **G50 4.65 V**. 7.3 (p. 10) says "0.82 V to 3.3 V or from 4.4 V to 5 V" can be factory-set; only G50 (4.65 V) is listed. G50 is **above 4.5 V**: not usable. G01 is adjustable, VIT 0.405 V, "any voltage above 0.405 V using an external resistor divider": VIT' = (1 + R1/R2) x 0.405 (Figure 7-1, p. 11) | read |
| B2 | Threshold accuracy | G01: -2 % / +/-1 % typ / +2 %. Fixed, 3.3 V < VIT <= 5 V: -2 % / +2 %; -40 to 85 C: +/-1.5 % (6.5, p. 6) | read |
| B3 | Hysteresis | G01: 1.5 % typ, 3 % max of VIT. Fixed: 1 % typ, 2.5 % max. **Minimum hysteresis: not found** (6.5, p. 6) | read; min not found |
| B4 | SENSE input current | G01: -25 to +25 nA at VSENSE = VIT (6.5, p. 6) | read |
| B5 | Delay formula | CT (nF) = (tD (s) - 0.5 ms) x 175, so tD = CT (nF) / 175 + 0.5 ms (Equation 1, p. 11). 220 nA current source charging CT to 1.23 V. CT must be >= 100 pF. Fixed options: CT open 20 ms; CT to VDD through 40 to 200 kohm 300 ms (p. 11) | read |
| B6 | Delay accuracy | 6.6 (p. 7): CT open 12 / 20 / 28 ms; CT = VDD 180 / 300 / 420 ms; CT = 130 pF 0.75 / 1.25 / 1.75 ms; CT = 180 nF 0.62 / 1.03 / 1.44 s. That is -40 % / +40 % of typ at every listed row (0.62 / 1.03 = 0.602; 1.44 / 1.03 = 1.398). Delay is given over -40 to 125 C. Figure 6-4 (normalized timeout vs temperature, +/-10 % axis) is a figure, not read. **Whether the min/max includes the tolerance of the external capacitor: not stated.** Only three CT points are specified; applying the +/-40 % to 68 nF is an extrapolation | read; CT-tolerance inclusion: not found |
| B7 | CT leakage | "a low-leakage type capacitor such as a ceramic must be used, and ... stray capacitance around this pin can cause errors" (7.3.2, p. 11). No leakage figure. CIN of CT pin 5 pF | read; figure not found |
| B8 | Output type | Open-drain RESET; pull-up 10 kohm to 1 Mohm; "allows the reset pin to attain voltages higher than VDD" up to 6.5 V (pin table p. 4; 7.3.4, p. 12) | read |
| B9 | Minimum VDD for a valid low | VPOR max 0.8 V at VOL max 0.2 V, IRESET = 15 uA (6.5, p. 6, with the note "Trise(VDD) >= 15 us/V"). Below VPOR: "RESET is undefined" (7.4.3, p. 13). VDD range 1.7 to 6.5 V (-40 to 125 C); between VPOR and 1.7 V the output is asserted and low-impedance (7.4.2, p. 13) | read |
| B10 | VOL | max 0.3 V at 1.3 V <= VDD < 1.8 V, 0.4 mA; max 0.4 V at 1.8 V <= VDD <= 6.5 V, 1 mA (6.5, p. 6) | read |
| B11 | Abs max on RESET | VRESET, VMR, VSENSE -0.3 to 7 V; VDD -0.3 to 7 V; RESET current +/-5 mA (6.1, p. 5). RESET leakage 300 nA max at 6.5 V (6.5) | read |
| B12 | Operating temperature | -40 to 125 C (TJ) | read |
| B13 | Supply current | 2.4 uA typ, 5 uA max at VDD = 3.3 V; 2.7 / 6 uA at 6.5 V (6.5, p. 6) | read |
| B14 | Package and pins | DBV SOT-23-6 (Table 5-1, p. 4): RESET 1, GND 2, MR 3, CT 4, SENSE 5, VDD 6. DRV WSON-6: VDD 1, SENSE 2, CT 3, MR 4, GND 5, RESET 6, thermal pad | read |
| B15 | Delay restart on a dip | RESET asserts when SENSE < VIT. "When a RESET is asserted, the capacitor is discharged" (7.3.2, p. 11). **No discharge time given.** SENSE glitch immunity: Figure 8-2 (p. 15) "RESET occurs above the curve" for duration against overdrive; values not read. SENSE pulse width to RESET 20 us typ (6.6) | read; discharge time: not found |
| B16 | Orderable | TPS3808G01DBVR / DBVT "Active, Production" (addendum, p. 18 and following) | read |
| B17 | LCSC / JLCPCB stock | not checked | not checked |

**Divider and threshold (derived).** R2 = 100 kohm, R1 = 887 kohm (E96): VIT' nominal = (1 + 8.87) x 0.405 = 3.997 V. Worst case: VIT 0.405 V x (1 -/+ 2 %), SENSE current +/-25 nA x (R1 || R2 = 89.9 kohm) = +/-2.25 mV, resistors 1 % opposite ends.

| Resistor tolerance | VIT' min | VIT' max | Release max (VIT' max x 1.03) | Against 3.6 V and 4.5 V |
|--------------------|----------|----------|-------------------------------|-------------------------|
| 1 % | 3.826 V | 4.174 V | 4.299 V | min above 3.6 V by 226 mV; release 201 mV below 4.5 V |
| 0.1 % | 3.888 V | 4.107 V | 4.230 V | min above 3.6 V by 288 mV; release 270 mV below 4.5 V |

The hysteresis is applied to VIT as a percentage (3 % max); the minimum is not found, so the lowest release voltage is not computed. Divider cost: the divider draws about 4 V / 987 kohm = 4.1 uA from VBUS (derived, more than the IC itself).

**Delay window, TPS3808G01 (derived).** Assumes the +/-40 % of B6 holds at all CT values, and that it does not include the external capacitor (B6: not stated; the worst case is taken). tD nominal = CT / 175 + 0.5 ms. Minimum = 0.6 x tD nominal x (1 - tol); maximum = 1.4 x tD nominal x (1 + tol).
- Window ratio left for the capacitor: 3.0 / (1.4 / 0.6 = 2.333) = 1.286, so (1 + tol) / (1 - tol) <= 1.286, tol <= 12.5 %.
- CT = 68 nF: tD nom = 68 / 175 + 0.5 ms = 0.3886 + 0.0005 = 389.1 ms.
  - tol 0 %: 0.6 x 389.1 = 233.4 ms; 1.4 x 389.1 = 544.7 ms.
  - tol +/-5 %: 0.6 x 389.1 x 0.95 = 221.8 ms; 1.4 x 389.1 x 1.05 = 571.9 ms.
  - tol +/-10 %: 0.6 x 389.1 x 0.90 = 210.1 ms; 1.4 x 389.1 x 1.10 = 599.2 ms (1 ms from the upper limit).
- CT = 62 nF (nom 354.8 ms) at +/-10 %: 191.6 ms, not met. CT = 75 nF (nom 429.1 ms) at +/-5 %: 630.7 ms, not met.

**Result.** 68 nF (E6/E12 value) meets 200 to 600 ms for a capacitor tolerance up to +/-10 %: 210 to 599 ms. This is the part that tolerates the common capacitor tolerance best of the three, but it depends on the extrapolation of +/-40 % to 68 nF and on the capacitor tolerance not being included in the +/-40 % (if it is included, the margin is larger). It needs a divider (3 parts) and a 6-pin package.

## C) TPS3839K50 (S3), fixed delay, 4.38 V, push-pull
| # | Item | Fact | Status |
|---|------|------|--------|
| C1 | Threshold | TPS3839K50: VIT- 4.271 / 4.38 / 4.446 V, -40 to 85 C (7.5, p. 7). Other 4.xx V options: **not found** (options 0.9 to 4.38 V, p. 4). Hysteresis 44 mV (typ; no min or max given) | read; hysteresis min/max not found |
| C2 | Release voltage (derived) | VIT- max + Vhys typ = 4.446 + 0.044 = 4.490 V; margin to 4.5 V is **10 mV** and uses a typical hysteresis | derived |
| C3 | Delay | td 120 / 200 / 350 ms (7.6, p. 8), fixed, no CT pin | read |
| C4 | Delay against window | **min 120 ms < 200 ms: not met.** max 350 ms < 600 ms met | derived |
| C5 | Output | Push-pull RESET (pin table, p. 5). Valid output for VDD > 0.6 V (V(POR) max 0.6 V at IOL = 1 uA, 7.5, p. 7). VOL max 0.4 V at 2 mA for VDD 2.8 to 6.5 V | read |
| C6 | Abs max | VDD, RESET -0.3 to 7 V; RESET current +/-10 mA (7.1, p. 6) | read |
| C7 | Temperature, supply current | -40 to 85 C; IDD 150 nA typ, 500 nA max (7.5, p. 7) | read |
| C8 | Package | DBZ SOT-23-3 (p. 5): GND 1, RESET 2, VDD 3. DQN X2SON-4 | read |
| C9 | Dip restart | "RESET remains asserted ... until the delay time (td) elapses after VDD rises above the threshold"; transient rejection, duration against amplitude: Figure 13 (p. 12) "Reset Occurs Above Line", axis up to 50 us / 35 % under VIT-; values not read. No statement that the delay restarts in full after a partial dip: not found | read; restart behaviour: not found |
| C10 | Orderable | TPS3839K50DBZR / DBZT "Active, Production" | read |

**Result.** TPS3839K50 does not meet the lower limit (120 ms) and its release voltage is within 10 mV of 4.5 V. It is listed as a negative control only.

## D) Comparison
| Item | TPS3840DL40 | TPS3808G01 (+ divider) | TPS3839K50 |
|------|-------------|------------------------|------------|
| Threshold meets 3.6 to 4.5 V incl. hysteresis | yes: 3.94 to 4.285 V | yes, with 1 % resistors: 3.826 to 4.299 V | marginal: 4.271 to 4.490 V |
| Delay 200 to 600 ms | 211 to 570 ms at 620 nF +/-5 % total; fails at +/-10 % | 210 to 599 ms at 68 nF +/-10 % (extrapolated tolerance) | fails: 120 ms min |
| Valid low down to VDD | 0.95 V max VPOR | 0.8 V max VPOR | 0.6 V |
| Output | open-drain (pull-up to 10 V allowed) | open-drain (pull-up up to 6.5 V) | push-pull |
| Supply current | 0.3 uA typ, 0.7 uA max | 2.4 uA typ, 5 uA max (+ 4 uA divider) | 0.15 uA typ, 0.5 uA max |
| Parts around it | 1 capacitor | 1 capacitor + 2 resistors (+1 nF SENSE bypass recommended, p. 10) | none |
| Temperature | -40 to 125 C | -40 to 125 C | -40 to 85 C |
| Dip restart | full restart not guaranteed in text (discharge time not found) | same | same, not stated |

**Pull-up resistor for the "low when VDD is low" requirement (derived from A10, B9).** With the pull-up to VBUS and VBUS at VPOR, the pull-up current must stay at or below the specified sink current: TPS3840DL, R >= (0.95 V - 0.2 V) / 5.6 uA = 134 kohm; TPS3808, R >= (0.8 V - 0.2 V) / 15 uA = 40 kohm. For TPS3840DL the pull-up should therefore be at least 134 kohm (the datasheet test uses 100 kohm). Below VPOR the output is undefined in both datasheets; with the pull-up to VBUS a floating output follows VBUS, which is below 0.95 V there. Whether that reads "low" depends on the input threshold of the gate it feeds (not checked here).

## E) JLCPCB / LCSC stock
Not checked. A request to the LCSC search API returned "Access Denied" (bot protection), and no LCSC part page was read. No stock, price or part number at LCSC is claimed. TI lists the DBV orderables as Active (A2, B16, C10), which is not stock at LCSC.

## F) TUSB321 OUT1 / OUT2 (S4, SLLSEO6C)
| # | Item | Fact | Status |
|---|------|------|--------|
| F1 | Output type | Pin functions (Table, p. 3): OUT1 pin 7 and OUT2 pin 8, type "I/O": "This pin is an open drain output for communicating Type-C current mode detect when the device is in UFP mode." OUT1: default current high (H), medium or high low (L). OUT2: default or medium high (H), high low (L) (Table 2, p. 11). The datasheet does not describe a push-pull mode | read |
| F2 | Absolute maximum on OUT1, OUT2 | **-0.3 V to VDD + 0.3 V** (6.1, p. 4). VDD -0.3 to 6 V. The same VDD + 0.3 V limit applies to PORT, CURRENT_MODE, ID, DIR and VCONN_FAULT. CC1/CC2 -0.3 to 6 V. VBUS_DET -0.3 to 4 V | read |
| F3 | Recommended operating | VDD 4.5 to 5.5 V (6.3, p. 4); TA 0 to 70 C. **No recommended operating voltage range for OUT1/OUT2 is given separately** | read; separate OUT range: not found |
| F4 | Electrical | VOL max 0.4 V at IOL = -1.6 mA (open-drain pins VCONN_FAULT, ID, OUT1, OUT2, 6.5, p. 5). "External pullup resistor on open drain IOs" (Rp_ODext) 200 kohm, listed in the TYP column (p. 5). No statement whether this is a minimum, a maximum or a recommendation | read; meaning of 200 kohm: not found |
| F5 | Input leakage / clamp | IIH +/-20 uA, IIL +/-10 uA for the control pins (6.5, p. 5). No current rating of an internal clamp diode to VDD, no Ioff-type specification for a pin held above VDD with the device unpowered | not found |
| F6 | Pull-up rail in the datasheet's example | The DFP typical application (section 8.2.1, p. 15; figure number not checked) shows pull-up resistors (200 kohm, 200 kohm, 10 kohm, 4.7 kohm) to a net labelled VCC_3.3V while VDD is labelled VDD_5V. From the extracted text it is not possible to say which resistor belongs to which pin, and the example is DFP mode (OUT1/OUT2 are UFP outputs) | read; pin assignment not determinable |
| F7 | Power supply note | "The TUSB321 device has a wide power supply range from 4.5 to 5.5 V" (9, p. 17). No statement about the behaviour of the pins at VDD below 4.5 V or at VDD = 0 V | read; behaviour at 0 V not found |

**Answer to the question.**
1. OUT1 and OUT2 are **open-drain** outputs (F1).
2. The absolute maximum on them is **VDD + 0.3 V** (F2), not a fixed voltage. With VDD at 0 V (VBUS removed), the limit is 0.3 V. A 3.3 V pull-up that is still at 3.3 V (or has not yet decayed) while VDD falls to 0 V puts the pin up to about 3.0 V above the limit. That is **outside the absolute maximum rating** for the time the pull-up rail is above VDD + 0.3 V. During normal operation (VDD 4.5 to 5.5 V) a 3.3 V pull-up is inside the rating (3.3 V < 4.5 V + 0.3 V).
3. The datasheet gives no current-limit figure for the pin when it is above VDD+0.3 V (F5). A series resistor therefore cannot be qualified from this datasheet: the resistor limits the current into whatever clamp exists, but the permitted current is **not found**. Ask TI, or avoid the condition.
4. Options that stay inside the rating by construction (derived, not from the datasheet): pull OUT1/OUT2 up to a rail that cannot exceed VDD + 0.3 V when VDD falls (for example a rail derived from the same VBUS, with equal or faster fall); or add a level shifter/buffer that is specified for Ioff with the TUSB321 side unpowered; or hold the 3.3 V rail off until VBUS is good. Whether the 3.3 V rail falls faster than VDD depends on the regulator and the loads (not analysed).
5. Document number: the file read is SLLSEO6C (Rev. C, August 2018); SLLSF53 was not found and was not checked.

## Not done
No Microchip, Analog Devices/Maxim, ST or Diodes datasheet (not obtained; not evaluated). No LCSC or JLCPCB stock check. No simulation, no bench measurement. Not read: Figure 6-3 and 6-4 of S2 (timeout against CT and temperature), Figure 8-2 of S2 and the transient figures of S1 and S3 (values), so the dip depth and duration needed to trigger a reset are not quantified beyond tGI = 10 us at 5 % (S1). CT discharge time on a dip (S1, S2), CT leakage, DC-bias loss of the CT capacitor and the effect of VBUS ramp rate on the delay are not found or not computed. The delay arithmetic assumes the datasheet constants only. The TUSB321 behaviour with a pin above VDD + 0.3 V and VDD = 0 V is not in the datasheet. No statement here says a part "is compliant"; only which values were read.
