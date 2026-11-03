# ADR-0009: USB-C power input and detection of the advertised source current

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-04
- **Deciders / reviewers:** Ben Spoor (owner); no goldfish review yet
- **Related:** NEED-003, SYS-020, SYS-021, SYS-022, SYS-027, SYS-028, HW-003, HW-004, ADR-0003, ADR-0004 (item 4), RISK-003, RISK-004, RISK-005; `docs/verification/reports/spike-7-5-power-budget-paper.md` (sections 2.3 and 8)

## Context and problem
The device takes 5 V from a USB-C connector. It is a sink only. The only data function is the chip's USB-Serial-JTAG for programming (ESP32-C3-MINI-1, 16 single-wire RGB LEDs).
Owner decision of 2026-11-04 (SYS-020): the device may draw more than the default [500] mA when the source advertises 1.5 A or more on the CC lines. The limit is the advertised value minus a [10] % margin, at most [1500] mA, so at most 1350 mA. If nothing higher is advertised, or the value cannot be read, the limit is [500] mA. A USB-C to USB-A cable advertises the default current.
Why it matters: at 500 mA the Wi-Fi transmit peak leaves 46 to 148 mA for the LEDs (spike 7.5 paper budget, RISK-004). At 1350 mA the LED budget is no longer the constraint (spike 7.5, section 8).
This ADR decides how the firmware learns the advertised current. It does not decide the hardware current limit (ADR-0004 item 4). It relates to it in the consequences.

Not known: the accuracy of the ESP32-C3 ADC on a CC line under Wi-Fi load (spike needed); the real stock and price of the candidate parts at the shop (live pages not readable, see section "Evidence"); the rating of the chosen USB-C receptacle at 1.5 A; whether the Zephyr ADC driver for the C3 gives calibrated millivolts (not checked).

## Evidence
Status of each source: **read** = I read the text of the document in this session; **snippet** = I saw it only in a search result; **not found** = I looked and did not find it. I did not read the USB Type-C specification itself. All CC voltage values are secondary sources.

