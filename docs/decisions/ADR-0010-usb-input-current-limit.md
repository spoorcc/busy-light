# ADR-0010: Hardware current limit on the USB input

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-04
- **Deciders / reviewers:** Ben Spoor (owner); no goldfish review yet
- **Related:** NEED-003, SYS-020, SYS-021, SYS-022, HW-003, HW-004, HW-010, ADR-0004 (item 4), ADR-0009, RISK-003, RISK-004, RISK-005, RISK-024, RISK-025, RISK-026; `docs/verification/reports/spike-7-5-power-budget-paper.md`

## Context and problem
The device takes 5 V from a USB-C connector as a sink (SYS-020). The firmware reads the advertised current from the CC lines with the processor ADC (ADR-0009, owner choice). The allowed limit is [500] mA by default. It is the advertised value minus [10] % when the source advertises more, at most [1500] mA (so 1350 mA).
Owner decision of 2026-11-04 (HW-010, ADR-0004 item 4): the board has a hardware current limit. It starts at [500] mA with the firmware stopped. The firmware raises it, in steps, only after the CC read.
Why: a firmware-only limiter cannot protect a source that advertises 500 mA if the firmware fails or misreads the CC voltage (RISK-003, RISK-025).
The limiter must also:
- pass the Wi-Fi transmit peak (350 mA at 3.3 V, spike 7.5 E1) and the LED current (16 LEDs) without a false trip or a collapse of the 5 V rail (HW-004, RISK-004);
- start into the input capacitance without tripping (start-up inrush);
- block current from the output back to the USB input (back-feed).
Constraints: all-SMD parts from a prototype shop, one side (SYS-022; prefer "basic" parts and note "extended" part fees); total board cost EUR 10 to 20 (SYS-021).

Not known: the bulk capacitance on the 5 V rail (not designed yet, 100 uF is only an assumption in this ADR); the pin state of the chosen GPIO while the ESP32-C3 is in reset (not read); the JLCPCB class (basic or extended) of the candidate parts on the day of the order (only a listing for one part was read); accuracy of the limit at the 500 mA step for TPS25200 (table has no point there); the datasheet of SGM2523 (only the vendor product page was read).

## Evidence
Status of each source: **read** = I read the text of the document in this session (PDF downloaded, text extracted, or page text fetched); **snippet** = I saw it only in a search result; **not found** = I looked and did not find it. No value comes from memory.

