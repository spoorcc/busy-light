# Software Requirements

- **Status:** Draft
- **Version:** 0.1
- **Owner:**

Entries use IDs `SW-nnn` and follow `docs/templates/requirement.md`.
Process rules: `docs/process/README.md`.

### SW-001 Input limits of the extractor and mapper

- **Statement:** The extractor and mapper shall accept at most [8] KiB of input text per message, a path depth of at most [8], a path length of at most [64] characters, a document nesting of at most [32] levels (also in parts that are skipped), numbers as 32-bit integers or decimals with at most [6] fractional digits (numbers with an exponent are not accepted as a target), and at most [16] table rows per source, and shall reject anything larger with an error, without crashing or waiting.
- **Rationale:** Bounded input keeps memory and time bounded (ADR-0005 item 3). Oversize input from a source that the user or a network peer controls must not stop the device.
- **Parent:** SYS-005, SYS-008
- **Acceptance criteria:** For every limit, an input one unit over the limit is rejected with a named error and an input at the limit is accepted. The run time on the maximum input is at most [50] ms on the target (measured in spike 7.1). No allocation from the heap happens during extraction.
- **Verification method:** Test
- **Verified by:** TC-101
- **Category:** Robustness
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### SW-002 Limit on concurrent network sessions

- **Statement:** The device shall serve at most [2] TLS sessions at the same time, shall refuse further connections within [1] s with a busy answer, and shall keep the LED output and the watchdog running while sessions are open or refused.
- **Rationale:** RAM is small and a TLS handshake is expensive. A flood of connection attempts on a shared LAN must not exhaust the heap or stop the display (RISK-010, RISK-018).
- **Parent:** SYS-027, SYS-005
- **Acceptance criteria:** With [10] simultaneous connection attempts: [2] sessions work, the others get the busy answer, the free heap stays above the SYS-026 limit, no reset happens in [10] min, and the LED frame rate does not drop by more than [10] %.
- **Verification method:** Test
- **Verified by:** TC-102
- **Category:** Robustness
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### SW-003 Fuzz tests of external inputs

- **Statement:** Each parser of external input (JSON extractor, push body, HTTP request, PEM and X.509 loader, update stream header) shall have a fuzz test that runs on the PC.
- **Rationale:** External input on a shared LAN is untrusted (A3). Fuzzing finds crashes that example tests do not (SYS-005, SYS-025).
- **Parent:** SYS-005, SYS-025
- **Acceptance criteria:** Each fuzz target runs at least [10000] mutated inputs per test run, and a longer run of at least [1] hour before each release, with no crash, hang or sanitizer finding. Found inputs become regression tests.
- **Verification method:** Test
- **Verified by:** TC-103
- **Category:** Robustness
- **Regulatory:** CRA Annex I Part I (2)(h)-(j) *(verify)*
- **Priority:** Must
- **Status:** Draft

### SW-004 Image confirmation and forced restart

- **Statement:** A new image shall confirm itself only after the main loop, the watchdog, the web server and a local health check have run without fault for [30] s, and shall restart itself if it has not confirmed within [45] s of its first start.
- **Rationale:** ADR-0007 item 3 and RV-001 items 7 and 8: the rule must have a trigger, and a confirmed image must be able to receive the next update. Wi-Fi is not part of the rule, so a changed network does not cause a revert loop.
- **Parent:** SYS-029, SYS-027
- **Acceptance criteria:** A test image that hangs before confirming is replaced by the previous image within [60] s of its first start (SYS-029). A test image whose web server does not start does not confirm. A test image on a network without Wi-Fi coverage confirms.
- **Verification method:** Test
- **Verified by:** TC-104
- **Category:** Reliability
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft


### SW-005 Raise the current limit only after a stable advertised-current reading