| ID | Fact | Value | Source | Status |
|----|------|-------|--------|--------|
| E1 | Sink Rd on each CC line | 5.1 kohm (4.6 to 5.6 in the TUSB321 datasheet) | https://www.ti.com/lit/gpn/tusb321 (SLLSEO6C) | read |
| E2 | Source Rp to 5 V: default / 1.5 A / 3 A | 56 / 22 / 10 kohm. CC voltage at a 5.1 kohm sink: about 0.41 / 0.92 / 1.68 V | https://applied-ee.github.io/embedded/docs/power-battery/usb-power-and-pmics/usb-power-fundamentals/ | read (secondary) |
| E3 | Source Rp to 3.3 V: 36 / 12 / 4.7 kohm | same values for the three levels | Infineon KB 253544, https://community.infineon.com/t5/Knowledge-Base-Articles/Termination-Resistors-Required-for-the-USB-Type-C-Connector/ta-p/253544 (fetch gave 403) | snippet |
| E4 | Sink CC voltage bands: default 0.25 to 0.61 V; 1.5 A 0.70 to 1.16 V; 3.0 A 1.31 to 2.04 V | gaps: 0.61 to 0.70 V and 1.16 to 1.31 V | same page as E2 | read (secondary) |
| E5 | Sink detection thresholds in an IC: attach 0.20 V (0.15 to 0.25); 1.5 A 0.66 V (0.61 to 0.70); 3 A 1.23 V (1.169 to 1.29) | the thresholds lie inside the gaps of E4 | TUSB321 datasheet, table of CC pin parameters | read |
| E6 | Another summary gives 1.5 A 0.61 to 0.70 V (typ. 0.66) and 3 A 1.16 to 1.31 V (typ. 1.23) as thresholds; a further excerpt gives 3 A values of 2.04 / 2.11 / 2.18 V (min/typ/max) | 2.18 V is the highest CC voltage I saw | search summary (TI TPS65988 datasheet and an unnamed datasheet excerpt; page not identified) | snippet |
| E7 | Limits `vRa` and `vRd` as defined in the Type-C specification (Tables 4-23 to 4-25 in an older revision) | numbers | USB Type-C specification | not found |
| E8 | ESP32-C3: two 12-bit SAR ADCs. ADC1: 5 channels, factory-calibrated. ADC2: 1 channel, not factory-calibrated, not operable on some chip revisions | | https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf (v2.4), section 4.2.2.1 | read |
| E9 | ADC pins: GPIO0 to GPIO4 = ADC1_CH0 to CH4; GPIO5 = ADC2_CH0. On the module: IO0 pin 12, IO1 pin 13, IO2 pin 5, IO3 pin 6, IO4 pin 18, IO5 pin 19 | | same datasheet, pin tables; ESP32-C3-MINI-1 datasheet v2.2, https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf | read |
| E10 | Strapping pins GPIO2, GPIO8, GPIO9. USB pins GPIO18 (D-), GPIO19 (D+). GPIO4 is also MTMS (JTAG) | | ESP32-C3-MINI-1 datasheet, pin table and strapping section | read |
| E11 | Calibrated total error: 0 to 750 mV +-10 mV; 0 to 1050 +-10; 0 to 1300 +-10; 0 to 2500 mV (ATTEN3) +-35 mV. INL +-12 LSB, DNL +-7 LSB (25 C, Wi-Fi off, 100 nF on the pin) | | ESP32-C3 datasheet v2.4, tables 5-5 and 5-6 | read |
| E12 | ESP-IDF oneshot driver: ADC2 oneshot "no longer supported, due to hardware limitations. The results are not stable"; the highest attenuation is 12 dB (11 dB deprecated, same behaviour) | the page gives no millivolt range | https://docs.espressif.com/projects/esp-idf/en/v5.3/esp32c3/api-reference/peripherals/adc_oneshot.html | read |
| E13 | ADC input resistance and leakage; accuracy with Wi-Fi active; absolute maximum voltage of a GPIO pin | | ESP32-C3 datasheet, ESP32-C3-MINI-1 datasheet | not found (pin capacitance 2 pF is given; the "input power pins" maximum is 3.6 V) |
| E14 | TUSB321: sink mode; open-drain outputs OUT1 (low = 1.5 A or 3 A) and OUT2 (low = 3 A); external pull-up at most 200 kohm; VDD 4.5 to 5.5 V; recommended ambient 0 to 70 C; package X2QFN-12, 1.6 x 1.6 mm; about 100 uA | | TUSB321 datasheet, sections 6.3 and 6.5, Table 2 | read |
| E15 | TUSB321RWBR on LCSC: part C139392, X2-QFN-12, listed -40 to +85 C (conflicts with the 0 to 70 C of E14) | stock and price not shown on the fetched page | https://www.lcsc.com/product-detail/C139392.html | read |
| E16 | TUSB321RWBR price at 1 piece about USD 0.51; TUSB320LIRWBR (C2836598, I2C part, JLCPCB "Extended") about USD 0.77 to 0.99 | cached listings, different dates | search result summaries from lcsc.com | snippet |
| E17 | NXP PTN5150A (LCSC C2651889): open-drain current-mode outputs, 5.1 kohm Rd, X2QFN-12 | price | https://www.lcsc.com/datasheet/lcsc_datasheet_2108070630_NXP-Semicon-PTN5150AHXMP_C2651889.pdf | snippet; price not found |
| E18 | Rohm BD91N01NUX: sink-side CC detection with integrated Rd | package, price, shop listing | search result | snippet; package and price not found |
| E19 | WCH CH224K (LCSC and JLCPCB C970725): PD 3.0 sink controller, ESSOP-10, JLCPCB "Extended", 5/9/12/15/20 V, 4 to 30 V supply, -40 to +90 C | price about USD 0.48 to 0.60 at 1 piece (cached) | https://jlcpcb.com/partdetail/CH224K/C970725 (read); prices from lcsc.com snippets | read (listing), snippet (price). Datasheet fetch gave 403: its 5 V behaviour, current reporting and CC handling without PD are not found |
| E20 | A dual comparator or a discrete window detector: part and price | | none searched | not found |
| E21 | Rating of the USB-C receptacle at 1.5 A and the shop's choice of receptacle | | none searched | not found |

## Decision criteria
Criterion 1 is a gate: an option that scores 0 on it cannot meet SYS-020 as amended and is excluded whatever its sum.

