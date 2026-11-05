# Goldfish review 2: full-board schematic spike (spike/hw-gate, hw/kicad/spike-gate)

- **Status:** Draft. Reviewer: stateless goldfish (second pass), read-only on generator and schematic. Nothing here approves anything; approval stays with the owner.
- **Date:** 2026-11-05
- **Reviewed:** branch `spike/hw-gate` at 852b6ce. Previous review: `review-full-board-goldfish.md` (finding IDs H/M/L/T below are from it).
- **Paths:** relative to the worktree `/home/ben/Programming/busy-light-spike-gate`. `layout_full.py` = `hw/kicad/spike-gate/src/layout_full.py`; `test_layout_full.py` = `hw/kicad/spike-gate/tests/test_layout_full.py`.
- **Datasheets** (local only, not committed, read with pdftotext): TUSB321 SLLSEO6C, TPS3840, USBLC6-2, TPS2553 SLVS841G, ESP32-C3-MINI-1 v2.2, ESP32-C3 TRM v1.4, SN74LVC1G04/G11/G125, SN74AHCT1G125.

## What I ran (reproduced)
| Check | Result |
|---|---|
| `run_full.sh` (venv python, `GATE_NET=tests/data/gate.net`) | ERC errors 0; intent nets 52, drawn nets 52, 0 only in either; two generations identical |
| `unittest discover` in `tests/` | 39 tests OK; `test_layout_full.py` alone 16 tests OK |
| `kicad-cli sch erc --severity-all` | 308 violations: 221 `lib_symbol_issues` + 87 `footprint_link_issues`, all warnings, nothing else (matches report row 2) |
| `len(PARTS)` | 84 references (matches report section 1) |

## Part 1: status of the previous findings
| # | Sev. | Previous finding | Evidence | Status |
|---|---|---|---|---|
| H1 | High | GPIO2 and GPIO8 floating | `layout_full.py:537-550` pulls both up through R16/R17 (10 k to 3V3); test `test_strapping_pins_have_defined_levels`; MINI-1 datasheet Table 4-1 p.12 (both "Floating"), Table 4-3 p.13 (GPIO2 pull-up recommended, GPIO8 = 1 for download boot) | **Fixed** |
| H2 | High | Tests cannot catch electrical errors | Connection-based test `test_no_mcu_net_is_pulled_to_5v_or_driven_by_a_5v_output` added; still uses a hand-listed set of 5 V output pins and only looks one resistor away; intent still comes from the drawing script (report says so) | **Partly** |
| M1 | Med | D+ pull-up back-feed into VBUS_IC through U6 | Analysis only; USBLC6 pin map confirmed (datasheet p.1: 1/6 I/O1, 2 GND, 3/4 I/O2, 5 VBUS); TRM Table 5.12-1 note: GPIO19 USB pull-up is 1 at reset. No hardware change; owner decision pending. Analysis is incomplete, see N2 | **Partly** (open, with new point N2) |
| M2 | Med | CC_OK reads high with VBUS gone | Mechanism confirmed from `layout_full.py:365-391` (R1/R7 to VBUS_IC, U2/U12 on 3V3). Firmware rule drafted as a Proposed SW-009 amendment, validity condition HOLD_OK_RB; no test, no hardware change | **Partly** (accepted-for-now, owner decision pending) |
| M3 | Med | GPIO20/21 readbacks, boot argument incomplete | R14/R15 = 1 k placed (`layout_full.py:522-536`); Zephyr console and ROM-print analysis recorded; console still not disabled anywhere (no SW change). The report M3 text still says the resistor value is open, which contradicts the 1 k in the drawing (N5). Reset state of GPIO21 is worse than "boot prints", see N1 | **Partly** |
| M4 | Med | Hold-off threshold 4.0 V below TUSB321 4.5 V | Report now carries it; DL40 kept, bench ramp check proposed; TPS3840 VIT+ and TUSB321 4.5 V are as quoted. No design change | **Partly** (analysed, open by design) |
| M5 | Med | TUSB321 symbol: invented ADR pin, missing pins | `layout_full.py:83-89` has the 12 datasheet names; numbers 3, 6, 7, 8, 9, 11 match SLLSEO6C p.3 Pin Functions; test `test_cc_ic_symbol_has_the_datasheet_pins`. Residual: VDD (12), GND (10), PORT (4), VBUS_DET (5), CC1 (1), CC2 (2) are still names, not numbers; caption `layout_full.py:300` says "only pins 7, 8 numbered" and is stale | **Fixed** (residual N5) |
| M6 | Med | Missing parts (CC clamp, fuse, ILIM values, module decoupling, LDO) | Unchanged; report section 4 lists most; module-pin decoupling and LDO dissipation not listed | **Open** (acknowledged, not fixed) |
| M7 | Med | Report stale | Counts for warnings (308/87/221), refs (84) and nets (52) now verified. Test counts are stale again: report says 14 and 37, actual 16 and 39 (N5) | **Partly** |
| L1 | Low | LED start-up state undefined | No change; `datasheet-evidence-switch-buffers.md` C5 records the no-Ioff open point for U11 | **Open** |
| L2 | Low | 74LVC1G125 not read | Read: pins 1 OE, 2 A, 3 GND, 4 Y, 5 VCC, Ioff 10 uA at 5.5 V (datasheet p.3, p.6) | **Fixed** |
| L5 | Low | U5 pin 4 MR/NC floating | TPS3840 Table 5-1 p.4: "MR can be left floating when not in use" | **Fixed** |
| L6 | Low | Power flags on legend stubs, passive pins on boxes hide drive/supply errors | `layout_full.py:253-257, 91-96` unchanged | **Open** |
| T1 | Low | 5 V test was a name list | Replaced by connection test (see H2) | **Partly** |
| T2 | Low | Strapping test passed trivially | `test_strapping_pins_have_defined_levels` asserts net, resistor and 3V3 | **Fixed** |
| T3, T4 | Low | Weak ILIM test; intent and drawing share one writer; determinism test shares module state | `test_tps2553_in_the_vbus_path` unchanged; `PLACE` still mutated by `put()` (`layout_full.py:188-191`); `run_full.sh` compares two processes | **Open** (T4 mitigated by `check_full.py`, `run_full.sh`) |
| T5 | Low | No tests for pull-ups (R4, R5, R11, R13, R9) or power-order rules | Not added (only R16/R17) | **Open** |