| ID | Fact | Value | Source | Status |
|----|------|-------|--------|--------|
| E1 | TPS2553 (TI): limit programmed by one resistor RILIM from ILIM to GND, recommended 15 to 232 kohm. "Adjustable current limit: 75 mA to 1700 mA (typical)". ILIM tied to IN gives 50 / 75 / 100 mA (min/typ/max). ILIM must never be driven directly by a signal. ILIM source current max 1 mA | | https://www.ti.com/lit/gpn/tps2553 (SLVS841G, TPS2552/53 family), sections 1, 6.5, 8.5.1, 9.2.1 | read |
| E2 | TPS2553 limit tolerance (IOS, min/typ/max). RILIM 20 kohm: 1215 / 1295 / 1375 mA at 25 C, 1200 / 1295 / 1375 mA over -40 to 125 C. RILIM 49.9 kohm: 490 / 520 / 550 mA at 25 C, 475 / 520 / 565 mA over -40 to 125 C. RILIM 15 kohm: 1610 / 1700 / 1800 mA (-40 to 105 C). RILIM 210 kohm: 110 / 130 / 150 mA | | same, section 6.5 | read |
| E3 | TPS2553 limit equations in mA with RILIM in kohm: IOSmax = 22980 / R^0.94, IOSnom = 23950 / R^0.977, IOSmin = 25230 / R^1.016. They include temperature and process, not the resistor tolerance. (The text extraction listed them in the order max, nom, min. I checked them against the table of E2: R = 20 kohm gives 1202 / 1283 / 1375 mA, table 1200 / 1295 / 1375; R = 49.9 kohm gives 475 / 525 / 582, table 475 / 520 / 565.) | | same, equations (1) to (3); check: see "Verification of arithmetic" | read |
| E4 | TPS2553 has a TI application example for a two-level limit: "a logic-level input enables or disables MOSFET Q1 [2N7002] and changes the current-limit threshold by modifying the total resistance from ILIM to GND. Additional MOSFET and resistor combinations can be used in parallel to Q1/R2 to increase the number of additional current-limit levels." Example R1 = 210 kohm, R2 = 22.1 kohm | | same, section 9.2.1, Figure 9-1 | read |
| E5 | TPS2553 behaviour in overload: constant current IOS, the output voltage falls to IOS x RLOAD (no foldback below IOS). FAULT asserts after a 7.5 ms deglitch (3 to 11 ms). Version TPS2553 (no suffix) is "auto retry": it thermal-cycles (off above 135 C junction while in limit, back on after 10 C cooling). Version TPS2553-1 latches off after the deglitch until EN is toggled or power is cycled. Response to a short: 2 us typ | | same, sections 8.3, 9.1.1, Table 4-1 | read |
| E6 | TPS2553 other numbers: input 2.5 to 6.5 V; rDS(on) DBV package 85 mohm typ, 95 mohm max at 25 C, 135 mohm max over -40 to 125 C; supply current 120 uA typ, 150 uA max enabled (RILIM 20 kohm, VIN 6.5 V, no load), 0.1 uA typ, 1 uA max disabled; UVLO rising 2.35 V typ, 2.45 V max; rise time 1.1 ms typ, 1.5 ms max (VIN 6.5 V, 1 uF, 100 ohm); thermal shutdown 155 C min (135 C min while in current limit); packages SOT-23-6 and WSON-6 2x2 | | same, sections 1, 6.5 | read |
| E7 | TPS2553 reverse protection: the switch turns off when VOUT exceeds VIN by 135 mV typ (95 to 190 mV) for 4 ms typ (3 to 7 ms). During those ms a reverse current of (VOUT - VIN) / rDS(on) flows. FAULT also asserts. Reverse leakage with VIN = 0 V and VOUT = 6.5 V: 0.01 uA typ, 1 uA max (25 C) | | same, sections 8.3.2, 6.5 | read |
| E8 | TPS2553DBVR on JLCPCB: C55266, SOT-23-6, library type **Extended**. Stock and price not shown on the page I fetched | | https://jlcpcb.com/partdetail/TexasInstruments-TPS2553DBVR/C55266 | read (class); price and stock not found there |
| E9 | TPS2553DBVR stock about 35,914 on JLCPCB; price about USD 0.20 at 1 piece and about 0.10 at 3,000 pieces; LCSC snapshots 17,475 in stock, USD 0.20 to 0.23 at 5+ | | search result summaries of jlcpcb.com and lcsc.com (C55266) | snippet |
| E10 | TPS2553DBVR-1 (latch-off, C111738): JLCPCB "Extended"; LCSC shows 1,768 in stock and "not recommended for new designs" | | https://www.lcsc.com/product-detail/C111738.html | snippet |
| E11 | TPS25200 (TI 5 V eFuse): 2.5 to 6.5 V, input withstands 20 V, overvoltage lockout 7.6 V, output clamp 5.4 V, 60 mohm typ (70 mohm max at 25 C, 90 mohm max at 85 C), reverse current blocking while disabled, limit 85 mA to 2.9 A with one resistor, RILIM at least 33 kohm (UL), DRV (WSON-6, 2 x 2 mm). Limit table: 150 kohm gives 590 / 647 / 710 mA; 1100 kohm gives 40 / 83 / 130 mA. Supply current 143 uA typ, 200 uA max enabled (33 kohm), 0.8 uA typ, 5 uA max disabled. Reverse leakage 3 uA typ, 5 uA max. Constant-current limit with thermal cycling (no latch version). FAULT deglitch 8 ms. Output discharge 480 ohm typ | | https://www.ti.com/lit/gpn/tps25200 (SLVSCJ0F, July 2025), sections 1, 5.5, 7.3 | read |
| E12 | TPS25200 limit accuracy at the 500 mA step (RILIM about 190 to 200 kohm): table has no point there | | same | not found |
| E13 | TPS25200DRVR: LCSC C128401, price from USD 0.1489 (one snapshot) or USD 0.185 at 5+ (another), stock 630 or 4,323 (two snapshots). JLCPCB class of the DRVR part not found. The DRVT variant (C2653855) is listed "Extended" | | search result summaries of lcsc.com and jlcpcb.com | snippet |
| E14 | TPS25925x (TI 5 V eFuse, VSON-10 3 x 3 mm): adjustable ILIMIT **2 A to 5 A**, +-15 %, 30 mohm; supply current 0.35 / 0.42 / 0.6 mA enabled; versions latched (TPS259250) and auto-retry (TPS259251). The lowest limit (2 A) is far above 500 mA | | https://www.ti.com/lit/gpn/tps25925 (SLVSCQ3B), sections 1, 6 | read |
| E15 | TPS20xxC family (TI fixed-limit switches), "0.5-A rated" part TPS2051C: current limit IOS 0.67 / 0.85 / 1.01 A (min/typ/max) at 25 C; 0.65 / 0.85 / 1.05 A over temperature. 1.5-A rated: 1.7 / 2.15 / 2.5 A. rDS(on) 97 mohm typ, 110 mohm max at 25 C (DBV). Supply current enabled 65 uA typ, 90 uA max. UVLO rising 3.5 / 3.75 / 4.0 V. Input 4.5 to 5.5 V. Overload: constant current, then thermal cycling (restart after 20 C cooling). FLT deglitch 6 / 9 / 12 ms. Reverse leakage 0.2 uA typ, 20 uA max. SOT-23-5 | | https://www.ti.com/lit/gpn/tps2051c (SLVSAU6I, family TPS20xxC), sections 1, 6.6, 6.7, 8 | read |
| E16 | TPS2051CDBVR: LCSC C129581, SOT-23-5, 4.5 to 5.5 V; price | | https://www.lcsc.com/product-detail/C129581.html | snippet (listing); price not found; JLCPCB class not found |
| E17 | SGM2523 (SG Micro, "active programmable current limit switch", eFuse): input 2.6 to 22 V (surge to 30 V), 75 mohm, programmable limit 100 mA to 1.6 A, +-10 % at 25 C, programmable soft start, SOT-23-6. A version: limited-current mode on overcurrent, thermal auto-retry. B version: shutdown mode, thermal latch-off. "Protects input from undesired shorts and transients coming from the output". Vendor price (SGMICRO, 1 to 24 units): USD 0.875 per unit | | https://www.sg-micro.com/product/SGM2523 (product page, not the datasheet) | read |
| E18 | SGM2523: formula or resistor for the limit, quiescent current, accuracy over temperature, reverse-current numbers, any two-level circuit | | datasheet PDF not fetchable (the LCSC link returned an HTML page) | not found |
| E19 | SGM2523AXN6G/TR: LCSC C5153396, USD 0.388 at 30+ and 0.3289 at 100+; JLCPCB class not found | | search result summary of lcsc.com | snippet |
| E20 | Diodes AP22802 (SOT25): fixed overload limit 2.2 / 2.7 / 3.2 A, short-circuit 1.1 A typ, 2.7 to 5.5 V, thermal shutdown 140 C, reverse current blocking, FLG output. Status on the first page: "Not recommended for new design, use AP22811". Fixed limit and not recommended for new designs: not a candidate | | https://www.diodes.com/assets/Datasheets/AP22802.pdf | read |
| E21 | Other parts seen only in search results and not read: MP5013E (MPS, 5 V, 2 A, programmable limit, TSOT23-8); MP5042 (MPS, 25 mA to 2 A, TSOT23-6, input 4.2 to 28 V); MAX4772/MAX4773 (Maxim, logic input selects a 200 mA or 500 mA limit); TPS2559 (TI, limit 1.2 to 4.7 A with 24.9 to 100 kohm, too high for the 500 mA step); TPS2141/TPS2151 (TI, dual current limit, 14-pin HTSSOP); Microchip UCS2113 (limit set at power-up by a resistor). TPS2557 and Richtek parts: no search done | | search result summaries | snippet (all); TPS2557 and Richtek not searched |
| E22 | Spike 7.5: Wi-Fi TX peak 350 mA at 3.3 V (MINI-1, 802.11b 1 Mbps, 100 % duty); worst case on the 3.3 V rail 454 mA with CPU and 20 % margin; LED full white 16 x 3 x 5 mA = 240 mA (variant A) or 16 x 3 x 12 mA = 576 mA (variant B); 46 mA (LDO) or 148 mA (buck 85 %) left for the LEDs at 500 mA. Power-up and Wi-Fi calibration inrush: not found | | `docs/verification/reports/spike-7-5-power-budget-paper.md` (E1, E16, E17, L1, L6) | read |
| E23 | Type-C or USB rule for the maximum input capacitance (inrush) of a sink | | not searched | not found |
| E24 | ESP32-C3 GPIO state during reset and boot (pull-up or pull-down, high impedance) for the pin to be used as limit select | | not read in this session | not found |
| E25 | Discrete foldback (option E): comparator, sense resistor and MOSFET part numbers and prices | | none searched | not found |
| E26 | PTC polymer fuse (option D): hold and trip current, trip time, and part number at the shop | | none searched | not found |