| # | Criterion | Weight (1-5) | Source requirement |
|---|-----------|--------------|--------------------|
| 1 | Delivers the rule: higher limit only when the source advertises it | 5 | SYS-020, HW-003 |
| 2 | Falls back to [500] mA when the value is unreadable or wrong (safe side) | 5 | SYS-020 (safety), RISK-003 |
| 3 | Added unit cost | 4 | SYS-021 |
| 4 | Parts available at the prototype shop, all SMD, one side | 4 | SYS-022 |
| 5 | Part count and board area (small ring board) | 3 | SYS-028, SYS-022 |
| 6 | Detection margin against the CC voltage bands | 4 | SYS-020, HW-003 acceptance (three sources) |
| 7 | Testable on the bench and in production (design for test) | 3 | HW-003, TC-203, DFx standard |
| 8 | Few processor pins used | 2 | HW-003 (module has few free pins) |
| 9 | Firmware effort and unit-testable logic | 2 | SYS-025, SYS-037 |

## Alternatives considered

### A. Read the CC voltages with the processor ADC
Two 5.1 kohm resistors to ground (the same as C). CC1 goes straight to one ADC1 pin and CC2 to another. Firmware reads both, takes the higher voltage, and compares it with one threshold.
Pins: GPIO0, GPIO1 and GPIO3 are on ADC1, are not strapping pins and are not USB pins (E9, E10). GPIO4 is also on ADC1 but is the JTAG MTMS pin. GPIO5 is on ADC2 and is not usable (E8, E12). GPIO2 is a strapping pin.
Range: the 12 dB attenuation covers 0 to 2500 mV with +-35 mV total error after calibration (E11). The highest CC voltage seen is 2.18 V (E6), and the 3 A band ends at 2.04 V (E4). Both are inside the range, but near the top where the error is largest. No divider is needed. A divider would load the CC line and shift the bands, so the design has none. HW-003 allows a divider only "if the input range needs it". It does not.
Rule: only one threshold is needed, because 1.5 A and 3 A both allow the high limit. The gap between the bands is 0.61 to 0.70 V (E4), 90 mV wide. A threshold in the gap leaves +-45 mV at the centre. The ADC error is +-35 mV (E11), which leaves 10 mV for noise, resistor tolerance and temperature. That margin is thin. Two measures: put the threshold on the safe side (nearer 0.70 V, so a default source is never read as 1.5 A, at the price of reading a weak 1.5 A source as default), and require several consecutive equal readings, with the average of many samples (E11 note on DNL). The typical voltages (0.41 / 0.92 / 1.68 V, E2) are far from the edges, so real sources should read with more margin than the band edges suggest. This needs a measurement.
Cons: accuracy with Wi-Fi active and the input behaviour are not documented (E13). The CC line can see VCONN or a fault voltage above the GPIO rating (E13, not found), so the pin needs a clamp or ESD diode and a series resistor. Zephyr ADC driver support for the C3 is not checked.
Cost: a small ESD part and two resistors at most; no extra IC. Pins: 2. Safe fallback: if the read fails, firmware stays at [500] mA.

### B. Dedicated USB-C sink or CC detection IC (TUSB321 type)
The IC carries its own Rd (E14) and reports the level on two open-drain outputs with a pull-up to 3.3 V: OUT1 low means 1.5 A or 3 A. Thresholds are set and specified by the vendor (E5). Firmware reads 2 GPIO pins. If the IC fails, the pull-ups read "default", which is the safe side.
Candidates, with what I found:
- **TI TUSB321** (LCSC C139392): X2QFN-12, 1.6 x 1.6 mm, 4.5 to 5.5 V, about 100 uA (all read, E14, E15). Price about USD 0.51 at 1 piece (snippet, E16). Conflict: the datasheet lists 0 to 70 C recommended, LCSC lists -40 to +85 C (E14, E15).
- **NXP PTN5150A** (LCSC C2651889): open-drain outputs, X2QFN-12 (snippet, E17). Price not found.
- **Rohm BD91N01NUX**: integrated Rd, detects current (snippet, E18). Package and price not found.
- TI TUSB320 variants have an I2C interface instead of two output pins (E16). Not needed.
Cons: another fine-pitch 1.6 mm package (can the shop place it? not checked); extra parts (decoupling, pull-ups, VBUS sense pin); "Extended" part at JLCPCB (setup fee per part; E16, TUSB320LI only); stock not confirmed.
Strength: the outputs can drive a hardware current-limit select directly, with no firmware in the loop (see consequences).

