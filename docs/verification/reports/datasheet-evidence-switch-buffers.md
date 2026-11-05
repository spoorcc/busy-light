# Datasheet evidence for the current-limit switch TPS2553 (U7) and the buffers SN74LVC1G125 (U10) and SN74AHCT1G125 (U11)

- **Status:** Draft
- **Date:** 2026-11-05
- **Author:** Claude. Not reviewed. Nothing here is Approved or Accepted. No part is chosen.
- **Related:** HW-002, HW-010, ADR-0010, ADR-0016, `spike-full-board-schematic.md` (F3, F4, F7, F8), `datasheet-evidence-supervisor.md` (E1 to E6 for the TPS2553 limit numbers)
- **Source of the generator checked:** `hw/kicad/spike-gate/src/layout_full.py` (U7 box symbol, U10, U11).
- **Labels:** **read** (read in the text extracted with pdftotext from the local PDF on 2026-11-05), **derived** (computed here, arithmetic shown), **not found** (searched for, not in the text). Page numbers are the printed page numbers. Figures (graphs, package drawings) were not read from the text extraction; pin positions are taken from the pin tables. The PDFs are local only and are not committed (ADR-0015).

## Sources
- **S1** TI TPS2552, TPS2552-1, TPS2553, TPS2553-1, SLVS841G, November 2008, revised October 2026 (`tps2553.pdf`).
- **S2** TI SN74LVC1G125, SCES223U, April 1999, revised August 2026 (`sn74lvc1g125.pdf`).
- **S3** TI SN74AHCT1G125, SCLS378P, August 1997, revised March 2024 (`sn74ahct1g125.pdf`).

## A) TPS2553, U7 (S1)
| # | Item | Fact | Generator | Status |
|---|------|------|-----------|--------|
| A1 | Package pins, DBV SOT-23-6 | Table 5-1, p. 4: for the TPS2553 in SOT-23: EN 3 ("Enable input, logic high turns on power switch"), FAULT 4 (active-low open drain), GND 2, ILIM 5, IN 1, OUT 6. Fig. 5-1 text: IN 1, GND 2, EN 3 on one side, OUT 6, ILIM 5, FAULT 4 on the other | U7 box: 1 IN, 2 GND, 3 EN, 4 FAULT, 5 ILIM, 6 OUT; footprint `Package_TO_SOT_SMD:SOT-23-6`. **Match.** | read |
| A2 | Active-high enable | "EN = Active High for the TPS2553" (p. 4). The TPS2552 is active low. U7 EN is tied to VBUS_IC with IN, which is correct only for the active-high TPS2553 | **Match** | read |
| A3 | Latch-off and QOD variants | "Add -1 to part number for latch-off version; add 0 for QOD version" (p. 4). Which variant is wanted (TPS2553 auto-retry or TPS2553-1 latch-off) is not decided in the generator | Generator names "TPS2553" only | read; decision open |
| A4 | RILIM range | "recommended 15 kohm <= RILIM <= 232 kohm" (p. 4, p. 6 table 6.3 "Current-limit threshold resistor range (nominal 1%)"; section 8 text) | R_ILIM1, R_ILIM2, R_ILIM3 are all value `tbd`. **Nothing to compare yet.** Any chosen value, and the parallel combinations when Q2 or Q3 conduct, must lie in 15 to 232 kohm | read |
| A5 | Limit equations | IOSmax = 22980 / RILIM^0.94, IOSnom = 23950 / RILIM^0.977, IOSmin = 25230 / RILIM^1.016 (mA, RILIM in kohm, 15 to 232 kohm; section 8, pp. 16 to 17). They include temperature and process, not the resistor tolerance (text). Already recorded and cross-checked against the table in `datasheet-evidence-supervisor.md` E3 | none | read |
| A6 | Resistor network | The generator has R_ILIM1 from ILIM to GND and R_ILIM2 / R_ILIM3 each in series with a 2N7002 drain, joined at ILIM. A switched resistor in parallel with R_ILIM1 lowers the total, so a conducting Q2 or Q3 raises the limit. This is the structure of the datasheet two-level example (E4 in the supervisor report) | Structure consistent with E4 | read (E4); structure checked against `layout_full.py` |
| A7 | ILIM pin | "ILIM source current" 0 to 1 mA absolute maximum (p. 5); voltage range on IN, OUT, EN, ILIM, FAULT -0.3 to 7 V (p. 5). ILIM is regulated by the device; the 2N7002 drains must not drive it | No signal drives ILIM in the generator | read |
| A8 | EN thresholds | VIH min 1.1 V, VIL max 0.66 V, VEN 0 to 6.5 V (6.3, p. 6) | EN tied to VBUS_IC (about 5 V) | read |
| A9 | FAULT | "Continuous FAULT sink current" 0 to 10 mA (6.3, p. 6). Open drain, so a pull-up is needed; U7 pin 4 net FAULT_N | A test already requires FAULT_N pulled up to 3V3 | read |
| A10 | Input voltage | VIN 2.5 to 6.5 V; decoupling "0.1 uF or greater" from IN to GND (6.3, p. 6; Table 5-1) | C2 is `1u tbd` | read |