## Part 2: new findings
| # | Sev. | Finding | Evidence | Status |
|---|---|---|---|---|
| N1 | Medium | **The readback resistors weaken the HW-010 fault coverage.** R14/R15 (1 k) connect the MCU pins GPIO20/GPIO21 to the enable nets ILIM_STEP2_EN / ILIM_STEP3_EN, whose only defined low level besides the gate output is R2/R3 = 100 k to GND. If the AND output is open (solder defect, open in the output path) or not yet driving, the net is set by the MCU pin: TRM Table 5.12-1 reset state of GPIO21 is "4" (OE = 1, pull-up enabled, output idles high for UART TX) and of GPIO20 is "3" (input with pull-up). With 1 k in series and 100 k to GND the net sits at about 3.3 V (GPIO21 output high) or about 2 V (pull-up of tens of kohm); a 2N7002 turns on in that range, raising the TPS2553 limit with the firmware stopped. HW-010 acceptance: "every open or short on the gate path resolves to the lowest step". Before the readbacks an open AND output resolved low through R2/R3. The report treats GPIO21 only as "an output during ROM boot messages" and only checks contention against a driving gate. | `layout_full.py:522-536`; TRM v1.4 Table 5.12-1 (reset column legend: 3 = IE+WPU, 4 = OE+WPU); HW-010 acceptance text; `datasheet-evidence-switch-buffers.md` A6 (Q2/Q3 raise the limit when conducting). Pull-up value of GPIO20 and 2N7002 Vgs(th) not read by me, so the voltage is estimated, not measured | **Open**. Option to evaluate: series 100 k or more on the readbacks (inputs only need leakage current) and 10 k pull-downs on R2/R3, then a fault-injection scenario with the AND output open and the MCU pin driven high |
| N2 | Medium | **The M1 back-feed analysis stops at the supervisor and the CC IC.** The same VBUS_IC net feeds U7 IN and EN. TPS2553 UVLO rising is 2.35 to 2.45 V and EN VIH is 1.1 V (U7 EN is tied to IN), so at the estimated 2.7 V the switch turns on and passes the D+ pull-up current to +5V and the regulator input, loading the node. The "near 2.7 V" value is therefore the open-circuit figure; 1.2 to 2.5 mA is the short-circuit current of the 2.2/1.1 k pull-up, not a current that can hold 2.7 V against the MCU, LED and regulator load. The state is not a stable "gate closed, VBUS_IC at 2.7 V" but an unexamined loop (3V3 -> D+ pull-up -> VBUS_IC -> TPS2553 -> +5V -> regulator -> 3V3). The proposed bench check ("VBUS_IC with the cable unplugged and 3V3 up") does not name +5V or 3V3 as measured nodes. | TPS2553 SLVS841G electrical characteristics (UVLO rising 2.35 min, 2.45 max V) and 6.3 (VIH 1.1 V, per the repo evidence file); `datasheet-evidence-switch-buffers.md` A8, A10 (already lists these numbers); `layout_full.py:457-473`; TRM Table 5.12-1 note (USB pull-up on after reset) | **Open**. Add +5V and 3V3 to the bench check, or name the series diode/switch option |
| N3 | Low | Report text contradicts the drawing in several places: (a) test counts 14 / 37 vs actual 16 / 39 (report row 5); (b) M3 text "series resistor not calculated ... value open" while R14/R15 = 1 k are drawn and F1 says 1 k; (c) caption `layout_full.py:300` "only pins 7, 8 numbered" while six pins are numbered; (d) F8 text "U9 pin numbers ... not read" while Table 3-1 pins 22, 23, 5, 26, 27, 30, 31 and others were read for the HW-010 amendment | `spike-full-board-schematic.md` rows 5, M3, F8; `layout_full.py:300, 302` | **Open** |
| N4 | Low | C1 is "620n C0G 5%" in an 0603 footprint (`layout_full.py:59`). From general knowledge, C0G is not made in 620 nF in 0603; X7R would carry a large DC-bias and tolerance loss on the 200 to 600 ms window (TPS3840 tD = 618937 x C + 50 us gives 384 ms nominal). Not checked against a distributor listing. | `layout_full.py:59`; TPS3840 equation (4) | **Open**, check against a real part and the tolerance equations (6), (7) |
| N5 | Low | Process: the files `hw/kicad/spike-gate/gen_gate.erc`, `gen_gate.log`, `skidl_REPL.erc`, `skidl_REPL.log` are tracked build/tool output (CLAUDE.md rule 12: do not commit build output). | `git diff main --stat` | **Open** |
| N6 | Info | The worktree `docs/requirements/hw.md` is older than the copy in the main checkout (HW-006 still lists UART test points, HW-010 has no proposed amendment). The schematic is traced to the main-checkout text; any merge must reconcile. | Both `docs/requirements/hw.md` files | **Open** |