### C. USB Power Delivery negotiation with a PD sink controller
A PD sink controller negotiates a fixed 5 V contract. Example: WCH CH224K, ESSOP-10, about USD 0.48 to 0.60 (E19). This gives the contract current only when the source speaks PD. A plain charger that advertises 1.5 A with Rp, and no PD, would not be recognised unless the chip also reads Rp. I did not find whether the CH224K does (E19, not found). Many PD sources advertise the same current on CC too, so the owner decision (CC advertisement) is already met by A and B without PD.
Cons: PD adds a protocol, a larger part and more risk of a sink that fails to power up on a non-PD source. Current reporting and 5 V behaviour are not found. Overkill for a 5 V-only device. Benefit: a negotiated contract is stronger than a CC advertisement.

### D. Comparator window detection with discrete parts
One dual comparator with a threshold near 0.66 V on each CC line, a reference divider from the 3.3 V rail, and a wired-OR or two inputs to the processor. Parts: the comparator, about four to six resistors, a capacitor. No part searched (E20, not found).
Cons: the most parts for the same function as A; the reference follows the 3.3 V rail tolerance (not looked up), so the threshold shifts in the same range as the gap; comparator input bias loads the CC line; a hand-built detector needs its own verification. Strength: no ADC, no firmware timing, 1 to 2 digital pins.

### E. Do nothing: fixed 500 mA with two 5.1 kohm Rd
No detection. The limit is always [500] mA. Two Rd resistors to ground are still required: without them some chargers give no power (HW-003 rationale).
This is the baseline and the fallback in every other option. It does not deliver the owner decision (criterion 1 = 0). It leaves 46 to 148 mA for LEDs in the worst case (RISK-004).

## Comparison
Scores 0 to 5, my judgement from the evidence above. The weighted sums were computed with Python (weights 5, 5, 4, 4, 3, 4, 3, 2, 2; sum 32; maximum 160).

| Criterion (weight) | A ADC | B IC | C PD | D comparator | E do nothing |
|--------------------|-------|------|------|--------------|--------------|
| 1 Delivers rule (5) | 5 | 5 | 2 | 5 | 0 |
| 2 Safe fallback (5) | 4 | 5 | 3 | 4 | 5 |
| 3 Cost (4) | 5 | 3 | 2 | 3 | 5 |
| 4 Shop availability (4) | 5 | 3 | 3 | 4 | 5 |
| 5 Parts and area (3) | 5 | 3 | 3 | 1 | 5 |
| 6 Detection margin (4) | 3 | 4 | 4 | 3 | 5 (nothing to detect) |
| 7 Testability (3) | 4 | 4 | 2 | 3 | 5 |
| 8 Pins (2) | 3 | 3 | 4 | 4 | 5 |
| 9 Firmware effort (2) | 3 | 5 | 2 | 5 | 5 |
| **Weighted sum (max 160)** | 136 | 127 | 88 | 115 | 135 (excluded by gate 1) |

Reading: A leads B by 9 points. That is inside my scoring error. A wins on cost, parts and area. B wins on margin, safe fallback and firmware effort. The decision therefore depends on the spike in "Verification", not on the table. E scores high because it does nothing and is excluded by the gate. It is also the fallback of A (firmware stays at [500] mA).

## Decision
Recommend **A**: read both CC lines with two ADC1 inputs, no divider, with these rules. The owner decides; two points are open (marked **OPEN**).
1. **CC termination:** two 5.1 kohm resistors to ground on CC1 and CC2, the only load on the CC lines (HW-003). Each CC line also goes to one ADC1 pin through a series resistor and an ESD diode or clamp sized in design. The series resistor must not shift the bands (value checked in the spike).
2. **Pins:** two of GPIO0, GPIO1, GPIO3 (ADC1, not strapping, not USB). Final choice in the schematic, together with the LED data and button pins.
3. **Rule in firmware (in `core/`, unit tested on the PC):** take the higher of the two voltages. Below the attach level, or on any read error: [500] mA. At or above the threshold, held for several consecutive readings: advertised value (1.5 A and 3 A both count as "at least 1.5 A") minus [10] %, capped at [1500] mA, so 1350 mA. A value above the cap is still capped. Any change in the reading drops the limit to [500] mA first and raises it again after the readings are stable. Limit is set within [1] s of connection (SYS-020).
4. **Threshold:** inside the gap 0.61 to 0.70 V, on the safe side. Final value from the spike measurement.
5. **Order of events:** the limiter starts at [500] mA at boot, before the first read. The Wi-Fi radio is not needed for the read.
6. **Fallback to B:** I propose no second footprint on the board (area, SYS-028). If the spike fails, the next board revision moves to B. Owner may ask for a footprint instead.
7. **OPEN, owner: cap value.** I recommend the cap of [1500] mA from SYS-020 (1350 mA after margin) only if the connector, tracks and the shop's receptacle are rated for it (E21 not found; HW-003 acceptance). A cap of [900] mA is the fallback and still gives full white for variant A (spike 7.5, section 8).
8. **OPEN, owner: ADC or IC.** My recommendation is A. The owner may prefer B for the better margin and the firmware-independent outputs (see consequences).