## Decision criteria
Criteria 1 and 2 are a gate. An option that scores 0 or 1 on either cannot meet HW-010 and is excluded whatever its sum.

| # | Criterion | Weight (1-5) | Source requirement |
|---|-----------|--------------|--------------------|
| 1 | Limit is [500] mA (plus part tolerance) in hardware with the firmware stopped | 5 | HW-010, SYS-020, RISK-003, RISK-025 |
| 2 | Firmware can raise the limit in steps up to the advertised value minus [10] %, cap [1500] mA | 5 | HW-010, SYS-020 |
| 3 | Tolerance band fits both ends: not below the firmware budget, not above what the source advertises | 4 | SYS-020, RISK-024, RISK-025 |
| 4 | Passes legitimate peaks and inrush without a false trip, latch-off or voltage collapse | 4 | HW-004, RISK-004 |
| 5 | Added unit cost | 4 | SYS-021 |
| 6 | Parts at the prototype shop, all SMD, one side; basic parts preferred | 4 | SYS-022 |
| 7 | Part count and board area | 3 | SYS-022, SYS-028 |
| 8 | Stated over-temperature, short-circuit and reverse-current behaviour; fault flag | 4 | HW-010 acceptance, RISK-005 |
| 9 | Testable on the bench and in production (design for test) | 3 | HW-010 (TC-210), DFx standard |
| 10 | Firmware effort and pins | 2 | HW-010, ADR-0009 |