- **Statement:** The firmware shall start with the lowest current step and shall select a higher step only after the advertised-current input has given the same value in [5] consecutive reads over at least [500] ms, and shall select a step no higher than the one that the stable value allows.
- **Rationale:** A higher step on a source that advertises only the default overloads the source (RISK-003, RISK-025, RV-006 S1). The hardware gate (ADR-0016) is independent of firmware faults only. This rule is the first of two checks, not a replacement for it.
- **Parent:** SYS-020
- **Acceptance criteria:** After power-up, the step is the lowest until the stable reading exists. A reading that changes inside the window restarts the count. With a stable default reading, the high select outputs stay off. With an unreadable or unknown value, the step is the lowest. The step is set within [1] s of a stable reading (SYS-020).
- **Verification method:** Test
- **Verified by:** TC-105
- **Category:** Safety
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft
- **Proposed amendment (2026-11-05, owner decision; the Approved/Draft text above is unchanged until the owner approves):** Replace the statement by: "The firmware shall start with the lowest current step. It shall read the advertised-current inputs every [100] ms, shall count a read only while HOLD_OK_RB is high, and shall restart the count on any change of a read or when HOLD_OK_RB goes low. It shall select a higher step only after at least [6] consecutive equal reads (at least [500] ms), and shall select the step of the value table below, no higher." Acceptance criteria to add or replace: (1) the step is selected within [700] ms of the rising edge of HOLD_OK_RB (100 ms read phase, 500 ms window, GPIO and settling time, with margin; the derived sum is 612 ms); this replaces "within [1] s of a stable reading"; (2) after every falling edge of HOLD_OK_RB the firmware sets the select outputs low and starts a new count, also after a cable wobble and not only after power-up; (3) value table: default, or HOLD_OK_RB low, gives step 1; 1.5 A and 3 A give the highest step that the SYS-020 maximum allows (table to be agreed with ADR-0010 open point 3); (4) an unknown value is HOLD_OK_RB low or any input combination that the CC IC cannot output, and gives step 1. Rationale to add: the read period of [100] ms is the one of SW-006; with 6 reads at 100 ms the count and the time agree, so the owner may keep either the count or the time; [500] ms is about 3.75 times the typical CC debounce of 133 ms (the maximum debounce is not found). With SYS-020 at [2] s (proposal) the worst case of 1222 ms leaves 778 ms of margin. Findings closed by this text: C1, C2, G1 to G5 of `analysis-sw005-holdoff-timing.md`. Tests: TC-105 outline (Draft). Not run: no firmware exists; the boot time and the select latency are assumptions.
- **Proposed amendment (2026-11-06, goldfish review RV-010 finding 26; status Proposed; the Approved/Draft text above is unchanged until the owner approves):** The count is the normative criterion: "at least [6] consecutive equal reads". The time of [500] ms is derived (6 reads at [100] ms span 5 intervals) and is not a separate criterion. If the read period changes, the count stays and criterion (1) of the earlier proposal (the [700] ms within the rising edge of HOLD_OK_RB) is recomputed from the new period. Not run: no firmware.

### SW-006 Reduce load before lowering the current step