## Spot checks that found no defect
- **U1 TUSB321** (SLLSEO6C p.3): CC1 1, CC2 2, CURRENT_MODE 3, PORT 4, VBUS_DET 5, VCONN_FAULT 6, OUT1 7, OUT2 8, ID 9, GND 10, DIR 11, VDD 12. Drawing: PORT to GND (UFP), OUT1/OUT2 open drain pulled to VBUS_IC, VBUS_DET through 887 k (RVBUS typ per revision history), unused outputs not connected. No mismatch.
- **U5 TPS3840DL** (Table 5-1 p.4): RESET 1 (DL = active low), VDD 2, GND 3, MR/NC 4, CT 5. Matches `layout_sch.py:64-67` and the drawing. CT 620 nF gives 384 ms nominal by equation (4).
- **U6 USBLC6-2P6**: pin map as drawn (D- pair 1/6, D+ pair 3/4, GND 2, VBUS 5). J1 D+ = A6/B6, D- = A7/B7 ties are correct.
- **U7 TPS2553** (Table 5-1, SOT-23): IN 1, GND 2, EN 3 (active high), FAULT 4, ILIM 5, OUT 6. Matches.
- **U9 ESP32-C3-MINI-1** (Table 3-1 p.11): GPIO18 pin 26 (D-), GPIO19 pin 27 (D+), GPIO20 pin 30, GPIO21 pin 31, GPIO0/1/2/3/4/5/6/7/8/9/10 all exposed; GPIO2/8/9 are the strapping pins; GPIO5 (button) is not. Pin numbers of the box are hidden, so footprint mapping is untested (acknowledged).
- **Buffers and gates**: U10/U11 pins match SCES223U / SCLS378P; U2, U12 (LVC1G04) and U3, U4 (LVC1G11) have Ioff (10 uA at 5.5 V), so 5 V inputs with 3V3 absent are within the datasheet.
- **Power order, VBUS present and 3V3 absent**: SEL_STEP lines, LED_DATA and enable gates default low through R4/R5, R11 and R2/R3; gates unpowered with Ioff; first step limited by R_ILIM1 only (value tbd). No defect found beyond N1 and N2.
- **Process**: new reports are `Draft`, "Nothing here is Approved or Accepted"; no compliance claims found; no vendor datasheet is tracked (`hw/datasheets/` holds only `.gitkeep`). SPDX header changes elsewhere on the branch are not related to the schematic.

## Not run
- No bench measurement, no simulation of any power-up or back-feed path (N1 and N2 are analysis from datasheet text, not measured).
- Did not re-run the negative test (5 V connection test failing on a deliberately broken netlist) claimed in report row 5.
- No ESP32-C3 GPIO input-threshold comparison, no 2N7002 or WS2812B datasheet read, no ILIM resistor check (values are tbd).
- KiCad GUI, PCB update, footprint and library table checks, DRC, power budget, thermal check of the 5 V to 3.3 V regulator: not done.
- Figures in the datasheets (pin drawings, timing graphs) were not read; pin numbers come from the pin tables.

## Outcome
**Approved with actions** is not mine to give. My assessment for the owner: the spike is a fair exploratory record. The previous High findings are fixed (H1) or honestly bounded (H2). Two Medium points (N1, N2) concern HW-010 fault behaviour and should be resolved or accepted explicitly before the schematic is used as a design basis; the other items are documentation clean-up. Owner decisions still open: M1, M2, M3 (console and ROM print), M4.