## Alternatives considered

### Power-up behaviour in every option (firmware stopped)
The processor is downstream of the limiter. So the switch must be on at power-up, with no help from the firmware. Rules for any option: the enable input is pulled up to VIN with a resistor; the limit select line has a pull-down resistor (about 100 kohm) so the higher-limit path is off when the GPIO is high impedance or in reset. This gives the [500] mA limit with the processor in reset or unpowered. It does **not** hold if the firmware is hung with the GPIO driven high. That case is outside HW-010 "firmware stopped (held in reset)". It is an owner-open point (see "Owner-open points"). The GPIO state during reset is E24, not found.

### A. Adjustable-limit USB power switch, limit resistor switched by the firmware
The limit is set by the total resistance from ILIM to GND (E1). A main resistor R1 sets the 500 mA step. One or two small N-channel MOSFETs, driven by GPIO pins, put resistors R2 and R3 in parallel with R1 for higher steps. TI documents this circuit for the TPS2553 (E4).
Candidates:
- **A1 TPS2553 (TI), recommended.** SOT-23-6 (E6). 2.5 to 6.5 V. 85 mohm typ. Enabled supply current 120 to 150 uA (E6). Limit 75 mA to 1.7 A (E1). Tolerance see E2, E3. Auto-retry thermal cycling, no latch, FAULT after 7.5 ms (E5). Reverse protection with 4 ms delay (E7). JLCPCB **extended** part C55266 (E8), price about USD 0.20 at one piece (E9, snippet). The latch-off version TPS2553-1 is not recommended for new designs (E10, snippet) and would also latch on a legitimate overload.
- **A2 TPS25200 (TI).** WSON-6 2 x 2 mm. Input withstands 20 V and the output clamps at 5.4 V (E11). That protects against a wrong-voltage source, which a USB-C receptacle can meet. Pin-compatible with the TPS2553 per its feature list (E11). Accuracy at the 500 mA step: not found (E12). Class at JLCPCB: not found (E13). The 20 V tolerance is a real benefit, but the lower step is not specified, so A1 stays first choice.
- **A3 SGM2523 (SG Micro).** See option C. It is an eFuse with the same resistor idea.
- **AP22802 (Diodes):** fixed 2.7 A, not recommended for new designs (E20). Excluded.
Limit values for A1, from the equations E3 (checked with Python, see "Verification of arithmetic"):

| Step | Resistor (parallel result) | Min / nom / max limit (mA), resistor +-1 % | Meaning |
|------|---------------------------|----------------------------------------------|---------|
| 1 (start-up) | R1 = 46.4 kohm | 506 to 511 / 558 to 564 / 618 to 623 | min at or above 500 mA |
| 2 | R1 in parallel with 59.0 kohm = 25.97 kohm | 913 to 932 / 984 to 1004 / 1066 to 1086 | for a 1.0 A class value |
| 3 (top) | R1 in parallel with 28.0 kohm = 17.46 kohm | 1366 to 1394 / 1451 to 1479 / 1548 to 1577 | min at or above 1350 mA |

