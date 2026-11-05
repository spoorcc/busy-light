# Owner decisions of 2026-11-05 on the hardware gate spike

Status: Draft. Record of answers that the owner (Ben Spoor) gave in the working session on 2026-11-05.
They are **owner-confirmed proposals only**. Nothing here is Approved or Accepted, and no Approved requirement text is changed. Only the "Proposed amendment" paragraph of HW-010 and the Proposed SW-009 amendment were extended.
Traces: HW-010, SW-009, SYS-020, ADR-0010, ADR-0016, RISK-027, RISK-044.
Nothing in this record was run on the bench, simulated or measured.

## 1. Decisions

| # | Decision | Owner answer | Author recommendation matched? | Where recorded | Follow-up work | Bench check |
|---|---|---|---|---|---|---|
| 1 | ILIM resistor class | Use 0.1 % E192 parts for the prototype: R_ILIM 47.0 k / 56.9 k / 27.7 k (`analysis-ilim-steps.md`). Keep the HW-010 numbers. Check JLCPCB stock. | Yes (the only combination found that meets all four HW-010 numbers) | HW-010 Proposed amendment (docs/requirements/hw.md); `analysis-ilim-steps.md` | Stock check of the three values (open); set values in the generator when the owner confirms; margin is thin (4 to 15 mA) | Measure each limit step with a load |
| 2 | Middle step | About 1.0 A; proposed window 850 to 1150 mA | Not recorded as a separate recommendation; follows the analysis assumption | HW-010 Proposed amendment | Owner approval of the window with HW-010 | Measure step 2 |
| 3 | Step 1 | Maximum only (623 mA), no minimum in the requirement; nominal target 500 mA as a note | Not stated in the session | HW-010 Proposed amendment | Remove the step 1 minimum from the acceptance text only after approval | Measure step 1 against the 623 mA maximum |
| 4 | Q2 and Q3 both on | Exclude in hardware: steps are exclusive; the step 3 enable forces step 2 off | Not stated in the session | HW-010 Proposed amendment | Gate logic change in the generator and tests (not done here) | Truth-table test on the board: no input pattern turns both on |
| 5 | 2N7002 | Microchip DS20005797A read: IDSS max 1 uA at 60 V / 25 C only; no Rds below 5 V gate. Find a part with stated low-voltage leakage. | Yes | This report (Still open) | Another agent selects the part; update `analysis-ilim-steps.md` leakage assumption (below about 100 nA) | Leakage of the ILIM switches at the ILIM voltage |
| 6 | Hold-off capacitor | Parallel C0G set in 1206/1210, for example 220 + 220 + 150 + 33 nF, 5 % | Not stated in the session | HW-010 Proposed amendment; `analysis-n4-holdoff-capacitor.md` | Stock check by another agent (open) | Measure the hold-off time |
| 7 | M4 supervisor ramp | Keep TPS3840DL40; accept with the bench ramp check | Yes | HW-010 Proposed amendment; spike-full-board-schematic.md (M4) | None | Ramp VBUS_IC from 3.5 V to 5 V with a default-current source: no enable output rises |
| 8 | M1 D+ back-feed | Accept with bench check; firmware ignores FAULT_N when HOLD_OK_RB is low | Yes | HW-010 and SW-009 Proposed amendments; spike-full-board-schematic.md (M1) | SW-009 test case for the FAULT_N rule | VBUS_IC, +5V, 3V3, FAULT_N during unplug decay and with 5 V on TP1 only |
| 9 | M2 CC_OK validity | Firmware rule: CC_OK inputs valid only while HOLD_OK_RB is high, otherwise assume the lowest step; no hardware change | Yes | SW-009 Proposed amendment (docs/requirements/sw.md); spike-full-board-schematic.md (M2) | SW-009 test case | Unplug cable with 3V3 up: firmware uses the lowest step |
| 10 | M3 console and ROM print | Disable UART0 console; use USB-Serial-JTAG for console and logs (Zephyr node `usb_serial` exists in the ESP32-C3 devicetree; exact Kconfig not verified); tolerate ROM print on GPIO21 via the 100 kohm series resistor on the readback; eFuse not burnt for the prototype | Partly (the recommendation allowed series resistor or eFuse; the owner chose the resistor) | HW-010 Proposed amendment; spike-full-board-schematic.md (M3) | Find and verify the Kconfig symbols; record the GPIO20/21 pull-up rule in SW-009 | Read GPIO21 readback during boot; check console on USB |
| 11 | Supervisor part | TPS3840DL40 fixed for the prototype | Yes | HW-010 Proposed amendment (with decision 7) | None | See decision 7 |
| 12 | Status | Record as owner-confirmed proposals only | n/a | This report; all edits above | Owner approval of documents is separate | none |

"Matched?" states only what is visible in this session. Where the session shows no earlier recommendation, the cell says so.

## 2. Added firmware rules (Proposed SW-009 amendment)
- Decision 8: ignore FAULT_N while HOLD_OK_RB is low.
- Decision 9: CC_OK inputs valid only while HOLD_OK_RB is high, otherwise assume the lowest step.
- From `analysis-n1-n2-readback-backfeed.md`: disable the internal pull-ups on GPIO20 and GPIO21 before using the readbacks (with the 100 kohm series resistor, an enabled 45 kohm pull-up gives about 2.1 V for a low gate, which is an invalid level). Whether `gpio_pin_configure(GPIO_INPUT)` clears the pull-up on this SoC is not checked.
- Never drive both select outputs at the same time.

## 3. Still open
- HW-006 text (programming and self-test through the USB-C connector alone; UART test points were dropped in F1).
- ADR-0012 (ring geometry, peg-azimuth conflict, gate G1) and LED count / peg azimuth.
- ADR-0010 points 3 to 6.
- Lawyer items (legal review of regulatory statements).
- ILIM stock: JLCPCB availability of the 0.1 % E192 values.
- 2N7002 replacement (decision 5).
- Hold-off capacitor stock (decision 6).
- SW-005 against the hold-off maximum (not examined in this record).
- Kconfig for the USB-Serial-JTAG console (not verified).
- All approvals: HW-010, SW-009 and the ADRs stay as they were.
