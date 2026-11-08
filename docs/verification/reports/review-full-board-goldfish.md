# Goldfish review: full-board schematic spike (spike/hw-gate, hw/kicad/spike-gate)

Reviewer: stateless goldfish. Read-only. Paths are relative to the worktree /home/ben/Programming/busy-light-spike-gate unless noted. layout_full.py = hw/kicad/spike-gate/src/layout_full.py, test = hw/kicad/spike-gate/tests/test_layout_full.py.

## What I could not run
- kiutils is not installed in this environment, so I could not run layout_full.py, the 12 tests, check_full.py, or kicad-cli ERC. All "run" results in the report were taken as claimed, not reproduced. Review is by reading code, report, ADR/requirements and the evidence files.
- I did not open the KiCad symbols for J1 (USB_C_Receptacle_USB2.0_16P pin names such as A1B12), so I cannot say whether the pin names used at layout_full.py:313-324 exist in the library.
- No datasheet was read by me. TUSB321 pinout (is there an ADR pin? VCONN?), TPS2553 pin order, 74LVC1G125 / 74AHCT1G125 limits, USBLC6-2P6 behaviour, ESP32-C3 USB D+ pull-up behaviour without VBUS are from memory or from the repo's own evidence files.
- No simulation or timing analysis. Power budget, LDO dissipation, ILIM values not examined (none exist).

## Findings

### High

H1. Strapping pins GPIO2 and GPIO8 are left floating (no-connect), against the module datasheet. layout_full.py:533-534 (`s.nc(GPIO2)`, `s.nc(GPIO8)`); ESP32-C3-MINI-1 datasheet Table 4-1: GPIO2 and GPIO8 default "Floating", GPIO9 weak pull-up. Table 4-3 note 2: "recommended to pull [GPIO2] up due to glitches"; Joint Download Boot needs GPIO8 = 1; Table 4-4: GPIO8 also controls UART0 ROM printing. With GPIO8 floating, pulling GPIO9 low (the TP6 BOOT test point, line 512-517) may or may not enter download mode, and the ROM-print state at power-up is undefined (it matters because GPIO21 TX is used as an input here, see M3). The report never mentions this. HW-007 is about the button only, and test_button_is_not_on_a_strapping_pin_hw007 passes trivially because these pins are not connected at all. Fix: 10 k pull-ups to 3V3 on GPIO2 and GPIO8 (Espressif reference design), add a test that checks them. HW-006 "programming through USB-C alone" is not shown to work with floating GPIO8.

H2. Test suite cannot catch the electrical class of errors the spike claims to examine. See the test section below (T1 to T4). The report states clearly that the intent table proves only that the script drew what it meant (report section 2, last paragraph) and that is honest, but the headline results (ERC 0 errors, intent equals drawing, 10/12 tests) do not touch voltage levels, power order or pull-ups. Rated High because the report presents "no 5 V net on an MCU pin" as a checked property.

### Medium