## Consequences
- Positive: no extra IC; no extra unit cost beyond a few passives; E is the same board with firmware at 500 mA; the rule is plain logic that the PC can test with recorded voltages.
- **Negative / trade-offs accepted:** the margin of one ADC threshold in a 90 mV gap is thin (E4, E11); detection depends on firmware (no hardware path); two GPIO pins stay used; a weak 1.5 A source can be read as default (accepted, safe side).
- Relation to ADR-0004 item 4 (hardware backstop, not decided here): a load switch with a fixed current limit protects the connector and cable, not a source that advertises 500 mA. To protect a default source it needs two limits, selected by the advertised current. With A, the select line comes from firmware, so a firmware fault still removes the protection. With B, OUT1 could set the limit select in hardware (my idea, not checked in a datasheet). That is an argument for B if item 4 turns out to be required.
- New risks (proposed text for the risk register, not added there): **RISK-024** Source advertises 1.5 A but supplies less (weak charger, long cable, drop in the cable) and the device browns out or the source shuts down. **RISK-025** The CC voltage is read wrongly (ADC error, Wi-Fi noise, tolerance of Rd or Rp) and the device draws up to 1350 mA from a source that advertises 500 mA. **RISK-026** The CC pin sees a voltage above the processor pin rating (VCONN or a fault) and damages the ADC pin. RISK-003 must say that the limit value, not only the limiter, comes from a firmware read. RISK-005 changes: more dissipation at 1350 mA.
- Requirements created or changed: HW-003 already allows the ADC read path; add that the ADC pin has a clamp and that the safe threshold is on the default side. New SW requirement for the CC read and the limit rule (with a PC test). TC-203 needs a procedure (three sources). SYS-020 stays as written; criteria for the margin check should name the bands.

## Verification and revisit
- Spike (before the schematic is frozen): measure CC voltage and ADC readings on the C3 kit with 5.1 kohm to ground, using a USB-C to USB-A cable, one 1.5 A charger, one 3 A charger, and a bench source with a current source or resistor set to each Rp value, with the Wi-Fi in transmit. Record mean, spread, and temperature effect. Pass: the three classes never overlap, and the threshold keeps at least [20] mV beyond the worst reading on each side. Zephyr ADC driver support for the C3 is checked in the same spike.
- PC unit tests: the rule with all voltages from 0 to 2.5 V, error injection, stuck and noisy readings, cap and margin arithmetic.
- TC-203 on a prototype: three different sources, reported value within tolerance. TC-020: current at or below the limit that applies, no reset.
- Analysis: connector and track rating at 1350 mA in `hw/sim/` (HW-003).
- Revisit when: the spike fails the margin; the shop's X2QFN parts and prices are confirmed (then recompare B); ADR-0004 item 4 is decided as required; the cap value or the 10 % margin changes; a charger is found that misclassifies.

## Critical review notes
Strongest objection: "A 90 mV gap and a +-35 mV ADC, with Wi-Fi noise and unknown input behaviour, is too thin for a safety function. A dedicated IC costs about USD 0.5 and removes the doubt."
Answer: the objection is correct about the margin, and the table is close (136 against 127). Three things make A acceptable for a first board: the error direction is safe (any doubt means [500] mA); the real voltages are far from the band edges (E2); and a spike measures the margin before the schematic is frozen. If the spike fails, B is the fallback. I did not find a shop price or a placement check for the X2QFN parts, so B is not proven cheaper to build either.
Second objection: "Why not accept a 3 A advertisement as a 1.5 A-class device only?" Answer: no. Both count the same. The cap of 1350 mA applies to both.
Third objection: "The CC voltages come from secondary sources." Answer: yes, E7 is not found. The spike uses real sources, and TC-203 is the evidence. The values here must be checked against the specification before approval.
