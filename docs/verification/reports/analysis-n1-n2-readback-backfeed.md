# Analysis N1 and N2: gate-enable readbacks and D+ back-feed (full-board spike)

Status: analysis from datasheet text and hand calculation. Nothing here was measured, simulated in SPICE or run on hardware.
Answers findings N1 and N2 of `review-full-board-goldfish-2.md`. Traces: HW-010 (Proposed amendment), SW-009, RISK-044, ADR-0016 (all Proposed/Draft; nothing is approved by this report).
Calculation script: `hw/kicad/spike-gate/sim/readback_margin.py`; regression test: `hw/kicad/spike-gate/tests/test_readback_margin.py`.

## 1. Sources and assumptions

| Item | Value | Source |
|---|---|---|
| GPIO20 reset state | "3" = input enabled, weak pull-up (IE + WPU) | ESP32-C3 TRM v1.4 Table 5.12-1 and legend (local PDF); datasheet Table 2-1 note 5 |
| GPIO21 reset state | "4" = output enabled + WPU (U0TXD; UART idle level high) | same |
| Internal pull-up RPU | 45 kohm typ, no min/max given | ESP32-C3 datasheet Table 5-4 (local PDF) |
| Input levels at VDD = 3.3 V | VIH = 0.75 VDD (2.475 V), VIL = 0.25 VDD (0.825 V); IIH, IIL max 50 nA; VOH min 0.8 VDD | same table (identical in ESP32-C3-MINI-1 datasheet Table 6-3) |
| 2N7002 Vgs(th) at Id = 0.25 mA | min 1.0 V, typ 2.0 V, max 2.5 V at 25 C; min 0.6 V at 150 C; max 2.75 V at -55 C | **Not in the local datasheet folder.** Web search result: a Scribd copy of the Nexperia 2N7002 datasheet Rev. 7 (https://www.scribd.com/document/347020335/2N7002-pdf), consistent with distributor listings (Arrow, RS). Secondary copy, **assumption until the exact vendor datasheet of the chosen part is read**. Other family members differ (2N7002PV: 1.1 to 2.4 V) |
| TPS2553 | UVLO rising 2.35 min / 2.45 max V, hysteresis 25 mV (TJ = 25 C); EN threshold 0.66 to 1.1 V; IN 2.5 to 6.5 V; reverse-voltage comparator trips at OUT - IN = 95 / 135 / 190 mV, turn-off 3 to 7 ms; FAULT asserts on reverse voltage; Rds(on) 85-95 mohm (DBV) | TPS2552/53 SLVS841G sections 6.3, 6.5, 8.3.2, 8.3.4 (local PDF) |
| 74LVC1G11 output | VOH >= VCC - 0.1 V at -100 uA; 2.4 V at -16 mA (VCC = 3 V); VOL <= 0.1 V at 100 uA | SN74LVC1G11 datasheet (local PDF) |
| USBLC6-2 steering diode | VF 1.1 V max at IF = 10 mA; no value at 0.2 to 2.5 mA | USBLC6-2 datasheet (local PDF). **Assumption:** VF = 0.5 to 0.6 V in the 0.2 to 2.5 mA range (silicon junction, as in the review) |
| TUSB321 supply current | 100 uA typ unattached, VDD = 5 V; behaviour below the 4.5 V minimum not specified | TUSB321 SLLSEO6C |

## 2. N1: readback resistors versus the "lowest step" rule

### 2.1 Quantification of the finding (old values R14/R15 = 1 k, R2/R3 = 100 k)

Gate output open (or not driving). Net voltage = V_MCU-side x R2 / (R2 + R14 + R_source). VDD taken at its 3.6 V maximum (worst case):

| Case | Net voltage | Against Vgs(th) 1.0 / 2.0 / 2.5 V |
|---|---|---|
| GPIO21 output high (reset state, ROM TX idle) | 3.56 V | above max: Q3 fully on |
| Input with WPU 45 k (GPIO20 reset, GPIO21 once input) | 2.47 V | above typ, about at max |
| Input with WPU 30 k (assumed spread) | 2.75 V | above max |
| Input with WPU 70 k (assumed spread) | 2.11 V | above typ |

N1 is confirmed: with the old values the readback holds the enable above Vgs(th) min in every open-output case, so the limit rises with firmware stopped, against the HW-010 acceptance text. Before the readbacks, an open output resolved low through R2/R3.

### 2.2 Fix chosen: R14/R15 = 100 k, R2/R3 = 10 k

Ratio R2 / (R2 + R14) = 0.091. Gate output open:

| Case | Net voltage (VDD = 3.6 V) | Margin to Vgs(th) min 1.0 V | Margin to 0.6 V (150 C min) |
|---|---|---|---|
| GPIO21 drives high | 0.33 V | 0.67 V (3.0x) | 0.27 V (1.8x) |
| Input, WPU 30 k / 45 k / 70 k | 0.26 / 0.23 / 0.20 V | >= 0.74 V | >= 0.34 V |

Test requires every case below 0.6 V / 1.5 = 0.4 V (passes, worst 0.33 V). Contention with a driving gate: GPIO21 high against gate low is 3.3 V / 110 k = 30 uA, gate low against GPIO21 low or high is not an issue (gate output impedance is tens of ohm; net shift below 10 mV). Gate output high drives R2 = 10 k with 0.33 mA; VOH is specified >= VCC - 0.1 V at 100 uA and 2.4 V at 16 mA, so the net is about 2.9 V or better (interpolated estimate, not a datasheet value). Gate drive of Q2/Q3 stays above Vgs(th) max 2.5 V at 25 C (margin about 0.4 V) but only 0.1 to 0.15 V above the cold maximum of 2.75 V; **this thin margin exists with the old 100 k as well and is a separate point (rDS(on) of the 2N7002 at Vgs = 2.9 V is not in the sources read; recommend a 3.3 V-drive MOSFET or a check of the datasheet)**. The off-state 2N7002 leakage into ILIM at 0.33 V Vgs was not quantified (IDSS 1 uA max at Vgs = 0 per the secondary copy, against a roughly 24 uA ILIM current for a 50 k R_ILIM1 at 1.2 V; to be confirmed).

Cases that every open or stuck condition on the gate path resolves to the lowest step (Q2/Q3 off):

| Condition | Result with the new values |
|---|---|
| U3/U4 output open, MCU pin input with WPU or pin high | net <= 0.33 V, Q off |
| U3/U4 unpowered (3V3 absent) | gate output high-Z (Ioff / unpowered); MCU also unpowered; R2/R3 pull to 0 V |
| Gate output stuck low | Q off (lowest step) |
| R2/R3 open together with open gate output (double fault) | net floats, **not covered** (same as before the readbacks) |
| Gate output stuck high | step raised; not resolvable by passives; the readback exists to let firmware see it (SW-009) |
| R14/R15 shorted (single fault) with gate output open | WPU case 0.65 V: above the 150 C Vgs(th) min 0.6 V, below 25 C min 1.0 V; GPIO21 output high case: 3.6 V, Q on. **Not covered; residual, accepted as a double fault (short plus open gate) in the prototype** |
| R14/R15 shorted with gate driving low and GPIO21 output high (ROM boot) | gate output low impedance against about 80 ohm pin: about 0.8 V (estimate), below 1.0 V min but thin. Residual |

### 2.3 Readback level with the new values

- Gate driving, internal pull-ups **off**: pin = net minus 100 k x 50 nA = net - 5 mV. High: about 2.9 V, above VIH 2.475 V at 3.3 V and above 2.25 V at VDD = 3.0 V. Low: <= 0.1 V (VOL), below VIL. Valid.
- Gate driving low, internal pull-up **on** (the reset state of both pins): pin = 0.1 + 2.9 x 100 k / (100 k + 45 k) = 2.1 V at VDD = 3.0 V, which is above VIL (0.75 V) and below VIH (2.25 V): invalid. With the old 1 k it was 0.16 V. So the new values **need a firmware rule**: configure GPIO20 and GPIO21 as plain inputs with the pull-up disabled (IO MUX FUN_WPU = 0) before using the readbacks; until then the readback is not valid (a pull-up fails towards "enabled": a false high, no false low). Whether Zephyr's `gpio_pin_configure(GPIO_INPUT)` clears the pull-up on this SoC was **not checked**; to be proved in the SW-009 test. Alternative without that rule: R14/R15 = 10 k with R2/R3 = 1.8 k gives pin 0.6 V (VIL 0.75 V, margin 0.15 V, fails for RPU 30 k): rejected.
- Timing: 100 k x about 5 pF = 0.5 us. ROM TX at 115200 baud toggles the net by at most 0.33 V peak, below Vgs(th) min.
- Reading the readback is only valid with 3V3 present; the pin levels at power order "VBUS present, 3V3 absent" are unchanged (MCU off).

### 2.4 Decision on N1

The numbers support the change. Implemented in `layout_full.py`: R2, R3 = 10 k; R14, R15 = 100 k (the standalone gate fragment generator `gen_gate.py` and `tests/data/gate.net` still show R2/R3 = 100 k; that fragment has no readbacks and was not changed). Regression test added. Open: the 2N7002 numbers are from a secondary copy; the firmware pull-up rule is not yet in SW-009.

## 3. N2: D+ back-feed into VBUS_IC and the TPS2553

### 3.1 Loaded estimate of VBUS_IC (switch off, VBUS gone, 3V3 up)

Source: V(3V3) - VF - I x Rpu, Rpu 1.1 k or 2.2 k (TRM, selectable; reset default of the selector not established). Loads on VBUS_IC while the switch is off: TUSB321 up to 100 uA (below its 4.5 V minimum: unspecified, 100 uA is a ceiling by assumption), R1 and R7 100 k pull-ups into outputs that may be low (2 x 27 uA at 2.7 V), R6 150 k (18 uA), R21 887 k (3 uA), TPS3840 and TPS2553 (off, <= 1 uA each). Sum about 0.18 mA.

| Rpu | V(3V3) | VF | VBUS_IC (0.18 mA) |
|---|---|---|---|
| 1.1 k | 3.3 V | 0.5 / 0.6 V | 2.60 / 2.50 V |
| 2.2 k | 3.3 V | 0.5 / 0.6 V | 2.40 / 2.30 V |
| 2.2 k | 3.0 V | 0.6 V | 2.00 V |

The 1.2 to 2.5 mA is the short-circuit current of the pull-up (3.3 V - 0.6 V over 2.2 k / 1.1 k). With the real load of 0.18 mA the node sits at 2.0 to 2.6 V, which straddles the TPS2553 UVLO rising threshold (2.35 to 2.45 V). EN is tied to IN, and 2.0 to 2.6 V is above the EN VIH 1.1 V, so EN does not prevent turn-on. So the switch **could** be enabled by UVLO at the top of the range.

### 3.2 Does the switch stay on? Loop analysis

If the switch were closed, the load on VBUS_IC is the regulator, the MCU (tens of mA) and the LED chain, at least 20 mA against a source of 1.2 to 2.5 mA at best. VBUS_IC would collapse below UVLO falling (about 2.33 V) within the soft-start, the switch opens, VBUS_IC recovers: at most a hiccup, never a stable "on" state.

More basically, the loop D+ pull-up -> U6 diode -> VBUS_IC -> TPS2553 -> +5V -> regulator -> 3V3 has no gain: every element drops voltage (diode VF >= 0.5 V, Rpu x I, switch Rds(on) x I, regulator dropout). In steady state V(3V3) < V(+5V) and V(VBUS_IC) = V(3V3) - VF - I x Rpu, so **OUT (+5V) exceeds IN (VBUS_IC) by at least VF + I x Rpu + regulator dropout >= 0.5 + 0.2 = 0.7 V** (a switching regulator at 100 % duty has dropout of a few mV; a linear one more). The TPS2553 reverse-voltage comparator trips at 190 mV max (95 to 190 mV), which gives a margin of at least 3.5x. So the switch is turned off by the reverse-voltage protection (3 to 7 ms) and cannot stay on in this loop. The conditions in which "3V3 is up with VBUS gone" are only: (a) the unplug decay window, while C3, C4 and C5/C6 still hold charge, (b) a bench supply on the +5V test point TP1 (or 3V3 TP2) with the cable unplugged. There is no other 3V3 source in the schematic (no battery, regulator input only +5V from the switch).

Residual effects, analysis only:
1. The reverse-voltage comparator asserts FAULT_N (GPIO4) after about 4 ms; in case (b) the firmware sees a fault flag without overcurrent. SW-009/fault handling must not treat it as a cable event.
2. Up to 3 to 7 ms of conduction at UVLO rising is possible before the comparator acts. The datasheet does not say whether the switch starts when OUT > IN at the UVLO crossing; any reverse current is limited only by (OUT - IN)/Rds(on) into C2 (1 uF placeholder). Not quantified.
3. VBUS_IC at 2.0 to 2.6 V is below the TUSB321 minimum 4.5 V, the TPS3840 supply is valid (operating range from 1.5 V per the supervisor datasheet), so HOLD_OK is low and the gates stay closed (unchanged from M1/M2).

### 3.3 Does the M1 recommendation hold?

Yes, with a corrected rationale and a wider bench check. "VBUS_IC near 2.7 V, so the gate stays closed" was the open-circuit value; the loaded value is 2.0 to 2.6 V, and the reason the switch does not turn on is the reverse-voltage protection plus the loop's lack of gain, not a threshold margin. No schematic change is required for the prototype. Options considered:

| Option | Assessment |
|---|---|
| Accept + extended bench check (recommended) | No part change; evidence from measurement of the actual part and Rpu |
| Series diode or switch in the D+ pull-up path | Not applicable: the pull-up is inside the SoC, the D+ line carries data both ways; an external element would break USB signalling |
| EN of U7 driven by HOLD_OK or the gate | Makes turn-on independent of UVLO, but then +5V (and the MCU) wait for the hold-off timer (200 ms) and the supervisor would gate the MCU's own power; architecture change, not justified by the analysis |
| Firmware switches the D+ pull-up off (USB_SERIAL_JTAG DP_PULLUP/PAD_PULL_OVERRIDE) when VBUS is absent | Possible mitigation if the bench check fails; there is no VBUS-present GPIO (F1), HOLD_OK_RB would be the indicator |
| Do not use the USB pins on the prototype | Contradicts HW-006 (programming over USB-C) |

Bench check to replace "VBUS_IC with the cable unplugged and 3V3 up" (scope with VBUS_IC, +5V, 3V3, FAULT_N, HOLD_OK_RB): (1) unplug the cable while running; record the decay of all four nodes for 1 s and check that VBUS_IC does not stay up and that +5V does not recover. (2) Cable unplugged, 5 V from a bench supply on TP1 only (current-limited, 100 mA): record VBUS_IC (expected 2.0 to 2.6 V), the state of FAULT_N, and that the gates stay closed. Not run.

## 4. What was not done

- No bench measurement, no SPICE simulation of either path (the existing `sim/powerup.cir` was not extended).
- 2N7002 numbers from a secondary web copy; vendor datasheet of the final part not read. USBLC6 VF at low current and the TUSB321 low-voltage supply current are assumptions. RPU min/max, the D+ pull-up selector default and the Zephyr pull-up handling were not read.
- No compliance statement is made or implied.