Finding: the tolerance band is wide (-10 / +10 % around nominal, plus resistor). Two readings follow.
1. At step 1, the lowest limit is about 506 mA and the highest is about 623 mA. The hardware limit is above 500 mA by up to 25 %. HW-010 allows "500 mA plus the tolerance of the limit part". If the owner wants a hard 500 mA ceiling, R must be about 59 kohm and the minimum falls to about 395 mA, below the firmware budget of 500 mA. A firmware budget of 450 mA would then be needed. This is a trade-off for the owner (see open points).
2. At step 3 a limit above 1500 mA is possible (up to about 1577 mA). A source that advertises 1.5 A may not supply that. To keep the maximum at or below 1500 mA, R must be about 18.4 kohm. The minimum then falls to about 1294 mA, which is below the 1350 mA firmware value (RISK-024: the firmware value is then the more limiting number and the hardware limit may trip on a legitimate 1350 mA draw). The margin of [10] % is smaller than the tolerance band of the part. This is the main finding of this ADR for the owner.
Start-up with the processor in reset: R1 only, because the MOSFET gates are pulled down. R1 open (fault) gives a lower limit, so the failure goes to the safe side. A shorted MOSFET gives the higher step. That single fault is not covered (see risks).
LED and Wi-Fi peaks: the limit is constant-current, not foldback (E5). A legitimate peak above the limit does not trip or latch. The output voltage falls until the load current falls. This matters because a buck converter is a constant-power load: when the 5 V rail falls, the buck draws more current, and the rail can collapse (RISK-004). The input capacitor of the buck and the bulk capacitor on the 5 V rail must carry the peak. A peak of 1 ms that is 100 mA above the limit takes 0.1 A x 1 ms / 100 uF = 1 V of droop on the 5 V rail (my arithmetic, assumed 100 uF). So the firmware budget must keep the sum of Wi-Fi and LED current below the minimum hardware limit, and the capacitor covers only short peaks. The FAULT deglitch of 7.5 ms (E5) stops a false flag on short peaks.
Start-up inrush: the output rise time is 0.7 to 1.5 ms (E6). With an assumed 100 uF, charging at constant 5 V in 1.1 ms needs about 0.45 A. That is inside the 500 mA step. A larger capacitance (220 uF gives 1.0 A on the same ramp) makes the switch sit in current limit during the ramp, which is allowed (constant current, 2.2 ms at 0.5 A), but it must not exceed the thermal limit: at 5 V across the switch and 0.5 A the power is 2.5 W for a short time. The USB rule on sink capacitance is not found (E23).
Reverse current: protected by the reverse-voltage comparator after 4 ms and by a 1 uA leakage with VIN at 0 V (E7). The board has no second power source, so back-feed comes only from the output capacitance and the USB-C connector side. The 4 ms window is acceptable for a sink-only device.
Cost: switch about USD 0.10 to 0.20 (E9, snippet), two small MOSFETs, three or four resistors. Extended-part fee for the switch (and for the MOSFETs if not basic parts; class not found). Pins: 2 GPIO (one per step above 1) plus an optional FAULT input.
Cons: tolerance band wider than the margin (see above); extended part fee; accuracy at 500 mA relies on a 1 % resistor; two GPIO pins; the datasheet advises that the traces from RILIM be short.

### B. Two fixed-limit switches in parallel, the second enabled by the firmware
The TPS20xxC family has fixed limits in steps of rated current (E15). The "0.5-A rated" part TPS2051C has a limit of 0.67 to 1.01 A (E15). That is already above 500 mA by 34 to 100 %. The next rating (1 A) limits at 1.3 to 1.8 A. Two switches in parallel add their limits: 0.85 A typ + 0.85 A typ = 1.7 A typ for two 0.5 A parts. No fixed combination gives a first step at 500 mA or a top step at 1350 mA. Paralleling switches that limit on their own also shares current badly (my reasoning, not from a datasheet). The undervoltage lockout of 3.5 to 4.0 V (E15) is also higher than for the TPS2553.
Verdict: fails the gate (criteria 1, 2). A fixed part with a limit of about 500 mA was not found in the sources I read (the MAX4772/MAX4773 selectable 200/500 mA parts were not read, E21).