M1. USB data lines can back-feed raw VBUS through the ESD part with VBUS absent. layout_full.py:349 ties U6 pin 5 (USBLC6 VCC/VBUS pin) to VBUS_IC, and GPIO18/19 go straight to D-/D+ through U6 with no series resistor and no VBUS gating (lines 351-352, 509-510). The ESP32-C3 USB D+ pull-up (to 3.3 V) is on whenever the USB peripheral is enabled; I believe it is not gated by a VBUS sense, but I did not read this. When the cable is unplugged and 3V3 is still up (the "VBUS gone, 3V3 up" case that HW-010's proposed amendment demands to be checked), D+ at ~3.3 V forward-biases the USBLC6 steering diode to its VBUS pin and lifts VBUS_IC to roughly 2.5 to 2.7 V through the pull-up. Consequences: the supervisor U5 (reset asserts below 4.0 V so the hold-off still restarts, but VPOR logic is exercised at an odd level), TPS2553 EN/IN sit at ~2.6 V, R21 and the pull-ups R1/R6/R7 see a non-zero VBUS_IC. Not discussed in F6. Needs a check against the USBLC6 datasheet and the ESP32-C3 TRM; a series resistor or a VBUS sense/gate may be needed.

M2. CC_OK_1A5 reads "1.5 A advertised" while VBUS is gone and 3V3 is still up (inherited from review-gate-v3a H1, now reached the MCU pin). OUT1_N is pulled to VBUS_IC (R1, line 363); with VBUS = 0, OUT1_N = 0 V and U2 (powered from +3V3, line 366) outputs 1 on CC_OK_1A5, which goes to GPIO0 (line 505) and to both gates (lines 392-395). Only HOLD_OK keeps the gates closed. F6 says the 3V3 decay is "short" and "not simulated", but does not state the consequence: the firmware can see a false 1.5 A advertisement during the decay (3V3 is held by C3, C5, C6, LED capacitors: 16 x 100 n plus bulk). Should be written as a firmware rule (SW-005/009: use CC_OK only while HOLD_OK_RB is high) and as a test.

M3. GPIO20/GPIO21 as readbacks: acceptable electrically but the boot-time argument is incomplete. layout_full.py:520-532. The 1 k series resistors limit contention current (GPIO21 TX high into a low gate output: about 3.3 mA; the 74LVC1G11 output stays within about 0.1 V), so I find no damage case. But: (a) with GPIO8 floating (H1) it is not defined whether UART0 ROM printing is on; (b) GPIO20 U0RXD is also the default console RX; the Zephyr esp32c3 console defaults to UART0, so the console must be moved to USB-Serial-JTAG or the readback will see log bytes. No requirement or SW note records this (SW-009 / HW-006 rationale only mention the ROM prints). (c) The GPIO21 output also moves ILIM_STEP3_EN (the Q3 gate drive net) by a few tens of mV during boot prints; 100 k pull-down plus the strong gate output make this harmless, but it was not stated.

M4. TUSB321 supply/min-voltage versus hold-off threshold (inherited from review-gate-v3a M1) is still unresolved in the full board. U5 is TPS3840DL40 (VIT- about 4.0 V, line 58 and caption 298) while the CC IC needs VDD >= 4.5 V (cc-ic-datasheet-evidence.md row 1). A dip to 4.1 to 4.4 V browns out the IC without restarting the hold-off, and OUT1 can glitch. The full-board report does not carry this open point at all.

M5. CC_IC box pins not read; ADR pin possibly invented. layout_full.py:81-86 draws an "ADR" pin on the TUSB321 and marks it no-connect (line 358). The repo's own evidence file attributes the ADR pin (I2C mode select) to the second part (TUSB320 family, rows 12 to 15), not to TUSB321 (rows 1 to 11). If TUSB321 has no ADR pin the symbol is wrong; if it has a mode pin that must be tied, leaving it open is a floating input. The VCONN pin of TUSB321 (evidence row 10, "not read") is absent from the symbol. F8 says only OUT1/OUT2 are numbered, but does not say that the pin set itself is a guess. HW-003 acceptance criterion "PORT tied low" is met (line 357); the rest of the IC pinout is unproven.

M6. Missing parts that HW-003 / HW-010 acceptance text expects on the schematic. Acknowledged in report section 4, so only rated Medium: CC clamp/series resistor (HW-003 statement), connector current rating and fuse (HW-003 AC), ILIM values (HW-010 623 mA / 1366-1577 mA bands depend on them), module decoupling at U9 3V3 pin (only C5/C6 at the regulator, lines 483-492; the MINI-1 reference circuit has bulk and 0.1 uF at the module). Also the 3.3 V LDO from 5 V at up to ~0.35 A Wi-Fi peak dissipates about 0.6 W for a 1.7 V drop; no part, no thermal check (HW-004).

M7. Report is stale and internally inconsistent after the F1 update (claims not backed by the checks):
- Section 1 "Test points" still lists TX and RX and "8 test points" in the size line; the file has 6 (layout_full.py:74). Section 1 MCU bullet still says "UART".
- Section 2 row 5: "10 tests pass (...)" and "whole folder 33 tests pass"; F1 update says 35 tests, and test_layout_full.py contains 12 test methods. The table row was not updated, and the list in the row does not match the file.
- Section 2 row 2: "302 warnings, all library not configured (85 footprint, 217 symbol)". check_full.py:136-139 runs ERC with `--severity-error` only, so the run script produces no warning count; the figure must come from a manual run that is not scripted or recorded. Also 82 refs vs 85 footprint warnings do not obviously agree (power symbols have no footprint), unexplained.
- Row 6 "overlaps fixed over three rounds" is a visual check with no recorded output.

### Low

L1. WS2812B 5 V data from 3.3 V: electrically sound as drawn. U11 74AHCT1G125 on +5V (line 602), input from GPIO7 3.3 V (ESP VOH min 0.8 x VDD = 2.64 V vs AHCT VIH 2.0 V), output 5 V into WS2812B (VIH 0.7 x 5 = 3.5 V), 330 R series (line 610), pull-down R11 keeps the buffer input low during reset (line 590-593). AHCT datasheet not read (F4 says so). One residual: the +5V rail is supplied only through the TPS2553 current limit (500 mA initially) while 16 LEDs may show white at power-up if data is garbage; no startup state is defined here (firmware/HW-001 question, not a drawing error).

L2. HOLD_OK 5 V into U10 (74LVC1G125, 3V3) and U3/U4 (74LVC1G11): input 5.5 V recommended per the repo evidence for LVC1G04/G11 (read); G125 not read (F3). Pin map U10: 1 OE, 2 A, 3 GND, 4 Y, 5 VCC matches what I remember of the part (OE active low, tied to GND at line 580-583). A drawn ground symbol pointing up is cosmetic.

L3. USB-C front end: TVS (VBUS), USBLC6 on D+/D-, shield to GND directly (line 325). CC1/CC2 unprotected apart from the IC (TUSB321 CC rating 6 V, HBM 7 kV; evidence row 3), as the report states. Button path: R12 1 k series, R13 10 k pull-up to 3V3, TVS2 on the MCU side, switch to GND, no debounce capacitor (line 549-567). Meets HW-007 wording; GPIO5 is MTDI (JTAG pad) not strapping, and the JTAG pads are not enabled by default, I did not verify.

L4. GPIO use: GPIO0/1 (XTAL_32K pins) and GPIO4-7 (JTAG pads) are used as plain GPIO. Acceptable on the C3 with USB-Serial-JTAG, not examined further.

L5. U5 pin 4 (MR/NC) is marked no-connect (line 437). The evidence file labels it "MR/NC"; whether the pin may float on the DL variant was not shown. Probably fine (internal pull-up) but not read.

L6. Rail naming and tautology in the schematic: `VBUS_IC`, `+5V`, `+3V3` rails have power flags drawn through `rail()` at 20,28..49 (lines 250-254, 309-310), i.e. the flags are on dummy stub wires in the legend, not on the real source nets. ERC "power pin not driven" would be silenced by these flags without the real sources having flags; with passive output pins on boxes (U7 OUT is "passive", line 91; U8 OUT "passive", line 93) ERC cannot check driver conflicts or missing drivers on these nets. The "ERC 0 errors" result therefore says little about drive/supply correctness.

L7. Power order summary as drawn (for the record, checked by reading): pull-ups for OUT1_N, OUT2_N, HOLD_OK, VBUS_DET all go to VBUS_IC (lines 359-363, 378, 443), so with VBUS = 0 and 3V3 up no MCU pin sees more than 3V3 and the only 5 V-referenced nets terminate in 5.5 V-tolerant LVC inputs (read in the evidence) or in the AHCT on +5V. No pin of U9 is on a net with a 5 V driver (confirmed by reading lines 505-534). The remaining unknown is output level of U2/U12 at VCC = 0 (not specified, evidence inverter item 12), harmless here because both ends of that net share 3V3.

## Tests that cannot fail, or do not test what the name says (test_layout_full.py)

T1. test_no_5v_net_reaches_an_mcu_pin (lines 51-55): the "5 V" set is a hard-coded list of net names. A 5 V net renamed, or a new 5 V source on a differently named net, passes. The test knows nothing about the supply of the driving part (e.g. U11 on +5V driving a net named anything else). It will pass for any wiring that keeps those names off U9. At best a naming-convention check.

T2. test_button_is_not_on_a_strapping_pin_hw007 (lines 44-49): GPIO2 and GPIO8 are nc, so `pin_net.get` is None and the assertNotEqual passes trivially; GPIO9 is the BOOT net. It never asserts anything about the strapping pins' state (H1), so HW-007's "boot pins" evidence is thinner than the test name suggests. Also note that pins marked `nc()` do not appear in `intent`, so test_every_gpio_in_use_is_listed (94-97) cannot see them either.

T3. test_tps2553_in_the_vbus_path (lines 64-72): the last loop `assertIn(x, ("ILIM",))` uses a ternary that reads pin 1 for R_ILIM1 and pin 2 for the others; R_ILIM1 pin 2 (GND) and the Q2/Q3 source/drain wiring are not checked; it also does not check that the EN of U7 goes to the right net for the intended behaviour beyond VBUS_IC. It can fail only on a net rename. The same holds for test_cc_ic_is_sink_only_and_supplied_from_vbus: it can fail, and the PORT/VDD checks are good, but nothing checks VBUS_DET value (887 k is in PARTS only as a string "887k").

T4. All tests read `intent`, which is written by the same code that draws (the report says so). Nothing tests that the saved .kicad_sch matches (check_full.py does, but it is not a unit test and was not reproduced by me). test_two_builds_are_identical (18-26) shares mutated module state (PLACE is rewritten by `put()`, line 186-188) so the second build starts from the first one's snapped coordinates: it tests idempotence, not cross-process determinism (hash order, etc.). run_full.sh does compare two process runs, which is the better evidence.

T5. Missing tests that match the review concerns: no test asserts pull-ups/pull-downs on SEL_STEP2/3 (R4, R5 pins), on LED_DATA (R11), on BUTTON (R13) or that EN has R9 (only the net names used by other tests are touched); no test for the power-order rules in section F6; no test that every U9 input has either a driver or a pull; no check of unconnected gate inputs (a floating pin would not appear in `intent`).

## Gaps against requirements (summary)
- HW-003: CC clamp and series resistor, connector/track rating, fuse, power-budget file in hw/sim/ missing (report section 4 admits most).
- HW-006: five of six points present; reset (EN), boot (GPIO9), 5 V, 3.3 V, GND, LED data present; pad size set by footprint D1.5 mm (>= 1.0 mm OK); "programming via USB-C alone" unsupported while GPIO2/GPIO8 float (H1).
- HW-007: button on GPIO5 with pull-up, series R and ESD diode: met on paper; strapping pins are not addressed (H1).
- HW-010 (Approved text and proposed amendment): readbacks for hold-off and both enables exist at 3.3 V logic; "VBUS 0 V and 3V3 present, no readback pin exceeds rating" is satisfied by construction for the readback nets, but M1 (back-feed via ESD part and USB D+ pull-up) and M2 (CC_OK false positive) are not covered; ILIM values tbd so 623 mA / 1366-1577 mA cannot be shown; hold-off 200-600 ms rests on the earlier arithmetic only.
- ADR-0016: gate and fault behaviour as in the gate fragment; M4 open.

## Summary of what the report claims that I could not confirm
- "ERC 0 errors", "50 nets equal", "33/35 tests pass", "byte-identical": not reproduced (kiutils missing here).
- "302 warnings": no script produces it.
- Section 1 text (test points, UART, 8 TP, test counts) contradicts the F1 update and the code.