## B) SN74LVC1G125, U10 (S2), HOLD_OK_RB level step
| # | Item | Fact | Generator | Status |
|---|------|------|-----------|--------|
| B1 | Package pins, DBV (SOT-23-5) | Pin Functions, p. 3: A 2, GND 3, OE 1, VCC 5, Y 4 | U10: 1 OE, 2 A, 3 GND, 4 Y, 5 VCC; footprint `SOT-23-5`. KiCad symbol `74xGxx:74LVC1G125` has pins 1, 2, 3 GND, 4 (tri_state), 5 VCC. **Match.** | read |
| B2 | Function table | Table 7-1: OE low and A high gives Y high; OE low and A low gives Y low; OE high gives Z. **OE is active low** | OE (pin 1) is tied to GND, so the output is always enabled. **Correct.** | read |
| B3 | 5 V on the input with VCC = 3.3 V | VI recommended 0 to 5.5 V (5.3, p. 5); absolute maximum VI -0.5 to 6.5 V (5.1, p. 4); II "VI = 5.5 V or GND" at VCC 0 to 5.5 V: +-5 uA (5.5, p. 6). Application text: the device "can be used ... translating up from 3.3 V to 5 V" (8.1) | HOLD_OK is pulled up to VBUS_IC. Input within the recommended range **provided VBUS_IC stays at or below 5.5 V**. A VBUS above 5.5 V (USB 2.0 upper limit not read here) would exceed the recommended input range; the absolute maximum is 6.5 V | read |
| B4 | VCC = 0 V (3V3 absent, VBUS_IC present) | 7.3.2 Partial Power Down (Ioff): "This device includes circuitry to disable all outputs when the supply pin is held at 0 V. When disabled, the outputs neither source nor sink current". Ioff, test "VI or VO = 5.5 V", VCC = 0: +-10 uA max (5.5, p. 6). Absolute maximum VO in the high-impedance or power-off state: -0.5 to 6.5 V | Covered for a 5 V input with VCC = 0. The Ioff row is a leakage limit at 5.5 V on the pin; it is a stated limit, not a measured value here. **A partially powered VCC between 0 V and 1.65 V** (3V3 ramp) is not covered by the recommended range (VCC operating 1.65 to 5.5 V, data retention 1.5 V); behaviour of Y in that region is **not found**. HOLD_OK_RB only goes to GPIO6 | read; ramp region not found |
| B5 | VIH, VIL at VCC = 3 to 3.6 V | VIH min 2 V, VIL max 0.8 V (5.3, p. 5) | Input: HOLD_OK from an open-drain pulled to about 5 V (high) or pulled low by TPS3840. High is far above 2 V. Low level depends on the TPS3840 VOL (`datasheet-evidence-supervisor.md`) and must be below 0.8 V; not re-derived here | read |
| B6 | VOH at VCC = 3 V | IOH = -100 uA: VCC - 0.1 V; IOH = -16 mA: 2.4 V min; IOH = -24 mA: 2.3 V min (5.5, p. 6). VOL IOL = 100 uA: 0.1 V max | Load is one GPIO input: current negligible, so VOH is about VCC - 0.1 V = 3.2 V at 3.3 V. The ESP32-C3 input threshold was not compared here | read; MCU VIH not compared |
| B7 | VCC range | Operating 1.65 to 5.5 V (5.3, p. 5) | 3V3 rail | read |