- **Statement:** The firmware shall read the advertised-current input at least every [100] ms during operation, and when the stable value falls, shall reduce the LED current to the new allowed level within [50] ms and only then lower the current step.
- **Rationale:** Lowering the limit under load can cause the brown-out that the limit is meant to prevent (RV-006 S4). Lowering the load first keeps the 5 V rail up.
- **Parent:** SYS-020
- **Acceptance criteria:** A change from the 1.5 A value to the default value at full white: the LED current is at or below the new allowed level within [50] ms, the step is lowered after that, and the device does not reset. The 5 V rail stays above [4.5] V during the change (to be confirmed against HW-004).
- **Verification method:** Test
- **Verified by:** TC-106
- **Category:** Safety
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft
- **Proposed amendment (2026-11-05, owner decision; the Approved/Draft text above is unchanged until the owner approves):** Replace the statement of order by: "The firmware shall reduce the LED current to the new allowed level within [50] ms of the stable advertised value falling, or of an enable readback (EN2, EN3) falling, whichever is first, and shall set the select output low after that." Rationale: for a change from 1.5 A to the default value the CC IC output goes high and the hardware gate lowers the limit by itself, before the next read of the firmware (up to 100 ms later); the order "load first, step after" cannot be kept by the firmware in that case (finding C4 of `analysis-sw005-holdoff-timing.md`). The hardware gate is then the first action and the firmware sheds the load as fast as it can. The [50] ms has no derivation yet; see the SW-009 proposal. Acceptance criteria to change: the check "the step is lowered after that" becomes "the select output is low after the LED current is at or below the new level", and the case of a falling readback is added. Not run: no firmware, no bench.
- **Proposed amendment (2026-11-06, goldfish review RV-010 finding 15; status Proposed; the Approved/Draft text above is unchanged until the owner approves):** The [50] ms of the statement is measured from the read that shows the stable advertised value falling, not from the fall itself (the read period is [100] ms, so no shorter time can be met from the fall). The case of a gate closing is covered by the [X] ms of SW-009. [50] ms stays open: it is a firmware path (read, LED current write, select low) and is set from a measured latency. Not run: no firmware.

### SW-007 Back-off after a brown-out reset

- **Statement:** After a brown-out reset, the firmware shall start at the lowest current step and shall not raise the step for [60] s, and after [3] brown-out resets in [10] min shall stay at the lowest step until the next power-up and show this state on the LEDs.
- **Rationale:** Without a rule, the device reads the 1.5 A value after each reset and raises the limit again, which gives a reset loop (RV-006 S5).
- **Parent:** SYS-020, SYS-029
- **Acceptance criteria:** After a forced brown-out the step stays lowest for [60] s. After [3] forced brown-outs in [10] min the step stays lowest after a further reset. The reset cause and the counter are kept over a reset (persistence method is a design decision). The LED indication is defined with the user documentation.
- **Verification method:** Test
- **Verified by:** TC-107
- **Category:** Reliability
- **Regulatory:** TBD
- **Priority:** Should
- **Status:** Draft
- **Proposed amendment (2026-11-05, owner decision; the Approved/Draft text above is unchanged until the owner approves):** Add the definition: "A brown-out reset happens during a hold-off when HOLD_OK_RB is low at the first read after the reset, or when a retained flag, set by the readback interrupt of SW-009, is set at that reset." Rationale: SW-009 says that a brown-out during a hold-off is not counted, but the reset cause alone does not say that; the rule has no observable test without this definition (finding G6 of `analysis-sw005-holdoff-timing.md`). Acceptance criteria to add: a forced reset with HOLD_OK_RB low, and a forced reset with the retained flag set, do not increase the brown-out counter; a forced reset with both clear does. Not run: the method to keep the flag over a reset is a design decision, not made here.
- **Proposed amendment (2026-11-06, goldfish review RV-010 finding 26; status Proposed; the Approved/Draft text above is unchanged until the owner approves):** This paragraph adds to the earlier proposed amendment above. The method to keep the flag over a reset is a design decision with a cost, so the owner or a design note decides it before this requirement is Approved. Two options. (a) A retained flag in memory that survives the reset (for the ESP32-C3 the RTC memory is the candidate; whether it survives this reset cause is not verified). Cost: a platform dependence and a test hook. (b) No flag: use only HOLD_OK_RB at the first read after the reset. Cost: a reset that lasts longer than the remaining hold-off (up to 600 ms) is counted as a real brown-out, so a cable wobble can start the back-off of [60] s. Recommendation: (a), if the retention is shown on the prototype; otherwise (b) with the cost stated. Acceptance criteria to add: the test uses a hook that forces the reset and the flag state; a read of the flag before the readback configuration of SW-009 is allowed and the flag is cleared only after it has been used. Not run: the retention of the chosen memory is not measured.

### SW-008 Tolerance of Power Delivery traffic and source changes on the CC line