### C. eFuse or hot-swap controller with a programmable limit
- **TPS25925x (TI):** limit 2 to 5 A only (E14). Fails criterion 1.
- **SGM2523 (SG Micro):** 100 mA to 1.6 A, +-10 % at 25 C, 75 mohm, 2.6 to 22 V, SOT-23-6, auto-retry (A) or latch-off (B) (E17). It could use the same switched-resistor circuit as A, but the datasheet was not read, so the formula, the quiescent current and the reverse-current figures are not found (E18). Price USD 0.875 at one piece from the vendor (E17), USD 0.388 at LCSC 30+ (E19, snippet). The wide input range protects against a bad source. The limit is 1.6 A at most, which covers the 1350 mA step with a tolerance of 10 % (about 1485 mA). That is tighter than A1 at 25 C, but over temperature it is not found.
- **TPS25200 (TI):** see A2.
- **MP5013E, MP5042 (MPS):** seen in search results only (E21). Not evaluated.
An eFuse with a digital or analog limit input was not found among the parts above. The resistor-switching idea of A applies to the eFuses too.
Verdict: possible, not better than A1 on the evidence read. Higher price and less evidence.

### D. Polymer resettable fuse (PTC) sized for the cap, firmware-only dynamic limit
A PTC with a hold current of at least 1.5 A protects the connector and tracks. It gives no 500 mA guarantee at start-up. A source that advertises 500 mA is not protected, which is the case HW-010 wants to cover. A PTC also adds a voltage drop and its trip current depends on temperature. No part was searched (E26).
Verdict: fails the gate (criterion 1). It could be added in addition to A for the connector (not decided here).

### E. Discrete MOSFET, sense resistor and comparator (foldback)
A P-channel or N-channel MOSFET, a sense resistor of about 50 to 100 mohm, a comparator and a reference, with a switched threshold. Pro: full control of foldback and trip behaviour. Cons: at 500 mA a 100 mohm resistor gives 50 mV, so the comparator offset (a few mV) is 5 to 10 % of the signal; at least eight parts; the loop stability with a capacitive load and the behaviour at start-up (comparator supply) must be designed and verified by simulation; no part searched (E25). A hand-built limiter also needs its own proof for short-circuit and thermal behaviour (HW-010 acceptance).
Verdict: possible. More parts and more design risk than A for a device with a EUR 10 to 20 budget.

### F. Do nothing: firmware-only limiter (ADR-0004 as it stands)
No hardware limit. The limit is a software function. Cost zero. Does not meet HW-010 and leaves RISK-003 and RISK-025 with the firmware as the only protection. Excluded by the gate. It is also the fallback of every other option if the limiter is removed in a cost-down.

## Comparison
Scores 0 to 5, my judgement from the evidence above. Weighted sums computed with Python (weights 5, 5, 4, 4, 4, 4, 3, 4, 3, 2; sum 38; maximum 190). Gate: criteria 1 and 2 must score 2 or more.

| Criterion (weight) | A TPS2553 + switched R | B fixed pair | C eFuse (SGM2523 class) | D PTC + firmware | E discrete | F do nothing |
|--------------------|-----|-----|-----|-----|-----|-----|
| 1 Hardware 500 mA at start (5) | 5 | 0 | 3 | 0 | 4 | 0 |
| 2 Raisable in steps (5) | 5 | 1 | 3 | 2 | 4 | 0 |
| 3 Tolerance fits (4) | 3 | 0 | 4 | 2 | 2 | 5 |
| 4 Peaks and inrush (4) | 4 | 3 | 4 | 4 | 2 | 5 |
| 5 Cost (4) | 5 | 4 | 3 | 5 | 3 | 5 |
| 6 Shop availability (4) | 4 | 3 | 3 | 4 | 3 | 5 |
| 7 Parts and area (3) | 3 | 3 | 3 | 5 | 1 | 5 |
| 8 Stated fault behaviour (4) | 5 | 4 | 4 | 2 | 2 | 1 |
| 9 Testability (3) | 4 | 3 | 3 | 2 | 2 | 5 |
| 10 Firmware and pins (2) | 4 | 5 | 4 | 3 | 4 | 3 |
| **Weighted sum (max 190)** | 163 | 89 | 128 | 105 | 105 | 120 |
| Gate | pass | fail | pass | fail | pass | fail |

Reading: A leads C by 35 points. That is more than my scoring error. The reason is evidence: for A1 I read the datasheet, the tolerance table and a TI application example for exactly this circuit (E1 to E7). For C I read only a vendor product page (E17, E18). The score of C would rise if its datasheet shows a better tolerance and a stated two-level circuit. A scores 3 on criterion 3 because the TPS2553 band is wider than the [10] % margin (see A). F scores 120 and E 105 only because they do little or are hard to verify; F is excluded by the gate.