## C) SN74AHCT1G125, U11 (S3), LED data buffer
| # | Item | Fact | Generator | Status |
|---|------|------|-----------|--------|
| C1 | Package pins, DBV (SOT-23-5) | Table 4-1, p. 3: 1 OE (input), 2 A, 3 GND, 4 Y, 5 VCC | U11 pin map equals U10 (KiCad `74AHCT1G125` extends `74LVC1G125`). **Match.** The pin drawing in the PDF was not readable as text; the numbers come from Table 4-1 | read |
| C2 | Supply | Recommended VCC **4.5 to 5.5 V** (5.3, p. 4). Absolute maximum VCC -0.5 to 7 V | U11 VCC is +5V (U7 OUT). The datasheet specifies VIH and the output levels only for VCC 4.5 to 5.5 V | read |
| C3 | VIH, VIL | VIH min 2 V, VIL max 0.8 V (5.3, p. 4), at VCC 4.5 to 5.5 V | A 3.3 V MCU output (VOH about 3.3 V minus the load drop) exceeds 2 V. MCU VOH min was not read from the ESP32-C3 datasheet in this task | read; MCU VOH not read |
| C4 | VIH at VCC = 3.3 V | **Not found.** No VIH or VOH is given for VCC below 4.5 V; the part is not specified for 3.3 V operation. It is not used so in the design (U11 runs on +5V) | none needed | not found |
| C5 | Input with VCC below range | VI recommended 0 to 5.5 V (5.3). II "VI = 5.5 V or GND", VCC 0 to 5.5 V: +-0.1 uA typ at 25 C, +-1 uA max (5.5, p. 5). **No Ioff or partial-power-down feature is stated** (searched for "Ioff", "partial power down": not found). So behaviour with +5V absent and LED_DATA driven by a 3.3 V MCU output is not specified for the output; the input leakage row covers VCC 0 V | Power-up with the MCU driving LED_DATA before +5V is present: not covered by the datasheet. Pull-down R11 holds the input low when the MCU pin is not driving | read; not found |
| C6 | Output | VOH 4.4 V min at IOH = -50 uA, 3.8 V min at -8 mA (-40 to 85 C); IOH max -8 mA (5.3, 5.5) | Output drives LED_BUF through R10 (330 ohm) into D1 DIN. The WS2812B VIH was not read in this task | read |
| C7 | OE | Table 7-1: OE low gives Y = A; OE high gives Z. OE is active low | OE tied to GND: always enabled. **Correct.** | read |

## Findings
1. **No pin-number, package or polarity mismatch** was found for U7, U10 or U11 against S1 to S3. The only change to `layout_full.py` was a caption: "pin order not read" now reads "pins per SLVS841G". A test (`test_switch_and_buffer_pins_follow_the_datasheets`) now fixes the pin map of the three parts.
2. The ILIM resistors are `tbd`; the range check 15 to 232 kohm cannot be done until values are chosen. When chosen, check the nominal and the parallel combinations against the equations in A5, including resistor tolerance (not included in the datasheet equations).
3. U10 input: 5 V is within the datasheet recommended range (up to 5.5 V) with VCC = 3.3 V and with VCC = 0 V (Ioff). Margin to 5.5 V depends on the highest VBUS_IC; not analysed.
4. U11: the datasheet gives no partial-power-down protection; with +5V absent and an MCU-driven LED_DATA, the device is outside its stated conditions. Not a fault in normal operation; record as an open point for the power-up sequence.
5. Not run: no simulation, no bench measurement, no ESP32-C3 input-level comparison, no check of the USB VBUS upper limit.