- **Statement:** The firmware shall not raise the current step while the advertised-current input changes more often than [once] per [500] ms, and shall give the lowest step when the input does not settle within [5] s.
- **Rationale:** Power Delivery sources and cables put traffic on the CC line, and some sources change the advertised current (RV-006 S3, S6). A filter that never settles must fail to the safe step.
- **Parent:** SYS-020
- **Acceptance criteria:** With a Power Delivery charger, a charger that toggles the advertised value, and a cable with a wrong pull-up (test setup to define): the step never exceeds the one that the true advertised value allows, and the device ends in a stable state in [5] s or at the lowest step.
- **Verification method:** Test
- **Verified by:** TC-108
- **Category:** Safety
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SW-009 Follow the hardware gate state and shed load when the gate closes

- **Statement:** The firmware shall read the hold-off and gate-enable state back from the hardware gate and shall reduce the LED load to the budget of the lowest current step within [50] ms of the hold-off or the gate closing, and shall not count a brown-out that happens during a hold-off towards the back-off of SW-007.
- **Rationale:** The gate (ADR-0016) closes by itself after a dip of VBUS for [200] to [600] ms and drops the limit to the first step while the MCU stays up with its select line high (goldfish review of the gate, finding H2). Without readback the firmware keeps a full load on a limit that is already lower and causes a brown-out and the 60 s back-off after a cable wobble. Needs a readback line from the gate to the MCU, which HW-010 does not yet have (owner decision).
- **Parent:** SYS-020
- **Acceptance criteria:** With the hold-off forced active (VBUS dip, bench), the LED load is within the lowest-step budget within [50] ms of the gate state change, and no brown-out back-off starts. When the gate state input is not readable, the firmware assumes the gate closed and uses the lowest step.
- **Verification method:** Test
- **Verified by:** TC-109
- **Category:** Safety
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft
- **Proposed amendment (2026-11-05, owner-confirmed proposal; status Proposed; the Draft text above is unchanged until the owner approves):** Add to the statement: "The firmware shall treat the CC_OK inputs as valid only while HOLD_OK_RB is high, and otherwise shall assume the lowest step. The firmware shall ignore FAULT_N while HOLD_OK_RB is low. The firmware shall disable the internal pull-ups on GPIO20 and GPIO21 before it uses the gate-enable readbacks. The firmware shall never drive both select outputs at the same time." Rationale: CC_OK_1A5 and CC_OK_3A read high with VBUS gone and 3V3 up (M2); the D+ back-feed can raise FAULT_N while the gate is closed (M1); with the 100 kohm readback resistor an enabled 45 kohm pull-up gives about 2.1 V for a low gate, which is an invalid level (analysis-n1-n2-readback-backfeed.md); the select outputs must stay exclusive (HW-010 proposal). Acceptance criteria to add: a test with HOLD_OK_RB low and CC_OK inputs high gives the lowest step; a test with FAULT_N low and HOLD_OK_RB low gives no fault action; a test reads the pull-up state of GPIO20 and GPIO21 after start-up; no test or run drives both select outputs. Not checked: whether gpio_pin_configure with GPIO_INPUT clears the pull-up on this SoC.
- **Proposed amendment (2026-11-05, owner decision; the Approved/Draft text above is unchanged until the owner approves):** This paragraph adds to the earlier proposed amendment above and does not replace it. (1) Rationale, replace "closes by itself after a dip of VBUS for [200] to [600] ms" by: "closes within about 10 us of a VBUS dip and stays closed for [200] to [600] ms after VBUS returns (a short dip can give a shorter time, TC-210)"; replace the claim that the shed avoids the brown-out by: "The shed limits the time of the overload and the time in which the MCU can reset; the 5 V rail falls in under 1 ms at the assumed capacitance, so the reset is not prevented" (finding C3 of `analysis-sw005-holdoff-timing.md`). (2) Statement, replace "within [50] ms of the hold-off or the gate closing" by "within [X] ms of the falling edge of HOLD_OK_RB or of EN2 or EN3, with edge-triggered interrupts and an interrupt latency of at most [1] ms"; [X] is set from a measured rail hold-up (open, finding G10; the ADR-0010 assumption of 100 uF gives a rail hold-up of about 0.07 ms, not 50 ms). Add: "A falling edge that is shorter than the poll period shall not be missed; the firmware latches the edge." (3) Statement addition: "The firmware shall configure GPIO20 and GPIO21 as inputs without any pull (no GPIO_PULL_UP, no GPIO_PULL_DOWN) before it reads the gate-enable readbacks, and shall treat the readbacks as invalid until that configuration has completed. The firmware shall send its console and logs over the USB-Serial-JTAG interface and shall not enable the uart0 device, so that the firmware does not configure GPIO20 or GPIO21 for the UART." (4) Rationale addition: after reset GPIO20 has its pull-up enabled and GPIO21 has its output and pull-up enabled (ESP32-C3 TRM v1.4, Table 5.12-1); in Zephyr v4.5.0 gpio_pin_configure with GPIO_INPUT clears both pull bits and disables the output, and the UART driver would apply its pinctrl (GPIO21 output high, GPIO20 pull-up) if uart0 were enabled (`zephyr-usb-console-and-gpio-pull-facts.md`; source reading, no build, no hardware run). This answers the "Not checked" sentence of the earlier proposed amendment for the source level only. (5) Acceptance criteria to add: (a) the build configuration shows usb_serial as zephyr,console, uart0 disabled in the final devicetree, CONFIG_SERIAL_ESP32_USB=y, CONFIG_UART_ESP32 not set and CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y (inspection of zephyr.dts and .config, recorded in docs/verification/); (b) on the prototype, a test reads IO_MUX_GPIO20_REG and IO_MUX_GPIO21_REG after the start-up configuration and shows FUN_WPU (bit 8) and FUN_WPD (bit 7) both 0 and MCU_SEL equal to 1; (c) on the prototype the log is visible on the USB-C connector alone, and a scope or logic analyser shows no UART activity on GPIO21 after the application has started (the ROM boot print before that is tolerated by the 100 kohm readback resistor); (d) a unit test on the native or simulated build shows that the readback code calls gpio_pin_configure with GPIO_INPUT only and reports a readback taken before configuration as invalid. Open for the owner: whether the readbacks need GPIO_ACTIVE_LOW in the devicetree; whether the window between reset and the configuration call needs a hardware answer; whether a hardware measure for the rail hold-up is wanted (not recommended without a measured hold-up). The exact Kconfig symbols are not verified by a build. Tests: TC-109 outline (Draft).
- **Proposed amendment (2026-11-06, goldfish review RV-010 finding 15; status Proposed; the Approved/Draft text above is unchanged until the owner approves):** This paragraph adds to the earlier proposed amendments above. (1) Decision recommended to the owner: the requirement is "shed the load in [X] ms", not "avoid the reset". A reset after a gate closure is expected and tolerated, because the gate closes within about 10 us and the 5 V rail falls in under 1 ms (hold-up about 0.07 ms at the assumed 100 uF), which the firmware cannot beat. (2) In the acceptance criteria, replace "and no brown-out back-off starts" by: "and a processor reset that happens while HOLD_OK_RB is low, or with the retained flag of SW-007 set, does not increase the brown-out counter of SW-007". (3) Statement: remove any wording that says the shed prevents the reset; the shed shortens the time of the overload and gives the processor a lower load for the restart. (4) [X] stays a bracketed placeholder. Bench item to add (TC-109): measure the fall of the 5 V and 3V3 rails after a VBUS dip at full white and at the lowest-step load, and record the hold-up time and the 3V3 value at which the processor resets; [X] is set from that record. Open for the owner: whether bulk capacitance to ride through a dip is wanted (cost, inrush and SYS-021; not recommended without the measured hold-up). Not run: no bench, no firmware.