## Decision
**Recommend A1: TPS2553 (SOT-23-6, auto-retry version) with R1 for the 500 mA step and one or two N-channel MOSFET + resistor branches for the higher steps.** This ADR stays Proposed until the owner sets Accepted. Values in brackets are working values.
1. **Start-up:** EN is pulled up to VIN. The MOSFET gates have pull-downs (about 100 kohm). With the processor in reset only R1 is in circuit. The limit is then 506 to 623 mA (R1 = 46.4 kohm, E3, 1 % resistor), see open point 1.
2. **Steps:** [500] mA at start; one step near [900] mA and one step for the top value. The firmware raises the limit only after the CC read (ADR-0009) and the CC stable-reading rule, and lowers it first on any change or error. Final step count and resistor values are a design task with the tolerance finding of option A.
3. **Fault handling:** the FAULT output goes to a processor input (and is logged). The firmware answers a fault by dropping to the lowest step. Auto-retry (not latch-off) is chosen because a latched switch on a legitimate Wi-Fi/LED peak would leave the unit dead until the user unplugs it. Thermal cycling is allowed by the datasheet (E5); it gives no hazard at 5 V and below 1.5 A, but the switch dissipates up to 2.6 W for a short-circuit at the 500 mA step (5 V x 0.52 A). That is checked in the thermal analysis (see "Verification and revisit").
4. **Back-feed:** accepted as in E7. There is no second source on the board.
5. **Alternative to keep open:** TPS25200 (A2) if the owner wants 20 V input tolerance and the 5.4 V clamp for a USB-C source with a wrong VBUS. Pin-compatible per E11, but the 500 mA step needs the table point found (E12).
6. **No second footprint** is proposed (area, SYS-028).
The recommendation is mine. The owner decides. Points marked OPEN below are not decided.

## Consequences
- Positive: the 500 mA limit is in hardware when the processor is in reset (HW-010); the part is documented, with a TI two-level circuit (E4) and a stated overload and reverse behaviour (E5, E7); about USD 0.2 for the switch (snippet, E9) plus a few passives; RISK-003 and RISK-025 get a hardware backstop for the "firmware stopped" case.
- **Negative / trade-offs accepted:** the hardware band is wide: at step 1 up to about 623 mA (+25 % over 500 mA), at the top step up to about 1577 mA unless the resistor is lowered (then the minimum falls below 1350 mA); a "basic" part was not found, so the switch is an extended part with a per-part fee at JLCPCB (E8; the amount of the fee was not looked up); the limit is a constant-current clamp, so a peak above the limit collapses the 5 V rail instead of tripping cleanly; two GPIO pins and a FAULT input; the limit does not cover a firmware that hangs with the GPIO high; a shorted limit MOSFET gives the higher step.
- New risks (proposed text for the risk register, not added there): **RISK-027** The hardware limit band is wider than the [10] % margin (up to +25 % at 500 mA, up to about +5 % over the advertised 1500 mA at the top step), so the limit does not protect a source at its exact rating, or trips below the firmware value. **RISK-028** A peak above the limit lets the 5 V rail collapse because the buck is a constant-power load; the unit resets (links RISK-004). **RISK-029** The limit select GPIO is driven high while the firmware hangs, or the select MOSFET shorts; the higher step stays on after a firmware fault. **RISK-030** The chosen switch is an extended part, goes out of stock or is not recommended for new designs (as for TPS2553-1 and AP22802, E10, E20); the board needs a re-layout for another part. Existing risks: RISK-003 and RISK-025 residual text changes from "hardware backstop open" to "backstop with the stated band"; RISK-005 changes: switch dissipation at 1350 mA is 0.155 W typ and 0.246 W at the maximum rDS(on) (my arithmetic from E6).
- Requirements created or changed: HW-010 (Draft) says "[500] mA plus the tolerance of the limit part". The owner should decide the allowed band (open point 1), then HW-010 states the band as numbers. New HW requirement or acceptance text for the FAULT input, the pull-up on EN and the pull-downs on the select lines. HW-004 gets the capacitor sizing for the peak. SW requirement: raise only after the CC read, drop first on a fault. TC-210 gets the procedure (below).

