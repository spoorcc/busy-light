# Software test cases

- **Status:** Draft (stubs; procedures are written when the requirements are approved)

### TC-101 Input limits of the extractor and mapper

- **Verifies:** SW-001
- **Level:** Unit / integration
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of SW-001
- **Automated:** TBD
- **Evidence:** TBD

### TC-102 Limit on concurrent network sessions

- **Verifies:** SW-002
- **Level:** Unit / integration
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of SW-002
- **Automated:** TBD
- **Evidence:** TBD

### TC-103 Fuzz tests of external inputs

- **Verifies:** SW-003
- **Level:** Unit / integration
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of SW-003
- **Automated:** TBD
- **Evidence:** TBD

### TC-104 Image confirmation and forced restart

- **Verifies:** SW-004
- **Level:** Unit / integration
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of SW-004
- **Automated:** TBD
- **Evidence:** TBD


### TC-105 Raise the current limit only after a stable reading

- **Verifies:** SW-005
- **Level:** Unit / integration, then bench with TC-203
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of SW-005
- **Automated:** TBD
- **Evidence:** TBD
- **Proposed procedure outline (Draft, 2026-11-05, owner decision; proposal P6 of `docs/verification/reports/analysis-sw005-holdoff-timing.md`; it belongs to the Proposed amendment of SW-005 and is not Approved; "Procedure: TBD" above stays until the owner approves the amendment):** Unit level with an injected clock and a fake GPIO: (a) 6 equal reads at 100 ms give the step at read 6; (b) a change at read 5 restarts the count; (c) HOLD_OK_RB low during the count restarts it; (d) a falling edge of HOLD_OK_RB sets the select outputs low and the next raise needs a new count; (e) a default reading never sets a select output; (f) the step arrives within 700 ms of the rising edge of HOLD_OK_RB with 5 ms of clock jitter; (g) an input combination that the CC IC cannot output gives step 1. Bench level, with TC-203: a scope on HOLD_OK_RB and on the select GPIO, a 1.5 A source, the limit step read from the input current; the time from VBUS applied to the raised step is recorded against the [2] s of SYS-020 (TC-020). Not run: no firmware exists.

### TC-106 Reduce load before lowering the current step

- **Verifies:** SW-006
- **Level:** Unit / integration, then bench with TC-203
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of SW-006
- **Automated:** TBD
- **Evidence:** TBD

### TC-107 Back-off after a brown-out reset

- **Verifies:** SW-007
- **Level:** Unit / integration, then bench with TC-203
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of SW-007
- **Automated:** TBD
- **Evidence:** TBD

### TC-108 Tolerance of Power Delivery traffic and source changes

- **Verifies:** SW-008
- **Level:** Unit / integration, then bench with TC-203
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of SW-008
- **Automated:** TBD
- **Evidence:** TBD

### TC-109 Follow the hardware gate state and shed load

- **Verifies:** SW-009
- **Level:** Unit / integration, then bench with TC-210
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of SW-009
- **Automated:** TBD
- **Evidence:** TBD
- **Proposed procedure outline (Draft, 2026-11-05, owner decision; proposal P6 of `docs/verification/reports/analysis-sw005-holdoff-timing.md`; it belongs to the Proposed amendment of SW-009 and is not Approved; "Procedure: TBD" above stays until the owner approves the amendment):** Unit level: (a) edge interrupt to load shed within [X] ms of the falling edge of HOLD_OK_RB, EN2 or EN3, with [X] open until a rail hold-up is measured; (b) a falling edge shorter than the poll period is latched and not missed; (c) HOLD_OK_RB low with CC_OK inputs high gives the lowest step; (d) FAULT_N low with HOLD_OK_RB low gives no fault action; (e) the readback code calls gpio_pin_configure with GPIO_INPUT only, and a readback before configuration is reported as invalid; (f) no test or run drives both select outputs; (g) a forced reset with HOLD_OK_RB low, and one with the retained flag set, do not increase the brown-out counter (SW-007). Inspection: the build configuration lists usb_serial as zephyr,console, uart0 disabled, CONFIG_SERIAL_ESP32_USB=y, CONFIG_UART_ESP32 not set, CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y (zephyr.dts and .config stored in docs/verification/). Bench, with TC-210: a forced VBUS dip of 10 us, 10 ms and 100 ms; record the time from the HOLD_OK_RB fall to the LED current and whether the MCU resets (recorded, not a pass criterion until [X] is set); read IO_MUX_GPIO20_REG and IO_MUX_GPIO21_REG after start-up (FUN_WPU and FUN_WPD 0, MCU_SEL 1); the log is visible on USB-C alone and no UART activity is seen on GPIO21 after the application starts; unplug the cable with 3V3 up and show that the firmware uses the lowest step. Not run: no firmware exists.