## Verification and revisit
Verification of arithmetic (done in this session, Python script in the scratchpad, not committed): the equations E3 reproduce the table E2 within 3 % at 20 kohm and 49.9 kohm (E3 note). Resistor values above use E96 1 % values. Weighted sums: A 163, B 89, C 128, D 105, E 105, F 120. Rail sums as in spike 7.5: 3.3 V rail 454 mA; 5 V side 352 mA (buck 85 %). Rise time and capacitor figures use the assumed 100 uF.
Planned evidence:
- Bench (TC-210): firmware held in reset, 5 V supply with a current meter, an electronic load on the 5 V rail raised until the switch limits; record the limit at each step with three board samples and the resistor tolerance. Pass: at step 1 the limit is within the band that the owner accepts (open point 1); step 3 at or above 1350 mA and not above the owner's ceiling.
- Short-circuit on the LED supply with the firmware in reset: input current at or below the step-1 maximum, switch thermal cycles and recovers (HW-010 acceptance). Record the case temperature.
- Peak test (HW-004, TC-204): continuous Wi-Fi transmit with the LEDs at the limited maximum at each step, a scope on the 5 V rail and the 3.3 V rail. Pass: no reset in [10] min and no FAULT assertion. Also a step of load from 0 to the limit plus 100 mA for 1 ms to see the rail droop.
- Inrush: scope of the input current at plug-in with the real bulk capacitance.
- Simulation: ngspice model of the ILIM circuit is not available from TI in the sources I read (not found); a simple behavioural model of the clamp plus the buck as a constant-power load is proposed in `hw/sim/` to check the collapse (RISK-028).
- Datasheet copy of the chosen part in `hw/datasheets/` (HW-010).
- Not run: anything on hardware; the JLCPCB class and stock of every part on the order day; the TPS25200 limit at 500 mA; the SGM2523 datasheet; the ESP32-C3 pin state in reset (E24).
Revisit when: the owner changes the margin or the cap; the bench band is wider than the owner accepts; the switch becomes unavailable or not recommended for new designs; a basic fixed-limit part with about 500 mA is found; the SGM2523 datasheet shows a tighter band over temperature; ADR-0009 moves to a CC IC (then the IC output could select the limit in hardware, my idea, not checked in a datasheet).

## Critical review notes
Strongest objection: "The part's tolerance (about -10 / +10 % of the nominal limit, plus resistor tolerance) is larger than the [10] % margin the owner chose. So the hardware limit cannot protect a source at its exact advertised value, and may trip on a legitimate draw. It is a backstop with a wide net, not a precise limiter."
Answer: the objection is correct (see option A, finding). The limiter is a backstop for faults, not the control loop. The firmware stays the precise limiter, with the [10] % margin. The hardware limit protects against a stopped or wrong-reading firmware at the 500 mA step, where the owner's concern lies, and against a short circuit. What the owner must decide is whether the band is acceptable (open point 1). Without the hardware limit the case "source advertises 500 mA, firmware misreads" has no protection at all.
Second objection: "Constant-current limiting with a buck load can collapse the rail, so the limiter makes a brown-out worse." Answer: yes, if the firmware budget is above the hardware minimum. So the firmware budget must stay below the minimum limit at each step, and the bench test peaks must show it (RISK-028). A reset after a collapse is safe (the limit falls back to step 1).
Third objection: "The TPS2553 is an extended part and has a fee at JLCPCB; a basic part would be cheaper." Answer: no basic candidate was found in this research (E8, E16, E19: class not found for the others). The fee was not looked up. The cost against SYS-021 must be checked in the real quote (TC-021).
Fourth objection: "Most of the numbers come from one family datasheet." Answer: yes, for A1. They were read in the document (E1 to E7), and the same page has the two-level circuit. The prices and stocks are snippets.

## Owner-open points
1. **OPEN, band at the 500 mA step.** Options: (a) R1 = 46.4 kohm, limit 506 to 623 mA, firmware budget 500 mA (my recommendation: the firmware never meets the limit); (b) R about 59 kohm, limit at most 500 mA but as low as 395 mA, firmware budget about 450 mA (HW-010 wording "500 mA" strictly kept).
2. **OPEN, top step ceiling.** Minimum 1366 mA and maximum up to 1577 mA (above the 1500 mA cap), or maximum at or below 1500 mA with a minimum of 1294 mA (below the 1350 mA firmware value). I recommend the first and a firmware value of 1350 mA, but the owner decides whether a hardware ceiling above 1500 mA is acceptable.
3. **OPEN, number of steps.** Two (500 / top) or three (500 / about 900 / top). Three need two MOSFETs and two GPIO pins. Two are enough for the owner rule in SYS-020.
4. **OPEN, hung firmware.** Accept that a hung firmware with the GPIO high keeps the higher step, or add a circuit that drops the step without the firmware (for example a watchdog output). I propose to accept, because the watchdog resets the processor (the reset releases the GPIO).
5. **OPEN, TPS2553 versus TPS25200.** The TPS25200 adds a 20 V input and a 5.4 V clamp for USB-C; its 500 mA step is not specified in the table I read.
6. **OPEN, extended-part fee.** The owner accepts the extended-part fee of the switch (amount not looked up) or asks for a search of a basic part.
